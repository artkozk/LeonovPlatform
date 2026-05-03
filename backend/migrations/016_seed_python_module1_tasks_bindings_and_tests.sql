-- 016_seed_python_module1_tasks_bindings_and_tests.sql
-- Generated from osnovy_python_platform_ready_v3 (1).md
-- Purpose:
-- 1) Seed full task catalog for python-zero module 1 lessons 2-13.
-- 2) Attach every practice block to a real task_id.
-- 3) Seed task test-cases from admin examples for platform auto-check.
-- 4) Keep lesson blocks synchronized with current markdown import source.

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
), lesson_seed(position, title, content_md) AS (
    VALUES
    (2, $l2_title$Урок 2. Числа$l2_title$, $l2_content$Арифметика, деление, остаток, дробные числа и формулы.$l2_content$),
    (3, $l3_title$Урок 3. Условия$l3_title$, $l3_content$Сравнения и ветвления: if, else, elif.$l3_content$),
    (4, $l4_title$Урок 4. Логика$l4_title$, $l4_content$Сложные проверки через and, or, not.$l4_content$),
    (5, $l5_title$Урок 5. while$l5_title$, $l5_content$Цикл, который работает, пока условие истинно.$l5_content$),
    (6, $l6_title$Урок 6. for и range$l6_title$, $l6_content$Повторение известное количество раз.$l6_content$),
    (7, $l7_title$Урок 7. Строки$l7_title$, $l7_content$Длина, индексы, срезы, методы и простая обработка текста.$l7_content$),
    (8, $l8_title$Урок 8. Списки$l8_title$, $l8_content$Хранение нескольких значений, append, split и перебор.$l8_content$),
    (9, $l9_title$Урок 9. Словари$l9_title$, $l9_content$Ключи, значения, поиск и перебор словаря.$l9_content$),
    (10, $l10_title$Урок 10. Множества$l10_title$, $l10_content$Уникальные значения и частотные словари.$l10_content$),
    (11, $l11_title$Урок 11. Функции$l11_title$, $l11_content$def, параметры, return и разбиение кода.$l11_content$),
    (12, $l12_title$Урок 12. Проект$l12_title$, $l12_content$Консольный трекер задач с командами.$l12_content$),
    (13, $l13_title$Урок 13. Контроль$l13_title$, $l13_content$Проверка всех тем модуля.$l13_content$)
)
INSERT INTO lessons(module_id, title, content_md, position, is_published)
SELECT
    mr.module_id,
    ls.title,
    ls.content_md,
    ls.position,
    TRUE
FROM module_ref mr
CROSS JOIN lesson_seed ls
ON CONFLICT (module_id, position) DO UPDATE
SET title = EXCLUDED.title,
    content_md = EXCLUDED.content_md,
    is_published = TRUE,
    updated_at = NOW();

-- Lesson 2: Урок 2. Числа
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 2
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l2_t2_title$Скобки$l2_t2_title$, $l2_t2_statement$**Коротко:** Вычислите выражение со скобками.

### Условие

На вход подаются три числа `a`, `b`, `c`. Выведи значение `(a + b) * c`.

### Вход

Три целых числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
2
3
4
```

Вывод:

```text
20
```

### Пример 2

Ввод:

```text
10
5
2
```

Вывод:

```text
30
```

### Шаблон

```python
a = int(input())
b = int(input())
c = int(input())
```

### Подсказки

1. Сначала сложи `a` и `b`.

2. Запиши формулу: `(a + b) * c`.$l2_t2_statement$, $l2_t2_starter$a = int(input())
b = int(input())
c = int(input())
$l2_t2_starter$, $l2_t2_solution$a = int(input())
b = int(input())
c = int(input())
print((a + b) * c)
$l2_t2_solution$, 1, 40, $l2_t2_topic$Python M1 — Числа$l2_t2_topic$, 'python', $l2_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l2_t2_policy$::jsonb),
    ($l2_t4_title$Целое деление$l2_t4_title$, $l2_t4_statement$**Коротко:** Найдите число полных коробок.

### Условие

Есть `items` предметов. В одну коробку помещается `box_size` предметов. Выведи, сколько полных коробок получится.

### Вход

Два целых числа: предметы и размер коробки.

### Выход

Одно число — количество полных коробок.

### Пример 1

Ввод:

```text
17
5
```

Вывод:

```text
3
```

### Пример 2

Ввод:

```text
20
4
```

Вывод:

```text
5
```

### Шаблон

```python
items = int(input())
box_size = int(input())
```

### Подсказки

1. Нужна только целая часть деления.

2. Используй `//`.$l2_t4_statement$, $l2_t4_starter$items = int(input())
box_size = int(input())
$l2_t4_starter$, $l2_t4_solution$items = int(input())
box_size = int(input())
print(items // box_size)
$l2_t4_solution$, 1, 40, $l2_t4_topic$Python M1 — Числа$l2_t4_topic$, 'python', $l2_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l2_t4_policy$::jsonb),
    ($l2_t5_title$Остаток$l2_t5_title$, $l2_t5_statement$**Коротко:** Найдите остаток предметов.

### Условие

Есть `items` предметов. В одну коробку помещается `box_size` предметов. Выведи, сколько предметов останется после заполнения полных коробок.

### Вход

Два целых числа.

### Выход

Одно число — остаток.

### Пример 1

Ввод:

```text
17
5
```

Вывод:

```text
2
```

### Пример 2

Ввод:

```text
20
4
```

Вывод:

```text
0
```

### Шаблон

```python
items = int(input())
box_size = int(input())
```

### Подсказки

1. Остаток от деления даёт `%`.

2. Формула: `items % box_size`.$l2_t5_statement$, $l2_t5_starter$items = int(input())
box_size = int(input())
$l2_t5_starter$, $l2_t5_solution$items = int(input())
box_size = int(input())
print(items % box_size)
$l2_t5_solution$, 1, 40, $l2_t5_topic$Python M1 — Числа$l2_t5_topic$, 'python', $l2_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l2_t5_policy$::jsonb),
    ($l2_t6_title$Минуты$l2_t6_title$, $l2_t6_statement$**Коротко:** Переведите минуты в часы и минуты.

### Условие

На вход подаётся количество минут. Выведи две строки: полные часы и оставшиеся минуты.

### Вход

Одно целое число — минуты.

### Выход

Две строки: `Часы: <h>` и `Минуты: <m>`.

### Пример 1

Ввод:

```text
125
```

Вывод:

```text
Часы: 2
Минуты: 5
```

### Пример 2

Ввод:

```text
60
```

Вывод:

```text
Часы: 1
Минуты: 0
```

### Шаблон

```python
minutes = int(input())
```

### Подсказки

1. Часы: `minutes // 60`.

2. Остаток минут: `minutes % 60`.$l2_t6_statement$, $l2_t6_starter$minutes = int(input())
$l2_t6_starter$, $l2_t6_solution$minutes = int(input())
hours = minutes // 60
rest = minutes % 60
print("Часы:", hours)
print("Минуты:", rest)
$l2_t6_solution$, 2, 55, $l2_t6_topic$Python M1 — Числа$l2_t6_topic$, 'python', $l2_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l2_t6_policy$::jsonb),
    ($l2_t8_title$Скидка$l2_t8_title$, $l2_t8_statement$**Коротко:** Посчитайте цену со скидкой.

### Условие

На вход подаются цена и скидка в процентах. Выведи цену после скидки.

### Вход

Два числа: цена и скидка.

### Выход

Одно число. Допускается дробный вывод Python.

### Пример 1

Ввод:

```text
1000
10
```

Вывод:

```text
900.0
```

### Пример 2

Ввод:

```text
500
25
```

Вывод:

```text
375.0
```

### Шаблон

```python
price = float(input())
discount = float(input())
```

### Подсказки

1. Скидка в деньгах: `price * discount / 100`.

2. Новая цена: `price - ...`.$l2_t8_statement$, $l2_t8_starter$price = float(input())
discount = float(input())
$l2_t8_starter$, $l2_t8_solution$price = float(input())
discount = float(input())
result = price - price * discount / 100
print(result)
$l2_t8_solution$, 2, 55, $l2_t8_topic$Python M1 — Числа$l2_t8_topic$, 'python', $l2_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l2_t8_policy$::jsonb),
    ($l2_t10_title$Среднее$l2_t10_title$, $l2_t10_statement$**Коротко:** Найдите среднее трёх чисел.

### Условие

На вход подаются три числа. Выведи их среднее, округлённое до 2 знаков.

### Вход

Три числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
1
2
3
```

Вывод:

```text
2.0
```

### Пример 2

Ввод:

```text
10
20
21
```

Вывод:

```text
17.0
```

### Шаблон

```python
a = float(input())
b = float(input())
c = float(input())
```

### Подсказки

1. Среднее: `(a + b + c) / 3`.

2. Используй `round(value, 2)`.$l2_t10_statement$, $l2_t10_starter$a = float(input())
b = float(input())
c = float(input())
$l2_t10_starter$, $l2_t10_solution$a = float(input())
b = float(input())
c = float(input())
avg = (a + b + c) / 3
print(round(avg, 2))
$l2_t10_solution$, 2, 55, $l2_t10_topic$Python M1 — Числа$l2_t10_topic$, 'python', $l2_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l2_t10_policy$::jsonb),
    ($l2_t11_title$Формула$l2_t11_title$, $l2_t11_statement$**Коротко:** Соберите формулу покупки.

### Условие

На вход подаются цена, количество, скидка и доставка. Итог: `price * count - скидка + доставка`. Скидка задаётся в процентах от `price * count`. Выведи итог, округлив до 2 знаков.

### Вход

Четыре числа: цена, количество, скидка, доставка.

### Выход

Одно число.

### Пример 1

Ввод:

```text
200
3
10
50
```

Вывод:

```text
590.0
```

### Пример 2

Ввод:

```text
100
2
0
30
```

Вывод:

```text
230.0
```

### Шаблон

```python
price = float(input())
count = int(input())
discount = float(input())
delivery = float(input())
```

### Подсказки

1. Сначала найди сумму без скидки.

2. Скидка: `subtotal * discount / 100`.$l2_t11_statement$, $l2_t11_starter$price = float(input())
count = int(input())
discount = float(input())
delivery = float(input())
$l2_t11_starter$, $l2_t11_solution$price = float(input())
count = int(input())
discount = float(input())
delivery = float(input())
subtotal = price * count
total = subtotal - subtotal * discount / 100 + delivery
print(round(total, 2))
$l2_t11_solution$, 2, 65, $l2_t11_topic$Python M1 — Числа$l2_t11_topic$, 'python', $l2_t11_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l2_t11_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 2
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l2_t2_delete_title$Скобки$l2_t2_delete_title$,
        $l2_t4_delete_title$Целое деление$l2_t4_delete_title$,
        $l2_t5_delete_title$Остаток$l2_t5_delete_title$,
        $l2_t6_delete_title$Минуты$l2_t6_delete_title$,
        $l2_t8_delete_title$Скидка$l2_t8_delete_title$,
        $l2_t10_delete_title$Среднее$l2_t10_delete_title$,
        $l2_t11_delete_title$Формула$l2_t11_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 2
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l2_test_2_1_title$Скобки$l2_test_2_1_title$, $l2_test_2_1_input$2
3
4$l2_test_2_1_input$, $l2_test_2_1_expected$20$l2_test_2_1_expected$, FALSE, 1),
    ($l2_test_2_2_title$Скобки$l2_test_2_2_title$, $l2_test_2_2_input$10
5
2$l2_test_2_2_input$, $l2_test_2_2_expected$30$l2_test_2_2_expected$, TRUE, 2),
    ($l2_test_2_3_title$Скобки$l2_test_2_3_title$, $l2_test_2_3_input$0
7
3$l2_test_2_3_input$, $l2_test_2_3_expected$21$l2_test_2_3_expected$, TRUE, 3),
    ($l2_test_4_1_title$Целое деление$l2_test_4_1_title$, $l2_test_4_1_input$17
5$l2_test_4_1_input$, $l2_test_4_1_expected$3$l2_test_4_1_expected$, FALSE, 1),
    ($l2_test_4_2_title$Целое деление$l2_test_4_2_title$, $l2_test_4_2_input$20
4$l2_test_4_2_input$, $l2_test_4_2_expected$5$l2_test_4_2_expected$, TRUE, 2),
    ($l2_test_4_3_title$Целое деление$l2_test_4_3_title$, $l2_test_4_3_input$3
10$l2_test_4_3_input$, $l2_test_4_3_expected$0$l2_test_4_3_expected$, TRUE, 3),
    ($l2_test_5_1_title$Остаток$l2_test_5_1_title$, $l2_test_5_1_input$17
5$l2_test_5_1_input$, $l2_test_5_1_expected$2$l2_test_5_1_expected$, FALSE, 1),
    ($l2_test_5_2_title$Остаток$l2_test_5_2_title$, $l2_test_5_2_input$20
4$l2_test_5_2_input$, $l2_test_5_2_expected$0$l2_test_5_2_expected$, TRUE, 2),
    ($l2_test_5_3_title$Остаток$l2_test_5_3_title$, $l2_test_5_3_input$3
10$l2_test_5_3_input$, $l2_test_5_3_expected$3$l2_test_5_3_expected$, TRUE, 3),
    ($l2_test_6_1_title$Минуты$l2_test_6_1_title$, $l2_test_6_1_input$125$l2_test_6_1_input$, $l2_test_6_1_expected$Часы: 2
Минуты: 5$l2_test_6_1_expected$, FALSE, 1),
    ($l2_test_6_2_title$Минуты$l2_test_6_2_title$, $l2_test_6_2_input$60$l2_test_6_2_input$, $l2_test_6_2_expected$Часы: 1
Минуты: 0$l2_test_6_2_expected$, TRUE, 2),
    ($l2_test_6_3_title$Минуты$l2_test_6_3_title$, $l2_test_6_3_input$59$l2_test_6_3_input$, $l2_test_6_3_expected$Часы: 0
Минуты: 59$l2_test_6_3_expected$, TRUE, 3),
    ($l2_test_8_1_title$Скидка$l2_test_8_1_title$, $l2_test_8_1_input$1000
10$l2_test_8_1_input$, $l2_test_8_1_expected$900.0$l2_test_8_1_expected$, FALSE, 1),
    ($l2_test_8_2_title$Скидка$l2_test_8_2_title$, $l2_test_8_2_input$500
25$l2_test_8_2_input$, $l2_test_8_2_expected$375.0$l2_test_8_2_expected$, TRUE, 2),
    ($l2_test_8_3_title$Скидка$l2_test_8_3_title$, $l2_test_8_3_input$1200
0$l2_test_8_3_input$, $l2_test_8_3_expected$1200.0$l2_test_8_3_expected$, TRUE, 3),
    ($l2_test_10_1_title$Среднее$l2_test_10_1_title$, $l2_test_10_1_input$1
2
3$l2_test_10_1_input$, $l2_test_10_1_expected$2.0$l2_test_10_1_expected$, FALSE, 1),
    ($l2_test_10_2_title$Среднее$l2_test_10_2_title$, $l2_test_10_2_input$10
20
21$l2_test_10_2_input$, $l2_test_10_2_expected$17.0$l2_test_10_2_expected$, TRUE, 2),
    ($l2_test_10_3_title$Среднее$l2_test_10_3_title$, $l2_test_10_3_input$1
1
2$l2_test_10_3_input$, $l2_test_10_3_expected$1.33$l2_test_10_3_expected$, TRUE, 3),
    ($l2_test_11_1_title$Формула$l2_test_11_1_title$, $l2_test_11_1_input$200
3
10
50$l2_test_11_1_input$, $l2_test_11_1_expected$590.0$l2_test_11_1_expected$, FALSE, 1),
    ($l2_test_11_2_title$Формула$l2_test_11_2_title$, $l2_test_11_2_input$100
2
0
30$l2_test_11_2_input$, $l2_test_11_2_expected$230.0$l2_test_11_2_expected$, TRUE, 2),
    ($l2_test_11_3_title$Формула$l2_test_11_3_title$, $l2_test_11_3_input$99.9
3
5
0$l2_test_11_3_input$, $l2_test_11_3_expected$284.72$l2_test_11_3_expected$, TRUE, 3)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 2
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l2_b1_title$Операции$l2_b1_title$, $l2_b1_content$В Python можно считать с помощью операторов:

| Оператор | Значение |
|---|---|
| `+` | сложение |
| `-` | вычитание |
| `*` | умножение |
| `/` | деление |

Скобки работают как в математике:
```python
result = 2 * (3 + 4)
print(result)  # 14
```$l2_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l2_b2_title$Скобки$l2_b2_title$, $l2_b2_content$**Коротко:** Вычислите выражение со скобками.

### Условие

На вход подаются три числа `a`, `b`, `c`. Выведи значение `(a + b) * c`.

### Вход

Три целых числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
2
3
4
```

Вывод:

```text
20
```

### Пример 2

Ввод:

```text
10
5
2
```

Вывод:

```text
30
```

### Шаблон

```python
a = int(input())
b = int(input())
c = int(input())
```

### Подсказки

1. Сначала сложи `a` и `b`.

2. Запиши формулу: `(a + b) * c`.$l2_b2_content$, $l2_b2_task$Скобки$l2_b2_task$, NULL::jsonb),
    (3, 'theory', $l2_b3_title$Деление$l2_b3_title$, $l2_b3_content$Обычное деление `/` возвращает дробное число:
```python
print(10 / 2)  # 5.0
```

Целое деление `//` оставляет только целую часть:
```python
print(17 // 5)  # 3
```

Остаток `%` показывает остаток от деления:
```python
print(17 % 5)  # 2
```$l2_b3_content$, NULL, NULL::jsonb),
    (4, 'practice', $l2_b4_title$Целое деление$l2_b4_title$, $l2_b4_content$**Коротко:** Найдите число полных коробок.

### Условие

Есть `items` предметов. В одну коробку помещается `box_size` предметов. Выведи, сколько полных коробок получится.

### Вход

Два целых числа: предметы и размер коробки.

### Выход

Одно число — количество полных коробок.

### Пример 1

Ввод:

```text
17
5
```

Вывод:

```text
3
```

### Пример 2

Ввод:

```text
20
4
```

Вывод:

```text
5
```

### Шаблон

```python
items = int(input())
box_size = int(input())
```

### Подсказки

1. Нужна только целая часть деления.

2. Используй `//`.$l2_b4_content$, $l2_b4_task$Целое деление$l2_b4_task$, NULL::jsonb),
    (5, 'practice', $l2_b5_title$Остаток$l2_b5_title$, $l2_b5_content$**Коротко:** Найдите остаток предметов.

### Условие

Есть `items` предметов. В одну коробку помещается `box_size` предметов. Выведи, сколько предметов останется после заполнения полных коробок.

### Вход

Два целых числа.

### Выход

Одно число — остаток.

### Пример 1

Ввод:

```text
17
5
```

Вывод:

```text
2
```

### Пример 2

Ввод:

```text
20
4
```

Вывод:

```text
0
```

### Шаблон

```python
items = int(input())
box_size = int(input())
```

### Подсказки

1. Остаток от деления даёт `%`.

2. Формула: `items % box_size`.$l2_b5_content$, $l2_b5_task$Остаток$l2_b5_task$, NULL::jsonb),
    (6, 'practice', $l2_b6_title$Минуты$l2_b6_title$, $l2_b6_content$**Коротко:** Переведите минуты в часы и минуты.

### Условие

На вход подаётся количество минут. Выведи две строки: полные часы и оставшиеся минуты.

### Вход

Одно целое число — минуты.

### Выход

Две строки: `Часы: <h>` и `Минуты: <m>`.

### Пример 1

Ввод:

```text
125
```

Вывод:

```text
Часы: 2
Минуты: 5
```

### Пример 2

Ввод:

```text
60
```

Вывод:

```text
Часы: 1
Минуты: 0
```

### Шаблон

```python
minutes = int(input())
```

### Подсказки

1. Часы: `minutes // 60`.

2. Остаток минут: `minutes % 60`.$l2_b6_content$, $l2_b6_task$Минуты$l2_b6_task$, NULL::jsonb),
    (7, 'theory', $l2_b7_title$float$l2_b7_title$, $l2_b7_content$`float` — дробное число.

```python
price = float(input())
```

Используй `float`, если во вводе может быть число с точкой:
```text
12.5
```$l2_b7_content$, NULL, NULL::jsonb),
    (8, 'practice', $l2_b8_title$Скидка$l2_b8_title$, $l2_b8_content$**Коротко:** Посчитайте цену со скидкой.

### Условие

На вход подаются цена и скидка в процентах. Выведи цену после скидки.

### Вход

Два числа: цена и скидка.

### Выход

Одно число. Допускается дробный вывод Python.

### Пример 1

Ввод:

```text
1000
10
```

Вывод:

```text
900.0
```

### Пример 2

Ввод:

```text
500
25
```

Вывод:

```text
375.0
```

### Шаблон

```python
price = float(input())
discount = float(input())
```

### Подсказки

1. Скидка в деньгах: `price * discount / 100`.

2. Новая цена: `price - ...`.$l2_b8_content$, $l2_b8_task$Скидка$l2_b8_task$, NULL::jsonb),
    (9, 'theory', $l2_b9_title$Округление$l2_b9_title$, $l2_b9_content$`round(number, 2)` округляет число до двух знаков после точки.

```python
value = 12.3456
print(round(value, 2))  # 12.35
```

На этом уроке не требуем денежный формат `690.00`. Достаточно обычного вывода Python.$l2_b9_content$, NULL, NULL::jsonb),
    (10, 'practice', $l2_b10_title$Среднее$l2_b10_title$, $l2_b10_content$**Коротко:** Найдите среднее трёх чисел.

### Условие

На вход подаются три числа. Выведи их среднее, округлённое до 2 знаков.

### Вход

Три числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
1
2
3
```

Вывод:

```text
2.0
```

### Пример 2

Ввод:

```text
10
20
21
```

Вывод:

```text
17.0
```

### Шаблон

```python
a = float(input())
b = float(input())
c = float(input())
```

### Подсказки

1. Среднее: `(a + b + c) / 3`.

2. Используй `round(value, 2)`.$l2_b10_content$, $l2_b10_task$Среднее$l2_b10_task$, NULL::jsonb),
    (11, 'practice', $l2_b11_title$Формула$l2_b11_title$, $l2_b11_content$**Коротко:** Соберите формулу покупки.

### Условие

На вход подаются цена, количество, скидка и доставка. Итог: `price * count - скидка + доставка`. Скидка задаётся в процентах от `price * count`. Выведи итог, округлив до 2 знаков.

### Вход

Четыре числа: цена, количество, скидка, доставка.

### Выход

Одно число.

### Пример 1

Ввод:

```text
200
3
10
50
```

Вывод:

```text
590.0
```

### Пример 2

Ввод:

```text
100
2
0
30
```

Вывод:

```text
230.0
```

### Шаблон

```python
price = float(input())
count = int(input())
discount = float(input())
delivery = float(input())
```

### Подсказки

1. Сначала найди сумму без скидки.

2. Скидка: `subtotal * discount / 100`.$l2_b11_content$, $l2_b11_task$Формула$l2_b11_task$, NULL::jsonb),
    (12, 'quiz', $l2_b12_title$Итог$l2_b12_title$, $l2_b12_content$### Вопрос

Что выведет `17 % 5`?

### Варианты

1. 3

2. 2

3. 5

4. 17$l2_b12_content$, NULL, $l2_b12_quiz${"question":"Что выведет `17 % 5`?","options":[{"id":"A","text":"3"},{"id":"B","text":"2"},{"id":"C","text":"5"},{"id":"D","text":"17"}],"correctOptionId":"B","explanation":"`%` возвращает остаток от деления. 17 = 5 * 3 + 2."}$l2_b12_quiz$::jsonb)
), resolved AS (
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

-- Lesson 3: Урок 3. Условия
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 3
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l3_t2_title$Пароль$l3_t2_title$, $l3_t2_statement$**Коротко:** Проверьте пароль.

### Условие

На вход подаётся строка. Если она равна `python`, выведи `Доступ открыт`, иначе `Доступ закрыт`.

### Вход

Одна строка.

### Выход

Одна строка результата.

### Пример 1

Ввод:

```text
python
```

Вывод:

```text
Доступ открыт
```

### Пример 2

Ввод:

```text
qwerty
```

Вывод:

```text
Доступ закрыт
```

### Шаблон

```python
password = input()
```

### Подсказки

1. Для проверки равенства используй `==`.

2. Нужны `if` и `else`.$l3_t2_statement$, $l3_t2_starter$password = input()
$l3_t2_starter$, $l3_t2_solution$password = input()
if password == "python":
    print("Доступ открыт")
else:
    print("Доступ закрыт")
$l3_t2_solution$, 1, 45, $l3_t2_topic$Python M1 — Условия$l3_t2_topic$, 'python', $l3_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l3_t2_policy$::jsonb),
    ($l3_t4_title$Возраст$l3_t4_title$, $l3_t4_statement$**Коротко:** Проверьте совершеннолетие.

### Условие

На вход подаётся возраст. Если возраст 18 или больше, выведи `Можно`, иначе `Нельзя`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
18
```

Вывод:

```text
Можно
```

### Пример 2

Ввод:

```text
17
```

Вывод:

```text
Нельзя
```

### Шаблон

```python
age = int(input())
```

### Подсказки

1. Проверка: `age >= 18`.

2. Не забудь `else`.$l3_t4_statement$, $l3_t4_starter$age = int(input())
$l3_t4_starter$, $l3_t4_solution$age = int(input())
if age >= 18:
    print("Можно")
else:
    print("Нельзя")
$l3_t4_solution$, 1, 45, $l3_t4_topic$Python M1 — Условия$l3_t4_topic$, 'python', $l3_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l3_t4_policy$::jsonb),
    ($l3_t6_title$Оценка$l3_t6_title$, $l3_t6_statement$**Коротко:** Определите результат по баллам.

### Условие

На вход подаётся балл от 0 до 100. Выведи: `Отлично` для 90+, `Хорошо` для 70–89, `Повторить` для меньших значений.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
95
```

Вывод:

```text
Отлично
```

### Пример 2

Ввод:

```text
70
```

Вывод:

```text
Хорошо
```

### Пример 3

Ввод:

```text
69
```

Вывод:

```text
Повторить
```

### Шаблон

```python
score = int(input())
```

### Подсказки

1. Сначала проверяй 90+.

2. Потом 70+, затем `else`.$l3_t6_statement$, $l3_t6_starter$score = int(input())
$l3_t6_starter$, $l3_t6_solution$score = int(input())
if score >= 90:
    print("Отлично")
elif score >= 70:
    print("Хорошо")
else:
    print("Повторить")
$l3_t6_solution$, 2, 55, $l3_t6_topic$Python M1 — Условия$l3_t6_topic$, 'python', $l3_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l3_t6_policy$::jsonb),
    ($l3_t8_title$Скидка$l3_t8_title$, $l3_t8_statement$**Коротко:** Определите скидку по сумме.

### Условие

На вход подаётся сумма покупки. Выведи размер скидки: `0%` до 1000, `5%` от 1000 до 4999, `10%` от 5000.

### Вход

Одно целое число.

### Выход

Одна строка со скидкой.

### Пример 1

Ввод:

```text
999
```

Вывод:

```text
0%
```

### Пример 2

Ввод:

```text
1000
```

Вывод:

```text
5%
```

### Пример 3

Ввод:

```text
5000
```

Вывод:

```text
10%
```

### Шаблон

```python
amount = int(input())
```

### Подсказки

1. Начни с проверки `amount >= 5000`.

2. Потом проверь `amount >= 1000`.$l3_t8_statement$, $l3_t8_starter$amount = int(input())
$l3_t8_starter$, $l3_t8_solution$amount = int(input())
if amount >= 5000:
    print("10%")
elif amount >= 1000:
    print("5%")
else:
    print("0%")
$l3_t8_solution$, 2, 55, $l3_t8_topic$Python M1 — Условия$l3_t8_topic$, 'python', $l3_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l3_t8_policy$::jsonb),
    ($l3_t9_title$Чётность$l3_t9_title$, $l3_t9_statement$**Коротко:** Проверьте чётность числа.

### Условие

На вход подаётся целое число. Выведи `Чётное`, если число чётное, иначе `Нечётное`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
10
```

Вывод:

```text
Чётное
```

### Пример 2

Ввод:

```text
7
```

Вывод:

```text
Нечётное
```

### Шаблон

```python
number = int(input())
```

### Подсказки

1. Используй остаток от деления на 2.

2. Чётное число: `number % 2 == 0`.$l3_t9_statement$, $l3_t9_starter$number = int(input())
$l3_t9_starter$, $l3_t9_solution$number = int(input())
if number % 2 == 0:
    print("Чётное")
else:
    print("Нечётное")
$l3_t9_solution$, 2, 55, $l3_t9_topic$Python M1 — Условия$l3_t9_topic$, 'python', $l3_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l3_t9_policy$::jsonb),
    ($l3_t10_title$Ошибка =$l3_t10_title$, $l3_t10_statement$**Коротко:** Исправьте сравнение.

### Код с ошибкой

```python
age = int(input())
if age = 18:
    print("Ровно 18")
```

### Что нужно сделать

Код должен вывести `Ровно 18`, если введено число 18. Иначе вывести `Другое`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
18
```

Вывод:

```text
Ровно 18
```

### Пример 2

Ввод:

```text
19
```

Вывод:

```text
Другое
```

### Подсказки

1. `=` — присваивание.

2. Для сравнения нужен `==`.$l3_t10_statement$, $l3_t10_starter$age = int(input())
if age = 18:
    print("Ровно 18")
$l3_t10_starter$, $l3_t10_solution$age = int(input())
if age == 18:
    print("Ровно 18")
else:
    print("Другое")
$l3_t10_solution$, 2, 45, $l3_t10_topic$Python M1 — Условия$l3_t10_topic$, 'python', $l3_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l3_t10_policy$::jsonb),
    ($l3_t11_title$Категория$l3_t11_title$, $l3_t11_statement$**Коротко:** Определите возрастную категорию.

### Условие

На вход подаётся возраст. Выведи: `Ребёнок` до 7, `Школьник` от 7 до 17, `Взрослый` от 18 до 59, `Пенсионер` от 60.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
6
```

Вывод:

```text
Ребёнок
```

### Пример 2

Ввод:

```text
7
```

Вывод:

```text
Школьник
```

### Пример 3

Ввод:

```text
60
```

Вывод:

```text
Пенсионер
```

### Шаблон

```python
age = int(input())
```

### Подсказки

1. Проверяй категории сверху вниз.

2. Можно идти от меньшего к большему: `< 7`, `< 18`, `< 60`, `else`.$l3_t11_statement$, $l3_t11_starter$age = int(input())
$l3_t11_starter$, $l3_t11_solution$age = int(input())
if age < 7:
    print("Ребёнок")
elif age < 18:
    print("Школьник")
elif age < 60:
    print("Взрослый")
else:
    print("Пенсионер")
$l3_t11_solution$, 2, 70, $l3_t11_topic$Python M1 — Условия$l3_t11_topic$, 'python', $l3_t11_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l3_t11_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 3
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l3_t2_delete_title$Пароль$l3_t2_delete_title$,
        $l3_t4_delete_title$Возраст$l3_t4_delete_title$,
        $l3_t6_delete_title$Оценка$l3_t6_delete_title$,
        $l3_t8_delete_title$Скидка$l3_t8_delete_title$,
        $l3_t9_delete_title$Чётность$l3_t9_delete_title$,
        $l3_t10_delete_title$Ошибка =$l3_t10_delete_title$,
        $l3_t11_delete_title$Категория$l3_t11_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 3
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l3_test_2_1_title$Пароль$l3_test_2_1_title$, $l3_test_2_1_input$python$l3_test_2_1_input$, $l3_test_2_1_expected$Доступ открыт$l3_test_2_1_expected$, FALSE, 1),
    ($l3_test_2_2_title$Пароль$l3_test_2_2_title$, $l3_test_2_2_input$qwerty$l3_test_2_2_input$, $l3_test_2_2_expected$Доступ закрыт$l3_test_2_2_expected$, TRUE, 2),
    ($l3_test_2_3_title$Пароль$l3_test_2_3_title$, $l3_test_2_3_input$Python$l3_test_2_3_input$, $l3_test_2_3_expected$Доступ закрыт$l3_test_2_3_expected$, TRUE, 3),
    ($l3_test_4_1_title$Возраст$l3_test_4_1_title$, $l3_test_4_1_input$18$l3_test_4_1_input$, $l3_test_4_1_expected$Можно$l3_test_4_1_expected$, FALSE, 1),
    ($l3_test_4_2_title$Возраст$l3_test_4_2_title$, $l3_test_4_2_input$17$l3_test_4_2_input$, $l3_test_4_2_expected$Нельзя$l3_test_4_2_expected$, TRUE, 2),
    ($l3_test_4_3_title$Возраст$l3_test_4_3_title$, $l3_test_4_3_input$0$l3_test_4_3_input$, $l3_test_4_3_expected$Нельзя$l3_test_4_3_expected$, TRUE, 3),
    ($l3_test_4_4_title$Возраст$l3_test_4_4_title$, $l3_test_4_4_input$99$l3_test_4_4_input$, $l3_test_4_4_expected$Можно$l3_test_4_4_expected$, TRUE, 4),
    ($l3_test_6_1_title$Оценка$l3_test_6_1_title$, $l3_test_6_1_input$95$l3_test_6_1_input$, $l3_test_6_1_expected$Отлично$l3_test_6_1_expected$, FALSE, 1),
    ($l3_test_6_2_title$Оценка$l3_test_6_2_title$, $l3_test_6_2_input$90$l3_test_6_2_input$, $l3_test_6_2_expected$Отлично$l3_test_6_2_expected$, TRUE, 2),
    ($l3_test_6_3_title$Оценка$l3_test_6_3_title$, $l3_test_6_3_input$89$l3_test_6_3_input$, $l3_test_6_3_expected$Хорошо$l3_test_6_3_expected$, TRUE, 3),
    ($l3_test_6_4_title$Оценка$l3_test_6_4_title$, $l3_test_6_4_input$70$l3_test_6_4_input$, $l3_test_6_4_expected$Хорошо$l3_test_6_4_expected$, TRUE, 4),
    ($l3_test_6_5_title$Оценка$l3_test_6_5_title$, $l3_test_6_5_input$69$l3_test_6_5_input$, $l3_test_6_5_expected$Повторить$l3_test_6_5_expected$, TRUE, 5),
    ($l3_test_8_1_title$Скидка$l3_test_8_1_title$, $l3_test_8_1_input$999$l3_test_8_1_input$, $l3_test_8_1_expected$0%$l3_test_8_1_expected$, FALSE, 1),
    ($l3_test_8_2_title$Скидка$l3_test_8_2_title$, $l3_test_8_2_input$1000$l3_test_8_2_input$, $l3_test_8_2_expected$5%$l3_test_8_2_expected$, TRUE, 2),
    ($l3_test_8_3_title$Скидка$l3_test_8_3_title$, $l3_test_8_3_input$4999$l3_test_8_3_input$, $l3_test_8_3_expected$5%$l3_test_8_3_expected$, TRUE, 3),
    ($l3_test_8_4_title$Скидка$l3_test_8_4_title$, $l3_test_8_4_input$5000$l3_test_8_4_input$, $l3_test_8_4_expected$10%$l3_test_8_4_expected$, TRUE, 4),
    ($l3_test_9_1_title$Чётность$l3_test_9_1_title$, $l3_test_9_1_input$10$l3_test_9_1_input$, $l3_test_9_1_expected$Чётное$l3_test_9_1_expected$, FALSE, 1),
    ($l3_test_9_2_title$Чётность$l3_test_9_2_title$, $l3_test_9_2_input$7$l3_test_9_2_input$, $l3_test_9_2_expected$Нечётное$l3_test_9_2_expected$, TRUE, 2),
    ($l3_test_9_3_title$Чётность$l3_test_9_3_title$, $l3_test_9_3_input$0$l3_test_9_3_input$, $l3_test_9_3_expected$Чётное$l3_test_9_3_expected$, TRUE, 3),
    ($l3_test_9_4_title$Чётность$l3_test_9_4_title$, $l3_test_9_4_input$-3$l3_test_9_4_input$, $l3_test_9_4_expected$Нечётное$l3_test_9_4_expected$, TRUE, 4),
    ($l3_test_10_1_title$Ошибка =$l3_test_10_1_title$, $l3_test_10_1_input$18$l3_test_10_1_input$, $l3_test_10_1_expected$Ровно 18$l3_test_10_1_expected$, FALSE, 1),
    ($l3_test_10_2_title$Ошибка =$l3_test_10_2_title$, $l3_test_10_2_input$19$l3_test_10_2_input$, $l3_test_10_2_expected$Другое$l3_test_10_2_expected$, TRUE, 2),
    ($l3_test_10_3_title$Ошибка =$l3_test_10_3_title$, $l3_test_10_3_input$17$l3_test_10_3_input$, $l3_test_10_3_expected$Другое$l3_test_10_3_expected$, TRUE, 3),
    ($l3_test_11_1_title$Категория$l3_test_11_1_title$, $l3_test_11_1_input$6$l3_test_11_1_input$, $l3_test_11_1_expected$Ребёнок$l3_test_11_1_expected$, FALSE, 1),
    ($l3_test_11_2_title$Категория$l3_test_11_2_title$, $l3_test_11_2_input$7$l3_test_11_2_input$, $l3_test_11_2_expected$Школьник$l3_test_11_2_expected$, TRUE, 2),
    ($l3_test_11_3_title$Категория$l3_test_11_3_title$, $l3_test_11_3_input$17$l3_test_11_3_input$, $l3_test_11_3_expected$Школьник$l3_test_11_3_expected$, TRUE, 3),
    ($l3_test_11_4_title$Категория$l3_test_11_4_title$, $l3_test_11_4_input$18$l3_test_11_4_input$, $l3_test_11_4_expected$Взрослый$l3_test_11_4_expected$, TRUE, 4),
    ($l3_test_11_5_title$Категория$l3_test_11_5_title$, $l3_test_11_5_input$59$l3_test_11_5_input$, $l3_test_11_5_expected$Взрослый$l3_test_11_5_expected$, TRUE, 5),
    ($l3_test_11_6_title$Категория$l3_test_11_6_title$, $l3_test_11_6_input$60$l3_test_11_6_input$, $l3_test_11_6_expected$Пенсионер$l3_test_11_6_expected$, TRUE, 6)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 3
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l3_b1_title$Сравнения$l3_b1_title$, $l3_b1_content$Условия позволяют программе принимать решения.

