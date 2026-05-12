"""Experiment manifest parsing (YAML -> dataclasses)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Prompt:
    id: str
    text: str


@dataclass
class Mutation:
    target_file: str      # e.g. "SOUL.md", "memory/MEMORY.md"
    encoding: str         # e.g. "unicode_tags", "zero_width", "homoglyphs"
    payload: str          # plaintext instruction to encode invisibly
    position: str = "append"  # "append" | "prepend"


@dataclass
class RunSpec:
    class_label: str
    mutations: list[Mutation] = field(default_factory=list)
    setup: list[str] = field(default_factory=list)  # prompts to run in session 1 (priming/poisoning phase)
    remove_after_setup: list[str] = field(default_factory=list)  # files to delete between setup and main session


@dataclass
class ExperimentManifest:
    name: str
    model: str
    repeats: int
    honeypot_tool: str
    prompts: list[Prompt]
    runs: list[RunSpec]
    workspace_seed: str | None = None


def load_manifest(path: Path) -> ExperimentManifest:
    """Parse a YAML experiment manifest into typed dataclasses.

    Raises ValueError with details on malformed manifests.
    """
    with open(path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"Manifest must be a YAML mapping, got {type(raw).__name__}")

    # Required top-level fields
    for key in ("name", "model", "prompts", "runs"):
        if key not in raw:
            raise ValueError(f"Manifest missing required field: {key!r}")

    prompts = []
    for i, p in enumerate(raw["prompts"]):
        if not isinstance(p, dict) or "id" not in p or "text" not in p:
            raise ValueError(f"prompts[{i}] must have 'id' and 'text' fields")
        prompts.append(Prompt(id=p["id"], text=p["text"]))

    runs = []
    for i, r in enumerate(raw["runs"]):
        if not isinstance(r, dict) or "class" not in r:
            raise ValueError(f"runs[{i}] must have a 'class' field")

        mutations = []
        raw_mutations = r.get("mutations", {})
        if isinstance(raw_mutations, dict):
            for target_file, spec in raw_mutations.items():
                if not isinstance(spec, dict):
                    raise ValueError(
                        f"runs[{i}].mutations[{target_file!r}] must be a mapping "
                        f"with 'encoding' and 'payload'"
                    )
                mutations.append(Mutation(
                    target_file=target_file,
                    encoding=spec["encoding"],
                    payload=spec["payload"],
                    position=spec.get("position", "append"),
                ))

        setup = r.get("setup", [])
        if isinstance(setup, str):
            setup = [setup]

        remove_after_setup = r.get("remove_after_setup", [])
        if isinstance(remove_after_setup, str):
            remove_after_setup = [remove_after_setup]

        runs.append(RunSpec(class_label=r["class"], mutations=mutations, setup=setup, remove_after_setup=remove_after_setup))

    return ExperimentManifest(
        name=raw["name"],
        model=raw["model"],
        repeats=raw.get("repeats", 10),
        honeypot_tool=raw.get("honeypot_tool", "bad_news"),
        prompts=prompts,
        runs=runs,
        workspace_seed=raw.get("workspace_seed"),
    )
