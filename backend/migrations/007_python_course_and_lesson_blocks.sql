-- 007_python_course_and_lesson_blocks.sql
--
-- Purpose:
-- 1) Add language support for tasks (java/python).
-- 2) Add structured lesson blocks (theory/practice/quiz/summary).
-- 3) Seed first production Python course with lesson 1 content.

ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS language TEXT NOT NULL DEFAULT 'java';

UPDATE tasks
SET language = 'java'
WHERE language IS NULL OR BTRIM(language) = '';

UPDATE tasks
SET language = 'python'
WHERE LOWER(language) IN ('py', 'python3');

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'chk_tasks_language'
    ) THEN
        ALTER TABLE tasks
            ADD CONSTRAINT chk_tasks_language
            CHECK (language IN ('java', 'python'));
    END IF;
END;
$$;

CREATE TABLE IF NOT EXISTS lesson_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    block_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content_md TEXT NOT NULL DEFAULT '',
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    quiz_payload JSONB,
    position INTEGER NOT NULL,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(lesson_id, position)
);

CREATE INDEX IF NOT EXISTS idx_lesson_blocks_lesson_position
    ON lesson_blocks(lesson_id, position);

INSERT INTO courses(slug, title, description, is_published)
VALUES (
    'python-zero',
    'Python с нуля',
    'Стартовый курс по Python: вывод, переменные, ввод и первые вычисления.',
    TRUE
)
ON CONFLICT (slug) DO UPDATE
SET title = EXCLUDED.title,
    description = EXCLUDED.description,
    is_published = TRUE,
    updated_at = NOW();

WITH course_ref AS (
    SELECT id AS course_id
    FROM courses
    WHERE slug = 'python-zero'
)
INSERT INTO modules(course_id, title, position)
SELECT course_id, 'Модуль 1. Базовый синтаксис', 1
FROM course_ref
ON CONFLICT (course_id, position) DO UPDATE
SET title = EXCLUDED.title,
    updated_at = NOW();

WITH module_ref AS (
    SELECT m.id AS module_id
    FROM modules m
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1
)
INSERT INTO lessons(module_id, title, content_md, position, is_published)
SELECT
    module_id,
    'Урок 1. Первый код на Python: вывод, переменные и ввод данных',
    $$
Первый урок по Python: теория, практические задачи и контрольные вопросы.
    $$,
    1,
    TRUE
FROM module_ref
ON CONFLICT (module_id, position) DO UPDATE
SET title = EXCLUDED.title,
    content_md = EXCLUDED.content_md,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
),
task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language) AS (
    VALUES
    (
        'Первый вывод',
        $$
Напиши программу, которая выводит на экран ровно одну строку:

Привет, Python!

Входные данные: нет.
Выходные данные: одна строка `Привет, Python!`.
        $$,
        E'# Напишите ваш код ниже\n',
        E'print("Привет, Python!")\n',
        1,
        30,
        'Python Basics',
        'python'
    ),
    (
        'Две строки',
        $$
Напиши программу, которая выводит две строки:

Привет!
Это мой первый код.

Входные данные: нет.
Выходные данные: две строки в указанном порядке.
        $$,
        E'# Выведите две строки с помощью двух print()\n',
        E'print("Привет!")\nprint("Это мой первый код.")\n',
        1,
        30,
        'Python Basics',
        'python'
    ),
    (
        'Простая математика',
        $$
Выведи с новой строки:
1) сумму 12 и 8;
2) разность 30 и 5;
3) произведение 7 и 6.