Операторы сравнения:

| Оператор | Значение |
|---|---|
| `==` | равно |
| `!=` | не равно |
| `>` | больше |
| `<` | меньше |
| `>=` | больше или равно |
| `<=` | меньше или равно |$l3_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l3_b2_title$Пароль$l3_b2_title$, $l3_b2_content$**Коротко:** Проверьте пароль.

### Условие

На вход подаётся строка. Если она равна `python`, выведи `Доступ открыт`, иначе `Доступ закрыт`.

### Вход

Одна строка.

### Выход

Одна строка результата.

### Пример 1

Ввод:

```text
python
```

Вывод:

```text
Доступ открыт
```

### Пример 2

Ввод:

```text
qwerty
```

Вывод:

```text
Доступ закрыт
```

### Шаблон

```python
password = input()
```

### Подсказки

1. Для проверки равенства используй `==`.

2. Нужны `if` и `else`.$l3_b2_content$, $l3_b2_task$Пароль$l3_b2_task$, NULL::jsonb),
    (3, 'theory', $l3_b3_title$if else$l3_b3_title$, $l3_b3_content$`if` проверяет условие. `else` выполняется, если условие ложно.

```python
age = int(input())

if age >= 18:
    print("Можно")
else:
    print("Нельзя")
```

Отступы обязательны: строки внутри `if` сдвигаются вправо.$l3_b3_content$, NULL, NULL::jsonb),
    (4, 'practice', $l3_b4_title$Возраст$l3_b4_title$, $l3_b4_content$**Коротко:** Проверьте совершеннолетие.

### Условие

На вход подаётся возраст. Если возраст 18 или больше, выведи `Можно`, иначе `Нельзя`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
18
```

Вывод:

```text
Можно
```

### Пример 2

Ввод:

```text
17
```

Вывод:

```text
Нельзя
```

### Шаблон

```python
age = int(input())
```

### Подсказки

1. Проверка: `age >= 18`.

2. Не забудь `else`.$l3_b4_content$, $l3_b4_task$Возраст$l3_b4_task$, NULL::jsonb),
    (5, 'theory', $l3_b5_title$elif$l3_b5_title$, $l3_b5_content$`elif` нужен, когда вариантов больше двух.

```python
score = int(input())

if score >= 90:
    print("Отлично")
elif score >= 70:
    print("Хорошо")
else:
    print("Нужно повторить")
```

Python проверяет условия сверху вниз.$l3_b5_content$, NULL, NULL::jsonb),
    (6, 'practice', $l3_b6_title$Оценка$l3_b6_title$, $l3_b6_content$**Коротко:** Определите результат по баллам.

### Условие

На вход подаётся балл от 0 до 100. Выведи: `Отлично` для 90+, `Хорошо` для 70–89, `Повторить` для меньших значений.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
95
```

Вывод:

```text
Отлично
```

### Пример 2

Ввод:

```text
70
```

Вывод:

```text
Хорошо
```

### Пример 3

Ввод:

```text
69
```

Вывод:

```text
Повторить
```

### Шаблон

```python
score = int(input())
```

### Подсказки

1. Сначала проверяй 90+.

2. Потом 70+, затем `else`.$l3_b6_content$, $l3_b6_task$Оценка$l3_b6_task$, NULL::jsonb),
    (7, 'theory', $l3_b7_title$Границы$l3_b7_title$, $l3_b7_content$В задачах с условиями важны границы.

Если сказано `от 18`, проверка должна включать 18:
```python
age >= 18
```

Если сказано `меньше 18`, проверка:
```python
age < 18
```$l3_b7_content$, NULL, NULL::jsonb),
    (8, 'practice', $l3_b8_title$Скидка$l3_b8_title$, $l3_b8_content$**Коротко:** Определите скидку по сумме.

### Условие

На вход подаётся сумма покупки. Выведи размер скидки: `0%` до 1000, `5%` от 1000 до 4999, `10%` от 5000.

### Вход

Одно целое число.

### Выход

Одна строка со скидкой.

### Пример 1

Ввод:

```text
999
```

Вывод:

```text
0%
```

### Пример 2

Ввод:

```text
1000
```

Вывод:

```text
5%
```

### Пример 3

Ввод:

```text
5000
```

Вывод:

```text
10%
```

### Шаблон

```python
amount = int(input())
```

### Подсказки

1. Начни с проверки `amount >= 5000`.

2. Потом проверь `amount >= 1000`.$l3_b8_content$, $l3_b8_task$Скидка$l3_b8_task$, NULL::jsonb),
    (9, 'practice', $l3_b9_title$Чётность$l3_b9_title$, $l3_b9_content$**Коротко:** Проверьте чётность числа.

### Условие

На вход подаётся целое число. Выведи `Чётное`, если число чётное, иначе `Нечётное`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
10
```

Вывод:

```text
Чётное
```

### Пример 2

Ввод:

```text
7
```

Вывод:

```text
Нечётное
```

### Шаблон

```python
number = int(input())
```

### Подсказки

1. Используй остаток от деления на 2.

2. Чётное число: `number % 2 == 0`.$l3_b9_content$, $l3_b9_task$Чётность$l3_b9_task$, NULL::jsonb),
    (10, 'practice', $l3_b10_title$Ошибка =$l3_b10_title$, $l3_b10_content$**Коротко:** Исправьте сравнение.

### Код с ошибкой

```python
age = int(input())
if age = 18:
    print("Ровно 18")
```

### Что нужно сделать

Код должен вывести `Ровно 18`, если введено число 18. Иначе вывести `Другое`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
18
```

Вывод:

```text
Ровно 18
```

### Пример 2

Ввод:

```text
19
```

Вывод:

```text
Другое
```

### Подсказки

1. `=` — присваивание.

2. Для сравнения нужен `==`.$l3_b10_content$, $l3_b10_task$Ошибка =$l3_b10_task$, NULL::jsonb),
    (11, 'practice', $l3_b11_title$Категория$l3_b11_title$, $l3_b11_content$**Коротко:** Определите возрастную категорию.

### Условие

На вход подаётся возраст. Выведи: `Ребёнок` до 7, `Школьник` от 7 до 17, `Взрослый` от 18 до 59, `Пенсионер` от 60.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
6
```

Вывод:

```text
Ребёнок
```

### Пример 2

Ввод:

```text
7
```

Вывод:

```text
Школьник
```

### Пример 3

Ввод:

```text
60
```

Вывод:

```text
Пенсионер
```

### Шаблон

```python
age = int(input())
```

### Подсказки

1. Проверяй категории сверху вниз.

2. Можно идти от меньшего к большему: `< 7`, `< 18`, `< 60`, `else`.$l3_b11_content$, $l3_b11_task$Категория$l3_b11_task$, NULL::jsonb),
    (12, 'quiz', $l3_b12_title$Итог$l3_b12_title$, $l3_b12_content$### Вопрос

Чем отличается `=` от `==`?

### Варианты

1. Ничем

2. `=` сравнивает, `==` присваивает

3. `=` присваивает, `==` сравнивает

4. Оба выводят текст$l3_b12_content$, NULL, $l3_b12_quiz${"question":"Чем отличается `=` от `==`?","options":[{"id":"A","text":"Ничем"},{"id":"B","text":"`=` сравнивает, `==` присваивает"},{"id":"C","text":"`=` присваивает, `==` сравнивает"},{"id":"D","text":"Оба выводят текст"}],"correctOptionId":"C","explanation":"`=` сохраняет значение в переменную, `==` сравнивает два значения."}$l3_b12_quiz$::jsonb)
), resolved AS (
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

-- Lesson 4: Урок 4. Логика
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 4
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l4_t2_title$Диапазон$l4_t2_title$, $l4_t2_statement$**Коротко:** Проверьте число в диапазоне.

### Условие

На вход подаётся число. Если оно от 1 до 10 включительно, выведи `Внутри`, иначе `Снаружи`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
1
```

Вывод:

```text
Внутри
```

### Пример 2

Ввод:

```text
10
```

Вывод:

```text
Внутри
```

### Пример 3

Ввод:

```text
11
```

Вывод:

```text
Снаружи
```

### Шаблон

```python
number = int(input())
```

### Подсказки

1. Нужны две проверки.

2. Используй `and`.$l4_t2_statement$, $l4_t2_starter$number = int(input())
$l4_t2_starter$, $l4_t2_solution$number = int(input())
if number >= 1 and number <= 10:
    print("Внутри")
else:
    print("Снаружи")
$l4_t2_solution$, 1, 45, $l4_t2_topic$Python M1 — Логика$l4_t2_topic$, 'python', $l4_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l4_t2_policy$::jsonb),
    ($l4_t3_title$Два условия$l4_t3_title$, $l4_t3_statement$**Коротко:** Проверьте возраст и балл.

### Условие

На вход подаются возраст и балл. Если возраст 18+ и балл 70+, выведи `Допущен`, иначе `Не допущен`.

### Вход

Два целых числа.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
18
70
```

Вывод:

```text
Допущен
```

### Пример 2

Ввод:

```text
17
90
```

Вывод:

```text
Не допущен
```

### Шаблон

```python
age = int(input())
score = int(input())
```

### Подсказки

1. Оба условия должны быть верны.

2. Используй `and`.$l4_t3_statement$, $l4_t3_starter$age = int(input())
score = int(input())
$l4_t3_starter$, $l4_t3_solution$age = int(input())
score = int(input())
if age >= 18 and score >= 70:
    print("Допущен")
else:
    print("Не допущен")
$l4_t3_solution$, 2, 55, $l4_t3_topic$Python M1 — Логика$l4_t3_topic$, 'python', $l4_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l4_t3_policy$::jsonb),
    ($l4_t5_title$Роль$l4_t5_title$, $l4_t5_statement$**Коротко:** Проверьте роль пользователя.

### Условие

На вход подаётся роль. Для `admin` и `moderator` выведи `Доступ`, для остальных — `Нет доступа`.

### Вход

Одна строка.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
admin
```

Вывод:

```text
Доступ
```

### Пример 2

Ввод:

```text
user
```

Вывод:

```text
Нет доступа
```

### Шаблон

```python
role = input()
```

### Подсказки

1. Нужен `or`.

2. Пиши `role == ...` с обеих сторон `or`.$l4_t5_statement$, $l4_t5_starter$role = input()
$l4_t5_starter$, $l4_t5_solution$role = input()
if role == "admin" or role == "moderator":
    print("Доступ")
else:
    print("Нет доступа")
$l4_t5_solution$, 2, 55, $l4_t5_topic$Python M1 — Логика$l4_t5_topic$, 'python', $l4_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l4_t5_policy$::jsonb),
    ($l4_t7_title$Запрет$l4_t7_title$, $l4_t7_statement$**Коротко:** Проверьте блокировку.

### Условие

На вход подаётся `yes` или `no`. `yes` значит пользователь заблокирован. Если не заблокирован, выведи `Можно`, иначе `Нельзя`.

### Вход

Одна строка: `yes` или `no`.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
no
```

Вывод:

```text
Можно
```

### Пример 2

Ввод:

```text
yes
```

Вывод:

```text
Нельзя
```

### Шаблон

```python
blocked = input()
```

### Подсказки

1. Сравни ввод с `yes`.

2. Можно решить через `if blocked == "no"` или через `not`.$l4_t7_statement$, $l4_t7_starter$blocked = input()
$l4_t7_starter$, $l4_t7_solution$blocked = input()
is_blocked = blocked == "yes"
if not is_blocked:
    print("Можно")
else:
    print("Нельзя")
$l4_t7_solution$, 2, 50, $l4_t7_topic$Python M1 — Логика$l4_t7_topic$, 'python', $l4_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l4_t7_policy$::jsonb),
    ($l4_t8_title$Ошибка or$l4_t8_title$, $l4_t8_statement$**Коротко:** Исправьте условие с or.

### Код с ошибкой

```python
role = input()
if role == "admin" or "moderator":
    print("Доступ")
else:
    print("Нет доступа")
```

### Что нужно сделать

Код должен давать доступ только ролям `admin` и `moderator`.

### Вход

Одна строка.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
user
```

Вывод:

```text
Нет доступа
```

### Пример 2

Ввод:

```text
moderator
```

Вывод:

```text
Доступ
```

### Подсказки

1. Строка `"moderator"` сама по себе считается истинной.

2. Нужно написать `role == "moderator"`.$l4_t8_statement$, $l4_t8_starter$role = input()
if role == "admin" or "moderator":
    print("Доступ")
else:
    print("Нет доступа")
$l4_t8_starter$, $l4_t8_solution$role = input()
if role == "admin" or role == "moderator":
    print("Доступ")
else:
    print("Нет доступа")
$l4_t8_solution$, 2, 45, $l4_t8_topic$Python M1 — Логика$l4_t8_topic$, 'python', $l4_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l4_t8_policy$::jsonb),
    ($l4_t9_title$Заявка$l4_t9_title$, $l4_t9_statement$**Коротко:** Примите решение по заявке.

### Условие

На вход подаются возраст, доход и наличие долга (`yes` или `no`). Одобрить заявку, если возраст 18+, доход 30000+ и долга нет. Выведи `Одобрено` или `Отказ`.

### Вход

Возраст, доход, долг — каждое с новой строки.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
20
50000
no
```

Вывод:

```text
Одобрено
```

### Пример 2

Ввод:

```text
20
50000
yes
```

Вывод:

```text
Отказ
```

### Шаблон

```python
age = int(input())
income = int(input())
debt = input()
```

### Подсказки

1. Все три условия должны быть верны.

2. Долга нет: `debt == "no"`.$l4_t9_statement$, $l4_t9_starter$age = int(input())
income = int(input())
debt = input()
$l4_t9_starter$, $l4_t9_solution$age = int(input())
income = int(input())
debt = input()
if age >= 18 and income >= 30000 and debt == "no":
    print("Одобрено")
else:
    print("Отказ")
$l4_t9_solution$, 3, 75, $l4_t9_topic$Python M1 — Логика$l4_t9_topic$, 'python', $l4_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l4_t9_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 4
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l4_t2_delete_title$Диапазон$l4_t2_delete_title$,
        $l4_t3_delete_title$Два условия$l4_t3_delete_title$,
        $l4_t5_delete_title$Роль$l4_t5_delete_title$,
        $l4_t7_delete_title$Запрет$l4_t7_delete_title$,
        $l4_t8_delete_title$Ошибка or$l4_t8_delete_title$,
        $l4_t9_delete_title$Заявка$l4_t9_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 4
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l4_test_2_1_title$Диапазон$l4_test_2_1_title$, $l4_test_2_1_input$1$l4_test_2_1_input$, $l4_test_2_1_expected$Внутри$l4_test_2_1_expected$, FALSE, 1),
    ($l4_test_2_2_title$Диапазон$l4_test_2_2_title$, $l4_test_2_2_input$10$l4_test_2_2_input$, $l4_test_2_2_expected$Внутри$l4_test_2_2_expected$, TRUE, 2),
    ($l4_test_2_3_title$Диапазон$l4_test_2_3_title$, $l4_test_2_3_input$0$l4_test_2_3_input$, $l4_test_2_3_expected$Снаружи$l4_test_2_3_expected$, TRUE, 3),
    ($l4_test_2_4_title$Диапазон$l4_test_2_4_title$, $l4_test_2_4_input$11$l4_test_2_4_input$, $l4_test_2_4_expected$Снаружи$l4_test_2_4_expected$, TRUE, 4),
    ($l4_test_3_1_title$Два условия$l4_test_3_1_title$, $l4_test_3_1_input$18
70$l4_test_3_1_input$, $l4_test_3_1_expected$Допущен$l4_test_3_1_expected$, FALSE, 1),
    ($l4_test_3_2_title$Два условия$l4_test_3_2_title$, $l4_test_3_2_input$17
90$l4_test_3_2_input$, $l4_test_3_2_expected$Не допущен$l4_test_3_2_expected$, TRUE, 2),
    ($l4_test_3_3_title$Два условия$l4_test_3_3_title$, $l4_test_3_3_input$20
69$l4_test_3_3_input$, $l4_test_3_3_expected$Не допущен$l4_test_3_3_expected$, TRUE, 3),
    ($l4_test_3_4_title$Два условия$l4_test_3_4_title$, $l4_test_3_4_input$25
100$l4_test_3_4_input$, $l4_test_3_4_expected$Допущен$l4_test_3_4_expected$, TRUE, 4),
    ($l4_test_5_1_title$Роль$l4_test_5_1_title$, $l4_test_5_1_input$admin$l4_test_5_1_input$, $l4_test_5_1_expected$Доступ$l4_test_5_1_expected$, FALSE, 1),
    ($l4_test_5_2_title$Роль$l4_test_5_2_title$, $l4_test_5_2_input$moderator$l4_test_5_2_input$, $l4_test_5_2_expected$Доступ$l4_test_5_2_expected$, TRUE, 2),
    ($l4_test_5_3_title$Роль$l4_test_5_3_title$, $l4_test_5_3_input$user$l4_test_5_3_input$, $l4_test_5_3_expected$Нет доступа$l4_test_5_3_expected$, TRUE, 3),
    ($l4_test_7_1_title$Запрет$l4_test_7_1_title$, $l4_test_7_1_input$no$l4_test_7_1_input$, $l4_test_7_1_expected$Можно$l4_test_7_1_expected$, FALSE, 1),
    ($l4_test_7_2_title$Запрет$l4_test_7_2_title$, $l4_test_7_2_input$yes$l4_test_7_2_input$, $l4_test_7_2_expected$Нельзя$l4_test_7_2_expected$, TRUE, 2),
    ($l4_test_8_1_title$Ошибка or$l4_test_8_1_title$, $l4_test_8_1_input$admin$l4_test_8_1_input$, $l4_test_8_1_expected$Доступ$l4_test_8_1_expected$, FALSE, 1),
    ($l4_test_8_2_title$Ошибка or$l4_test_8_2_title$, $l4_test_8_2_input$moderator$l4_test_8_2_input$, $l4_test_8_2_expected$Доступ$l4_test_8_2_expected$, TRUE, 2),
    ($l4_test_8_3_title$Ошибка or$l4_test_8_3_title$, $l4_test_8_3_input$user$l4_test_8_3_input$, $l4_test_8_3_expected$Нет доступа$l4_test_8_3_expected$, TRUE, 3),
    ($l4_test_9_1_title$Заявка$l4_test_9_1_title$, $l4_test_9_1_input$20
50000
no$l4_test_9_1_input$, $l4_test_9_1_expected$Одобрено$l4_test_9_1_expected$, FALSE, 1),
    ($l4_test_9_2_title$Заявка$l4_test_9_2_title$, $l4_test_9_2_input$17
50000
no$l4_test_9_2_input$, $l4_test_9_2_expected$Отказ$l4_test_9_2_expected$, TRUE, 2),
    ($l4_test_9_3_title$Заявка$l4_test_9_3_title$, $l4_test_9_3_input$20
29999
no$l4_test_9_3_input$, $l4_test_9_3_expected$Отказ$l4_test_9_3_expected$, TRUE, 3),
    ($l4_test_9_4_title$Заявка$l4_test_9_4_title$, $l4_test_9_4_input$20
50000
yes$l4_test_9_4_input$, $l4_test_9_4_expected$Отказ$l4_test_9_4_expected$, TRUE, 4)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 4
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l4_b1_title$and or not$l4_b1_title$, $l4_b1_content$Логические операторы помогают объединять условия.

| Оператор | Когда истина |
|---|---|
| `and` | оба условия верны |
| `or` | хотя бы одно условие верно |
| `not` | меняет истину на ложь |

Пример:
```python
age = int(input())
if age >= 18 and age <= 60:
    print("Подходит")
```$l4_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l4_b2_title$Диапазон$l4_b2_title$, $l4_b2_content$**Коротко:** Проверьте число в диапазоне.

### Условие

На вход подаётся число. Если оно от 1 до 10 включительно, выведи `Внутри`, иначе `Снаружи`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
1
```

Вывод:

```text
Внутри
```

### Пример 2

Ввод:

```text
10
```

Вывод:

```text
Внутри
```

### Пример 3

Ввод:

```text
11
```

Вывод:

```text
Снаружи
```

### Шаблон

```python
number = int(input())
```

### Подсказки

1. Нужны две проверки.

2. Используй `and`.$l4_b2_content$, $l4_b2_task$Диапазон$l4_b2_task$, NULL::jsonb),
    (3, 'practice', $l4_b3_title$Два условия$l4_b3_title$, $l4_b3_content$**Коротко:** Проверьте возраст и балл.

### Условие

На вход подаются возраст и балл. Если возраст 18+ и балл 70+, выведи `Допущен`, иначе `Не допущен`.

### Вход

Два целых числа.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
18
70
```

Вывод:

```text
Допущен
```

### Пример 2

Ввод:

```text
17
90
```

Вывод:

```text
Не допущен
```

### Шаблон

```python
age = int(input())
score = int(input())
```

### Подсказки

1. Оба условия должны быть верны.

2. Используй `and`.$l4_b3_content$, $l4_b3_task$Два условия$l4_b3_task$, NULL::jsonb),
    (4, 'theory', $l4_b4_title$or$l4_b4_title$, $l4_b4_content$`or` подходит, когда достаточно одного верного условия.

```python
role = input()
if role == "admin" or role == "moderator":
    print("Доступ")
```

Каждую проверку нужно писать полностью.$l4_b4_content$, NULL, NULL::jsonb),
    (5, 'practice', $l4_b5_title$Роль$l4_b5_title$, $l4_b5_content$**Коротко:** Проверьте роль пользователя.

### Условие

На вход подаётся роль. Для `admin` и `moderator` выведи `Доступ`, для остальных — `Нет доступа`.

### Вход

Одна строка.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
admin
```

Вывод:

```text
Доступ
```

### Пример 2

Ввод:

```text
user
```

Вывод:

```text
Нет доступа
```

### Шаблон

```python
role = input()
```

### Подсказки

1. Нужен `or`.

2. Пиши `role == ...` с обеих сторон `or`.$l4_b5_content$, $l4_b5_task$Роль$l4_b5_task$, NULL::jsonb),
    (6, 'theory', $l4_b6_title$not$l4_b6_title$, $l4_b6_content$`not` меняет значение условия на противоположное.

```python
is_blocked = input() == "yes"
if not is_blocked:
    print("Можно войти")
```$l4_b6_content$, NULL, NULL::jsonb),
    (7, 'practice', $l4_b7_title$Запрет$l4_b7_title$, $l4_b7_content$**Коротко:** Проверьте блокировку.

### Условие

На вход подаётся `yes` или `no`. `yes` значит пользователь заблокирован. Если не заблокирован, выведи `Можно`, иначе `Нельзя`.

### Вход

Одна строка: `yes` или `no`.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
no
```

Вывод:

```text
Можно
```

### Пример 2

Ввод:

```text
yes
```

Вывод:

```text
Нельзя
```

### Шаблон

```python
blocked = input()
```

### Подсказки

1. Сравни ввод с `yes`.

2. Можно решить через `if blocked == "no"` или через `not`.$l4_b7_content$, $l4_b7_task$Запрет$l4_b7_task$, NULL::jsonb),
    (8, 'practice', $l4_b8_title$Ошибка or$l4_b8_title$, $l4_b8_content$**Коротко:** Исправьте условие с or.

### Код с ошибкой

```python
role = input()
if role == "admin" or "moderator":
    print("Доступ")
else:
    print("Нет доступа")
```

### Что нужно сделать

Код должен давать доступ только ролям `admin` и `moderator`.

### Вход

Одна строка.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
user
```

Вывод:

```text
Нет доступа
```

### Пример 2

Ввод:

```text
moderator
```

Вывод:

```text
Доступ
```

### Подсказки

1. Строка `"moderator"` сама по себе считается истинной.

2. Нужно написать `role == "moderator"`.$l4_b8_content$, $l4_b8_task$Ошибка or$l4_b8_task$, NULL::jsonb),
    (9, 'practice', $l4_b9_title$Заявка$l4_b9_title$, $l4_b9_content$**Коротко:** Примите решение по заявке.

### Условие

На вход подаются возраст, доход и наличие долга (`yes` или `no`). Одобрить заявку, если возраст 18+, доход 30000+ и долга нет. Выведи `Одобрено` или `Отказ`.

### Вход

Возраст, доход, долг — каждое с новой строки.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
20
50000
no
```

Вывод:

```text
Одобрено
```

### Пример 2

Ввод:

```text
20
50000
yes
```

Вывод:

```text
Отказ
```

### Шаблон

```python
age = int(input())
income = int(input())
debt = input()
```

### Подсказки

1. Все три условия должны быть верны.

2. Долга нет: `debt == "no"`.$l4_b9_content$, $l4_b9_task$Заявка$l4_b9_task$, NULL::jsonb),
    (10, 'quiz', $l4_b10_title$Итог$l4_b10_title$, $l4_b10_content$### Вопрос

Как правильно проверить роль admin или moderator?

### Варианты

1. `role == "admin" or "moderator"`

2. `role == "admin" or role == "moderator"`

3. `role = "admin" or role = "moderator"`

4. `role == admin or moderator`$l4_b10_content$, NULL, $l4_b10_quiz${"question":"Как правильно проверить роль admin или moderator?","options":[{"id":"A","text":"`role == \"admin\" or \"moderator\"`"},{"id":"B","text":"`role == \"admin\" or role == \"moderator\"`"},{"id":"C","text":"`role = \"admin\" or role = \"moderator\"`"},{"id":"D","text":"`role == admin or moderator`"}],"correctOptionId":"B","explanation":"Каждое сравнение должно быть записано полностью."}$l4_b10_quiz$::jsonb)
), resolved AS (
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

-- Lesson 5: Урок 5. while
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 5
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l5_t2_title$От 1 до N$l5_t2_title$, $l5_t2_statement$**Коротко:** Выведите числа от 1 до n.

### Условие

На вход подаётся `n`. Выведи числа от 1 до `n`, каждое с новой строки.

### Вход

Одно целое число `n`.

### Выход

Числа от 1 до n.

### Пример 1

Ввод:

```text
3
```

Вывод:

```text
1
2
3
```

### Пример 2

Ввод:

```text
1
```

Вывод:

```text
1
```

### Шаблон

```python
n = int(input())
number = 1
```

### Подсказки

1. Цикл: `while number <= n`.

2. Внутри цикла увеличивай `number` на 1.$l5_t2_statement$, $l5_t2_starter$n = int(input())
number = 1
$l5_t2_starter$, $l5_t2_solution$n = int(input())
number = 1
while number <= n:
    print(number)
    number = number + 1
$l5_t2_solution$, 1, 50, $l5_t2_topic$Python M1 — while$l5_t2_topic$, 'python', $l5_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l5_t2_policy$::jsonb),
    ($l5_t4_title$Сумма N$l5_t4_title$, $l5_t4_statement$**Коротко:** Найдите сумму от 1 до n.

### Условие

На вход подаётся `n`. Выведи сумму чисел от 1 до `n`.

### Вход

Одно целое число.

### Выход

Одно число — сумма.

### Пример 1

Ввод:

```text
5
```

Вывод:

```text
15
```

### Пример 2

Ввод:

```text
1
```

Вывод:

```text
1
```

### Шаблон

```python
n = int(input())
total = 0
```

### Подсказки

1. Нужен счётчик от 1 до n.

2. На каждом шаге добавляй счётчик к `total`.$l5_t4_statement$, $l5_t4_starter$n = int(input())
total = 0
$l5_t4_starter$, $l5_t4_solution$n = int(input())
total = 0
number = 1
while number <= n:
    total = total + number
    number = number + 1
print(total)
$l5_t4_solution$, 2, 60, $l5_t4_topic$Python M1 — while$l5_t4_topic$, 'python', $l5_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l5_t4_policy$::jsonb),
    ($l5_t5_title$До нуля$l5_t5_title$, $l5_t5_statement$**Коротко:** Суммируйте числа до нуля.

### Условие

На вход подаются числа по одному. Ввод заканчивается числом `0`. Выведи сумму всех чисел до нуля.

### Вход

Несколько целых чисел, последнее — 0.

### Выход

Одно число — сумма.

### Пример 1

Ввод:

```text
1
2
3
0
```

Вывод:

```text
6
```

### Пример 2

Ввод:

```text
0
```

Вывод:

```text
0
```

### Шаблон

```python
total = 0
number = int(input())
```

### Подсказки

1. Пока число не равно 0, добавляй его к сумме.

2. В конце цикла считывай следующее число.$l5_t5_statement$, $l5_t5_starter$total = 0
number = int(input())
$l5_t5_starter$, $l5_t5_solution$total = 0
number = int(input())
while number != 0:
    total = total + number
    number = int(input())
print(total)
$l5_t5_solution$, 2, 65, $l5_t5_topic$Python M1 — while$l5_t5_topic$, 'python', $l5_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l5_t5_policy$::jsonb),
    ($l5_t7_title$Пароль$l5_t7_title$, $l5_t7_statement$**Коротко:** Повторяйте ввод до верного пароля.

### Условие

На вход подаются строки. Когда строка равна `python`, выведи `Вход выполнен` и останови программу. Неверные строки не выводи.

### Вход

Несколько строк, одна из них `python`.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
123
qwerty
python
```

Вывод:

```text
Вход выполнен
```

### Пример 2

Ввод:

```text
python
```

Вывод:

```text
Вход выполнен
```

### Шаблон

```python
while True:
    password = input()
```

### Подсказки

1. Используй бесконечный цикл.

2. Если пароль верный, выведи сообщение и сделай `break`.$l5_t7_statement$, $l5_t7_starter$while True:
    password = input()
$l5_t7_starter$, $l5_t7_solution$while True:
    password = input()
    if password == "python":
        print("Вход выполнен")
        break
$l5_t7_solution$, 2, 60, $l5_t7_topic$Python M1 — while$l5_t7_topic$, 'python', $l5_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l5_t7_policy$::jsonb),
    ($l5_t8_title$Бесконечный$l5_t8_title$, $l5_t8_statement$**Коротко:** Исправьте бесконечный цикл.

### Код с ошибкой

```python
number = 1
while number <= 5:
    print(number)
```

### Что нужно сделать

Код должен вывести числа от 1 до 5 и остановиться.

### Вход

Нет.

### Выход

Числа от 1 до 5.

### Пример 1

Ввод:

```text

```

Вывод:

```text
1
2
3
4
5
```

### Подсказки

1. Переменная `number` не меняется.

2. Добавь `number = number + 1` внутри цикла.$l5_t8_statement$, $l5_t8_starter$number = 1
while number <= 5:
    print(number)
$l5_t8_starter$, $l5_t8_solution$number = 1
while number <= 5:
    print(number)
    number = number + 1
$l5_t8_solution$, 2, 45, $l5_t8_topic$Python M1 — while$l5_t8_topic$, 'python', $l5_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l5_t8_policy$::jsonb),
    ($l5_t9_title$Угадай$l5_t9_title$, $l5_t9_statement$**Коротко:** Найдите число по попыткам.

### Условие

Первое число во входе — секрет. Дальше идут попытки. Для каждой неверной попытки выведи `Мимо`. Когда попытка равна секрету, выведи `Угадал` и остановись.

### Вход

Секрет и несколько попыток.

### Выход

Строки ответов.

### Пример 1

Ввод:

```text
5
1
2
5
```

Вывод:

```text
Мимо
Мимо
Угадал
```

### Пример 2

Ввод:

```text
3
3
```

Вывод:

```text
Угадал
```

### Шаблон

```python
secret = int(input())
```

### Подсказки

1. Считывай попытки в цикле.

2. При совпадении печатай `Угадал` и делай `break`.$l5_t9_statement$, $l5_t9_starter$secret = int(input())
$l5_t9_starter$, $l5_t9_solution$secret = int(input())
while True:
    guess = int(input())
    if guess == secret:
        print("Угадал")
        break
    else:
        print("Мимо")
$l5_t9_solution$, 3, 75, $l5_t9_topic$Python M1 — while$l5_t9_topic$, 'python', $l5_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l5_t9_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 5
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l5_t2_delete_title$От 1 до N$l5_t2_delete_title$,
        $l5_t4_delete_title$Сумма N$l5_t4_delete_title$,
        $l5_t5_delete_title$До нуля$l5_t5_delete_title$,
        $l5_t7_delete_title$Пароль$l5_t7_delete_title$,
        $l5_t8_delete_title$Бесконечный$l5_t8_delete_title$,
        $l5_t9_delete_title$Угадай$l5_t9_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 5
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l5_test_2_1_title$От 1 до N$l5_test_2_1_title$, $l5_test_2_1_input$3$l5_test_2_1_input$, $l5_test_2_1_expected$1
2
3$l5_test_2_1_expected$, FALSE, 1),
    ($l5_test_2_2_title$От 1 до N$l5_test_2_2_title$, $l5_test_2_2_input$1$l5_test_2_2_input$, $l5_test_2_2_expected$1$l5_test_2_2_expected$, TRUE, 2),
    ($l5_test_2_3_title$От 1 до N$l5_test_2_3_title$, $l5_test_2_3_input$5$l5_test_2_3_input$, $l5_test_2_3_expected$1
2
3
4
5$l5_test_2_3_expected$, TRUE, 3),
    ($l5_test_4_1_title$Сумма N$l5_test_4_1_title$, $l5_test_4_1_input$5$l5_test_4_1_input$, $l5_test_4_1_expected$15$l5_test_4_1_expected$, FALSE, 1),
    ($l5_test_4_2_title$Сумма N$l5_test_4_2_title$, $l5_test_4_2_input$1$l5_test_4_2_input$, $l5_test_4_2_expected$1$l5_test_4_2_expected$, TRUE, 2),
    ($l5_test_4_3_title$Сумма N$l5_test_4_3_title$, $l5_test_4_3_input$10$l5_test_4_3_input$, $l5_test_4_3_expected$55$l5_test_4_3_expected$, TRUE, 3),
    ($l5_test_5_1_title$До нуля$l5_test_5_1_title$, $l5_test_5_1_input$1
2
3
0$l5_test_5_1_input$, $l5_test_5_1_expected$6$l5_test_5_1_expected$, FALSE, 1),
    ($l5_test_5_2_title$До нуля$l5_test_5_2_title$, $l5_test_5_2_input$0$l5_test_5_2_input$, $l5_test_5_2_expected$0$l5_test_5_2_expected$, TRUE, 2),
    ($l5_test_5_3_title$До нуля$l5_test_5_3_title$, $l5_test_5_3_input$10
-5
0$l5_test_5_3_input$, $l5_test_5_3_expected$5$l5_test_5_3_expected$, TRUE, 3),
    ($l5_test_7_1_title$Пароль$l5_test_7_1_title$, $l5_test_7_1_input$123
qwerty
python$l5_test_7_1_input$, $l5_test_7_1_expected$Вход выполнен$l5_test_7_1_expected$, FALSE, 1),
    ($l5_test_7_2_title$Пароль$l5_test_7_2_title$, $l5_test_7_2_input$python$l5_test_7_2_input$, $l5_test_7_2_expected$Вход выполнен$l5_test_7_2_expected$, TRUE, 2),
    ($l5_test_8_1_title$Бесконечный$l5_test_8_1_title$, $l5_test_8_1_input$$l5_test_8_1_input$, $l5_test_8_1_expected$1
2
3
4
5$l5_test_8_1_expected$, FALSE, 1),
    ($l5_test_9_1_title$Угадай$l5_test_9_1_title$, $l5_test_9_1_input$5
1
2
5$l5_test_9_1_input$, $l5_test_9_1_expected$Мимо
Мимо
Угадал$l5_test_9_1_expected$, FALSE, 1),
    ($l5_test_9_2_title$Угадай$l5_test_9_2_title$, $l5_test_9_2_input$3
3$l5_test_9_2_input$, $l5_test_9_2_expected$Угадал$l5_test_9_2_expected$, TRUE, 2),
    ($l5_test_9_3_title$Угадай$l5_test_9_3_title$, $l5_test_9_3_input$10
1
10$l5_test_9_3_input$, $l5_test_9_3_expected$Мимо
Угадал$l5_test_9_3_expected$, TRUE, 3)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 5
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l5_b1_title$while$l5_b1_title$, $l5_b1_content$`while` повторяет код, пока условие истинно.

```python
number = 1
while number <= 5:
    print(number)
    number = number + 1
```

Важно менять переменную внутри цикла. Иначе цикл может стать бесконечным.$l5_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l5_b2_title$От 1 до N$l5_b2_title$, $l5_b2_content$**Коротко:** Выведите числа от 1 до n.

### Условие

На вход подаётся `n`. Выведи числа от 1 до `n`, каждое с новой строки.

### Вход

Одно целое число `n`.

### Выход

Числа от 1 до n.

### Пример 1

Ввод:

```text
3
```

Вывод:

```text
1
2
3
```

### Пример 2

Ввод:

```text
1
```

Вывод:

```text
1
```

### Шаблон

```python
n = int(input())
number = 1
```

### Подсказки

1. Цикл: `while number <= n`.

2. Внутри цикла увеличивай `number` на 1.$l5_b2_content$, $l5_b2_task$От 1 до N$l5_b2_task$, NULL::jsonb),
    (3, 'theory', $l5_b3_title$Счётчик$l5_b3_title$, $l5_b3_content$Для суммы часто используют накопитель.

```python
total = 0
number = 1
while number <= 5:
    total = total + number
    number = number + 1
print(total)
```

`total` хранит промежуточный результат.$l5_b3_content$, NULL, NULL::jsonb),
    (4, 'practice', $l5_b4_title$Сумма N$l5_b4_title$, $l5_b4_content$**Коротко:** Найдите сумму от 1 до n.

### Условие

На вход подаётся `n`. Выведи сумму чисел от 1 до `n`.

### Вход

Одно целое число.

### Выход

Одно число — сумма.

### Пример 1

Ввод:

```text
5
```

Вывод:

```text
15
```

### Пример 2

Ввод:

```text
1
```

Вывод:

```text
1
```

### Шаблон

```python
n = int(input())
total = 0
```

### Подсказки

1. Нужен счётчик от 1 до n.

2. На каждом шаге добавляй счётчик к `total`.$l5_b4_content$, $l5_b4_task$Сумма N$l5_b4_task$, NULL::jsonb),
    (5, 'practice', $l5_b5_title$До нуля$l5_b5_title$, $l5_b5_content$**Коротко:** Суммируйте числа до нуля.

### Условие

На вход подаются числа по одному. Ввод заканчивается числом `0`. Выведи сумму всех чисел до нуля.

### Вход

Несколько целых чисел, последнее — 0.

### Выход

Одно число — сумма.

### Пример 1

Ввод:

```text
1
2
3
0
```

Вывод:

```text
6
```

### Пример 2

Ввод:

```text
0
```

Вывод:

```text
0
```

### Шаблон

```python
total = 0
number = int(input())
```

### Подсказки

1. Пока число не равно 0, добавляй его к сумме.

2. В конце цикла считывай следующее число.$l5_b5_content$, $l5_b5_task$До нуля$l5_b5_task$, NULL::jsonb),
    (6, 'theory', $l5_b6_title$break$l5_b6_title$, $l5_b6_content$`break` останавливает цикл досрочно.

```python
while True:
    text = input()
    if text == "stop":
        break
```

`while True` всегда требует условия выхода через `break`.$l5_b6_content$, NULL, NULL::jsonb),
    (7, 'practice', $l5_b7_title$Пароль$l5_b7_title$, $l5_b7_content$**Коротко:** Повторяйте ввод до верного пароля.

### Условие

На вход подаются строки. Когда строка равна `python`, выведи `Вход выполнен` и останови программу. Неверные строки не выводи.

### Вход

Несколько строк, одна из них `python`.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
123
qwerty
python
```

Вывод:

```text
Вход выполнен
```

### Пример 2

Ввод:

```text
python
```

Вывод:

```text
Вход выполнен
```

### Шаблон

```python
while True:
    password = input()
```

### Подсказки

1. Используй бесконечный цикл.

2. Если пароль верный, выведи сообщение и сделай `break`.$l5_b7_content$, $l5_b7_task$Пароль$l5_b7_task$, NULL::jsonb),
    (8, 'practice', $l5_b8_title$Бесконечный$l5_b8_title$, $l5_b8_content$**Коротко:** Исправьте бесконечный цикл.

### Код с ошибкой

```python
number = 1
while number <= 5:
    print(number)
```

### Что нужно сделать

Код должен вывести числа от 1 до 5 и остановиться.

### Вход

Нет.

### Выход

Числа от 1 до 5.

### Пример 1

Ввод:

```text

```

Вывод:

```text
1
2
3
4
5
```

### Подсказки

1. Переменная `number` не меняется.

2. Добавь `number = number + 1` внутри цикла.$l5_b8_content$, $l5_b8_task$Бесконечный$l5_b8_task$, NULL::jsonb),
    (9, 'practice', $l5_b9_title$Угадай$l5_b9_title$, $l5_b9_content$**Коротко:** Найдите число по попыткам.

### Условие

Первое число во входе — секрет. Дальше идут попытки. Для каждой неверной попытки выведи `Мимо`. Когда попытка равна секрету, выведи `Угадал` и остановись.

### Вход

Секрет и несколько попыток.

### Выход

Строки ответов.

### Пример 1

Ввод:

```text
5
1
2
5
```

Вывод:

```text
Мимо
Мимо
Угадал
```

### Пример 2

Ввод:

```text
3
3
```

Вывод:

```text
Угадал
```

### Шаблон

```python
secret = int(input())
```

### Подсказки

1. Считывай попытки в цикле.

2. При совпадении печатай `Угадал` и делай `break`.$l5_b9_content$, $l5_b9_task$Угадай$l5_b9_task$, NULL::jsonb),
    (10, 'quiz', $l5_b10_title$Итог$l5_b10_title$, $l5_b10_content$### Вопрос

Что чаще всего вызывает бесконечный цикл?

### Варианты

1. `print()` внутри цикла

2. Переменная условия не меняется

3. Использование `int()`

4. Пустая строка$l5_b10_content$, NULL, $l5_b10_quiz${"question":"Что чаще всего вызывает бесконечный цикл?","options":[{"id":"A","text":"`print()` внутри цикла"},{"id":"B","text":"Переменная условия не меняется"},{"id":"C","text":"Использование `int()`"},{"id":"D","text":"Пустая строка"}],"correctOptionId":"B","explanation":"Если условие цикла всегда остаётся истинным, цикл не остановится."}$l5_b10_quiz$::jsonb)
), resolved AS (
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

-- Lesson 6: Урок 6. for и range
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 6
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l6_t2_title$От 1 до N$l6_t2_title$, $l6_t2_statement$**Коротко:** Выведите числа через for.

### Условие

На вход подаётся `n`. Выведи числа от 1 до `n` включительно.

### Вход

Одно целое число.

### Выход

Числа от 1 до n.

### Пример 1

Ввод:

```text
3
```

Вывод:

```text
1
2
3
```

### Шаблон

```python
n = int(input())
```

### Подсказки

1. Используй `range(1, n + 1)`.

2. Правая граница не включается.$l6_t2_statement$, $l6_t2_starter$n = int(input())
$l6_t2_starter$, $l6_t2_solution$n = int(input())
for i in range(1, n + 1):
    print(i)
$l6_t2_solution$, 1, 45, $l6_t2_topic$Python M1 — for и range$l6_t2_topic$, 'python', $l6_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l6_t2_policy$::jsonb),
    ($l6_t4_title$Повторить N$l6_t4_title$, $l6_t4_statement$**Коротко:** Выведите слово несколько раз.

### Условие

На вход подаются число `n` и слово. Выведи слово `n` раз, каждое с новой строки.

### Вход

Число и строка.

### Выход

Слово n раз.

### Пример 1

Ввод:

```text
3
код
```

Вывод:

```text
код
код
код
```

### Шаблон

```python
n = int(input())
word = input()
```

### Подсказки

1. Цикл можно написать `for i in range(n)`.

2. Индекс `i` можно не использовать.$l6_t4_statement$, $l6_t4_starter$n = int(input())
word = input()
$l6_t4_starter$, $l6_t4_solution$n = int(input())
word = input()
for i in range(n):
    print(word)
$l6_t4_solution$, 1, 45, $l6_t4_topic$Python M1 — for и range$l6_t4_topic$, 'python', $l6_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l6_t4_policy$::jsonb),
    ($l6_t5_title$Сумма чисел$l6_t5_title$, $l6_t5_statement$**Коротко:** Сложите n чисел.

### Условие

Сначала вводится `n`, затем `n` целых чисел. Выведи их сумму.

### Вход

Количество чисел и сами числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
3
10
20
30
```

Вывод:

```text
60
```

### Пример 2

Ввод:

```text
1
5
```

Вывод:

```text
5
```

### Шаблон

```python
n = int(input())
total = 0
```

### Подсказки

1. Цикл должен повториться `n` раз.

2. Внутри цикла считывай число и добавляй к `total`.$l6_t5_statement$, $l6_t5_starter$n = int(input())
total = 0
$l6_t5_starter$, $l6_t5_solution$n = int(input())
total = 0
for i in range(n):
    number = int(input())
    total = total + number
print(total)
$l6_t5_solution$, 2, 60, $l6_t5_topic$Python M1 — for и range$l6_t5_topic$, 'python', $l6_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l6_t5_policy$::jsonb),
    ($l6_t6_title$Чётные$l6_t6_title$, $l6_t6_statement$**Коротко:** Выведите чётные от 1 до n.

### Условие

На вход подаётся `n`. Выведи все чётные числа от 1 до `n`.

### Вход

Одно целое число.

### Выход

Чётные числа, каждое с новой строки. Если их нет, ничего не выводи.

### Пример 1

Ввод:

```text
6
```

Вывод:

```text
2
4
6
```

### Пример 2

Ввод:

```text
1
```

Вывод:

```text

```

### Шаблон

```python
n = int(input())
```

### Подсказки

1. Можно идти от 2 с шагом 2.

2. `range(2, n + 1, 2)`.$l6_t6_statement$, $l6_t6_starter$n = int(input())
$l6_t6_starter$, $l6_t6_solution$n = int(input())
for i in range(2, n + 1, 2):
    print(i)
$l6_t6_solution$, 2, 55, $l6_t6_topic$Python M1 — for и range$l6_t6_topic$, 'python', $l6_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l6_t6_policy$::jsonb),
    ($l6_t8_title$Максимум$l6_t8_title$, $l6_t8_statement$**Коротко:** Найдите максимум из n чисел.

### Условие

Сначала вводится `n`, затем `n` целых чисел. Выведи максимальное число.

### Вход

Количество и числа.

### Выход

Одно число — максимум.

### Пример 1

Ввод:

```text
3
5
9
1
```

Вывод:

```text
9
```

### Пример 2

Ввод:

```text
1
-5
```

Вывод:

```text
-5
```

### Шаблон

```python
n = int(input())
maximum = None
```

### Подсказки

1. Считай первое число отдельно или используй `None`.

2. Если новое число больше максимума, обнови максимум.$l6_t8_statement$, $l6_t8_starter$n = int(input())
maximum = None
$l6_t8_starter$, $l6_t8_solution$n = int(input())
maximum = int(input())
for i in range(n - 1):
    number = int(input())
    if number > maximum:
        maximum = number
print(maximum)
$l6_t8_solution$, 3, 70, $l6_t8_topic$Python M1 — for и range$l6_t8_topic$, 'python', $l6_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l6_t8_policy$::jsonb),
    ($l6_t9_title$Количество$l6_t9_title$, $l6_t9_statement$**Коротко:** Посчитайте числа больше 10.

### Условие

Сначала вводится `n`, затем `n` чисел. Выведи, сколько из них больше 10.

### Вход

Количество и числа.

### Выход

Одно число — количество.

### Пример 1

Ввод:

```text
5
1
11
10
20
30
```

Вывод:

```text
3
```

### Шаблон

```python
n = int(input())
count = 0
```

### Подсказки

1. Нужен счётчик `count`.

2. Увеличивай его, если `number > 10`.$l6_t9_statement$, $l6_t9_starter$n = int(input())
count = 0
$l6_t9_starter$, $l6_t9_solution$n = int(input())
count = 0
for i in range(n):
    number = int(input())
    if number > 10:
        count = count + 1
print(count)
$l6_t9_solution$, 2, 60, $l6_t9_topic$Python M1 — for и range$l6_t9_topic$, 'python', $l6_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l6_t9_policy$::jsonb),
    ($l6_t10_title$Таблица$l6_t10_title$, $l6_t10_statement$**Коротко:** Выведите таблицу умножения.

### Условие

На вход подаётся число `n`. Выведи строки умножения от 1 до 10 в формате `n x i = result`.

### Вход

Одно целое число.

### Выход

10 строк таблицы.

### Пример 1

Ввод:

```text
3
```

Вывод:

```text
3 x 1 = 3
3 x 2 = 6
3 x 3 = 9
3 x 4 = 12
3 x 5 = 15
3 x 6 = 18
3 x 7 = 21
3 x 8 = 24
3 x 9 = 27
3 x 10 = 30
```

### Шаблон

```python
n = int(input())
```

### Подсказки

1. Цикл: `for i in range(1, 11)`.

2. Результат: `n * i`.$l6_t10_statement$, $l6_t10_starter$n = int(input())
$l6_t10_starter$, $l6_t10_solution$n = int(input())
for i in range(1, 11):
    print(n, "x", i, "=", n * i)
$l6_t10_solution$, 3, 75, $l6_t10_topic$Python M1 — for и range$l6_t10_topic$, 'python', $l6_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l6_t10_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 6
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l6_t2_delete_title$От 1 до N$l6_t2_delete_title$,
        $l6_t4_delete_title$Повторить N$l6_t4_delete_title$,
        $l6_t5_delete_title$Сумма чисел$l6_t5_delete_title$,
        $l6_t6_delete_title$Чётные$l6_t6_delete_title$,
        $l6_t8_delete_title$Максимум$l6_t8_delete_title$,
        $l6_t9_delete_title$Количество$l6_t9_delete_title$,
        $l6_t10_delete_title$Таблица$l6_t10_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 6
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l6_test_2_1_title$От 1 до N$l6_test_2_1_title$, $l6_test_2_1_input$3$l6_test_2_1_input$, $l6_test_2_1_expected$1
2
3$l6_test_2_1_expected$, FALSE, 1),
    ($l6_test_2_2_title$От 1 до N$l6_test_2_2_title$, $l6_test_2_2_input$1$l6_test_2_2_input$, $l6_test_2_2_expected$1$l6_test_2_2_expected$, TRUE, 2),
    ($l6_test_2_3_title$От 1 до N$l6_test_2_3_title$, $l6_test_2_3_input$5$l6_test_2_3_input$, $l6_test_2_3_expected$1
2
3
4
5$l6_test_2_3_expected$, TRUE, 3),
    ($l6_test_4_1_title$Повторить N$l6_test_4_1_title$, $l6_test_4_1_input$3
код$l6_test_4_1_input$, $l6_test_4_1_expected$код
код
код$l6_test_4_1_expected$, FALSE, 1),
    ($l6_test_4_2_title$Повторить N$l6_test_4_2_title$, $l6_test_4_2_input$1
Python$l6_test_4_2_input$, $l6_test_4_2_expected$Python$l6_test_4_2_expected$, TRUE, 2),
    ($l6_test_4_3_title$Повторить N$l6_test_4_3_title$, $l6_test_4_3_input$0
text$l6_test_4_3_input$, $l6_test_4_3_expected$$l6_test_4_3_expected$, TRUE, 3),
    ($l6_test_5_1_title$Сумма чисел$l6_test_5_1_title$, $l6_test_5_1_input$3
10
20
30$l6_test_5_1_input$, $l6_test_5_1_expected$60$l6_test_5_1_expected$, FALSE, 1),
    ($l6_test_5_2_title$Сумма чисел$l6_test_5_2_title$, $l6_test_5_2_input$1
5$l6_test_5_2_input$, $l6_test_5_2_expected$5$l6_test_5_2_expected$, TRUE, 2),
    ($l6_test_5_3_title$Сумма чисел$l6_test_5_3_title$, $l6_test_5_3_input$4
1
-1
2
-2$l6_test_5_3_input$, $l6_test_5_3_expected$0$l6_test_5_3_expected$, TRUE, 3),
    ($l6_test_6_1_title$Чётные$l6_test_6_1_title$, $l6_test_6_1_input$6$l6_test_6_1_input$, $l6_test_6_1_expected$2
4
6$l6_test_6_1_expected$, FALSE, 1),
    ($l6_test_6_2_title$Чётные$l6_test_6_2_title$, $l6_test_6_2_input$1$l6_test_6_2_input$, $l6_test_6_2_expected$$l6_test_6_2_expected$, TRUE, 2),
    ($l6_test_6_3_title$Чётные$l6_test_6_3_title$, $l6_test_6_3_input$2$l6_test_6_3_input$, $l6_test_6_3_expected$2$l6_test_6_3_expected$, TRUE, 3),
    ($l6_test_6_4_title$Чётные$l6_test_6_4_title$, $l6_test_6_4_input$7$l6_test_6_4_input$, $l6_test_6_4_expected$2
4
6$l6_test_6_4_expected$, TRUE, 4),
    ($l6_test_8_1_title$Максимум$l6_test_8_1_title$, $l6_test_8_1_input$3
5
9
1$l6_test_8_1_input$, $l6_test_8_1_expected$9$l6_test_8_1_expected$, FALSE, 1),
    ($l6_test_8_2_title$Максимум$l6_test_8_2_title$, $l6_test_8_2_input$1
-5$l6_test_8_2_input$, $l6_test_8_2_expected$-5$l6_test_8_2_expected$, TRUE, 2),
    ($l6_test_8_3_title$Максимум$l6_test_8_3_title$, $l6_test_8_3_input$4
-10
-3
-7
-1$l6_test_8_3_input$, $l6_test_8_3_expected$-1$l6_test_8_3_expected$, TRUE, 3),
    ($l6_test_9_1_title$Количество$l6_test_9_1_title$, $l6_test_9_1_input$5
1
11
10
20
30$l6_test_9_1_input$, $l6_test_9_1_expected$3$l6_test_9_1_expected$, FALSE, 1),
    ($l6_test_9_2_title$Количество$l6_test_9_2_title$, $l6_test_9_2_input$3
1
2
3$l6_test_9_2_input$, $l6_test_9_2_expected$0$l6_test_9_2_expected$, TRUE, 2),
    ($l6_test_9_3_title$Количество$l6_test_9_3_title$, $l6_test_9_3_input$2
11
12$l6_test_9_3_input$, $l6_test_9_3_expected$2$l6_test_9_3_expected$, TRUE, 3),
    ($l6_test_10_1_title$Таблица$l6_test_10_1_title$, $l6_test_10_1_input$1$l6_test_10_1_input$, $l6_test_10_1_expected$1 x 1 = 1
1 x 2 = 2
1 x 3 = 3
1 x 4 = 4
1 x 5 = 5
1 x 6 = 6
1 x 7 = 7
1 x 8 = 8
1 x 9 = 9
1 x 10 = 10$l6_test_10_1_expected$, FALSE, 1),
    ($l6_test_10_2_title$Таблица$l6_test_10_2_title$, $l6_test_10_2_input$3$l6_test_10_2_input$, $l6_test_10_2_expected$3 x 1 = 3
3 x 2 = 6
3 x 3 = 9
3 x 4 = 12
3 x 5 = 15
3 x 6 = 18
3 x 7 = 21
3 x 8 = 24
3 x 9 = 27
3 x 10 = 30$l6_test_10_2_expected$, TRUE, 2)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 6
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l6_b1_title$for range$l6_b1_title$, $l6_b1_content$`for` удобен, когда известно количество повторений.

```python
for i in range(5):
    print(i)
```

Вывод:
```text
0
1
2
3
4
```

`range(1, 5)` даёт числа 1, 2, 3, 4. Правая граница не включается.$l6_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l6_b2_title$От 1 до N$l6_b2_title$, $l6_b2_content$**Коротко:** Выведите числа через for.

### Условие

На вход подаётся `n`. Выведи числа от 1 до `n` включительно.

### Вход

Одно целое число.

### Выход

Числа от 1 до n.

### Пример 1

Ввод:

```text
3
```

Вывод:

```text
1
2
3
```

### Шаблон

```python
n = int(input())
```

### Подсказки

1. Используй `range(1, n + 1)`.

2. Правая граница не включается.$l6_b2_content$, $l6_b2_task$От 1 до N$l6_b2_task$, NULL::jsonb),
    (3, 'quiz', $l6_b3_title$Правая граница$l6_b3_title$, $l6_b3_content$### Вопрос

Что выведет `range(1, 4)` в цикле?

### Варианты

1. 1 2 3

2. 1 2 3 4

3. 0 1 2 3

4. 4$l6_b3_content$, NULL, $l6_b3_quiz${"question":"Что выведет `range(1, 4)` в цикле?","options":[{"id":"A","text":"1 2 3"},{"id":"B","text":"1 2 3 4"},{"id":"C","text":"0 1 2 3"},{"id":"D","text":"4"}],"correctOptionId":"A","explanation":"Правая граница `4` не включается."}$l6_b3_quiz$::jsonb),
    (4, 'practice', $l6_b4_title$Повторить N$l6_b4_title$, $l6_b4_content$**Коротко:** Выведите слово несколько раз.

### Условие

На вход подаются число `n` и слово. Выведи слово `n` раз, каждое с новой строки.

### Вход

Число и строка.

### Выход

Слово n раз.

### Пример 1

Ввод:

```text
3
код
```

Вывод:

```text
код
код
код
```

### Шаблон

```python
n = int(input())
word = input()
```

### Подсказки

1. Цикл можно написать `for i in range(n)`.

2. Индекс `i` можно не использовать.$l6_b4_content$, $l6_b4_task$Повторить N$l6_b4_task$, NULL::jsonb),
    (5, 'practice', $l6_b5_title$Сумма чисел$l6_b5_title$, $l6_b5_content$**Коротко:** Сложите n чисел.

### Условие

Сначала вводится `n`, затем `n` целых чисел. Выведи их сумму.

### Вход

Количество чисел и сами числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
3
10
20
30
```

Вывод:

```text
60
```

### Пример 2

Ввод:

```text
1
5
```

Вывод:

```text
5
```

### Шаблон

```python
n = int(input())
total = 0
```

### Подсказки

1. Цикл должен повториться `n` раз.

2. Внутри цикла считывай число и добавляй к `total`.$l6_b5_content$, $l6_b5_task$Сумма чисел$l6_b5_task$, NULL::jsonb),
    (6, 'practice', $l6_b6_title$Чётные$l6_b6_title$, $l6_b6_content$**Коротко:** Выведите чётные от 1 до n.

### Условие

На вход подаётся `n`. Выведи все чётные числа от 1 до `n`.

### Вход

Одно целое число.

### Выход

Чётные числа, каждое с новой строки. Если их нет, ничего не выводи.

### Пример 1

Ввод:

```text
6
```

Вывод:

```text
2
4
6
```

### Пример 2

Ввод:

```text
1
```

Вывод:

```text

```

### Шаблон

```python
n = int(input())
```

### Подсказки

1. Можно идти от 2 с шагом 2.

2. `range(2, n + 1, 2)`.$l6_b6_content$, $l6_b6_task$Чётные$l6_b6_task$, NULL::jsonb),
    (7, 'theory', $l6_b7_title$Ввод N чисел$l6_b7_title$, $l6_b7_content$Частый шаблон:

```python
n = int(input())
for i in range(n):
    number = int(input())
    # работа с number
```

Так считывают заранее известное количество чисел.$l6_b7_content$, NULL, NULL::jsonb),
    (8, 'practice', $l6_b8_title$Максимум$l6_b8_title$, $l6_b8_content$**Коротко:** Найдите максимум из n чисел.

### Условие

Сначала вводится `n`, затем `n` целых чисел. Выведи максимальное число.

### Вход

Количество и числа.

### Выход

Одно число — максимум.

### Пример 1

Ввод:

```text
3
5
9
1
```

Вывод:

```text
9
```

### Пример 2

Ввод:

```text
1
-5
```

Вывод:

```text
-5
```

### Шаблон

```python
n = int(input())
maximum = None
```

### Подсказки

1. Считай первое число отдельно или используй `None`.

2. Если новое число больше максимума, обнови максимум.$l6_b8_content$, $l6_b8_task$Максимум$l6_b8_task$, NULL::jsonb),
    (9, 'practice', $l6_b9_title$Количество$l6_b9_title$, $l6_b9_content$**Коротко:** Посчитайте числа больше 10.

### Условие

Сначала вводится `n`, затем `n` чисел. Выведи, сколько из них больше 10.

### Вход

Количество и числа.

### Выход

Одно число — количество.

### Пример 1

Ввод:

```text
5
1
11
10
20
30
```

Вывод:

```text
3
```

### Шаблон

```python
n = int(input())
count = 0
```

### Подсказки

1. Нужен счётчик `count`.

2. Увеличивай его, если `number > 10`.$l6_b9_content$, $l6_b9_task$Количество$l6_b9_task$, NULL::jsonb),
    (10, 'practice', $l6_b10_title$Таблица$l6_b10_title$, $l6_b10_content$**Коротко:** Выведите таблицу умножения.

### Условие

На вход подаётся число `n`. Выведи строки умножения от 1 до 10 в формате `n x i = result`.

### Вход

Одно целое число.

### Выход

10 строк таблицы.

### Пример 1

Ввод:

```text
3
```

Вывод:

```text
3 x 1 = 3
3 x 2 = 6
3 x 3 = 9
3 x 4 = 12
3 x 5 = 15
3 x 6 = 18
3 x 7 = 21
3 x 8 = 24
3 x 9 = 27
3 x 10 = 30
```

### Шаблон

```python
n = int(input())
```

### Подсказки

1. Цикл: `for i in range(1, 11)`.

2. Результат: `n * i`.$l6_b10_content$, $l6_b10_task$Таблица$l6_b10_task$, NULL::jsonb),
    (11, 'quiz', $l6_b11_title$Итог$l6_b11_title$, $l6_b11_content$### Вопрос

Почему для вывода от 1 до n пишут `range(1, n + 1)`?

### Варианты

1. Потому что range не включает правую границу

2. Потому что n нельзя использовать

3. Потому что for начинает с 1 всегда

4. Потому что print требует n + 1$l6_b11_content$, NULL, $l6_b11_quiz${"question":"Почему для вывода от 1 до n пишут `range(1, n + 1)`?","options":[{"id":"A","text":"Потому что range не включает правую границу"},{"id":"B","text":"Потому что n нельзя использовать"},{"id":"C","text":"Потому что for начинает с 1 всегда"},{"id":"D","text":"Потому что print требует n + 1"}],"correctOptionId":"A","explanation":"Правая граница в `range` не включается, поэтому нужно `n + 1`."}$l6_b11_quiz$::jsonb)
), resolved AS (
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

-- Lesson 7: Урок 7. Строки
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 7
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l7_t2_title$Длина$l7_t2_title$, $l7_t2_statement$**Коротко:** Выведите длину строки.

### Условие

На вход подаётся строка. Выведи количество символов в ней.

### Вход

Одна строка.

### Выход

Одно число.

### Пример 1

Ввод:

```text
Python
```

Вывод:

```text
6
```

### Пример 2

Ввод:

```text
код
```

Вывод:

```text
3
```

### Шаблон

```python
text = input()
```

### Подсказки

1. Используй `len(text)`.

2. Пробелы тоже считаются символами.$l7_t2_statement$, $l7_t2_starter$text = input()
$l7_t2_starter$, $l7_t2_solution$text = input()
print(len(text))
$l7_t2_solution$, 1, 40, $l7_t2_topic$Python M1 — Строки$l7_t2_topic$, 'python', $l7_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l7_t2_policy$::jsonb),
    ($l7_t4_title$Первый символ$l7_t4_title$, $l7_t4_statement$**Коротко:** Выведите первый символ строки.

### Условие

На вход подаётся непустая строка. Выведи её первый символ.

### Вход

Одна строка.

### Выход

Один символ.

### Пример 1

Ввод:

```text
Python
```

Вывод:

```text
P
```

### Пример 2

Ввод:

```text
код
```

Вывод:

```text
к
```

### Шаблон

```python
text = input()
```

### Подсказки

1. Первый символ имеет индекс 0.

2. Используй `text[0]`.$l7_t4_statement$, $l7_t4_starter$text = input()
$l7_t4_starter$, $l7_t4_solution$text = input()
print(text[0])
$l7_t4_solution$, 1, 40, $l7_t4_topic$Python M1 — Строки$l7_t4_topic$, 'python', $l7_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l7_t4_policy$::jsonb),
    ($l7_t6_title$Первые N$l7_t6_title$, $l7_t6_statement$**Коротко:** Выведите первые n символов.

### Условие

На вход подаются строка и число `n`. Выведи первые `n` символов строки.

### Вход

Строка и целое число.

### Выход

Часть строки.

### Пример 1

Ввод:

```text
Python
3
```

Вывод:

```text
Pyt
```

### Пример 2

Ввод:

```text
abcdef
2
```

Вывод:

```text
ab
```

### Шаблон

```python
text = input()
n = int(input())
```

### Подсказки

1. Срез от начала: `text[:n]`.

2. Если n больше длины, Python просто вернёт всю строку.$l7_t6_statement$, $l7_t6_starter$text = input()
n = int(input())
$l7_t6_starter$, $l7_t6_solution$text = input()
n = int(input())
print(text[:n])
$l7_t6_solution$, 2, 50, $l7_t6_topic$Python M1 — Строки$l7_t6_topic$, 'python', $l7_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l7_t6_policy$::jsonb),
    ($l7_t8_title$Палиндром$l7_t8_title$, $l7_t8_statement$**Коротко:** Проверьте слово на палиндром.

### Условие

На вход подаётся слово. Если оно читается одинаково слева направо и справа налево, выведи `Да`, иначе `Нет`.

### Вход

Одна строка.

### Выход

`Да` или `Нет`.

### Пример 1

Ввод:

```text
топот
```

Вывод:

```text
Да
```

### Пример 2

Ввод:

```text
python
```

Вывод:

```text
Нет
```

### Шаблон

```python
word = input()
```

### Подсказки

1. Переверни слово через `word[::-1]`.

2. Сравни исходное и перевёрнутое слово.$l7_t8_statement$, $l7_t8_starter$word = input()
$l7_t8_starter$, $l7_t8_solution$word = input()
if word == word[::-1]:
    print("Да")
else:
    print("Нет")
$l7_t8_solution$, 2, 60, $l7_t8_topic$Python M1 — Строки$l7_t8_topic$, 'python', $l7_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l7_t8_policy$::jsonb),
    ($l7_t10_title$Нормализация$l7_t10_title$, $l7_t10_statement$**Коротко:** Приведите строку к нижнему регистру.

### Условие

На вход подаётся строка. Убери пробелы по краям и выведи её в нижнем регистре.

### Вход

Одна строка.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
  PyThOn
```

Вывод:

```text
python
```

### Пример 2

Ввод:

```text
 CODE
```

Вывод:

```text
code
```

### Шаблон

```python
text = input()
```

### Подсказки

1. Сначала можно сделать `strip()`.

2. Потом `lower()`.$l7_t10_statement$, $l7_t10_starter$text = input()
$l7_t10_starter$, $l7_t10_solution$text = input()
print(text.strip().lower())
$l7_t10_solution$, 2, 55, $l7_t10_topic$Python M1 — Строки$l7_t10_topic$, 'python', $l7_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l7_t10_policy$::jsonb),
    ($l7_t11_title$Счёт букв$l7_t11_title$, $l7_t11_statement$**Коротко:** Посчитайте букву в строке.

### Условие

На вход подаются строка и символ. Выведи, сколько раз символ встречается в строке.

### Вход

Строка и один символ.

### Выход

Одно число.

### Пример 1

Ввод:

```text
banana
a
```

Вывод:

```text
3
```

### Пример 2

Ввод:

```text
hello
z
```

Вывод:

```text
0
```

### Шаблон

```python
text = input()
char = input()
```

### Подсказки

1. Перебери строку циклом `for`.

2. Увеличивай счётчик при совпадении.$l7_t11_statement$, $l7_t11_starter$text = input()
char = input()
$l7_t11_starter$, $l7_t11_solution$text = input()
char = input()
count = 0
for symbol in text:
    if symbol == char:
        count = count + 1
print(count)
$l7_t11_solution$, 2, 60, $l7_t11_topic$Python M1 — Строки$l7_t11_topic$, 'python', $l7_t11_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l7_t11_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 7
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l7_t2_delete_title$Длина$l7_t2_delete_title$,
        $l7_t4_delete_title$Первый символ$l7_t4_delete_title$,
        $l7_t6_delete_title$Первые N$l7_t6_delete_title$,
        $l7_t8_delete_title$Палиндром$l7_t8_delete_title$,
        $l7_t10_delete_title$Нормализация$l7_t10_delete_title$,
        $l7_t11_delete_title$Счёт букв$l7_t11_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 7
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l7_test_2_1_title$Длина$l7_test_2_1_title$, $l7_test_2_1_input$Python$l7_test_2_1_input$, $l7_test_2_1_expected$6$l7_test_2_1_expected$, FALSE, 1),
    ($l7_test_2_2_title$Длина$l7_test_2_2_title$, $l7_test_2_2_input$код$l7_test_2_2_input$, $l7_test_2_2_expected$3$l7_test_2_2_expected$, TRUE, 2),
    ($l7_test_2_3_title$Длина$l7_test_2_3_title$, $l7_test_2_3_input$a b$l7_test_2_3_input$, $l7_test_2_3_expected$3$l7_test_2_3_expected$, TRUE, 3),
    ($l7_test_4_1_title$Первый символ$l7_test_4_1_title$, $l7_test_4_1_input$Python$l7_test_4_1_input$, $l7_test_4_1_expected$P$l7_test_4_1_expected$, FALSE, 1),
    ($l7_test_4_2_title$Первый символ$l7_test_4_2_title$, $l7_test_4_2_input$код$l7_test_4_2_input$, $l7_test_4_2_expected$к$l7_test_4_2_expected$, TRUE, 2),
    ($l7_test_4_3_title$Первый символ$l7_test_4_3_title$, $l7_test_4_3_input$A$l7_test_4_3_input$, $l7_test_4_3_expected$A$l7_test_4_3_expected$, TRUE, 3),
    ($l7_test_6_1_title$Первые N$l7_test_6_1_title$, $l7_test_6_1_input$Python
3$l7_test_6_1_input$, $l7_test_6_1_expected$Pyt$l7_test_6_1_expected$, FALSE, 1),
    ($l7_test_6_2_title$Первые N$l7_test_6_2_title$, $l7_test_6_2_input$abcdef
2$l7_test_6_2_input$, $l7_test_6_2_expected$ab$l7_test_6_2_expected$, TRUE, 2),
    ($l7_test_6_3_title$Первые N$l7_test_6_3_title$, $l7_test_6_3_input$hi
10$l7_test_6_3_input$, $l7_test_6_3_expected$hi$l7_test_6_3_expected$, TRUE, 3),
    ($l7_test_8_1_title$Палиндром$l7_test_8_1_title$, $l7_test_8_1_input$топот$l7_test_8_1_input$, $l7_test_8_1_expected$Да$l7_test_8_1_expected$, FALSE, 1),
    ($l7_test_8_2_title$Палиндром$l7_test_8_2_title$, $l7_test_8_2_input$python$l7_test_8_2_input$, $l7_test_8_2_expected$Нет$l7_test_8_2_expected$, TRUE, 2),
    ($l7_test_8_3_title$Палиндром$l7_test_8_3_title$, $l7_test_8_3_input$а$l7_test_8_3_input$, $l7_test_8_3_expected$Да$l7_test_8_3_expected$, TRUE, 3),
    ($l7_test_10_1_title$Нормализация$l7_test_10_1_title$, $l7_test_10_1_input$  PyThOn$l7_test_10_1_input$, $l7_test_10_1_expected$python$l7_test_10_1_expected$, FALSE, 1),
    ($l7_test_10_2_title$Нормализация$l7_test_10_2_title$, $l7_test_10_2_input$ CODE$l7_test_10_2_input$, $l7_test_10_2_expected$code$l7_test_10_2_expected$, TRUE, 2),
    ($l7_test_10_3_title$Нормализация$l7_test_10_3_title$, $l7_test_10_3_input$test$l7_test_10_3_input$, $l7_test_10_3_expected$test$l7_test_10_3_expected$, TRUE, 3),
    ($l7_test_11_1_title$Счёт букв$l7_test_11_1_title$, $l7_test_11_1_input$banana
a$l7_test_11_1_input$, $l7_test_11_1_expected$3$l7_test_11_1_expected$, FALSE, 1),
    ($l7_test_11_2_title$Счёт букв$l7_test_11_2_title$, $l7_test_11_2_input$hello
z$l7_test_11_2_input$, $l7_test_11_2_expected$0$l7_test_11_2_expected$, TRUE, 2),
    ($l7_test_11_3_title$Счёт букв$l7_test_11_3_title$, $l7_test_11_3_input$aaaa
a$l7_test_11_3_input$, $l7_test_11_3_expected$4$l7_test_11_3_expected$, TRUE, 3)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 7
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l7_b1_title$Строки$l7_b1_title$, $l7_b1_content$Строка — это текст. Её можно хранить в переменной:
```python
text = "Python"
```

`len(text)` возвращает длину строки.$l7_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l7_b2_title$Длина$l7_b2_title$, $l7_b2_content$**Коротко:** Выведите длину строки.

### Условие

На вход подаётся строка. Выведи количество символов в ней.

### Вход

Одна строка.

### Выход

Одно число.

### Пример 1

Ввод:

```text
Python
```

Вывод:

```text
6
```

### Пример 2

Ввод:

```text
код
```

Вывод:

```text
3
```

### Шаблон

```python
text = input()
```

### Подсказки

1. Используй `len(text)`.

2. Пробелы тоже считаются символами.$l7_b2_content$, $l7_b2_task$Длина$l7_b2_task$, NULL::jsonb),
    (3, 'theory', $l7_b3_title$Индекс$l7_b3_title$, $l7_b3_content$У символов строки есть индексы. Первый символ имеет индекс 0.

```python
text = "Python"
print(text[0])  # P
print(text[1])  # y
```$l7_b3_content$, NULL, NULL::jsonb),
    (4, 'practice', $l7_b4_title$Первый символ$l7_b4_title$, $l7_b4_content$**Коротко:** Выведите первый символ строки.

### Условие

На вход подаётся непустая строка. Выведи её первый символ.

### Вход

Одна строка.

### Выход

Один символ.

### Пример 1

Ввод:

```text
Python
```

Вывод:

```text
P
```

### Пример 2

Ввод:

```text
код
```

Вывод:

```text
к
```

### Шаблон

```python
text = input()
```

### Подсказки

1. Первый символ имеет индекс 0.

2. Используй `text[0]`.$l7_b4_content$, $l7_b4_task$Первый символ$l7_b4_task$, NULL::jsonb),
    (5, 'theory', $l7_b5_title$Срезы$l7_b5_title$, $l7_b5_content$Срез берёт часть строки.

```python
text = "Python"
print(text[:3])  # Pyt
print(text[3:])  # hon
```$l7_b5_content$, NULL, NULL::jsonb),
    (6, 'practice', $l7_b6_title$Первые N$l7_b6_title$, $l7_b6_content$**Коротко:** Выведите первые n символов.

### Условие

На вход подаются строка и число `n`. Выведи первые `n` символов строки.

### Вход

Строка и целое число.

### Выход

Часть строки.

### Пример 1

Ввод:

```text
Python
3
```

Вывод:

```text
Pyt
```

### Пример 2

Ввод:

```text
abcdef
2
```

Вывод:

```text
ab
```

### Шаблон

```python
text = input()
n = int(input())
```

### Подсказки

1. Срез от начала: `text[:n]`.

2. Если n больше длины, Python просто вернёт всю строку.$l7_b6_content$, $l7_b6_task$Первые N$l7_b6_task$, NULL::jsonb),
    (7, 'theory', $l7_b7_title$Переворот$l7_b7_title$, $l7_b7_content$Строку можно перевернуть срезом:

```python
word = "топот"
print(word[::-1])
```

`[::-1]` создаёт строку в обратном порядке.$l7_b7_content$, NULL, NULL::jsonb),
    (8, 'practice', $l7_b8_title$Палиндром$l7_b8_title$, $l7_b8_content$**Коротко:** Проверьте слово на палиндром.

### Условие

На вход подаётся слово. Если оно читается одинаково слева направо и справа налево, выведи `Да`, иначе `Нет`.

### Вход

Одна строка.

### Выход

`Да` или `Нет`.

### Пример 1

Ввод:

```text
топот
```

Вывод:

```text
Да
```

### Пример 2

Ввод:

```text
python
```

Вывод:

```text
Нет
```

### Шаблон

```python
word = input()
```

### Подсказки

1. Переверни слово через `word[::-1]`.

2. Сравни исходное и перевёрнутое слово.$l7_b8_content$, $l7_b8_task$Палиндром$l7_b8_task$, NULL::jsonb),
    (9, 'theory', $l7_b9_title$Методы$l7_b9_title$, $l7_b9_content$У строк есть методы:

```python
text.lower()   # нижний регистр
text.upper()   # верхний регистр
text.strip()   # убрать пробелы по краям
```$l7_b9_content$, NULL, NULL::jsonb),
    (10, 'practice', $l7_b10_title$Нормализация$l7_b10_title$, $l7_b10_content$**Коротко:** Приведите строку к нижнему регистру.

### Условие

На вход подаётся строка. Убери пробелы по краям и выведи её в нижнем регистре.

### Вход

Одна строка.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
  PyThOn
```

Вывод:

```text
python
```

### Пример 2

Ввод:

```text
 CODE
```

Вывод:

```text
code
```

### Шаблон

```python
text = input()
```

### Подсказки

1. Сначала можно сделать `strip()`.

2. Потом `lower()`.$l7_b10_content$, $l7_b10_task$Нормализация$l7_b10_task$, NULL::jsonb),
    (11, 'practice', $l7_b11_title$Счёт букв$l7_b11_title$, $l7_b11_content$**Коротко:** Посчитайте букву в строке.

### Условие

На вход подаются строка и символ. Выведи, сколько раз символ встречается в строке.

### Вход

Строка и один символ.

### Выход

Одно число.

### Пример 1

Ввод:

```text
banana
a
```

Вывод:

```text
3
```

### Пример 2

Ввод:

```text
hello
z
```

Вывод:

```text
0
```

### Шаблон

```python
text = input()
char = input()
```

### Подсказки

1. Перебери строку циклом `for`.

2. Увеличивай счётчик при совпадении.$l7_b11_content$, $l7_b11_task$Счёт букв$l7_b11_task$, NULL::jsonb),
    (12, 'quiz', $l7_b12_title$Итог$l7_b12_title$, $l7_b12_content$### Вопрос

Как получить строку в обратном порядке?

### Варианты

1. `text[-1]`

2. `text[::-1]`

3. `reverse(text)`

4. `text[1:]`$l7_b12_content$, NULL, $l7_b12_quiz${"question":"Как получить строку в обратном порядке?","options":[{"id":"A","text":"`text[-1]`"},{"id":"B","text":"`text[::-1]`"},{"id":"C","text":"`reverse(text)`"},{"id":"D","text":"`text[1:]`"}],"correctOptionId":"B","explanation":"Срез `[::-1]` идёт по строке с шагом -1."}$l7_b12_quiz$::jsonb)
), resolved AS (
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

-- Lesson 8: Урок 8. Списки
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 8
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l8_t2_title$Первый элемент$l8_t2_title$, $l8_t2_statement$**Коротко:** Выведите первый элемент списка.

### Условие

На вход подаётся строка с элементами через пробел. Выведи первый элемент.

### Вход

Одна строка.

### Выход

Один элемент.

### Пример 1

Ввод:

```text
хлеб молоко сыр
```

Вывод:

```text
хлеб
```

### Пример 2

Ввод:

```text
a b c
```

Вывод:

```text
a
```

### Шаблон

```python
items = input().split()
```

### Подсказки

1. `split()` делает список строк.

2. Первый элемент: `items[0]`.$l8_t2_statement$, $l8_t2_starter$items = input().split()
$l8_t2_starter$, $l8_t2_solution$items = input().split()
print(items[0])
$l8_t2_solution$, 1, 45, $l8_t2_topic$Python M1 — Списки$l8_t2_topic$, 'python', $l8_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l8_t2_policy$::jsonb),
    ($l8_t4_title$Список покупок$l8_t4_title$, $l8_t4_statement$**Коротко:** Соберите список из n строк.

### Условие

Сначала вводится `n`, затем `n` товаров. Выведи каждый товар с новой строки.

### Вход

Количество и товары.

### Выход

Товары по одному в строке.

### Пример 1

Ввод:

```text
3
хлеб
молоко
сыр
```

Вывод:

```text
хлеб
молоко
сыр
```

### Шаблон

```python
n = int(input())
items = []
```

### Подсказки

1. В цикле считывай товар и добавляй в список.

2. Потом выведи элементы циклом.$l8_t4_statement$, $l8_t4_starter$n = int(input())
items = []
$l8_t4_starter$, $l8_t4_solution$n = int(input())
items = []
for i in range(n):
    item = input()
    items.append(item)
for item in items:
    print(item)
$l8_t4_solution$, 2, 55, $l8_t4_topic$Python M1 — Списки$l8_t4_topic$, 'python', $l8_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l8_t4_policy$::jsonb),
    ($l8_t6_title$Сумма списка$l8_t6_title$, $l8_t6_statement$**Коротко:** Сложите числа из строки.

### Условие

На вход подаётся строка целых чисел через пробел. Выведи их сумму.

### Вход

Одна строка чисел.

### Выход

Одно число.

### Пример 1

Ввод:

```text
1 2 3
```

Вывод:

```text
6
```

### Пример 2

Ввод:

```text
10 -5 2
```

Вывод:

```text
7
```

### Шаблон

```python
parts = input().split()
total = 0
```

### Подсказки

1. Перебери элементы списка.

2. Каждый элемент преобразуй через `int()`.$l8_t6_statement$, $l8_t6_starter$parts = input().split()
total = 0
$l8_t6_starter$, $l8_t6_solution$parts = input().split()
total = 0
for part in parts:
    total = total + int(part)
print(total)
$l8_t6_solution$, 2, 60, $l8_t6_topic$Python M1 — Списки$l8_t6_topic$, 'python', $l8_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l8_t6_policy$::jsonb),
    ($l8_t7_title$Фильтр$l8_t7_title$, $l8_t7_statement$**Коротко:** Выведите числа больше 10.

### Условие

На вход подаётся строка чисел через пробел. Выведи только числа больше 10, каждое с новой строки.

### Вход

Одна строка чисел.

### Выход

Числа больше 10. Если таких нет, ничего не выводи.

### Пример 1

Ввод:

```text
1 11 10 20
```

Вывод:

```text
11
20
```

### Пример 2

Ввод:

```text
1 2 3
```

Вывод:

```text

```

### Шаблон

```python
parts = input().split()
```

### Подсказки

1. Преобразуй каждый элемент в число.

2. Проверь `number > 10`.$l8_t7_statement$, $l8_t7_starter$parts = input().split()
$l8_t7_starter$, $l8_t7_solution$parts = input().split()
for part in parts:
    number = int(part)
    if number > 10:
        print(number)
$l8_t7_solution$, 2, 60, $l8_t7_topic$Python M1 — Списки$l8_t7_topic$, 'python', $l8_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l8_t7_policy$::jsonb),
    ($l8_t8_title$Минимум$l8_t8_title$, $l8_t8_statement$**Коротко:** Найдите минимальное число.

### Условие

На вход подаётся строка чисел через пробел. Выведи минимальное число.

### Вход

Одна строка чисел.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5 2 9
```

Вывод:

```text
2
```

### Пример 2

Ввод:

```text
-1 -5 3
```

Вывод:

```text
-5
```

### Шаблон

```python
numbers = input().split()
```

### Подсказки

1. Можно использовать `min`, но сначала нужны числа.

2. Или перебери список вручную.$l8_t8_statement$, $l8_t8_starter$numbers = input().split()
$l8_t8_starter$, $l8_t8_solution$parts = input().split()
minimum = int(parts[0])
for part in parts:
    number = int(part)
    if number < minimum:
        minimum = number
print(minimum)
$l8_t8_solution$, 2, 60, $l8_t8_topic$Python M1 — Списки$l8_t8_topic$, 'python', $l8_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l8_t8_policy$::jsonb),
    ($l8_t10_title$Все строки$l8_t10_title$, $l8_t10_statement$**Коротко:** Отфильтруйте слова по длине.

### Условие

На вход подаётся строка слов через пробел. Выведи слова длиной больше 3 символов, каждое с новой строки.

### Вход

Одна строка слов.

### Выход

Подходящие слова построчно.

### Пример 1

Ввод:

```text
кот собака дом python
```

Вывод:

```text
собака
python
```

### Шаблон

```python
words = input().split()
```

### Подсказки

1. Длина слова: `len(word)`.

2. Проверка: `len(word) > 3`.$l8_t10_statement$, $l8_t10_starter$words = input().split()
$l8_t10_starter$, $l8_t10_solution$words = input().split()
for word in words:
    if len(word) > 3:
        print(word)
$l8_t10_solution$, 2, 65, $l8_t10_topic$Python M1 — Списки$l8_t10_topic$, 'python', $l8_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l8_t10_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 8
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l8_t2_delete_title$Первый элемент$l8_t2_delete_title$,
        $l8_t4_delete_title$Список покупок$l8_t4_delete_title$,
        $l8_t6_delete_title$Сумма списка$l8_t6_delete_title$,
        $l8_t7_delete_title$Фильтр$l8_t7_delete_title$,
        $l8_t8_delete_title$Минимум$l8_t8_delete_title$,
        $l8_t10_delete_title$Все строки$l8_t10_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 8
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l8_test_2_1_title$Первый элемент$l8_test_2_1_title$, $l8_test_2_1_input$хлеб молоко сыр$l8_test_2_1_input$, $l8_test_2_1_expected$хлеб$l8_test_2_1_expected$, FALSE, 1),
    ($l8_test_2_2_title$Первый элемент$l8_test_2_2_title$, $l8_test_2_2_input$a b c$l8_test_2_2_input$, $l8_test_2_2_expected$a$l8_test_2_2_expected$, TRUE, 2),
    ($l8_test_2_3_title$Первый элемент$l8_test_2_3_title$, $l8_test_2_3_input$one$l8_test_2_3_input$, $l8_test_2_3_expected$one$l8_test_2_3_expected$, TRUE, 3),
    ($l8_test_4_1_title$Список покупок$l8_test_4_1_title$, $l8_test_4_1_input$3
хлеб
молоко
сыр$l8_test_4_1_input$, $l8_test_4_1_expected$хлеб
молоко
сыр$l8_test_4_1_expected$, FALSE, 1),
    ($l8_test_4_2_title$Список покупок$l8_test_4_2_title$, $l8_test_4_2_input$1
чай$l8_test_4_2_input$, $l8_test_4_2_expected$чай$l8_test_4_2_expected$, TRUE, 2),
    ($l8_test_6_1_title$Сумма списка$l8_test_6_1_title$, $l8_test_6_1_input$1 2 3$l8_test_6_1_input$, $l8_test_6_1_expected$6$l8_test_6_1_expected$, FALSE, 1),
    ($l8_test_6_2_title$Сумма списка$l8_test_6_2_title$, $l8_test_6_2_input$10 -5 2$l8_test_6_2_input$, $l8_test_6_2_expected$7$l8_test_6_2_expected$, TRUE, 2),
    ($l8_test_6_3_title$Сумма списка$l8_test_6_3_title$, $l8_test_6_3_input$0 0 0$l8_test_6_3_input$, $l8_test_6_3_expected$0$l8_test_6_3_expected$, TRUE, 3),
    ($l8_test_7_1_title$Фильтр$l8_test_7_1_title$, $l8_test_7_1_input$1 11 10 20$l8_test_7_1_input$, $l8_test_7_1_expected$11
20$l8_test_7_1_expected$, FALSE, 1),
    ($l8_test_7_2_title$Фильтр$l8_test_7_2_title$, $l8_test_7_2_input$1 2 3$l8_test_7_2_input$, $l8_test_7_2_expected$$l8_test_7_2_expected$, TRUE, 2),
    ($l8_test_7_3_title$Фильтр$l8_test_7_3_title$, $l8_test_7_3_input$12$l8_test_7_3_input$, $l8_test_7_3_expected$12$l8_test_7_3_expected$, TRUE, 3),
    ($l8_test_8_1_title$Минимум$l8_test_8_1_title$, $l8_test_8_1_input$5 2 9$l8_test_8_1_input$, $l8_test_8_1_expected$2$l8_test_8_1_expected$, FALSE, 1),
    ($l8_test_8_2_title$Минимум$l8_test_8_2_title$, $l8_test_8_2_input$-1 -5 3$l8_test_8_2_input$, $l8_test_8_2_expected$-5$l8_test_8_2_expected$, TRUE, 2),
    ($l8_test_8_3_title$Минимум$l8_test_8_3_title$, $l8_test_8_3_input$7$l8_test_8_3_input$, $l8_test_8_3_expected$7$l8_test_8_3_expected$, TRUE, 3),
    ($l8_test_10_1_title$Все строки$l8_test_10_1_title$, $l8_test_10_1_input$кот собака дом python$l8_test_10_1_input$, $l8_test_10_1_expected$собака
python$l8_test_10_1_expected$, FALSE, 1),
    ($l8_test_10_2_title$Все строки$l8_test_10_2_title$, $l8_test_10_2_input$a bb ccc$l8_test_10_2_input$, $l8_test_10_2_expected$$l8_test_10_2_expected$, TRUE, 2)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 8
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l8_b1_title$Списки$l8_b1_title$, $l8_b1_content$Список хранит несколько значений.

```python
items = ["хлеб", "молоко", "сыр"]
print(items[0])  # хлеб
```

Индексы начинаются с 0.$l8_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l8_b2_title$Первый элемент$l8_b2_title$, $l8_b2_content$**Коротко:** Выведите первый элемент списка.

### Условие

На вход подаётся строка с элементами через пробел. Выведи первый элемент.

### Вход

Одна строка.

### Выход

Один элемент.

### Пример 1

Ввод:

```text
хлеб молоко сыр
```

Вывод:

```text
хлеб
```

### Пример 2

Ввод:

```text
a b c
```

Вывод:

```text
a
```

### Шаблон

```python
items = input().split()
```

### Подсказки

1. `split()` делает список строк.

2. Первый элемент: `items[0]`.$l8_b2_content$, $l8_b2_task$Первый элемент$l8_b2_task$, NULL::jsonb),
    (3, 'theory', $l8_b3_title$append$l8_b3_title$, $l8_b3_content$`append()` добавляет элемент в конец списка.

```python
items = []
items.append("хлеб")
items.append("молоко")
```$l8_b3_content$, NULL, NULL::jsonb),
    (4, 'practice', $l8_b4_title$Список покупок$l8_b4_title$, $l8_b4_content$**Коротко:** Соберите список из n строк.

### Условие

Сначала вводится `n`, затем `n` товаров. Выведи каждый товар с новой строки.

### Вход

Количество и товары.

### Выход

Товары по одному в строке.

### Пример 1

Ввод:

```text
3
хлеб
молоко
сыр
```

Вывод:

```text
хлеб
молоко
сыр
```

### Шаблон

```python
n = int(input())
items = []
```

### Подсказки

1. В цикле считывай товар и добавляй в список.

2. Потом выведи элементы циклом.$l8_b4_content$, $l8_b4_task$Список покупок$l8_b4_task$, NULL::jsonb),
    (5, 'theory', $l8_b5_title$split$l8_b5_title$, $l8_b5_content$`input().split()` разбивает строку по пробелам.

```python
numbers = input().split()
```

Сначала это список строк. Для арифметики элементы нужно превращать в `int`.$l8_b5_content$, NULL, NULL::jsonb),
    (6, 'practice', $l8_b6_title$Сумма списка$l8_b6_title$, $l8_b6_content$**Коротко:** Сложите числа из строки.

### Условие

На вход подаётся строка целых чисел через пробел. Выведи их сумму.

### Вход

Одна строка чисел.

### Выход

Одно число.

### Пример 1

Ввод:

```text
1 2 3
```

Вывод:

```text
6
```

### Пример 2

Ввод:

```text
10 -5 2
```

Вывод:

```text
7
```

### Шаблон

```python
parts = input().split()
total = 0
```

### Подсказки

1. Перебери элементы списка.

2. Каждый элемент преобразуй через `int()`.$l8_b6_content$, $l8_b6_task$Сумма списка$l8_b6_task$, NULL::jsonb),
    (7, 'practice', $l8_b7_title$Фильтр$l8_b7_title$, $l8_b7_content$**Коротко:** Выведите числа больше 10.

### Условие

На вход подаётся строка чисел через пробел. Выведи только числа больше 10, каждое с новой строки.

### Вход

Одна строка чисел.

### Выход

Числа больше 10. Если таких нет, ничего не выводи.

### Пример 1

Ввод:

```text
1 11 10 20
```

Вывод:

```text
11
20
```

### Пример 2

Ввод:

```text
1 2 3
```

Вывод:

```text

```

### Шаблон

```python
parts = input().split()
```

### Подсказки

1. Преобразуй каждый элемент в число.

2. Проверь `number > 10`.$l8_b7_content$, $l8_b7_task$Фильтр$l8_b7_task$, NULL::jsonb),
    (8, 'practice', $l8_b8_title$Минимум$l8_b8_title$, $l8_b8_content$**Коротко:** Найдите минимальное число.

### Условие

На вход подаётся строка чисел через пробел. Выведи минимальное число.

### Вход

Одна строка чисел.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5 2 9
```

Вывод:

```text
2
```

### Пример 2

Ввод:

```text
-1 -5 3
```

Вывод:

```text
-5
```

### Шаблон

```python
numbers = input().split()
```

### Подсказки

1. Можно использовать `min`, но сначала нужны числа.

2. Или перебери список вручную.$l8_b8_content$, $l8_b8_task$Минимум$l8_b8_task$, NULL::jsonb),
    (9, 'theory', $l8_b9_title$Вывод списка$l8_b9_title$, $l8_b9_content$Не выводи список напрямую, если условие просит элементы построчно.

Плохо для таких задач:
```python
print(items)
```

Лучше:
```python
for item in items:
    print(item)
```$l8_b9_content$, NULL, NULL::jsonb),
    (10, 'practice', $l8_b10_title$Все строки$l8_b10_title$, $l8_b10_content$**Коротко:** Отфильтруйте слова по длине.

### Условие

На вход подаётся строка слов через пробел. Выведи слова длиной больше 3 символов, каждое с новой строки.

### Вход

Одна строка слов.

### Выход

Подходящие слова построчно.

### Пример 1

Ввод:

```text
кот собака дом python
```

Вывод:

```text
собака
python
```

### Шаблон

```python
words = input().split()
```

### Подсказки

1. Длина слова: `len(word)`.

2. Проверка: `len(word) > 3`.$l8_b10_content$, $l8_b10_task$Все строки$l8_b10_task$, NULL::jsonb),
    (11, 'quiz', $l8_b11_title$Итог$l8_b11_title$, $l8_b11_content$### Вопрос

Что делает `input().split()`?

### Варианты

1. Считает сумму

2. Создаёт список строк

3. Создаёт список чисел

4. Удаляет пробелы по краям$l8_b11_content$, NULL, $l8_b11_quiz${"question":"Что делает `input().split()`?","options":[{"id":"A","text":"Считает сумму"},{"id":"B","text":"Создаёт список строк"},{"id":"C","text":"Создаёт список чисел"},{"id":"D","text":"Удаляет пробелы по краям"}],"correctOptionId":"B","explanation":"`split()` разбивает строку на части и возвращает список строк."}$l8_b11_quiz$::jsonb)
), resolved AS (
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

-- Lesson 9: Урок 9. Словари
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 9
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l9_t2_title$Контакт$l9_t2_title$, $l9_t2_statement$**Коротко:** Выведите телефон по имени.

### Условие

Создай словарь с контактами: `Анна -> 111`, `Олег -> 222`. На вход подаётся имя. Выведи телефон.

### Вход

Одно имя.

### Выход

Телефон.

### Пример 1

Ввод:

```text
Анна
```

Вывод:

```text
111
```

### Пример 2

Ввод:

```text
Олег
```

Вывод:

```text
222
```

### Шаблон

```python
name = input()
contacts = {"Анна": "111", "Олег": "222"}
```

### Подсказки

1. Ключ — имя.

2. Значение — телефон.$l9_t2_statement$, $l9_t2_starter$name = input()
contacts = {"Анна": "111", "Олег": "222"}
$l9_t2_starter$, $l9_t2_solution$name = input()
contacts = {"Анна": "111", "Олег": "222"}
print(contacts[name])
$l9_t2_solution$, 1, 45, $l9_t2_topic$Python M1 — Словари$l9_t2_topic$, 'python', $l9_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l9_t2_policy$::jsonb),
    ($l9_t4_title$Поиск$l9_t4_title$, $l9_t4_statement$**Коротко:** Найдите контакт безопасно.

### Условие

Используй словарь контактов: `Анна -> 111`, `Олег -> 222`. Если имени нет, выведи `Не найдено`.

### Вход

Одно имя.

### Выход

Телефон или `Не найдено`.

### Пример 1

Ввод:

```text
Анна
```

Вывод:

```text
111
```

### Пример 2

Ввод:

```text
Маша
```

Вывод:

```text
Не найдено
```

### Шаблон

```python
name = input()
contacts = {"Анна": "111", "Олег": "222"}
```

### Подсказки

1. Используй `contacts.get(...)`.

2. Второй аргумент `get` — значение по умолчанию.$l9_t4_statement$, $l9_t4_starter$name = input()
contacts = {"Анна": "111", "Олег": "222"}
$l9_t4_starter$, $l9_t4_solution$name = input()
contacts = {"Анна": "111", "Олег": "222"}
print(contacts.get(name, "Не найдено"))
$l9_t4_solution$, 2, 55, $l9_t4_topic$Python M1 — Словари$l9_t4_topic$, 'python', $l9_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l9_t4_policy$::jsonb),
    ($l9_t5_title$Добавление$l9_t5_title$, $l9_t5_statement$**Коротко:** Добавьте пару в словарь.

### Условие

На вход подаются имя и телефон. Добавь контакт в пустой словарь и выведи телефон по этому имени.

### Вход

Имя и телефон.

### Выход

Телефон.

### Пример 1

Ввод:

```text
Иван
333
```

Вывод:

```text
333
```

### Шаблон

```python
name = input()
phone = input()
contacts = {}
```

### Подсказки

1. Добавление: `contacts[name] = phone`.

2. Потом выведи `contacts[name]`.$l9_t5_statement$, $l9_t5_starter$name = input()
phone = input()
contacts = {}
$l9_t5_starter$, $l9_t5_solution$name = input()
phone = input()
contacts = {}
contacts[name] = phone
print(contacts[name])
$l9_t5_solution$, 1, 45, $l9_t5_topic$Python M1 — Словари$l9_t5_topic$, 'python', $l9_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l9_t5_policy$::jsonb),
    ($l9_t7_title$Вывод оценок$l9_t7_title$, $l9_t7_statement$**Коротко:** Выведите оценки в заданном порядке.

### Условие

Дан словарь оценок в коде. Выведи оценки учеников в порядке: `Анна`, `Олег`, `Маша`.

### Вход

Нет.

### Выход

Три строки `Имя: оценка`.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Анна: 5
Олег: 4
Маша: 3
```

### Шаблон

```python
grades = {"Анна": 5, "Олег": 4, "Маша": 3}
```

### Подсказки

1. Для автопроверки порядок фиксирован.

2. Выводи имена из списка в нужном порядке.$l9_t7_statement$, $l9_t7_starter$grades = {"Анна": 5, "Олег": 4, "Маша": 3}
$l9_t7_starter$, $l9_t7_solution$grades = {"Анна": 5, "Олег": 4, "Маша": 3}
for name in ["Анна", "Олег", "Маша"]:
    print(name + ":", grades[name])
$l9_t7_solution$, 2, 55, $l9_t7_topic$Python M1 — Словари$l9_t7_topic$, 'python', $l9_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l9_t7_policy$::jsonb),
    ($l9_t8_title$Сумма товаров$l9_t8_title$, $l9_t8_statement$**Коротко:** Посчитайте стоимость корзины.

### Условие

Сначала вводится `n`, затем `n` строк: название товара и цена через пробел. Выведи общую сумму цен.

### Вход

Количество и товары с ценами.

### Выход

Одно число.

### Пример 1

Ввод:

```text
3
хлеб 50
молоко 80
сыр 120
```

Вывод:

```text
250
```

### Шаблон

```python
n = int(input())
products = {}
```

### Подсказки

1. Разбей строку через `split()`.

2. Цену преобразуй в `int`.$l9_t8_statement$, $l9_t8_starter$n = int(input())
products = {}
$l9_t8_starter$, $l9_t8_solution$n = int(input())
products = {}
for i in range(n):
    line = input().split()
    name = line[0]
    price = int(line[1])
    products[name] = price
total = 0
for price in products.values():
    total = total + price
print(total)
$l9_t8_solution$, 3, 75, $l9_t8_topic$Python M1 — Словари$l9_t8_topic$, 'python', $l9_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l9_t8_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 9
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l9_t2_delete_title$Контакт$l9_t2_delete_title$,
        $l9_t4_delete_title$Поиск$l9_t4_delete_title$,
        $l9_t5_delete_title$Добавление$l9_t5_delete_title$,
        $l9_t7_delete_title$Вывод оценок$l9_t7_delete_title$,
        $l9_t8_delete_title$Сумма товаров$l9_t8_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 9
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l9_test_2_1_title$Контакт$l9_test_2_1_title$, $l9_test_2_1_input$Анна$l9_test_2_1_input$, $l9_test_2_1_expected$111$l9_test_2_1_expected$, FALSE, 1),
    ($l9_test_2_2_title$Контакт$l9_test_2_2_title$, $l9_test_2_2_input$Олег$l9_test_2_2_input$, $l9_test_2_2_expected$222$l9_test_2_2_expected$, TRUE, 2),
    ($l9_test_4_1_title$Поиск$l9_test_4_1_title$, $l9_test_4_1_input$Анна$l9_test_4_1_input$, $l9_test_4_1_expected$111$l9_test_4_1_expected$, FALSE, 1),
    ($l9_test_4_2_title$Поиск$l9_test_4_2_title$, $l9_test_4_2_input$Олег$l9_test_4_2_input$, $l9_test_4_2_expected$222$l9_test_4_2_expected$, TRUE, 2),
    ($l9_test_4_3_title$Поиск$l9_test_4_3_title$, $l9_test_4_3_input$Маша$l9_test_4_3_input$, $l9_test_4_3_expected$Не найдено$l9_test_4_3_expected$, TRUE, 3),
    ($l9_test_5_1_title$Добавление$l9_test_5_1_title$, $l9_test_5_1_input$Иван
333$l9_test_5_1_input$, $l9_test_5_1_expected$333$l9_test_5_1_expected$, FALSE, 1),
    ($l9_test_5_2_title$Добавление$l9_test_5_2_title$, $l9_test_5_2_input$A
1$l9_test_5_2_input$, $l9_test_5_2_expected$1$l9_test_5_2_expected$, TRUE, 2),
    ($l9_test_7_1_title$Вывод оценок$l9_test_7_1_title$, $l9_test_7_1_input$$l9_test_7_1_input$, $l9_test_7_1_expected$Анна: 5
Олег: 4
Маша: 3$l9_test_7_1_expected$, FALSE, 1),
    ($l9_test_8_1_title$Сумма товаров$l9_test_8_1_title$, $l9_test_8_1_input$3
хлеб 50
молоко 80
сыр 120$l9_test_8_1_input$, $l9_test_8_1_expected$250$l9_test_8_1_expected$, FALSE, 1),
    ($l9_test_8_2_title$Сумма товаров$l9_test_8_2_title$, $l9_test_8_2_input$1
чай 100$l9_test_8_2_input$, $l9_test_8_2_expected$100$l9_test_8_2_expected$, TRUE, 2)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 9
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l9_b1_title$dict$l9_b1_title$, $l9_b1_content$Словарь хранит пары `ключ: значение`.

```python
user = {"name": "Анна", "age": 16}
print(user["name"])
```

Ключ помогает быстро найти значение.$l9_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l9_b2_title$Контакт$l9_b2_title$, $l9_b2_content$**Коротко:** Выведите телефон по имени.

### Условие

Создай словарь с контактами: `Анна -> 111`, `Олег -> 222`. На вход подаётся имя. Выведи телефон.

### Вход

Одно имя.

### Выход

Телефон.

### Пример 1

Ввод:

```text
Анна
```

Вывод:

```text
111
```

### Пример 2

Ввод:

```text
Олег
```

Вывод:

```text
222
```

### Шаблон

```python
name = input()
contacts = {"Анна": "111", "Олег": "222"}
```

### Подсказки

1. Ключ — имя.

2. Значение — телефон.$l9_b2_content$, $l9_b2_task$Контакт$l9_b2_task$, NULL::jsonb),
    (3, 'theory', $l9_b3_title$get$l9_b3_title$, $l9_b3_content$`get()` безопасно получает значение по ключу.

```python
contacts.get(name, "Не найдено")
```

Если ключа нет, вернётся значение по умолчанию.$l9_b3_content$, NULL, NULL::jsonb),
    (4, 'practice', $l9_b4_title$Поиск$l9_b4_title$, $l9_b4_content$**Коротко:** Найдите контакт безопасно.

### Условие

Используй словарь контактов: `Анна -> 111`, `Олег -> 222`. Если имени нет, выведи `Не найдено`.

### Вход

Одно имя.

### Выход

Телефон или `Не найдено`.

### Пример 1

Ввод:

```text
Анна
```

Вывод:

```text
111
```

### Пример 2

Ввод:

```text
Маша
```

Вывод:

```text
Не найдено
```

### Шаблон

```python
name = input()
contacts = {"Анна": "111", "Олег": "222"}
```

### Подсказки

1. Используй `contacts.get(...)`.

2. Второй аргумент `get` — значение по умолчанию.$l9_b4_content$, $l9_b4_task$Поиск$l9_b4_task$, NULL::jsonb),
    (5, 'practice', $l9_b5_title$Добавление$l9_b5_title$, $l9_b5_content$**Коротко:** Добавьте пару в словарь.

### Условие

На вход подаются имя и телефон. Добавь контакт в пустой словарь и выведи телефон по этому имени.

### Вход

Имя и телефон.

### Выход

Телефон.

### Пример 1

Ввод:

```text
Иван
333
```

Вывод:

```text
333
```

### Шаблон

```python
name = input()
phone = input()
contacts = {}
```

### Подсказки

1. Добавление: `contacts[name] = phone`.

2. Потом выведи `contacts[name]`.$l9_b5_content$, $l9_b5_task$Добавление$l9_b5_task$, NULL::jsonb),
    (6, 'theory', $l9_b6_title$items$l9_b6_title$, $l9_b6_content$`.items()` даёт пары ключ-значение.

```python
for name, phone in contacts.items():
    print(name, phone)
```$l9_b6_content$, NULL, NULL::jsonb),
    (7, 'practice', $l9_b7_title$Вывод оценок$l9_b7_title$, $l9_b7_content$**Коротко:** Выведите оценки в заданном порядке.

### Условие

Дан словарь оценок в коде. Выведи оценки учеников в порядке: `Анна`, `Олег`, `Маша`.

### Вход

Нет.

### Выход

Три строки `Имя: оценка`.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Анна: 5
Олег: 4
Маша: 3
```

### Шаблон

```python
grades = {"Анна": 5, "Олег": 4, "Маша": 3}
```

### Подсказки

1. Для автопроверки порядок фиксирован.

2. Выводи имена из списка в нужном порядке.$l9_b7_content$, $l9_b7_task$Вывод оценок$l9_b7_task$, NULL::jsonb),
    (8, 'practice', $l9_b8_title$Сумма товаров$l9_b8_title$, $l9_b8_content$**Коротко:** Посчитайте стоимость корзины.

### Условие

Сначала вводится `n`, затем `n` строк: название товара и цена через пробел. Выведи общую сумму цен.

### Вход

Количество и товары с ценами.

### Выход

Одно число.

### Пример 1

Ввод:

```text
3
хлеб 50
молоко 80
сыр 120
```

Вывод:

```text
250
```

### Шаблон

```python
n = int(input())
products = {}
```

### Подсказки

1. Разбей строку через `split()`.

2. Цену преобразуй в `int`.$l9_b8_content$, $l9_b8_task$Сумма товаров$l9_b8_task$, NULL::jsonb),
    (9, 'quiz', $l9_b9_title$Итог$l9_b9_title$, $l9_b9_content$### Вопрос

Что делает `dict.get(key, default)`?

### Варианты

1. Удаляет ключ

2. Получает значение или default

3. Сортирует словарь

4. Печатает словарь$l9_b9_content$, NULL, $l9_b9_quiz${"question":"Что делает `dict.get(key, default)`?","options":[{"id":"A","text":"Удаляет ключ"},{"id":"B","text":"Получает значение или default"},{"id":"C","text":"Сортирует словарь"},{"id":"D","text":"Печатает словарь"}],"correctOptionId":"B","explanation":"`get` возвращает значение по ключу, а если ключа нет — значение по умолчанию."}$l9_b9_quiz$::jsonb)
), resolved AS (
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

-- Lesson 10: Урок 10. Множества
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 10
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l10_t2_title$Уникальные$l10_t2_title$, $l10_t2_statement$**Коротко:** Посчитайте уникальные слова.

### Условие

На вход подаётся строка слов через пробел. Выведи количество уникальных слов.

### Вход

Одна строка.

### Выход

Одно число.

### Пример 1

Ввод:

```text
кот пёс кот
```

Вывод:

```text
2
```

### Пример 2

Ввод:

```text
a b c
```

Вывод:

```text
3
```

### Шаблон

```python
words = input().split()
```

### Подсказки

1. Создай `set(words)`.

2. Количество: `len(...)`.$l10_t2_statement$, $l10_t2_starter$words = input().split()
$l10_t2_starter$, $l10_t2_solution$words = input().split()
unique_words = set(words)
print(len(unique_words))
$l10_t2_solution$, 1, 45, $l10_t2_topic$Python M1 — Множества$l10_t2_topic$, 'python', $l10_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l10_t2_policy$::jsonb),
    ($l10_t4_title$Проверка$l10_t4_title$, $l10_t4_statement$**Коротко:** Проверьте слово в списке.

### Условие

Первая строка — набор слов. Вторая строка — слово для поиска. Если слово есть, выведи `Есть`, иначе `Нет`.

### Вход

Строка слов и слово.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
кот пёс
кот
```

Вывод:

```text
Есть
```

### Пример 2

Ввод:

```text
кот пёс
лось
```

Вывод:

```text
Нет
```

### Шаблон

```python
words = set(input().split())
word = input()
```

### Подсказки

1. Используй `word in words`.

2. Множество ускоряет поиск.$l10_t4_statement$, $l10_t4_starter$words = set(input().split())
word = input()
$l10_t4_starter$, $l10_t4_solution$words = set(input().split())
word = input()
if word in words:
    print("Есть")
else:
    print("Нет")
$l10_t4_solution$, 1, 45, $l10_t4_topic$Python M1 — Множества$l10_t4_topic$, 'python', $l10_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l10_t4_policy$::jsonb),
    ($l10_t6_title$Буквы$l10_t6_title$, $l10_t6_statement$**Коротко:** Посчитайте частоту буквы.

### Условие

На вход подаётся строка. Выведи, сколько раз встречается каждая буква `a`, `b`, `c` в фиксированном порядке.

### Вход

Одна строка.

### Выход

Три строки: `a:`, `b:`, `c:`.

### Пример 1

Ввод:

```text
abac
```

Вывод:

```text
a: 2
b: 1
c: 1
```

### Шаблон

```python
text = input()
```

### Подсказки

1. Создай словарь счётчиков.

2. Выводи буквы в порядке `a`, `b`, `c`.$l10_t6_statement$, $l10_t6_starter$text = input()
$l10_t6_starter$, $l10_t6_solution$text = input()
counts = {"a": 0, "b": 0, "c": 0}
for char in text:
    if char in counts:
        counts[char] = counts[char] + 1
for char in ["a", "b", "c"]:
    print(char + ":", counts[char])
$l10_t6_solution$, 2, 60, $l10_t6_topic$Python M1 — Множества$l10_t6_topic$, 'python', $l10_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l10_t6_policy$::jsonb),
    ($l10_t7_title$Слова$l10_t7_title$, $l10_t7_statement$**Коротко:** Найдите повторяющиеся слова.

### Условие

На вход подаётся строка слов. Выведи слова, которые встретились больше одного раза, в порядке первого появления.

### Вход

Одна строка.

### Выход

Повторяющиеся слова построчно.

### Пример 1

Ввод:

```text
кот пёс кот лис пёс
```

Вывод:

```text
кот
пёс
```

### Шаблон

```python
words = input().split()
```

### Подсказки

1. Сначала посчитай частоты.

2. Потом снова пройди по словам и выводи ещё не выведенные повторы.$l10_t7_statement$, $l10_t7_starter$words = input().split()
$l10_t7_starter$, $l10_t7_solution$words = input().split()
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
printed = set()
for word in words:
    if counts[word] > 1 and word not in printed:
        print(word)
        printed.add(word)
$l10_t7_solution$, 3, 75, $l10_t7_topic$Python M1 — Множества$l10_t7_topic$, 'python', $l10_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l10_t7_policy$::jsonb),
    ($l10_t8_title$Оценки$l10_t8_title$, $l10_t8_statement$**Коротко:** Посчитайте оценки 1–5.

### Условие

На вход подаётся строка оценок через пробел. Выведи количество оценок 1, 2, 3, 4, 5 в фиксированном порядке.

### Вход

Строка оценок.

### Выход

Пять строк `оценка: количество`.

### Пример 1

Ввод:

```text
5 4 5 3
```

Вывод:

```text
1: 0
2: 0
3: 1
4: 1
5: 2
```

### Шаблон

```python
grades = input().split()
```

### Подсказки

1. Создай словарь с ключами `1`–`5`.

2. Выводи в порядке от 1 до 5.$l10_t8_statement$, $l10_t8_starter$grades = input().split()
$l10_t8_starter$, $l10_t8_solution$grades = input().split()
counts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
for grade in grades:
    counts[grade] = counts[grade] + 1
for grade in ["1", "2", "3", "4", "5"]:
    print(grade + ":", counts[grade])
$l10_t8_solution$, 3, 75, $l10_t8_topic$Python M1 — Множества$l10_t8_topic$, 'python', $l10_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l10_t8_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 10
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l10_t2_delete_title$Уникальные$l10_t2_delete_title$,
        $l10_t4_delete_title$Проверка$l10_t4_delete_title$,
        $l10_t6_delete_title$Буквы$l10_t6_delete_title$,
        $l10_t7_delete_title$Слова$l10_t7_delete_title$,
        $l10_t8_delete_title$Оценки$l10_t8_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 10
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l10_test_2_1_title$Уникальные$l10_test_2_1_title$, $l10_test_2_1_input$кот пёс кот$l10_test_2_1_input$, $l10_test_2_1_expected$2$l10_test_2_1_expected$, FALSE, 1),
    ($l10_test_2_2_title$Уникальные$l10_test_2_2_title$, $l10_test_2_2_input$a b c$l10_test_2_2_input$, $l10_test_2_2_expected$3$l10_test_2_2_expected$, TRUE, 2),
    ($l10_test_2_3_title$Уникальные$l10_test_2_3_title$, $l10_test_2_3_input$a a a$l10_test_2_3_input$, $l10_test_2_3_expected$1$l10_test_2_3_expected$, TRUE, 3),
    ($l10_test_4_1_title$Проверка$l10_test_4_1_title$, $l10_test_4_1_input$кот пёс
кот$l10_test_4_1_input$, $l10_test_4_1_expected$Есть$l10_test_4_1_expected$, FALSE, 1),
    ($l10_test_4_2_title$Проверка$l10_test_4_2_title$, $l10_test_4_2_input$кот пёс
лось$l10_test_4_2_input$, $l10_test_4_2_expected$Нет$l10_test_4_2_expected$, TRUE, 2),
    ($l10_test_6_1_title$Буквы$l10_test_6_1_title$, $l10_test_6_1_input$abac$l10_test_6_1_input$, $l10_test_6_1_expected$a: 2
b: 1
c: 1$l10_test_6_1_expected$, FALSE, 1),
    ($l10_test_6_2_title$Буквы$l10_test_6_2_title$, $l10_test_6_2_input$zzz$l10_test_6_2_input$, $l10_test_6_2_expected$a: 0
b: 0
c: 0$l10_test_6_2_expected$, TRUE, 2),
    ($l10_test_7_1_title$Слова$l10_test_7_1_title$, $l10_test_7_1_input$кот пёс кот лис пёс$l10_test_7_1_input$, $l10_test_7_1_expected$кот
пёс$l10_test_7_1_expected$, FALSE, 1),
    ($l10_test_7_2_title$Слова$l10_test_7_2_title$, $l10_test_7_2_input$a b c$l10_test_7_2_input$, $l10_test_7_2_expected$$l10_test_7_2_expected$, TRUE, 2),
    ($l10_test_8_1_title$Оценки$l10_test_8_1_title$, $l10_test_8_1_input$5 4 5 3$l10_test_8_1_input$, $l10_test_8_1_expected$1: 0
2: 0
3: 1
4: 1
5: 2$l10_test_8_1_expected$, FALSE, 1),
    ($l10_test_8_2_title$Оценки$l10_test_8_2_title$, $l10_test_8_2_input$1 1 2$l10_test_8_2_input$, $l10_test_8_2_expected$1: 2
2: 1
3: 0
4: 0
5: 0$l10_test_8_2_expected$, TRUE, 2)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 10
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l10_b1_title$set$l10_b1_title$, $l10_b1_content$Множество хранит только уникальные значения.

```python
items = set(["a", "b", "a"])
print(len(items))  # 2
```$l10_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l10_b2_title$Уникальные$l10_b2_title$, $l10_b2_content$**Коротко:** Посчитайте уникальные слова.

### Условие

На вход подаётся строка слов через пробел. Выведи количество уникальных слов.

### Вход

Одна строка.

### Выход

Одно число.

### Пример 1

Ввод:

```text
кот пёс кот
```

Вывод:

```text
2
```

### Пример 2

Ввод:

```text
a b c
```

Вывод:

```text
3
```

### Шаблон

```python
words = input().split()
```

### Подсказки

1. Создай `set(words)`.

2. Количество: `len(...)`.$l10_b2_content$, $l10_b2_task$Уникальные$l10_b2_task$, NULL::jsonb),
    (3, 'theory', $l10_b3_title$in$l10_b3_title$, $l10_b3_content$Оператор `in` проверяет наличие элемента.

```python
if word in words_set:
    print("Есть")
```$l10_b3_content$, NULL, NULL::jsonb),
    (4, 'practice', $l10_b4_title$Проверка$l10_b4_title$, $l10_b4_content$**Коротко:** Проверьте слово в списке.

### Условие

Первая строка — набор слов. Вторая строка — слово для поиска. Если слово есть, выведи `Есть`, иначе `Нет`.

### Вход

Строка слов и слово.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
кот пёс
кот
```

Вывод:

```text
Есть
```

### Пример 2

Ввод:

```text
кот пёс
лось
```

Вывод:

```text
Нет
```

### Шаблон

```python
words = set(input().split())
word = input()
```

### Подсказки

1. Используй `word in words`.

2. Множество ускоряет поиск.$l10_b4_content$, $l10_b4_task$Проверка$l10_b4_task$, NULL::jsonb),
    (5, 'theory', $l10_b5_title$Частоты$l10_b5_title$, $l10_b5_content$Частотный словарь считает, сколько раз встретилось значение.

```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
```$l10_b5_content$, NULL, NULL::jsonb),
    (6, 'practice', $l10_b6_title$Буквы$l10_b6_title$, $l10_b6_content$**Коротко:** Посчитайте частоту буквы.

### Условие

На вход подаётся строка. Выведи, сколько раз встречается каждая буква `a`, `b`, `c` в фиксированном порядке.

### Вход

Одна строка.

### Выход

Три строки: `a:`, `b:`, `c:`.

### Пример 1

Ввод:

```text
abac
```

Вывод:

```text
a: 2
b: 1
c: 1
```

### Шаблон

```python
text = input()
```

### Подсказки

1. Создай словарь счётчиков.

2. Выводи буквы в порядке `a`, `b`, `c`.$l10_b6_content$, $l10_b6_task$Буквы$l10_b6_task$, NULL::jsonb),
    (7, 'practice', $l10_b7_title$Слова$l10_b7_title$, $l10_b7_content$**Коротко:** Найдите повторяющиеся слова.

### Условие

На вход подаётся строка слов. Выведи слова, которые встретились больше одного раза, в порядке первого появления.

### Вход

Одна строка.

### Выход

Повторяющиеся слова построчно.

### Пример 1

Ввод:

```text
кот пёс кот лис пёс
```

Вывод:

```text
кот
пёс
```

### Шаблон

```python
words = input().split()
```

### Подсказки

1. Сначала посчитай частоты.

2. Потом снова пройди по словам и выводи ещё не выведенные повторы.$l10_b7_content$, $l10_b7_task$Слова$l10_b7_task$, NULL::jsonb),
    (8, 'practice', $l10_b8_title$Оценки$l10_b8_title$, $l10_b8_content$**Коротко:** Посчитайте оценки 1–5.

### Условие

На вход подаётся строка оценок через пробел. Выведи количество оценок 1, 2, 3, 4, 5 в фиксированном порядке.

### Вход

Строка оценок.

### Выход

Пять строк `оценка: количество`.

### Пример 1

Ввод:

```text
5 4 5 3
```

Вывод:

```text
1: 0
2: 0
3: 1
4: 1
5: 2
```

### Шаблон

```python
grades = input().split()
```

### Подсказки

1. Создай словарь с ключами `1`–`5`.

2. Выводи в порядке от 1 до 5.$l10_b8_content$, $l10_b8_task$Оценки$l10_b8_task$, NULL::jsonb),
    (9, 'quiz', $l10_b9_title$Итог$l10_b9_title$, $l10_b9_content$### Вопрос

Что хранит `set`?

### Варианты

1. Только уникальные значения

2. Пары ключ-значение

3. Только числа

4. Только строки$l10_b9_content$, NULL, $l10_b9_quiz${"question":"Что хранит `set`?","options":[{"id":"A","text":"Только уникальные значения"},{"id":"B","text":"Пары ключ-значение"},{"id":"C","text":"Только числа"},{"id":"D","text":"Только строки"}],"correctOptionId":"A","explanation":"Множество удаляет повторяющиеся значения."}$l10_b9_quiz$::jsonb)
), resolved AS (
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

-- Lesson 11: Урок 11. Функции
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 11
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l11_t2_title$Привет$l11_t2_title$, $l11_t2_statement$**Коротко:** Создайте и вызовите функцию.

### Условие

Напиши функцию `say_hello()`, которая выводит `Привет`. Затем вызови её.

### Вход

Нет.

### Выход

Одна строка.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Привет
```

### Шаблон

```python
def say_hello():
    # код функции

# вызов
```

### Подсказки

1. Код внутри функции должен быть с отступом.

2. После определения функции вызови `say_hello()`.$l11_t2_statement$, $l11_t2_starter$def say_hello():
    # код функции

# вызов
$l11_t2_starter$, $l11_t2_solution$def say_hello():
    print("Привет")

say_hello()
$l11_t2_solution$, 1, 45, $l11_t2_topic$Python M1 — Функции$l11_t2_topic$, 'python', $l11_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l11_t2_policy$::jsonb),
    ($l11_t4_title$Сумма$l11_t4_title$, $l11_t4_statement$**Коротко:** Верните сумму двух чисел.

### Условие

Напиши функцию `add(a, b)`, которая возвращает сумму. Считай два числа, вызови функцию и выведи результат.

### Вход

Два целых числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
2
3
```

Вывод:

```text
5
```

### Пример 2

Ввод:

```text
10
-5
```

Вывод:

```text
5
```

### Шаблон

```python
def add(a, b):
    # return ...

a = int(input())
b = int(input())
```

### Подсказки

1. Внутри функции нужен `return`.

2. Вывод делай после вызова функции.$l11_t4_statement$, $l11_t4_starter$def add(a, b):
    # return ...

a = int(input())
b = int(input())
$l11_t4_starter$, $l11_t4_solution$def add(a, b):
    return a + b

a = int(input())
b = int(input())
print(add(a, b))
$l11_t4_solution$, 2, 60, $l11_t4_topic$Python M1 — Функции$l11_t4_topic$, 'python', $l11_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l11_t4_policy$::jsonb),
    ($l11_t6_title$Площадь$l11_t6_title$, $l11_t6_statement$**Коротко:** Функция для площади.

### Условие

Напиши функцию `area(width, height)`, которая возвращает площадь прямоугольника. Считай ширину и высоту, выведи результат.

### Вход

Два целых числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5
8
```

Вывод:

```text
40
```

### Шаблон

```python
def area(width, height):
    # return ...
```

### Подсказки

1. Площадь: `width * height`.

2. Функция должна вернуть значение, а не печатать внутри.$l11_t6_statement$, $l11_t6_starter$def area(width, height):
    # return ...
$l11_t6_starter$, $l11_t6_solution$def area(width, height):
    return width * height

width = int(input())
height = int(input())
print(area(width, height))
$l11_t6_solution$, 2, 60, $l11_t6_topic$Python M1 — Функции$l11_t6_topic$, 'python', $l11_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l11_t6_policy$::jsonb),
    ($l11_t8_title$Ошибка return$l11_t8_title$, $l11_t8_statement$**Коротко:** Замените print на return.

### Код с ошибкой

```python
def double(x):
    print(x * 2)

number = int(input())
result = double(number) + 1
print(result)
```

### Что нужно сделать

Код должен вывести число, умноженное на 2, плюс 1. Сейчас функция ничего не возвращает. Исправь функцию.

### Вход

Одно целое число.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5
```

Вывод:

```text
11
```

### Подсказки

1. `print()` не возвращает значение.

2. В функции нужен `return x * 2`.$l11_t8_statement$, $l11_t8_starter$def double(x):
    print(x * 2)

number = int(input())
result = double(number) + 1
print(result)
$l11_t8_starter$, $l11_t8_solution$def double(x):
    return x * 2

number = int(input())
result = double(number) + 1
print(result)
$l11_t8_solution$, 2, 45, $l11_t8_topic$Python M1 — Функции$l11_t8_topic$, 'python', $l11_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l11_t8_policy$::jsonb),
    ($l11_t9_title$Валидатор$l11_t9_title$, $l11_t9_statement$**Коротко:** Проверьте длину пароля.

### Условие

Напиши функцию `is_valid(password)`, которая возвращает `True`, если длина пароля 8 или больше. Считай пароль и выведи `OK` или `NO`.

### Вход

Одна строка.

### Выход

`OK` или `NO`.

### Пример 1

Ввод:

```text
12345678
```

Вывод:

```text
OK
```

### Пример 2

Ввод:

```text
123
```

Вывод:

```text
NO
```

### Шаблон

```python
def is_valid(password):
    # return ...

password = input()
```

### Подсказки

1. Длина: `len(password)`.

2. Функция возвращает логическое значение.$l11_t9_statement$, $l11_t9_starter$def is_valid(password):
    # return ...

password = input()
$l11_t9_starter$, $l11_t9_solution$def is_valid(password):
    return len(password) >= 8

password = input()
if is_valid(password):
    print("OK")
else:
    print("NO")
$l11_t9_solution$, 2, 65, $l11_t9_topic$Python M1 — Функции$l11_t9_topic$, 'python', $l11_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l11_t9_policy$::jsonb),
    ($l11_t10_title$Калькулятор$l11_t10_title$, $l11_t10_statement$**Коротко:** Разбейте калькулятор на функции.

### Условие

На вход подаются два числа и операция: `+`, `-`, `*`. Напиши функции `add`, `subtract`, `multiply` и выведи результат выбранной операции.

### Вход

Два числа и операция.

### Выход

Одно число.

### Пример 1

Ввод:

```text
2
3
+
```

Вывод:

```text
5
```

### Пример 2

Ввод:

```text
10
4
-
```

Вывод:

```text
6
```

### Пример 3

Ввод:

```text
3
5
*
```

Вывод:

```text
15
```

### Шаблон

```python
def add(a, b):
    pass

def subtract(a, b):
    pass

def multiply(a, b):
    pass
```

### Подсказки

1. Каждая функция должна делать одну операцию.

2. После ввода операции выбери нужную функцию через `if`.$l11_t10_statement$, $l11_t10_starter$def add(a, b):
    pass

def subtract(a, b):
    pass

def multiply(a, b):
    pass
$l11_t10_starter$, $l11_t10_solution$def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

a = int(input())
b = int(input())
op = input()

if op == "+":
    print(add(a, b))
elif op == "-":
    print(subtract(a, b))
elif op == "*":
    print(multiply(a, b))
$l11_t10_solution$, 3, 80, $l11_t10_topic$Python M1 — Функции$l11_t10_topic$, 'python', $l11_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l11_t10_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 11
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l11_t2_delete_title$Привет$l11_t2_delete_title$,
        $l11_t4_delete_title$Сумма$l11_t4_delete_title$,
        $l11_t6_delete_title$Площадь$l11_t6_delete_title$,
        $l11_t8_delete_title$Ошибка return$l11_t8_delete_title$,
        $l11_t9_delete_title$Валидатор$l11_t9_delete_title$,
        $l11_t10_delete_title$Калькулятор$l11_t10_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 11
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l11_test_2_1_title$Привет$l11_test_2_1_title$, $l11_test_2_1_input$$l11_test_2_1_input$, $l11_test_2_1_expected$Привет$l11_test_2_1_expected$, FALSE, 1),
    ($l11_test_4_1_title$Сумма$l11_test_4_1_title$, $l11_test_4_1_input$2
3$l11_test_4_1_input$, $l11_test_4_1_expected$5$l11_test_4_1_expected$, FALSE, 1),
    ($l11_test_4_2_title$Сумма$l11_test_4_2_title$, $l11_test_4_2_input$10
-5$l11_test_4_2_input$, $l11_test_4_2_expected$5$l11_test_4_2_expected$, TRUE, 2),
    ($l11_test_4_3_title$Сумма$l11_test_4_3_title$, $l11_test_4_3_input$0
0$l11_test_4_3_input$, $l11_test_4_3_expected$0$l11_test_4_3_expected$, TRUE, 3),
    ($l11_test_6_1_title$Площадь$l11_test_6_1_title$, $l11_test_6_1_input$5
8$l11_test_6_1_input$, $l11_test_6_1_expected$40$l11_test_6_1_expected$, FALSE, 1),
    ($l11_test_6_2_title$Площадь$l11_test_6_2_title$, $l11_test_6_2_input$1
1$l11_test_6_2_input$, $l11_test_6_2_expected$1$l11_test_6_2_expected$, TRUE, 2),
    ($l11_test_8_1_title$Ошибка return$l11_test_8_1_title$, $l11_test_8_1_input$5$l11_test_8_1_input$, $l11_test_8_1_expected$11$l11_test_8_1_expected$, FALSE, 1),
    ($l11_test_8_2_title$Ошибка return$l11_test_8_2_title$, $l11_test_8_2_input$0$l11_test_8_2_input$, $l11_test_8_2_expected$1$l11_test_8_2_expected$, TRUE, 2),
    ($l11_test_9_1_title$Валидатор$l11_test_9_1_title$, $l11_test_9_1_input$12345678$l11_test_9_1_input$, $l11_test_9_1_expected$OK$l11_test_9_1_expected$, FALSE, 1),
    ($l11_test_9_2_title$Валидатор$l11_test_9_2_title$, $l11_test_9_2_input$123$l11_test_9_2_input$, $l11_test_9_2_expected$NO$l11_test_9_2_expected$, TRUE, 2),
    ($l11_test_9_3_title$Валидатор$l11_test_9_3_title$, $l11_test_9_3_input$abcdefgh$l11_test_9_3_input$, $l11_test_9_3_expected$OK$l11_test_9_3_expected$, TRUE, 3),
    ($l11_test_10_1_title$Калькулятор$l11_test_10_1_title$, $l11_test_10_1_input$2
3
+$l11_test_10_1_input$, $l11_test_10_1_expected$5$l11_test_10_1_expected$, FALSE, 1),
    ($l11_test_10_2_title$Калькулятор$l11_test_10_2_title$, $l11_test_10_2_input$10
4
-$l11_test_10_2_input$, $l11_test_10_2_expected$6$l11_test_10_2_expected$, TRUE, 2),
    ($l11_test_10_3_title$Калькулятор$l11_test_10_3_title$, $l11_test_10_3_input$3
5
*$l11_test_10_3_input$, $l11_test_10_3_expected$15$l11_test_10_3_expected$, TRUE, 3)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 11
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l11_b1_title$def$l11_b1_title$, $l11_b1_content$Функция — это именованный блок кода.

