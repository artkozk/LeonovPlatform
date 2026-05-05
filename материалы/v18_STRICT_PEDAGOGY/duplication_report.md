# Duplication report v18_STRICT_PEDAGOGY

- duplicate groups before: known generic batch titles README/Команда/Ошибка/Git state/Проверка/Контрольный артефакт plus repeated summaries
- exact duplicate practice/project bodies after: 0
- normalized duplicate practice/project bodies after: 0
- exact duplicate solutions after: 0
- normalized duplicate solutions after: 0
- max duplicate group after: 1

## Rewritten Groups
- README/Команда/Ошибка/Git state/Проверка replaced with concrete command, Git, terminal, CLI and Python tasks.
- Контрольный артефакт replaced with topic-specific project names and concrete deliverables.
- Repeated terminal/Git summaries rewritten with lesson-specific state checks.
- Set/dict tasks separated from later hash-map tasks by changing function contracts and implementation details.
- Git merge-conflict task no longer checks only README; it also requires a conflict-resolution artifact.
- Repeated title `Проверка сдачи` replaced with lesson-specific verification titles.

## Why Remaining Similarity Is Acceptable
- Some IDE tasks share the idea “run a command and inspect state”, because terminal and Git require observable state. The concrete required files, commands and git_checks differ.
- Python practices still use functions because the platform checks functions through pytest, but each function uses a different input/output contract and a different lesson tool.
- The validator now fails on exact/normalized duplicates, repeated generic titles, README-only tasks and Git steps without git_checks.

## Remaining Similarity
- No exact/normalized practice/project body or solution duplicates by current normalizer.

## Final Result
- PASS if validate_course.py passes