Входные данные: нет.
        $$,
        E'# Выведите с новой строки: сумму, разность и произведение\n',
        E'print(12 + 8)\nprint(30 - 5)\nprint(7 * 6)\n',
        1,
        35,
        'Python Basics',
        'python'
    ),
    (
        'Анкета',
        $$
Задай значения переменных:

Имя - Анна
Возраст - 25
Город - Москва

Выведи анкету в формате:
Имя: Анна
Возраст: 25
Город: Москва
        $$,
        E'name = ""\nage = 0\ncity = ""\n\n# Выведите анкету в требуемом формате\n',
        E'name = "Анна"\nage = 25\ncity = "Москва"\n\nprint("Имя:", name)\nprint("Возраст:", age)\nprint("Город:", city)\n',
        1,
        35,
        'Variables',
        'python'
    ),
    (
        'Переменная или текст?',
        $$
В стартовом коде программа выводит слово `name` вместо значения переменной.

Даны значения переменных:
Имя - Анна

Исправьте программу. Итоговый вывод:
Привет, Анна
        $$,
        E'name = "Анна"\nprint("Привет, name")\n',
        E'name = "Анна"\nprint("Привет,", name)\n',
        2,
        40,
        'Variables',
        'python'
    ),
    (
        'Приветствие пользователя',
        $$
Пользователь вводит имя.
Выведи строку:

Привет, <имя>
        $$,
        E'name = input()\n# Выведите: Привет, <имя>\n',
        E'name = input()\nprint("Привет,", name)\n',
        1,
        40,
        'Input/Output',
        'python'
    ),
    (
        'Возраст через год',
        $$
Пользователь вводит возраст (целое число).
Выведи:

Через год вам будет <возраст + 1>
        $$,
        E'age = int(input())\n# Выведите возраст через год\n',
        E'age = int(input())\nnext_age = age + 1\nprint("Через год вам будет", next_age)\n',
        1,
        45,
        'Input/Output',
        'python'
    ),
    (
        'Сумма двух чисел',
        $$
Пользователь вводит два целых числа (каждое с новой строки).
Выведи их сумму.
        $$,
        E'a = int(input())\nb = int(input())\n# Выведите сумму\n',
        E'a = int(input())\nb = int(input())\nprint(a + b)\n',
        1,
        45,
        'Input/Output',
        'python'
    ),
    (
        'Почему получилось 105?',
        $$
Исправь код, чтобы программа складывала числа, а не склеивала строки.

Ввод: два целых числа.
Вывод: их сумма.
        $$,
        E'a = input()\nb = input()\nprint(a + b)\n',
        E'a = int(input())\nb = int(input())\nprint(a + b)\n',
        2,
        50,
        'Type conversion',
        'python'
    ),
    (
        'Периметр прямоугольника',
        $$
Пользователь вводит ширину и высоту.
Выведи периметр по формуле:

2 * (width + height)
        $$,
        E'width = int(input())\nheight = int(input())\n# perimeter = 2 * (width + height)\n',
        E'width = int(input())\nheight = int(input())\nperimeter = 2 * (width + height)\nprint(perimeter)\n',
        2,
        55,
        'Math',
        'python'
    ),
    (
        'Мини-чек',
        $$
Пользователь вводит цену и количество товаров.
Выведи строку:

Итого: <сумма>
        $$,
        E'price = int(input())\ncount = int(input())\n# Вычислите итоговую сумму и выведите ее\n',
        E'price = int(input())\ncount = int(input())\ntotal = price * count\nprint("Итого:", total)\n',
        2,
        55,
        'Math',
        'python'
    ),
    (
        'Анкета пользователя (контрольная)',
        $$
Ввод:
1) имя
2) возраст
3) город

Вывод:
Имя: <имя>
Возраст через год: <возраст + 1>
Город: <город>
        $$,
        E'name = input()\nage = int(input())\ncity = input()\n# Выведите анкету в требуемом формате\n',
        E'name = input()\nage = int(input())\ncity = input()\nnext_age = age + 1\nprint("Имя:", name)\nprint("Возраст через год:", next_age)\nprint("Город:", city)\n',
        3,
        70,
        'Control task',
        'python'
    )
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, is_published)
SELECT
    lr.lesson_id,
    ts.title,
    ts.statement_md,
    ts.starter_code,
    ts.solution_code,
    ts.difficulty,
    ts.xp_reward,
    ts.topic,
    ts.language,
    TRUE