```python
def say_hello():
    print("Привет")

say_hello()
```

Функцию нужно не только создать, но и вызвать.$l11_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l11_b2_title$Привет$l11_b2_title$, $l11_b2_content$**Коротко:** Создайте и вызовите функцию.

### Условие

Напиши функцию `say_hello()`, которая выводит `Привет`. Затем вызови её.

### Вход

Нет.

### Выход

Одна строка.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Привет
```

### Шаблон

```python
def say_hello():
    # код функции

# вызов
```

### Подсказки

1. Код внутри функции должен быть с отступом.

2. После определения функции вызови `say_hello()`.$l11_b2_content$, $l11_b2_task$Привет$l11_b2_task$, NULL::jsonb),
    (3, 'theory', $l11_b3_title$Параметры$l11_b3_title$, $l11_b3_content$Функция может принимать параметры.

```python
def greet(name):
    print("Привет,", name)

greet("Анна")
```$l11_b3_content$, NULL, NULL::jsonb),
    (4, 'practice', $l11_b4_title$Сумма$l11_b4_title$, $l11_b4_content$**Коротко:** Верните сумму двух чисел.

### Условие

Напиши функцию `add(a, b)`, которая возвращает сумму. Считай два числа, вызови функцию и выведи результат.

### Вход

Два целых числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
2
3
```

