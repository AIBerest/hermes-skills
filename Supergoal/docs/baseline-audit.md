# Baseline audit — chip-supergoal Architect+ v3 Phase 1

Generated: 2026-06-25T22:34:17.181187+00:00

## Scope
- Phase 1 freezes current observable behavior and records known semantic/security escapes as expected-failure regression tests.
- The launched goal text referenced `<installed-skill-dir>/.supergoal/architect-plus-v3-upgrade`, but the verified package was relocated to `<workspace-dir>/.supergoal/chip-supergoal-architect-plus-v3-upgrade` to avoid polluting the skill self-test launch-marker scan. This path drift is recorded and should be corrected by future launch generation.

## Source hashes
- `<home-dir>/.hermes/document_cache/doc_fbdd75e323cd_CHIP_SUPERGOAL_ARCHITECT_PLUS_UPGRADE_PLAN-1.md` — sha256 `b000e0882a340ea39970c5748e5e282d6add09cbaf87745ee0ff292a45b34f15` — bytes 94826
- `<installed-skill-dir>/SKILL.md` — sha256 `ed51792c1c571c2283d0d5bd2a90fbbce44f8db1a3e01d100e553f7423f6108d` — bytes 14982
- `<installed-skill-dir>/scripts/test.sh` — sha256 `5b933f625da9294f4669ff1806c931bf86b269b65298dd99c76b0e13532cbc9d` — bytes 18569
- `<installed-skill-dir>/scripts/validate-phase.sh` — sha256 `06154d9ea3621addd5e4203c51d115bb088c25c1eb2de9a0625ae5589698bdb1` — bytes 3990
- `<installed-skill-dir>/scripts/validate-loop-design.sh` — sha256 `fd5d92c11807945c04e3b3a127a1edb989c6293e6ce5963b20997637630350c6` — bytes 4712
- `<installed-skill-dir>/templates/delivery/package-final-artifacts.sh` — sha256 `ecc86c85817d6dc70b29ec7352f403a4854056aa6928771b08f650ad90ccadc4` — bytes 1227
- `<installed-skill-dir>/templates/delivery/send-review-md-files.sh` — sha256 `ee742012ca499ef569704d9acf0124dac612ddb49859e90f0f4e3b6820d39acf` — bytes 2188
- `<installed-skill-dir>/templates/delivery/send-final-artifacts.sh` — sha256 `f73422c132a623d38bc1fe535320fef92dbd1e1cc286cd355b77aeca2c673667` — bytes 1598

## Current SuperGoal package inventory
- `LAUNCH_GOAL.md` — sha256 `2e181710ae86674d3e8043a5b208dd1c1c0107a0c8478e40d44c445383b56daf` — bytes 1633
- `LOOP_DESIGN.md` — sha256 `6072436b3869cbb2b5909b3325eab6f95be76e7357344b458d121e6d8ef1ce84` — bytes 5133
- `MANIFEST.planner.json` — sha256 `7c847b08167763a12fe15b18a7a6cc5a8ada0d2b2c0b8e08cddb9db20245e333` — bytes 630
- `PROTOCOL.md` — sha256 `82c58abd8c6ae935a3292d2783d2d5ee160757acca21279e073bf700242319e4` — bytes 19111
- `RESEARCH.md` — sha256 `10e87448751bd9051351dc806217bbdcba4357258c953e7477e1a8572b204922` — bytes 2545
- `ROADMAP.md` — sha256 `1a6cdd57d0f1be2abbe8a52c225f92d9598380830771b7941a3887c7ad21192e` — bytes 12192
- `STATE.md` — sha256 `4c1e7be604a6c05cb28a4ff0e6caf966b7135f4333d7c64f16fc6548568eae9b` — bytes 813
- `THINKING.md` — sha256 `a3be6cd9a423459a61582a8da2455df5c648f64b94fea7547c1c570237b7cc3b` — bytes 4129
- `phases/phase-01.md` — sha256 `6ac1040e6a7d2c87df3ec7772831333ac5be4cedf5184ea29682267eaf2835e1` — bytes 1738
- `phases/phase-02.md` — sha256 `2b93bde9d17ca7a1425979677fab882fafd207e75be1887f4bc3c4a9b7e5a292` — bytes 1701
- `phases/phase-03.md` — sha256 `75a6888b9298ea86ac8b099212cc7809a00c9f128349f5b295e575dc9fc243e6` — bytes 1726
- `phases/phase-04.md` — sha256 `5ed586cc64efbefb6326b6f53f57c1af5c69b5e0a74c52d628eae5b9581ecf6d` — bytes 1739
- `phases/phase-05.md` — sha256 `fc53d668d77fc89ffb9c52ab70000a732fbf7f225a9bf753767b94ad2d162aaa` — bytes 1742
- `phases/phase-06.md` — sha256 `af0a061bf3a2487bd0e17e721499eac65a8651d8d7403cff91581704acdeb4e3` — bytes 1754
- `phases/phase-07.md` — sha256 `d8632a96f84058e06eb248486de7f8130496affca83a4d8ca4f749d0174f8840` — bytes 1669
- `phases/phase-08.md` — sha256 `6db26f7271426223fae76b082a147504fa579b316dce0aaf38946371da4323a4` — bytes 1738
- `phases/phase-09.md` — sha256 `f9201bce744211bd76f8a84fd9ac0ad8803d60f633416875a2611d6621725530` — bytes 1736
- `phases/phase-10.md` — sha256 `fd9a30b4c2c9e423ca4dc18010177dccae753a4b3d8c9294dbf5d24c51d3b4ff` — bytes 1721
- `phases/phase-11.md` — sha256 `35f2a758716750e70057e3b66a96a333a0f52a2b422fbf680187580adc61fcaa` — bytes 1675
- `phases/phase-12.md` — sha256 `79d95d38675eda6957eb50a526d2fec49126ed856def07e64a43417184aa20e7` — bytes 1742
- `phases/phase-13.md` — sha256 `0553d2d4387045761b163b8227fdce54a32313ed8f188052c27e1dfab0a12521` — bytes 1754
- `review-md-files-delivery-receipt.json` — sha256 `ba85ea39268b36bed3c3ae48cb4c51e270f92cdfb53c5a48625ea9583c78a77b` — bytes 1124
- `scripts/detect-env.sh` — sha256 `8ec2c89b64c91320d49b53c7aee9578b9a754b5ff8bf7121c10a8fa1161261a5` — bytes 1399
- `scripts/detect-stack.sh` — sha256 `239a27920bfff96b0dc79eec2143309dd12aed279dc79a3aaa1b6dc6d3789d81` — bytes 4438
- `scripts/repo-state.sh` — sha256 `d9ab904fafb0f320fc3bea545fbb971551231a1baf0562e535e5afefcf8e028f` — bytes 5888
- `scripts/summarize-repo.sh` — sha256 `99ea7c71df11d680760fdc31d6f2fa69fb96969e21c475688e87554eed9a36af` — bytes 3376
- `scripts/validate-loop-design.sh` — sha256 `fd5d92c11807945c04e3b3a127a1edb989c6293e6ce5963b20997637630350c6` — bytes 4712
- `scripts/validate-phase.sh` — sha256 `06154d9ea3621addd5e4203c51d115bb088c25c1eb2de9a0625ae5589698bdb1` — bytes 3990

