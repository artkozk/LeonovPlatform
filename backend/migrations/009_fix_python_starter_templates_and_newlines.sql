-- 009_fix_python_starter_templates_and_newlines.sql
--
-- Purpose:
-- 1) Fix already deployed python-zero task code where starter/solution may contain literal \n, \t, \" sequences.
-- 2) Replace starter_code with training templates (not full solutions) for practice tasks.
-- 3) Keep solution_code intact for judge correctness while normalizing escaped sequences.

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
)
UPDATE lessons l
SET content_md = 'Первый урок по Python: теория, практические задачи и контрольные вопросы.',
    updated_at = NOW()
FROM lesson_ref lr
WHERE l.id = lr.lesson_id;

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
),
target_tasks AS (
    SELECT t.id, t.title, t.starter_code, t.solution_code
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        'Первый вывод',
        'Две строки',
        'Простая математика',
        'Анкета',
        'Переменная или текст?',
        'Приветствие пользователя',
        'Возраст через год',
        'Сумма двух чисел',
        'Почему получилось 105?',
        'Периметр прямоугольника',
        'Мини-чек',
        'Анкета пользователя (контрольная)'
    )
)
UPDATE tasks t
SET starter_code = CASE tt.title
        WHEN 'Первый вывод' THEN E'# Напишите ваш код ниже\n'
        WHEN 'Две строки' THEN E'# Выведите две строки с помощью двух print()\n'
        WHEN 'Простая математика' THEN E'# Выведите с новой строки: сумму, разность и произведение\n'
        WHEN 'Анкета' THEN E'name = ""\nage = 0\ncity = ""\n\n# Выведите анкету в требуемом формате\n'
        WHEN 'Переменная или текст?' THEN E'name = "Анна"\nprint("Привет, name")\n'
        WHEN 'Приветствие пользователя' THEN E'name = input()\n# Выведите: Привет, <имя>\n'
        WHEN 'Возраст через год' THEN E'age = int(input())\n# Выведите возраст через год\n'
        WHEN 'Сумма двух чисел' THEN E'a = int(input())\nb = int(input())\n# Выведите сумму\n'
        WHEN 'Почему получилось 105?' THEN E'a = input()\nb = input()\nprint(a + b)\n'
        WHEN 'Периметр прямоугольника' THEN E'width = int(input())\nheight = int(input())\n# perimeter = 2 * (width + height)\n'
        WHEN 'Мини-чек' THEN E'price = int(input())\ncount = int(input())\n# Вычислите итоговую сумму и выведите ее\n'
        WHEN 'Анкета пользователя (контрольная)' THEN E'name = input()\nage = int(input())\ncity = input()\n# Выведите анкету в требуемом формате\n'
        ELSE REPLACE(REPLACE(REPLACE(REPLACE(tt.starter_code, '\n', E'\n'), '\t', E'\t'), '\"', '"'), E'\r\n', E'\n')
    END,
    solution_code = REPLACE(REPLACE(REPLACE(REPLACE(tt.solution_code, '\n', E'\n'), '\t', E'\t'), '\"', '"'), E'\r\n', E'\n'),
    updated_at = NOW()
FROM target_tasks tt
WHERE t.id = tt.id;
