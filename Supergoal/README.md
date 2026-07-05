# chip-supergoal

**chip-supergoal** is a Hermes skill that turns a non-trivial engineering request into a disk-backed, reviewable **SuperGoal package** and one standard Hermes `/goal` handoff.

It is designed for work that should not be handled as a loose chat plan: production-adjacent changes, risky refactors, multi-phase implementation, migrations, security-sensitive work, and long-running agent execution that needs state, evidence, and a final audit.

Русская документация: [`docs/README.ru.md`](docs/README.ru.md)

## What it does

`chip-supergoal` is a **planner/compiler**, not the executor.

It creates a `.supergoal/` package containing:

- `THINKING.md` — goals, assumptions, constraints, risk notes, context used.
- `RESEARCH.md` — generated research gate record when current facts or external context matter.
- `reports/research.json` — machine-readable research provider/status/sources report when the gate is active.
- `LOOP_DESIGN.md` — execution loop design: host, reviewer/judge, gates, stop conditions, recovery, boundaries.
- `ROADMAP.md` — phase map, acceptance criteria, required commands, evidence contract.
- `STATE.md` — initial execution state and current phase pointer.
- `PROTOCOL.md` — self-contained executor protocol for a later `/goal` run.
- `LAUNCH_GOAL.md` — the only file containing the launch body line beginning with `SUPERGOAL_GOAL_BODY:`.
- `phases/phase-N.md` — strict phase specifications.
- helper scripts and delivery receipts when the workflow requires them.

The later Hermes `/goal` session reads those files and executes the work. Final completion is only valid after final audit markers such as `AUDIT_COMPLETE` and `SUPERGOAL_RUN_COMPLETE`.

## Why it exists

Agentic engineering often fails in predictable ways:

1. The assistant starts implementing before understanding the real target.
2. Long tasks lose state between turns.
3. “Done” is reported before tests, deployment, or audit evidence exists.
4. Risky work skips review because it looks like routine implementation.
5. Generated plans are not executable by a separate agent.

`chip-supergoal` addresses those failure modes by compiling the task into a package with:

- explicit phase boundaries;
- mandatory verification commands;
- evidence requirements;
- risk/RPD review gates;
- state and recovery rules;
- strict launch-marker placement;
- package validation and manifest integrity checks.

## Quick start

Install or clone this repository as a Hermes skill directory, then load it through Hermes.

Typical usage in Hermes:

```text
/chip-supergoal Build or refactor X end-to-end
```

For direct CLI validation of this repository:

```bash
python3 -m unittest discover -s tests
bash scripts/test.sh
```

Compile the example contract:

```bash
python3 scripts/sgctl.py compile examples/brownfield-feature/CONTRACT.json --out /tmp/example-supergoal
python3 scripts/sgctl.py validate-package /tmp/example-supergoal --strict
```

Then inspect:

```bash
ls -la /tmp/example-supergoal
sed -n '1,80p' /tmp/example-supergoal/LAUNCH_GOAL.md
```

## CLI: `sgctl.py`

The repository includes `scripts/sgctl.py`, a small control utility used by tests and by generated packages.

### Research provider gate

For plans where current facts matter, set `compatibility.research_gate` in `CONTRACT.json`. The preferred provider is `perplex`; official docs, Context7, generic web search, or manual research must include `provider_unavailable_reason` when Perplex was not used.

Minimal satisfied gate:

```json
{
  "compatibility": {
    "research_gate": {
      "required": true,
      "status": "satisfied",
      "provider": "perplex",
      "query": "current facts needed before planning",
      "summary": "Research summary explaining what changed in the plan.",
      "sources": [{"title": "Source", "url": "https://example.com", "provider": "perplex"}],
      "planning_implications": ["Specific phase/spec/acceptance change caused by research"]
    }
  }
}
```

Validate and inspect it:

```bash
python3 scripts/sgctl.py research-gate examples/brownfield-feature/CONTRACT.json --format json
python3 scripts/sgctl.py validate-contract examples/brownfield-feature/CONTRACT.json --strict
```

