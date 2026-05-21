# Release Checklist: Java Metanit v1

## Перед импортом
- [ ] `python validate_course.py` возвращает PASS.
- [ ] `validation_report.md` показывает `critical errors: 0`.
- [ ] Для каждого урока есть шаги `theory`, `test`, `practice`.
- [ ] Для каждого practice есть checker, public/hidden tests, hints и ai_hint_config.
- [ ] Теория не содержит внешних promo/channel упоминаний.

## После миграции
- [ ] Курс `java-zero-core` опубликован и открывается в UI.
- [ ] Первый урок отображает theory, quiz, practice.
- [ ] Quiz шаг сохраняет результат и влияет на прогресс.
- [ ] Practice шаг принимает Java-решение и выдает вердикт.
- [ ] AI hint по Java-задаче возвращает подсказку без раскрытия hidden tests.
