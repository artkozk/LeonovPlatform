# QA report v15_PRODUCTION_DEEPENED

PASS/FAIL: PASS

## Critical blockers
- не найдено

## Hard fail rules
- первый урок должен быть `Первый код` и первый шаг `Смысл`;
- practice без checker запрещены;
- project без IDE/AI проверки запрещены;
- test без structured questions запрещены;
- body_markdown не содержит служебные секции, solution/checker/admin и banned-фразы;
- manifest и JSON совпадают построчно;
- coverage_matrix не содержит missing/thin/placeholder;

## Quantitative audit
- modules: 5
- lessons: 169
- steps: 2132
- hours: 867.08
- practice tasks: 933
- project/IDE tasks: 507
- structured questions: 335
- SQL query tasks: 221
- SQLite/sqlite3 steps: 104
- Git steps: 112
- FastAPI steps: 616
- Docker/CI/CD/DevOps steps: 181

## Duplicate and semantics audit
- exact duplicate body_markdown: 0
- duplicate body groups: 0
- duplicate learning objectives: 0
- unique learning objectives: 1292
- semantic objective uniqueness is treated as a hard gate, not as a warning.

## Solution audit
- practice with empty solution_code: 0
- project with empty solution_code: 0
- IDE/project solutions include expected files, commands, successful output shape and decision notes.

## Checker audit
- unique IDE checker signatures: 471
- max IDE signature repeat: 2
- Git labs check dirty worktree, conflict markers, branches, commit count, reflog/stash/force-with-lease scenarios.
- DevOps labs include runtime checks: container start, healthcheck, env, tests inside container, deploy dry-run and rollback dry-run.
- Final gates include gate_checks with required artifacts and pass/fail criteria.

## Deep-topic audit
- SQL advanced includes LEFT JOIN anti-patterns, window ranking, CTE aggregation, transactions with rollback/savepoint, indexes with EXPLAIN and lock/isolation simulations.
- FastAPI tasks include 201/204/401/404/422 checks, request bodies, routers, auth, SQLAlchemy, TestClient and integration paths.
- Docker/CI/CD/Deploy tasks check real runtime meaning instead of only file presence.
- Final project gates are split into requirements, user stories, DB schema, API contract, Git workflow, FastAPI structure, SQLAlchemy, Alembic, auth, CRUD, tests, Docker, CI/CD, AI integration, logging, README, deploy and defense.

## Hidden-test audit
- hidden tests cover empty values, wrong types, missing ordering, SQL injection, 401/404/422, dirty git trees, missing env files, missing healthcheck and rollback paths.

## Manual QA required before launch
- import package on staging;
- compare imported counts against manifest.csv;
- complete first 10 lessons as a student;
- manually sample 50-100 steps across Python, Git, SQLite, SQL, FastAPI, Docker and final gates;
- run IDE plugin on a real Git/FastAPI/Docker/final-project repository;
- complete one final project end to end including deploy and defense;
- run mentor dry-run for hidden-test complaints and recovery routes.

## 20 худших шагов
- критичных кандидатов после автоматического аудита не найдено; ручная выборка на staging обязательна, потому что автоматическая проверка не оценивает педагогическую интонацию на уровне живого студента.

## Итог
Пакет считается готовым только при PASS всех quality gates выше и после ручного staging-регламента.
