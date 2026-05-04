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

## SEMANTIC_ALIGNMENT_2026_05_05

- Запустить `python validate_course.py`.
- Проверить `pedagogical_audit_report.md`: rewritten lessons > 0, weak lessons after fixes = 0 by gates.
- Проверить `duplication_report.md`: exact duplicate practice/project bodies = 0, exact duplicate solutions = 0.
- После импорта на staging пройти вручную 10 первых уроков, известные исправленные уроки module 2/4/5 и минимум 20 случайных шагов.
