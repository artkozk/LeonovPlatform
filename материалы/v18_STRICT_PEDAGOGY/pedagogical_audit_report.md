# Pedagogical audit report v18_STRICT_PEDAGOGY

- total lessons checked: 169
- weak lessons before fixes: 38 known duplicate/topic-alignment groups plus generic theory hits
- weak lessons after fixes: 0 by automated topic-contract gates
- lessons rewritten: 66
- steps rewritten: 532

## Examples of fixed lessons
- Полиморфизм: renderer-copy заменён на payment providers, notification senders, serializers, discount policies, storage adapters.
- Абстракции: renderer-copy заменён на repository boundary, payment gateway, mailer adapter, unit of work, clock, access policy.
- Redis: generic CSV/inventory/state tasks заменены на GET/SET, TTL, counters, invalidation, rate limit и lock.
- S3 и MinIO: generic state/priority tasks заменены на bucket/object key/upload/download/metadata/presigned URL/size limit.
- Алгоритмы: сложность: generic tasks заменены на O(n), O(log n), nested loop, operation budget и выбор структуры данных.

## Remaining risks
- Статус остаётся STAGING READY: массовый запуск требует staging-import и реального прогона IDE-plugin на проектных gates.

## Final status
- STAGING READY


## Method
Проверка не доверяет старым отчётам. Она читает course_import.json, берёт только practice/project steps, сравнивает exact body, normalized body, exact solution_code и normalized solution_code. Нормализация убирает имена функций и классов, чтобы повтор, отличающийся только именем, не проходил как уникальный.

## Reviewer notes
Оставшиеся похожие форматы уроков допустимы только как структура урока: теория, вопросы, практика, граничный случай, мини-проект. Сами проверяемые задачи после правок отличаются контрактом, входом, выходом, edge case и checker-кодом. Если новая независимая проверка найдёт группу больше 1, пакет должен получить NOT READY, а не PASS.

## Deployment gate
Перед массовым запуском нужно импортировать пакет на staging, пройти первые 30 уроков как студент, запустить IDE-plugin на выбранных Git/FastAPI/Docker/final-project gates и сверить скрытые проверки с mentor_handbook.md.
