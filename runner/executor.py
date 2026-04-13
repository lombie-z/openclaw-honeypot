"""Experiment execution — orchestrates runs across instances."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .config import ExperimentManifest, RunSpec, Prompt
from .instance import OpenClawInstance
from .payloads import PayloadEncoder


@dataclass
class RunResult:
    run_id: str
    class_label: str
    prompt_id: str
    repeat: int
    transcript: str          # filename relative to output dir
    success: bool
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


class ExperimentExecutor:
    """Runs all prompt x class x repeat combinations for an experiment."""

    def __init__(self, manifest: ExperimentManifest, output_dir: Path):
        self.manifest = manifest
        self.output_dir = output_dir

    def execute_all(self) -> list[RunResult]:
        """Execute all runs and collect transcripts.

        Each run gets a completely fresh OpenClaw instance to prevent
        cross-contamination.
        """
        results: list[RunResult] = []
        total = len(self.manifest.runs) * len(self.manifest.prompts) * self.manifest.repeats
        current = 0

        for run_spec in self.manifest.runs:
            for prompt in self.manifest.prompts:
                for repeat in range(self.manifest.repeats):
                    current += 1
                    run_id = f"{run_spec.class_label}-{prompt.id}-{repeat}"
                    print(
                        f"[{current}/{total}] {run_id} ... ",
                        end="", flush=True,
                    )

                    result = self._execute_single(run_spec, prompt, repeat, run_id)
                    results.append(result)

                    status = "OK" if result.success else "FAIL"
                    print(f"{status} ({result.duration_seconds:.1f}s)")

                    if result.errors:
                        for err in result.errors:
                            print(f"  ERROR: {err[:200]}")

        # Write manifest summary
        self._write_manifest(results)

        return results

    def _execute_single(
        self,
        run_spec: RunSpec,
        prompt: Prompt,
        repeat: int,
        run_id: str,
    ) -> RunResult:
        """Execute a single run: provision, mutate, send, collect, teardown."""
        instance = OpenClawInstance(self.manifest)
        transcript_name = f"{run_id}.jsonl"
        t0 = time.monotonic()

        try:
            # 1. Provision clean instance
            instance.provision()

            # 2. Apply file mutations (poisoned bootstrap/memory/skills)
            instance.apply_mutations(run_spec.mutations)

            # 3. Run setup phase (if any) — separate session on same instance
            #    This is for multi-session attacks: setup poisons memory,
            #    main prompt tests if the poison activates in a fresh session.
            if run_spec.setup:
                setup_errors = self._run_setup(instance, run_id, run_spec.setup)
                if setup_errors:
                    errors = setup_errors
                    # Continue anyway — the main prompt is the real test

            # 4. Prepare prompt text (apply __prompt__ mutations if any)
            prompt_text = self._prepare_prompt(prompt.text, run_spec)

            # 5. Send main message in a NEW session (simulates session reset)
            session_id = run_id
            errors = self._send_message(instance, session_id, prompt_text)

            # 6. Collect transcript — get the MAIN session transcript, not setup
            transcripts = instance.collect_transcripts()
            if transcripts:
                # Find the transcript matching the main session_id
                main_transcript = None
                for t in transcripts:
                    if run_id in t.stem and "setup" not in t.stem:
                        main_transcript = t
                        break
                # Fall back to the last transcript if no exact match
                if main_transcript is None:
                    main_transcript = transcripts[-1]

                dest = self.output_dir / transcript_name
                shutil.copy2(main_transcript, dest)
                success = len(errors) == 0
            else:
                success = False
                errors.append("No transcript file found after execution")

            duration = time.monotonic() - t0
            return RunResult(
                run_id=run_id,
                class_label=run_spec.class_label,
                prompt_id=prompt.id,
                repeat=repeat,
                transcript=transcript_name,
                success=success,
                errors=errors,
                duration_seconds=round(duration, 2),
            )

        except Exception as e:
            duration = time.monotonic() - t0
            return RunResult(
                run_id=run_id,
                class_label=run_spec.class_label,
                prompt_id=prompt.id,
                repeat=repeat,
                transcript=transcript_name,
                success=False,
                errors=[str(e)],
                duration_seconds=round(duration, 2),
            )

        finally:
            instance.teardown()

    def _run_setup(
        self,
        instance: OpenClawInstance,
        run_id: str,
        setup_prompts: list[str],
    ) -> list[str]:
        """Run setup-phase prompts in a separate session.

        The setup session uses a different session ID so the main prompt
        starts in a fresh session — but the instance (and its memory files)
        persists, simulating a session reset.
        """
        errors = []
        for i, prompt_text in enumerate(setup_prompts):
            setup_session = f"{run_id}-setup-{i}"
            errs = self._send_message(instance, setup_session, prompt_text)
            errors.extend(errs)
        return errors

    def _prepare_prompt(self, prompt_text: str, run_spec: RunSpec) -> str:
        """Apply any __prompt__ mutations to the prompt text."""
        for mut in run_spec.mutations:
            if mut.target_file != "__prompt__":
                continue
            # Encode the payload and append/prepend to the prompt
            encoded = PayloadEncoder.encode(
                text=mut.payload,
                encoding=mut.encoding,
                carrier=prompt_text if mut.position == "append" else "",
            )
            if mut.position == "append":
                prompt_text = encoded
            else:
                prompt_text = encoded + prompt_text
        return prompt_text

    def _send_message(
        self,
        instance: OpenClawInstance,
        session_id: str,
        prompt_text: str,
    ) -> list[str]:
        """Send a message via the OpenClaw CLI and wait for completion.

        Returns a list of error strings (empty on success).
        """
        errors = []
        env = instance.get_env()

        try:
            result = subprocess.run(
                [
                    "openclaw", "agent",
                    "--local",
                    "--session-id", session_id,
                    "--message", prompt_text,
                    "--json",
                ],
                capture_output=True,
                text=True,
                timeout=300,
                env=env,
                cwd=str(instance.workspace_dir),
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                errors.append(
                    f"openclaw exited {result.returncode}: {stderr[:500]}"
                )
        except FileNotFoundError:
            errors.append("openclaw CLI not found in PATH")
        except subprocess.TimeoutExpired:
            errors.append("Timeout after 300s")

        return errors

    def _write_manifest(self, results: list[RunResult]):
        """Write a manifest.json summarising the experiment run."""
        manifest_data = {
            "name": self.manifest.name,
            "model": self.manifest.model,
            "repeats": self.manifest.repeats,
            "honeypot_tool": self.manifest.honeypot_tool,
            "prompts": [{"id": p.id, "text": p.text} for p in self.manifest.prompts],
            "runs": [
                {
                    "class_label": r.class_label,
                    "mutations": [
                        {
                            "target_file": m.target_file,
                            "encoding": m.encoding,
                            "payload": m.payload,
                            "position": m.position,
                        }
                        for m in r.mutations
                    ],
                }
                for r in self.manifest.runs
            ],
            "results": [asdict(r) for r in results],
        }

        with open(self.output_dir / "manifest.json", "w") as f:
            json.dump(manifest_data, f, indent=2, default=str)
