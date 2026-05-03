# Import instructions v18

Импортируй только `course_import.json`. Markdown-файлы нужны для методиста и QA, но не являются источником импорта.

Перед импортом запусти:

```powershell
python validate_course.py
```

Если статус не PASS, пакет не импортировать.
