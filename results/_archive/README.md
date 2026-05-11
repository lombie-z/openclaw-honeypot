Archived preliminary/test results — not used in the thesis.

- `poc/` — single-run proof-of-concept (1 run per class, no YAML manifest)
- `run1/` — earliest experimental run, older format
- `quick-test/` — 3-run framework smoke test
- `minimal-3x/` — 3 repeats × 5 classes, includes homoglyph (plaintext SOUL.md injection, not steganographic)
- `minimal-5x/` — 5 repeats × 5 classes, same issue

The homoglyph results (100% ASR) are misleading as an "invisible encoding" — the Cyrillic-substituted text is fully readable. These are effectively plaintext system-prompt injections.

- `semantic-nudge/` — tests vague SOUL.md hints, not memory or encoding. Tangential to thesis scope.
- `memory-poison/` — early 3-run pilot (4 classes × 3 runs). Superseded by ablation.yaml (4 classes × 20 runs).
- `memory-laundered-10x/` — 10 extra laundering runs with no matched control arm.
- `memory-laundered-20x/` — 20 extra laundering runs with no matched control arm.
- `invisible-v2/` — unicode encoding tests (n=3 per variant). Too underpowered; replaced by new encoding-memory experiment.
