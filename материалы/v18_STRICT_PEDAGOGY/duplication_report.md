# Duplication report v18_STRICT_PEDAGOGY

## Итог после правок
- exact duplicate bodies after: 0
- normalized duplicate bodies after: 0
- exact duplicate solutions after: 0
- normalized duplicate solutions after: 0
- max duplicate group after: 1

## Theory Duplicate / Generic Audit
- generic theory hits before: 245
- generic theory hits after: 0
- topic-contract theory failures after: 0
- value/print generic examples after: 0

## Переписанные группы
- Единый интерфейс в полиморфизме и абстракциях заменён на providers, senders, serializers, policies, adapters, repositories и service boundaries.
- Cache TTL, Inventory delta, State transition, CSV columns, Priority queue, Retry log удалены из чужих уроков; Redis/S3/network/algorithms получили свои задачи.
- Повторяющиеся OOP-задачи по атрибутам, методам, инкапсуляции, магическим методам и dataclasses заменены на разные объектные контракты.
- Универсальные theory steps заменены на объяснение конкретной темы урока.

## Статус
- PASS по duplicate-аудиту.
- STAGING READY до реального IDE-plugin прогона на staging.

## Method
Аудит читает `course_import.json`, берёт только student-facing practice/project body и `solution_code`, затем сравнивает exact и normalized формы. Нормализация убирает имена функций, классов, числовые маркеры и технические id, поэтому задача не считается уникальной, если меняется только название функции или урока.

## Why Remaining Similarity Is Acceptable
Оставшееся сходство относится к учебной структуре урока: theory, structured questions, practice, edge/debug step, mini-project. Проверяемые задачи после правок отличаются входом, выходом, edge case, checker-кодом или topic contract. Если будущая независимая проверка найдёт группу practice/project больше 1, пакет должен получить NOT READY.

## Deployment Gate
Перед массовым запуском нужно импортировать пакет на staging, пройти первые 30 уроков как студент, запустить IDE-plugin на Git/FastAPI/Docker/final-project gates и сверить hidden checks с `mentor_handbook.md`.
