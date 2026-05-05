# Python v18 Git/CLI Batch and SQL Context Cleanup - 2026-05-05

## Current behavior
The v18 strict pedagogy package now treats `course_import.json` as the source of truth for the Python course import. This iteration rewrites the end of Module 1 around Git, remotes, the CLI task manager project, and Exam 1. The rewritten lessons are:

- `m01_l026_git-vetki`
- `m01_l027_git-otmena-izmeneniy`
- `m01_l028_git-merge-i-rebase`
- `m01_l029_github-i-remote`
- `m01_l030_cli-proekt-menedzher-zadach`
- `m01_l031_ekzamen-1`

The Git lessons now use IDE-plugin checks with real `git_checks`: branches, clean working tree, required commits, remote/upstream, tags, status and log commands. The CLI project now checks real task-manager files and commands instead of a generic README artifact.

## Why this was done
The previous package passed the structural validator, but the end of Module 1 still had generic project-style tasks and did not consistently prove Git state. This is risky for a large student flow because students can submit a file that exists without demonstrating the actual Git skill. The updated checks make the required state explicit and easier to debug during support.

## SQL context cleanup
This iteration also removes non-topic `sql_query` tasks from lessons where SQL is not the subject. Those tasks are replaced with topic-aligned checkers:

- `python_pytest` for Python/session/repository behavior;
- `http_api` for FastAPI contracts;
- `ide_plugin` for project gates.

SQL checkers remain allowed only in SQL-like lessons such as SQL, SQLite, ClickHouse/OLAP, indexes, schema design, and database project gates.

## Validator gates added
`validate_course.py` now fails on these additional quality issues:

- practice/project title repeated more than five times;
- universal hands-on titles such as `Контрольный артефакт`, `Мини-проект`, `SQL-файл`, `Команда`, `Ошибка`, `Git state`, `Проверка`, `README`;
- `sql_query` outside a SQL-like lesson context;
- Git/GitHub IDE-plugin tasks without `git_checks`;
- IDE projects without `required_files` or `commands`;
- practice/project body shorter than 350 characters;
- generic visible wording such as `проверяемый артефакт`;
- missing Git/CLI gates in the target Module 1 batch.

## Import migration behavior
The generated migration `backend/migrations/031_reseed_python_zero_v18_no_duplicate_tasks.sql` now stores pytest checker payloads with `pytest_code` and strips the legacy nested `test_code` key from source policy. This is required because the import validation gate rejects mixed pytest key formats.

## Verification performed

```powershell
python .\материалы\v18_STRICT_PEDAGOGY\validate_course.py
node backend/tools/generate_python_v18_materials_migration.js
node backend/tools/validate_python_v18_materials_import.js
git diff --check
cd backend; go test ./...
cd frontend; npm run build
```

Current expected validation metrics:

- modules: 5
- lessons: 169
- steps: 1960
- practice: 769
- project: 377
- questions: 921
- sql_query outside SQL-like context: 0
- repeated practice/project titles > 5: 0
- Git IDE-plugin tasks without git checks in the target batch: 0

## Review notes
This update intentionally does not claim the whole course is ready for mass launch. The current batch is ready for student testing, but later modules still need the same manual pedagogy pass and staging IDE-plugin smoke testing before a large launch.
