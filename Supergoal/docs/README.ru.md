# chip-supergoal

**chip-supergoal** — это skill для Hermes, который превращает нетривиальную инженерную задачу в проверяемый, файловый **SuperGoal package** и один стандартный handoff для Hermes `/goal`.

Он нужен для задач, где обычный план в чате слишком хрупкий: production-adjacent изменения, рискованные рефакторы, миграции, безопасность, длинная многофазная разработка и автономное исполнение, где нужны состояние, доказательства и финальный аудит.

English documentation: [`../README.md`](../README.md)

## Что делает skill

`chip-supergoal` — это **planner/compiler**, а не исполнитель.

Он создаёт директорию `.supergoal/` с артефактами:

- `THINKING.md` — цель, ограничения, риски, допущения, использованный контекст.
- `RESEARCH.md` — generated research gate record, если нужны свежие факты или внешний контекст.
- `reports/research.json` — machine-readable отчёт provider/status/sources, когда research gate активен.
- `LOOP_DESIGN.md` — дизайн исполнительного цикла: host, reviewer/judge, проверки, stop conditions, recovery, boundaries.
- `ROADMAP.md` — карта фаз, acceptance criteria, обязательные команды, требования к evidence.
- `STATE.md` — стартовое состояние и текущая фаза.
- `PROTOCOL.md` — самодостаточный протокол для будущего `/goal` запуска.
- `LAUNCH_GOAL.md` — единственный файл с launch body, начинающимся с `SUPERGOAL_GOAL_BODY:`.
- `phases/phase-N.md` — строгие спецификации фаз.
- helper scripts и delivery receipts, если workflow требует доставки файлов.

После этого отдельная Hermes `/goal` сессия читает пакет и выполняет работу. Завершение считается валидным только после финального аудита и маркеров вроде `AUDIT_COMPLETE` и `SUPERGOAL_RUN_COMPLETE`.

## Зачем это нужно

У агентной разработки есть типовые провалы:

1. Агент начинает делать, не зафиксировав реальную цель.
2. Длинная задача теряет состояние между turns.
3. “Готово” пишется до тестов, деплоя или доказательств.
4. Рискованные изменения проходят без review.
5. План нельзя безопасно передать другому исполнителю.

`chip-supergoal` закрывает эти провалы через package contract:

- явные фазы;
- обязательные verification commands;
- evidence requirements;
- risk/RPD review gates;
- state и recovery правила;
- строгую позицию launch-marker;
- validation и manifest integrity checks.

## Быстрый старт

Склонируйте или установите репозиторий как Hermes skill directory, затем загрузите skill в Hermes.

Типичный вызов:

```text
/chip-supergoal Build or refactor X end-to-end
```

Проверить репозиторий локально:

```bash
python3 -m unittest discover -s tests
bash scripts/test.sh
```

Скомпилировать пример:

```bash
python3 scripts/sgctl.py compile examples/brownfield-feature/CONTRACT.json --out /tmp/example-supergoal
python3 scripts/sgctl.py validate-package /tmp/example-supergoal --strict
```

Посмотреть результат:

```bash
ls -la /tmp/example-supergoal
sed -n '1,80p' /tmp/example-supergoal/LAUNCH_GOAL.md
```

## CLI: `sgctl.py`

В репозитории есть `scripts/sgctl.py` — утилита для contract/package операций.

### Research provider gate

Если перед планом нужны свежие факты, добавьте `compatibility.research_gate` в `CONTRACT.json`. Предпочтительный provider — `perplex`; official docs, Context7, generic web search или manual research должны указывать `provider_unavailable_reason`, если Perplex не использовался.

Минимальный satisfied gate:

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

Проверить gate:

```bash
python3 scripts/sgctl.py research-gate examples/brownfield-feature/CONTRACT.json --format json
python3 scripts/sgctl.py validate-contract examples/brownfield-feature/CONTRACT.json --strict
```

Compile пишет `RESEARCH.md` и `reports/research.json`; `validate-package` ловит drift в обоих файлах.

Основные команды:

