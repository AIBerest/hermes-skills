# Release checklist — chip-supergoal Architect+ v3

## Mandatory local gates

- [ ] `bash scripts/test.sh`
- [ ] `python3 -m unittest discover -s tests`
- [ ] `python3 scripts/sgctl.py validate-contract examples/brownfield-feature/CONTRACT.json --strict`
- [ ] `python3 scripts/sgctl.py compile examples/brownfield-feature/CONTRACT.json --out /tmp/sg-build-a`
- [ ] `python3 scripts/sgctl.py compile examples/brownfield-feature/CONTRACT.json --out /tmp/sg-build-b`
- [ ] compare deterministic immutable outputs from both builds
- [ ] verify secure archive tests and receipt tampering tests pass
- [ ] verify reference catalog/generated index are consistent
- [ ] verify v2 migration fixtures pass

## Release metadata

- [ ] `VERSION` matches the top `CHANGELOG.md` heading
- [ ] generated package manifest has stable fingerprint
- [ ] CI uses least permissions (`contents: read`)
- [ ] GitHub actions are pinned by full SHA
- [ ] public-clean build/profile contains no private operator defaults

## Graduation blockers

Do not label the release Architect+ while any P0/P1 finding, strict semantic failure, security failure, E2E failure, reproducibility failure, migration failure, or reference/invariant traceability gap remains open.

## Alpha.2 coffee-review evidence

- [x] `python3 -m unittest discover -s tests` — 67 tests, 1 skipped, pass in local release workspace.
- [x] `python3 scripts/sgctl.py validate-contract examples/brownfield-feature/CONTRACT.json --strict`.
- [x] Two independent compiles to `/tmp/sg-build-a` and `/tmp/sg-build-b` validate strictly and compare byte-identical across all 9 generated files.
- [x] `validate-package` catches manual generated-view drift, manifest hash drift, and unsealed file-set drift.
- [x] Compiler refuses unsealed existing output directories and source-container targets.
- [x] Secret scan and deterministic release ZIP self-check completed for the attached alpha.2 archive.