Compile writes `RESEARCH.md` and `reports/research.json`; `validate-package` detects drift in both.

Common commands:

```bash
# Validate a v3 contract
python3 scripts/sgctl.py validate-contract examples/brownfield-feature/CONTRACT.json --strict

# Compile a contract into a sealed SuperGoal package
python3 scripts/sgctl.py compile examples/brownfield-feature/CONTRACT.json --out /tmp/example-supergoal

# Validate a generated package
python3 scripts/sgctl.py validate-package /tmp/example-supergoal --strict

# Migrate an older v2-style package when supported
python3 scripts/sgctl.py migrate-v2 <old-package-root> --out <new-contract-or-package>
```

## Safety model

### Planner/executor boundary

This skill plans and compiles. It does **not** execute implementation phases itself. That boundary is deliberate: the package must be readable, reviewable, and executable by a later standard `/goal` session.

### One launch body

Exactly one actual launch body is allowed, and it belongs in `LAUNCH_GOAL.md`.

Other files may explain the launch process, but they must not contain another real line starting with:

`SUPERGOAL_GOAL_BODY:`

This prevents accidental duplicate goal launches and stale package execution.

### Package sealing

Generated packages include `MANIFEST.json` records with file paths, sha256 hashes, byte counts, modes, and a package fingerprint. `validate-package` detects:

- generated Markdown drift from canonical `CONTRACT.json` rendering;
- manifest hash/size/mode drift;
- extra unsealed files;
- missing required files;
- duplicate or unsafe manifest paths;
- wrong launch-marker placement.

### Compile overwrite protection

The compiler refuses unsafe output targets, including:

- arbitrary existing directories that are not sealed SuperGoal packages;
- packages for a different goal ID;
- changed contracts without the required `contract_revision` advance;
- source-container targets;
- started/runtime packages containing runtime state or delivery output.

## Repository layout

```text
.
├── SKILL.md                      # Hermes skill entrypoint and operating contract
├── README.md                     # English documentation
├── docs/README.ru.md             # Russian documentation
├── lib/chip_supergoal/           # Contract, compiler, validator, state, audit logic
├── scripts/                      # sgctl and verification/probe scripts
├── spec/                         # JSON schemas and policy catalogs
├── templates/                    # Generated package templates
├── references/                   # Detailed workflow and invariant references
├── examples/                     # Example contracts
└── tests/                        # Unit, semantic, rendering, security, migration, e2e tests
```

## Test suite

Run the full local gate:

```bash
bash scripts/test.sh
```

Run Python tests directly:

```bash
python3 -m unittest discover -s tests
```

Focused useful tests:

```bash
python3 -m unittest tests.rendering.test_compile_determinism
python3 -m unittest tests.semantic.test_sgctl_semantic_validation
python3 -m unittest tests.security.test_archive_symlink tests.security.test_forged_receipt
```

## Development workflow

1. Change code, templates, references, or tests.
2. Run focused tests for the changed area.
3. Run `python3 -m unittest discover -s tests`.
4. Run `bash scripts/test.sh`.
5. Compile the example package and validate it strictly.
6. Check that only `templates/LAUNCH_GOAL.md` contains a real `SUPERGOAL_GOAL_BODY:` marker.

Suggested final gate:

```bash
python3 -m unittest discover -s tests
bash scripts/test.sh
python3 scripts/sgctl.py compile examples/brownfield-feature/CONTRACT.json --out /tmp/chip-supergoal-example
python3 scripts/sgctl.py validate-package /tmp/chip-supergoal-example --strict
```

## Public-use notes

This repository contains the public-safe source of the skill and its validation harness. Runtime state, generated local `.supergoal/` packages, credentials, receipts, caches, and local deployment artifacts should stay outside git.

If you adapt this for another agent runtime, keep the invariants intact:

- one launch surface;
- explicit planner/executor boundary;
- generated package validation;
- no false completion without final audit;
- risk-aware review gates;
- state recovery and blocker semantics.

## License

MIT. See [`LICENSE`](LICENSE).
