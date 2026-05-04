# Release checklist v18

- [ ] `python validate_course.py` PASS.
- [ ] Первый урок `Первый код`.
- [ ] Первые 30 уроков проходят prerequisite-gate.
- [ ] Manifest совпадает с JSON.
- [ ] Coverage без missing/thin/placeholder.
- [ ] Нет битого текста.
- [ ] Нет body leaks.
- [ ] Все practice/project/test имеют проверки.
- [ ] SQL/FastAPI/AI/OOP gates равны 0.
- [ ] Ручная выборка на staging: первые 10 уроков и 50-100 шагов по ключевым трекам.

## Обновление 2026-05-05: обязательные проверки перед staging
- `python validate_course.py` должен вернуть PASS.
- `pedagogical_audit_report.md` должен показывать проверку всех уроков и отдельный статус первых 30 уроков.
- `duplication_report.md` должен показывать максимальный размер оставшейся структурной группы.
- На staging пройти FastAPI lesson 1 как студент: `GET /health`, `GET /hello`, `GET /version`, `GET /ready`, `GET /about`, `GET /ping`.
- Не запускать массовый поток без ручной выборки 50-100 шагов после импорта.
