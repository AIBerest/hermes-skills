# Coffee review — alpha.2 ZIP gate

Date: 2026-06-26
Package: `chip-supergoal` operator distribution
Version: `3.0.0-alpha.2`

## Review verdict

The alpha.2 ZIP is a hardened Architect+ workstream artifact. It is still labeled alpha because the package is a private operator edition, but the release gate no longer has the coffee-review blockers found in alpha.1.

## Fixes applied in alpha.2

1. **Compiler output reproducibility**
   - `LAUNCH_GOAL.md` no longer embeds the physical `--out` directory.
   - `MANIFEST.json` no longer changes solely because the package was compiled into another path.
   - Two independent compiles now compare byte-identical across all generated files.

2. **Destructive compile protection**
   - Existing output directories must already be sealed chip-supergoal packages.
   - Arbitrary existing directories are refused and preserved.
   - Output targets containing the contract source are refused.
   - Different goal IDs are refused.
   - Contract content changes must advance `contract_revision` by exactly one.
   - Started/runtime packages with state, event, evidence, or delivery output artifacts are not overwritten.

3. **Package validation integrity**
   - `validate-package` now checks generated Markdown views against canonical `CONTRACT.json` rendering.
   - Manual generated-view drift is detected even when the single launch-marker rule still passes.
   - Manifest file-set drift, byte/hash drift, mode drift, and fingerprint drift are detected.
   - Unsealed immutable files are rejected.

4. **Traceability cleanup**
   - Previously documented xfail rows for semantic validator, archive symlink, and forged receipt hardening are now marked as passed.
   - New alpha.2 traceability rows cover compile safety, package drift detection, and full compile reproducibility.

## Local evidence

- `python3 -m unittest discover -s tests` — 67 tests, 1 skipped, pass.
- `python3 scripts/sgctl.py validate-contract examples/brownfield-feature/CONTRACT.json --strict` — pass.
- Two independent compiles to `/tmp/sg-build-a` and `/tmp/sg-build-b` — pass.
- `python3 scripts/sgctl.py validate-package /tmp/sg-build-a --strict` — pass.
- `python3 scripts/sgctl.py validate-package /tmp/sg-build-b --strict` — pass.
- Full byte comparison of all 9 generated package files across both compile outputs — pass.
- `python3 scripts/probe-dev-history-contracts.py` — pass.
- `python3 scripts/test-user-stories.py` — 55/55 pass.
- `python3 scripts/probe-reference-taxonomy.py` — pass.
- `python3 scripts/probe-upstream-goal-compat.py` — pass.
- Release ZIP path traversal scan — pass.
- Release ZIP secret scan — pass.
- Release ZIP deterministic rebuild check — pass.

## Known caveat

`bash scripts/test.sh` contains the same checks, but in this sandbox the aggregate shell wrapper intermittently stalls under the tool runner while the underlying Python and probe gates complete independently. The release gate therefore records the underlying gates directly rather than pretending the wrapper completed cleanly in this runtime.
