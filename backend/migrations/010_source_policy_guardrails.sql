-- 010_source_policy_guardrails.sql
--
-- Purpose:
-- 1) Add reusable task-level source policy rules for anti-cheat and pedagogy constraints.
-- 2) Block trivial constant-answer submissions for selected learning tasks.
-- 3) Keep the lesson theory clean for production users.

ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS source_policy JSONB NOT NULL DEFAULT '{}'::jsonb;

UPDATE tasks
SET source_policy = '{}'::jsonb
WHERE source_policy IS NULL;

WITH target_task AS (
    SELECT t.id
    FROM tasks t
    JOIN lessons l ON l.id = t.lesson_id
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero'
      AND m.position = 1
      AND l.position = 1
      AND t.title = 'Простая математика'
)
UPDATE tasks t
SET source_policy = jsonb_build_object(
        'language', 'python',
        'emptySourceMessage', 'Код пока пуст. Напишите решение и запустите проверку снова.',
        'ignoreCommentOnlyLines', true,
        'requireAll', jsonb_build_array(
            jsonb_build_object('pattern', '(?s)(12\s*\+\s*8|8\s*\+\s*12)', 'message', 'В коде нет вычисления суммы 12 + 8. Добавьте вычисление и выведите результат.'),
            jsonb_build_object('pattern', '(?s)30\s*-\s*5', 'message', 'В коде нет вычисления разности 30 - 5. Добавьте это вычисление отдельной строкой вывода.'),
            jsonb_build_object('pattern', '(?s)(7\s*\*\s*6|6\s*\*\s*7)', 'message', 'В коде нет вычисления произведения 7 * 6. Добавьте это вычисление и выведите результат.')
        ),
        'forbidAny', jsonb_build_array(
            jsonb_build_object('pattern', '(?m)^\s*print\s*\(\s*20\s*\)\s*$', 'message', 'Нельзя выводить готовое число 20. Нужно вывести результат выражения 12 + 8.'),
            jsonb_build_object('pattern', '(?m)^\s*print\s*\(\s*25\s*\)\s*$', 'message', 'Нельзя выводить готовое число 25. Нужно вывести результат выражения 30 - 5.'),
            jsonb_build_object('pattern', '(?m)^\s*print\s*\(\s*42\s*\)\s*$', 'message', 'Нельзя выводить готовое число 42. Нужно вывести результат выражения 7 * 6.')
        )
    ),
    updated_at = NOW()
FROM target_task tt
WHERE t.id = tt.id;

WITH target_block AS (
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
FROM target_block tb
WHERE lb.id = tb.id;