```bash
# Проверить v3 contract
python3 scripts/sgctl.py validate-contract examples/brownfield-feature/CONTRACT.json --strict

# Скомпилировать contract в sealed SuperGoal package
python3 scripts/sgctl.py compile examples/brownfield-feature/CONTRACT.json --out /tmp/example-supergoal

# Проверить generated package
python3 scripts/sgctl.py validate-package /tmp/example-supergoal --strict

# Мигрировать старый v2-style package, если поддерживается
python3 scripts/sgctl.py migrate-v2 <old-package-root> --out <new-contract-or-package>
```

## Модель безопасности

### Граница planner/executor

Skill планирует и компилирует. Он **не выполняет** implementation phases сам. Это намеренная граница: пакет должен быть читаемым, проверяемым и исполнимым отдельной стандартной `/goal` сессией.

### Один launch body

Настоящий launch body должен быть ровно один — в `LAUNCH_GOAL.md`.

Другие файлы могут объяснять процесс запуска, но не должны содержать ещё одну реальную строку:

`SUPERGOAL_GOAL_BODY:`

Это защищает от случайного запуска stale/duplicate goal.

### Sealed package

Generated package содержит `MANIFEST.json`: path, sha256, bytes, mode и package fingerprint.

`validate-package` ловит:

- ручное изменение generated Markdown относительно `CONTRACT.json`;
- drift hash/size/mode;
- лишние unsealed файлы;
- отсутствие обязательных файлов;
- unsafe/duplicate manifest paths;
- неправильное место launch-marker.

### Защита от destructive overwrite

Compiler отказывается писать в опасные targets:

- произвольные существующие директории, которые не являются sealed package;
- package с другим goal ID;
- изменённый contract без корректного `contract_revision`;
- source-container targets;
- started/runtime packages с runtime state или delivery output.

## Структура репозитория

```text
.
├── SKILL.md                      # Hermes skill entrypoint и operating contract
├── README.md                     # English documentation
├── docs/README.ru.md             # Русская документация
├── lib/chip_supergoal/           # Contract, compiler, validator, state, audit logic
├── scripts/                      # sgctl и verification/probe scripts
├── spec/                         # JSON schemas и policy catalogs
├── templates/                    # Templates generated package
├── references/                   # Детальные workflow/invariant references
├── examples/                     # Example contracts
└── tests/                        # Unit, semantic, rendering, security, migration, e2e tests
```

## Тесты

Полный локальный gate:

```bash
bash scripts/test.sh
```

Python tests напрямую:

```bash
python3 -m unittest discover -s tests
```

Полезные focused tests:

```bash
python3 -m unittest tests.rendering.test_compile_determinism
python3 -m unittest tests.semantic.test_sgctl_semantic_validation
python3 -m unittest tests.security.test_archive_symlink tests.security.test_forged_receipt
```

## Workflow разработки

1. Измените code/templates/references/tests.
2. Запустите focused tests для изменённой зоны.
3. Запустите `python3 -m unittest discover -s tests`.
4. Запустите `bash scripts/test.sh`.
5. Скомпилируйте example package и провалидируйте его strict mode.
6. Проверьте, что реальный `SUPERGOAL_GOAL_BODY:` есть только в `templates/LAUNCH_GOAL.md`.

Финальный gate:

```bash
python3 -m unittest discover -s tests
bash scripts/test.sh
python3 scripts/sgctl.py compile examples/brownfield-feature/CONTRACT.json --out /tmp/chip-supergoal-example
python3 scripts/sgctl.py validate-package /tmp/chip-supergoal-example --strict
```

## Public-use notes

Репозиторий содержит public-safe source skill и validation harness. Runtime state, локальные generated `.supergoal/` packages, credentials, receipts, caches и deployment artifacts не должны попадать в git.

Если адаптируете skill под другой agent runtime, сохраняйте инварианты:

- одна launch surface;
- явная граница planner/executor;
- validation generated package;
- никакого false completion без final audit;
- risk-aware review gates;
- state recovery и blocker semantics.

## Лицензия

MIT. См. [`../LICENSE`](../LICENSE).
