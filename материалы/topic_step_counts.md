# Количество шагов по темам

Файл отвечает на вопрос, сколько практики заложено по каждой теме roadmap. Источник данных — `coverage_matrix.csv`, который пересобирается вместе с `course_import.json`.

| Тема | Всего шагов | Практика | Проекты | Проверки | Статус |
|---|---:|---:|---:|---|---|
| AI для учёбы | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| среда и терминал | 36 | 15 | 6 | ide_plugin; python_stdout; quiz_single | covered |
| Git и GitHub | 108 | 45 | 18 | ide_plugin; python_stdout; quiz_single | covered |
| Python Core | 288 | 120 | 48 | ide_plugin; python_stdout; quiz_single | covered |
| CLI-проект | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| ООП | 120 | 50 | 20 | ide_plugin; python_pytest; quiz_single | covered |
| магические методы | 12 | 5 | 2 | ide_plugin; python_pytest; quiz_single | covered |
| протоколы | 12 | 5 | 2 | ide_plugin; python_pytest; quiz_single | covered |
| наследование и полиморфизм | 24 | 10 | 4 | ide_plugin; python_pytest; quiz_single | covered |
| типизация | 36 | 15 | 6 | ide_plugin; python_stdout; quiz_single | covered |
| threading | 12 | 5 | 2 | ide_plugin; python_pytest; quiz_single | covered |
| multiprocessing | 12 | 5 | 2 | ide_plugin; python_pytest; quiz_single | covered |
| asyncio | 48 | 20 | 8 | ide_plugin; python_pytest; quiz_single | covered |
| алгоритмы и структуры данных | 36 | 15 | 6 | ide_plugin; python_stdout; quiz_single | covered |
| SQL | 312 | 130 | 52 | ide_plugin; python_pytest; quiz_single; sql_query | covered |
| транзакции | 36 | 15 | 6 | ide_plugin; python_pytest; python_stdout; quiz_single; sql_query | covered |
| уровни изоляции | 12 | 5 | 2 | ide_plugin; quiz_single; sql_query | covered |
| блокировки | 12 | 5 | 2 | ide_plugin; quiz_single; sql_query | covered |
| индексы | 12 | 5 | 2 | ide_plugin; quiz_single; sql_query | covered |
| NoSQL | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| Redis | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| ClickHouse / OLAP | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| S3 / MinIO | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| сети | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| HTTP / HTTPS | 24 | 10 | 4 | ide_plugin; python_pytest; python_stdout; quiz_single | covered |
| TCP / UDP | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| REST | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| SOAP / GraphQL / gRPC / WebSockets обзорно | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| авторизация | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| Docker | 168 | 70 | 28 | ide_plugin; python_stdout; quiz_single | covered |
| Docker Compose | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| Poetry | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| FastAPI | 240 | 100 | 40 | http_api; ide_plugin; quiz_single; sql_query | covered |
| SQLAlchemy | 84 | 35 | 14 | ide_plugin; python_pytest; python_stdout; quiz_single; sql_query | covered |
| CRUD-проект | 12 | 5 | 2 | http_api; ide_plugin; quiz_single | covered |
| Postman | 12 | 5 | 2 | http_api; ide_plugin; quiz_single | covered |
| pytest | 175 | 126 | 14 | http_api; ide_plugin; python_pytest; python_stdout; quiz_single | covered |
| CI/CD | 192 | 80 | 32 | ide_plugin; python_stdout; quiz_single | covered |
| GitHub Actions | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| GitLab CI/CD | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| multistage build | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| AI API | 180 | 75 | 30 | ide_plugin; python_stdout; quiz_single | covered |
| RAG | 60 | 25 | 10 | ide_plugin; python_stdout; quiz_single | covered |
| vector databases | 36 | 15 | 6 | ide_plugin; python_stdout; quiz_single | covered |
| LangChain / LangGraph концептуально | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| вайбкодинг | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| финальный проект | 108 | 45 | 18 | ide_plugin; python_stdout; quiz_single | covered |
| VPS | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| безопасность сервера | 24 | 10 | 4 | ide_plugin; python_stdout; quiz_single | covered |
| домен | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| SSL | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |
| автодеплой | 12 | 5 | 2 | ide_plugin; python_stdout; quiz_single | covered |

## Как читать эти числа
Большое число шагов показывает объём отработки, но не гарантирует качество само по себе. Поэтому рядом с этим файлом лежат `validation_report.md`, `qa_report.md` и `content_quality_audit.md`: они объясняют, прошёл ли пакет структурные и содержательные проверки.