FROM lesson_ref lr
CROSS JOIN task_seed ts
ON CONFLICT (lesson_id, title) DO UPDATE
SET statement_md = EXCLUDED.statement_md,
    starter_code = EXCLUDED.starter_code,
    solution_code = EXCLUDED.solution_code,
    difficulty = EXCLUDED.difficulty,
    xp_reward = EXCLUDED.xp_reward,
    topic = EXCLUDED.topic,
    language = EXCLUDED.language,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
),
target_tasks AS (
    SELECT t.id
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
DELETE FROM task_test_cases tc
USING target_tasks tt
WHERE tc.task_id = tt.id;

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
),
task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
),
test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ('Первый вывод', '', 'Привет, Python!', FALSE, 1),

    ('Две строки', '', E'Привет!\nЭто мой первый код.', FALSE, 1),

    ('Простая математика', '', E'20\n25\n42', FALSE, 1),

    ('Анкета', '', E'Имя: Анна\nВозраст: 25\nГород: Москва', FALSE, 1),

    ('Переменная или текст?', '', 'Привет, Анна', FALSE, 1),

    ('Приветствие пользователя', 'Маша', 'Привет, Маша', FALSE, 1),
    ('Приветствие пользователя', 'Илья', 'Привет, Илья', TRUE, 2),
    ('Приветствие пользователя', 'Python', 'Привет, Python', TRUE, 3),

    ('Возраст через год', '15', 'Через год вам будет 16', FALSE, 1),
    ('Возраст через год', '20', 'Через год вам будет 21', TRUE, 2),
    ('Возраст через год', '0', 'Через год вам будет 1', TRUE, 3),

    ('Сумма двух чисел', E'10\n25', '35', FALSE, 1),
    ('Сумма двух чисел', E'3\n7', '10', TRUE, 2),
    ('Сумма двух чисел', E'100\n200', '300', TRUE, 3),

    ('Почему получилось 105?', E'10\n5', '15', FALSE, 1),
    ('Почему получилось 105?', E'8\n12', '20', TRUE, 2),

    ('Периметр прямоугольника', E'4\n7', '22', FALSE, 1),
    ('Периметр прямоугольника', E'10\n20', '60', TRUE, 2),
    ('Периметр прямоугольника', E'1\n1', '4', TRUE, 3),

    ('Мини-чек', E'150\n3', 'Итого: 450', FALSE, 1),
    ('Мини-чек', E'99\n5', 'Итого: 495', TRUE, 2),
    ('Мини-чек', E'1000\n1', 'Итого: 1000', TRUE, 3),

    ('Анкета пользователя (контрольная)', E'Анна\n16\nМосква', E'Имя: Анна\nВозраст через год: 17\nГород: Москва', FALSE, 1),
    ('Анкета пользователя (контрольная)', E'Олег\n25\nКазань', E'Имя: Олег\nВозраст через год: 26\nГород: Казань', TRUE, 2),
    ('Анкета пользователя (контрольная)', E'Маша\n0\nСочи', E'Имя: Маша\nВозраст через год: 1\nГород: Сочи', TRUE, 3)
),
resolved AS (
    SELECT
        tl.id AS task_id,
        ts.input_data,
        ts.expected_output,
        ts.is_hidden,
        ts.position
    FROM test_seed ts
    JOIN task_lookup tl ON tl.title = ts.task_title
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT task_id, input_data, expected_output, is_hidden, position
FROM resolved
ORDER BY task_id, position;

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
),
block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (
        1,
        'theory',
        'Python и первая программа',
        $$
Python — это язык программирования. С его помощью создают сайты, ботов, игры, скрипты и сервисы анализа данных.

Программа — это набор инструкций для компьютера.

```python
print("Привет, Python!")
```

`print()` выводит текст на экран. Текст пишется в кавычках.
        $$,
        NULL,
        NULL::jsonb
    ),
    (
        2,
        'practice',
        'Практика: Первый вывод',
        'Напишите программу, которая выводит строку `Привет, Python!`.',
        'Первый вывод',
        NULL::jsonb
    ),
    (
        3,
        'theory',
        'Несколько строк вывода',
        $$
Одна команда `print()` выводит одну строку.

```python
print("Привет!")
print("Это мой первый код.")
```

Python выполняет код сверху вниз, по строкам.
        $$,
        NULL,
        NULL::jsonb
    ),
    (
        4,
        'practice',
        'Практика: Две строки',
        'Выведите две строки в нужном порядке с помощью двух `print()`.',
        'Две строки',
        NULL::jsonb
    ),
    (
        5,
        'theory',
        'Текст и числа',
        $$
Python различает текст и числа.

```python
print("123")
print(123)
```

С числами можно считать:

```python
print(10 + 5)
print(10 - 5)
print(10 * 5)
```

`print(2 + 3)` выведет `5`, а `print("2 + 3")` выведет текст `2 + 3`.
        $$,
        NULL,
        NULL::jsonb
    ),
    (
        6,
        'quiz',
        'Вопрос: Что выведет print(4 + 6)?',
        'Выберите один вариант.',
        NULL,
        jsonb_build_object(
            'question', 'Что выведет этот код? print(4 + 6)',
            'options', jsonb_build_array(
                jsonb_build_object('id', 'A', 'text', '4 + 6'),
                jsonb_build_object('id', 'B', 'text', '10'),
                jsonb_build_object('id', 'C', 'text', '"10"'),
                jsonb_build_object('id', 'D', 'text', 'Ошибку')
            ),
            'correctOptionId', 'B',
            'explanation', 'Числа записаны без кавычек, Python выполняет сложение и выводит 10.'
        )
    ),
    (
        7,
        'quiz',
        'Вопрос: Текст или вычисление?',
        'Выберите один вариант.',
        NULL,
        jsonb_build_object(
            'question', 'Что выведет этот код? print("4 + 6")',
            'options', jsonb_build_array(
                jsonb_build_object('id', 'A', 'text', '10'),
                jsonb_build_object('id', 'B', 'text', '4 + 6'),
                jsonb_build_object('id', 'C', 'text', 'Ошибку'),
                jsonb_build_object('id', 'D', 'text', 'Ничего')
            ),
            'correctOptionId', 'B',
            'explanation', 'Строка в кавычках не вычисляется, она выводится как текст.'
        )
    ),
    (
        8,
        'practice',
        'Практика: Простая математика',
        'Вычислите и выведите 3 результата, каждый с новой строки.',
        'Простая математика',
        NULL::jsonb
    ),
    (
        9,
        'theory',
        'Переменные',
        $$
Переменная — это имя, за которым хранится значение.

```python
name = "Анна"
age = 16

print(name)
print(age)
```

Можно выводить текст и переменную вместе:

```python
print("Имя:", name)
```

Сначала переменную нужно создать, потом использовать.
        $$,
        NULL,
        NULL::jsonb
    ),
    (
        10,
        'theory',
        'Имена переменных',
        $$
Используйте понятные имена: `user_name`, `user_age`, `total`.

Правила:
- допустимы английские буквы, цифры и `_`;
- имя не должно начинаться с цифры;
- `user-city` недопустимо из-за `-`.
        $$,
        NULL,
        NULL::jsonb
    ),
    (
        11,
        'practice',
        'Практика: Анкета',
        'Создайте переменные `name`, `age`, `city` и выведите анкету.',
        'Анкета',
        NULL::jsonb
    ),
    (
        12,
        'practice',
        'Исправление кода: Переменная или текст?',
        'Исправьте программу. Итоговый вывод должен быть: `Привет, Анна`.',
        'Переменная или текст?',
        NULL::jsonb
    ),
    (
        13,
        'theory',
        'Ввод данных: input()',
        $$
`input()` считывает данные пользователя и возвращает строку.

```python
name = input()
print("Привет,", name)
```

В задачах автопроверки не добавляйте подсказку в `input()`, например `input("Введите имя")`.
        $$,
        NULL,
        NULL::jsonb
    ),
    (
        14,
        'practice',
        'Практика: Приветствие пользователя',
        'Считайте имя и выведите `Привет, <имя>`.',
        'Приветствие пользователя',
        NULL::jsonb
    ),
    (
        15,
        'theory',
        'input() всегда возвращает текст',
        $$
Даже если пользователь вводит число, `input()` вернет строку.

Чтобы получить число, используйте `int(input())`.

```python
age = int(input())
print(age + 1)
```
        $$,
        NULL,
        NULL::jsonb
    ),
    (
        16,
        'quiz',
        'Вопрос: Что не так с кодом?',
        'Выберите один вариант.',
        NULL,
        jsonb_build_object(
            'question', 'Что не так в коде? age = input(); print(age + 1)',
            'options', jsonb_build_array(
                jsonb_build_object('id', 'A', 'text', 'input() нельзя сохранять в переменную'),
                jsonb_build_object('id', 'B', 'text', 'print() нельзя использовать с переменными'),
                jsonb_build_object('id', 'C', 'text', 'input() возвращает текст, его нельзя сложить с числом'),
                jsonb_build_object('id', 'D', 'text', 'Нужно писать print(input())')
            ),
            'correctOptionId', 'C',
            'explanation', 'Преобразуйте ввод в число: age = int(input()).'
        )
    ),
    (
        17,
        'practice',
        'Практика: Возраст через год',
        'Считайте возраст и выведите возраст через год.',
        'Возраст через год',
        NULL::jsonb
    ),
    (
        18,
        'practice',
        'Практика: Сумма двух чисел',
        'Считайте два числа и выведите их сумму.',
        'Сумма двух чисел',
        NULL::jsonb
    ),
    (
        19,
        'practice',
        'Исправление: Почему получилось 105?',
        'Исправьте программу, чтобы она считала сумму чисел.',
        'Почему получилось 105?',
        NULL::jsonb
    ),
    (
        20,
        'practice',
        'Практика: Периметр прямоугольника',
        'Считайте ширину и высоту, затем выведите периметр.',
        'Периметр прямоугольника',
        NULL::jsonb
    ),
    (
        21,
        'practice',
        'Практика: Мини-чек',
        'Считайте цену и количество, выведите строку `Итого: <сумма>`.',
        'Мини-чек',
        NULL::jsonb
    ),
    (
        22,
        'theory',
        'Правило автопроверки',
        $$
Автопроверка сравнивает вывод точно с ожидаемым.

Если ожидается `15`, нельзя выводить `Ответ: 15`.

Также в большинстве задач не нужно писать подсказки внутри `input()`.
        $$,
        NULL,
        NULL::jsonb
    ),
    (
        23,
        'practice',
        'Контрольная задача: Анкета пользователя',
        'Итоговая задача урока на ввод, переменные и вычисления.',
        'Анкета пользователя (контрольная)',
        NULL::jsonb
    ),
    (
        24,
        'summary',
        'Итоговые вопросы урока',
        $$
Проверьте себя:

1. Что делает `print()`?
2. Что выведет `print(2 + 3)`?
3. Что выведет `print("2 + 3")`?
4. Что делает `name = input()`?
5. Как получить число из ввода?
6. Почему `a = input(); b = input(); print(a + b)` может дать `105`?

Правильные ответы:
1) выводит данные на экран;
2) `5`;
3) `2 + 3`;
4) сохраняет ввод в переменную;
5) `int(input())`;
6) потому что `input()` возвращает текст.
        $$,
        NULL,
        NULL::jsonb
    ),
    (
        25,
        'summary',
        'Итог урока и домашняя работа',
        $$
В уроке вы научились:
- выводить текст через `print()`;
- хранить данные в переменных;
- считывать ввод через `input()`;
- преобразовывать строки в числа через `int()`.

Домашняя работа (рекомендуется):
1. `Рад знакомству, <имя>`;
2. возраст через 5 лет;
3. сумма трех чисел;
4. площадь прямоугольника;
5. итоговая стоимость покупки с доставкой.
        $$,
        NULL,
        NULL::jsonb
    )
),
task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
),
resolved AS (
    SELECT
        bs.position,
        bs.block_type,
        bs.title,
        bs.content_md,
        tl.task_id,
        bs.quiz_payload
    FROM block_seed bs
    LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT
    lr.lesson_id,
    r.block_type,
    r.title,
    r.content_md,
    r.task_id,
    r.quiz_payload,
    r.position,
    TRUE
FROM lesson_ref lr
CROSS JOIN resolved r
ON CONFLICT (lesson_id, position) DO UPDATE
SET block_type = EXCLUDED.block_type,
    title = EXCLUDED.title,
    content_md = EXCLUDED.content_md,
    task_id = EXCLUDED.task_id,
    quiz_payload = EXCLUDED.quiz_payload,
    is_published = TRUE,
    updated_at = NOW();
