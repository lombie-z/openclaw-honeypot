"""OpenClaw instance provisioning and teardown.

Creates ephemeral, isolated OpenClaw state directories for experiment runs.
Adapted from the existing sandbox harness at
~/.openclaw/workspace/openclaw-sandbox-harness/runner.py
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .config import ExperimentManifest, Mutation
from .payloads import PayloadEncoder

# Paths relative to this file
_RUNNER_DIR = Path(__file__).parent
_BASE_CONFIG_PATH = _RUNNER_DIR / "base_config.json"
_BOOTSTRAP_DIR = _RUNNER_DIR / "bootstrap"
_WORKSPACE_SEED_DIR = _RUNNER_DIR / "workspace_seed"
_HONEYPOT_DIR = _RUNNER_DIR.parent / "honeypot"

# Host auth location (for credential passthrough)
_HOST_AUTH_PATH = Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json"
_HOST_MODELS_PATH = Path.home() / ".openclaw" / "agents" / "main" / "agent" / "models.json"


class OpenClawInstance:
    """Manages the lifecycle of an isolated OpenClaw instance."""

    def __init__(self, manifest: ExperimentManifest):
        self.manifest = manifest
        self.state_dir: Path | None = None
        self.workspace_dir: Path | None = None
        if manifest.workspace_seed:
            self._seed_dir = Path(manifest.workspace_seed)
            if not self._seed_dir.is_absolute():
                self._seed_dir = _RUNNER_DIR / manifest.workspace_seed
        else:
            self._seed_dir = _WORKSPACE_SEED_DIR

    def provision(self) -> Path:
        """Create a fresh ephemeral state directory with all required files.

        Returns the state directory path.
        """
        self.state_dir = Path(tempfile.mkdtemp(prefix="openclaw-exp-"))
        self.workspace_dir = self.state_dir / "workspace"

        # Create directory structure
        (self.state_dir / "logs").mkdir()
        (self.state_dir / "memory").mkdir()
        (self.state_dir / "extensions").mkdir()
        (self.state_dir / "skills").mkdir()
        self.workspace_dir.mkdir()
        (self.state_dir / "agents" / "main" / "agent").mkdir(parents=True)
        (self.state_dir / "agents" / "main" / "sessions").mkdir(parents=True)

        # Write config
        self._write_config()

        # Copy auth credentials from host
        self._copy_auth()

        # Copy honeypot plugin
        self._copy_honeypot()

        # Write bootstrap files to workspace
        self._write_bootstrap()

        # Copy workspace seed files
        self._copy_workspace_seed()

        return self.state_dir

    def apply_mutations(self, mutations: list[Mutation]) -> dict[str, str]:
        """Apply encoded payloads to bootstrap/workspace files.

        Returns a dict of {target_file: "applied"} for logging. Mutations
        targeting "__prompt__" are skipped here (handled by the executor).
        """
        applied = {}
        for mut in mutations:
            if mut.target_file == "__prompt__":
                continue  # prompt mutations applied at send time

            target = self._resolve_mutation_target(mut.target_file)
            target.parent.mkdir(parents=True, exist_ok=True)

            # Read existing content or start empty
            existing = ""
            if target.exists():
                existing = target.read_text(encoding="utf-8")

            # Encode the payload
            encoded = PayloadEncoder.encode(
                text=mut.payload,
                encoding=mut.encoding,
                carrier=existing if mut.position == "append" else "",
            )

            if mut.position == "append":
                content = encoded  # carrier already includes existing
            else:  # prepend
                content = encoded + existing

            target.write_text(content, encoding="utf-8")
            applied[mut.target_file] = "applied"

        return applied

    def get_env(self) -> dict[str, str]:
        """Return environment dict with OpenClaw state dir set."""
        env = {**os.environ}
        env["OPENCLAW_STATE_DIR"] = str(self.state_dir)
        env["OPENCLAW_CONFIG_PATH"] = str(self.state_dir / "openclaw.json")
        return env

    def collect_transcripts(self) -> list[Path]:
        """Find all session transcript JSONL files."""
        if self.state_dir is None:
            return []
        sessions_dir = self.state_dir / "agents" / "main" / "sessions"
        if not sessions_dir.exists():
            return []
        return sorted(
            p for p in sessions_dir.glob("*.jsonl")
            if ".reset." not in p.name and ".acp-stream." not in p.name
        )

    def teardown(self):
        """Remove the ephemeral state directory."""
        if self.state_dir and self.state_dir.exists():
            shutil.rmtree(self.state_dir, ignore_errors=True)
            self.state_dir = None
            self.workspace_dir = None

    # ── Private helpers ──────────────────────────────────────────────

    def _write_config(self):
        """Write openclaw.json with model override and workspace path."""
        with open(_BASE_CONFIG_PATH) as f:
            config = json.load(f)

        config["meta"]["lastTouchedAt"] = datetime.now(timezone.utc).isoformat()
        config["agents"]["defaults"]["model"]["primary"] = self.manifest.model
        config["agents"]["defaults"]["workspace"] = str(self.workspace_dir)

        with open(self.state_dir / "openclaw.json", "w") as f:
            json.dump(config, f, indent=2)

    def _copy_auth(self):
        """Copy auth credentials from the host OpenClaw installation."""
        agent_dir = self.state_dir / "agents" / "main" / "agent"

        if _HOST_AUTH_PATH.exists():
            shutil.copy2(_HOST_AUTH_PATH, agent_dir / "auth-profiles.json")
        else:
            # Fall back to environment variables
            auth = {}
            openai_key = os.environ.get("OPENAI_API_KEY", "")
            if openai_key:
                auth["openai-codex"] = {"apiKey": openai_key}
                auth["openai"] = {"apiKey": openai_key}
            anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if anthropic_key:
                auth["anthropic"] = {"apiKey": anthropic_key}
            with open(agent_dir / "auth-profiles.json", "w") as f:
                json.dump(auth, f, indent=2)

        if _HOST_MODELS_PATH.exists():
            shutil.copy2(_HOST_MODELS_PATH, agent_dir / "models.json")

    def _copy_honeypot(self):
        """Copy the honeypot plugin into the instance's extensions dir."""
        dest = self.state_dir / "extensions" / "honeypot"
        if _HONEYPOT_DIR.exists():
            shutil.copytree(_HONEYPOT_DIR, dest)

    def _write_bootstrap(self):
        """Write clean bootstrap files to the workspace."""
        for src in _BOOTSTRAP_DIR.glob("*.md"):
            shutil.copy2(src, self.workspace_dir / src.name)

    def _copy_workspace_seed(self):
        """Copy seed files (and directories) into the workspace."""
        if not self._seed_dir.exists():
            raise FileNotFoundError(f"Workspace seed not found: {self._seed_dir}")
        for src in self._seed_dir.iterdir():
            dest = self.workspace_dir / src.name
            if src.is_file():
                shutil.copy2(src, dest)
            elif src.is_dir():
                shutil.copytree(src, dest)

    def _resolve_mutation_target(self, target_file: str) -> Path:
        """Resolve a mutation target path relative to the workspace.

        Supports paths like:
          - "SOUL.md"          -> workspace/SOUL.md
          - "memory/MEMORY.md" -> workspace/memory/MEMORY.md (or state_dir/memory/)
          - "skills/x/SKILL.md" -> state_dir/skills/x/SKILL.md
        """
        if target_file.startswith("skills/"):
            return self.state_dir / target_file
        elif target_file.startswith("memory/"):
            # OpenClaw stores workspace memory under workspace_dir/memory/
            return self.workspace_dir / target_file
        else:
            return self.workspace_dir / target_file