Вывод:

```text
5
```

### Пример 2

Ввод:

```text
10
-5
```

Вывод:

```text
5
```

### Шаблон

```python
def add(a, b):
    # return ...

a = int(input())
b = int(input())
```

### Подсказки

1. Внутри функции нужен `return`.

2. Вывод делай после вызова функции.$l11_b4_content$, $l11_b4_task$Сумма$l11_b4_task$, NULL::jsonb),
    (5, 'theory', $l11_b5_title$return$l11_b5_title$, $l11_b5_content$`return` возвращает результат функции.

```python
def square(x):
    return x * x

result = square(5)
print(result)
```

`print()` только выводит. `return` отдаёт значение дальше в код.$l11_b5_content$, NULL, NULL::jsonb),
    (6, 'practice', $l11_b6_title$Площадь$l11_b6_title$, $l11_b6_content$**Коротко:** Функция для площади.

### Условие

Напиши функцию `area(width, height)`, которая возвращает площадь прямоугольника. Считай ширину и высоту, выведи результат.

### Вход

Два целых числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5
8
```

Вывод:

```text
40
```

### Шаблон

```python
def area(width, height):
    # return ...
```

### Подсказки

1. Площадь: `width * height`.

2. Функция должна вернуть значение, а не печатать внутри.$l11_b6_content$, $l11_b6_task$Площадь$l11_b6_task$, NULL::jsonb),
    (7, 'theory', $l11_b7_title$print vs return$l11_b7_title$, $l11_b7_content$Сравни:

```python
def add(a, b):
    print(a + b)
```

и:

```python
def add(a, b):
    return a + b
```

Если результат нужно использовать дальше, нужен `return`.$l11_b7_content$, NULL, NULL::jsonb),
    (8, 'practice', $l11_b8_title$Ошибка return$l11_b8_title$, $l11_b8_content$**Коротко:** Замените print на return.

### Код с ошибкой

```python
def double(x):
    print(x * 2)

number = int(input())
result = double(number) + 1
print(result)
```

### Что нужно сделать

Код должен вывести число, умноженное на 2, плюс 1. Сейчас функция ничего не возвращает. Исправь функцию.

### Вход

Одно целое число.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5
```

Вывод:

```text
11
```

### Подсказки

1. `print()` не возвращает значение.

2. В функции нужен `return x * 2`.$l11_b8_content$, $l11_b8_task$Ошибка return$l11_b8_task$, NULL::jsonb),
    (9, 'practice', $l11_b9_title$Валидатор$l11_b9_title$, $l11_b9_content$**Коротко:** Проверьте длину пароля.

### Условие

Напиши функцию `is_valid(password)`, которая возвращает `True`, если длина пароля 8 или больше. Считай пароль и выведи `OK` или `NO`.

### Вход

Одна строка.

### Выход

`OK` или `NO`.

### Пример 1

Ввод:

```text
12345678
```

Вывод:

```text
OK
```

### Пример 2

Ввод:

```text
123
```

Вывод:

```text
NO
```

### Шаблон

```python
def is_valid(password):
    # return ...

password = input()
```

### Подсказки

1. Длина: `len(password)`.

2. Функция возвращает логическое значение.$l11_b9_content$, $l11_b9_task$Валидатор$l11_b9_task$, NULL::jsonb),
    (10, 'practice', $l11_b10_title$Калькулятор$l11_b10_title$, $l11_b10_content$**Коротко:** Разбейте калькулятор на функции.

### Условие

На вход подаются два числа и операция: `+`, `-`, `*`. Напиши функции `add`, `subtract`, `multiply` и выведи результат выбранной операции.

### Вход

Два числа и операция.

### Выход

Одно число.

### Пример 1

Ввод:

```text
2
3
+
```

Вывод:

```text
5
```

### Пример 2

Ввод:

```text
10
4
-
```

Вывод:

```text
6
```

### Пример 3

Ввод:

```text
3
5
*
```

Вывод:

```text
15
```

### Шаблон

```python
def add(a, b):
    pass

def subtract(a, b):
    pass

def multiply(a, b):
    pass
```

### Подсказки

1. Каждая функция должна делать одну операцию.

2. После ввода операции выбери нужную функцию через `if`.$l11_b10_content$, $l11_b10_task$Калькулятор$l11_b10_task$, NULL::jsonb),
    (11, 'quiz', $l11_b11_title$Итог$l11_b11_title$, $l11_b11_content$### Вопрос

Что делает `return`?

### Варианты

1. Печатает текст

2. Возвращает результат функции

3. Создаёт цикл

4. Считывает ввод$l11_b11_content$, NULL, $l11_b11_quiz${"question":"Что делает `return`?","options":[{"id":"A","text":"Печатает текст"},{"id":"B","text":"Возвращает результат функции"},{"id":"C","text":"Создаёт цикл"},{"id":"D","text":"Считывает ввод"}],"correctOptionId":"B","explanation":"`return` отдаёт результат из функции в остальной код."}$l11_b11_quiz$::jsonb)
), resolved AS (
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

-- Lesson 12: Урок 12. Проект
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 12
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l12_t3_title$Добавить$l12_t3_title$, $l12_t3_statement$**Коротко:** Реализуйте добавление задачи.

### Условие

На вход подаётся название задачи. Добавь задачу в список и выведи `Добавлено`.

### Вход

Одна строка — название.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
Купить хлеб
```

Вывод:

```text
Добавлено
```

### Шаблон

```python
tasks = []
title = input()
```

### Подсказки

1. Задача — словарь с ключами `title` и `done`.

2. Добавь словарь через `append`.$l12_t3_statement$, $l12_t3_starter$tasks = []
title = input()
$l12_t3_starter$, $l12_t3_solution$tasks = []
title = input()
tasks.append({"title": title, "done": False})
print("Добавлено")
$l12_t3_solution$, 1, 40, $l12_t3_topic$Python M1 — Проект$l12_t3_topic$, 'python', $l12_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l12_t3_policy$::jsonb),
    ($l12_t4_title$Показать$l12_t4_title$, $l12_t4_statement$**Коротко:** Выведите список задач.

### Условие

Дан список задач в коде. Выведи их с номерами. Невыполненная задача помечается `[ ]`, выполненная — `[x]`.

### Вход

Нет.

### Выход

Задачи с номерами.

### Пример 1

Ввод:

```text

```

Вывод:

```text
1. [ ] Купить хлеб
2. [x] Сделать урок
```

### Шаблон

```python
tasks = [{"title": "Купить хлеб", "done": False}, {"title": "Сделать урок", "done": True}]
```

### Подсказки

1. Номер можно получить через `range(len(tasks))`.

2. Статус зависит от `done`.$l12_t4_statement$, $l12_t4_starter$tasks = [{"title": "Купить хлеб", "done": False}, {"title": "Сделать урок", "done": True}]
$l12_t4_starter$, $l12_t4_solution$tasks = [{"title": "Купить хлеб", "done": False}, {"title": "Сделать урок", "done": True}]
for i in range(len(tasks)):
    task = tasks[i]
    mark = "[x]" if task["done"] else "[ ]"
    print(str(i + 1) + ".", mark, task["title"])
$l12_t4_solution$, 2, 55, $l12_t4_topic$Python M1 — Проект$l12_t4_topic$, 'python', $l12_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l12_t4_policy$::jsonb),
    ($l12_t5_title$Выполнить$l12_t5_title$, $l12_t5_statement$**Коротко:** Отметьте задачу выполненной.

### Условие

Дан список из двух задач. На вход подаётся номер. Отметь задачу выполненной и выведи `Готово`.

### Вход

Одно число — номер задачи.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
1
```

Вывод:

```text
Готово
```

### Шаблон

```python
tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
```

### Подсказки

1. Номер в интерфейсе начинается с 1.

2. Индекс в списке: `number - 1`.$l12_t5_statement$, $l12_t5_starter$tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
$l12_t5_starter$, $l12_t5_solution$tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
tasks[number - 1]["done"] = True
print("Готово")
$l12_t5_solution$, 2, 55, $l12_t5_topic$Python M1 — Проект$l12_t5_topic$, 'python', $l12_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l12_t5_policy$::jsonb),
    ($l12_t6_title$Удалить$l12_t6_title$, $l12_t6_statement$**Коротко:** Удалите задачу по номеру.

### Условие

Дан список из двух задач. На вход подаётся номер. Удали задачу и выведи количество оставшихся задач.

### Вход

Одно число — номер задачи.

### Выход

Одно число.

### Пример 1

Ввод:

```text
1
```

Вывод:

```text
1
```

### Шаблон

```python
tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
```

### Подсказки

1. Индекс: `number - 1`.

2. Удалить можно через `del tasks[index]`.$l12_t6_statement$, $l12_t6_starter$tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
$l12_t6_starter$, $l12_t6_solution$tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
del tasks[number - 1]
print(len(tasks))
$l12_t6_solution$, 2, 55, $l12_t6_topic$Python M1 — Проект$l12_t6_topic$, 'python', $l12_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l12_t6_policy$::jsonb),
    ($l12_t7_title$Ошибки$l12_t7_title$, $l12_t7_statement$**Коротко:** Проверьте неверный номер.

### Условие

Дан список из двух задач. На вход подаётся номер. Если номера нет, выведи `Нет такой задачи`, иначе `OK`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
3
```

Вывод:

```text
Нет такой задачи
```

### Пример 2

Ввод:

```text
2
```

Вывод:

```text
OK
```

### Шаблон

```python
tasks = [{"title": "A"}, {"title": "B"}]
number = int(input())
```

### Подсказки

1. Допустимые номера: от 1 до `len(tasks)`.

2. Используй условие с `and`.$l12_t7_statement$, $l12_t7_starter$tasks = [{"title": "A"}, {"title": "B"}]
number = int(input())
$l12_t7_starter$, $l12_t7_solution$tasks = [{"title": "A"}, {"title": "B"}]
number = int(input())
if number >= 1 and number <= len(tasks):
    print("OK")
else:
    print("Нет такой задачи")
$l12_t7_solution$, 2, 55, $l12_t7_topic$Python M1 — Проект$l12_t7_topic$, 'python', $l12_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l12_t7_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 12
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l12_t3_delete_title$Добавить$l12_t3_delete_title$,
        $l12_t4_delete_title$Показать$l12_t4_delete_title$,
        $l12_t5_delete_title$Выполнить$l12_t5_delete_title$,
        $l12_t6_delete_title$Удалить$l12_t6_delete_title$,
        $l12_t7_delete_title$Ошибки$l12_t7_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 12
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l12_test_3_1_title$Добавить$l12_test_3_1_title$, $l12_test_3_1_input$Купить хлеб$l12_test_3_1_input$, $l12_test_3_1_expected$Добавлено$l12_test_3_1_expected$, FALSE, 1),
    ($l12_test_4_1_title$Показать$l12_test_4_1_title$, $l12_test_4_1_input$$l12_test_4_1_input$, $l12_test_4_1_expected$1. [ ] Купить хлеб
2. [x] Сделать урок$l12_test_4_1_expected$, FALSE, 1),
    ($l12_test_5_1_title$Выполнить$l12_test_5_1_title$, $l12_test_5_1_input$1$l12_test_5_1_input$, $l12_test_5_1_expected$Готово$l12_test_5_1_expected$, FALSE, 1),
    ($l12_test_5_2_title$Выполнить$l12_test_5_2_title$, $l12_test_5_2_input$2$l12_test_5_2_input$, $l12_test_5_2_expected$Готово$l12_test_5_2_expected$, TRUE, 2),
    ($l12_test_6_1_title$Удалить$l12_test_6_1_title$, $l12_test_6_1_input$1$l12_test_6_1_input$, $l12_test_6_1_expected$1$l12_test_6_1_expected$, FALSE, 1),
    ($l12_test_6_2_title$Удалить$l12_test_6_2_title$, $l12_test_6_2_input$2$l12_test_6_2_input$, $l12_test_6_2_expected$1$l12_test_6_2_expected$, TRUE, 2),
    ($l12_test_7_1_title$Ошибки$l12_test_7_1_title$, $l12_test_7_1_input$3$l12_test_7_1_input$, $l12_test_7_1_expected$Нет такой задачи$l12_test_7_1_expected$, FALSE, 1),
    ($l12_test_7_2_title$Ошибки$l12_test_7_2_title$, $l12_test_7_2_input$2$l12_test_7_2_input$, $l12_test_7_2_expected$OK$l12_test_7_2_expected$, TRUE, 2),
    ($l12_test_7_3_title$Ошибки$l12_test_7_3_title$, $l12_test_7_3_input$0$l12_test_7_3_input$, $l12_test_7_3_expected$Нет такой задачи$l12_test_7_3_expected$, TRUE, 3)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 12
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l12_b1_title$Задача проекта$l12_b1_title$, $l12_b1_content$Итоговый проект модуля — консольный трекер задач.

Программа должна хранить задачи в списке словарей:
```python
tasks = []
```

Каждая задача:
```python
{"title": "Купить хлеб", "done": False}
```$l12_b1_content$, NULL, NULL::jsonb),
    (2, 'theory', $l12_b2_title$Команды$l12_b2_title$, $l12_b2_content$Программа принимает команды:

| Команда | Действие |
|---|---|
| `add` | добавить задачу |
| `list` | показать задачи |
| `done` | отметить выполненной |
| `delete` | удалить задачу |
| `exit` | завершить программу |

После неизвестной команды вывести `Неизвестная команда`.$l12_b2_content$, NULL, NULL::jsonb),
    (3, 'practice', $l12_b3_title$Добавить$l12_b3_title$, $l12_b3_content$**Коротко:** Реализуйте добавление задачи.

### Условие

На вход подаётся название задачи. Добавь задачу в список и выведи `Добавлено`.

### Вход

Одна строка — название.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
Купить хлеб
```

Вывод:

```text
Добавлено
```

### Шаблон

```python
tasks = []
title = input()
```

### Подсказки

1. Задача — словарь с ключами `title` и `done`.

2. Добавь словарь через `append`.$l12_b3_content$, $l12_b3_task$Добавить$l12_b3_task$, NULL::jsonb),
    (4, 'practice', $l12_b4_title$Показать$l12_b4_title$, $l12_b4_content$**Коротко:** Выведите список задач.

### Условие

Дан список задач в коде. Выведи их с номерами. Невыполненная задача помечается `[ ]`, выполненная — `[x]`.

### Вход

Нет.

### Выход

Задачи с номерами.

### Пример 1

Ввод:

```text

```

Вывод:

```text
1. [ ] Купить хлеб
2. [x] Сделать урок
```

### Шаблон

```python
tasks = [{"title": "Купить хлеб", "done": False}, {"title": "Сделать урок", "done": True}]
```

### Подсказки

1. Номер можно получить через `range(len(tasks))`.

2. Статус зависит от `done`.$l12_b4_content$, $l12_b4_task$Показать$l12_b4_task$, NULL::jsonb),
    (5, 'practice', $l12_b5_title$Выполнить$l12_b5_title$, $l12_b5_content$**Коротко:** Отметьте задачу выполненной.

### Условие

Дан список из двух задач. На вход подаётся номер. Отметь задачу выполненной и выведи `Готово`.

### Вход

Одно число — номер задачи.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
1
```

Вывод:

```text
Готово
```

### Шаблон

```python
tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
```

### Подсказки

1. Номер в интерфейсе начинается с 1.

2. Индекс в списке: `number - 1`.$l12_b5_content$, $l12_b5_task$Выполнить$l12_b5_task$, NULL::jsonb),
    (6, 'practice', $l12_b6_title$Удалить$l12_b6_title$, $l12_b6_content$**Коротко:** Удалите задачу по номеру.

### Условие

Дан список из двух задач. На вход подаётся номер. Удали задачу и выведи количество оставшихся задач.

### Вход

Одно число — номер задачи.

### Выход

Одно число.

### Пример 1

Ввод:

```text
1
```

Вывод:

```text
1
```

### Шаблон

```python
tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
```

### Подсказки

1. Индекс: `number - 1`.

2. Удалить можно через `del tasks[index]`.$l12_b6_content$, $l12_b6_task$Удалить$l12_b6_task$, NULL::jsonb),
    (7, 'practice', $l12_b7_title$Ошибки$l12_b7_title$, $l12_b7_content$**Коротко:** Проверьте неверный номер.

### Условие

Дан список из двух задач. На вход подаётся номер. Если номера нет, выведи `Нет такой задачи`, иначе `OK`.

### Вход

Одно целое число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
3
```

Вывод:

```text
Нет такой задачи
```

### Пример 2

Ввод:

```text
2
```

Вывод:

```text
OK
```

### Шаблон

```python
tasks = [{"title": "A"}, {"title": "B"}]
number = int(input())
```

### Подсказки

1. Допустимые номера: от 1 до `len(tasks)`.

2. Используй условие с `and`.$l12_b7_content$, $l12_b7_task$Ошибки$l12_b7_task$, NULL::jsonb),
    (8, 'theory', $l12_b8_title$Сборка$l12_b8_title$, $l12_b8_content$**Коротко:** соберите полноценный трекер задач.

### Требования

Программа должна работать в цикле и принимать команды:

```text
add
list
done
delete
exit
```

Поведение:

- `add`: следующая строка — название задачи. Добавить задачу и вывести `Добавлено`.
- `list`: вывести все задачи с номерами. Формат: `1. [ ] Название` или `1. [x] Название`.
- `done`: следующая строка — номер задачи. Отметить задачу выполненной или вывести `Нет такой задачи`.
- `delete`: следующая строка — номер задачи. Удалить задачу или вывести `Нет такой задачи`.
- `exit`: вывести `Пока` и завершить программу.
- неизвестная команда: вывести `Неизвестная команда`.

### Пример

Ввод:
```text
add
Купить хлеб
add
Сделать урок
list
done
1
list
exit
```

Вывод:
```text
Добавлено
Добавлено
1. [ ] Купить хлеб
2. [ ] Сделать урок
Готово
1. [x] Купить хлеб
2. [ ] Сделать урок
Пока
```

### Подсказки

1. Храни задачи в списке словарей.
2. Разбей код на функции: `add_task`, `list_tasks`, `mark_done`, `delete_task`.
3. Номера задач начинаются с 1, индексы списка — с 0.$l12_b8_content$, NULL, NULL::jsonb),
    (9, 'theory', $l12_b9_title$README$l12_b9_title$, $l12_b9_content$Для проекта нужен короткий README:

```text
Название проекта
Что делает программа
Какие команды поддерживает
Как запустить
Пример работы
```$l12_b9_content$, NULL, NULL::jsonb),
    (10, 'theory', $l12_b10_title$AI-проверка$l12_b10_title$, $l12_b10_content$Этот шаг запускает AI-проверку проекта и показывает ученику результат по критериям. Ученик видит только итоговые замечания и рекомендации, но не внутренний prompt.$l12_b10_content$, NULL, NULL::jsonb)
), resolved AS (
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

-- Lesson 13: Урок 13. Контроль
WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 13
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
    VALUES
    ($l13_t2_title$Ввод и вывод$l13_t2_title$, $l13_t2_statement$**Коротко:** Соберите строку профиля.

### Условие

На вход подаются имя и город. Выведи `Имя из города Город`.

### Вход

Две строки.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
Анна
Москва
```

Вывод:

```text
Анна из города Москва
```

### Шаблон

```python
name = input()
city = input()
```

### Подсказки

1. Выведи несколько значений через `print()`.

2. Следи за точным текстом.$l13_t2_statement$, $l13_t2_starter$name = input()
city = input()
$l13_t2_starter$, $l13_t2_solution$name = input()
city = input()
print(name, "из города", city)
$l13_t2_solution$, 1, 40, $l13_t2_topic$Python M1 — Контроль$l13_t2_topic$, 'python', $l13_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l13_t2_policy$::jsonb),
    ($l13_t3_title$Арифметика$l13_t3_title$, $l13_t3_statement$**Коротко:** Посчитайте оплату.

### Условие

На вход подаются цена, количество и скидка в рублях. Выведи `price * count - discount`.

### Вход

Три целых числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
100
3
50
```

Вывод:

```text
250
```

### Шаблон

```python
price = int(input())
count = int(input())
discount = int(input())
```

### Подсказки

1. Сначала умножение.

2. Потом вычитание скидки.$l13_t3_statement$, $l13_t3_starter$price = int(input())
count = int(input())
discount = int(input())
$l13_t3_starter$, $l13_t3_solution$price = int(input())
count = int(input())
discount = int(input())
print(price * count - discount)
$l13_t3_solution$, 1, 45, $l13_t3_topic$Python M1 — Контроль$l13_t3_topic$, 'python', $l13_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l13_t3_policy$::jsonb),
    ($l13_t4_title$Условия$l13_t4_title$, $l13_t4_statement$**Коротко:** Определите доступ.

### Условие

На вход подаётся возраст. До 18 — `Нет`, от 18 до 64 — `Да`, от 65 — `Льготный`.

### Вход

Одно число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
17
```

Вывод:

```text
Нет
```

### Пример 2

Ввод:

```text
18
```

Вывод:

```text
Да
```

### Пример 3

Ввод:

```text
65
```

Вывод:

```text
Льготный
```

### Шаблон

```python
age = int(input())
```

### Подсказки

1. Границы: 18 и 65.

2. Порядок проверок важен.$l13_t4_statement$, $l13_t4_starter$age = int(input())
$l13_t4_starter$, $l13_t4_solution$age = int(input())
if age < 18:
    print("Нет")
elif age < 65:
    print("Да")
else:
    print("Льготный")
$l13_t4_solution$, 2, 60, $l13_t4_topic$Python M1 — Контроль$l13_t4_topic$, 'python', $l13_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l13_t4_policy$::jsonb),
    ($l13_t5_title$Логика$l13_t5_title$, $l13_t5_statement$**Коротко:** Проверьте вход в систему.

### Условие

На вход подаются роль и статус блокировки (`yes` или `no`). Доступ есть для `admin` или `moderator`, если блокировки нет.

### Вход

Роль и блокировка.

### Выход

`Доступ` или `Нет доступа`.

### Пример 1

Ввод:

```text
admin
no
```

Вывод:

```text
Доступ
```

### Пример 2

Ввод:

```text
admin
yes
```

Вывод:

```text
Нет доступа
```

### Пример 3

Ввод:

```text
user
no
```

Вывод:

```text
Нет доступа
```

### Шаблон

```python
role = input()
blocked = input()
```

### Подсказки

1. Роль проверяй через `or`.

2. Блокировки нет: `blocked == "no"`.$l13_t5_statement$, $l13_t5_starter$role = input()
blocked = input()
$l13_t5_starter$, $l13_t5_solution$role = input()
blocked = input()
if (role == "admin" or role == "moderator") and blocked == "no":
    print("Доступ")
else:
    print("Нет доступа")
$l13_t5_solution$, 2, 65, $l13_t5_topic$Python M1 — Контроль$l13_t5_topic$, 'python', $l13_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l13_t5_policy$::jsonb),
    ($l13_t6_title$Циклы$l13_t6_title$, $l13_t6_statement$**Коротко:** Найдите сумму чётных.

### Условие

Сначала вводится `n`, затем `n` чисел. Выведи сумму чётных чисел.

### Вход

Количество и числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5
1
2
3
4
5
```

Вывод:

```text
6
```

### Шаблон

```python
n = int(input())
total = 0
```

### Подсказки

1. Чётность: `% 2 == 0`.

2. Суммируй только подходящие числа.$l13_t6_statement$, $l13_t6_starter$n = int(input())
total = 0
$l13_t6_starter$, $l13_t6_solution$n = int(input())
total = 0
for i in range(n):
    number = int(input())
    if number % 2 == 0:
        total = total + number
print(total)
$l13_t6_solution$, 2, 70, $l13_t6_topic$Python M1 — Контроль$l13_t6_topic$, 'python', $l13_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l13_t6_policy$::jsonb),
    ($l13_t7_title$Строки$l13_t7_title$, $l13_t7_statement$**Коротко:** Найдите короткое имя.

### Условие

На вход подаётся строка имён через пробел. Выведи первое имя длиной меньше 4 символов. Если такого нет, выведи `Не найдено`.

### Вход

Одна строка.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
Анна Ли Олег
```

Вывод:

```text
Ли
```

### Пример 2

Ввод:

```text
Анна Олег
```

Вывод:

```text
Не найдено
```

### Шаблон

```python
names = input().split()
```

### Подсказки

1. Нужен флаг `found`.

2. После первого найденного имени можно использовать `break`.$l13_t7_statement$, $l13_t7_starter$names = input().split()
$l13_t7_starter$, $l13_t7_solution$names = input().split()
found = False
for name in names:
    if len(name) < 4:
        print(name)
        found = True
        break
if not found:
    print("Не найдено")
$l13_t7_solution$, 3, 75, $l13_t7_topic$Python M1 — Контроль$l13_t7_topic$, 'python', $l13_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l13_t7_policy$::jsonb),
    ($l13_t8_title$Списки$l13_t8_title$, $l13_t8_statement$**Коротко:** Посчитайте средний балл.

### Условие

На вход подаётся строка оценок через пробел. Выведи среднее значение, округлённое до 2 знаков.

### Вход

Одна строка чисел.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5 4 3
```

Вывод:

```text
4.0
```

### Пример 2

Ввод:

```text
1 2
```

Вывод:

```text
1.5
```

### Шаблон

```python
grades = input().split()
```

### Подсказки

1. Сложи числа и раздели на количество.

2. Количество элементов: `len(grades)`.$l13_t8_statement$, $l13_t8_starter$grades = input().split()
$l13_t8_starter$, $l13_t8_solution$grades = input().split()
total = 0
for grade in grades:
    total = total + int(grade)
avg = total / len(grades)
print(round(avg, 2))
$l13_t8_solution$, 2, 70, $l13_t8_topic$Python M1 — Контроль$l13_t8_topic$, 'python', $l13_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l13_t8_policy$::jsonb),
    ($l13_t9_title$Словари$l13_t9_title$, $l13_t9_statement$**Коротко:** Найдите самый частый товар.

### Условие

На вход подаётся строка товаров через пробел. Выведи товар, который встретился чаще всего. Если есть равенство, выведи тот, который встретился раньше.

### Вход

Одна строка.

### Выход

Один товар.

### Пример 1

Ввод:

```text
чай кофе чай сок
```

Вывод:

```text
чай
```

### Пример 2

Ввод:

```text
a b a b
```

Вывод:

```text
a
```

### Шаблон

```python
items = input().split()
```

### Подсказки

1. Сначала посчитай частоты словарём.

2. Потом пройди по исходному списку и найди максимум.$l13_t9_statement$, $l13_t9_starter$items = input().split()
$l13_t9_starter$, $l13_t9_solution$items = input().split()
counts = {}
for item in items:
    counts[item] = counts.get(item, 0) + 1
best = items[0]
for item in items:
    if counts[item] > counts[best]:
        best = item
print(best)
$l13_t9_solution$, 3, 85, $l13_t9_topic$Python M1 — Контроль$l13_t9_topic$, 'python', $l13_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l13_t9_policy$::jsonb),
    ($l13_t10_title$Функции$l13_t10_title$, $l13_t10_statement$**Коротко:** Напишите функцию скидки.

### Условие

Напиши функцию `final_price(price, discount)`, которая возвращает цену после скидки в процентах. Считай цену и скидку, выведи результат, округлённый до 2 знаков.

### Вход

Цена и скидка.

### Выход

Одно число.

### Пример 1

Ввод:

```text
1000
10
```

Вывод:

```text
900.0
```

### Пример 2

Ввод:

```text
500
25
```

Вывод:

```text
375.0
```

### Шаблон

```python
def final_price(price, discount):
    # return ...
```

### Подсказки

1. Скидка: `price * discount / 100`.

2. Функция должна использовать `return`.$l13_t10_statement$, $l13_t10_starter$def final_price(price, discount):
    # return ...
$l13_t10_starter$, $l13_t10_solution$def final_price(price, discount):
    return price - price * discount / 100

price = float(input())
discount = float(input())
print(round(final_price(price, discount), 2))
$l13_t10_solution$, 3, 85, $l13_t10_topic$Python M1 — Контроль$l13_t10_topic$, 'python', $l13_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true}$l13_t10_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
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
    ts.source_policy,
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
    source_policy = EXCLUDED.source_policy,
    is_published = TRUE,
    updated_at = NOW();

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 13
), target_tasks AS (
    SELECT t.id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
    WHERE t.title IN (
        $l13_t2_delete_title$Ввод и вывод$l13_t2_delete_title$,
        $l13_t3_delete_title$Арифметика$l13_t3_delete_title$,
        $l13_t4_delete_title$Условия$l13_t4_delete_title$,
        $l13_t5_delete_title$Логика$l13_t5_delete_title$,
        $l13_t6_delete_title$Циклы$l13_t6_delete_title$,
        $l13_t7_delete_title$Строки$l13_t7_delete_title$,
        $l13_t8_delete_title$Списки$l13_t8_delete_title$,
        $l13_t9_delete_title$Словари$l13_t9_delete_title$,
        $l13_t10_delete_title$Функции$l13_t10_delete_title$
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 13
), task_lookup AS (
    SELECT t.id, t.title
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
    VALUES
    ($l13_test_2_1_title$Ввод и вывод$l13_test_2_1_title$, $l13_test_2_1_input$Анна
Москва$l13_test_2_1_input$, $l13_test_2_1_expected$Анна из города Москва$l13_test_2_1_expected$, FALSE, 1),
    ($l13_test_2_2_title$Ввод и вывод$l13_test_2_2_title$, $l13_test_2_2_input$Олег
Казань$l13_test_2_2_input$, $l13_test_2_2_expected$Олег из города Казань$l13_test_2_2_expected$, TRUE, 2),
    ($l13_test_3_1_title$Арифметика$l13_test_3_1_title$, $l13_test_3_1_input$100
3
50$l13_test_3_1_input$, $l13_test_3_1_expected$250$l13_test_3_1_expected$, FALSE, 1),
    ($l13_test_3_2_title$Арифметика$l13_test_3_2_title$, $l13_test_3_2_input$10
1
0$l13_test_3_2_input$, $l13_test_3_2_expected$10$l13_test_3_2_expected$, TRUE, 2),
    ($l13_test_4_1_title$Условия$l13_test_4_1_title$, $l13_test_4_1_input$17$l13_test_4_1_input$, $l13_test_4_1_expected$Нет$l13_test_4_1_expected$, FALSE, 1),
    ($l13_test_4_2_title$Условия$l13_test_4_2_title$, $l13_test_4_2_input$18$l13_test_4_2_input$, $l13_test_4_2_expected$Да$l13_test_4_2_expected$, TRUE, 2),
    ($l13_test_4_3_title$Условия$l13_test_4_3_title$, $l13_test_4_3_input$64$l13_test_4_3_input$, $l13_test_4_3_expected$Да$l13_test_4_3_expected$, TRUE, 3),
    ($l13_test_4_4_title$Условия$l13_test_4_4_title$, $l13_test_4_4_input$65$l13_test_4_4_input$, $l13_test_4_4_expected$Льготный$l13_test_4_4_expected$, TRUE, 4),
    ($l13_test_5_1_title$Логика$l13_test_5_1_title$, $l13_test_5_1_input$admin
no$l13_test_5_1_input$, $l13_test_5_1_expected$Доступ$l13_test_5_1_expected$, FALSE, 1),
    ($l13_test_5_2_title$Логика$l13_test_5_2_title$, $l13_test_5_2_input$moderator
no$l13_test_5_2_input$, $l13_test_5_2_expected$Доступ$l13_test_5_2_expected$, TRUE, 2),
    ($l13_test_5_3_title$Логика$l13_test_5_3_title$, $l13_test_5_3_input$admin
yes$l13_test_5_3_input$, $l13_test_5_3_expected$Нет доступа$l13_test_5_3_expected$, TRUE, 3),
    ($l13_test_5_4_title$Логика$l13_test_5_4_title$, $l13_test_5_4_input$user
no$l13_test_5_4_input$, $l13_test_5_4_expected$Нет доступа$l13_test_5_4_expected$, TRUE, 4),
    ($l13_test_6_1_title$Циклы$l13_test_6_1_title$, $l13_test_6_1_input$5
1
2
3
4
5$l13_test_6_1_input$, $l13_test_6_1_expected$6$l13_test_6_1_expected$, FALSE, 1),
    ($l13_test_6_2_title$Циклы$l13_test_6_2_title$, $l13_test_6_2_input$3
1
3
5$l13_test_6_2_input$, $l13_test_6_2_expected$0$l13_test_6_2_expected$, TRUE, 2),
    ($l13_test_6_3_title$Циклы$l13_test_6_3_title$, $l13_test_6_3_input$2
-2
4$l13_test_6_3_input$, $l13_test_6_3_expected$2$l13_test_6_3_expected$, TRUE, 3),
    ($l13_test_7_1_title$Строки$l13_test_7_1_title$, $l13_test_7_1_input$Анна Ли Олег$l13_test_7_1_input$, $l13_test_7_1_expected$Ли$l13_test_7_1_expected$, FALSE, 1),
    ($l13_test_7_2_title$Строки$l13_test_7_2_title$, $l13_test_7_2_input$Анна Олег$l13_test_7_2_input$, $l13_test_7_2_expected$Не найдено$l13_test_7_2_expected$, TRUE, 2),
    ($l13_test_7_3_title$Строки$l13_test_7_3_title$, $l13_test_7_3_input$A B$l13_test_7_3_input$, $l13_test_7_3_expected$A$l13_test_7_3_expected$, TRUE, 3),
    ($l13_test_8_1_title$Списки$l13_test_8_1_title$, $l13_test_8_1_input$5 4 3$l13_test_8_1_input$, $l13_test_8_1_expected$4.0$l13_test_8_1_expected$, FALSE, 1),
    ($l13_test_8_2_title$Списки$l13_test_8_2_title$, $l13_test_8_2_input$1 2$l13_test_8_2_input$, $l13_test_8_2_expected$1.5$l13_test_8_2_expected$, TRUE, 2),
    ($l13_test_8_3_title$Списки$l13_test_8_3_title$, $l13_test_8_3_input$1 1 2$l13_test_8_3_input$, $l13_test_8_3_expected$1.33$l13_test_8_3_expected$, TRUE, 3),
    ($l13_test_9_1_title$Словари$l13_test_9_1_title$, $l13_test_9_1_input$чай кофе чай сок$l13_test_9_1_input$, $l13_test_9_1_expected$чай$l13_test_9_1_expected$, FALSE, 1),
    ($l13_test_9_2_title$Словари$l13_test_9_2_title$, $l13_test_9_2_input$a b a b$l13_test_9_2_input$, $l13_test_9_2_expected$a$l13_test_9_2_expected$, TRUE, 2),
    ($l13_test_9_3_title$Словари$l13_test_9_3_title$, $l13_test_9_3_input$x y y x y$l13_test_9_3_input$, $l13_test_9_3_expected$y$l13_test_9_3_expected$, TRUE, 3),
    ($l13_test_10_1_title$Функции$l13_test_10_1_title$, $l13_test_10_1_input$1000
10$l13_test_10_1_input$, $l13_test_10_1_expected$900.0$l13_test_10_1_expected$, FALSE, 1),
    ($l13_test_10_2_title$Функции$l13_test_10_2_title$, $l13_test_10_2_input$500
25$l13_test_10_2_input$, $l13_test_10_2_expected$375.0$l13_test_10_2_expected$, TRUE, 2),
    ($l13_test_10_3_title$Функции$l13_test_10_3_title$, $l13_test_10_3_input$99.9
5$l13_test_10_3_input$, $l13_test_10_3_expected$94.91$l13_test_10_3_expected$, TRUE, 3)
), resolved AS (
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
    WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 13
), task_lookup AS (
    SELECT t.title, t.id AS task_id
    FROM tasks t
    JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
    VALUES
    (1, 'theory', $l13_b1_title$Инструкция$l13_b1_title$, $l13_b1_content$Контрольный урок проверяет весь модуль. Условия короткие, подсказок меньше.

Правила:

- не добавляй лишний текст;
- используй `input()` без приглашений;
- проверяй граничные случаи;
- если задача про функции, функция должна возвращать результат через `return`.$l13_b1_content$, NULL, NULL::jsonb),
    (2, 'practice', $l13_b2_title$Ввод и вывод$l13_b2_title$, $l13_b2_content$**Коротко:** Соберите строку профиля.

### Условие

На вход подаются имя и город. Выведи `Имя из города Город`.

### Вход

Две строки.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
Анна
Москва
```

Вывод:

```text
Анна из города Москва
```

### Шаблон

```python
name = input()
city = input()
```

### Подсказки

1. Выведи несколько значений через `print()`.

2. Следи за точным текстом.$l13_b2_content$, $l13_b2_task$Ввод и вывод$l13_b2_task$, NULL::jsonb),
    (3, 'practice', $l13_b3_title$Арифметика$l13_b3_title$, $l13_b3_content$**Коротко:** Посчитайте оплату.

### Условие

На вход подаются цена, количество и скидка в рублях. Выведи `price * count - discount`.

### Вход

Три целых числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
100
3
50
```

Вывод:

```text
250
```

### Шаблон

```python
price = int(input())
count = int(input())
discount = int(input())
```

### Подсказки

1. Сначала умножение.

2. Потом вычитание скидки.$l13_b3_content$, $l13_b3_task$Арифметика$l13_b3_task$, NULL::jsonb),
    (4, 'practice', $l13_b4_title$Условия$l13_b4_title$, $l13_b4_content$**Коротко:** Определите доступ.

### Условие

На вход подаётся возраст. До 18 — `Нет`, от 18 до 64 — `Да`, от 65 — `Льготный`.

### Вход

Одно число.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
17
```

Вывод:

```text
Нет
```

### Пример 2

Ввод:

```text
18
```

Вывод:

```text
Да
```

### Пример 3

Ввод:

```text
65
```

Вывод:

```text
Льготный
```

### Шаблон

```python
age = int(input())
```

### Подсказки

1. Границы: 18 и 65.

2. Порядок проверок важен.$l13_b4_content$, $l13_b4_task$Условия$l13_b4_task$, NULL::jsonb),
    (5, 'practice', $l13_b5_title$Логика$l13_b5_title$, $l13_b5_content$**Коротко:** Проверьте вход в систему.

### Условие

На вход подаются роль и статус блокировки (`yes` или `no`). Доступ есть для `admin` или `moderator`, если блокировки нет.

### Вход

Роль и блокировка.

### Выход

`Доступ` или `Нет доступа`.

### Пример 1

Ввод:

```text
admin
no
```

Вывод:

```text
Доступ
```

### Пример 2

Ввод:

```text
admin
yes
```

Вывод:

```text
Нет доступа
```

### Пример 3

Ввод:

```text
user
no
```

Вывод:

```text
Нет доступа
```

### Шаблон

```python
role = input()
blocked = input()
```

### Подсказки

1. Роль проверяй через `or`.

2. Блокировки нет: `blocked == "no"`.$l13_b5_content$, $l13_b5_task$Логика$l13_b5_task$, NULL::jsonb),
    (6, 'practice', $l13_b6_title$Циклы$l13_b6_title$, $l13_b6_content$**Коротко:** Найдите сумму чётных.

### Условие

Сначала вводится `n`, затем `n` чисел. Выведи сумму чётных чисел.

### Вход

Количество и числа.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5
1
2
3
4
5
```

Вывод:

```text
6
```

### Шаблон

```python
n = int(input())
total = 0
```

### Подсказки

1. Чётность: `% 2 == 0`.

2. Суммируй только подходящие числа.$l13_b6_content$, $l13_b6_task$Циклы$l13_b6_task$, NULL::jsonb),
    (7, 'practice', $l13_b7_title$Строки$l13_b7_title$, $l13_b7_content$**Коротко:** Найдите короткое имя.

### Условие

На вход подаётся строка имён через пробел. Выведи первое имя длиной меньше 4 символов. Если такого нет, выведи `Не найдено`.

### Вход

Одна строка.

### Выход

Одна строка.

### Пример 1

Ввод:

```text
Анна Ли Олег
```

Вывод:

```text
Ли
```

### Пример 2

Ввод:

```text
Анна Олег
```

Вывод:

```text
Не найдено
```

### Шаблон

```python
names = input().split()
```

### Подсказки

1. Нужен флаг `found`.

2. После первого найденного имени можно использовать `break`.$l13_b7_content$, $l13_b7_task$Строки$l13_b7_task$, NULL::jsonb),
    (8, 'practice', $l13_b8_title$Списки$l13_b8_title$, $l13_b8_content$**Коротко:** Посчитайте средний балл.

### Условие

На вход подаётся строка оценок через пробел. Выведи среднее значение, округлённое до 2 знаков.

### Вход

Одна строка чисел.

### Выход

Одно число.

### Пример 1

Ввод:

```text
5 4 3
```

Вывод:

```text
4.0
```

### Пример 2

Ввод:

```text
1 2
```

Вывод:

```text
1.5
```

### Шаблон

```python
grades = input().split()
```

### Подсказки

1. Сложи числа и раздели на количество.

2. Количество элементов: `len(grades)`.$l13_b8_content$, $l13_b8_task$Списки$l13_b8_task$, NULL::jsonb),
    (9, 'practice', $l13_b9_title$Словари$l13_b9_title$, $l13_b9_content$**Коротко:** Найдите самый частый товар.

### Условие

На вход подаётся строка товаров через пробел. Выведи товар, который встретился чаще всего. Если есть равенство, выведи тот, который встретился раньше.

### Вход

Одна строка.

### Выход

Один товар.

### Пример 1

Ввод:

```text
чай кофе чай сок
```

Вывод:

```text
чай
```

### Пример 2

Ввод:

```text
a b a b
```

Вывод:

```text
a
```

### Шаблон

```python
items = input().split()
```

### Подсказки

1. Сначала посчитай частоты словарём.

2. Потом пройди по исходному списку и найди максимум.$l13_b9_content$, $l13_b9_task$Словари$l13_b9_task$, NULL::jsonb),
    (10, 'practice', $l13_b10_title$Функции$l13_b10_title$, $l13_b10_content$**Коротко:** Напишите функцию скидки.

### Условие

Напиши функцию `final_price(price, discount)`, которая возвращает цену после скидки в процентах. Считай цену и скидку, выведи результат, округлённый до 2 знаков.

### Вход

Цена и скидка.

### Выход

Одно число.

### Пример 1

Ввод:

```text
1000
10
```

Вывод:

```text
900.0
```

### Пример 2

Ввод:

```text
500
25
```

Вывод:

```text
375.0
```

### Шаблон

```python
def final_price(price, discount):
    # return ...
```

### Подсказки

1. Скидка: `price * discount / 100`.

2. Функция должна использовать `return`.$l13_b10_content$, $l13_b10_task$Функции$l13_b10_task$, NULL::jsonb),
    (11, 'theory', $l13_b11_title$Результат$l13_b11_title$, $l13_b11_content$После контрольного урока ученик должен уметь:

- писать программы с вводом и выводом;
- использовать числа, строки, списки и словари;
- писать условия и циклы;
- разбивать часть логики на функции;
- читать условие задачи и соблюдать точный формат вывода.

Если ученик провалил тему, платформа должна отправить его в маршрут восстановления по соответствующему уроку.

# Маршруты восстановления

Использовать автоматически, если ученик не решил обязательную задачу урока за 5 попыток или провалил контроль по теме.

| Тема | Куда вернуть | Что дать |
|---|---|---|
| `input` и `int` | Урок 1, шаги 11–18 | 5 простых задач на ввод чисел |
| Условия | Урок 3, шаги 3–11 | задачи на границы 17/18/59/60 |
| Логика | Урок 4, шаги 1–9 | таблицы истинности и задачи на `and/or` |
| Циклы | Уроки 5–6 | сумма, количество, максимум |
| Строки | Урок 7 | len, index, slice, lower/strip |
| Списки | Урок 8 | split, перебор, фильтр |
| Словари | Уроки 9–10 | get, частоты, фиксированный порядок вывода |
| Функции | Урок 11 | return, параметры, вызов функции |

# Политика AI-подсказок

AI-подсказка должна помогать, но не решать задачу за ученика.

Разрешено:
- указать, где вероятная ошибка;
- напомнить нужную конструкцию;
- предложить проверить конкретный тест;
- объяснить ошибку простыми словами.

Запрещено:
- выдавать полный код до 3 неудачных попыток;
- переписывать всё решение;
- подсказывать скрытые тесты.

Пример хорошей AI-подсказки:
> В задаче нужен числовой ввод. Проверь, используешь ли ты `int(input())` для обоих чисел.

Пример плохой AI-подсказки:
> Напиши `a = int(input()); b = int(input()); print(a + b)`.$l13_b11_content$, NULL, NULL::jsonb)
), resolved AS (
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

