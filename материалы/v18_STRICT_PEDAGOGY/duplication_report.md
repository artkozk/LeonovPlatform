# Duplication report v18_STRICT_PEDAGOGY

## Итог после правок
- exact duplicate bodies after: 0
- normalized duplicate bodies after: 0
- exact duplicate solutions after: 0
- normalized duplicate solutions after: 0
- max duplicate group after: 1

## Переписанные группы
- Единый интерфейс в полиморфизме и абстракциях заменён на providers, senders, serializers, policies, adapters, repositories и service boundaries.
- Cache TTL, Inventory delta, State transition, CSV columns, Priority queue, Retry log удалены из чужих уроков; Redis/S3/network/algorithms получили свои задачи.
- Повторяющиеся OOP-задачи по атрибутам, методам, инкапсуляции, магическим методам и dataclasses заменены на разные объектные контракты.

## Статус
- PASS по строгому duplicate-аудиту.


## Method
Проверка не доверяет старым отчётам. Она читает course_import.json, берёт только practice/project steps, сравнивает exact body, normalized body, exact solution_code и normalized solution_code. Нормализация убирает имена функций и классов, чтобы повтор, отличающийся только именем, не проходил как уникальный.

## Reviewer notes
Оставшиеся похожие форматы уроков допустимы только как структура урока: теория, вопросы, практика, граничный случай, мини-проект. Сами проверяемые задачи после правок отличаются контрактом, входом, выходом, edge case и checker-кодом. Если новая независимая проверка найдёт группу больше 1, пакет должен получить NOT READY, а не PASS.

## Deployment gate
Перед массовым запуском нужно импортировать пакет на staging, пройти первые 30 уроков как студент, запустить IDE-plugin на выбранных Git/FastAPI/Docker/final-project gates и сверить скрытые проверки с mentor_handbook.md.