## Commands and outputs

### `python3 -m unittest discover -s tests`
Exit: `0`
**stdout**
```text
<empty>
```
**stderr**
```text
xxxxx.
----------------------------------------------------------------------
Ran 6 tests in 0.400s

OK (expected failures=5)
```

### `bash scripts/test.sh`
Exit: `0`
**stdout**
```text
PASS: shell syntax
PASS: install layout contains required assets
PASS: loop-design template validates
PASS: validate-loop-design instantiated fixture validates
PASS: validate-loop-design rejects weak instantiated loop
PASS: validate-loop-design rejects missing sections
PASS: validate-loop-design rejects launch body
PASS: private-boundary scan
PASS: phase-01 regression fixtures (expected failures documented)
PASS: artifact boundary and stale-phrase contract
PASS: root architecture contract
PASS: launch body canonical placement
PASS: marker contract
PASS: generated protocol is self-contained
PASS: preservation docs match upstream-shaped rail
PASS: gitignore protects runtime/secrets (skipped outside git)
PASS: validate-phase positive fixture
PASS: validate-phase rejects empty sections
PASS: validate-phase anchors exact headings
PASS: validate-phase requires RPD metadata
PASS: validate-phase rejects placeholder bullets
PASS: phase template validates after fill
PASS: protocol continues through phase boundaries
PASS: dev-history hardening contracts
PASS: dev-history hardening contracts
USER_STORY_TESTS total=55 passed=55 failed=0
PASS: user-story contract coverage
PASS: reference taxonomy contracts
PASS: reference taxonomy contracts
PASS: upstream /goal compatibility contracts
PASS: upstream goal compatibility contracts
PASS: repo-state regressions
PASS: detect-env minimal env
PASS: git diff --check (skipped outside git)
```
**stderr**
```text
xxxxx.
----------------------------------------------------------------------
Ran 6 tests in 0.391s

OK (expected failures=5)
```

### `bash scripts/validate-phase.sh tests/fixtures/v2-invalid/phase-99-of-1-rpd-mismatch.md`
Exit: `0`
**stdout**
```text
✓ tests/fixtures/v2-invalid/phase-99-of-1-rpd-mismatch.md: structure ok (21 lines, 1 acceptance bullets, 1 warnings)
```
**stderr**
```text
⚠️  tests/fixtures/v2-invalid/phase-99-of-1-rpd-mismatch.md: only 1 acceptance bullet(s) — criteria may be thin
```

### `bash scripts/validate-loop-design.sh --instantiated tests/fixtures/v2-invalid/loop-one-word.md`
Exit: `0`
**stdout**
```text
✓ tests/fixtures/v2-invalid/loop-one-word.md: loop design instantiated ok (37 lines)
```
**stderr**
```text
<empty>
```

### `SUPERGOAL_ROOT=$tmp/.supergoal bash templates/delivery/package-final-artifacts.sh  # symlink fixture`
Exit: `0`
**stdout**
```text
/tmp/tmpc9wuwy11/.supergoal/out/final-artifacts.zip
824add5b9f9c82d78f33b9b04677d8ee8a2c1300c353228f32126d0de7871561

ZIP members: ["escape.txt", "safe.txt"]
ZIP contains outside-content: True
```
**stderr**
```text
<empty>
```

### `forged minimal review receipt then send-review-md-files.sh`
Exit: `0`
**stdout**
```text
review files already sent for target+hash
```
**stderr**
```text
<empty>
```

### `forged minimal final receipt then send-final-artifacts.sh`
Exit: `0`
**stdout**
```text
final artifacts already sent for target+hash
```
**stderr**
```text
<empty>
```

## Baseline verdict
- Aggregate suite is green with 5 expected failures documenting current known escapes.
- Current v2 validators still accept the malformed phase and one-word loop fixtures.
- Current package script follows a symlink into ZIP content.
- Current delivery scripts skip real transport when given minimal forged receipts.
- These xfail cases are now executable regression targets for later phases; they must be converted to normal passing tests when the corresponding fixes land.
