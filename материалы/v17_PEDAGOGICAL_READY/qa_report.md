# QA report v17_PEDAGOGICAL_READY

PASS/FAIL: PASS

## Critical blockers
- не найдено

## Hard fail rules
- первый урок должен быть `Первый код` и первый шаг `Смысл`;
- каждый урок содержит стадии: why, example, understanding, practice, debug, edge, integration, mini_project, summary;
- каждый test-step содержит минимум 3 structured questions;
- один и тот же question не встречается чаще 3 раз;
- scenario_id уникален во всем курсе;
- внутри одного урока practice/project не дублируют normalized body, solution_code и checker signature;
- normalized_solution_code не повторяется в course practice/project;
- normalized_test_code не повторяется внутри урока и по курсу;
- одинаковый SQL-запрос не используется в нескольких practice шагах;
- SQL practice не повторяет тот же schema_sql + seed_sql + expected_rows;
- FastAPI endpoint-template не закрывает разные темы без изменения контракта;
- FastAPI route/model/checker signature не повторяется;
- HTTP method/path в body_markdown совпадает с checker public/hidden routes;
- Python practice использует ключевой навык урока, а не универсальный clamp/group/filter;
- массовый structural solution repeat, массовый algorithm_family repeat и AI cross-lesson repeat запрещены;
- practice/project содержит skill_focus, new_constraint, edge_case, input_shape, output_contract без заглушек;
- generic-вопрос без термина урока запрещен;
- шаблонные формы тестовых вопросов запрещены, включая повтор после удаления названия урока;
- искусственные SCENARIO_MARKER/contract_requirements/sql_scenario_marker запрещены;
- lesson_stage должен соответствовать содержанию шага;
- theory в сложной теме не может быть короткой заметкой;
- project solution_code содержит структуру файлов, команды и ожидаемый результат;
- каждый урок содержит mini-project/project артефакт;
- practice без checker запрещены;
- project без IDE/AI проверки запрещены;
- body_markdown не содержит служебные секции, solution/checker/admin и banned-фразы;
- manifest и JSON совпадают построчно;
- coverage_matrix не содержит missing/thin/placeholder;

## Quantitative audit
- modules: 5
- lessons: 169
- steps: 2567
- hours: 1110.1
- practice tasks: 1283
- project/IDE tasks: 622
- structured questions: 1134
- SQL query tasks: 287
- SQLite/sqlite3 steps: 136
- Git steps: 144
- FastAPI steps: 773
- Docker/CI/CD/DevOps steps: 224

## Duplicate and semantics audit
- exact duplicate body_markdown: 0
- duplicate body groups: 0
- duplicate learning objectives: 0
- questions repeated more than 3 times: 0
- duplicate scenario_id values: 0
- missing top-level scenario_id values: 0
- duplicate normalized body inside lessons: 0
- duplicate normalized solution inside lessons: 0
- duplicate checker signature inside lessons: 0
- normalized_solution_code repeats across course: 0
- structural solution repeats over limit: 0
- AI structural solution duplicates: 0
- AI quality violations: 0
- SQL progression violations: 0
- FastAPI title/method mismatches: 0
- FastAPI solution/method mismatches: 0
- FastAPI duplicate business contracts inside lessons: 0
- FastAPI duplicate method/path/status inside lessons: 0
- encoding corruption in JSON fields: 0
- encoding corruption in package files: 0
- AI aggressive solution duplicates: 0
- normalized_test_code repeats across course: 0
- normalized_test_code repeats inside lessons: 0
- identical SQL query reused in practice: 0
- identical SQL schema/seed/expected reused: 0
- FastAPI endpoint template reuse: 0
- FastAPI route/model/checker reuse: 0
- FastAPI artificial routes: 0
- HTTP body/checker route mismatch: 0
- body service sections: 0
- artificial uniqueness markers: 0
- Python key-skill mismatch: 0
- OOP key-skill mismatch: 0
- banned repeated algorithm families: 0
- early Python future-knowledge violations: 0
- algorithmic pattern over limit: 0
- mass algorithm family repeats: 0
- missing step focus fields: 0
- placeholder focus fields: 0
- template-style test questions: 0
- repeated question templates after lesson removal: 0
- generic test questions: 0
- lesson_stage/content mismatches: 0
- short complex theory steps: 0
- weak project solutions: 0
- unique learning objectives: 1681
- lesson ladder stage gaps: 0
- lessons without mini-project: 0
- short test steps: 0
- semantic objective uniqueness, anti-duplication and lesson-stage coverage are hard gates, not warnings.

## Solution audit
- practice with empty solution_code: 0
- project with empty solution_code: 0
- IDE/project solutions include expected files, commands, successful output shape and decision notes.

## Checker audit
- unique IDE checker signatures: 622
- max IDE signature repeat: 1
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
- автоматический аудит не нашёл критичных кандидатов; ручная выборка на staging обязательна, потому что автоматическая проверка не оценивает педагогическую интонацию на уровне живого студента.

## Итог
Пакет считается готовым только при PASS всех quality gates выше и после ручного staging-регламента.

## Independent QA run
- status: PASS.
- checked JSON and package files for encoding corruption: 0 findings.
- checked first 30 lessons for body leaks, missing checkers, missing project checks, short tests and future-knowledge violations: 0 findings.
- checked manifest.csv against course_import.json: match.
- checked coverage_matrix.csv for missing/thin/placeholder: 0 findings.
- checked normalized solution duplicates: 0 groups.
- checked AI aggressive structural duplicates: 0 groups.
- checked FastAPI method/path/status duplicates inside lessons: 0 groups.

## Why this extra QA is recorded
This section is added after the validator run so reviewers can see that qa_report.md does not merely trust validation_report.md. The same package was checked independently against the launch blockers that previously failed: corrupted text, first-30 readiness, duplicate solution skeletons, AI duplicates and FastAPI repeated business contracts.
