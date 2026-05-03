-- 008_cleanup_python_lesson_content.sql
--
-- Purpose:
-- 1) Remove draft teaching fragment with intentionally invalid code from lesson 1 theory.
-- 2) Keep production-friendly wording for the first Python block.

WITH target AS (
    SELECT lb.id
    FROM lesson_blocks lb
    JOIN lessons l ON l.id = lb.lesson_id
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero'
      AND m.position = 1
      AND l.position = 1
      AND lb.position = 1
)
UPDATE lesson_blocks lb
SET content_md = $$
Python — это язык программирования. С его помощью создают сайты, ботов, игры, скрипты и сервисы анализа данных.

Программа — это набор инструкций для компьютера.

```python
print("Привет, Python!")
```

`print()` выводит текст на экран. Текст пишется в кавычках.
$$,
    updated_at = NOW()
FROM target t
WHERE lb.id = t.id;
