-- 018_seed_python_zero_full_v4.sql
-- Generated from python_course_platform_v4_full.md + import_manifest.csv
-- Purpose: full-course import with whitelist body parsing and separated system fields.

INSERT INTO courses(slug, title, description, is_published)
VALUES ('python-zero', $course_title$Python с нуля — Full Stack + AI$course_title$, $course_desc$Полный курс на 5 месяцев: Python Core, Python Hard, SQL/сети, FastAPI/DevOps, финальный проект и AI-интеграция.$course_desc$, TRUE)
ON CONFLICT (slug) DO UPDATE
SET title = EXCLUDED.title,
    description = EXCLUDED.description,
    is_published = TRUE,
    updated_at = NOW();

WITH course_ref AS (
  SELECT id AS course_id FROM courses WHERE slug = 'python-zero'
), module_seed(position, title) AS (
  VALUES
  (1, $m1_title$Месяц 1. Python Core$m1_title$),
  (2, $m2_title$Месяц 2. Python Hard$m2_title$),
  (3, $m3_title$Месяц 3. SQL и сети$m3_title$),
  (4, $m4_title$Месяц 4. FastAPI и DevOps$m4_title$),
  (5, $m5_title$Месяц 5. Финальный проект, AI и деплой$m5_title$)
)
INSERT INTO modules(course_id, title, position)
SELECT cr.course_id, ms.title, ms.position
FROM course_ref cr
CROSS JOIN module_seed ms
ON CONFLICT (course_id, position) DO UPDATE
SET title = EXCLUDED.title,
    updated_at = NOW();

-- Module 1: Месяц 1. Python Core
WITH module_ref AS (
  SELECT m.id AS module_id
  FROM modules m
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1
), lesson_seed(position, title, content_md) AS (
  VALUES
  (1, $m1_l1_title$Первый код$m1_l1_title$, $m1_l1_content$Первый вывод, переменные, ввод данных и числа.$m1_l1_content$),
  (2, $m1_l2_title$Числа$m1_l2_title$, $m1_l2_content$Арифметика, деление, остаток, дробные числа и формулы.$m1_l2_content$),
  (3, $m1_l3_title$Условия$m1_l3_title$, $m1_l3_content$Сравнения и ветвления: if, else, elif.$m1_l3_content$),
  (4, $m1_l4_title$Логика$m1_l4_title$, $m1_l4_content$Сложные проверки через and, or, not.$m1_l4_content$),
  (5, $m1_l5_title$while$m1_l5_title$, $m1_l5_content$Цикл, который работает, пока условие истинно.$m1_l5_content$),
  (6, $m1_l6_title$for и range$m1_l6_title$, $m1_l6_content$Повторение известное количество раз.$m1_l6_content$),
  (7, $m1_l7_title$Строки$m1_l7_title$, $m1_l7_content$Длина, индексы, срезы, методы и простая обработка текста.$m1_l7_content$),
  (8, $m1_l8_title$Списки$m1_l8_title$, $m1_l8_content$Хранение нескольких значений, append, split и перебор.$m1_l8_content$),
  (9, $m1_l9_title$Словари$m1_l9_title$, $m1_l9_content$Ключи, значения, поиск и перебор словаря.$m1_l9_content$),
  (10, $m1_l10_title$Множества$m1_l10_title$, $m1_l10_content$Уникальные значения и частотные словари.$m1_l10_content$),
  (11, $m1_l11_title$Функции$m1_l11_title$, $m1_l11_content$def, параметры, return и разбиение кода.$m1_l11_content$),
  (12, $m1_l12_title$Проект$m1_l12_title$, $m1_l12_content$Консольный трекер задач с командами.$m1_l12_content$),
  (13, $m1_l13_title$Контроль$m1_l13_title$, $m1_l13_content$Проверка всех тем модуля.$m1_l13_content$)
)
INSERT INTO lessons(module_id, title, content_md, position, is_published)
SELECT mr.module_id, ls.title, ls.content_md, ls.position, TRUE
FROM module_ref mr
CROSS JOIN lesson_seed ls
ON CONFLICT (module_id, position) DO UPDATE
SET title = EXCLUDED.title,
    content_md = EXCLUDED.content_md,
    is_published = TRUE,
    updated_at = NOW();

-- Module 1, lesson 1: Первый код
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l1_t2_title$Первый вывод$m1_l1_t2_title$, $m1_l1_t2_statement$**Коротко:** Выведите одну строку.

### Условие

Напиши программу, которая выводит `Привет, Python!`.

### Вход

Нет.

### Выход

Одна строка: `Привет, Python!`.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Привет, Python!
```$m1_l1_t2_statement$, $m1_l1_t2_starter$print(...)
$m1_l1_t2_starter$, $m1_l1_t2_solution$print("Привет, Python!")
$m1_l1_t2_solution$, 1, 25, $m1_l1_t2_topic$Месяц 1. Python Core — Первый код$m1_l1_t2_topic$, $m1_l1_t2_lang$python$m1_l1_t2_lang$, $m1_l1_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Используй `print()`.","Текст напиши в кавычках."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t2_policy$::jsonb),
  ($m1_l1_t3_title$Две строки$m1_l1_t3_title$, $m1_l1_t3_statement$**Коротко:** Выведите две строки подряд.

### Условие

Напиши программу, которая выводит две строки: `Привет!` и `Это мой первый код.`.

### Вход

Нет.

### Выход

Две строки в указанном порядке.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Привет!
Это мой первый код.
```$m1_l1_t3_statement$, $m1_l1_t3_starter$# напиши два print()
$m1_l1_t3_starter$, $m1_l1_t3_solution$print("Привет!")
print("Это мой первый код.")
$m1_l1_t3_solution$, 1, 30, $m1_l1_t3_topic$Месяц 1. Python Core — Первый код$m1_l1_t3_topic$, $m1_l1_t3_lang$python$m1_l1_t3_lang$, $m1_l1_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Один `print()` выводит одну строку.","Используй два `print()`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t3_policy$::jsonb),
  ($m1_l1_t6_title$Математика$m1_l1_t6_title$, $m1_l1_t6_statement$**Коротко:** Выведите три результата.

### Условие

Выведи сумму `12 + 8`, разность `30 - 5` и произведение `7 * 6`. Каждый результат — с новой строки.

### Вход

Нет.

### Выход

Три числа, каждое с новой строки.

### Пример 1

Ввод:

```text

```

Вывод:

```text
20
25
42
```$m1_l1_t6_statement$, $m1_l1_t6_starter$# три print()
$m1_l1_t6_starter$, $m1_l1_t6_solution$print(12 + 8)
print(30 - 5)
print(7 * 6)
$m1_l1_t6_solution$, 1, 35, $m1_l1_t6_topic$Месяц 1. Python Core — Первый код$m1_l1_t6_topic$, $m1_l1_t6_lang$python$m1_l1_t6_lang$, $m1_l1_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Считать можно прямо внутри `print()`.","Для умножения используется `*`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t6_policy$::jsonb),
  ($m1_l1_t9_title$Анкета$m1_l1_t9_title$, $m1_l1_t9_statement$**Коротко:** Создайте переменные и выведите анкету.

### Условие

Создай переменные `name = "Анна"`, `age = 16`, `city = "Москва"`. Выведи анкету в точном формате.

### Вход

Нет.

### Выход

Три строки: имя, возраст, город.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Имя: Анна
Возраст: 16
Город: Москва
```$m1_l1_t9_statement$, $m1_l1_t9_starter$name = "Анна"
age = 16
city = "Москва"

# выведи анкету
$m1_l1_t9_starter$, $m1_l1_t9_solution$name = "Анна"
age = 16
city = "Москва"

print("Имя:", name)
print("Возраст:", age)
print("Город:", city)
$m1_l1_t9_solution$, 1, 35, $m1_l1_t9_topic$Месяц 1. Python Core — Первый код$m1_l1_t9_topic$, $m1_l1_t9_lang$python$m1_l1_t9_lang$, $m1_l1_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Используй `print(\"Имя:\", name)`.","Следи за точным текстом перед двоеточием."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t9_policy$::jsonb),
  ($m1_l1_t10_title$Не строка$m1_l1_t10_title$, $m1_l1_t10_statement$**Коротко:** Исправьте вывод переменной.

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
Привет, Анна
```$m1_l1_t10_statement$, $m1_l1_t10_starter$$m1_l1_t10_starter$, $m1_l1_t10_solution$name = "Анна"
print("Привет,", name)
$m1_l1_t10_solution$, 2, 45, $m1_l1_t10_topic$Месяц 1. Python Core — Первый код$m1_l1_t10_topic$, $m1_l1_t10_lang$python$m1_l1_t10_lang$, $m1_l1_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["`name` внутри кавычек — текст.","Переменную нужно передать в `print()` без кавычек."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t10_policy$::jsonb),
  ($m1_l1_t12_title$Приветствие$m1_l1_t12_title$, $m1_l1_t12_statement$**Коротко:** Считайте имя и поприветствуйте.

### Условие

На вход подаётся имя. Выведи `Привет, <имя>`.

### Вход

Одна строка — имя.

### Выход

Одна строка приветствия.

### Пример 1

Ввод:

```text
Маша
```

Вывод:

```text
Привет, Маша
```

### Пример 2

Ввод:

```text
Илья
```

Вывод:

```text
Привет, Илья
```$m1_l1_t12_statement$, $m1_l1_t12_starter$name = input()
# выведи приветствие
$m1_l1_t12_starter$, $m1_l1_t12_solution$name = input()
print("Привет,", name)
$m1_l1_t12_solution$, 1, 35, $m1_l1_t12_topic$Месяц 1. Python Core — Первый код$m1_l1_t12_topic$, $m1_l1_t12_lang$python$m1_l1_t12_lang$, $m1_l1_t12_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сохрани имя в переменную.","Выведи текст и переменную через запятую."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t12_policy$::jsonb),
  ($m1_l1_t14_title$Возраст +1$m1_l1_t14_title$, $m1_l1_t14_statement$**Коротко:** Считайте возраст и прибавьте 1.

### Условие

На вход подаётся возраст. Выведи, сколько будет через год.

### Вход

Одно целое число.

### Выход

Строка `Через год вам будет <число>`.

### Пример 1

Ввод:

```text
15
```

Вывод:

```text
Через год вам будет 16
```

### Пример 2

Ввод:

```text
20
```

Вывод:

```text
Через год вам будет 21
```$m1_l1_t14_statement$, $m1_l1_t14_starter$age = int(input())
# посчитай возраст через год
$m1_l1_t14_starter$, $m1_l1_t14_solution$age = int(input())
next_age = age + 1
print("Через год вам будет", next_age)
$m1_l1_t14_solution$, 1, 40, $m1_l1_t14_topic$Месяц 1. Python Core — Первый код$m1_l1_t14_topic$, $m1_l1_t14_lang$python$m1_l1_t14_lang$, $m1_l1_t14_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Возраст нужно считать через `int(input())`.","Создай переменную `next_age = age + 1`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t14_policy$::jsonb),
  ($m1_l1_t15_title$Сумма двух$m1_l1_t15_title$, $m1_l1_t15_statement$**Коротко:** Сложите два числа.

### Условие

На вход подаются два целых числа. Выведи их сумму.

### Вход

Два целых числа, каждое с новой строки.

### Выход

Одно число — сумма.

### Пример 1

Ввод:

```text
10
25
```

Вывод:

```text
35
```

### Пример 2

Ввод:

```text
3
7
```

Вывод:

```text
10
```$m1_l1_t15_statement$, $m1_l1_t15_starter$a = int(input())
b = int(input())
# выведи сумму
$m1_l1_t15_starter$, $m1_l1_t15_solution$a = int(input())
b = int(input())
print(a + b)
$m1_l1_t15_solution$, 1, 40, $m1_l1_t15_topic$Месяц 1. Python Core — Первый код$m1_l1_t15_topic$, $m1_l1_t15_lang$python$m1_l1_t15_lang$, $m1_l1_t15_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Нужно два `input()`.","Оба значения нужно преобразовать через `int()`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t15_policy$::jsonb),
  ($m1_l1_t16_title$Ошибка 105$m1_l1_t16_title$, $m1_l1_t16_statement$**Коротко:** Исправьте сложение строк.

### Вход

Два целых числа.

### Выход

Одно число — сумма.

### Пример 1

Ввод:

```text
10
5
```

Вывод:

```text
15
```$m1_l1_t16_statement$, $m1_l1_t16_starter$$m1_l1_t16_starter$, $m1_l1_t16_solution$a = int(input())
b = int(input())
print(a + b)
$m1_l1_t16_solution$, 2, 45, $m1_l1_t16_topic$Месяц 1. Python Core — Первый код$m1_l1_t16_topic$, $m1_l1_t16_lang$python$m1_l1_t16_lang$, $m1_l1_t16_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["`input()` возвращает строки.","Используй `int(input())` для обоих чисел."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t16_policy$::jsonb),
  ($m1_l1_t17_title$Периметр$m1_l1_t17_title$, $m1_l1_t17_statement$**Коротко:** Посчитайте периметр прямоугольника.

### Условие

На вход подаются ширина и высота. Выведи периметр по формуле `2 * (width + height)`.

### Вход

Два целых числа: ширина и высота.

### Выход

Одно число — периметр.

### Пример 1

Ввод:

```text
4
7
```

Вывод:

```text
22
```

### Пример 2

Ввод:

```text
10
20
```

Вывод:

```text
60
```$m1_l1_t17_statement$, $m1_l1_t17_starter$width = int(input())
height = int(input())
# perimeter = ...
$m1_l1_t17_starter$, $m1_l1_t17_solution$width = int(input())
height = int(input())
perimeter = 2 * (width + height)
print(perimeter)
$m1_l1_t17_solution$, 2, 55, $m1_l1_t17_topic$Месяц 1. Python Core — Первый код$m1_l1_t17_topic$, $m1_l1_t17_lang$python$m1_l1_t17_lang$, $m1_l1_t17_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сначала сложи ширину и высоту.","Скобки нужны: `2 * (width + height)`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t17_policy$::jsonb),
  ($m1_l1_t18_title$Мини-чек$m1_l1_t18_title$, $m1_l1_t18_statement$**Коротко:** Посчитайте итог покупки.

### Условие

На вход подаются цена товара и количество. Выведи итоговую сумму в формате `Итого: <сумма>`.

### Вход

Два целых числа: цена и количество.

### Выход

Строка с итоговой суммой.

### Пример 1

Ввод:

```text
150
3
```

Вывод:

```text
Итого: 450
```

### Пример 2

Ввод:

```text
99
5
```

Вывод:

```text
Итого: 495
```$m1_l1_t18_statement$, $m1_l1_t18_starter$price = int(input())
count = int(input())
# total = ...
$m1_l1_t18_starter$, $m1_l1_t18_solution$price = int(input())
count = int(input())
total = price * count
print("Итого:", total)
$m1_l1_t18_solution$, 2, 55, $m1_l1_t18_topic$Месяц 1. Python Core — Первый код$m1_l1_t18_topic$, $m1_l1_t18_lang$python$m1_l1_t18_lang$, $m1_l1_t18_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Итог: `price * count`.","Выведи текст `Итого:` и сумму."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t18_policy$::jsonb),
  ($m1_l1_t20_title$Анкета 2$m1_l1_t20_title$, $m1_l1_t20_statement$**Коротко:** Соберите ввод, число и вывод.

### Условие

На вход подаются имя, возраст и город. Выведи анкету и возраст через год.

### Вход

Три строки: имя, возраст, город.

### Выход

Три строки по образцу.

### Пример 1

Ввод:

```text
Анна
16
Москва
```

Вывод:

```text
Имя: Анна
Возраст через год: 17
Город: Москва
```

### Пример 2

Ввод:

```text
Олег
25
Казань
```

Вывод:

```text
Имя: Олег
Возраст через год: 26
Город: Казань
```$m1_l1_t20_statement$, $m1_l1_t20_starter$name = input()
age = int(input())
city = input()
# выведи анкету
$m1_l1_t20_starter$, $m1_l1_t20_solution$name = input()
age = int(input())
city = input()
next_age = age + 1
print("Имя:", name)
print("Возраст через год:", next_age)
print("Город:", city)
$m1_l1_t20_solution$, 2, 65, $m1_l1_t20_topic$Месяц 1. Python Core — Первый код$m1_l1_t20_topic$, $m1_l1_t20_lang$python$m1_l1_t20_lang$, $m1_l1_t20_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Возраст нужен как число.","Возраст через год: `age + 1`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l1_t20_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m1_l1_ttitle_2$Первый вывод$m1_l1_ttitle_2$,
    $m1_l1_ttitle_3$Две строки$m1_l1_ttitle_3$,
    $m1_l1_ttitle_6$Математика$m1_l1_ttitle_6$,
    $m1_l1_ttitle_9$Анкета$m1_l1_ttitle_9$,
    $m1_l1_ttitle_10$Не строка$m1_l1_ttitle_10$,
    $m1_l1_ttitle_12$Приветствие$m1_l1_ttitle_12$,
    $m1_l1_ttitle_14$Возраст +1$m1_l1_ttitle_14$,
    $m1_l1_ttitle_15$Сумма двух$m1_l1_ttitle_15$,
    $m1_l1_ttitle_16$Ошибка 105$m1_l1_ttitle_16$,
    $m1_l1_ttitle_17$Периметр$m1_l1_ttitle_17$,
    $m1_l1_ttitle_18$Мини-чек$m1_l1_ttitle_18$,
    $m1_l1_ttitle_20$Анкета 2$m1_l1_ttitle_20$
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
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l1_test_2_1_title$Первый вывод$m1_l1_test_2_1_title$, $m1_l1_test_2_1_input$$m1_l1_test_2_1_input$, $m1_l1_test_2_1_expected$Привет, Python!$m1_l1_test_2_1_expected$, FALSE, 1),
  ($m1_l1_test_3_1_title$Две строки$m1_l1_test_3_1_title$, $m1_l1_test_3_1_input$$m1_l1_test_3_1_input$, $m1_l1_test_3_1_expected$Привет!
Это мой первый код.$m1_l1_test_3_1_expected$, FALSE, 1),
  ($m1_l1_test_6_1_title$Математика$m1_l1_test_6_1_title$, $m1_l1_test_6_1_input$$m1_l1_test_6_1_input$, $m1_l1_test_6_1_expected$20
25
42$m1_l1_test_6_1_expected$, FALSE, 1),
  ($m1_l1_test_9_1_title$Анкета$m1_l1_test_9_1_title$, $m1_l1_test_9_1_input$$m1_l1_test_9_1_input$, $m1_l1_test_9_1_expected$Имя: Анна
Возраст: 16
Город: Москва$m1_l1_test_9_1_expected$, FALSE, 1),
  ($m1_l1_test_10_1_title$Не строка$m1_l1_test_10_1_title$, $m1_l1_test_10_1_input$$m1_l1_test_10_1_input$, $m1_l1_test_10_1_expected$Привет, Анна$m1_l1_test_10_1_expected$, FALSE, 1),
  ($m1_l1_test_12_1_title$Приветствие$m1_l1_test_12_1_title$, $m1_l1_test_12_1_input$Маша$m1_l1_test_12_1_input$, $m1_l1_test_12_1_expected$Привет, Маша$m1_l1_test_12_1_expected$, FALSE, 1),
  ($m1_l1_test_12_2_title$Приветствие$m1_l1_test_12_2_title$, $m1_l1_test_12_2_input$Илья$m1_l1_test_12_2_input$, $m1_l1_test_12_2_expected$Привет, Илья$m1_l1_test_12_2_expected$, TRUE, 2),
  ($m1_l1_test_12_3_title$Приветствие$m1_l1_test_12_3_title$, $m1_l1_test_12_3_input$Python$m1_l1_test_12_3_input$, $m1_l1_test_12_3_expected$Привет, Python$m1_l1_test_12_3_expected$, TRUE, 3),
  ($m1_l1_test_14_1_title$Возраст +1$m1_l1_test_14_1_title$, $m1_l1_test_14_1_input$15$m1_l1_test_14_1_input$, $m1_l1_test_14_1_expected$Через год вам будет 16$m1_l1_test_14_1_expected$, FALSE, 1),
  ($m1_l1_test_14_2_title$Возраст +1$m1_l1_test_14_2_title$, $m1_l1_test_14_2_input$20$m1_l1_test_14_2_input$, $m1_l1_test_14_2_expected$Через год вам будет 21$m1_l1_test_14_2_expected$, TRUE, 2),
  ($m1_l1_test_14_3_title$Возраст +1$m1_l1_test_14_3_title$, $m1_l1_test_14_3_input$0$m1_l1_test_14_3_input$, $m1_l1_test_14_3_expected$Через год вам будет 1$m1_l1_test_14_3_expected$, TRUE, 3),
  ($m1_l1_test_15_1_title$Сумма двух$m1_l1_test_15_1_title$, $m1_l1_test_15_1_input$10
25$m1_l1_test_15_1_input$, $m1_l1_test_15_1_expected$35$m1_l1_test_15_1_expected$, FALSE, 1),
  ($m1_l1_test_15_2_title$Сумма двух$m1_l1_test_15_2_title$, $m1_l1_test_15_2_input$3
7$m1_l1_test_15_2_input$, $m1_l1_test_15_2_expected$10$m1_l1_test_15_2_expected$, TRUE, 2),
  ($m1_l1_test_15_3_title$Сумма двух$m1_l1_test_15_3_title$, $m1_l1_test_15_3_input$100
200$m1_l1_test_15_3_input$, $m1_l1_test_15_3_expected$300$m1_l1_test_15_3_expected$, TRUE, 3),
  ($m1_l1_test_16_1_title$Ошибка 105$m1_l1_test_16_1_title$, $m1_l1_test_16_1_input$10
5$m1_l1_test_16_1_input$, $m1_l1_test_16_1_expected$15$m1_l1_test_16_1_expected$, FALSE, 1),
  ($m1_l1_test_16_2_title$Ошибка 105$m1_l1_test_16_2_title$, $m1_l1_test_16_2_input$1
2$m1_l1_test_16_2_input$, $m1_l1_test_16_2_expected$3$m1_l1_test_16_2_expected$, TRUE, 2),
  ($m1_l1_test_16_3_title$Ошибка 105$m1_l1_test_16_3_title$, $m1_l1_test_16_3_input$100
0$m1_l1_test_16_3_input$, $m1_l1_test_16_3_expected$100$m1_l1_test_16_3_expected$, TRUE, 3),
  ($m1_l1_test_17_1_title$Периметр$m1_l1_test_17_1_title$, $m1_l1_test_17_1_input$4
7$m1_l1_test_17_1_input$, $m1_l1_test_17_1_expected$22$m1_l1_test_17_1_expected$, FALSE, 1),
  ($m1_l1_test_17_2_title$Периметр$m1_l1_test_17_2_title$, $m1_l1_test_17_2_input$10
20$m1_l1_test_17_2_input$, $m1_l1_test_17_2_expected$60$m1_l1_test_17_2_expected$, TRUE, 2),
  ($m1_l1_test_17_3_title$Периметр$m1_l1_test_17_3_title$, $m1_l1_test_17_3_input$1
1$m1_l1_test_17_3_input$, $m1_l1_test_17_3_expected$4$m1_l1_test_17_3_expected$, TRUE, 3),
  ($m1_l1_test_18_1_title$Мини-чек$m1_l1_test_18_1_title$, $m1_l1_test_18_1_input$150
3$m1_l1_test_18_1_input$, $m1_l1_test_18_1_expected$Итого: 450$m1_l1_test_18_1_expected$, FALSE, 1),
  ($m1_l1_test_18_2_title$Мини-чек$m1_l1_test_18_2_title$, $m1_l1_test_18_2_input$99
5$m1_l1_test_18_2_input$, $m1_l1_test_18_2_expected$Итого: 495$m1_l1_test_18_2_expected$, TRUE, 2),
  ($m1_l1_test_18_3_title$Мини-чек$m1_l1_test_18_3_title$, $m1_l1_test_18_3_input$1000
1$m1_l1_test_18_3_input$, $m1_l1_test_18_3_expected$Итого: 1000$m1_l1_test_18_3_expected$, TRUE, 3),
  ($m1_l1_test_20_1_title$Анкета 2$m1_l1_test_20_1_title$, $m1_l1_test_20_1_input$Анна
16
Москва$m1_l1_test_20_1_input$, $m1_l1_test_20_1_expected$Имя: Анна
Возраст через год: 17
Город: Москва$m1_l1_test_20_1_expected$, FALSE, 1),
  ($m1_l1_test_20_2_title$Анкета 2$m1_l1_test_20_2_title$, $m1_l1_test_20_2_input$Олег
25
Казань$m1_l1_test_20_2_input$, $m1_l1_test_20_2_expected$Имя: Олег
Возраст через год: 26
Город: Казань$m1_l1_test_20_2_expected$, TRUE, 2),
  ($m1_l1_test_20_3_title$Анкета 2$m1_l1_test_20_3_title$, $m1_l1_test_20_3_input$Маша
0
Сочи$m1_l1_test_20_3_input$, $m1_l1_test_20_3_expected$Имя: Маша
Возраст через год: 1
Город: Сочи$m1_l1_test_20_3_expected$, TRUE, 3)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 1
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m1_l1_b1_type$theory$m1_l1_b1_type$, $m1_l1_b1_title$Старт$m1_l1_b1_title$, $m1_l1_b1_content$Python — это язык программирования. Программа — это набор инструкций для компьютера.

Первая команда:
```python
print("Привет, Python!")
```

Результат:
```text
Привет, Python!
```

`print()` выводит текст на экран. Текст пишется в кавычках.$m1_l1_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l1_b2_type$practice$m1_l1_b2_type$, $m1_l1_b2_title$Первый вывод$m1_l1_b2_title$, $m1_l1_b2_content$**Коротко:** Выведите одну строку.

### Условие

Напиши программу, которая выводит `Привет, Python!`.

### Вход

Нет.

### Выход

Одна строка: `Привет, Python!`.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Привет, Python!
```$m1_l1_b2_content$, $m1_l1_b2_task_title$Первый вывод$m1_l1_b2_task_title$, NULL::jsonb),
  (3, $m1_l1_b3_type$practice$m1_l1_b3_type$, $m1_l1_b3_title$Две строки$m1_l1_b3_title$, $m1_l1_b3_content$**Коротко:** Выведите две строки подряд.

### Условие

Напиши программу, которая выводит две строки: `Привет!` и `Это мой первый код.`.

### Вход

Нет.

### Выход

Две строки в указанном порядке.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Привет!
Это мой первый код.
```$m1_l1_b3_content$, $m1_l1_b3_task_title$Две строки$m1_l1_b3_task_title$, NULL::jsonb),
  (4, $m1_l1_b4_type$theory$m1_l1_b4_type$, $m1_l1_b4_title$Текст и числа$m1_l1_b4_title$, $m1_l1_b4_content$Python различает текст и числа.

```python
print("123")  # текст
print(123)    # число
```

С числами можно считать:
```python
print(10 + 5)
print(10 - 5)
print(10 * 5)
```

Если выражение написано в кавычках, Python выводит его как текст:
```python
print("2 + 3")
```$m1_l1_b4_content$, NULL, NULL::jsonb),
  (5, $m1_l1_b5_type$quiz$m1_l1_b5_type$, $m1_l1_b5_title$Кавычки$m1_l1_b5_title$, $m1_l1_b5_content$### Вопрос

Что выведет код?

```python
print(2 + 3)
print("2 + 3")
```

### Варианты

1. 5 и 5

2. 2 + 3 и 2 + 3

3. 5 и 2 + 3

4. Ошибка$m1_l1_b5_content$, NULL, NULL::jsonb),
  (6, $m1_l1_b6_type$practice$m1_l1_b6_type$, $m1_l1_b6_title$Математика$m1_l1_b6_title$, $m1_l1_b6_content$**Коротко:** Выведите три результата.

### Условие

Выведи сумму `12 + 8`, разность `30 - 5` и произведение `7 * 6`. Каждый результат — с новой строки.

### Вход

Нет.

### Выход

Три числа, каждое с новой строки.

### Пример 1

Ввод:

```text

```

Вывод:

```text
20
25
42
```$m1_l1_b6_content$, $m1_l1_b6_task_title$Математика$m1_l1_b6_task_title$, NULL::jsonb),
  (7, $m1_l1_b7_type$theory$m1_l1_b7_type$, $m1_l1_b7_title$Переменные$m1_l1_b7_title$, $m1_l1_b7_content$Переменная — это имя, за которым хранится значение.

```python
name = "Анна"
age = 16
```

Переменную можно вывести:
```python
print(name)
print(age)
```

Можно вывести текст и переменную вместе:
```python
print("Имя:", name)
```$m1_l1_b7_content$, NULL, NULL::jsonb),
  (8, $m1_l1_b8_type$theory$m1_l1_b8_type$, $m1_l1_b8_title$Имена$m1_l1_b8_title$, $m1_l1_b8_content$Имена переменных должны быть понятными.

Хорошо:
```python
user_name = "Иван"
user_age = 20
```

Плохо:
```python
a = "Иван"
b = 20
```

Правила: имя не начинается с цифры, использует буквы, цифры и `_`.$m1_l1_b8_content$, NULL, NULL::jsonb),
  (9, $m1_l1_b9_type$practice$m1_l1_b9_type$, $m1_l1_b9_title$Анкета$m1_l1_b9_title$, $m1_l1_b9_content$**Коротко:** Создайте переменные и выведите анкету.

### Условие

Создай переменные `name = "Анна"`, `age = 16`, `city = "Москва"`. Выведи анкету в точном формате.

### Вход

Нет.

### Выход

Три строки: имя, возраст, город.

### Пример 1

Ввод:

```text

```

Вывод:

```text
Имя: Анна
Возраст: 16
Город: Москва
```$m1_l1_b9_content$, $m1_l1_b9_task_title$Анкета$m1_l1_b9_task_title$, NULL::jsonb),
  (10, $m1_l1_b10_type$practice$m1_l1_b10_type$, $m1_l1_b10_title$Не строка$m1_l1_b10_title$, $m1_l1_b10_content$**Коротко:** Исправьте вывод переменной.

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
Привет, Анна
```$m1_l1_b10_content$, $m1_l1_b10_task_title$Не строка$m1_l1_b10_task_title$, NULL::jsonb),
  (11, $m1_l1_b11_type$theory$m1_l1_b11_type$, $m1_l1_b11_title$input$m1_l1_b11_title$, $m1_l1_b11_content$`input()` получает данные от пользователя.

```python
name = input()
print("Привет,", name)
```

В задачах с автопроверкой не пишем приглашения внутри `input()`:

```python
name = input()
```

Не нужно:
```python
name = input("Введите имя: ")
```$m1_l1_b11_content$, NULL, NULL::jsonb),
  (12, $m1_l1_b12_type$practice$m1_l1_b12_type$, $m1_l1_b12_title$Приветствие$m1_l1_b12_title$, $m1_l1_b12_content$**Коротко:** Считайте имя и поприветствуйте.

### Условие

На вход подаётся имя. Выведи `Привет, <имя>`.

### Вход

Одна строка — имя.

### Выход

Одна строка приветствия.

### Пример 1

Ввод:

```text
Маша
```

Вывод:

```text
Привет, Маша
```

### Пример 2

Ввод:

```text
Илья
```

Вывод:

```text
Привет, Илья
```$m1_l1_b12_content$, $m1_l1_b12_task_title$Приветствие$m1_l1_b12_task_title$, NULL::jsonb),
  (13, $m1_l1_b13_type$theory$m1_l1_b13_type$, $m1_l1_b13_title$int(input())$m1_l1_b13_title$, $m1_l1_b13_content$`input()` всегда возвращает текст.

Если нужно число, используй `int(input())`:

```python
age = int(input())
print(age + 1)
```

Без `int()` Python будет работать с текстом, а не с числом.$m1_l1_b13_content$, NULL, NULL::jsonb),
  (14, $m1_l1_b14_type$practice$m1_l1_b14_type$, $m1_l1_b14_title$Возраст +1$m1_l1_b14_title$, $m1_l1_b14_content$**Коротко:** Считайте возраст и прибавьте 1.

### Условие

На вход подаётся возраст. Выведи, сколько будет через год.

### Вход

Одно целое число.

### Выход

Строка `Через год вам будет <число>`.

### Пример 1

Ввод:

```text
15
```

Вывод:

```text
Через год вам будет 16
```

### Пример 2

Ввод:

```text
20
```

Вывод:

```text
Через год вам будет 21
```$m1_l1_b14_content$, $m1_l1_b14_task_title$Возраст +1$m1_l1_b14_task_title$, NULL::jsonb),
  (15, $m1_l1_b15_type$practice$m1_l1_b15_type$, $m1_l1_b15_title$Сумма двух$m1_l1_b15_title$, $m1_l1_b15_content$**Коротко:** Сложите два числа.

### Условие

На вход подаются два целых числа. Выведи их сумму.

### Вход

Два целых числа, каждое с новой строки.

### Выход

Одно число — сумма.

### Пример 1

Ввод:

```text
10
25
```

Вывод:

```text
35
```

### Пример 2

Ввод:

```text
3
7
```

Вывод:

```text
10
```$m1_l1_b15_content$, $m1_l1_b15_task_title$Сумма двух$m1_l1_b15_task_title$, NULL::jsonb),
  (16, $m1_l1_b16_type$practice$m1_l1_b16_type$, $m1_l1_b16_title$Ошибка 105$m1_l1_b16_title$, $m1_l1_b16_content$**Коротко:** Исправьте сложение строк.

### Вход

Два целых числа.

### Выход

Одно число — сумма.

### Пример 1

Ввод:

```text
10
5
```

Вывод:

```text
15
```$m1_l1_b16_content$, $m1_l1_b16_task_title$Ошибка 105$m1_l1_b16_task_title$, NULL::jsonb),
  (17, $m1_l1_b17_type$practice$m1_l1_b17_type$, $m1_l1_b17_title$Периметр$m1_l1_b17_title$, $m1_l1_b17_content$**Коротко:** Посчитайте периметр прямоугольника.

### Условие

На вход подаются ширина и высота. Выведи периметр по формуле `2 * (width + height)`.

### Вход

Два целых числа: ширина и высота.

### Выход

Одно число — периметр.

### Пример 1

Ввод:

```text
4
7
```

Вывод:

```text
22
```

### Пример 2

Ввод:

```text
10
20
```

Вывод:

```text
60
```$m1_l1_b17_content$, $m1_l1_b17_task_title$Периметр$m1_l1_b17_task_title$, NULL::jsonb),
  (18, $m1_l1_b18_type$practice$m1_l1_b18_type$, $m1_l1_b18_title$Мини-чек$m1_l1_b18_title$, $m1_l1_b18_content$**Коротко:** Посчитайте итог покупки.

### Условие

На вход подаются цена товара и количество. Выведи итоговую сумму в формате `Итого: <сумма>`.

### Вход

Два целых числа: цена и количество.

### Выход

Строка с итоговой суммой.

### Пример 1

Ввод:

```text
150
3
```

Вывод:

```text
Итого: 450
```

### Пример 2

Ввод:

```text
99
5
```

Вывод:

```text
Итого: 495
```$m1_l1_b18_content$, $m1_l1_b18_task_title$Мини-чек$m1_l1_b18_task_title$, NULL::jsonb),
  (19, $m1_l1_b19_type$theory$m1_l1_b19_type$, $m1_l1_b19_title$Автопроверка$m1_l1_b19_title$, $m1_l1_b19_content$В задачах важно выводить ровно то, что просит условие.

Если нужен вывод:
```text
15
```

не пиши:
```python
print("Ответ:", 15)
```

Такой вывод будет другим:
```text
Ответ: 15
```

Автопроверка считает это ошибкой.$m1_l1_b19_content$, NULL, NULL::jsonb),
  (20, $m1_l1_b20_type$practice$m1_l1_b20_type$, $m1_l1_b20_title$Анкета 2$m1_l1_b20_title$, $m1_l1_b20_content$**Коротко:** Соберите ввод, число и вывод.

### Условие

На вход подаются имя, возраст и город. Выведи анкету и возраст через год.

### Вход

Три строки: имя, возраст, город.

### Выход

Три строки по образцу.

### Пример 1

Ввод:

```text
Анна
16
Москва
```

Вывод:

```text
Имя: Анна
Возраст через год: 17
Город: Москва
```

### Пример 2

Ввод:

```text
Олег
25
Казань
```

Вывод:

```text
Имя: Олег
Возраст через год: 26
Город: Казань
```$m1_l1_b20_content$, $m1_l1_b20_task_title$Анкета 2$m1_l1_b20_task_title$, NULL::jsonb),
  (21, $m1_l1_b21_type$quiz$m1_l1_b21_type$, $m1_l1_b21_title$Итог$m1_l1_b21_title$, $m1_l1_b21_content$### Вопрос

Как правильно считать целое число из ввода?

### Варианты

1. `number = input()`

2. `number = int(input())`

3. `number = print(input())`

4. `number = text(input())`$m1_l1_b21_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 2: Числа
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 2
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 2
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l2_t2_title$Скобки$m1_l2_t2_title$, $m1_l2_t2_statement$**Коротко:** Вычислите выражение со скобками.

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
```$m1_l2_t2_statement$, $m1_l2_t2_starter$a = int(input())
b = int(input())
c = int(input())
$m1_l2_t2_starter$, $m1_l2_t2_solution$a = int(input())
b = int(input())
c = int(input())
print((a + b) * c)
$m1_l2_t2_solution$, 1, 40, $m1_l2_t2_topic$Месяц 1. Python Core — Числа$m1_l2_t2_topic$, $m1_l2_t2_lang$python$m1_l2_t2_lang$, $m1_l2_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сначала сложи `a` и `b`.","Запиши формулу: `(a + b) * c`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l2_t2_policy$::jsonb),
  ($m1_l2_t4_title$Целое деление$m1_l2_t4_title$, $m1_l2_t4_statement$**Коротко:** Найдите число полных коробок.

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
```$m1_l2_t4_statement$, $m1_l2_t4_starter$items = int(input())
box_size = int(input())
$m1_l2_t4_starter$, $m1_l2_t4_solution$items = int(input())
box_size = int(input())
print(items // box_size)
$m1_l2_t4_solution$, 1, 40, $m1_l2_t4_topic$Месяц 1. Python Core — Числа$m1_l2_t4_topic$, $m1_l2_t4_lang$python$m1_l2_t4_lang$, $m1_l2_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Нужна только целая часть деления.","Используй `//`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l2_t4_policy$::jsonb),
  ($m1_l2_t5_title$Остаток$m1_l2_t5_title$, $m1_l2_t5_statement$**Коротко:** Найдите остаток предметов.

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
```$m1_l2_t5_statement$, $m1_l2_t5_starter$items = int(input())
box_size = int(input())
$m1_l2_t5_starter$, $m1_l2_t5_solution$items = int(input())
box_size = int(input())
print(items % box_size)
$m1_l2_t5_solution$, 1, 40, $m1_l2_t5_topic$Месяц 1. Python Core — Числа$m1_l2_t5_topic$, $m1_l2_t5_lang$python$m1_l2_t5_lang$, $m1_l2_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Остаток от деления даёт `%`.","Формула: `items % box_size`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l2_t5_policy$::jsonb),
  ($m1_l2_t6_title$Минуты$m1_l2_t6_title$, $m1_l2_t6_statement$**Коротко:** Переведите минуты в часы и минуты.

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
```$m1_l2_t6_statement$, $m1_l2_t6_starter$minutes = int(input())
$m1_l2_t6_starter$, $m1_l2_t6_solution$minutes = int(input())
hours = minutes // 60
rest = minutes % 60
print("Часы:", hours)
print("Минуты:", rest)
$m1_l2_t6_solution$, 2, 55, $m1_l2_t6_topic$Месяц 1. Python Core — Числа$m1_l2_t6_topic$, $m1_l2_t6_lang$python$m1_l2_t6_lang$, $m1_l2_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Часы: `minutes // 60`.","Остаток минут: `minutes % 60`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l2_t6_policy$::jsonb),
  ($m1_l2_t8_title$Скидка$m1_l2_t8_title$, $m1_l2_t8_statement$**Коротко:** Посчитайте цену со скидкой.

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
```$m1_l2_t8_statement$, $m1_l2_t8_starter$price = float(input())
discount = float(input())
$m1_l2_t8_starter$, $m1_l2_t8_solution$price = float(input())
discount = float(input())
result = price - price * discount / 100
print(result)
$m1_l2_t8_solution$, 2, 55, $m1_l2_t8_topic$Месяц 1. Python Core — Числа$m1_l2_t8_topic$, $m1_l2_t8_lang$python$m1_l2_t8_lang$, $m1_l2_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Скидка в деньгах: `price * discount / 100`.","Новая цена: `price - ...`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l2_t8_policy$::jsonb),
  ($m1_l2_t10_title$Среднее$m1_l2_t10_title$, $m1_l2_t10_statement$**Коротко:** Найдите среднее трёх чисел.

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
```$m1_l2_t10_statement$, $m1_l2_t10_starter$a = float(input())
b = float(input())
c = float(input())
$m1_l2_t10_starter$, $m1_l2_t10_solution$a = float(input())
b = float(input())
c = float(input())
avg = (a + b + c) / 3
print(round(avg, 2))
$m1_l2_t10_solution$, 2, 55, $m1_l2_t10_topic$Месяц 1. Python Core — Числа$m1_l2_t10_topic$, $m1_l2_t10_lang$python$m1_l2_t10_lang$, $m1_l2_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Среднее: `(a + b + c) / 3`.","Используй `round(value, 2)`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l2_t10_policy$::jsonb),
  ($m1_l2_t11_title$Формула$m1_l2_t11_title$, $m1_l2_t11_statement$**Коротко:** Соберите формулу покупки.

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
```$m1_l2_t11_statement$, $m1_l2_t11_starter$price = float(input())
count = int(input())
discount = float(input())
delivery = float(input())
$m1_l2_t11_starter$, $m1_l2_t11_solution$price = float(input())
count = int(input())
discount = float(input())
delivery = float(input())
subtotal = price * count
total = subtotal - subtotal * discount / 100 + delivery
print(round(total, 2))
$m1_l2_t11_solution$, 2, 65, $m1_l2_t11_topic$Месяц 1. Python Core — Числа$m1_l2_t11_topic$, $m1_l2_t11_lang$python$m1_l2_t11_lang$, $m1_l2_t11_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сначала найди сумму без скидки.","Скидка: `subtotal * discount / 100`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l2_t11_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l2_ttitle_2$Скобки$m1_l2_ttitle_2$,
    $m1_l2_ttitle_4$Целое деление$m1_l2_ttitle_4$,
    $m1_l2_ttitle_5$Остаток$m1_l2_ttitle_5$,
    $m1_l2_ttitle_6$Минуты$m1_l2_ttitle_6$,
    $m1_l2_ttitle_8$Скидка$m1_l2_ttitle_8$,
    $m1_l2_ttitle_10$Среднее$m1_l2_ttitle_10$,
    $m1_l2_ttitle_11$Формула$m1_l2_ttitle_11$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l2_test_2_1_title$Скобки$m1_l2_test_2_1_title$, $m1_l2_test_2_1_input$2
3
4$m1_l2_test_2_1_input$, $m1_l2_test_2_1_expected$20$m1_l2_test_2_1_expected$, FALSE, 1),
  ($m1_l2_test_2_2_title$Скобки$m1_l2_test_2_2_title$, $m1_l2_test_2_2_input$10
5
2$m1_l2_test_2_2_input$, $m1_l2_test_2_2_expected$30$m1_l2_test_2_2_expected$, TRUE, 2),
  ($m1_l2_test_2_3_title$Скобки$m1_l2_test_2_3_title$, $m1_l2_test_2_3_input$0
7
3$m1_l2_test_2_3_input$, $m1_l2_test_2_3_expected$21$m1_l2_test_2_3_expected$, TRUE, 3),
  ($m1_l2_test_4_1_title$Целое деление$m1_l2_test_4_1_title$, $m1_l2_test_4_1_input$17
5$m1_l2_test_4_1_input$, $m1_l2_test_4_1_expected$3$m1_l2_test_4_1_expected$, FALSE, 1),
  ($m1_l2_test_4_2_title$Целое деление$m1_l2_test_4_2_title$, $m1_l2_test_4_2_input$20
4$m1_l2_test_4_2_input$, $m1_l2_test_4_2_expected$5$m1_l2_test_4_2_expected$, TRUE, 2),
  ($m1_l2_test_4_3_title$Целое деление$m1_l2_test_4_3_title$, $m1_l2_test_4_3_input$3
10$m1_l2_test_4_3_input$, $m1_l2_test_4_3_expected$0$m1_l2_test_4_3_expected$, TRUE, 3),
  ($m1_l2_test_5_1_title$Остаток$m1_l2_test_5_1_title$, $m1_l2_test_5_1_input$17
5$m1_l2_test_5_1_input$, $m1_l2_test_5_1_expected$2$m1_l2_test_5_1_expected$, FALSE, 1),
  ($m1_l2_test_5_2_title$Остаток$m1_l2_test_5_2_title$, $m1_l2_test_5_2_input$20
4$m1_l2_test_5_2_input$, $m1_l2_test_5_2_expected$0$m1_l2_test_5_2_expected$, TRUE, 2),
  ($m1_l2_test_5_3_title$Остаток$m1_l2_test_5_3_title$, $m1_l2_test_5_3_input$3
10$m1_l2_test_5_3_input$, $m1_l2_test_5_3_expected$3$m1_l2_test_5_3_expected$, TRUE, 3),
  ($m1_l2_test_6_1_title$Минуты$m1_l2_test_6_1_title$, $m1_l2_test_6_1_input$125$m1_l2_test_6_1_input$, $m1_l2_test_6_1_expected$Часы: 2
Минуты: 5$m1_l2_test_6_1_expected$, FALSE, 1),
  ($m1_l2_test_6_2_title$Минуты$m1_l2_test_6_2_title$, $m1_l2_test_6_2_input$60$m1_l2_test_6_2_input$, $m1_l2_test_6_2_expected$Часы: 1
Минуты: 0$m1_l2_test_6_2_expected$, TRUE, 2),
  ($m1_l2_test_6_3_title$Минуты$m1_l2_test_6_3_title$, $m1_l2_test_6_3_input$59$m1_l2_test_6_3_input$, $m1_l2_test_6_3_expected$Часы: 0
Минуты: 59$m1_l2_test_6_3_expected$, TRUE, 3),
  ($m1_l2_test_8_1_title$Скидка$m1_l2_test_8_1_title$, $m1_l2_test_8_1_input$1000
10$m1_l2_test_8_1_input$, $m1_l2_test_8_1_expected$900.0$m1_l2_test_8_1_expected$, FALSE, 1),
  ($m1_l2_test_8_2_title$Скидка$m1_l2_test_8_2_title$, $m1_l2_test_8_2_input$500
25$m1_l2_test_8_2_input$, $m1_l2_test_8_2_expected$375.0$m1_l2_test_8_2_expected$, TRUE, 2),
  ($m1_l2_test_8_3_title$Скидка$m1_l2_test_8_3_title$, $m1_l2_test_8_3_input$1200
0$m1_l2_test_8_3_input$, $m1_l2_test_8_3_expected$1200.0$m1_l2_test_8_3_expected$, TRUE, 3),
  ($m1_l2_test_10_1_title$Среднее$m1_l2_test_10_1_title$, $m1_l2_test_10_1_input$1
2
3$m1_l2_test_10_1_input$, $m1_l2_test_10_1_expected$2.0$m1_l2_test_10_1_expected$, FALSE, 1),
  ($m1_l2_test_10_2_title$Среднее$m1_l2_test_10_2_title$, $m1_l2_test_10_2_input$10
20
21$m1_l2_test_10_2_input$, $m1_l2_test_10_2_expected$17.0$m1_l2_test_10_2_expected$, TRUE, 2),
  ($m1_l2_test_10_3_title$Среднее$m1_l2_test_10_3_title$, $m1_l2_test_10_3_input$1
1
2$m1_l2_test_10_3_input$, $m1_l2_test_10_3_expected$1.33$m1_l2_test_10_3_expected$, TRUE, 3),
  ($m1_l2_test_11_1_title$Формула$m1_l2_test_11_1_title$, $m1_l2_test_11_1_input$200
3
10
50$m1_l2_test_11_1_input$, $m1_l2_test_11_1_expected$590.0$m1_l2_test_11_1_expected$, FALSE, 1),
  ($m1_l2_test_11_2_title$Формула$m1_l2_test_11_2_title$, $m1_l2_test_11_2_input$100
2
0
30$m1_l2_test_11_2_input$, $m1_l2_test_11_2_expected$230.0$m1_l2_test_11_2_expected$, TRUE, 2),
  ($m1_l2_test_11_3_title$Формула$m1_l2_test_11_3_title$, $m1_l2_test_11_3_input$99.9
3
5
0$m1_l2_test_11_3_input$, $m1_l2_test_11_3_expected$284.72$m1_l2_test_11_3_expected$, TRUE, 3)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l2_b1_type$theory$m1_l2_b1_type$, $m1_l2_b1_title$Операции$m1_l2_b1_title$, $m1_l2_b1_content$В Python можно считать с помощью операторов:

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
```$m1_l2_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l2_b2_type$practice$m1_l2_b2_type$, $m1_l2_b2_title$Скобки$m1_l2_b2_title$, $m1_l2_b2_content$**Коротко:** Вычислите выражение со скобками.

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
```$m1_l2_b2_content$, $m1_l2_b2_task_title$Скобки$m1_l2_b2_task_title$, NULL::jsonb),
  (3, $m1_l2_b3_type$theory$m1_l2_b3_type$, $m1_l2_b3_title$Деление$m1_l2_b3_title$, $m1_l2_b3_content$Обычное деление `/` возвращает дробное число:
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
```$m1_l2_b3_content$, NULL, NULL::jsonb),
  (4, $m1_l2_b4_type$practice$m1_l2_b4_type$, $m1_l2_b4_title$Целое деление$m1_l2_b4_title$, $m1_l2_b4_content$**Коротко:** Найдите число полных коробок.

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
```$m1_l2_b4_content$, $m1_l2_b4_task_title$Целое деление$m1_l2_b4_task_title$, NULL::jsonb),
  (5, $m1_l2_b5_type$practice$m1_l2_b5_type$, $m1_l2_b5_title$Остаток$m1_l2_b5_title$, $m1_l2_b5_content$**Коротко:** Найдите остаток предметов.

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
```$m1_l2_b5_content$, $m1_l2_b5_task_title$Остаток$m1_l2_b5_task_title$, NULL::jsonb),
  (6, $m1_l2_b6_type$practice$m1_l2_b6_type$, $m1_l2_b6_title$Минуты$m1_l2_b6_title$, $m1_l2_b6_content$**Коротко:** Переведите минуты в часы и минуты.

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
```$m1_l2_b6_content$, $m1_l2_b6_task_title$Минуты$m1_l2_b6_task_title$, NULL::jsonb),
  (7, $m1_l2_b7_type$theory$m1_l2_b7_type$, $m1_l2_b7_title$float$m1_l2_b7_title$, $m1_l2_b7_content$`float` — дробное число.

```python
price = float(input())
```

Используй `float`, если во вводе может быть число с точкой:
```text
12.5
```$m1_l2_b7_content$, NULL, NULL::jsonb),
  (8, $m1_l2_b8_type$practice$m1_l2_b8_type$, $m1_l2_b8_title$Скидка$m1_l2_b8_title$, $m1_l2_b8_content$**Коротко:** Посчитайте цену со скидкой.

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
```$m1_l2_b8_content$, $m1_l2_b8_task_title$Скидка$m1_l2_b8_task_title$, NULL::jsonb),
  (9, $m1_l2_b9_type$theory$m1_l2_b9_type$, $m1_l2_b9_title$Округление$m1_l2_b9_title$, $m1_l2_b9_content$`round(number, 2)` округляет число до двух знаков после точки.

```python
value = 12.3456
print(round(value, 2))  # 12.35
```

На этом уроке не требуем денежный формат `690.00`. Достаточно обычного вывода Python.$m1_l2_b9_content$, NULL, NULL::jsonb),
  (10, $m1_l2_b10_type$practice$m1_l2_b10_type$, $m1_l2_b10_title$Среднее$m1_l2_b10_title$, $m1_l2_b10_content$**Коротко:** Найдите среднее трёх чисел.

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
```$m1_l2_b10_content$, $m1_l2_b10_task_title$Среднее$m1_l2_b10_task_title$, NULL::jsonb),
  (11, $m1_l2_b11_type$practice$m1_l2_b11_type$, $m1_l2_b11_title$Формула$m1_l2_b11_title$, $m1_l2_b11_content$**Коротко:** Соберите формулу покупки.

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
```$m1_l2_b11_content$, $m1_l2_b11_task_title$Формула$m1_l2_b11_task_title$, NULL::jsonb),
  (12, $m1_l2_b12_type$quiz$m1_l2_b12_type$, $m1_l2_b12_title$Итог$m1_l2_b12_title$, $m1_l2_b12_content$### Вопрос

Что выведет `17 % 5`?

### Варианты

1. 3

2. 2

3. 5

4. 17$m1_l2_b12_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 3: Условия
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 3
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 3
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l3_t2_title$Пароль$m1_l3_t2_title$, $m1_l3_t2_statement$**Коротко:** Проверьте пароль.

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
```$m1_l3_t2_statement$, $m1_l3_t2_starter$password = input()
$m1_l3_t2_starter$, $m1_l3_t2_solution$password = input()
if password == "python":
    print("Доступ открыт")
else:
    print("Доступ закрыт")
$m1_l3_t2_solution$, 1, 45, $m1_l3_t2_topic$Месяц 1. Python Core — Условия$m1_l3_t2_topic$, $m1_l3_t2_lang$python$m1_l3_t2_lang$, $m1_l3_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Для проверки равенства используй `==`.","Нужны `if` и `else`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l3_t2_policy$::jsonb),
  ($m1_l3_t4_title$Возраст$m1_l3_t4_title$, $m1_l3_t4_statement$**Коротко:** Проверьте совершеннолетие.

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
```$m1_l3_t4_statement$, $m1_l3_t4_starter$age = int(input())
$m1_l3_t4_starter$, $m1_l3_t4_solution$age = int(input())
if age >= 18:
    print("Можно")
else:
    print("Нельзя")
$m1_l3_t4_solution$, 1, 45, $m1_l3_t4_topic$Месяц 1. Python Core — Условия$m1_l3_t4_topic$, $m1_l3_t4_lang$python$m1_l3_t4_lang$, $m1_l3_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Проверка: `age >= 18`.","Не забудь `else`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l3_t4_policy$::jsonb),
  ($m1_l3_t6_title$Оценка$m1_l3_t6_title$, $m1_l3_t6_statement$**Коротко:** Определите результат по баллам.

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
```$m1_l3_t6_statement$, $m1_l3_t6_starter$score = int(input())
$m1_l3_t6_starter$, $m1_l3_t6_solution$score = int(input())
if score >= 90:
    print("Отлично")
elif score >= 70:
    print("Хорошо")
else:
    print("Повторить")
$m1_l3_t6_solution$, 2, 55, $m1_l3_t6_topic$Месяц 1. Python Core — Условия$m1_l3_t6_topic$, $m1_l3_t6_lang$python$m1_l3_t6_lang$, $m1_l3_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сначала проверяй 90+.","Потом 70+, затем `else`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l3_t6_policy$::jsonb),
  ($m1_l3_t8_title$Скидка$m1_l3_t8_title$, $m1_l3_t8_statement$**Коротко:** Определите скидку по сумме.

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
```$m1_l3_t8_statement$, $m1_l3_t8_starter$amount = int(input())
$m1_l3_t8_starter$, $m1_l3_t8_solution$amount = int(input())
if amount >= 5000:
    print("10%")
elif amount >= 1000:
    print("5%")
else:
    print("0%")
$m1_l3_t8_solution$, 2, 55, $m1_l3_t8_topic$Месяц 1. Python Core — Условия$m1_l3_t8_topic$, $m1_l3_t8_lang$python$m1_l3_t8_lang$, $m1_l3_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Начни с проверки `amount >= 5000`.","Потом проверь `amount >= 1000`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l3_t8_policy$::jsonb),
  ($m1_l3_t9_title$Чётность$m1_l3_t9_title$, $m1_l3_t9_statement$**Коротко:** Проверьте чётность числа.

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
```$m1_l3_t9_statement$, $m1_l3_t9_starter$number = int(input())
$m1_l3_t9_starter$, $m1_l3_t9_solution$number = int(input())
if number % 2 == 0:
    print("Чётное")
else:
    print("Нечётное")
$m1_l3_t9_solution$, 2, 55, $m1_l3_t9_topic$Месяц 1. Python Core — Условия$m1_l3_t9_topic$, $m1_l3_t9_lang$python$m1_l3_t9_lang$, $m1_l3_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Используй остаток от деления на 2.","Чётное число: `number % 2 == 0`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l3_t9_policy$::jsonb),
  ($m1_l3_t10_title$Ошибка =$m1_l3_t10_title$, $m1_l3_t10_statement$**Коротко:** Исправьте сравнение.

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
```$m1_l3_t10_statement$, $m1_l3_t10_starter$$m1_l3_t10_starter$, $m1_l3_t10_solution$age = int(input())
if age == 18:
    print("Ровно 18")
else:
    print("Другое")
$m1_l3_t10_solution$, 2, 45, $m1_l3_t10_topic$Месяц 1. Python Core — Условия$m1_l3_t10_topic$, $m1_l3_t10_lang$python$m1_l3_t10_lang$, $m1_l3_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["`=` — присваивание.","Для сравнения нужен `==`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l3_t10_policy$::jsonb),
  ($m1_l3_t11_title$Категория$m1_l3_t11_title$, $m1_l3_t11_statement$**Коротко:** Определите возрастную категорию.

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
```$m1_l3_t11_statement$, $m1_l3_t11_starter$age = int(input())
$m1_l3_t11_starter$, $m1_l3_t11_solution$age = int(input())
if age < 7:
    print("Ребёнок")
elif age < 18:
    print("Школьник")
elif age < 60:
    print("Взрослый")
else:
    print("Пенсионер")
$m1_l3_t11_solution$, 2, 70, $m1_l3_t11_topic$Месяц 1. Python Core — Условия$m1_l3_t11_topic$, $m1_l3_t11_lang$python$m1_l3_t11_lang$, $m1_l3_t11_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Проверяй категории сверху вниз.","Можно идти от меньшего к большему: `< 7`, `< 18`, `< 60`, `else`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l3_t11_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l3_ttitle_2$Пароль$m1_l3_ttitle_2$,
    $m1_l3_ttitle_4$Возраст$m1_l3_ttitle_4$,
    $m1_l3_ttitle_6$Оценка$m1_l3_ttitle_6$,
    $m1_l3_ttitle_8$Скидка$m1_l3_ttitle_8$,
    $m1_l3_ttitle_9$Чётность$m1_l3_ttitle_9$,
    $m1_l3_ttitle_10$Ошибка =$m1_l3_ttitle_10$,
    $m1_l3_ttitle_11$Категория$m1_l3_ttitle_11$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l3_test_2_1_title$Пароль$m1_l3_test_2_1_title$, $m1_l3_test_2_1_input$python$m1_l3_test_2_1_input$, $m1_l3_test_2_1_expected$Доступ открыт$m1_l3_test_2_1_expected$, FALSE, 1),
  ($m1_l3_test_2_2_title$Пароль$m1_l3_test_2_2_title$, $m1_l3_test_2_2_input$qwerty$m1_l3_test_2_2_input$, $m1_l3_test_2_2_expected$Доступ закрыт$m1_l3_test_2_2_expected$, TRUE, 2),
  ($m1_l3_test_2_3_title$Пароль$m1_l3_test_2_3_title$, $m1_l3_test_2_3_input$Python$m1_l3_test_2_3_input$, $m1_l3_test_2_3_expected$Доступ закрыт$m1_l3_test_2_3_expected$, TRUE, 3),
  ($m1_l3_test_4_1_title$Возраст$m1_l3_test_4_1_title$, $m1_l3_test_4_1_input$18$m1_l3_test_4_1_input$, $m1_l3_test_4_1_expected$Можно$m1_l3_test_4_1_expected$, FALSE, 1),
  ($m1_l3_test_4_2_title$Возраст$m1_l3_test_4_2_title$, $m1_l3_test_4_2_input$17$m1_l3_test_4_2_input$, $m1_l3_test_4_2_expected$Нельзя$m1_l3_test_4_2_expected$, TRUE, 2),
  ($m1_l3_test_4_3_title$Возраст$m1_l3_test_4_3_title$, $m1_l3_test_4_3_input$0$m1_l3_test_4_3_input$, $m1_l3_test_4_3_expected$Нельзя$m1_l3_test_4_3_expected$, TRUE, 3),
  ($m1_l3_test_4_4_title$Возраст$m1_l3_test_4_4_title$, $m1_l3_test_4_4_input$99$m1_l3_test_4_4_input$, $m1_l3_test_4_4_expected$Можно$m1_l3_test_4_4_expected$, TRUE, 4),
  ($m1_l3_test_6_1_title$Оценка$m1_l3_test_6_1_title$, $m1_l3_test_6_1_input$95$m1_l3_test_6_1_input$, $m1_l3_test_6_1_expected$Отлично$m1_l3_test_6_1_expected$, FALSE, 1),
  ($m1_l3_test_6_2_title$Оценка$m1_l3_test_6_2_title$, $m1_l3_test_6_2_input$90$m1_l3_test_6_2_input$, $m1_l3_test_6_2_expected$Отлично$m1_l3_test_6_2_expected$, TRUE, 2),
  ($m1_l3_test_6_3_title$Оценка$m1_l3_test_6_3_title$, $m1_l3_test_6_3_input$89$m1_l3_test_6_3_input$, $m1_l3_test_6_3_expected$Хорошо$m1_l3_test_6_3_expected$, TRUE, 3),
  ($m1_l3_test_6_4_title$Оценка$m1_l3_test_6_4_title$, $m1_l3_test_6_4_input$70$m1_l3_test_6_4_input$, $m1_l3_test_6_4_expected$Хорошо$m1_l3_test_6_4_expected$, TRUE, 4),
  ($m1_l3_test_6_5_title$Оценка$m1_l3_test_6_5_title$, $m1_l3_test_6_5_input$69$m1_l3_test_6_5_input$, $m1_l3_test_6_5_expected$Повторить$m1_l3_test_6_5_expected$, TRUE, 5),
  ($m1_l3_test_8_1_title$Скидка$m1_l3_test_8_1_title$, $m1_l3_test_8_1_input$999$m1_l3_test_8_1_input$, $m1_l3_test_8_1_expected$0%$m1_l3_test_8_1_expected$, FALSE, 1),
  ($m1_l3_test_8_2_title$Скидка$m1_l3_test_8_2_title$, $m1_l3_test_8_2_input$1000$m1_l3_test_8_2_input$, $m1_l3_test_8_2_expected$5%$m1_l3_test_8_2_expected$, TRUE, 2),
  ($m1_l3_test_8_3_title$Скидка$m1_l3_test_8_3_title$, $m1_l3_test_8_3_input$4999$m1_l3_test_8_3_input$, $m1_l3_test_8_3_expected$5%$m1_l3_test_8_3_expected$, TRUE, 3),
  ($m1_l3_test_8_4_title$Скидка$m1_l3_test_8_4_title$, $m1_l3_test_8_4_input$5000$m1_l3_test_8_4_input$, $m1_l3_test_8_4_expected$10%$m1_l3_test_8_4_expected$, TRUE, 4),
  ($m1_l3_test_9_1_title$Чётность$m1_l3_test_9_1_title$, $m1_l3_test_9_1_input$10$m1_l3_test_9_1_input$, $m1_l3_test_9_1_expected$Чётное$m1_l3_test_9_1_expected$, FALSE, 1),
  ($m1_l3_test_9_2_title$Чётность$m1_l3_test_9_2_title$, $m1_l3_test_9_2_input$7$m1_l3_test_9_2_input$, $m1_l3_test_9_2_expected$Нечётное$m1_l3_test_9_2_expected$, TRUE, 2),
  ($m1_l3_test_9_3_title$Чётность$m1_l3_test_9_3_title$, $m1_l3_test_9_3_input$0$m1_l3_test_9_3_input$, $m1_l3_test_9_3_expected$Чётное$m1_l3_test_9_3_expected$, TRUE, 3),
  ($m1_l3_test_9_4_title$Чётность$m1_l3_test_9_4_title$, $m1_l3_test_9_4_input$-3$m1_l3_test_9_4_input$, $m1_l3_test_9_4_expected$Нечётное$m1_l3_test_9_4_expected$, TRUE, 4),
  ($m1_l3_test_10_1_title$Ошибка =$m1_l3_test_10_1_title$, $m1_l3_test_10_1_input$18$m1_l3_test_10_1_input$, $m1_l3_test_10_1_expected$Ровно 18$m1_l3_test_10_1_expected$, FALSE, 1),
  ($m1_l3_test_10_2_title$Ошибка =$m1_l3_test_10_2_title$, $m1_l3_test_10_2_input$19$m1_l3_test_10_2_input$, $m1_l3_test_10_2_expected$Другое$m1_l3_test_10_2_expected$, TRUE, 2),
  ($m1_l3_test_10_3_title$Ошибка =$m1_l3_test_10_3_title$, $m1_l3_test_10_3_input$17$m1_l3_test_10_3_input$, $m1_l3_test_10_3_expected$Другое$m1_l3_test_10_3_expected$, TRUE, 3),
  ($m1_l3_test_11_1_title$Категория$m1_l3_test_11_1_title$, $m1_l3_test_11_1_input$6$m1_l3_test_11_1_input$, $m1_l3_test_11_1_expected$Ребёнок$m1_l3_test_11_1_expected$, FALSE, 1),
  ($m1_l3_test_11_2_title$Категория$m1_l3_test_11_2_title$, $m1_l3_test_11_2_input$7$m1_l3_test_11_2_input$, $m1_l3_test_11_2_expected$Школьник$m1_l3_test_11_2_expected$, TRUE, 2),
  ($m1_l3_test_11_3_title$Категория$m1_l3_test_11_3_title$, $m1_l3_test_11_3_input$17$m1_l3_test_11_3_input$, $m1_l3_test_11_3_expected$Школьник$m1_l3_test_11_3_expected$, TRUE, 3),
  ($m1_l3_test_11_4_title$Категория$m1_l3_test_11_4_title$, $m1_l3_test_11_4_input$18$m1_l3_test_11_4_input$, $m1_l3_test_11_4_expected$Взрослый$m1_l3_test_11_4_expected$, TRUE, 4),
  ($m1_l3_test_11_5_title$Категория$m1_l3_test_11_5_title$, $m1_l3_test_11_5_input$59$m1_l3_test_11_5_input$, $m1_l3_test_11_5_expected$Взрослый$m1_l3_test_11_5_expected$, TRUE, 5),
  ($m1_l3_test_11_6_title$Категория$m1_l3_test_11_6_title$, $m1_l3_test_11_6_input$60$m1_l3_test_11_6_input$, $m1_l3_test_11_6_expected$Пенсионер$m1_l3_test_11_6_expected$, TRUE, 6)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l3_b1_type$theory$m1_l3_b1_type$, $m1_l3_b1_title$Сравнения$m1_l3_b1_title$, $m1_l3_b1_content$Условия позволяют программе принимать решения.

Операторы сравнения:

| Оператор | Значение |
|---|---|
| `==` | равно |
| `!=` | не равно |
| `>` | больше |
| `<` | меньше |
| `>=` | больше или равно |
| `<=` | меньше или равно |$m1_l3_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l3_b2_type$practice$m1_l3_b2_type$, $m1_l3_b2_title$Пароль$m1_l3_b2_title$, $m1_l3_b2_content$**Коротко:** Проверьте пароль.

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
```$m1_l3_b2_content$, $m1_l3_b2_task_title$Пароль$m1_l3_b2_task_title$, NULL::jsonb),
  (3, $m1_l3_b3_type$theory$m1_l3_b3_type$, $m1_l3_b3_title$if else$m1_l3_b3_title$, $m1_l3_b3_content$`if` проверяет условие. `else` выполняется, если условие ложно.

```python
age = int(input())

if age >= 18:
    print("Можно")
else:
    print("Нельзя")
```

Отступы обязательны: строки внутри `if` сдвигаются вправо.$m1_l3_b3_content$, NULL, NULL::jsonb),
  (4, $m1_l3_b4_type$practice$m1_l3_b4_type$, $m1_l3_b4_title$Возраст$m1_l3_b4_title$, $m1_l3_b4_content$**Коротко:** Проверьте совершеннолетие.

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
```$m1_l3_b4_content$, $m1_l3_b4_task_title$Возраст$m1_l3_b4_task_title$, NULL::jsonb),
  (5, $m1_l3_b5_type$theory$m1_l3_b5_type$, $m1_l3_b5_title$elif$m1_l3_b5_title$, $m1_l3_b5_content$`elif` нужен, когда вариантов больше двух.

```python
score = int(input())

if score >= 90:
    print("Отлично")
elif score >= 70:
    print("Хорошо")
else:
    print("Нужно повторить")
```

Python проверяет условия сверху вниз.$m1_l3_b5_content$, NULL, NULL::jsonb),
  (6, $m1_l3_b6_type$practice$m1_l3_b6_type$, $m1_l3_b6_title$Оценка$m1_l3_b6_title$, $m1_l3_b6_content$**Коротко:** Определите результат по баллам.

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
```$m1_l3_b6_content$, $m1_l3_b6_task_title$Оценка$m1_l3_b6_task_title$, NULL::jsonb),
  (7, $m1_l3_b7_type$theory$m1_l3_b7_type$, $m1_l3_b7_title$Границы$m1_l3_b7_title$, $m1_l3_b7_content$В задачах с условиями важны границы.

Если сказано `от 18`, проверка должна включать 18:
```python
age >= 18
```

Если сказано `меньше 18`, проверка:
```python
age < 18
```$m1_l3_b7_content$, NULL, NULL::jsonb),
  (8, $m1_l3_b8_type$practice$m1_l3_b8_type$, $m1_l3_b8_title$Скидка$m1_l3_b8_title$, $m1_l3_b8_content$**Коротко:** Определите скидку по сумме.

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
```$m1_l3_b8_content$, $m1_l3_b8_task_title$Скидка$m1_l3_b8_task_title$, NULL::jsonb),
  (9, $m1_l3_b9_type$practice$m1_l3_b9_type$, $m1_l3_b9_title$Чётность$m1_l3_b9_title$, $m1_l3_b9_content$**Коротко:** Проверьте чётность числа.

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
```$m1_l3_b9_content$, $m1_l3_b9_task_title$Чётность$m1_l3_b9_task_title$, NULL::jsonb),
  (10, $m1_l3_b10_type$practice$m1_l3_b10_type$, $m1_l3_b10_title$Ошибка =$m1_l3_b10_title$, $m1_l3_b10_content$**Коротко:** Исправьте сравнение.

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
```$m1_l3_b10_content$, $m1_l3_b10_task_title$Ошибка =$m1_l3_b10_task_title$, NULL::jsonb),
  (11, $m1_l3_b11_type$practice$m1_l3_b11_type$, $m1_l3_b11_title$Категория$m1_l3_b11_title$, $m1_l3_b11_content$**Коротко:** Определите возрастную категорию.

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
```$m1_l3_b11_content$, $m1_l3_b11_task_title$Категория$m1_l3_b11_task_title$, NULL::jsonb),
  (12, $m1_l3_b12_type$quiz$m1_l3_b12_type$, $m1_l3_b12_title$Итог$m1_l3_b12_title$, $m1_l3_b12_content$### Вопрос

Чем отличается `=` от `==`?

### Варианты

1. Ничем

2. `=` сравнивает, `==` присваивает

3. `=` присваивает, `==` сравнивает

4. Оба выводят текст$m1_l3_b12_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 4: Логика
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 4
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 4
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l4_t2_title$Диапазон$m1_l4_t2_title$, $m1_l4_t2_statement$**Коротко:** Проверьте число в диапазоне.

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
```$m1_l4_t2_statement$, $m1_l4_t2_starter$number = int(input())
$m1_l4_t2_starter$, $m1_l4_t2_solution$number = int(input())
if number >= 1 and number <= 10:
    print("Внутри")
else:
    print("Снаружи")
$m1_l4_t2_solution$, 1, 45, $m1_l4_t2_topic$Месяц 1. Python Core — Логика$m1_l4_t2_topic$, $m1_l4_t2_lang$python$m1_l4_t2_lang$, $m1_l4_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Нужны две проверки.","Используй `and`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l4_t2_policy$::jsonb),
  ($m1_l4_t3_title$Два условия$m1_l4_t3_title$, $m1_l4_t3_statement$**Коротко:** Проверьте возраст и балл.

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
```$m1_l4_t3_statement$, $m1_l4_t3_starter$age = int(input())
score = int(input())
$m1_l4_t3_starter$, $m1_l4_t3_solution$age = int(input())
score = int(input())
if age >= 18 and score >= 70:
    print("Допущен")
else:
    print("Не допущен")
$m1_l4_t3_solution$, 2, 55, $m1_l4_t3_topic$Месяц 1. Python Core — Логика$m1_l4_t3_topic$, $m1_l4_t3_lang$python$m1_l4_t3_lang$, $m1_l4_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Оба условия должны быть верны.","Используй `and`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l4_t3_policy$::jsonb),
  ($m1_l4_t5_title$Роль$m1_l4_t5_title$, $m1_l4_t5_statement$**Коротко:** Проверьте роль пользователя.

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
```$m1_l4_t5_statement$, $m1_l4_t5_starter$role = input()
$m1_l4_t5_starter$, $m1_l4_t5_solution$role = input()
if role == "admin" or role == "moderator":
    print("Доступ")
else:
    print("Нет доступа")
$m1_l4_t5_solution$, 2, 55, $m1_l4_t5_topic$Месяц 1. Python Core — Логика$m1_l4_t5_topic$, $m1_l4_t5_lang$python$m1_l4_t5_lang$, $m1_l4_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Нужен `or`.","Пиши `role == ...` с обеих сторон `or`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l4_t5_policy$::jsonb),
  ($m1_l4_t7_title$Запрет$m1_l4_t7_title$, $m1_l4_t7_statement$**Коротко:** Проверьте блокировку.

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
```$m1_l4_t7_statement$, $m1_l4_t7_starter$blocked = input()
$m1_l4_t7_starter$, $m1_l4_t7_solution$blocked = input()
is_blocked = blocked == "yes"
if not is_blocked:
    print("Можно")
else:
    print("Нельзя")
$m1_l4_t7_solution$, 2, 50, $m1_l4_t7_topic$Месяц 1. Python Core — Логика$m1_l4_t7_topic$, $m1_l4_t7_lang$python$m1_l4_t7_lang$, $m1_l4_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сравни ввод с `yes`.","Можно решить через `if blocked == \"no\"` или через `not`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l4_t7_policy$::jsonb),
  ($m1_l4_t8_title$Ошибка or$m1_l4_t8_title$, $m1_l4_t8_statement$**Коротко:** Исправьте условие с or.

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
```$m1_l4_t8_statement$, $m1_l4_t8_starter$$m1_l4_t8_starter$, $m1_l4_t8_solution$role = input()
if role == "admin" or role == "moderator":
    print("Доступ")
else:
    print("Нет доступа")
$m1_l4_t8_solution$, 2, 45, $m1_l4_t8_topic$Месяц 1. Python Core — Логика$m1_l4_t8_topic$, $m1_l4_t8_lang$python$m1_l4_t8_lang$, $m1_l4_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Строка `\"moderator\"` сама по себе считается истинной.","Нужно написать `role == \"moderator\"`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l4_t8_policy$::jsonb),
  ($m1_l4_t9_title$Заявка$m1_l4_t9_title$, $m1_l4_t9_statement$**Коротко:** Примите решение по заявке.

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
```$m1_l4_t9_statement$, $m1_l4_t9_starter$age = int(input())
income = int(input())
debt = input()
$m1_l4_t9_starter$, $m1_l4_t9_solution$age = int(input())
income = int(input())
debt = input()
if age >= 18 and income >= 30000 and debt == "no":
    print("Одобрено")
else:
    print("Отказ")
$m1_l4_t9_solution$, 3, 75, $m1_l4_t9_topic$Месяц 1. Python Core — Логика$m1_l4_t9_topic$, $m1_l4_t9_lang$python$m1_l4_t9_lang$, $m1_l4_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Все три условия должны быть верны.","Долга нет: `debt == \"no\"`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l4_t9_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l4_ttitle_2$Диапазон$m1_l4_ttitle_2$,
    $m1_l4_ttitle_3$Два условия$m1_l4_ttitle_3$,
    $m1_l4_ttitle_5$Роль$m1_l4_ttitle_5$,
    $m1_l4_ttitle_7$Запрет$m1_l4_ttitle_7$,
    $m1_l4_ttitle_8$Ошибка or$m1_l4_ttitle_8$,
    $m1_l4_ttitle_9$Заявка$m1_l4_ttitle_9$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l4_test_2_1_title$Диапазон$m1_l4_test_2_1_title$, $m1_l4_test_2_1_input$1$m1_l4_test_2_1_input$, $m1_l4_test_2_1_expected$Внутри$m1_l4_test_2_1_expected$, FALSE, 1),
  ($m1_l4_test_2_2_title$Диапазон$m1_l4_test_2_2_title$, $m1_l4_test_2_2_input$10$m1_l4_test_2_2_input$, $m1_l4_test_2_2_expected$Внутри$m1_l4_test_2_2_expected$, TRUE, 2),
  ($m1_l4_test_2_3_title$Диапазон$m1_l4_test_2_3_title$, $m1_l4_test_2_3_input$0$m1_l4_test_2_3_input$, $m1_l4_test_2_3_expected$Снаружи$m1_l4_test_2_3_expected$, TRUE, 3),
  ($m1_l4_test_2_4_title$Диапазон$m1_l4_test_2_4_title$, $m1_l4_test_2_4_input$11$m1_l4_test_2_4_input$, $m1_l4_test_2_4_expected$Снаружи$m1_l4_test_2_4_expected$, TRUE, 4),
  ($m1_l4_test_3_1_title$Два условия$m1_l4_test_3_1_title$, $m1_l4_test_3_1_input$18
70$m1_l4_test_3_1_input$, $m1_l4_test_3_1_expected$Допущен$m1_l4_test_3_1_expected$, FALSE, 1),
  ($m1_l4_test_3_2_title$Два условия$m1_l4_test_3_2_title$, $m1_l4_test_3_2_input$17
90$m1_l4_test_3_2_input$, $m1_l4_test_3_2_expected$Не допущен$m1_l4_test_3_2_expected$, TRUE, 2),
  ($m1_l4_test_3_3_title$Два условия$m1_l4_test_3_3_title$, $m1_l4_test_3_3_input$20
69$m1_l4_test_3_3_input$, $m1_l4_test_3_3_expected$Не допущен$m1_l4_test_3_3_expected$, TRUE, 3),
  ($m1_l4_test_3_4_title$Два условия$m1_l4_test_3_4_title$, $m1_l4_test_3_4_input$25
100$m1_l4_test_3_4_input$, $m1_l4_test_3_4_expected$Допущен$m1_l4_test_3_4_expected$, TRUE, 4),
  ($m1_l4_test_5_1_title$Роль$m1_l4_test_5_1_title$, $m1_l4_test_5_1_input$admin$m1_l4_test_5_1_input$, $m1_l4_test_5_1_expected$Доступ$m1_l4_test_5_1_expected$, FALSE, 1),
  ($m1_l4_test_5_2_title$Роль$m1_l4_test_5_2_title$, $m1_l4_test_5_2_input$moderator$m1_l4_test_5_2_input$, $m1_l4_test_5_2_expected$Доступ$m1_l4_test_5_2_expected$, TRUE, 2),
  ($m1_l4_test_5_3_title$Роль$m1_l4_test_5_3_title$, $m1_l4_test_5_3_input$user$m1_l4_test_5_3_input$, $m1_l4_test_5_3_expected$Нет доступа$m1_l4_test_5_3_expected$, TRUE, 3),
  ($m1_l4_test_7_1_title$Запрет$m1_l4_test_7_1_title$, $m1_l4_test_7_1_input$no$m1_l4_test_7_1_input$, $m1_l4_test_7_1_expected$Можно$m1_l4_test_7_1_expected$, FALSE, 1),
  ($m1_l4_test_7_2_title$Запрет$m1_l4_test_7_2_title$, $m1_l4_test_7_2_input$yes$m1_l4_test_7_2_input$, $m1_l4_test_7_2_expected$Нельзя$m1_l4_test_7_2_expected$, TRUE, 2),
  ($m1_l4_test_8_1_title$Ошибка or$m1_l4_test_8_1_title$, $m1_l4_test_8_1_input$admin$m1_l4_test_8_1_input$, $m1_l4_test_8_1_expected$Доступ$m1_l4_test_8_1_expected$, FALSE, 1),
  ($m1_l4_test_8_2_title$Ошибка or$m1_l4_test_8_2_title$, $m1_l4_test_8_2_input$moderator$m1_l4_test_8_2_input$, $m1_l4_test_8_2_expected$Доступ$m1_l4_test_8_2_expected$, TRUE, 2),
  ($m1_l4_test_8_3_title$Ошибка or$m1_l4_test_8_3_title$, $m1_l4_test_8_3_input$user$m1_l4_test_8_3_input$, $m1_l4_test_8_3_expected$Нет доступа$m1_l4_test_8_3_expected$, TRUE, 3),
  ($m1_l4_test_9_1_title$Заявка$m1_l4_test_9_1_title$, $m1_l4_test_9_1_input$20
50000
no$m1_l4_test_9_1_input$, $m1_l4_test_9_1_expected$Одобрено$m1_l4_test_9_1_expected$, FALSE, 1),
  ($m1_l4_test_9_2_title$Заявка$m1_l4_test_9_2_title$, $m1_l4_test_9_2_input$17
50000
no$m1_l4_test_9_2_input$, $m1_l4_test_9_2_expected$Отказ$m1_l4_test_9_2_expected$, TRUE, 2),
  ($m1_l4_test_9_3_title$Заявка$m1_l4_test_9_3_title$, $m1_l4_test_9_3_input$20
29999
no$m1_l4_test_9_3_input$, $m1_l4_test_9_3_expected$Отказ$m1_l4_test_9_3_expected$, TRUE, 3),
  ($m1_l4_test_9_4_title$Заявка$m1_l4_test_9_4_title$, $m1_l4_test_9_4_input$20
50000
yes$m1_l4_test_9_4_input$, $m1_l4_test_9_4_expected$Отказ$m1_l4_test_9_4_expected$, TRUE, 4)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l4_b1_type$theory$m1_l4_b1_type$, $m1_l4_b1_title$and or not$m1_l4_b1_title$, $m1_l4_b1_content$Логические операторы помогают объединять условия.

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
```$m1_l4_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l4_b2_type$practice$m1_l4_b2_type$, $m1_l4_b2_title$Диапазон$m1_l4_b2_title$, $m1_l4_b2_content$**Коротко:** Проверьте число в диапазоне.

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
```$m1_l4_b2_content$, $m1_l4_b2_task_title$Диапазон$m1_l4_b2_task_title$, NULL::jsonb),
  (3, $m1_l4_b3_type$practice$m1_l4_b3_type$, $m1_l4_b3_title$Два условия$m1_l4_b3_title$, $m1_l4_b3_content$**Коротко:** Проверьте возраст и балл.

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
```$m1_l4_b3_content$, $m1_l4_b3_task_title$Два условия$m1_l4_b3_task_title$, NULL::jsonb),
  (4, $m1_l4_b4_type$theory$m1_l4_b4_type$, $m1_l4_b4_title$or$m1_l4_b4_title$, $m1_l4_b4_content$`or` подходит, когда достаточно одного верного условия.

```python
role = input()
if role == "admin" or role == "moderator":
    print("Доступ")
```

Каждую проверку нужно писать полностью.$m1_l4_b4_content$, NULL, NULL::jsonb),
  (5, $m1_l4_b5_type$practice$m1_l4_b5_type$, $m1_l4_b5_title$Роль$m1_l4_b5_title$, $m1_l4_b5_content$**Коротко:** Проверьте роль пользователя.

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
```$m1_l4_b5_content$, $m1_l4_b5_task_title$Роль$m1_l4_b5_task_title$, NULL::jsonb),
  (6, $m1_l4_b6_type$theory$m1_l4_b6_type$, $m1_l4_b6_title$not$m1_l4_b6_title$, $m1_l4_b6_content$`not` меняет значение условия на противоположное.

```python
is_blocked = input() == "yes"
if not is_blocked:
    print("Можно войти")
```$m1_l4_b6_content$, NULL, NULL::jsonb),
  (7, $m1_l4_b7_type$practice$m1_l4_b7_type$, $m1_l4_b7_title$Запрет$m1_l4_b7_title$, $m1_l4_b7_content$**Коротко:** Проверьте блокировку.

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
```$m1_l4_b7_content$, $m1_l4_b7_task_title$Запрет$m1_l4_b7_task_title$, NULL::jsonb),
  (8, $m1_l4_b8_type$practice$m1_l4_b8_type$, $m1_l4_b8_title$Ошибка or$m1_l4_b8_title$, $m1_l4_b8_content$**Коротко:** Исправьте условие с or.

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
```$m1_l4_b8_content$, $m1_l4_b8_task_title$Ошибка or$m1_l4_b8_task_title$, NULL::jsonb),
  (9, $m1_l4_b9_type$practice$m1_l4_b9_type$, $m1_l4_b9_title$Заявка$m1_l4_b9_title$, $m1_l4_b9_content$**Коротко:** Примите решение по заявке.

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
```$m1_l4_b9_content$, $m1_l4_b9_task_title$Заявка$m1_l4_b9_task_title$, NULL::jsonb),
  (10, $m1_l4_b10_type$quiz$m1_l4_b10_type$, $m1_l4_b10_title$Итог$m1_l4_b10_title$, $m1_l4_b10_content$### Вопрос

Как правильно проверить роль admin или moderator?

### Варианты

1. `role == "admin" or "moderator"`

2. `role == "admin" or role == "moderator"`

3. `role = "admin" or role = "moderator"`

4. `role == admin or moderator`$m1_l4_b10_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 5: while
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 5
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 5
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l5_t2_title$От 1 до N$m1_l5_t2_title$, $m1_l5_t2_statement$**Коротко:** Выведите числа от 1 до n.

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
```$m1_l5_t2_statement$, $m1_l5_t2_starter$n = int(input())
number = 1
$m1_l5_t2_starter$, $m1_l5_t2_solution$n = int(input())
number = 1
while number <= n:
    print(number)
    number = number + 1
$m1_l5_t2_solution$, 1, 50, $m1_l5_t2_topic$Месяц 1. Python Core — while$m1_l5_t2_topic$, $m1_l5_t2_lang$python$m1_l5_t2_lang$, $m1_l5_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Цикл: `while number <= n`.","Внутри цикла увеличивай `number` на 1."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l5_t2_policy$::jsonb),
  ($m1_l5_t4_title$Сумма N$m1_l5_t4_title$, $m1_l5_t4_statement$**Коротко:** Найдите сумму от 1 до n.

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
```$m1_l5_t4_statement$, $m1_l5_t4_starter$n = int(input())
total = 0
$m1_l5_t4_starter$, $m1_l5_t4_solution$n = int(input())
total = 0
number = 1
while number <= n:
    total = total + number
    number = number + 1
print(total)
$m1_l5_t4_solution$, 2, 60, $m1_l5_t4_topic$Месяц 1. Python Core — while$m1_l5_t4_topic$, $m1_l5_t4_lang$python$m1_l5_t4_lang$, $m1_l5_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Нужен счётчик от 1 до n.","На каждом шаге добавляй счётчик к `total`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l5_t4_policy$::jsonb),
  ($m1_l5_t5_title$До нуля$m1_l5_t5_title$, $m1_l5_t5_statement$**Коротко:** Суммируйте числа до нуля.

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
```$m1_l5_t5_statement$, $m1_l5_t5_starter$total = 0
number = int(input())
$m1_l5_t5_starter$, $m1_l5_t5_solution$total = 0
number = int(input())
while number != 0:
    total = total + number
    number = int(input())
print(total)
$m1_l5_t5_solution$, 2, 65, $m1_l5_t5_topic$Месяц 1. Python Core — while$m1_l5_t5_topic$, $m1_l5_t5_lang$python$m1_l5_t5_lang$, $m1_l5_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Пока число не равно 0, добавляй его к сумме.","В конце цикла считывай следующее число."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l5_t5_policy$::jsonb),
  ($m1_l5_t7_title$Пароль$m1_l5_t7_title$, $m1_l5_t7_statement$**Коротко:** Повторяйте ввод до верного пароля.

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
```$m1_l5_t7_statement$, $m1_l5_t7_starter$while True:
    password = input()
$m1_l5_t7_starter$, $m1_l5_t7_solution$while True:
    password = input()
    if password == "python":
        print("Вход выполнен")
        break
$m1_l5_t7_solution$, 2, 60, $m1_l5_t7_topic$Месяц 1. Python Core — while$m1_l5_t7_topic$, $m1_l5_t7_lang$python$m1_l5_t7_lang$, $m1_l5_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Используй бесконечный цикл.","Если пароль верный, выведи сообщение и сделай `break`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l5_t7_policy$::jsonb),
  ($m1_l5_t8_title$Бесконечный$m1_l5_t8_title$, $m1_l5_t8_statement$**Коротко:** Исправьте бесконечный цикл.

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
```$m1_l5_t8_statement$, $m1_l5_t8_starter$$m1_l5_t8_starter$, $m1_l5_t8_solution$number = 1
while number <= 5:
    print(number)
    number = number + 1
$m1_l5_t8_solution$, 2, 45, $m1_l5_t8_topic$Месяц 1. Python Core — while$m1_l5_t8_topic$, $m1_l5_t8_lang$python$m1_l5_t8_lang$, $m1_l5_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Переменная `number` не меняется.","Добавь `number = number + 1` внутри цикла."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l5_t8_policy$::jsonb),
  ($m1_l5_t9_title$Угадай$m1_l5_t9_title$, $m1_l5_t9_statement$**Коротко:** Найдите число по попыткам.

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
```$m1_l5_t9_statement$, $m1_l5_t9_starter$secret = int(input())
$m1_l5_t9_starter$, $m1_l5_t9_solution$secret = int(input())
while True:
    guess = int(input())
    if guess == secret:
        print("Угадал")
        break
    else:
        print("Мимо")
$m1_l5_t9_solution$, 3, 75, $m1_l5_t9_topic$Месяц 1. Python Core — while$m1_l5_t9_topic$, $m1_l5_t9_lang$python$m1_l5_t9_lang$, $m1_l5_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Считывай попытки в цикле.","При совпадении печатай `Угадал` и делай `break`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l5_t9_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l5_ttitle_2$От 1 до N$m1_l5_ttitle_2$,
    $m1_l5_ttitle_4$Сумма N$m1_l5_ttitle_4$,
    $m1_l5_ttitle_5$До нуля$m1_l5_ttitle_5$,
    $m1_l5_ttitle_7$Пароль$m1_l5_ttitle_7$,
    $m1_l5_ttitle_8$Бесконечный$m1_l5_ttitle_8$,
    $m1_l5_ttitle_9$Угадай$m1_l5_ttitle_9$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l5_test_2_1_title$От 1 до N$m1_l5_test_2_1_title$, $m1_l5_test_2_1_input$3$m1_l5_test_2_1_input$, $m1_l5_test_2_1_expected$1
2
3$m1_l5_test_2_1_expected$, FALSE, 1),
  ($m1_l5_test_2_2_title$От 1 до N$m1_l5_test_2_2_title$, $m1_l5_test_2_2_input$1$m1_l5_test_2_2_input$, $m1_l5_test_2_2_expected$1$m1_l5_test_2_2_expected$, TRUE, 2),
  ($m1_l5_test_2_3_title$От 1 до N$m1_l5_test_2_3_title$, $m1_l5_test_2_3_input$5$m1_l5_test_2_3_input$, $m1_l5_test_2_3_expected$1
2
3
4
5$m1_l5_test_2_3_expected$, TRUE, 3),
  ($m1_l5_test_4_1_title$Сумма N$m1_l5_test_4_1_title$, $m1_l5_test_4_1_input$5$m1_l5_test_4_1_input$, $m1_l5_test_4_1_expected$15$m1_l5_test_4_1_expected$, FALSE, 1),
  ($m1_l5_test_4_2_title$Сумма N$m1_l5_test_4_2_title$, $m1_l5_test_4_2_input$1$m1_l5_test_4_2_input$, $m1_l5_test_4_2_expected$1$m1_l5_test_4_2_expected$, TRUE, 2),
  ($m1_l5_test_4_3_title$Сумма N$m1_l5_test_4_3_title$, $m1_l5_test_4_3_input$10$m1_l5_test_4_3_input$, $m1_l5_test_4_3_expected$55$m1_l5_test_4_3_expected$, TRUE, 3),
  ($m1_l5_test_5_1_title$До нуля$m1_l5_test_5_1_title$, $m1_l5_test_5_1_input$1
2
3
0$m1_l5_test_5_1_input$, $m1_l5_test_5_1_expected$6$m1_l5_test_5_1_expected$, FALSE, 1),
  ($m1_l5_test_5_2_title$До нуля$m1_l5_test_5_2_title$, $m1_l5_test_5_2_input$0$m1_l5_test_5_2_input$, $m1_l5_test_5_2_expected$0$m1_l5_test_5_2_expected$, TRUE, 2),
  ($m1_l5_test_5_3_title$До нуля$m1_l5_test_5_3_title$, $m1_l5_test_5_3_input$10
-5
0$m1_l5_test_5_3_input$, $m1_l5_test_5_3_expected$5$m1_l5_test_5_3_expected$, TRUE, 3),
  ($m1_l5_test_7_1_title$Пароль$m1_l5_test_7_1_title$, $m1_l5_test_7_1_input$123
qwerty
python$m1_l5_test_7_1_input$, $m1_l5_test_7_1_expected$Вход выполнен$m1_l5_test_7_1_expected$, FALSE, 1),
  ($m1_l5_test_7_2_title$Пароль$m1_l5_test_7_2_title$, $m1_l5_test_7_2_input$python$m1_l5_test_7_2_input$, $m1_l5_test_7_2_expected$Вход выполнен$m1_l5_test_7_2_expected$, TRUE, 2),
  ($m1_l5_test_8_1_title$Бесконечный$m1_l5_test_8_1_title$, $m1_l5_test_8_1_input$$m1_l5_test_8_1_input$, $m1_l5_test_8_1_expected$1
2
3
4
5$m1_l5_test_8_1_expected$, FALSE, 1),
  ($m1_l5_test_9_1_title$Угадай$m1_l5_test_9_1_title$, $m1_l5_test_9_1_input$5
1
2
5$m1_l5_test_9_1_input$, $m1_l5_test_9_1_expected$Мимо
Мимо
Угадал$m1_l5_test_9_1_expected$, FALSE, 1),
  ($m1_l5_test_9_2_title$Угадай$m1_l5_test_9_2_title$, $m1_l5_test_9_2_input$3
3$m1_l5_test_9_2_input$, $m1_l5_test_9_2_expected$Угадал$m1_l5_test_9_2_expected$, TRUE, 2),
  ($m1_l5_test_9_3_title$Угадай$m1_l5_test_9_3_title$, $m1_l5_test_9_3_input$10
1
10$m1_l5_test_9_3_input$, $m1_l5_test_9_3_expected$Мимо
Угадал$m1_l5_test_9_3_expected$, TRUE, 3)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l5_b1_type$theory$m1_l5_b1_type$, $m1_l5_b1_title$while$m1_l5_b1_title$, $m1_l5_b1_content$`while` повторяет код, пока условие истинно.

```python
number = 1
while number <= 5:
    print(number)
    number = number + 1
```

Важно менять переменную внутри цикла. Иначе цикл может стать бесконечным.$m1_l5_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l5_b2_type$practice$m1_l5_b2_type$, $m1_l5_b2_title$От 1 до N$m1_l5_b2_title$, $m1_l5_b2_content$**Коротко:** Выведите числа от 1 до n.

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
```$m1_l5_b2_content$, $m1_l5_b2_task_title$От 1 до N$m1_l5_b2_task_title$, NULL::jsonb),
  (3, $m1_l5_b3_type$theory$m1_l5_b3_type$, $m1_l5_b3_title$Счётчик$m1_l5_b3_title$, $m1_l5_b3_content$Для суммы часто используют накопитель.

```python
total = 0
number = 1
while number <= 5:
    total = total + number
    number = number + 1
print(total)
```

`total` хранит промежуточный результат.$m1_l5_b3_content$, NULL, NULL::jsonb),
  (4, $m1_l5_b4_type$practice$m1_l5_b4_type$, $m1_l5_b4_title$Сумма N$m1_l5_b4_title$, $m1_l5_b4_content$**Коротко:** Найдите сумму от 1 до n.

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
```$m1_l5_b4_content$, $m1_l5_b4_task_title$Сумма N$m1_l5_b4_task_title$, NULL::jsonb),
  (5, $m1_l5_b5_type$practice$m1_l5_b5_type$, $m1_l5_b5_title$До нуля$m1_l5_b5_title$, $m1_l5_b5_content$**Коротко:** Суммируйте числа до нуля.

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
```$m1_l5_b5_content$, $m1_l5_b5_task_title$До нуля$m1_l5_b5_task_title$, NULL::jsonb),
  (6, $m1_l5_b6_type$theory$m1_l5_b6_type$, $m1_l5_b6_title$break$m1_l5_b6_title$, $m1_l5_b6_content$`break` останавливает цикл досрочно.

```python
while True:
    text = input()
    if text == "stop":
        break
```

`while True` всегда требует условия выхода через `break`.$m1_l5_b6_content$, NULL, NULL::jsonb),
  (7, $m1_l5_b7_type$practice$m1_l5_b7_type$, $m1_l5_b7_title$Пароль$m1_l5_b7_title$, $m1_l5_b7_content$**Коротко:** Повторяйте ввод до верного пароля.

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
```$m1_l5_b7_content$, $m1_l5_b7_task_title$Пароль$m1_l5_b7_task_title$, NULL::jsonb),
  (8, $m1_l5_b8_type$practice$m1_l5_b8_type$, $m1_l5_b8_title$Бесконечный$m1_l5_b8_title$, $m1_l5_b8_content$**Коротко:** Исправьте бесконечный цикл.

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
```$m1_l5_b8_content$, $m1_l5_b8_task_title$Бесконечный$m1_l5_b8_task_title$, NULL::jsonb),
  (9, $m1_l5_b9_type$practice$m1_l5_b9_type$, $m1_l5_b9_title$Угадай$m1_l5_b9_title$, $m1_l5_b9_content$**Коротко:** Найдите число по попыткам.

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
```$m1_l5_b9_content$, $m1_l5_b9_task_title$Угадай$m1_l5_b9_task_title$, NULL::jsonb),
  (10, $m1_l5_b10_type$quiz$m1_l5_b10_type$, $m1_l5_b10_title$Итог$m1_l5_b10_title$, $m1_l5_b10_content$### Вопрос

Что чаще всего вызывает бесконечный цикл?

### Варианты

1. `print()` внутри цикла

2. Переменная условия не меняется

3. Использование `int()`

4. Пустая строка$m1_l5_b10_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 6: for и range
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 6
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 6
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l6_t2_title$От 1 до N$m1_l6_t2_title$, $m1_l6_t2_statement$**Коротко:** Выведите числа через for.

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
```$m1_l6_t2_statement$, $m1_l6_t2_starter$n = int(input())
$m1_l6_t2_starter$, $m1_l6_t2_solution$n = int(input())
for i in range(1, n + 1):
    print(i)
$m1_l6_t2_solution$, 1, 45, $m1_l6_t2_topic$Месяц 1. Python Core — for и range$m1_l6_t2_topic$, $m1_l6_t2_lang$python$m1_l6_t2_lang$, $m1_l6_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Используй `range(1, n + 1)`.","Правая граница не включается."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l6_t2_policy$::jsonb),
  ($m1_l6_t4_title$Повторить N$m1_l6_t4_title$, $m1_l6_t4_statement$**Коротко:** Выведите слово несколько раз.

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
```$m1_l6_t4_statement$, $m1_l6_t4_starter$n = int(input())
word = input()
$m1_l6_t4_starter$, $m1_l6_t4_solution$n = int(input())
word = input()
for i in range(n):
    print(word)
$m1_l6_t4_solution$, 1, 45, $m1_l6_t4_topic$Месяц 1. Python Core — for и range$m1_l6_t4_topic$, $m1_l6_t4_lang$python$m1_l6_t4_lang$, $m1_l6_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Цикл можно написать `for i in range(n)`.","Индекс `i` можно не использовать."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l6_t4_policy$::jsonb),
  ($m1_l6_t5_title$Сумма чисел$m1_l6_t5_title$, $m1_l6_t5_statement$**Коротко:** Сложите n чисел.

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
```$m1_l6_t5_statement$, $m1_l6_t5_starter$n = int(input())
total = 0
$m1_l6_t5_starter$, $m1_l6_t5_solution$n = int(input())
total = 0
for i in range(n):
    number = int(input())
    total = total + number
print(total)
$m1_l6_t5_solution$, 2, 60, $m1_l6_t5_topic$Месяц 1. Python Core — for и range$m1_l6_t5_topic$, $m1_l6_t5_lang$python$m1_l6_t5_lang$, $m1_l6_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Цикл должен повториться `n` раз.","Внутри цикла считывай число и добавляй к `total`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l6_t5_policy$::jsonb),
  ($m1_l6_t6_title$Чётные$m1_l6_t6_title$, $m1_l6_t6_statement$**Коротко:** Выведите чётные от 1 до n.

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

```$m1_l6_t6_statement$, $m1_l6_t6_starter$n = int(input())
$m1_l6_t6_starter$, $m1_l6_t6_solution$n = int(input())
for i in range(2, n + 1, 2):
    print(i)
$m1_l6_t6_solution$, 2, 55, $m1_l6_t6_topic$Месяц 1. Python Core — for и range$m1_l6_t6_topic$, $m1_l6_t6_lang$python$m1_l6_t6_lang$, $m1_l6_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Можно идти от 2 с шагом 2.","`range(2, n + 1, 2)`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l6_t6_policy$::jsonb),
  ($m1_l6_t8_title$Максимум$m1_l6_t8_title$, $m1_l6_t8_statement$**Коротко:** Найдите максимум из n чисел.

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
```$m1_l6_t8_statement$, $m1_l6_t8_starter$n = int(input())
maximum = None
$m1_l6_t8_starter$, $m1_l6_t8_solution$n = int(input())
maximum = int(input())
for i in range(n - 1):
    number = int(input())
    if number > maximum:
        maximum = number
print(maximum)
$m1_l6_t8_solution$, 3, 70, $m1_l6_t8_topic$Месяц 1. Python Core — for и range$m1_l6_t8_topic$, $m1_l6_t8_lang$python$m1_l6_t8_lang$, $m1_l6_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Считай первое число отдельно или используй `None`.","Если новое число больше максимума, обнови максимум."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l6_t8_policy$::jsonb),
  ($m1_l6_t9_title$Количество$m1_l6_t9_title$, $m1_l6_t9_statement$**Коротко:** Посчитайте числа больше 10.

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
```$m1_l6_t9_statement$, $m1_l6_t9_starter$n = int(input())
count = 0
$m1_l6_t9_starter$, $m1_l6_t9_solution$n = int(input())
count = 0
for i in range(n):
    number = int(input())
    if number > 10:
        count = count + 1
print(count)
$m1_l6_t9_solution$, 2, 60, $m1_l6_t9_topic$Месяц 1. Python Core — for и range$m1_l6_t9_topic$, $m1_l6_t9_lang$python$m1_l6_t9_lang$, $m1_l6_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Нужен счётчик `count`.","Увеличивай его, если `number > 10`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l6_t9_policy$::jsonb),
  ($m1_l6_t10_title$Таблица$m1_l6_t10_title$, $m1_l6_t10_statement$**Коротко:** Выведите таблицу умножения.

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
```$m1_l6_t10_statement$, $m1_l6_t10_starter$n = int(input())
$m1_l6_t10_starter$, $m1_l6_t10_solution$n = int(input())
for i in range(1, 11):
    print(n, "x", i, "=", n * i)
$m1_l6_t10_solution$, 3, 75, $m1_l6_t10_topic$Месяц 1. Python Core — for и range$m1_l6_t10_topic$, $m1_l6_t10_lang$python$m1_l6_t10_lang$, $m1_l6_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Цикл: `for i in range(1, 11)`.","Результат: `n * i`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l6_t10_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l6_ttitle_2$От 1 до N$m1_l6_ttitle_2$,
    $m1_l6_ttitle_4$Повторить N$m1_l6_ttitle_4$,
    $m1_l6_ttitle_5$Сумма чисел$m1_l6_ttitle_5$,
    $m1_l6_ttitle_6$Чётные$m1_l6_ttitle_6$,
    $m1_l6_ttitle_8$Максимум$m1_l6_ttitle_8$,
    $m1_l6_ttitle_9$Количество$m1_l6_ttitle_9$,
    $m1_l6_ttitle_10$Таблица$m1_l6_ttitle_10$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l6_test_2_1_title$От 1 до N$m1_l6_test_2_1_title$, $m1_l6_test_2_1_input$3$m1_l6_test_2_1_input$, $m1_l6_test_2_1_expected$1
2
3$m1_l6_test_2_1_expected$, FALSE, 1),
  ($m1_l6_test_2_2_title$От 1 до N$m1_l6_test_2_2_title$, $m1_l6_test_2_2_input$1$m1_l6_test_2_2_input$, $m1_l6_test_2_2_expected$1$m1_l6_test_2_2_expected$, TRUE, 2),
  ($m1_l6_test_2_3_title$От 1 до N$m1_l6_test_2_3_title$, $m1_l6_test_2_3_input$5$m1_l6_test_2_3_input$, $m1_l6_test_2_3_expected$1
2
3
4
5$m1_l6_test_2_3_expected$, TRUE, 3),
  ($m1_l6_test_4_1_title$Повторить N$m1_l6_test_4_1_title$, $m1_l6_test_4_1_input$3
код$m1_l6_test_4_1_input$, $m1_l6_test_4_1_expected$код
код
код$m1_l6_test_4_1_expected$, FALSE, 1),
  ($m1_l6_test_4_2_title$Повторить N$m1_l6_test_4_2_title$, $m1_l6_test_4_2_input$1
Python$m1_l6_test_4_2_input$, $m1_l6_test_4_2_expected$Python$m1_l6_test_4_2_expected$, TRUE, 2),
  ($m1_l6_test_4_3_title$Повторить N$m1_l6_test_4_3_title$, $m1_l6_test_4_3_input$0
text$m1_l6_test_4_3_input$, $m1_l6_test_4_3_expected$$m1_l6_test_4_3_expected$, TRUE, 3),
  ($m1_l6_test_5_1_title$Сумма чисел$m1_l6_test_5_1_title$, $m1_l6_test_5_1_input$3
10
20
30$m1_l6_test_5_1_input$, $m1_l6_test_5_1_expected$60$m1_l6_test_5_1_expected$, FALSE, 1),
  ($m1_l6_test_5_2_title$Сумма чисел$m1_l6_test_5_2_title$, $m1_l6_test_5_2_input$1
5$m1_l6_test_5_2_input$, $m1_l6_test_5_2_expected$5$m1_l6_test_5_2_expected$, TRUE, 2),
  ($m1_l6_test_5_3_title$Сумма чисел$m1_l6_test_5_3_title$, $m1_l6_test_5_3_input$4
1
-1
2
-2$m1_l6_test_5_3_input$, $m1_l6_test_5_3_expected$0$m1_l6_test_5_3_expected$, TRUE, 3),
  ($m1_l6_test_6_1_title$Чётные$m1_l6_test_6_1_title$, $m1_l6_test_6_1_input$6$m1_l6_test_6_1_input$, $m1_l6_test_6_1_expected$2
4
6$m1_l6_test_6_1_expected$, FALSE, 1),
  ($m1_l6_test_6_2_title$Чётные$m1_l6_test_6_2_title$, $m1_l6_test_6_2_input$1$m1_l6_test_6_2_input$, $m1_l6_test_6_2_expected$$m1_l6_test_6_2_expected$, TRUE, 2),
  ($m1_l6_test_6_3_title$Чётные$m1_l6_test_6_3_title$, $m1_l6_test_6_3_input$2$m1_l6_test_6_3_input$, $m1_l6_test_6_3_expected$2$m1_l6_test_6_3_expected$, TRUE, 3),
  ($m1_l6_test_6_4_title$Чётные$m1_l6_test_6_4_title$, $m1_l6_test_6_4_input$7$m1_l6_test_6_4_input$, $m1_l6_test_6_4_expected$2
4
6$m1_l6_test_6_4_expected$, TRUE, 4),
  ($m1_l6_test_8_1_title$Максимум$m1_l6_test_8_1_title$, $m1_l6_test_8_1_input$3
5
9
1$m1_l6_test_8_1_input$, $m1_l6_test_8_1_expected$9$m1_l6_test_8_1_expected$, FALSE, 1),
  ($m1_l6_test_8_2_title$Максимум$m1_l6_test_8_2_title$, $m1_l6_test_8_2_input$1
-5$m1_l6_test_8_2_input$, $m1_l6_test_8_2_expected$-5$m1_l6_test_8_2_expected$, TRUE, 2),
  ($m1_l6_test_8_3_title$Максимум$m1_l6_test_8_3_title$, $m1_l6_test_8_3_input$4
-10
-3
-7
-1$m1_l6_test_8_3_input$, $m1_l6_test_8_3_expected$-1$m1_l6_test_8_3_expected$, TRUE, 3),
  ($m1_l6_test_9_1_title$Количество$m1_l6_test_9_1_title$, $m1_l6_test_9_1_input$5
1
11
10
20
30$m1_l6_test_9_1_input$, $m1_l6_test_9_1_expected$3$m1_l6_test_9_1_expected$, FALSE, 1),
  ($m1_l6_test_9_2_title$Количество$m1_l6_test_9_2_title$, $m1_l6_test_9_2_input$3
1
2
3$m1_l6_test_9_2_input$, $m1_l6_test_9_2_expected$0$m1_l6_test_9_2_expected$, TRUE, 2),
  ($m1_l6_test_9_3_title$Количество$m1_l6_test_9_3_title$, $m1_l6_test_9_3_input$2
11
12$m1_l6_test_9_3_input$, $m1_l6_test_9_3_expected$2$m1_l6_test_9_3_expected$, TRUE, 3),
  ($m1_l6_test_10_1_title$Таблица$m1_l6_test_10_1_title$, $m1_l6_test_10_1_input$1$m1_l6_test_10_1_input$, $m1_l6_test_10_1_expected$1 x 1 = 1
1 x 2 = 2
1 x 3 = 3
1 x 4 = 4
1 x 5 = 5
1 x 6 = 6
1 x 7 = 7
1 x 8 = 8
1 x 9 = 9
1 x 10 = 10$m1_l6_test_10_1_expected$, FALSE, 1),
  ($m1_l6_test_10_2_title$Таблица$m1_l6_test_10_2_title$, $m1_l6_test_10_2_input$3$m1_l6_test_10_2_input$, $m1_l6_test_10_2_expected$3 x 1 = 3
3 x 2 = 6
3 x 3 = 9
3 x 4 = 12
3 x 5 = 15
3 x 6 = 18
3 x 7 = 21
3 x 8 = 24
3 x 9 = 27
3 x 10 = 30$m1_l6_test_10_2_expected$, TRUE, 2)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l6_b1_type$theory$m1_l6_b1_type$, $m1_l6_b1_title$for range$m1_l6_b1_title$, $m1_l6_b1_content$`for` удобен, когда известно количество повторений.

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

`range(1, 5)` даёт числа 1, 2, 3, 4. Правая граница не включается.$m1_l6_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l6_b2_type$practice$m1_l6_b2_type$, $m1_l6_b2_title$От 1 до N$m1_l6_b2_title$, $m1_l6_b2_content$**Коротко:** Выведите числа через for.

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
```$m1_l6_b2_content$, $m1_l6_b2_task_title$От 1 до N$m1_l6_b2_task_title$, NULL::jsonb),
  (3, $m1_l6_b3_type$quiz$m1_l6_b3_type$, $m1_l6_b3_title$Правая граница$m1_l6_b3_title$, $m1_l6_b3_content$### Вопрос

Что выведет `range(1, 4)` в цикле?

### Варианты

1. 1 2 3

2. 1 2 3 4

3. 0 1 2 3

4. 4$m1_l6_b3_content$, NULL, NULL::jsonb),
  (4, $m1_l6_b4_type$practice$m1_l6_b4_type$, $m1_l6_b4_title$Повторить N$m1_l6_b4_title$, $m1_l6_b4_content$**Коротко:** Выведите слово несколько раз.

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
```$m1_l6_b4_content$, $m1_l6_b4_task_title$Повторить N$m1_l6_b4_task_title$, NULL::jsonb),
  (5, $m1_l6_b5_type$practice$m1_l6_b5_type$, $m1_l6_b5_title$Сумма чисел$m1_l6_b5_title$, $m1_l6_b5_content$**Коротко:** Сложите n чисел.

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
```$m1_l6_b5_content$, $m1_l6_b5_task_title$Сумма чисел$m1_l6_b5_task_title$, NULL::jsonb),
  (6, $m1_l6_b6_type$practice$m1_l6_b6_type$, $m1_l6_b6_title$Чётные$m1_l6_b6_title$, $m1_l6_b6_content$**Коротко:** Выведите чётные от 1 до n.

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

```$m1_l6_b6_content$, $m1_l6_b6_task_title$Чётные$m1_l6_b6_task_title$, NULL::jsonb),
  (7, $m1_l6_b7_type$theory$m1_l6_b7_type$, $m1_l6_b7_title$Ввод N чисел$m1_l6_b7_title$, $m1_l6_b7_content$Частый шаблон:

```python
n = int(input())
for i in range(n):
    number = int(input())
    # работа с number
```

Так считывают заранее известное количество чисел.$m1_l6_b7_content$, NULL, NULL::jsonb),
  (8, $m1_l6_b8_type$practice$m1_l6_b8_type$, $m1_l6_b8_title$Максимум$m1_l6_b8_title$, $m1_l6_b8_content$**Коротко:** Найдите максимум из n чисел.

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
```$m1_l6_b8_content$, $m1_l6_b8_task_title$Максимум$m1_l6_b8_task_title$, NULL::jsonb),
  (9, $m1_l6_b9_type$practice$m1_l6_b9_type$, $m1_l6_b9_title$Количество$m1_l6_b9_title$, $m1_l6_b9_content$**Коротко:** Посчитайте числа больше 10.

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
```$m1_l6_b9_content$, $m1_l6_b9_task_title$Количество$m1_l6_b9_task_title$, NULL::jsonb),
  (10, $m1_l6_b10_type$practice$m1_l6_b10_type$, $m1_l6_b10_title$Таблица$m1_l6_b10_title$, $m1_l6_b10_content$**Коротко:** Выведите таблицу умножения.

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
```$m1_l6_b10_content$, $m1_l6_b10_task_title$Таблица$m1_l6_b10_task_title$, NULL::jsonb),
  (11, $m1_l6_b11_type$quiz$m1_l6_b11_type$, $m1_l6_b11_title$Итог$m1_l6_b11_title$, $m1_l6_b11_content$### Вопрос

Почему для вывода от 1 до n пишут `range(1, n + 1)`?

### Варианты

1. Потому что range не включает правую границу

2. Потому что n нельзя использовать

3. Потому что for начинает с 1 всегда

4. Потому что print требует n + 1$m1_l6_b11_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 7: Строки
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 7
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 7
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l7_t2_title$Длина$m1_l7_t2_title$, $m1_l7_t2_statement$**Коротко:** Выведите длину строки.

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
```$m1_l7_t2_statement$, $m1_l7_t2_starter$text = input()
$m1_l7_t2_starter$, $m1_l7_t2_solution$text = input()
print(len(text))
$m1_l7_t2_solution$, 1, 40, $m1_l7_t2_topic$Месяц 1. Python Core — Строки$m1_l7_t2_topic$, $m1_l7_t2_lang$python$m1_l7_t2_lang$, $m1_l7_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Используй `len(text)`.","Пробелы тоже считаются символами."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l7_t2_policy$::jsonb),
  ($m1_l7_t4_title$Первый символ$m1_l7_t4_title$, $m1_l7_t4_statement$**Коротко:** Выведите первый символ строки.

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
```$m1_l7_t4_statement$, $m1_l7_t4_starter$text = input()
$m1_l7_t4_starter$, $m1_l7_t4_solution$text = input()
print(text[0])
$m1_l7_t4_solution$, 1, 40, $m1_l7_t4_topic$Месяц 1. Python Core — Строки$m1_l7_t4_topic$, $m1_l7_t4_lang$python$m1_l7_t4_lang$, $m1_l7_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Первый символ имеет индекс 0.","Используй `text[0]`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l7_t4_policy$::jsonb),
  ($m1_l7_t6_title$Первые N$m1_l7_t6_title$, $m1_l7_t6_statement$**Коротко:** Выведите первые n символов.

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
```$m1_l7_t6_statement$, $m1_l7_t6_starter$text = input()
n = int(input())
$m1_l7_t6_starter$, $m1_l7_t6_solution$text = input()
n = int(input())
print(text[:n])
$m1_l7_t6_solution$, 2, 50, $m1_l7_t6_topic$Месяц 1. Python Core — Строки$m1_l7_t6_topic$, $m1_l7_t6_lang$python$m1_l7_t6_lang$, $m1_l7_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Срез от начала: `text[:n]`.","Если n больше длины, Python просто вернёт всю строку."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l7_t6_policy$::jsonb),
  ($m1_l7_t8_title$Палиндром$m1_l7_t8_title$, $m1_l7_t8_statement$**Коротко:** Проверьте слово на палиндром.

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
```$m1_l7_t8_statement$, $m1_l7_t8_starter$word = input()
$m1_l7_t8_starter$, $m1_l7_t8_solution$word = input()
if word == word[::-1]:
    print("Да")
else:
    print("Нет")
$m1_l7_t8_solution$, 2, 60, $m1_l7_t8_topic$Месяц 1. Python Core — Строки$m1_l7_t8_topic$, $m1_l7_t8_lang$python$m1_l7_t8_lang$, $m1_l7_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Переверни слово через `word[::-1]`.","Сравни исходное и перевёрнутое слово."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l7_t8_policy$::jsonb),
  ($m1_l7_t10_title$Нормализация$m1_l7_t10_title$, $m1_l7_t10_statement$**Коротко:** Приведите строку к нижнему регистру.

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
```$m1_l7_t10_statement$, $m1_l7_t10_starter$text = input()
$m1_l7_t10_starter$, $m1_l7_t10_solution$text = input()
print(text.strip().lower())
$m1_l7_t10_solution$, 2, 55, $m1_l7_t10_topic$Месяц 1. Python Core — Строки$m1_l7_t10_topic$, $m1_l7_t10_lang$python$m1_l7_t10_lang$, $m1_l7_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сначала можно сделать `strip()`.","Потом `lower()`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l7_t10_policy$::jsonb),
  ($m1_l7_t11_title$Счёт букв$m1_l7_t11_title$, $m1_l7_t11_statement$**Коротко:** Посчитайте букву в строке.

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
```$m1_l7_t11_statement$, $m1_l7_t11_starter$text = input()
char = input()
$m1_l7_t11_starter$, $m1_l7_t11_solution$text = input()
char = input()
count = 0
for symbol in text:
    if symbol == char:
        count = count + 1
print(count)
$m1_l7_t11_solution$, 2, 60, $m1_l7_t11_topic$Месяц 1. Python Core — Строки$m1_l7_t11_topic$, $m1_l7_t11_lang$python$m1_l7_t11_lang$, $m1_l7_t11_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Перебери строку циклом `for`.","Увеличивай счётчик при совпадении."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l7_t11_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l7_ttitle_2$Длина$m1_l7_ttitle_2$,
    $m1_l7_ttitle_4$Первый символ$m1_l7_ttitle_4$,
    $m1_l7_ttitle_6$Первые N$m1_l7_ttitle_6$,
    $m1_l7_ttitle_8$Палиндром$m1_l7_ttitle_8$,
    $m1_l7_ttitle_10$Нормализация$m1_l7_ttitle_10$,
    $m1_l7_ttitle_11$Счёт букв$m1_l7_ttitle_11$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l7_test_2_1_title$Длина$m1_l7_test_2_1_title$, $m1_l7_test_2_1_input$Python$m1_l7_test_2_1_input$, $m1_l7_test_2_1_expected$6$m1_l7_test_2_1_expected$, FALSE, 1),
  ($m1_l7_test_2_2_title$Длина$m1_l7_test_2_2_title$, $m1_l7_test_2_2_input$код$m1_l7_test_2_2_input$, $m1_l7_test_2_2_expected$3$m1_l7_test_2_2_expected$, TRUE, 2),
  ($m1_l7_test_2_3_title$Длина$m1_l7_test_2_3_title$, $m1_l7_test_2_3_input$a b$m1_l7_test_2_3_input$, $m1_l7_test_2_3_expected$3$m1_l7_test_2_3_expected$, TRUE, 3),
  ($m1_l7_test_4_1_title$Первый символ$m1_l7_test_4_1_title$, $m1_l7_test_4_1_input$Python$m1_l7_test_4_1_input$, $m1_l7_test_4_1_expected$P$m1_l7_test_4_1_expected$, FALSE, 1),
  ($m1_l7_test_4_2_title$Первый символ$m1_l7_test_4_2_title$, $m1_l7_test_4_2_input$код$m1_l7_test_4_2_input$, $m1_l7_test_4_2_expected$к$m1_l7_test_4_2_expected$, TRUE, 2),
  ($m1_l7_test_4_3_title$Первый символ$m1_l7_test_4_3_title$, $m1_l7_test_4_3_input$A$m1_l7_test_4_3_input$, $m1_l7_test_4_3_expected$A$m1_l7_test_4_3_expected$, TRUE, 3),
  ($m1_l7_test_6_1_title$Первые N$m1_l7_test_6_1_title$, $m1_l7_test_6_1_input$Python
3$m1_l7_test_6_1_input$, $m1_l7_test_6_1_expected$Pyt$m1_l7_test_6_1_expected$, FALSE, 1),
  ($m1_l7_test_6_2_title$Первые N$m1_l7_test_6_2_title$, $m1_l7_test_6_2_input$abcdef
2$m1_l7_test_6_2_input$, $m1_l7_test_6_2_expected$ab$m1_l7_test_6_2_expected$, TRUE, 2),
  ($m1_l7_test_6_3_title$Первые N$m1_l7_test_6_3_title$, $m1_l7_test_6_3_input$hi
10$m1_l7_test_6_3_input$, $m1_l7_test_6_3_expected$hi$m1_l7_test_6_3_expected$, TRUE, 3),
  ($m1_l7_test_8_1_title$Палиндром$m1_l7_test_8_1_title$, $m1_l7_test_8_1_input$топот$m1_l7_test_8_1_input$, $m1_l7_test_8_1_expected$Да$m1_l7_test_8_1_expected$, FALSE, 1),
  ($m1_l7_test_8_2_title$Палиндром$m1_l7_test_8_2_title$, $m1_l7_test_8_2_input$python$m1_l7_test_8_2_input$, $m1_l7_test_8_2_expected$Нет$m1_l7_test_8_2_expected$, TRUE, 2),
  ($m1_l7_test_8_3_title$Палиндром$m1_l7_test_8_3_title$, $m1_l7_test_8_3_input$а$m1_l7_test_8_3_input$, $m1_l7_test_8_3_expected$Да$m1_l7_test_8_3_expected$, TRUE, 3),
  ($m1_l7_test_10_1_title$Нормализация$m1_l7_test_10_1_title$, $m1_l7_test_10_1_input$  PyThOn$m1_l7_test_10_1_input$, $m1_l7_test_10_1_expected$python$m1_l7_test_10_1_expected$, FALSE, 1),
  ($m1_l7_test_10_2_title$Нормализация$m1_l7_test_10_2_title$, $m1_l7_test_10_2_input$ CODE$m1_l7_test_10_2_input$, $m1_l7_test_10_2_expected$code$m1_l7_test_10_2_expected$, TRUE, 2),
  ($m1_l7_test_10_3_title$Нормализация$m1_l7_test_10_3_title$, $m1_l7_test_10_3_input$test$m1_l7_test_10_3_input$, $m1_l7_test_10_3_expected$test$m1_l7_test_10_3_expected$, TRUE, 3),
  ($m1_l7_test_11_1_title$Счёт букв$m1_l7_test_11_1_title$, $m1_l7_test_11_1_input$banana
a$m1_l7_test_11_1_input$, $m1_l7_test_11_1_expected$3$m1_l7_test_11_1_expected$, FALSE, 1),
  ($m1_l7_test_11_2_title$Счёт букв$m1_l7_test_11_2_title$, $m1_l7_test_11_2_input$hello
z$m1_l7_test_11_2_input$, $m1_l7_test_11_2_expected$0$m1_l7_test_11_2_expected$, TRUE, 2),
  ($m1_l7_test_11_3_title$Счёт букв$m1_l7_test_11_3_title$, $m1_l7_test_11_3_input$aaaa
a$m1_l7_test_11_3_input$, $m1_l7_test_11_3_expected$4$m1_l7_test_11_3_expected$, TRUE, 3)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l7_b1_type$theory$m1_l7_b1_type$, $m1_l7_b1_title$Строки$m1_l7_b1_title$, $m1_l7_b1_content$Строка — это текст. Её можно хранить в переменной:
```python
text = "Python"
```

`len(text)` возвращает длину строки.$m1_l7_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l7_b2_type$practice$m1_l7_b2_type$, $m1_l7_b2_title$Длина$m1_l7_b2_title$, $m1_l7_b2_content$**Коротко:** Выведите длину строки.

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
```$m1_l7_b2_content$, $m1_l7_b2_task_title$Длина$m1_l7_b2_task_title$, NULL::jsonb),
  (3, $m1_l7_b3_type$theory$m1_l7_b3_type$, $m1_l7_b3_title$Индекс$m1_l7_b3_title$, $m1_l7_b3_content$У символов строки есть индексы. Первый символ имеет индекс 0.

```python
text = "Python"
print(text[0])  # P
print(text[1])  # y
```$m1_l7_b3_content$, NULL, NULL::jsonb),
  (4, $m1_l7_b4_type$practice$m1_l7_b4_type$, $m1_l7_b4_title$Первый символ$m1_l7_b4_title$, $m1_l7_b4_content$**Коротко:** Выведите первый символ строки.

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
```$m1_l7_b4_content$, $m1_l7_b4_task_title$Первый символ$m1_l7_b4_task_title$, NULL::jsonb),
  (5, $m1_l7_b5_type$theory$m1_l7_b5_type$, $m1_l7_b5_title$Срезы$m1_l7_b5_title$, $m1_l7_b5_content$Срез берёт часть строки.

```python
text = "Python"
print(text[:3])  # Pyt
print(text[3:])  # hon
```$m1_l7_b5_content$, NULL, NULL::jsonb),
  (6, $m1_l7_b6_type$practice$m1_l7_b6_type$, $m1_l7_b6_title$Первые N$m1_l7_b6_title$, $m1_l7_b6_content$**Коротко:** Выведите первые n символов.

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
```$m1_l7_b6_content$, $m1_l7_b6_task_title$Первые N$m1_l7_b6_task_title$, NULL::jsonb),
  (7, $m1_l7_b7_type$theory$m1_l7_b7_type$, $m1_l7_b7_title$Переворот$m1_l7_b7_title$, $m1_l7_b7_content$Строку можно перевернуть срезом:

```python
word = "топот"
print(word[::-1])
```

`[::-1]` создаёт строку в обратном порядке.$m1_l7_b7_content$, NULL, NULL::jsonb),
  (8, $m1_l7_b8_type$practice$m1_l7_b8_type$, $m1_l7_b8_title$Палиндром$m1_l7_b8_title$, $m1_l7_b8_content$**Коротко:** Проверьте слово на палиндром.

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
```$m1_l7_b8_content$, $m1_l7_b8_task_title$Палиндром$m1_l7_b8_task_title$, NULL::jsonb),
  (9, $m1_l7_b9_type$theory$m1_l7_b9_type$, $m1_l7_b9_title$Методы$m1_l7_b9_title$, $m1_l7_b9_content$У строк есть методы:

```python
text.lower()   # нижний регистр
text.upper()   # верхний регистр
text.strip()   # убрать пробелы по краям
```$m1_l7_b9_content$, NULL, NULL::jsonb),
  (10, $m1_l7_b10_type$practice$m1_l7_b10_type$, $m1_l7_b10_title$Нормализация$m1_l7_b10_title$, $m1_l7_b10_content$**Коротко:** Приведите строку к нижнему регистру.

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
```$m1_l7_b10_content$, $m1_l7_b10_task_title$Нормализация$m1_l7_b10_task_title$, NULL::jsonb),
  (11, $m1_l7_b11_type$practice$m1_l7_b11_type$, $m1_l7_b11_title$Счёт букв$m1_l7_b11_title$, $m1_l7_b11_content$**Коротко:** Посчитайте букву в строке.

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
```$m1_l7_b11_content$, $m1_l7_b11_task_title$Счёт букв$m1_l7_b11_task_title$, NULL::jsonb),
  (12, $m1_l7_b12_type$quiz$m1_l7_b12_type$, $m1_l7_b12_title$Итог$m1_l7_b12_title$, $m1_l7_b12_content$### Вопрос

Как получить строку в обратном порядке?

### Варианты

1. `text[-1]`

2. `text[::-1]`

3. `reverse(text)`

4. `text[1:]`$m1_l7_b12_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 8: Списки
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 8
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 8
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l8_t2_title$Первый элемент$m1_l8_t2_title$, $m1_l8_t2_statement$**Коротко:** Выведите первый элемент списка.

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
```$m1_l8_t2_statement$, $m1_l8_t2_starter$items = input().split()
$m1_l8_t2_starter$, $m1_l8_t2_solution$items = input().split()
print(items[0])
$m1_l8_t2_solution$, 1, 45, $m1_l8_t2_topic$Месяц 1. Python Core — Списки$m1_l8_t2_topic$, $m1_l8_t2_lang$python$m1_l8_t2_lang$, $m1_l8_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["`split()` делает список строк.","Первый элемент: `items[0]`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l8_t2_policy$::jsonb),
  ($m1_l8_t4_title$Список покупок$m1_l8_t4_title$, $m1_l8_t4_statement$**Коротко:** Соберите список из n строк.

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
```$m1_l8_t4_statement$, $m1_l8_t4_starter$n = int(input())
items = []
$m1_l8_t4_starter$, $m1_l8_t4_solution$n = int(input())
items = []
for i in range(n):
    item = input()
    items.append(item)
for item in items:
    print(item)
$m1_l8_t4_solution$, 2, 55, $m1_l8_t4_topic$Месяц 1. Python Core — Списки$m1_l8_t4_topic$, $m1_l8_t4_lang$python$m1_l8_t4_lang$, $m1_l8_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["В цикле считывай товар и добавляй в список.","Потом выведи элементы циклом."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l8_t4_policy$::jsonb),
  ($m1_l8_t6_title$Сумма списка$m1_l8_t6_title$, $m1_l8_t6_statement$**Коротко:** Сложите числа из строки.

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
```$m1_l8_t6_statement$, $m1_l8_t6_starter$parts = input().split()
total = 0
$m1_l8_t6_starter$, $m1_l8_t6_solution$parts = input().split()
total = 0
for part in parts:
    total = total + int(part)
print(total)
$m1_l8_t6_solution$, 2, 60, $m1_l8_t6_topic$Месяц 1. Python Core — Списки$m1_l8_t6_topic$, $m1_l8_t6_lang$python$m1_l8_t6_lang$, $m1_l8_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Перебери элементы списка.","Каждый элемент преобразуй через `int()`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l8_t6_policy$::jsonb),
  ($m1_l8_t7_title$Фильтр$m1_l8_t7_title$, $m1_l8_t7_statement$**Коротко:** Выведите числа больше 10.

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

```$m1_l8_t7_statement$, $m1_l8_t7_starter$parts = input().split()
$m1_l8_t7_starter$, $m1_l8_t7_solution$parts = input().split()
for part in parts:
    number = int(part)
    if number > 10:
        print(number)
$m1_l8_t7_solution$, 2, 60, $m1_l8_t7_topic$Месяц 1. Python Core — Списки$m1_l8_t7_topic$, $m1_l8_t7_lang$python$m1_l8_t7_lang$, $m1_l8_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Преобразуй каждый элемент в число.","Проверь `number > 10`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l8_t7_policy$::jsonb),
  ($m1_l8_t8_title$Минимум$m1_l8_t8_title$, $m1_l8_t8_statement$**Коротко:** Найдите минимальное число.

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
```$m1_l8_t8_statement$, $m1_l8_t8_starter$numbers = input().split()
$m1_l8_t8_starter$, $m1_l8_t8_solution$parts = input().split()
minimum = int(parts[0])
for part in parts:
    number = int(part)
    if number < minimum:
        minimum = number
print(minimum)
$m1_l8_t8_solution$, 2, 60, $m1_l8_t8_topic$Месяц 1. Python Core — Списки$m1_l8_t8_topic$, $m1_l8_t8_lang$python$m1_l8_t8_lang$, $m1_l8_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Можно использовать `min`, но сначала нужны числа.","Или перебери список вручную."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l8_t8_policy$::jsonb),
  ($m1_l8_t10_title$Все строки$m1_l8_t10_title$, $m1_l8_t10_statement$**Коротко:** Отфильтруйте слова по длине.

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
```$m1_l8_t10_statement$, $m1_l8_t10_starter$words = input().split()
$m1_l8_t10_starter$, $m1_l8_t10_solution$words = input().split()
for word in words:
    if len(word) > 3:
        print(word)
$m1_l8_t10_solution$, 2, 65, $m1_l8_t10_topic$Месяц 1. Python Core — Списки$m1_l8_t10_topic$, $m1_l8_t10_lang$python$m1_l8_t10_lang$, $m1_l8_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Длина слова: `len(word)`.","Проверка: `len(word) > 3`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l8_t10_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l8_ttitle_2$Первый элемент$m1_l8_ttitle_2$,
    $m1_l8_ttitle_4$Список покупок$m1_l8_ttitle_4$,
    $m1_l8_ttitle_6$Сумма списка$m1_l8_ttitle_6$,
    $m1_l8_ttitle_7$Фильтр$m1_l8_ttitle_7$,
    $m1_l8_ttitle_8$Минимум$m1_l8_ttitle_8$,
    $m1_l8_ttitle_10$Все строки$m1_l8_ttitle_10$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l8_test_2_1_title$Первый элемент$m1_l8_test_2_1_title$, $m1_l8_test_2_1_input$хлеб молоко сыр$m1_l8_test_2_1_input$, $m1_l8_test_2_1_expected$хлеб$m1_l8_test_2_1_expected$, FALSE, 1),
  ($m1_l8_test_2_2_title$Первый элемент$m1_l8_test_2_2_title$, $m1_l8_test_2_2_input$a b c$m1_l8_test_2_2_input$, $m1_l8_test_2_2_expected$a$m1_l8_test_2_2_expected$, TRUE, 2),
  ($m1_l8_test_2_3_title$Первый элемент$m1_l8_test_2_3_title$, $m1_l8_test_2_3_input$one$m1_l8_test_2_3_input$, $m1_l8_test_2_3_expected$one$m1_l8_test_2_3_expected$, TRUE, 3),
  ($m1_l8_test_4_1_title$Список покупок$m1_l8_test_4_1_title$, $m1_l8_test_4_1_input$3
хлеб
молоко
сыр$m1_l8_test_4_1_input$, $m1_l8_test_4_1_expected$хлеб
молоко
сыр$m1_l8_test_4_1_expected$, FALSE, 1),
  ($m1_l8_test_4_2_title$Список покупок$m1_l8_test_4_2_title$, $m1_l8_test_4_2_input$1
чай$m1_l8_test_4_2_input$, $m1_l8_test_4_2_expected$чай$m1_l8_test_4_2_expected$, TRUE, 2),
  ($m1_l8_test_6_1_title$Сумма списка$m1_l8_test_6_1_title$, $m1_l8_test_6_1_input$1 2 3$m1_l8_test_6_1_input$, $m1_l8_test_6_1_expected$6$m1_l8_test_6_1_expected$, FALSE, 1),
  ($m1_l8_test_6_2_title$Сумма списка$m1_l8_test_6_2_title$, $m1_l8_test_6_2_input$10 -5 2$m1_l8_test_6_2_input$, $m1_l8_test_6_2_expected$7$m1_l8_test_6_2_expected$, TRUE, 2),
  ($m1_l8_test_6_3_title$Сумма списка$m1_l8_test_6_3_title$, $m1_l8_test_6_3_input$0 0 0$m1_l8_test_6_3_input$, $m1_l8_test_6_3_expected$0$m1_l8_test_6_3_expected$, TRUE, 3),
  ($m1_l8_test_7_1_title$Фильтр$m1_l8_test_7_1_title$, $m1_l8_test_7_1_input$1 11 10 20$m1_l8_test_7_1_input$, $m1_l8_test_7_1_expected$11
20$m1_l8_test_7_1_expected$, FALSE, 1),
  ($m1_l8_test_7_2_title$Фильтр$m1_l8_test_7_2_title$, $m1_l8_test_7_2_input$1 2 3$m1_l8_test_7_2_input$, $m1_l8_test_7_2_expected$$m1_l8_test_7_2_expected$, TRUE, 2),
  ($m1_l8_test_7_3_title$Фильтр$m1_l8_test_7_3_title$, $m1_l8_test_7_3_input$12$m1_l8_test_7_3_input$, $m1_l8_test_7_3_expected$12$m1_l8_test_7_3_expected$, TRUE, 3),
  ($m1_l8_test_8_1_title$Минимум$m1_l8_test_8_1_title$, $m1_l8_test_8_1_input$5 2 9$m1_l8_test_8_1_input$, $m1_l8_test_8_1_expected$2$m1_l8_test_8_1_expected$, FALSE, 1),
  ($m1_l8_test_8_2_title$Минимум$m1_l8_test_8_2_title$, $m1_l8_test_8_2_input$-1 -5 3$m1_l8_test_8_2_input$, $m1_l8_test_8_2_expected$-5$m1_l8_test_8_2_expected$, TRUE, 2),
  ($m1_l8_test_8_3_title$Минимум$m1_l8_test_8_3_title$, $m1_l8_test_8_3_input$7$m1_l8_test_8_3_input$, $m1_l8_test_8_3_expected$7$m1_l8_test_8_3_expected$, TRUE, 3),
  ($m1_l8_test_10_1_title$Все строки$m1_l8_test_10_1_title$, $m1_l8_test_10_1_input$кот собака дом python$m1_l8_test_10_1_input$, $m1_l8_test_10_1_expected$собака
python$m1_l8_test_10_1_expected$, FALSE, 1),
  ($m1_l8_test_10_2_title$Все строки$m1_l8_test_10_2_title$, $m1_l8_test_10_2_input$a bb ccc$m1_l8_test_10_2_input$, $m1_l8_test_10_2_expected$$m1_l8_test_10_2_expected$, TRUE, 2)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l8_b1_type$theory$m1_l8_b1_type$, $m1_l8_b1_title$Списки$m1_l8_b1_title$, $m1_l8_b1_content$Список хранит несколько значений.

```python
items = ["хлеб", "молоко", "сыр"]
print(items[0])  # хлеб
```

Индексы начинаются с 0.$m1_l8_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l8_b2_type$practice$m1_l8_b2_type$, $m1_l8_b2_title$Первый элемент$m1_l8_b2_title$, $m1_l8_b2_content$**Коротко:** Выведите первый элемент списка.

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
```$m1_l8_b2_content$, $m1_l8_b2_task_title$Первый элемент$m1_l8_b2_task_title$, NULL::jsonb),
  (3, $m1_l8_b3_type$theory$m1_l8_b3_type$, $m1_l8_b3_title$append$m1_l8_b3_title$, $m1_l8_b3_content$`append()` добавляет элемент в конец списка.

```python
items = []
items.append("хлеб")
items.append("молоко")
```$m1_l8_b3_content$, NULL, NULL::jsonb),
  (4, $m1_l8_b4_type$practice$m1_l8_b4_type$, $m1_l8_b4_title$Список покупок$m1_l8_b4_title$, $m1_l8_b4_content$**Коротко:** Соберите список из n строк.

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
```$m1_l8_b4_content$, $m1_l8_b4_task_title$Список покупок$m1_l8_b4_task_title$, NULL::jsonb),
  (5, $m1_l8_b5_type$theory$m1_l8_b5_type$, $m1_l8_b5_title$split$m1_l8_b5_title$, $m1_l8_b5_content$`input().split()` разбивает строку по пробелам.

```python
numbers = input().split()
```

Сначала это список строк. Для арифметики элементы нужно превращать в `int`.$m1_l8_b5_content$, NULL, NULL::jsonb),
  (6, $m1_l8_b6_type$practice$m1_l8_b6_type$, $m1_l8_b6_title$Сумма списка$m1_l8_b6_title$, $m1_l8_b6_content$**Коротко:** Сложите числа из строки.

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
```$m1_l8_b6_content$, $m1_l8_b6_task_title$Сумма списка$m1_l8_b6_task_title$, NULL::jsonb),
  (7, $m1_l8_b7_type$practice$m1_l8_b7_type$, $m1_l8_b7_title$Фильтр$m1_l8_b7_title$, $m1_l8_b7_content$**Коротко:** Выведите числа больше 10.

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

```$m1_l8_b7_content$, $m1_l8_b7_task_title$Фильтр$m1_l8_b7_task_title$, NULL::jsonb),
  (8, $m1_l8_b8_type$practice$m1_l8_b8_type$, $m1_l8_b8_title$Минимум$m1_l8_b8_title$, $m1_l8_b8_content$**Коротко:** Найдите минимальное число.

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
```$m1_l8_b8_content$, $m1_l8_b8_task_title$Минимум$m1_l8_b8_task_title$, NULL::jsonb),
  (9, $m1_l8_b9_type$theory$m1_l8_b9_type$, $m1_l8_b9_title$Вывод списка$m1_l8_b9_title$, $m1_l8_b9_content$Не выводи список напрямую, если условие просит элементы построчно.

Плохо для таких задач:
```python
print(items)
```

Лучше:
```python
for item in items:
    print(item)
```$m1_l8_b9_content$, NULL, NULL::jsonb),
  (10, $m1_l8_b10_type$practice$m1_l8_b10_type$, $m1_l8_b10_title$Все строки$m1_l8_b10_title$, $m1_l8_b10_content$**Коротко:** Отфильтруйте слова по длине.

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
```$m1_l8_b10_content$, $m1_l8_b10_task_title$Все строки$m1_l8_b10_task_title$, NULL::jsonb),
  (11, $m1_l8_b11_type$quiz$m1_l8_b11_type$, $m1_l8_b11_title$Итог$m1_l8_b11_title$, $m1_l8_b11_content$### Вопрос

Что делает `input().split()`?

### Варианты

1. Считает сумму

2. Создаёт список строк

3. Создаёт список чисел

4. Удаляет пробелы по краям$m1_l8_b11_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 9: Словари
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 9
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 9
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l9_t2_title$Контакт$m1_l9_t2_title$, $m1_l9_t2_statement$**Коротко:** Выведите телефон по имени.

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
```$m1_l9_t2_statement$, $m1_l9_t2_starter$name = input()
contacts = {"Анна": "111", "Олег": "222"}
$m1_l9_t2_starter$, $m1_l9_t2_solution$name = input()
contacts = {"Анна": "111", "Олег": "222"}
print(contacts[name])
$m1_l9_t2_solution$, 1, 45, $m1_l9_t2_topic$Месяц 1. Python Core — Словари$m1_l9_t2_topic$, $m1_l9_t2_lang$python$m1_l9_t2_lang$, $m1_l9_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Ключ — имя.","Значение — телефон."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l9_t2_policy$::jsonb),
  ($m1_l9_t4_title$Поиск$m1_l9_t4_title$, $m1_l9_t4_statement$**Коротко:** Найдите контакт безопасно.

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
```$m1_l9_t4_statement$, $m1_l9_t4_starter$name = input()
contacts = {"Анна": "111", "Олег": "222"}
$m1_l9_t4_starter$, $m1_l9_t4_solution$name = input()
contacts = {"Анна": "111", "Олег": "222"}
print(contacts.get(name, "Не найдено"))
$m1_l9_t4_solution$, 2, 55, $m1_l9_t4_topic$Месяц 1. Python Core — Словари$m1_l9_t4_topic$, $m1_l9_t4_lang$python$m1_l9_t4_lang$, $m1_l9_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Используй `contacts.get(...)`.","Второй аргумент `get` — значение по умолчанию."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l9_t4_policy$::jsonb),
  ($m1_l9_t5_title$Добавление$m1_l9_t5_title$, $m1_l9_t5_statement$**Коротко:** Добавьте пару в словарь.

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
```$m1_l9_t5_statement$, $m1_l9_t5_starter$name = input()
phone = input()
contacts = {}
$m1_l9_t5_starter$, $m1_l9_t5_solution$name = input()
phone = input()
contacts = {}
contacts[name] = phone
print(contacts[name])
$m1_l9_t5_solution$, 1, 45, $m1_l9_t5_topic$Месяц 1. Python Core — Словари$m1_l9_t5_topic$, $m1_l9_t5_lang$python$m1_l9_t5_lang$, $m1_l9_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Добавление: `contacts[name] = phone`.","Потом выведи `contacts[name]`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l9_t5_policy$::jsonb),
  ($m1_l9_t7_title$Вывод оценок$m1_l9_t7_title$, $m1_l9_t7_statement$**Коротко:** Выведите оценки в заданном порядке.

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
```$m1_l9_t7_statement$, $m1_l9_t7_starter$grades = {"Анна": 5, "Олег": 4, "Маша": 3}
$m1_l9_t7_starter$, $m1_l9_t7_solution$grades = {"Анна": 5, "Олег": 4, "Маша": 3}
for name in ["Анна", "Олег", "Маша"]:
    print(name + ":", grades[name])
$m1_l9_t7_solution$, 2, 55, $m1_l9_t7_topic$Месяц 1. Python Core — Словари$m1_l9_t7_topic$, $m1_l9_t7_lang$python$m1_l9_t7_lang$, $m1_l9_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Для автопроверки порядок фиксирован.","Выводи имена из списка в нужном порядке."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l9_t7_policy$::jsonb),
  ($m1_l9_t8_title$Сумма товаров$m1_l9_t8_title$, $m1_l9_t8_statement$**Коротко:** Посчитайте стоимость корзины.

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
```$m1_l9_t8_statement$, $m1_l9_t8_starter$n = int(input())
products = {}
$m1_l9_t8_starter$, $m1_l9_t8_solution$n = int(input())
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
$m1_l9_t8_solution$, 3, 75, $m1_l9_t8_topic$Месяц 1. Python Core — Словари$m1_l9_t8_topic$, $m1_l9_t8_lang$python$m1_l9_t8_lang$, $m1_l9_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Разбей строку через `split()`.","Цену преобразуй в `int`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l9_t8_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l9_ttitle_2$Контакт$m1_l9_ttitle_2$,
    $m1_l9_ttitle_4$Поиск$m1_l9_ttitle_4$,
    $m1_l9_ttitle_5$Добавление$m1_l9_ttitle_5$,
    $m1_l9_ttitle_7$Вывод оценок$m1_l9_ttitle_7$,
    $m1_l9_ttitle_8$Сумма товаров$m1_l9_ttitle_8$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l9_test_2_1_title$Контакт$m1_l9_test_2_1_title$, $m1_l9_test_2_1_input$Анна$m1_l9_test_2_1_input$, $m1_l9_test_2_1_expected$111$m1_l9_test_2_1_expected$, FALSE, 1),
  ($m1_l9_test_2_2_title$Контакт$m1_l9_test_2_2_title$, $m1_l9_test_2_2_input$Олег$m1_l9_test_2_2_input$, $m1_l9_test_2_2_expected$222$m1_l9_test_2_2_expected$, TRUE, 2),
  ($m1_l9_test_4_1_title$Поиск$m1_l9_test_4_1_title$, $m1_l9_test_4_1_input$Анна$m1_l9_test_4_1_input$, $m1_l9_test_4_1_expected$111$m1_l9_test_4_1_expected$, FALSE, 1),
  ($m1_l9_test_4_2_title$Поиск$m1_l9_test_4_2_title$, $m1_l9_test_4_2_input$Олег$m1_l9_test_4_2_input$, $m1_l9_test_4_2_expected$222$m1_l9_test_4_2_expected$, TRUE, 2),
  ($m1_l9_test_4_3_title$Поиск$m1_l9_test_4_3_title$, $m1_l9_test_4_3_input$Маша$m1_l9_test_4_3_input$, $m1_l9_test_4_3_expected$Не найдено$m1_l9_test_4_3_expected$, TRUE, 3),
  ($m1_l9_test_5_1_title$Добавление$m1_l9_test_5_1_title$, $m1_l9_test_5_1_input$Иван
333$m1_l9_test_5_1_input$, $m1_l9_test_5_1_expected$333$m1_l9_test_5_1_expected$, FALSE, 1),
  ($m1_l9_test_5_2_title$Добавление$m1_l9_test_5_2_title$, $m1_l9_test_5_2_input$A
1$m1_l9_test_5_2_input$, $m1_l9_test_5_2_expected$1$m1_l9_test_5_2_expected$, TRUE, 2),
  ($m1_l9_test_7_1_title$Вывод оценок$m1_l9_test_7_1_title$, $m1_l9_test_7_1_input$$m1_l9_test_7_1_input$, $m1_l9_test_7_1_expected$Анна: 5
Олег: 4
Маша: 3$m1_l9_test_7_1_expected$, FALSE, 1),
  ($m1_l9_test_8_1_title$Сумма товаров$m1_l9_test_8_1_title$, $m1_l9_test_8_1_input$3
хлеб 50
молоко 80
сыр 120$m1_l9_test_8_1_input$, $m1_l9_test_8_1_expected$250$m1_l9_test_8_1_expected$, FALSE, 1),
  ($m1_l9_test_8_2_title$Сумма товаров$m1_l9_test_8_2_title$, $m1_l9_test_8_2_input$1
чай 100$m1_l9_test_8_2_input$, $m1_l9_test_8_2_expected$100$m1_l9_test_8_2_expected$, TRUE, 2)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l9_b1_type$theory$m1_l9_b1_type$, $m1_l9_b1_title$dict$m1_l9_b1_title$, $m1_l9_b1_content$Словарь хранит пары `ключ: значение`.

```python
user = {"name": "Анна", "age": 16}
print(user["name"])
```

Ключ помогает быстро найти значение.$m1_l9_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l9_b2_type$practice$m1_l9_b2_type$, $m1_l9_b2_title$Контакт$m1_l9_b2_title$, $m1_l9_b2_content$**Коротко:** Выведите телефон по имени.

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
```$m1_l9_b2_content$, $m1_l9_b2_task_title$Контакт$m1_l9_b2_task_title$, NULL::jsonb),
  (3, $m1_l9_b3_type$theory$m1_l9_b3_type$, $m1_l9_b3_title$get$m1_l9_b3_title$, $m1_l9_b3_content$`get()` безопасно получает значение по ключу.

```python
contacts.get(name, "Не найдено")
```

Если ключа нет, вернётся значение по умолчанию.$m1_l9_b3_content$, NULL, NULL::jsonb),
  (4, $m1_l9_b4_type$practice$m1_l9_b4_type$, $m1_l9_b4_title$Поиск$m1_l9_b4_title$, $m1_l9_b4_content$**Коротко:** Найдите контакт безопасно.

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
```$m1_l9_b4_content$, $m1_l9_b4_task_title$Поиск$m1_l9_b4_task_title$, NULL::jsonb),
  (5, $m1_l9_b5_type$practice$m1_l9_b5_type$, $m1_l9_b5_title$Добавление$m1_l9_b5_title$, $m1_l9_b5_content$**Коротко:** Добавьте пару в словарь.

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
```$m1_l9_b5_content$, $m1_l9_b5_task_title$Добавление$m1_l9_b5_task_title$, NULL::jsonb),
  (6, $m1_l9_b6_type$theory$m1_l9_b6_type$, $m1_l9_b6_title$items$m1_l9_b6_title$, $m1_l9_b6_content$`.items()` даёт пары ключ-значение.

```python
for name, phone in contacts.items():
    print(name, phone)
```$m1_l9_b6_content$, NULL, NULL::jsonb),
  (7, $m1_l9_b7_type$practice$m1_l9_b7_type$, $m1_l9_b7_title$Вывод оценок$m1_l9_b7_title$, $m1_l9_b7_content$**Коротко:** Выведите оценки в заданном порядке.

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
```$m1_l9_b7_content$, $m1_l9_b7_task_title$Вывод оценок$m1_l9_b7_task_title$, NULL::jsonb),
  (8, $m1_l9_b8_type$practice$m1_l9_b8_type$, $m1_l9_b8_title$Сумма товаров$m1_l9_b8_title$, $m1_l9_b8_content$**Коротко:** Посчитайте стоимость корзины.

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
```$m1_l9_b8_content$, $m1_l9_b8_task_title$Сумма товаров$m1_l9_b8_task_title$, NULL::jsonb),
  (9, $m1_l9_b9_type$quiz$m1_l9_b9_type$, $m1_l9_b9_title$Итог$m1_l9_b9_title$, $m1_l9_b9_content$### Вопрос

Что делает `dict.get(key, default)`?

### Варианты

1. Удаляет ключ

2. Получает значение или default

3. Сортирует словарь

4. Печатает словарь$m1_l9_b9_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 10: Множества
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 10
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 10
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l10_t2_title$Уникальные$m1_l10_t2_title$, $m1_l10_t2_statement$**Коротко:** Посчитайте уникальные слова.

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
```$m1_l10_t2_statement$, $m1_l10_t2_starter$words = input().split()
$m1_l10_t2_starter$, $m1_l10_t2_solution$words = input().split()
unique_words = set(words)
print(len(unique_words))
$m1_l10_t2_solution$, 1, 45, $m1_l10_t2_topic$Месяц 1. Python Core — Множества$m1_l10_t2_topic$, $m1_l10_t2_lang$python$m1_l10_t2_lang$, $m1_l10_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Создай `set(words)`.","Количество: `len(...)`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l10_t2_policy$::jsonb),
  ($m1_l10_t4_title$Проверка$m1_l10_t4_title$, $m1_l10_t4_statement$**Коротко:** Проверьте слово в списке.

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
```$m1_l10_t4_statement$, $m1_l10_t4_starter$words = set(input().split())
word = input()
$m1_l10_t4_starter$, $m1_l10_t4_solution$words = set(input().split())
word = input()
if word in words:
    print("Есть")
else:
    print("Нет")
$m1_l10_t4_solution$, 1, 45, $m1_l10_t4_topic$Месяц 1. Python Core — Множества$m1_l10_t4_topic$, $m1_l10_t4_lang$python$m1_l10_t4_lang$, $m1_l10_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Используй `word in words`.","Множество ускоряет поиск."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l10_t4_policy$::jsonb),
  ($m1_l10_t6_title$Буквы$m1_l10_t6_title$, $m1_l10_t6_statement$**Коротко:** Посчитайте частоту буквы.

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
```$m1_l10_t6_statement$, $m1_l10_t6_starter$text = input()
$m1_l10_t6_starter$, $m1_l10_t6_solution$text = input()
counts = {"a": 0, "b": 0, "c": 0}
for char in text:
    if char in counts:
        counts[char] = counts[char] + 1
for char in ["a", "b", "c"]:
    print(char + ":", counts[char])
$m1_l10_t6_solution$, 2, 60, $m1_l10_t6_topic$Месяц 1. Python Core — Множества$m1_l10_t6_topic$, $m1_l10_t6_lang$python$m1_l10_t6_lang$, $m1_l10_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Создай словарь счётчиков.","Выводи буквы в порядке `a`, `b`, `c`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l10_t6_policy$::jsonb),
  ($m1_l10_t7_title$Слова$m1_l10_t7_title$, $m1_l10_t7_statement$**Коротко:** Найдите повторяющиеся слова.

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
```$m1_l10_t7_statement$, $m1_l10_t7_starter$words = input().split()
$m1_l10_t7_starter$, $m1_l10_t7_solution$words = input().split()
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
printed = set()
for word in words:
    if counts[word] > 1 and word not in printed:
        print(word)
        printed.add(word)
$m1_l10_t7_solution$, 3, 75, $m1_l10_t7_topic$Месяц 1. Python Core — Множества$m1_l10_t7_topic$, $m1_l10_t7_lang$python$m1_l10_t7_lang$, $m1_l10_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сначала посчитай частоты.","Потом снова пройди по словам и выводи ещё не выведенные повторы."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l10_t7_policy$::jsonb),
  ($m1_l10_t8_title$Оценки$m1_l10_t8_title$, $m1_l10_t8_statement$**Коротко:** Посчитайте оценки 1–5.

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
```$m1_l10_t8_statement$, $m1_l10_t8_starter$grades = input().split()
$m1_l10_t8_starter$, $m1_l10_t8_solution$grades = input().split()
counts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
for grade in grades:
    counts[grade] = counts[grade] + 1
for grade in ["1", "2", "3", "4", "5"]:
    print(grade + ":", counts[grade])
$m1_l10_t8_solution$, 3, 75, $m1_l10_t8_topic$Месяц 1. Python Core — Множества$m1_l10_t8_topic$, $m1_l10_t8_lang$python$m1_l10_t8_lang$, $m1_l10_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Создай словарь с ключами `1`–`5`.","Выводи в порядке от 1 до 5."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l10_t8_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l10_ttitle_2$Уникальные$m1_l10_ttitle_2$,
    $m1_l10_ttitle_4$Проверка$m1_l10_ttitle_4$,
    $m1_l10_ttitle_6$Буквы$m1_l10_ttitle_6$,
    $m1_l10_ttitle_7$Слова$m1_l10_ttitle_7$,
    $m1_l10_ttitle_8$Оценки$m1_l10_ttitle_8$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l10_test_2_1_title$Уникальные$m1_l10_test_2_1_title$, $m1_l10_test_2_1_input$кот пёс кот$m1_l10_test_2_1_input$, $m1_l10_test_2_1_expected$2$m1_l10_test_2_1_expected$, FALSE, 1),
  ($m1_l10_test_2_2_title$Уникальные$m1_l10_test_2_2_title$, $m1_l10_test_2_2_input$a b c$m1_l10_test_2_2_input$, $m1_l10_test_2_2_expected$3$m1_l10_test_2_2_expected$, TRUE, 2),
  ($m1_l10_test_2_3_title$Уникальные$m1_l10_test_2_3_title$, $m1_l10_test_2_3_input$a a a$m1_l10_test_2_3_input$, $m1_l10_test_2_3_expected$1$m1_l10_test_2_3_expected$, TRUE, 3),
  ($m1_l10_test_4_1_title$Проверка$m1_l10_test_4_1_title$, $m1_l10_test_4_1_input$кот пёс
кот$m1_l10_test_4_1_input$, $m1_l10_test_4_1_expected$Есть$m1_l10_test_4_1_expected$, FALSE, 1),
  ($m1_l10_test_4_2_title$Проверка$m1_l10_test_4_2_title$, $m1_l10_test_4_2_input$кот пёс
лось$m1_l10_test_4_2_input$, $m1_l10_test_4_2_expected$Нет$m1_l10_test_4_2_expected$, TRUE, 2),
  ($m1_l10_test_6_1_title$Буквы$m1_l10_test_6_1_title$, $m1_l10_test_6_1_input$abac$m1_l10_test_6_1_input$, $m1_l10_test_6_1_expected$a: 2
b: 1
c: 1$m1_l10_test_6_1_expected$, FALSE, 1),
  ($m1_l10_test_6_2_title$Буквы$m1_l10_test_6_2_title$, $m1_l10_test_6_2_input$zzz$m1_l10_test_6_2_input$, $m1_l10_test_6_2_expected$a: 0
b: 0
c: 0$m1_l10_test_6_2_expected$, TRUE, 2),
  ($m1_l10_test_7_1_title$Слова$m1_l10_test_7_1_title$, $m1_l10_test_7_1_input$кот пёс кот лис пёс$m1_l10_test_7_1_input$, $m1_l10_test_7_1_expected$кот
пёс$m1_l10_test_7_1_expected$, FALSE, 1),
  ($m1_l10_test_7_2_title$Слова$m1_l10_test_7_2_title$, $m1_l10_test_7_2_input$a b c$m1_l10_test_7_2_input$, $m1_l10_test_7_2_expected$$m1_l10_test_7_2_expected$, TRUE, 2),
  ($m1_l10_test_8_1_title$Оценки$m1_l10_test_8_1_title$, $m1_l10_test_8_1_input$5 4 5 3$m1_l10_test_8_1_input$, $m1_l10_test_8_1_expected$1: 0
2: 0
3: 1
4: 1
5: 2$m1_l10_test_8_1_expected$, FALSE, 1),
  ($m1_l10_test_8_2_title$Оценки$m1_l10_test_8_2_title$, $m1_l10_test_8_2_input$1 1 2$m1_l10_test_8_2_input$, $m1_l10_test_8_2_expected$1: 2
2: 1
3: 0
4: 0
5: 0$m1_l10_test_8_2_expected$, TRUE, 2)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l10_b1_type$theory$m1_l10_b1_type$, $m1_l10_b1_title$set$m1_l10_b1_title$, $m1_l10_b1_content$Множество хранит только уникальные значения.

```python
items = set(["a", "b", "a"])
print(len(items))  # 2
```$m1_l10_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l10_b2_type$practice$m1_l10_b2_type$, $m1_l10_b2_title$Уникальные$m1_l10_b2_title$, $m1_l10_b2_content$**Коротко:** Посчитайте уникальные слова.

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
```$m1_l10_b2_content$, $m1_l10_b2_task_title$Уникальные$m1_l10_b2_task_title$, NULL::jsonb),
  (3, $m1_l10_b3_type$theory$m1_l10_b3_type$, $m1_l10_b3_title$in$m1_l10_b3_title$, $m1_l10_b3_content$Оператор `in` проверяет наличие элемента.

```python
if word in words_set:
    print("Есть")
```$m1_l10_b3_content$, NULL, NULL::jsonb),
  (4, $m1_l10_b4_type$practice$m1_l10_b4_type$, $m1_l10_b4_title$Проверка$m1_l10_b4_title$, $m1_l10_b4_content$**Коротко:** Проверьте слово в списке.

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
```$m1_l10_b4_content$, $m1_l10_b4_task_title$Проверка$m1_l10_b4_task_title$, NULL::jsonb),
  (5, $m1_l10_b5_type$theory$m1_l10_b5_type$, $m1_l10_b5_title$Частоты$m1_l10_b5_title$, $m1_l10_b5_content$Частотный словарь считает, сколько раз встретилось значение.

```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
```$m1_l10_b5_content$, NULL, NULL::jsonb),
  (6, $m1_l10_b6_type$practice$m1_l10_b6_type$, $m1_l10_b6_title$Буквы$m1_l10_b6_title$, $m1_l10_b6_content$**Коротко:** Посчитайте частоту буквы.

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
```$m1_l10_b6_content$, $m1_l10_b6_task_title$Буквы$m1_l10_b6_task_title$, NULL::jsonb),
  (7, $m1_l10_b7_type$practice$m1_l10_b7_type$, $m1_l10_b7_title$Слова$m1_l10_b7_title$, $m1_l10_b7_content$**Коротко:** Найдите повторяющиеся слова.

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
```$m1_l10_b7_content$, $m1_l10_b7_task_title$Слова$m1_l10_b7_task_title$, NULL::jsonb),
  (8, $m1_l10_b8_type$practice$m1_l10_b8_type$, $m1_l10_b8_title$Оценки$m1_l10_b8_title$, $m1_l10_b8_content$**Коротко:** Посчитайте оценки 1–5.

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
```$m1_l10_b8_content$, $m1_l10_b8_task_title$Оценки$m1_l10_b8_task_title$, NULL::jsonb),
  (9, $m1_l10_b9_type$quiz$m1_l10_b9_type$, $m1_l10_b9_title$Итог$m1_l10_b9_title$, $m1_l10_b9_content$### Вопрос

Что хранит `set`?

### Варианты

1. Только уникальные значения

2. Пары ключ-значение

3. Только числа

4. Только строки$m1_l10_b9_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 11: Функции
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 11
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 11
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l11_t2_title$Привет$m1_l11_t2_title$, $m1_l11_t2_statement$**Коротко:** Создайте и вызовите функцию.

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
```$m1_l11_t2_statement$, $m1_l11_t2_starter$def say_hello():
    # код функции

# вызов
$m1_l11_t2_starter$, $m1_l11_t2_solution$def say_hello():
    print("Привет")

say_hello()
$m1_l11_t2_solution$, 1, 45, $m1_l11_t2_topic$Месяц 1. Python Core — Функции$m1_l11_t2_topic$, $m1_l11_t2_lang$python$m1_l11_t2_lang$, $m1_l11_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Код внутри функции должен быть с отступом.","После определения функции вызови `say_hello()`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l11_t2_policy$::jsonb),
  ($m1_l11_t4_title$Сумма$m1_l11_t4_title$, $m1_l11_t4_statement$**Коротко:** Верните сумму двух чисел.

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
```$m1_l11_t4_statement$, $m1_l11_t4_starter$def add(a, b):
    # return ...

a = int(input())
b = int(input())
$m1_l11_t4_starter$, $m1_l11_t4_solution$def add(a, b):
    return a + b

a = int(input())
b = int(input())
print(add(a, b))
$m1_l11_t4_solution$, 2, 60, $m1_l11_t4_topic$Месяц 1. Python Core — Функции$m1_l11_t4_topic$, $m1_l11_t4_lang$python$m1_l11_t4_lang$, $m1_l11_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Внутри функции нужен `return`.","Вывод делай после вызова функции."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l11_t4_policy$::jsonb),
  ($m1_l11_t6_title$Площадь$m1_l11_t6_title$, $m1_l11_t6_statement$**Коротко:** Функция для площади.

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
```$m1_l11_t6_statement$, $m1_l11_t6_starter$def area(width, height):
    # return ...
$m1_l11_t6_starter$, $m1_l11_t6_solution$def area(width, height):
    return width * height

width = int(input())
height = int(input())
print(area(width, height))
$m1_l11_t6_solution$, 2, 60, $m1_l11_t6_topic$Месяц 1. Python Core — Функции$m1_l11_t6_topic$, $m1_l11_t6_lang$python$m1_l11_t6_lang$, $m1_l11_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Площадь: `width * height`.","Функция должна вернуть значение, а не печатать внутри."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l11_t6_policy$::jsonb),
  ($m1_l11_t8_title$Ошибка return$m1_l11_t8_title$, $m1_l11_t8_statement$**Коротко:** Замените print на return.

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
```$m1_l11_t8_statement$, $m1_l11_t8_starter$$m1_l11_t8_starter$, $m1_l11_t8_solution$def double(x):
    return x * 2

number = int(input())
result = double(number) + 1
print(result)
$m1_l11_t8_solution$, 2, 45, $m1_l11_t8_topic$Месяц 1. Python Core — Функции$m1_l11_t8_topic$, $m1_l11_t8_lang$python$m1_l11_t8_lang$, $m1_l11_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["`print()` не возвращает значение.","В функции нужен `return x * 2`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l11_t8_policy$::jsonb),
  ($m1_l11_t9_title$Валидатор$m1_l11_t9_title$, $m1_l11_t9_statement$**Коротко:** Проверьте длину пароля.

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
```$m1_l11_t9_statement$, $m1_l11_t9_starter$def is_valid(password):
    # return ...

password = input()
$m1_l11_t9_starter$, $m1_l11_t9_solution$def is_valid(password):
    return len(password) >= 8

password = input()
if is_valid(password):
    print("OK")
else:
    print("NO")
$m1_l11_t9_solution$, 2, 65, $m1_l11_t9_topic$Месяц 1. Python Core — Функции$m1_l11_t9_topic$, $m1_l11_t9_lang$python$m1_l11_t9_lang$, $m1_l11_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Длина: `len(password)`.","Функция возвращает логическое значение."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l11_t9_policy$::jsonb),
  ($m1_l11_t10_title$Калькулятор$m1_l11_t10_title$, $m1_l11_t10_statement$**Коротко:** Разбейте калькулятор на функции.

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
```$m1_l11_t10_statement$, $m1_l11_t10_starter$def add(a, b):
    pass

def subtract(a, b):
    pass

def multiply(a, b):
    pass
$m1_l11_t10_starter$, $m1_l11_t10_solution$def add(a, b):
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
$m1_l11_t10_solution$, 3, 80, $m1_l11_t10_topic$Месяц 1. Python Core — Функции$m1_l11_t10_topic$, $m1_l11_t10_lang$python$m1_l11_t10_lang$, $m1_l11_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Каждая функция должна делать одну операцию.","После ввода операции выбери нужную функцию через `if`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l11_t10_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l11_ttitle_2$Привет$m1_l11_ttitle_2$,
    $m1_l11_ttitle_4$Сумма$m1_l11_ttitle_4$,
    $m1_l11_ttitle_6$Площадь$m1_l11_ttitle_6$,
    $m1_l11_ttitle_8$Ошибка return$m1_l11_ttitle_8$,
    $m1_l11_ttitle_9$Валидатор$m1_l11_ttitle_9$,
    $m1_l11_ttitle_10$Калькулятор$m1_l11_ttitle_10$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l11_test_2_1_title$Привет$m1_l11_test_2_1_title$, $m1_l11_test_2_1_input$$m1_l11_test_2_1_input$, $m1_l11_test_2_1_expected$Привет$m1_l11_test_2_1_expected$, FALSE, 1),
  ($m1_l11_test_4_1_title$Сумма$m1_l11_test_4_1_title$, $m1_l11_test_4_1_input$2
3$m1_l11_test_4_1_input$, $m1_l11_test_4_1_expected$5$m1_l11_test_4_1_expected$, FALSE, 1),
  ($m1_l11_test_4_2_title$Сумма$m1_l11_test_4_2_title$, $m1_l11_test_4_2_input$10
-5$m1_l11_test_4_2_input$, $m1_l11_test_4_2_expected$5$m1_l11_test_4_2_expected$, TRUE, 2),
  ($m1_l11_test_4_3_title$Сумма$m1_l11_test_4_3_title$, $m1_l11_test_4_3_input$0
0$m1_l11_test_4_3_input$, $m1_l11_test_4_3_expected$0$m1_l11_test_4_3_expected$, TRUE, 3),
  ($m1_l11_test_6_1_title$Площадь$m1_l11_test_6_1_title$, $m1_l11_test_6_1_input$5
8$m1_l11_test_6_1_input$, $m1_l11_test_6_1_expected$40$m1_l11_test_6_1_expected$, FALSE, 1),
  ($m1_l11_test_6_2_title$Площадь$m1_l11_test_6_2_title$, $m1_l11_test_6_2_input$1
1$m1_l11_test_6_2_input$, $m1_l11_test_6_2_expected$1$m1_l11_test_6_2_expected$, TRUE, 2),
  ($m1_l11_test_8_1_title$Ошибка return$m1_l11_test_8_1_title$, $m1_l11_test_8_1_input$5$m1_l11_test_8_1_input$, $m1_l11_test_8_1_expected$11$m1_l11_test_8_1_expected$, FALSE, 1),
  ($m1_l11_test_8_2_title$Ошибка return$m1_l11_test_8_2_title$, $m1_l11_test_8_2_input$0$m1_l11_test_8_2_input$, $m1_l11_test_8_2_expected$1$m1_l11_test_8_2_expected$, TRUE, 2),
  ($m1_l11_test_9_1_title$Валидатор$m1_l11_test_9_1_title$, $m1_l11_test_9_1_input$12345678$m1_l11_test_9_1_input$, $m1_l11_test_9_1_expected$OK$m1_l11_test_9_1_expected$, FALSE, 1),
  ($m1_l11_test_9_2_title$Валидатор$m1_l11_test_9_2_title$, $m1_l11_test_9_2_input$123$m1_l11_test_9_2_input$, $m1_l11_test_9_2_expected$NO$m1_l11_test_9_2_expected$, TRUE, 2),
  ($m1_l11_test_9_3_title$Валидатор$m1_l11_test_9_3_title$, $m1_l11_test_9_3_input$abcdefgh$m1_l11_test_9_3_input$, $m1_l11_test_9_3_expected$OK$m1_l11_test_9_3_expected$, TRUE, 3),
  ($m1_l11_test_10_1_title$Калькулятор$m1_l11_test_10_1_title$, $m1_l11_test_10_1_input$2
3
+$m1_l11_test_10_1_input$, $m1_l11_test_10_1_expected$5$m1_l11_test_10_1_expected$, FALSE, 1),
  ($m1_l11_test_10_2_title$Калькулятор$m1_l11_test_10_2_title$, $m1_l11_test_10_2_input$10
4
-$m1_l11_test_10_2_input$, $m1_l11_test_10_2_expected$6$m1_l11_test_10_2_expected$, TRUE, 2),
  ($m1_l11_test_10_3_title$Калькулятор$m1_l11_test_10_3_title$, $m1_l11_test_10_3_input$3
5
*$m1_l11_test_10_3_input$, $m1_l11_test_10_3_expected$15$m1_l11_test_10_3_expected$, TRUE, 3)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l11_b1_type$theory$m1_l11_b1_type$, $m1_l11_b1_title$def$m1_l11_b1_title$, $m1_l11_b1_content$Функция — это именованный блок кода.

```python
def say_hello():
    print("Привет")

say_hello()
```

Функцию нужно не только создать, но и вызвать.$m1_l11_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l11_b2_type$practice$m1_l11_b2_type$, $m1_l11_b2_title$Привет$m1_l11_b2_title$, $m1_l11_b2_content$**Коротко:** Создайте и вызовите функцию.

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
```$m1_l11_b2_content$, $m1_l11_b2_task_title$Привет$m1_l11_b2_task_title$, NULL::jsonb),
  (3, $m1_l11_b3_type$theory$m1_l11_b3_type$, $m1_l11_b3_title$Параметры$m1_l11_b3_title$, $m1_l11_b3_content$Функция может принимать параметры.

```python
def greet(name):
    print("Привет,", name)

greet("Анна")
```$m1_l11_b3_content$, NULL, NULL::jsonb),
  (4, $m1_l11_b4_type$practice$m1_l11_b4_type$, $m1_l11_b4_title$Сумма$m1_l11_b4_title$, $m1_l11_b4_content$**Коротко:** Верните сумму двух чисел.

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
```$m1_l11_b4_content$, $m1_l11_b4_task_title$Сумма$m1_l11_b4_task_title$, NULL::jsonb),
  (5, $m1_l11_b5_type$theory$m1_l11_b5_type$, $m1_l11_b5_title$return$m1_l11_b5_title$, $m1_l11_b5_content$`return` возвращает результат функции.

```python
def square(x):
    return x * x

result = square(5)
print(result)
```

`print()` только выводит. `return` отдаёт значение дальше в код.$m1_l11_b5_content$, NULL, NULL::jsonb),
  (6, $m1_l11_b6_type$practice$m1_l11_b6_type$, $m1_l11_b6_title$Площадь$m1_l11_b6_title$, $m1_l11_b6_content$**Коротко:** Функция для площади.

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
```$m1_l11_b6_content$, $m1_l11_b6_task_title$Площадь$m1_l11_b6_task_title$, NULL::jsonb),
  (7, $m1_l11_b7_type$theory$m1_l11_b7_type$, $m1_l11_b7_title$print vs return$m1_l11_b7_title$, $m1_l11_b7_content$Сравни:

```python
def add(a, b):
    print(a + b)
```

и:

```python
def add(a, b):
    return a + b
```

Если результат нужно использовать дальше, нужен `return`.$m1_l11_b7_content$, NULL, NULL::jsonb),
  (8, $m1_l11_b8_type$practice$m1_l11_b8_type$, $m1_l11_b8_title$Ошибка return$m1_l11_b8_title$, $m1_l11_b8_content$**Коротко:** Замените print на return.

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
```$m1_l11_b8_content$, $m1_l11_b8_task_title$Ошибка return$m1_l11_b8_task_title$, NULL::jsonb),
  (9, $m1_l11_b9_type$practice$m1_l11_b9_type$, $m1_l11_b9_title$Валидатор$m1_l11_b9_title$, $m1_l11_b9_content$**Коротко:** Проверьте длину пароля.

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
```$m1_l11_b9_content$, $m1_l11_b9_task_title$Валидатор$m1_l11_b9_task_title$, NULL::jsonb),
  (10, $m1_l11_b10_type$practice$m1_l11_b10_type$, $m1_l11_b10_title$Калькулятор$m1_l11_b10_title$, $m1_l11_b10_content$**Коротко:** Разбейте калькулятор на функции.

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
```$m1_l11_b10_content$, $m1_l11_b10_task_title$Калькулятор$m1_l11_b10_task_title$, NULL::jsonb),
  (11, $m1_l11_b11_type$quiz$m1_l11_b11_type$, $m1_l11_b11_title$Итог$m1_l11_b11_title$, $m1_l11_b11_content$### Вопрос

Что делает `return`?

### Варианты

1. Печатает текст

2. Возвращает результат функции

3. Создаёт цикл

4. Считывает ввод$m1_l11_b11_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 12: Проект
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 12
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 12
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l12_t3_title$Добавить$m1_l12_t3_title$, $m1_l12_t3_statement$**Коротко:** Реализуйте добавление задачи.

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
```$m1_l12_t3_statement$, $m1_l12_t3_starter$tasks = []
title = input()
$m1_l12_t3_starter$, $m1_l12_t3_solution$tasks = []
title = input()
tasks.append({"title": title, "done": False})
print("Добавлено")
$m1_l12_t3_solution$, 1, 40, $m1_l12_t3_topic$Месяц 1. Python Core — Проект$m1_l12_t3_topic$, $m1_l12_t3_lang$python$m1_l12_t3_lang$, $m1_l12_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Задача — словарь с ключами `title` и `done`.","Добавь словарь через `append`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l12_t3_policy$::jsonb),
  ($m1_l12_t4_title$Показать$m1_l12_t4_title$, $m1_l12_t4_statement$**Коротко:** Выведите список задач.

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
```$m1_l12_t4_statement$, $m1_l12_t4_starter$tasks = [{"title": "Купить хлеб", "done": False}, {"title": "Сделать урок", "done": True}]
$m1_l12_t4_starter$, $m1_l12_t4_solution$tasks = [{"title": "Купить хлеб", "done": False}, {"title": "Сделать урок", "done": True}]
for i in range(len(tasks)):
    task = tasks[i]
    mark = "[x]" if task["done"] else "[ ]"
    print(str(i + 1) + ".", mark, task["title"])
$m1_l12_t4_solution$, 2, 55, $m1_l12_t4_topic$Месяц 1. Python Core — Проект$m1_l12_t4_topic$, $m1_l12_t4_lang$python$m1_l12_t4_lang$, $m1_l12_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Номер можно получить через `range(len(tasks))`.","Статус зависит от `done`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l12_t4_policy$::jsonb),
  ($m1_l12_t5_title$Выполнить$m1_l12_t5_title$, $m1_l12_t5_statement$**Коротко:** Отметьте задачу выполненной.

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
```$m1_l12_t5_statement$, $m1_l12_t5_starter$tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
$m1_l12_t5_starter$, $m1_l12_t5_solution$tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
tasks[number - 1]["done"] = True
print("Готово")
$m1_l12_t5_solution$, 2, 55, $m1_l12_t5_topic$Месяц 1. Python Core — Проект$m1_l12_t5_topic$, $m1_l12_t5_lang$python$m1_l12_t5_lang$, $m1_l12_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Номер в интерфейсе начинается с 1.","Индекс в списке: `number - 1`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l12_t5_policy$::jsonb),
  ($m1_l12_t6_title$Удалить$m1_l12_t6_title$, $m1_l12_t6_statement$**Коротко:** Удалите задачу по номеру.

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
```$m1_l12_t6_statement$, $m1_l12_t6_starter$tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
$m1_l12_t6_starter$, $m1_l12_t6_solution$tasks = [{"title": "A", "done": False}, {"title": "B", "done": False}]
number = int(input())
del tasks[number - 1]
print(len(tasks))
$m1_l12_t6_solution$, 2, 55, $m1_l12_t6_topic$Месяц 1. Python Core — Проект$m1_l12_t6_topic$, $m1_l12_t6_lang$python$m1_l12_t6_lang$, $m1_l12_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Индекс: `number - 1`.","Удалить можно через `del tasks[index]`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l12_t6_policy$::jsonb),
  ($m1_l12_t7_title$Ошибки$m1_l12_t7_title$, $m1_l12_t7_statement$**Коротко:** Проверьте неверный номер.

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
```$m1_l12_t7_statement$, $m1_l12_t7_starter$tasks = [{"title": "A"}, {"title": "B"}]
number = int(input())
$m1_l12_t7_starter$, $m1_l12_t7_solution$tasks = [{"title": "A"}, {"title": "B"}]
number = int(input())
if number >= 1 and number <= len(tasks):
    print("OK")
else:
    print("Нет такой задачи")
$m1_l12_t7_solution$, 2, 55, $m1_l12_t7_topic$Месяц 1. Python Core — Проект$m1_l12_t7_topic$, $m1_l12_t7_lang$python$m1_l12_t7_lang$, $m1_l12_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Допустимые номера: от 1 до `len(tasks)`.","Используй условие с `and`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l12_t7_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l12_ttitle_3$Добавить$m1_l12_ttitle_3$,
    $m1_l12_ttitle_4$Показать$m1_l12_ttitle_4$,
    $m1_l12_ttitle_5$Выполнить$m1_l12_ttitle_5$,
    $m1_l12_ttitle_6$Удалить$m1_l12_ttitle_6$,
    $m1_l12_ttitle_7$Ошибки$m1_l12_ttitle_7$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l12_test_3_1_title$Добавить$m1_l12_test_3_1_title$, $m1_l12_test_3_1_input$Купить хлеб$m1_l12_test_3_1_input$, $m1_l12_test_3_1_expected$Добавлено$m1_l12_test_3_1_expected$, FALSE, 1),
  ($m1_l12_test_4_1_title$Показать$m1_l12_test_4_1_title$, $m1_l12_test_4_1_input$$m1_l12_test_4_1_input$, $m1_l12_test_4_1_expected$1. [ ] Купить хлеб
2. [x] Сделать урок$m1_l12_test_4_1_expected$, FALSE, 1),
  ($m1_l12_test_5_1_title$Выполнить$m1_l12_test_5_1_title$, $m1_l12_test_5_1_input$1$m1_l12_test_5_1_input$, $m1_l12_test_5_1_expected$Готово$m1_l12_test_5_1_expected$, FALSE, 1),
  ($m1_l12_test_5_2_title$Выполнить$m1_l12_test_5_2_title$, $m1_l12_test_5_2_input$2$m1_l12_test_5_2_input$, $m1_l12_test_5_2_expected$Готово$m1_l12_test_5_2_expected$, TRUE, 2),
  ($m1_l12_test_6_1_title$Удалить$m1_l12_test_6_1_title$, $m1_l12_test_6_1_input$1$m1_l12_test_6_1_input$, $m1_l12_test_6_1_expected$1$m1_l12_test_6_1_expected$, FALSE, 1),
  ($m1_l12_test_6_2_title$Удалить$m1_l12_test_6_2_title$, $m1_l12_test_6_2_input$2$m1_l12_test_6_2_input$, $m1_l12_test_6_2_expected$1$m1_l12_test_6_2_expected$, TRUE, 2),
  ($m1_l12_test_7_1_title$Ошибки$m1_l12_test_7_1_title$, $m1_l12_test_7_1_input$3$m1_l12_test_7_1_input$, $m1_l12_test_7_1_expected$Нет такой задачи$m1_l12_test_7_1_expected$, FALSE, 1),
  ($m1_l12_test_7_2_title$Ошибки$m1_l12_test_7_2_title$, $m1_l12_test_7_2_input$2$m1_l12_test_7_2_input$, $m1_l12_test_7_2_expected$OK$m1_l12_test_7_2_expected$, TRUE, 2),
  ($m1_l12_test_7_3_title$Ошибки$m1_l12_test_7_3_title$, $m1_l12_test_7_3_input$0$m1_l12_test_7_3_input$, $m1_l12_test_7_3_expected$Нет такой задачи$m1_l12_test_7_3_expected$, TRUE, 3)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l12_b1_type$theory$m1_l12_b1_type$, $m1_l12_b1_title$Задача проекта$m1_l12_b1_title$, $m1_l12_b1_content$Итоговый проект модуля — консольный трекер задач.

Программа должна хранить задачи в списке словарей:
```python
tasks = []
```

Каждая задача:
```python
{"title": "Купить хлеб", "done": False}
```$m1_l12_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l12_b2_type$theory$m1_l12_b2_type$, $m1_l12_b2_title$Команды$m1_l12_b2_title$, $m1_l12_b2_content$Программа принимает команды:

| Команда | Действие |
|---|---|
| `add` | добавить задачу |
| `list` | показать задачи |
| `done` | отметить выполненной |
| `delete` | удалить задачу |
| `exit` | завершить программу |

После неизвестной команды вывести `Неизвестная команда`.$m1_l12_b2_content$, NULL, NULL::jsonb),
  (3, $m1_l12_b3_type$practice$m1_l12_b3_type$, $m1_l12_b3_title$Добавить$m1_l12_b3_title$, $m1_l12_b3_content$**Коротко:** Реализуйте добавление задачи.

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
```$m1_l12_b3_content$, $m1_l12_b3_task_title$Добавить$m1_l12_b3_task_title$, NULL::jsonb),
  (4, $m1_l12_b4_type$practice$m1_l12_b4_type$, $m1_l12_b4_title$Показать$m1_l12_b4_title$, $m1_l12_b4_content$**Коротко:** Выведите список задач.

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
```$m1_l12_b4_content$, $m1_l12_b4_task_title$Показать$m1_l12_b4_task_title$, NULL::jsonb),
  (5, $m1_l12_b5_type$practice$m1_l12_b5_type$, $m1_l12_b5_title$Выполнить$m1_l12_b5_title$, $m1_l12_b5_content$**Коротко:** Отметьте задачу выполненной.

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
```$m1_l12_b5_content$, $m1_l12_b5_task_title$Выполнить$m1_l12_b5_task_title$, NULL::jsonb),
  (6, $m1_l12_b6_type$practice$m1_l12_b6_type$, $m1_l12_b6_title$Удалить$m1_l12_b6_title$, $m1_l12_b6_content$**Коротко:** Удалите задачу по номеру.

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
```$m1_l12_b6_content$, $m1_l12_b6_task_title$Удалить$m1_l12_b6_task_title$, NULL::jsonb),
  (7, $m1_l12_b7_type$practice$m1_l12_b7_type$, $m1_l12_b7_title$Ошибки$m1_l12_b7_title$, $m1_l12_b7_content$**Коротко:** Проверьте неверный номер.

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
```$m1_l12_b7_content$, $m1_l12_b7_task_title$Ошибки$m1_l12_b7_task_title$, NULL::jsonb),
  (8, $m1_l12_b8_type$project$m1_l12_b8_type$, $m1_l12_b8_title$Сборка$m1_l12_b8_title$, $m1_l12_b8_content$**Коротко:** соберите полноценный трекер задач.

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
3. Номера задач начинаются с 1, индексы списка — с 0.$m1_l12_b8_content$, NULL, NULL::jsonb),
  (9, $m1_l12_b9_type$theory$m1_l12_b9_type$, $m1_l12_b9_title$README$m1_l12_b9_title$, $m1_l12_b9_content$Для проекта нужен короткий README:

```text
Название проекта
Что делает программа
Какие команды поддерживает
Как запустить
Пример работы
```$m1_l12_b9_content$, NULL, NULL::jsonb),
  (10, $m1_l12_b10_type$theory$m1_l12_b10_type$, $m1_l12_b10_title$AI-проверка$m1_l12_b10_title$, $m1_l12_b10_content$Этот шаг запускает AI-проверку проекта и показывает ученику результат по критериям. Ученик видит только итоговые замечания и рекомендации, но не внутренний prompt.$m1_l12_b10_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 1, lesson 13: Контроль
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 13
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 1 AND l.position = 13
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m1_l13_t2_title$Ввод и вывод$m1_l13_t2_title$, $m1_l13_t2_statement$**Коротко:** Соберите строку профиля.

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
```$m1_l13_t2_statement$, $m1_l13_t2_starter$name = input()
city = input()
$m1_l13_t2_starter$, $m1_l13_t2_solution$name = input()
city = input()
print(name, "из города", city)
$m1_l13_t2_solution$, 1, 40, $m1_l13_t2_topic$Месяц 1. Python Core — Контроль$m1_l13_t2_topic$, $m1_l13_t2_lang$python$m1_l13_t2_lang$, $m1_l13_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Выведи несколько значений через `print()`.","Следи за точным текстом."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l13_t2_policy$::jsonb),
  ($m1_l13_t3_title$Арифметика$m1_l13_t3_title$, $m1_l13_t3_statement$**Коротко:** Посчитайте оплату.

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
```$m1_l13_t3_statement$, $m1_l13_t3_starter$price = int(input())
count = int(input())
discount = int(input())
$m1_l13_t3_starter$, $m1_l13_t3_solution$price = int(input())
count = int(input())
discount = int(input())
print(price * count - discount)
$m1_l13_t3_solution$, 1, 45, $m1_l13_t3_topic$Месяц 1. Python Core — Контроль$m1_l13_t3_topic$, $m1_l13_t3_lang$python$m1_l13_t3_lang$, $m1_l13_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сначала умножение.","Потом вычитание скидки."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l13_t3_policy$::jsonb),
  ($m1_l13_t4_title$Условия$m1_l13_t4_title$, $m1_l13_t4_statement$**Коротко:** Определите доступ.

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
```$m1_l13_t4_statement$, $m1_l13_t4_starter$age = int(input())
$m1_l13_t4_starter$, $m1_l13_t4_solution$age = int(input())
if age < 18:
    print("Нет")
elif age < 65:
    print("Да")
else:
    print("Льготный")
$m1_l13_t4_solution$, 2, 60, $m1_l13_t4_topic$Месяц 1. Python Core — Контроль$m1_l13_t4_topic$, $m1_l13_t4_lang$python$m1_l13_t4_lang$, $m1_l13_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Границы: 18 и 65.","Порядок проверок важен."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l13_t4_policy$::jsonb),
  ($m1_l13_t5_title$Логика$m1_l13_t5_title$, $m1_l13_t5_statement$**Коротко:** Проверьте вход в систему.

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
```$m1_l13_t5_statement$, $m1_l13_t5_starter$role = input()
blocked = input()
$m1_l13_t5_starter$, $m1_l13_t5_solution$role = input()
blocked = input()
if (role == "admin" or role == "moderator") and blocked == "no":
    print("Доступ")
else:
    print("Нет доступа")
$m1_l13_t5_solution$, 2, 65, $m1_l13_t5_topic$Месяц 1. Python Core — Контроль$m1_l13_t5_topic$, $m1_l13_t5_lang$python$m1_l13_t5_lang$, $m1_l13_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Роль проверяй через `or`.","Блокировки нет: `blocked == \"no\"`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l13_t5_policy$::jsonb),
  ($m1_l13_t6_title$Циклы$m1_l13_t6_title$, $m1_l13_t6_statement$**Коротко:** Найдите сумму чётных.

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
```$m1_l13_t6_statement$, $m1_l13_t6_starter$n = int(input())
total = 0
$m1_l13_t6_starter$, $m1_l13_t6_solution$n = int(input())
total = 0
for i in range(n):
    number = int(input())
    if number % 2 == 0:
        total = total + number
print(total)
$m1_l13_t6_solution$, 2, 70, $m1_l13_t6_topic$Месяц 1. Python Core — Контроль$m1_l13_t6_topic$, $m1_l13_t6_lang$python$m1_l13_t6_lang$, $m1_l13_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Чётность: `% 2 == 0`.","Суммируй только подходящие числа."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l13_t6_policy$::jsonb),
  ($m1_l13_t7_title$Строки$m1_l13_t7_title$, $m1_l13_t7_statement$**Коротко:** Найдите короткое имя.

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
```$m1_l13_t7_statement$, $m1_l13_t7_starter$names = input().split()
$m1_l13_t7_starter$, $m1_l13_t7_solution$names = input().split()
found = False
for name in names:
    if len(name) < 4:
        print(name)
        found = True
        break
if not found:
    print("Не найдено")
$m1_l13_t7_solution$, 3, 75, $m1_l13_t7_topic$Месяц 1. Python Core — Контроль$m1_l13_t7_topic$, $m1_l13_t7_lang$python$m1_l13_t7_lang$, $m1_l13_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Нужен флаг `found`.","После первого найденного имени можно использовать `break`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l13_t7_policy$::jsonb),
  ($m1_l13_t8_title$Списки$m1_l13_t8_title$, $m1_l13_t8_statement$**Коротко:** Посчитайте средний балл.

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
```$m1_l13_t8_statement$, $m1_l13_t8_starter$grades = input().split()
$m1_l13_t8_starter$, $m1_l13_t8_solution$grades = input().split()
total = 0
for grade in grades:
    total = total + int(grade)
avg = total / len(grades)
print(round(avg, 2))
$m1_l13_t8_solution$, 2, 70, $m1_l13_t8_topic$Месяц 1. Python Core — Контроль$m1_l13_t8_topic$, $m1_l13_t8_lang$python$m1_l13_t8_lang$, $m1_l13_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сложи числа и раздели на количество.","Количество элементов: `len(grades)`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l13_t8_policy$::jsonb),
  ($m1_l13_t9_title$Словари$m1_l13_t9_title$, $m1_l13_t9_statement$**Коротко:** Найдите самый частый товар.

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
```$m1_l13_t9_statement$, $m1_l13_t9_starter$items = input().split()
$m1_l13_t9_starter$, $m1_l13_t9_solution$items = input().split()
counts = {}
for item in items:
    counts[item] = counts.get(item, 0) + 1
best = items[0]
for item in items:
    if counts[item] > counts[best]:
        best = item
print(best)
$m1_l13_t9_solution$, 3, 85, $m1_l13_t9_topic$Месяц 1. Python Core — Контроль$m1_l13_t9_topic$, $m1_l13_t9_lang$python$m1_l13_t9_lang$, $m1_l13_t9_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Сначала посчитай частоты словарём.","Потом пройди по исходному списку и найди максимум."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l13_t9_policy$::jsonb),
  ($m1_l13_t10_title$Функции$m1_l13_t10_title$, $m1_l13_t10_statement$**Коротко:** Напишите функцию скидки.

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
```$m1_l13_t10_statement$, $m1_l13_t10_starter$def final_price(price, discount):
    # return ...
$m1_l13_t10_starter$, $m1_l13_t10_solution$def final_price(price, discount):
    return price - price * discount / 100

price = float(input())
discount = float(input())
print(round(final_price(price, discount), 2))
$m1_l13_t10_solution$, 3, 85, $m1_l13_t10_topic$Месяц 1. Python Core — Контроль$m1_l13_t10_topic$, $m1_l13_t10_lang$python$m1_l13_t10_lang$, $m1_l13_t10_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":["Скидка: `price * discount / 100`.","Функция должна использовать `return`."],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m1_l13_t10_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
    $m1_l13_ttitle_2$Ввод и вывод$m1_l13_ttitle_2$,
    $m1_l13_ttitle_3$Арифметика$m1_l13_ttitle_3$,
    $m1_l13_ttitle_4$Условия$m1_l13_ttitle_4$,
    $m1_l13_ttitle_5$Логика$m1_l13_ttitle_5$,
    $m1_l13_ttitle_6$Циклы$m1_l13_ttitle_6$,
    $m1_l13_ttitle_7$Строки$m1_l13_ttitle_7$,
    $m1_l13_ttitle_8$Списки$m1_l13_ttitle_8$,
    $m1_l13_ttitle_9$Словари$m1_l13_ttitle_9$,
    $m1_l13_ttitle_10$Функции$m1_l13_ttitle_10$
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
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m1_l13_test_2_1_title$Ввод и вывод$m1_l13_test_2_1_title$, $m1_l13_test_2_1_input$Анна
Москва$m1_l13_test_2_1_input$, $m1_l13_test_2_1_expected$Анна из города Москва$m1_l13_test_2_1_expected$, FALSE, 1),
  ($m1_l13_test_2_2_title$Ввод и вывод$m1_l13_test_2_2_title$, $m1_l13_test_2_2_input$Олег
Казань$m1_l13_test_2_2_input$, $m1_l13_test_2_2_expected$Олег из города Казань$m1_l13_test_2_2_expected$, TRUE, 2),
  ($m1_l13_test_3_1_title$Арифметика$m1_l13_test_3_1_title$, $m1_l13_test_3_1_input$100
3
50$m1_l13_test_3_1_input$, $m1_l13_test_3_1_expected$250$m1_l13_test_3_1_expected$, FALSE, 1),
  ($m1_l13_test_3_2_title$Арифметика$m1_l13_test_3_2_title$, $m1_l13_test_3_2_input$10
1
0$m1_l13_test_3_2_input$, $m1_l13_test_3_2_expected$10$m1_l13_test_3_2_expected$, TRUE, 2),
  ($m1_l13_test_4_1_title$Условия$m1_l13_test_4_1_title$, $m1_l13_test_4_1_input$17$m1_l13_test_4_1_input$, $m1_l13_test_4_1_expected$Нет$m1_l13_test_4_1_expected$, FALSE, 1),
  ($m1_l13_test_4_2_title$Условия$m1_l13_test_4_2_title$, $m1_l13_test_4_2_input$18$m1_l13_test_4_2_input$, $m1_l13_test_4_2_expected$Да$m1_l13_test_4_2_expected$, TRUE, 2),
  ($m1_l13_test_4_3_title$Условия$m1_l13_test_4_3_title$, $m1_l13_test_4_3_input$64$m1_l13_test_4_3_input$, $m1_l13_test_4_3_expected$Да$m1_l13_test_4_3_expected$, TRUE, 3),
  ($m1_l13_test_4_4_title$Условия$m1_l13_test_4_4_title$, $m1_l13_test_4_4_input$65$m1_l13_test_4_4_input$, $m1_l13_test_4_4_expected$Льготный$m1_l13_test_4_4_expected$, TRUE, 4),
  ($m1_l13_test_5_1_title$Логика$m1_l13_test_5_1_title$, $m1_l13_test_5_1_input$admin
no$m1_l13_test_5_1_input$, $m1_l13_test_5_1_expected$Доступ$m1_l13_test_5_1_expected$, FALSE, 1),
  ($m1_l13_test_5_2_title$Логика$m1_l13_test_5_2_title$, $m1_l13_test_5_2_input$moderator
no$m1_l13_test_5_2_input$, $m1_l13_test_5_2_expected$Доступ$m1_l13_test_5_2_expected$, TRUE, 2),
  ($m1_l13_test_5_3_title$Логика$m1_l13_test_5_3_title$, $m1_l13_test_5_3_input$admin
yes$m1_l13_test_5_3_input$, $m1_l13_test_5_3_expected$Нет доступа$m1_l13_test_5_3_expected$, TRUE, 3),
  ($m1_l13_test_5_4_title$Логика$m1_l13_test_5_4_title$, $m1_l13_test_5_4_input$user
no$m1_l13_test_5_4_input$, $m1_l13_test_5_4_expected$Нет доступа$m1_l13_test_5_4_expected$, TRUE, 4),
  ($m1_l13_test_6_1_title$Циклы$m1_l13_test_6_1_title$, $m1_l13_test_6_1_input$5
1
2
3
4
5$m1_l13_test_6_1_input$, $m1_l13_test_6_1_expected$6$m1_l13_test_6_1_expected$, FALSE, 1),
  ($m1_l13_test_6_2_title$Циклы$m1_l13_test_6_2_title$, $m1_l13_test_6_2_input$3
1
3
5$m1_l13_test_6_2_input$, $m1_l13_test_6_2_expected$0$m1_l13_test_6_2_expected$, TRUE, 2),
  ($m1_l13_test_6_3_title$Циклы$m1_l13_test_6_3_title$, $m1_l13_test_6_3_input$2
-2
4$m1_l13_test_6_3_input$, $m1_l13_test_6_3_expected$2$m1_l13_test_6_3_expected$, TRUE, 3),
  ($m1_l13_test_7_1_title$Строки$m1_l13_test_7_1_title$, $m1_l13_test_7_1_input$Анна Ли Олег$m1_l13_test_7_1_input$, $m1_l13_test_7_1_expected$Ли$m1_l13_test_7_1_expected$, FALSE, 1),
  ($m1_l13_test_7_2_title$Строки$m1_l13_test_7_2_title$, $m1_l13_test_7_2_input$Анна Олег$m1_l13_test_7_2_input$, $m1_l13_test_7_2_expected$Не найдено$m1_l13_test_7_2_expected$, TRUE, 2),
  ($m1_l13_test_7_3_title$Строки$m1_l13_test_7_3_title$, $m1_l13_test_7_3_input$A B$m1_l13_test_7_3_input$, $m1_l13_test_7_3_expected$A$m1_l13_test_7_3_expected$, TRUE, 3),
  ($m1_l13_test_8_1_title$Списки$m1_l13_test_8_1_title$, $m1_l13_test_8_1_input$5 4 3$m1_l13_test_8_1_input$, $m1_l13_test_8_1_expected$4.0$m1_l13_test_8_1_expected$, FALSE, 1),
  ($m1_l13_test_8_2_title$Списки$m1_l13_test_8_2_title$, $m1_l13_test_8_2_input$1 2$m1_l13_test_8_2_input$, $m1_l13_test_8_2_expected$1.5$m1_l13_test_8_2_expected$, TRUE, 2),
  ($m1_l13_test_8_3_title$Списки$m1_l13_test_8_3_title$, $m1_l13_test_8_3_input$1 1 2$m1_l13_test_8_3_input$, $m1_l13_test_8_3_expected$1.33$m1_l13_test_8_3_expected$, TRUE, 3),
  ($m1_l13_test_9_1_title$Словари$m1_l13_test_9_1_title$, $m1_l13_test_9_1_input$чай кофе чай сок$m1_l13_test_9_1_input$, $m1_l13_test_9_1_expected$чай$m1_l13_test_9_1_expected$, FALSE, 1),
  ($m1_l13_test_9_2_title$Словари$m1_l13_test_9_2_title$, $m1_l13_test_9_2_input$a b a b$m1_l13_test_9_2_input$, $m1_l13_test_9_2_expected$a$m1_l13_test_9_2_expected$, TRUE, 2),
  ($m1_l13_test_9_3_title$Словари$m1_l13_test_9_3_title$, $m1_l13_test_9_3_input$x y y x y$m1_l13_test_9_3_input$, $m1_l13_test_9_3_expected$y$m1_l13_test_9_3_expected$, TRUE, 3),
  ($m1_l13_test_10_1_title$Функции$m1_l13_test_10_1_title$, $m1_l13_test_10_1_input$1000
10$m1_l13_test_10_1_input$, $m1_l13_test_10_1_expected$900.0$m1_l13_test_10_1_expected$, FALSE, 1),
  ($m1_l13_test_10_2_title$Функции$m1_l13_test_10_2_title$, $m1_l13_test_10_2_input$500
25$m1_l13_test_10_2_input$, $m1_l13_test_10_2_expected$375.0$m1_l13_test_10_2_expected$, TRUE, 2),
  ($m1_l13_test_10_3_title$Функции$m1_l13_test_10_3_title$, $m1_l13_test_10_3_input$99.9
5$m1_l13_test_10_3_input$, $m1_l13_test_10_3_expected$94.91$m1_l13_test_10_3_expected$, TRUE, 3)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

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
  (1, $m1_l13_b1_type$theory$m1_l13_b1_type$, $m1_l13_b1_title$Инструкция$m1_l13_b1_title$, $m1_l13_b1_content$Контрольный урок проверяет весь модуль. Условия короткие, подсказок меньше.

Правила:

- не добавляй лишний текст;
- используй `input()` без приглашений;
- проверяй граничные случаи;
- если задача про функции, функция должна возвращать результат через `return`.$m1_l13_b1_content$, NULL, NULL::jsonb),
  (2, $m1_l13_b2_type$practice$m1_l13_b2_type$, $m1_l13_b2_title$Ввод и вывод$m1_l13_b2_title$, $m1_l13_b2_content$**Коротко:** Соберите строку профиля.

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
```$m1_l13_b2_content$, $m1_l13_b2_task_title$Ввод и вывод$m1_l13_b2_task_title$, NULL::jsonb),
  (3, $m1_l13_b3_type$practice$m1_l13_b3_type$, $m1_l13_b3_title$Арифметика$m1_l13_b3_title$, $m1_l13_b3_content$**Коротко:** Посчитайте оплату.

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
```$m1_l13_b3_content$, $m1_l13_b3_task_title$Арифметика$m1_l13_b3_task_title$, NULL::jsonb),
  (4, $m1_l13_b4_type$practice$m1_l13_b4_type$, $m1_l13_b4_title$Условия$m1_l13_b4_title$, $m1_l13_b4_content$**Коротко:** Определите доступ.

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
```$m1_l13_b4_content$, $m1_l13_b4_task_title$Условия$m1_l13_b4_task_title$, NULL::jsonb),
  (5, $m1_l13_b5_type$practice$m1_l13_b5_type$, $m1_l13_b5_title$Логика$m1_l13_b5_title$, $m1_l13_b5_content$**Коротко:** Проверьте вход в систему.

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
```$m1_l13_b5_content$, $m1_l13_b5_task_title$Логика$m1_l13_b5_task_title$, NULL::jsonb),
  (6, $m1_l13_b6_type$practice$m1_l13_b6_type$, $m1_l13_b6_title$Циклы$m1_l13_b6_title$, $m1_l13_b6_content$**Коротко:** Найдите сумму чётных.

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
```$m1_l13_b6_content$, $m1_l13_b6_task_title$Циклы$m1_l13_b6_task_title$, NULL::jsonb),
  (7, $m1_l13_b7_type$practice$m1_l13_b7_type$, $m1_l13_b7_title$Строки$m1_l13_b7_title$, $m1_l13_b7_content$**Коротко:** Найдите короткое имя.

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
```$m1_l13_b7_content$, $m1_l13_b7_task_title$Строки$m1_l13_b7_task_title$, NULL::jsonb),
  (8, $m1_l13_b8_type$practice$m1_l13_b8_type$, $m1_l13_b8_title$Списки$m1_l13_b8_title$, $m1_l13_b8_content$**Коротко:** Посчитайте средний балл.

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
```$m1_l13_b8_content$, $m1_l13_b8_task_title$Списки$m1_l13_b8_task_title$, NULL::jsonb),
  (9, $m1_l13_b9_type$practice$m1_l13_b9_type$, $m1_l13_b9_title$Словари$m1_l13_b9_title$, $m1_l13_b9_content$**Коротко:** Найдите самый частый товар.

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
```$m1_l13_b9_content$, $m1_l13_b9_task_title$Словари$m1_l13_b9_task_title$, NULL::jsonb),
  (10, $m1_l13_b10_type$practice$m1_l13_b10_type$, $m1_l13_b10_title$Функции$m1_l13_b10_title$, $m1_l13_b10_content$**Коротко:** Напишите функцию скидки.

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
```$m1_l13_b10_content$, $m1_l13_b10_task_title$Функции$m1_l13_b10_task_title$, NULL::jsonb),
  (11, $m1_l13_b11_type$theory$m1_l13_b11_type$, $m1_l13_b11_title$Результат$m1_l13_b11_title$, $m1_l13_b11_content$После контрольного урока ученик должен уметь:

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
> Напиши `a = int(input()); b = int(input()); print(a + b)`.
# Месяц 2. Python Hard

Цель месяца: перевести ученика от «пишу скрипты» к «пишу структурированный код». После месяца ученик должен понимать ООП, типы, исключения, генераторы, декораторы, контекстные менеджеры, основы конкурентности и алгоритмического мышления.

## Сетка месяца

| Урок | Название | Фокус | Проверка |
|---:|---|---|---|
| 1 | Классы | class, объект, метод | автотесты |
| 2 | Атрибуты | состояние, валидация, property | автотесты |
| 3 | Dunder | `__str__`, `__eq__`, `__len__` | автотесты |
| 4 | Наследование | наследование, `super`, полиморфизм | автотесты |
| 5 | ООП принципы | SRP, композиция, сервисы | AI-check |
| 6 | Типизация | type hints, коллекции, Optional | автотесты |
| 7 | Исключения | custom errors, `else/finally` | автотесты |
| 8 | Итераторы | iterable, iterator | автотесты |
| 9 | Генераторы | `yield`, lazy evaluation | автотесты |
| 10 | Декораторы | wrapper, params, class decorator | автотесты |
| 11 | Context | `with`, `__enter__`, `__exit__` | автотесты |
| 12 | Threads | I/O concurrency, lock | автотесты + AI |
| 13 | Processes | CPU tasks, Pool | теория + практика |
| 14 | Asyncio | event loop, async/await | автотесты |
| 15 | Алгоритмы | Big O, stack, queue, hash | автотесты |
| 16 | Проект bot | async task bot/service | AI-check |

---$m1_l13_b11_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2: Месяц 2. Python Hard
WITH module_ref AS (
  SELECT m.id AS module_id
  FROM modules m
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2
), lesson_seed(position, title, content_md) AS (
  VALUES
  (1, $m2_l1_title$Классы$m2_l1_title$, $m2_l1_content$Создаём собственные типы данных.$m2_l1_content$),
  (2, $m2_l2_title$Атрибуты$m2_l2_title$, $m2_l2_content$Контролируем состояние объекта.$m2_l2_content$),
  (3, $m2_l3_title$Dunder$m2_l3_title$, $m2_l3_content$Магические методы делают объекты удобными.$m2_l3_content$),
  (4, $m2_l4_title$Наследование$m2_l4_title$, $m2_l4_content$Общий код в базовом классе.$m2_l4_content$),
  (5, $m2_l5_title$ООП принципы$m2_l5_title$, $m2_l5_content$Как не превратить классы в хаос.$m2_l5_content$),
  (6, $m2_l6_title$Типизация$m2_l6_title$, $m2_l6_content$Типы помогают читать и проверять код.$m2_l6_content$),
  (7, $m2_l7_title$Исключения$m2_l7_title$, $m2_l7_content$Ошибки нужно обрабатывать явно.$m2_l7_content$),
  (8, $m2_l8_title$Итераторы$m2_l8_title$, $m2_l8_content$Как работает перебор в Python.$m2_l8_content$),
  (9, $m2_l9_title$Генераторы$m2_l9_title$, $m2_l9_content$Ленивые последовательности через `yield`.$m2_l9_content$),
  (10, $m2_l10_title$Декораторы$m2_l10_title$, $m2_l10_content$Оборачиваем функцию дополнительной логикой.$m2_l10_content$),
  (11, $m2_l11_title$Context$m2_l11_title$, $m2_l11_content$`with` гарантирует закрытие ресурса.$m2_l11_content$),
  (12, $m2_l12_title$Threads$m2_l12_title$, $m2_l12_content$Потоки полезны для ожидания I/O.$m2_l12_content$),
  (13, $m2_l13_title$Processes$m2_l13_title$, $m2_l13_content$Процессы подходят для CPU-задач.$m2_l13_content$),
  (14, $m2_l14_title$Asyncio$m2_l14_title$, $m2_l14_content$Асинхронность для большого числа ожиданий.$m2_l14_content$),
  (15, $m2_l15_title$Алгоритмы$m2_l15_title$, $m2_l15_content$Оцениваем скорость и память.$m2_l15_content$),
  (16, $m2_l16_title$Проект bot$m2_l16_title$, $m2_l16_content$Асинхронный бот или сервис очереди задач.$m2_l16_content$)
)
INSERT INTO lessons(module_id, title, content_md, position, is_published)
SELECT mr.module_id, ls.title, ls.content_md, ls.position, TRUE
FROM module_ref mr
CROSS JOIN lesson_seed ls
ON CONFLICT (module_id, position) DO UPDATE
SET title = EXCLUDED.title,
    content_md = EXCLUDED.content_md,
    is_published = TRUE,
    updated_at = NOW();

-- Module 2, lesson 1: Классы
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 1
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 1
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l1_t2_title$Первый класс$m2_l1_t2_title$, $m2_l1_t2_statement$**Коротко:** создай класс `User` и объект пользователя.

### Условие

Создай класс `User`. Создай объект этого класса. Добавь объекту атрибут `name` со значением `"Анна"`. Выведи имя.

### Выход

```text
Анна
```$m2_l1_t2_statement$, $m2_l1_t2_starter$class User:
    pass

user = User()
# добавь name

print(...)
$m2_l1_t2_starter$, $m2_l1_t2_solution$class User:
    pass

user = User()
user.name = "Анна"
print(user.name)
$m2_l1_t2_solution$, 2, 50, $m2_l1_t2_topic$Месяц 2. Python Hard — Классы$m2_l1_t2_topic$, $m2_l1_t2_lang$python$m2_l1_t2_lang$, $m2_l1_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l1_t2_policy$::jsonb),
  ($m2_l1_t4_title$User$m2_l1_t4_title$, $m2_l1_t4_statement$**Коротко:** создай пользователя через `__init__`.

### Условие

Создай класс `User`, который принимает `name` и `age`. Создай пользователя `"Олег"`, `25`. Выведи:

```text
Олег 25
```$m2_l1_t4_statement$, $m2_l1_t4_starter$$m2_l1_t4_starter$, $m2_l1_t4_solution$class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

user = User("Олег", 25)
print(user.name, user.age)
$m2_l1_t4_solution$, 2, 50, $m2_l1_t4_topic$Месяц 2. Python Hard — Классы$m2_l1_t4_topic$, $m2_l1_t4_lang$python$m2_l1_t4_lang$, $m2_l1_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l1_t4_policy$::jsonb),
  ($m2_l1_t6_title$BankAccount$m2_l1_t6_title$, $m2_l1_t6_statement$**Коротко:** создай счёт с пополнением.

### Условие

Создай класс `BankAccount`.

- атрибут `balance`;
- метод `deposit(amount)` увеличивает баланс.

Создай счёт с балансом `100`. Пополни на `50`. Выведи баланс.

### Выход

```text
150
```$m2_l1_t6_statement$, $m2_l1_t6_starter$$m2_l1_t6_starter$, $m2_l1_t6_solution$class BankAccount:
    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

account = BankAccount(100)
account.deposit(50)
print(account.balance)
$m2_l1_t6_solution$, 2, 50, $m2_l1_t6_topic$Месяц 2. Python Hard — Классы$m2_l1_t6_topic$, $m2_l1_t6_lang$python$m2_l1_t6_lang$, $m2_l1_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l1_t6_policy$::jsonb),
  ($m2_l1_t7_title$Ошибка self$m2_l1_t7_title$, $m2_l1_t7_statement$**Коротко:** исправь метод.

### Выход

```text
Анна
```$m2_l1_t7_statement$, $m2_l1_t7_starter$$m2_l1_t7_starter$, $m2_l1_t7_solution$class User:
    def __init__(self, name):
        self.name = name

user = User("Анна")
print(user.name)
$m2_l1_t7_solution$, 2, 50, $m2_l1_t7_topic$Месяц 2. Python Hard — Классы$m2_l1_t7_topic$, $m2_l1_t7_lang$python$m2_l1_t7_lang$, $m2_l1_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l1_t7_policy$::jsonb),
  ($m2_l1_t8_title$Контроль$m2_l1_t8_title$, $m2_l1_t8_statement$**Коротко:** создай класс задачи.

### Условие

Создай класс `Task`.

Атрибуты:

- `title`;
- `done`, по умолчанию `False`.

Методы:

- `mark_done()` — меняет `done` на `True`;
- `status()` — возвращает `"done"` или `"active"`.

Создай задачу `"Учить Python"`, отметь выполненной и выведи статус.

### Выход

```text
done
```

---$m2_l1_t8_statement$, $m2_l1_t8_starter$$m2_l1_t8_starter$, $m2_l1_t8_solution$class Task:
    def __init__(self, title):
        self.title = title
        self.done = False

    def mark_done(self):
        self.done = True

    def status(self):
        if self.done:
            return "done"
        return "active"

task = Task("Учить Python")
task.mark_done()
print(task.status())
$m2_l1_t8_solution$, 2, 50, $m2_l1_t8_topic$Месяц 2. Python Hard — Классы$m2_l1_t8_topic$, $m2_l1_t8_lang$python$m2_l1_t8_lang$, $m2_l1_t8_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l1_t8_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 1
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l1_ttitle_2$Первый класс$m2_l1_ttitle_2$,
    $m2_l1_ttitle_4$User$m2_l1_ttitle_4$,
    $m2_l1_ttitle_6$BankAccount$m2_l1_ttitle_6$,
    $m2_l1_ttitle_7$Ошибка self$m2_l1_ttitle_7$,
    $m2_l1_ttitle_8$Контроль$m2_l1_ttitle_8$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 1
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l1_test_2_1_title$Первый класс$m2_l1_test_2_1_title$, $m2_l1_test_2_1_input$$m2_l1_test_2_1_input$, $m2_l1_test_2_1_expected$Анна$m2_l1_test_2_1_expected$, FALSE, 1),
  ($m2_l1_test_4_1_title$User$m2_l1_test_4_1_title$, $m2_l1_test_4_1_input$$m2_l1_test_4_1_input$, $m2_l1_test_4_1_expected$Олег 25$m2_l1_test_4_1_expected$, FALSE, 1),
  ($m2_l1_test_6_1_title$BankAccount$m2_l1_test_6_1_title$, $m2_l1_test_6_1_input$$m2_l1_test_6_1_input$, $m2_l1_test_6_1_expected$150$m2_l1_test_6_1_expected$, FALSE, 1),
  ($m2_l1_test_7_1_title$Ошибка self$m2_l1_test_7_1_title$, $m2_l1_test_7_1_input$$m2_l1_test_7_1_input$, $m2_l1_test_7_1_expected$Анна$m2_l1_test_7_1_expected$, FALSE, 1),
  ($m2_l1_test_8_1_title$Контроль$m2_l1_test_8_1_title$, $m2_l1_test_8_1_input$$m2_l1_test_8_1_input$, $m2_l1_test_8_1_expected$done$m2_l1_test_8_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 1
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l1_b1_type$theory$m2_l1_b1_type$, $m2_l1_b1_title$Зачем class$m2_l1_b1_title$, $m2_l1_b1_content$Класс нужен, когда у объекта есть данные и поведение.

```python
class User:
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        return "Привет, " + self.name
```

Класс описывает тип объекта. Объект — конкретный экземпляр класса.$m2_l1_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l1_b2_type$practice$m2_l1_b2_type$, $m2_l1_b2_title$Первый класс$m2_l1_b2_title$, $m2_l1_b2_content$**Коротко:** создай класс `User` и объект пользователя.

### Условие

Создай класс `User`. Создай объект этого класса. Добавь объекту атрибут `name` со значением `"Анна"`. Выведи имя.

### Выход

```text
Анна
```$m2_l1_b2_content$, $m2_l1_b2_task_title$Первый класс$m2_l1_b2_task_title$, NULL::jsonb),
  (3, $m2_l1_b3_type$theory$m2_l1_b3_type$, $m2_l1_b3_title$__init__$m2_l1_b3_title$, $m2_l1_b3_content$`__init__` вызывается при создании объекта.

```python
class User:
    def __init__(self, name):
        self.name = name

user = User("Анна")
print(user.name)
```

`self` — это сам объект. Через `self.name` мы сохраняем значение внутри объекта.$m2_l1_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l1_b4_type$practice$m2_l1_b4_type$, $m2_l1_b4_title$User$m2_l1_b4_title$, $m2_l1_b4_content$**Коротко:** создай пользователя через `__init__`.

### Условие

Создай класс `User`, который принимает `name` и `age`. Создай пользователя `"Олег"`, `25`. Выведи:

```text
Олег 25
```$m2_l1_b4_content$, $m2_l1_b4_task_title$User$m2_l1_b4_task_title$, NULL::jsonb),
  (5, $m2_l1_b5_type$theory$m2_l1_b5_type$, $m2_l1_b5_title$Методы$m2_l1_b5_title$, $m2_l1_b5_content$Метод — функция внутри класса.

```python
class User:
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        print("Привет,", self.name)
```

Метод работает с данными объекта через `self`.$m2_l1_b5_content$, NULL, NULL::jsonb),
  (6, $m2_l1_b6_type$practice$m2_l1_b6_type$, $m2_l1_b6_title$BankAccount$m2_l1_b6_title$, $m2_l1_b6_content$**Коротко:** создай счёт с пополнением.

### Условие

Создай класс `BankAccount`.

- атрибут `balance`;
- метод `deposit(amount)` увеличивает баланс.

Создай счёт с балансом `100`. Пополни на `50`. Выведи баланс.

### Выход

```text
150
```$m2_l1_b6_content$, $m2_l1_b6_task_title$BankAccount$m2_l1_b6_task_title$, NULL::jsonb),
  (7, $m2_l1_b7_type$practice$m2_l1_b7_type$, $m2_l1_b7_title$Ошибка self$m2_l1_b7_title$, $m2_l1_b7_content$**Коротко:** исправь метод.

### Выход

```text
Анна
```$m2_l1_b7_content$, $m2_l1_b7_task_title$Ошибка self$m2_l1_b7_task_title$, NULL::jsonb),
  (8, $m2_l1_b8_type$practice$m2_l1_b8_type$, $m2_l1_b8_title$Контроль$m2_l1_b8_title$, $m2_l1_b8_content$**Коротко:** создай класс задачи.

### Условие

Создай класс `Task`.

Атрибуты:

- `title`;
- `done`, по умолчанию `False`.

Методы:

- `mark_done()` — меняет `done` на `True`;
- `status()` — возвращает `"done"` или `"active"`.

Создай задачу `"Учить Python"`, отметь выполненной и выведи статус.

### Выход

```text
done
```

---$m2_l1_b8_content$, $m2_l1_b8_task_title$Контроль$m2_l1_b8_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 2: Атрибуты
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 2
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 2
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l2_t2_title$Product$m2_l2_t2_title$, $m2_l2_t2_statement$**Коротко:** посчитай цену товара.

### Условие

Создай класс `Product` с атрибутами `title`, `price`, `count`. Метод `total()` возвращает `price * count`.

Создай товар `"Книга"`, цена `500`, количество `3`. Выведи общую стоимость.

### Выход

```text
1500
```$m2_l2_t2_statement$, $m2_l2_t2_starter$$m2_l2_t2_starter$, $m2_l2_t2_solution$class Product:
    def __init__(self, title, price, count):
        self.title = title
        self.price = price
        self.count = count

    def total(self):
        return self.price * self.count

product = Product("Книга", 500, 3)
print(product.total())
$m2_l2_t2_solution$, 2, 50, $m2_l2_t2_topic$Месяц 2. Python Hard — Атрибуты$m2_l2_t2_topic$, $m2_l2_t2_lang$python$m2_l2_t2_lang$, $m2_l2_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l2_t2_policy$::jsonb),
  ($m2_l2_t4_title$Price$m2_l2_t4_title$, $m2_l2_t4_statement$**Коротко:** запрети отрицательную цену.

### Условие

Создай класс `Product`. Цена задаётся через `set_price(amount)`. Если `amount < 0`, цена не меняется.

Начальная цена `100`. Попробуй установить `-50`. Выведи цену.

### Выход

```text
100
```$m2_l2_t4_statement$, $m2_l2_t4_starter$$m2_l2_t4_starter$, $m2_l2_t4_solution$class Product:
    def __init__(self, price):
        self.price = price

    def set_price(self, amount):
        if amount >= 0:
            self.price = amount

product = Product(100)
product.set_price(-50)
print(product.price)
$m2_l2_t4_solution$, 2, 50, $m2_l2_t4_topic$Месяц 2. Python Hard — Атрибуты$m2_l2_t4_topic$, $m2_l2_t4_lang$python$m2_l2_t4_lang$, $m2_l2_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l2_t4_policy$::jsonb),
  ($m2_l2_t5_title$Cart$m2_l2_t5_title$, $m2_l2_t5_statement$**Коротко:** реализуй корзину.

### Условие

Создай класс `Cart`.

Методы:

- `add(price)` — добавляет цену товара;
- `total()` — возвращает сумму товаров;
- `clear()` — очищает корзину.

Добавь `100`, `200`, `50`. Выведи сумму. Очисти корзину. Выведи сумму снова.

### Выход

```text
350
0
```

---$m2_l2_t5_statement$, $m2_l2_t5_starter$$m2_l2_t5_starter$, $m2_l2_t5_solution$class Cart:
    def __init__(self):
        self.items = []

    def add(self, price):
        self.items.append(price)

    def total(self):
        return sum(self.items)

    def clear(self):
        self.items.clear()

cart = Cart()
cart.add(100)
cart.add(200)
cart.add(50)
print(cart.total())
cart.clear()
print(cart.total())
$m2_l2_t5_solution$, 2, 50, $m2_l2_t5_topic$Месяц 2. Python Hard — Атрибуты$m2_l2_t5_topic$, $m2_l2_t5_lang$python$m2_l2_t5_lang$, $m2_l2_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l2_t5_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 2
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l2_ttitle_2$Product$m2_l2_ttitle_2$,
    $m2_l2_ttitle_4$Price$m2_l2_ttitle_4$,
    $m2_l2_ttitle_5$Cart$m2_l2_ttitle_5$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 2
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l2_test_2_1_title$Product$m2_l2_test_2_1_title$, $m2_l2_test_2_1_input$$m2_l2_test_2_1_input$, $m2_l2_test_2_1_expected$1500$m2_l2_test_2_1_expected$, FALSE, 1),
  ($m2_l2_test_4_1_title$Price$m2_l2_test_4_1_title$, $m2_l2_test_4_1_input$$m2_l2_test_4_1_input$, $m2_l2_test_4_1_expected$100$m2_l2_test_4_1_expected$, FALSE, 1),
  ($m2_l2_test_5_1_title$Cart$m2_l2_test_5_1_title$, $m2_l2_test_5_1_input$$m2_l2_test_5_1_input$, $m2_l2_test_5_1_expected$350
0$m2_l2_test_5_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 2
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l2_b1_type$theory$m2_l2_b1_type$, $m2_l2_b1_title$Состояние$m2_l2_b1_title$, $m2_l2_b1_content$Состояние объекта — значения его атрибутов.

```python
class Product:
    def __init__(self, title, price):
        self.title = title
        self.price = price
```

Методы могут менять состояние. Поэтому важно не позволять объекту оказаться в неправильном состоянии: отрицательная цена, пустой email, баланс меньше нуля без причины.$m2_l2_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l2_b2_type$practice$m2_l2_b2_type$, $m2_l2_b2_title$Product$m2_l2_b2_title$, $m2_l2_b2_content$**Коротко:** посчитай цену товара.

### Условие

Создай класс `Product` с атрибутами `title`, `price`, `count`. Метод `total()` возвращает `price * count`.

Создай товар `"Книга"`, цена `500`, количество `3`. Выведи общую стоимость.

### Выход

```text
1500
```$m2_l2_b2_content$, $m2_l2_b2_task_title$Product$m2_l2_b2_task_title$, NULL::jsonb),
  (3, $m2_l2_b3_type$theory$m2_l2_b3_type$, $m2_l2_b3_title$Инкапсуляция$m2_l2_b3_title$, $m2_l2_b3_content$Инкапсуляция — контроль доступа к данным объекта.

В Python один `_` в имени означает: поле внутреннее, лучше не менять его напрямую.

```python
self._balance = balance
```

Это соглашение, но оно помогает писать аккуратный код.$m2_l2_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l2_b4_type$practice$m2_l2_b4_type$, $m2_l2_b4_title$Price$m2_l2_b4_title$, $m2_l2_b4_content$**Коротко:** запрети отрицательную цену.

### Условие

Создай класс `Product`. Цена задаётся через `set_price(amount)`. Если `amount < 0`, цена не меняется.

Начальная цена `100`. Попробуй установить `-50`. Выведи цену.

### Выход

```text
100
```$m2_l2_b4_content$, $m2_l2_b4_task_title$Price$m2_l2_b4_task_title$, NULL::jsonb),
  (5, $m2_l2_b5_type$practice$m2_l2_b5_type$, $m2_l2_b5_title$Cart$m2_l2_b5_title$, $m2_l2_b5_content$**Коротко:** реализуй корзину.

### Условие

Создай класс `Cart`.

Методы:

- `add(price)` — добавляет цену товара;
- `total()` — возвращает сумму товаров;
- `clear()` — очищает корзину.

Добавь `100`, `200`, `50`. Выведи сумму. Очисти корзину. Выведи сумму снова.

### Выход

```text
350
0
```

---$m2_l2_b5_content$, $m2_l2_b5_task_title$Cart$m2_l2_b5_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 3: Dunder
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 3
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 3
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l3_t2_title$__str__$m2_l3_t2_title$, $m2_l3_t2_statement$**Коротко:** сделай красивый вывод объекта.

### Условие

Создай класс `User` с полями `name` и `age`. Реализуй `__str__`, чтобы `print(user)` выводил:

```text
Анна, 20
```$m2_l3_t2_statement$, $m2_l3_t2_starter$$m2_l3_t2_starter$, $m2_l3_t2_solution$class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name}, {self.age}"

user = User("Анна", 20)
print(user)
$m2_l3_t2_solution$, 2, 50, $m2_l3_t2_topic$Месяц 2. Python Hard — Dunder$m2_l3_t2_topic$, $m2_l3_t2_lang$python$m2_l3_t2_lang$, $m2_l3_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l3_t2_policy$::jsonb),
  ($m2_l3_t3_title$__eq__$m2_l3_t3_title$, $m2_l3_t3_statement$**Коротко:** сравни пользователей по email.

### Условие

Создай класс `User` с полем `email`. Два пользователя равны, если email одинаковый.

Выведи результат сравнения двух пользователей с одинаковым email.

### Выход

```text
True
```$m2_l3_t3_statement$, $m2_l3_t3_starter$$m2_l3_t3_starter$, $m2_l3_t3_solution$class User:
    def __init__(self, email):
        self.email = email

    def __eq__(self, other):
        return self.email == other.email

u1 = User("a@mail.com")
u2 = User("a@mail.com")
print(u1 == u2)
$m2_l3_t3_solution$, 2, 50, $m2_l3_t3_topic$Месяц 2. Python Hard — Dunder$m2_l3_t3_topic$, $m2_l3_t3_lang$python$m2_l3_t3_lang$, $m2_l3_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l3_t3_policy$::jsonb),
  ($m2_l3_t4_title$__len__$m2_l3_t4_title$, $m2_l3_t4_statement$**Коротко:** сделай длину корзины.

### Условие

Создай класс `Cart`. Метод `add(item)` добавляет товар. `len(cart)` должен возвращать количество товаров.

Добавь три товара и выведи длину.

### Выход

```text
3
```$m2_l3_t4_statement$, $m2_l3_t4_starter$$m2_l3_t4_starter$, $m2_l3_t4_solution$class Cart:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def __len__(self):
        return len(self.items)

cart = Cart()
cart.add("book")
cart.add("pen")
cart.add("bag")
print(len(cart))
$m2_l3_t4_solution$, 2, 50, $m2_l3_t4_topic$Месяц 2. Python Hard — Dunder$m2_l3_t4_topic$, $m2_l3_t4_lang$python$m2_l3_t4_lang$, $m2_l3_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l3_t4_policy$::jsonb),
  ($m2_l3_t5_title$Money$m2_l3_t5_title$, $m2_l3_t5_statement$**Коротко:** сделай класс денег.

### Условие

Создай класс `Money` с полями `amount` и `currency`.

`__str__` должен выводить:

```text
100 RUB
```

`__eq__` должен сравнивать сумму и валюту.

Создай два одинаковых объекта и выведи:

```text
100 RUB
True
```

---$m2_l3_t5_statement$, $m2_l3_t5_starter$$m2_l3_t5_starter$, $m2_l3_t5_solution$class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return f"{self.amount} {self.currency}"

    def __eq__(self, other):
        return self.amount == other.amount and self.currency == other.currency

m1 = Money(100, "RUB")
m2 = Money(100, "RUB")
print(m1)
print(m1 == m2)
$m2_l3_t5_solution$, 2, 50, $m2_l3_t5_topic$Месяц 2. Python Hard — Dunder$m2_l3_t5_topic$, $m2_l3_t5_lang$python$m2_l3_t5_lang$, $m2_l3_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l3_t5_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 3
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l3_ttitle_2$__str__$m2_l3_ttitle_2$,
    $m2_l3_ttitle_3$__eq__$m2_l3_ttitle_3$,
    $m2_l3_ttitle_4$__len__$m2_l3_ttitle_4$,
    $m2_l3_ttitle_5$Money$m2_l3_ttitle_5$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 3
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l3_test_2_1_title$__str__$m2_l3_test_2_1_title$, $m2_l3_test_2_1_input$$m2_l3_test_2_1_input$, $m2_l3_test_2_1_expected$Анна, 20$m2_l3_test_2_1_expected$, FALSE, 1),
  ($m2_l3_test_3_1_title$__eq__$m2_l3_test_3_1_title$, $m2_l3_test_3_1_input$$m2_l3_test_3_1_input$, $m2_l3_test_3_1_expected$True$m2_l3_test_3_1_expected$, FALSE, 1),
  ($m2_l3_test_4_1_title$__len__$m2_l3_test_4_1_title$, $m2_l3_test_4_1_input$$m2_l3_test_4_1_input$, $m2_l3_test_4_1_expected$3$m2_l3_test_4_1_expected$, FALSE, 1),
  ($m2_l3_test_5_1_title$Money$m2_l3_test_5_1_title$, $m2_l3_test_5_1_input$$m2_l3_test_5_1_input$, $m2_l3_test_5_1_expected$100 RUB$m2_l3_test_5_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 3
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l3_b1_type$theory$m2_l3_b1_type$, $m2_l3_b1_title$Что такое dunder$m2_l3_b1_title$, $m2_l3_b1_content$Dunder-методы — методы с двойным подчёркиванием:

```python
__init__
__str__
__len__
__eq__
```

Они позволяют объектам работать с обычными операциями Python. Например, `print(obj)` вызывает `obj.__str__()`.$m2_l3_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l3_b2_type$practice$m2_l3_b2_type$, $m2_l3_b2_title$__str__$m2_l3_b2_title$, $m2_l3_b2_content$**Коротко:** сделай красивый вывод объекта.

### Условие

Создай класс `User` с полями `name` и `age`. Реализуй `__str__`, чтобы `print(user)` выводил:

```text
Анна, 20
```$m2_l3_b2_content$, $m2_l3_b2_task_title$__str__$m2_l3_b2_task_title$, NULL::jsonb),
  (3, $m2_l3_b3_type$practice$m2_l3_b3_type$, $m2_l3_b3_title$__eq__$m2_l3_b3_title$, $m2_l3_b3_content$**Коротко:** сравни пользователей по email.

### Условие

Создай класс `User` с полем `email`. Два пользователя равны, если email одинаковый.

Выведи результат сравнения двух пользователей с одинаковым email.

### Выход

```text
True
```$m2_l3_b3_content$, $m2_l3_b3_task_title$__eq__$m2_l3_b3_task_title$, NULL::jsonb),
  (4, $m2_l3_b4_type$practice$m2_l3_b4_type$, $m2_l3_b4_title$__len__$m2_l3_b4_title$, $m2_l3_b4_content$**Коротко:** сделай длину корзины.

### Условие

Создай класс `Cart`. Метод `add(item)` добавляет товар. `len(cart)` должен возвращать количество товаров.

Добавь три товара и выведи длину.

### Выход

```text
3
```$m2_l3_b4_content$, $m2_l3_b4_task_title$__len__$m2_l3_b4_task_title$, NULL::jsonb),
  (5, $m2_l3_b5_type$practice$m2_l3_b5_type$, $m2_l3_b5_title$Money$m2_l3_b5_title$, $m2_l3_b5_content$**Коротко:** сделай класс денег.

### Условие

Создай класс `Money` с полями `amount` и `currency`.

`__str__` должен выводить:

```text
100 RUB
```

`__eq__` должен сравнивать сумму и валюту.

Создай два одинаковых объекта и выведи:

```text
100 RUB
True
```

---$m2_l3_b5_content$, $m2_l3_b5_task_title$Money$m2_l3_b5_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 4: Наследование
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 4
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 4
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l4_t2_title$Animal$m2_l4_t2_title$, $m2_l4_t2_statement$**Коротко:** создай наследника.

### Условие

Создай класс `Animal` с методом `voice()`, который возвращает `"..."`.

Создай класс `Dog`, который наследуется от `Animal` и переопределяет `voice()`, возвращая `"Гав"`.

Выведи голос собаки.

### Выход

```text
Гав
```$m2_l4_t2_statement$, $m2_l4_t2_starter$$m2_l4_t2_starter$, $m2_l4_t2_solution$class Animal:
    def voice(self):
        return "..."

class Dog(Animal):
    def voice(self):
        return "Гав"

dog = Dog()
print(dog.voice())
$m2_l4_t2_solution$, 2, 50, $m2_l4_t2_topic$Месяц 2. Python Hard — Наследование$m2_l4_t2_topic$, $m2_l4_t2_lang$python$m2_l4_t2_lang$, $m2_l4_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l4_t2_policy$::jsonb),
  ($m2_l4_t4_title$Employee$m2_l4_t4_title$, $m2_l4_t4_statement$**Коротко:** используй `super()`.

### Условие

Создай класс `Person` с `name`. Создай класс `Employee`, который наследуется от `Person` и добавляет `salary`.

Создай сотрудника `"Иван"`, `70000`. Выведи:

```text
Иван 70000
```$m2_l4_t4_statement$, $m2_l4_t4_starter$$m2_l4_t4_starter$, $m2_l4_t4_solution$class Person:
    def __init__(self, name):
        self.name = name

class Employee(Person):
    def __init__(self, name, salary):
        super().__init__(name)
        self.salary = salary

employee = Employee("Иван", 70000)
print(employee.name, employee.salary)
$m2_l4_t4_solution$, 2, 50, $m2_l4_t4_topic$Месяц 2. Python Hard — Наследование$m2_l4_t4_topic$, $m2_l4_t4_lang$python$m2_l4_t4_lang$, $m2_l4_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l4_t4_policy$::jsonb),
  ($m2_l4_t6_title$Shapes$m2_l4_t6_title$, $m2_l4_t6_statement$**Коротко:** посчитай площади фигур.

### Условие

Создай базовый класс `Shape` с методом `area()`.

Создай классы:

- `Rectangle(width, height)`;
- `Square(size)`.

Оба должны иметь метод `area()`.

Создай прямоугольник `3 x 4` и квадрат `5`. Выведи площади.

### Выход

```text
12
25
```

---$m2_l4_t6_statement$, $m2_l4_t6_starter$$m2_l4_t6_starter$, $m2_l4_t6_solution$class Shape:
    def area(self):
        return 0

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, size):
        self.size = size

    def area(self):
        return self.size * self.size

shapes = [Rectangle(3, 4), Square(5)]
for shape in shapes:
    print(shape.area())
$m2_l4_t6_solution$, 2, 50, $m2_l4_t6_topic$Месяц 2. Python Hard — Наследование$m2_l4_t6_topic$, $m2_l4_t6_lang$python$m2_l4_t6_lang$, $m2_l4_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l4_t6_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 4
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l4_ttitle_2$Animal$m2_l4_ttitle_2$,
    $m2_l4_ttitle_4$Employee$m2_l4_ttitle_4$,
    $m2_l4_ttitle_6$Shapes$m2_l4_ttitle_6$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 4
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l4_test_2_1_title$Animal$m2_l4_test_2_1_title$, $m2_l4_test_2_1_input$$m2_l4_test_2_1_input$, $m2_l4_test_2_1_expected$Гав$m2_l4_test_2_1_expected$, FALSE, 1),
  ($m2_l4_test_4_1_title$Employee$m2_l4_test_4_1_title$, $m2_l4_test_4_1_input$$m2_l4_test_4_1_input$, $m2_l4_test_4_1_expected$Иван 70000$m2_l4_test_4_1_expected$, FALSE, 1),
  ($m2_l4_test_6_1_title$Shapes$m2_l4_test_6_1_title$, $m2_l4_test_6_1_input$$m2_l4_test_6_1_input$, $m2_l4_test_6_1_expected$12
25$m2_l4_test_6_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 4
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l4_b1_type$theory$m2_l4_b1_type$, $m2_l4_b1_title$Базовый класс$m2_l4_b1_title$, $m2_l4_b1_content$Наследование позволяет создать новый класс на основе существующего.

```python
class Animal:
    def eat(self):
        print("Ем")

class Cat(Animal):
    pass
```

`Cat` наследует метод `eat` от `Animal`.$m2_l4_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l4_b2_type$practice$m2_l4_b2_type$, $m2_l4_b2_title$Animal$m2_l4_b2_title$, $m2_l4_b2_content$**Коротко:** создай наследника.

### Условие

Создай класс `Animal` с методом `voice()`, который возвращает `"..."`.

Создай класс `Dog`, который наследуется от `Animal` и переопределяет `voice()`, возвращая `"Гав"`.

Выведи голос собаки.

### Выход

```text
Гав
```$m2_l4_b2_content$, $m2_l4_b2_task_title$Animal$m2_l4_b2_task_title$, NULL::jsonb),
  (3, $m2_l4_b3_type$theory$m2_l4_b3_type$, $m2_l4_b3_title$super$m2_l4_b3_title$, $m2_l4_b3_content$`super()` вызывает метод родительского класса.

```python
class User:
    def __init__(self, name):
        self.name = name

class Admin(User):
    def __init__(self, name, level):
        super().__init__(name)
        self.level = level
```

Так мы не дублируем код родителя.$m2_l4_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l4_b4_type$practice$m2_l4_b4_type$, $m2_l4_b4_title$Employee$m2_l4_b4_title$, $m2_l4_b4_content$**Коротко:** используй `super()`.

### Условие

Создай класс `Person` с `name`. Создай класс `Employee`, который наследуется от `Person` и добавляет `salary`.

Создай сотрудника `"Иван"`, `70000`. Выведи:

```text
Иван 70000
```$m2_l4_b4_content$, $m2_l4_b4_task_title$Employee$m2_l4_b4_task_title$, NULL::jsonb),
  (5, $m2_l4_b5_type$theory$m2_l4_b5_type$, $m2_l4_b5_title$Полиморфизм$m2_l4_b5_title$, $m2_l4_b5_content$Полиморфизм означает: разные объекты могут иметь одинаковый метод, но выполнять его по-разному.

```python
animals = [Dog(), Cat()]
for animal in animals:
    print(animal.voice())
```

Коду не важно, собака это или кошка. Важно, что у объекта есть метод `voice()`.$m2_l4_b5_content$, NULL, NULL::jsonb),
  (6, $m2_l4_b6_type$practice$m2_l4_b6_type$, $m2_l4_b6_title$Shapes$m2_l4_b6_title$, $m2_l4_b6_content$**Коротко:** посчитай площади фигур.

### Условие

Создай базовый класс `Shape` с методом `area()`.

Создай классы:

- `Rectangle(width, height)`;
- `Square(size)`.

Оба должны иметь метод `area()`.

Создай прямоугольник `3 x 4` и квадрат `5`. Выведи площади.

### Выход

```text
12
25
```

---$m2_l4_b6_content$, $m2_l4_b6_task_title$Shapes$m2_l4_b6_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 5: ООП принципы
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 5
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 5
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l5_t4_title$Service$m2_l5_t4_title$, $m2_l5_t4_statement$**Коротко:** вынеси скидку в сервис.

### Условие

Создай `Order(amount)` и `DiscountService.apply(order)`. Если сумма заказа больше `1000`, скидка `10%`. Иначе скидки нет.

Создай заказ на `2000`. Выведи сумму после скидки.

### Выход

```text
1800.0
```$m2_l5_t4_statement$, $m2_l5_t4_starter$$m2_l5_t4_starter$, $m2_l5_t4_solution$class Order:
    def __init__(self, amount):
        self.amount = amount

class DiscountService:
    def apply(self, order):
        if order.amount > 1000:
            return order.amount * 0.9
        return order.amount

order = Order(2000)
service = DiscountService()
print(service.apply(order))
$m2_l5_t4_solution$, 2, 50, $m2_l5_t4_topic$Месяц 2. Python Hard — ООП принципы$m2_l5_t4_topic$, $m2_l5_t4_lang$python$m2_l5_t4_lang$, $m2_l5_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l5_t4_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 5
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l5_ttitle_4$Service$m2_l5_ttitle_4$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 5
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l5_test_4_1_title$Service$m2_l5_test_4_1_title$, $m2_l5_test_4_1_input$$m2_l5_test_4_1_input$, $m2_l5_test_4_1_expected$1800.0$m2_l5_test_4_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 5
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l5_b1_type$theory$m2_l5_b1_type$, $m2_l5_b1_title$SRP$m2_l5_b1_title$, $m2_l5_b1_content$SRP: у класса должна быть одна основная ответственность.

Плохо:

```python
class User:
    def save_to_db(self): ...
    def send_email(self): ...
    def calculate_discount(self): ...
```

Лучше разделить:

```text
User — данные пользователя
UserRepository — сохранение
EmailService — отправка письма
DiscountService — расчёт скидки
```$m2_l5_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l5_b2_type$theory$m2_l5_b2_type$, $m2_l5_b2_title$Композиция$m2_l5_b2_title$, $m2_l5_b2_content$Композиция — когда объект содержит другие объекты.

```python
class Cart:
    def __init__(self):
        self.items = []
```

Корзина не наследуется от списка. Она содержит список.$m2_l5_b2_content$, NULL, NULL::jsonb),
  (3, $m2_l5_b3_type$practice$m2_l5_b3_type$, $m2_l5_b3_title$Bad class$m2_l5_b3_title$, $m2_l5_b3_content$**Коротко:** раздели ответственность.

### Условие

Есть класс:

```python
class Order:
    def __init__(self, items):
        self.items = items

    def total(self):
        return sum(self.items)

    def send_email(self):
        print("Email sent")
```

Что здесь не так? Напиши короткий ответ и предложи, какие классы можно выделить.$m2_l5_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l5_b4_type$practice$m2_l5_b4_type$, $m2_l5_b4_title$Service$m2_l5_b4_title$, $m2_l5_b4_content$**Коротко:** вынеси скидку в сервис.

### Условие

Создай `Order(amount)` и `DiscountService.apply(order)`. Если сумма заказа больше `1000`, скидка `10%`. Иначе скидки нет.

Создай заказ на `2000`. Выведи сумму после скидки.

### Выход

```text
1800.0
```$m2_l5_b4_content$, $m2_l5_b4_task_title$Service$m2_l5_b4_task_title$, NULL::jsonb),
  (5, $m2_l5_b5_type$project$m2_l5_b5_type$, $m2_l5_b5_title$Ревью$m2_l5_b5_title$, $m2_l5_b5_content$Отправь код своего CLI-проекта на мини-ревью.

AI проверит:

- слишком большие функции;
- классы с несколькими ответственностями;
- понятные имена;
- дублирование;
- возможность выделить сервисы.

---$m2_l5_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 6: Типизация
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 6
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 6
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l6_t2_title$Функции$m2_l6_t2_title$, $m2_l6_t2_statement$**Коротко:** добавь типы функции.

### Условие

Напиши функцию `full_name(first, last)`, которая возвращает имя и фамилию через пробел. Добавь аннотации типов.

Вызов:

```python
print(full_name("Анна", "Иванова"))
```

### Выход

```text
Анна Иванова
```$m2_l6_t2_statement$, $m2_l6_t2_starter$$m2_l6_t2_starter$, $m2_l6_t2_solution$def full_name(first: str, last: str) -> str:
    return first + " " + last

print(full_name("Анна", "Иванова"))
$m2_l6_t2_solution$, 2, 50, $m2_l6_t2_topic$Месяц 2. Python Hard — Типизация$m2_l6_t2_topic$, $m2_l6_t2_lang$python$m2_l6_t2_lang$, $m2_l6_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l6_t2_policy$::jsonb),
  ($m2_l6_t5_title$Typed dict$m2_l6_t5_title$, $m2_l6_t5_statement$**Коротко:** типизируй словарь.

### Условие

Создай функцию `format_user(user)`, которая принимает словарь:

```python
{"name": "Анна", "age": 20}
```

и возвращает строку:

```text
Анна, 20
```

Используй тип `dict[str, str | int]`.$m2_l6_t5_statement$, $m2_l6_t5_starter$$m2_l6_t5_starter$, $m2_l6_t5_solution$def format_user(user: dict[str, str | int]) -> str:
    return f"{user['name']}, {user['age']}"

print(format_user({"name": "Анна", "age": 20}))
$m2_l6_t5_solution$, 2, 50, $m2_l6_t5_topic$Месяц 2. Python Hard — Типизация$m2_l6_t5_topic$, $m2_l6_t5_lang$python$m2_l6_t5_lang$, $m2_l6_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l6_t5_policy$::jsonb),
  ($m2_l6_t6_title$Контроль$m2_l6_t6_title$, $m2_l6_t6_statement$**Коротко:** типизируй сервис задач.

### Условие

Напиши функцию:

```python
def active_titles(tasks: list[dict[str, object]]) -> list[str]:
    ...
```

Она возвращает названия задач, у которых `done == False`.

Используй список:

```python
tasks = [
    {"title": "A", "done": False},
    {"title": "B", "done": True},
    {"title": "C", "done": False},
]
```

### Выход

```text
['A', 'C']
```

---$m2_l6_t6_statement$, $m2_l6_t6_starter$$m2_l6_t6_starter$, $m2_l6_t6_solution$def active_titles(tasks: list[dict[str, object]]) -> list[str]:
    result = []
    for task in tasks:
        if task["done"] is False:
            result.append(str(task["title"]))
    return result

tasks = [
    {"title": "A", "done": False},
    {"title": "B", "done": True},
    {"title": "C", "done": False},
]

print(active_titles(tasks))
$m2_l6_t6_solution$, 2, 50, $m2_l6_t6_topic$Месяц 2. Python Hard — Типизация$m2_l6_t6_topic$, $m2_l6_t6_lang$python$m2_l6_t6_lang$, $m2_l6_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l6_t6_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 6
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l6_ttitle_2$Функции$m2_l6_ttitle_2$,
    $m2_l6_ttitle_5$Typed dict$m2_l6_ttitle_5$,
    $m2_l6_ttitle_6$Контроль$m2_l6_ttitle_6$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 6
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l6_test_2_1_title$Функции$m2_l6_test_2_1_title$, $m2_l6_test_2_1_input$$m2_l6_test_2_1_input$, $m2_l6_test_2_1_expected$Анна Иванова$m2_l6_test_2_1_expected$, FALSE, 1),
  ($m2_l6_test_5_1_title$Typed dict$m2_l6_test_5_1_title$, $m2_l6_test_5_1_input$$m2_l6_test_5_1_input$, $m2_l6_test_5_1_expected$Анна, 20$m2_l6_test_5_1_expected$, FALSE, 1),
  ($m2_l6_test_6_1_title$Контроль$m2_l6_test_6_1_title$, $m2_l6_test_6_1_input$$m2_l6_test_6_1_input$, $m2_l6_test_6_1_expected$['A', 'C']$m2_l6_test_6_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 6
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l6_b1_type$theory$m2_l6_b1_type$, $m2_l6_b1_title$Зачем типы$m2_l6_b1_title$, $m2_l6_b1_content$Аннотации типов показывают, какие значения ожидает код.

```python
def add(a: int, b: int) -> int:
    return a + b
```

Они помогают читать код, ловить ошибки раньше и пользоваться автодополнением.$m2_l6_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l6_b2_type$practice$m2_l6_b2_type$, $m2_l6_b2_title$Функции$m2_l6_b2_title$, $m2_l6_b2_content$**Коротко:** добавь типы функции.

### Условие

Напиши функцию `full_name(first, last)`, которая возвращает имя и фамилию через пробел. Добавь аннотации типов.

Вызов:

```python
print(full_name("Анна", "Иванова"))
```

### Выход

```text
Анна Иванова
```$m2_l6_b2_content$, $m2_l6_b2_task_title$Функции$m2_l6_b2_task_title$, NULL::jsonb),
  (3, $m2_l6_b3_type$theory$m2_l6_b3_type$, $m2_l6_b3_title$Коллекции$m2_l6_b3_title$, $m2_l6_b3_content$Для коллекций используются такие типы:

```python
list[int]
dict[str, int]
set[str]
tuple[str, int]
```

Пример:

```python
def average(numbers: list[int]) -> float:
    return sum(numbers) / len(numbers)
```$m2_l6_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l6_b4_type$theory$m2_l6_b4_type$, $m2_l6_b4_title$Optional$m2_l6_b4_title$, $m2_l6_b4_content$Если значение может быть `None`, это нужно показать в типе:

```python
def find_user(user_id: int) -> User | None:
    ...
```

`User | None` означает: функция вернёт пользователя или ничего.$m2_l6_b4_content$, NULL, NULL::jsonb),
  (5, $m2_l6_b5_type$practice$m2_l6_b5_type$, $m2_l6_b5_title$Typed dict$m2_l6_b5_title$, $m2_l6_b5_content$**Коротко:** типизируй словарь.

### Условие

Создай функцию `format_user(user)`, которая принимает словарь:

```python
{"name": "Анна", "age": 20}
```

и возвращает строку:

```text
Анна, 20
```

Используй тип `dict[str, str | int]`.$m2_l6_b5_content$, $m2_l6_b5_task_title$Typed dict$m2_l6_b5_task_title$, NULL::jsonb),
  (6, $m2_l6_b6_type$practice$m2_l6_b6_type$, $m2_l6_b6_title$Контроль$m2_l6_b6_title$, $m2_l6_b6_content$**Коротко:** типизируй сервис задач.

### Условие

Напиши функцию:

```python
def active_titles(tasks: list[dict[str, object]]) -> list[str]:
    ...
```

Она возвращает названия задач, у которых `done == False`.

Используй список:

```python
tasks = [
    {"title": "A", "done": False},
    {"title": "B", "done": True},
    {"title": "C", "done": False},
]
```

### Выход

```text
['A', 'C']
```

---$m2_l6_b6_content$, $m2_l6_b6_task_title$Контроль$m2_l6_b6_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 7: Исключения
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 7
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 7
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l7_t2_title$Safe int$m2_l7_t2_title$, $m2_l7_t2_statement$**Коротко:** обработай неправильный ввод.

### Условие

Пользователь вводит значение. Если это целое число, выведи число * 2. Если нет — выведи `Ошибка`.

### Пример 1

Ввод:

```text
5
```

Вывод:

```text
10
```

### Пример 2

Ввод:

```text
abc
```

Вывод:

```text
Ошибка
```$m2_l7_t2_statement$, $m2_l7_t2_starter$$m2_l7_t2_starter$, $m2_l7_t2_solution$try:
    number = int(input())
    print(number * 2)
except ValueError:
    print("Ошибка")
$m2_l7_t2_solution$, 2, 50, $m2_l7_t2_topic$Месяц 2. Python Hard — Исключения$m2_l7_t2_topic$, $m2_l7_t2_lang$python$m2_l7_t2_lang$, $m2_l7_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l7_t2_policy$::jsonb),
  ($m2_l7_t5_title$Custom error$m2_l7_t5_title$, $m2_l7_t5_statement$**Коротко:** создай своё исключение.

### Условие

Создай исключение `NotEnoughMoneyError`. Создай класс `Account` с методом `withdraw(amount)`. Если денег недостаточно, метод выбрасывает `NotEnoughMoneyError`.

Обработай ошибку и выведи:

```text
Недостаточно средств
```$m2_l7_t5_statement$, $m2_l7_t5_starter$$m2_l7_t5_starter$, $m2_l7_t5_solution$class NotEnoughMoneyError(Exception):
    pass

class Account:
    def __init__(self, balance):
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise NotEnoughMoneyError()
        self.balance -= amount

account = Account(100)

try:
    account.withdraw(150)
except NotEnoughMoneyError:
    print("Недостаточно средств")
$m2_l7_t5_solution$, 2, 50, $m2_l7_t5_topic$Месяц 2. Python Hard — Исключения$m2_l7_t5_topic$, $m2_l7_t5_lang$python$m2_l7_t5_lang$, $m2_l7_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l7_t5_policy$::jsonb),
  ($m2_l7_t6_title$Контроль$m2_l7_t6_title$, $m2_l7_t6_statement$**Коротко:** валидируй пользователя.

### Условие

Создай функцию `validate_age(age)`. Если `age < 0`, выброси `ValueError`. Если `age >= 0`, верни `"OK"`.

Проверь возраст `-1`, обработай ошибку и выведи:

```text
Некорректный возраст
```

---$m2_l7_t6_statement$, $m2_l7_t6_starter$$m2_l7_t6_starter$, $m2_l7_t6_solution$def validate_age(age):
    if age < 0:
        raise ValueError()
    return "OK"

try:
    print(validate_age(-1))
except ValueError:
    print("Некорректный возраст")
$m2_l7_t6_solution$, 2, 50, $m2_l7_t6_topic$Месяц 2. Python Hard — Исключения$m2_l7_t6_topic$, $m2_l7_t6_lang$python$m2_l7_t6_lang$, $m2_l7_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l7_t6_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 7
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l7_ttitle_2$Safe int$m2_l7_ttitle_2$,
    $m2_l7_ttitle_5$Custom error$m2_l7_ttitle_5$,
    $m2_l7_ttitle_6$Контроль$m2_l7_ttitle_6$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 7
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l7_test_2_1_title$Safe int$m2_l7_test_2_1_title$, $m2_l7_test_2_1_input$5$m2_l7_test_2_1_input$, $m2_l7_test_2_1_expected$10$m2_l7_test_2_1_expected$, FALSE, 1),
  ($m2_l7_test_5_1_title$Custom error$m2_l7_test_5_1_title$, $m2_l7_test_5_1_input$$m2_l7_test_5_1_input$, $m2_l7_test_5_1_expected$Недостаточно средств$m2_l7_test_5_1_expected$, FALSE, 1),
  ($m2_l7_test_6_1_title$Контроль$m2_l7_test_6_1_title$, $m2_l7_test_6_1_input$$m2_l7_test_6_1_input$, $m2_l7_test_6_1_expected$Некорректный возраст$m2_l7_test_6_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 7
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l7_b1_type$theory$m2_l7_b1_type$, $m2_l7_b1_title$try/except$m2_l7_b1_title$, $m2_l7_b1_content$`try/except` нужен, когда код может упасть.

```python
try:
    number = int(input())
    print(number * 2)
except ValueError:
    print("Введите число")
```

Плохо:

```python
except:
    pass
```

Так ты скрываешь проблему.$m2_l7_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l7_b2_type$practice$m2_l7_b2_type$, $m2_l7_b2_title$Safe int$m2_l7_b2_title$, $m2_l7_b2_content$**Коротко:** обработай неправильный ввод.

### Условие

Пользователь вводит значение. Если это целое число, выведи число * 2. Если нет — выведи `Ошибка`.

### Пример 1

Ввод:

```text
5
```

Вывод:

```text
10
```

### Пример 2

Ввод:

```text
abc
```

Вывод:

```text
Ошибка
```$m2_l7_b2_content$, $m2_l7_b2_task_title$Safe int$m2_l7_b2_task_title$, NULL::jsonb),
  (3, $m2_l7_b3_type$theory$m2_l7_b3_type$, $m2_l7_b3_title$else/finally$m2_l7_b3_title$, $m2_l7_b3_content$`else` выполняется, если ошибки не было. `finally` выполняется всегда.

```python
try:
    number = int(input())
except ValueError:
    print("Ошибка")
else:
    print("OK")
finally:
    print("Конец")
```$m2_l7_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l7_b4_type$theory$m2_l7_b4_type$, $m2_l7_b4_title$raise$m2_l7_b4_title$, $m2_l7_b4_content$`raise` создаёт ошибку вручную.

```python
def set_age(age):
    if age < 0:
        raise ValueError("Возраст не может быть отрицательным")
```

Так функция явно сообщает: входные данные неправильные.$m2_l7_b4_content$, NULL, NULL::jsonb),
  (5, $m2_l7_b5_type$practice$m2_l7_b5_type$, $m2_l7_b5_title$Custom error$m2_l7_b5_title$, $m2_l7_b5_content$**Коротко:** создай своё исключение.

### Условие

Создай исключение `NotEnoughMoneyError`. Создай класс `Account` с методом `withdraw(amount)`. Если денег недостаточно, метод выбрасывает `NotEnoughMoneyError`.

Обработай ошибку и выведи:

```text
Недостаточно средств
```$m2_l7_b5_content$, $m2_l7_b5_task_title$Custom error$m2_l7_b5_task_title$, NULL::jsonb),
  (6, $m2_l7_b6_type$practice$m2_l7_b6_type$, $m2_l7_b6_title$Контроль$m2_l7_b6_title$, $m2_l7_b6_content$**Коротко:** валидируй пользователя.

### Условие

Создай функцию `validate_age(age)`. Если `age < 0`, выброси `ValueError`. Если `age >= 0`, верни `"OK"`.

Проверь возраст `-1`, обработай ошибку и выведи:

```text
Некорректный возраст
```

---$m2_l7_b6_content$, $m2_l7_b6_task_title$Контроль$m2_l7_b6_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 8: Итераторы
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 8
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 8
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l8_t2_title$iter/next$m2_l8_t2_title$, $m2_l8_t2_statement$**Коротко:** перебери список вручную.

### Условие

Дан список `numbers = [1, 2, 3]`. Создай итератор через `iter(numbers)` и выведи три значения через `next()`.

### Выход

```text
1
2
3
```$m2_l8_t2_statement$, $m2_l8_t2_starter$$m2_l8_t2_starter$, $m2_l8_t2_solution$numbers = [1, 2, 3]
iterator = iter(numbers)
print(next(iterator))
print(next(iterator))
print(next(iterator))
$m2_l8_t2_solution$, 2, 50, $m2_l8_t2_topic$Месяц 2. Python Hard — Итераторы$m2_l8_t2_topic$, $m2_l8_t2_lang$python$m2_l8_t2_lang$, $m2_l8_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l8_t2_policy$::jsonb),
  ($m2_l8_t4_title$Counter$m2_l8_t4_title$, $m2_l8_t4_statement$**Коротко:** сделай итератор чисел.

### Условие

Создай класс `Counter`, который выдаёт числа от `1` до `limit`.

```python
counter = Counter(3)
for number in counter:
    print(number)
```

### Выход

```text
1
2
3
```$m2_l8_t4_statement$, $m2_l8_t4_starter$$m2_l8_t4_starter$, $m2_l8_t4_solution$class Counter:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.current += 1
        if self.current > self.limit:
            raise StopIteration
        return self.current

counter = Counter(3)
for number in counter:
    print(number)
$m2_l8_t4_solution$, 2, 50, $m2_l8_t4_topic$Месяц 2. Python Hard — Итераторы$m2_l8_t4_topic$, $m2_l8_t4_lang$python$m2_l8_t4_lang$, $m2_l8_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l8_t4_policy$::jsonb),
  ($m2_l8_t5_title$Paginator$m2_l8_t5_title$, $m2_l8_t5_statement$**Коротко:** сделай итератор страниц.

### Условие

Создай класс `Paginator`. Он принимает список элементов и размер страницы. При переборе возвращает страницы.

```python
p = Paginator([1, 2, 3, 4, 5], 2)
```

Вывод:

```text
[1, 2]
[3, 4]
[5]
```

---$m2_l8_t5_statement$, $m2_l8_t5_starter$$m2_l8_t5_starter$, $m2_l8_t5_solution$class Paginator:
    def __init__(self, items, page_size):
        self.items = items
        self.page_size = page_size
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.items):
            raise StopIteration
        page = self.items[self.index:self.index + self.page_size]
        self.index += self.page_size
        return page

p = Paginator([1, 2, 3, 4, 5], 2)
for page in p:
    print(page)
$m2_l8_t5_solution$, 2, 50, $m2_l8_t5_topic$Месяц 2. Python Hard — Итераторы$m2_l8_t5_topic$, $m2_l8_t5_lang$python$m2_l8_t5_lang$, $m2_l8_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l8_t5_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 8
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l8_ttitle_2$iter/next$m2_l8_ttitle_2$,
    $m2_l8_ttitle_4$Counter$m2_l8_ttitle_4$,
    $m2_l8_ttitle_5$Paginator$m2_l8_ttitle_5$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 8
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l8_test_2_1_title$iter/next$m2_l8_test_2_1_title$, $m2_l8_test_2_1_input$$m2_l8_test_2_1_input$, $m2_l8_test_2_1_expected$1
2
3$m2_l8_test_2_1_expected$, FALSE, 1),
  ($m2_l8_test_4_1_title$Counter$m2_l8_test_4_1_title$, $m2_l8_test_4_1_input$$m2_l8_test_4_1_input$, $m2_l8_test_4_1_expected$1
2
3$m2_l8_test_4_1_expected$, FALSE, 1),
  ($m2_l8_test_5_1_title$Paginator$m2_l8_test_5_1_title$, $m2_l8_test_5_1_input$$m2_l8_test_5_1_input$, $m2_l8_test_5_1_expected$[1, 2]
[3, 4]
[5]$m2_l8_test_5_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 8
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l8_b1_type$theory$m2_l8_b1_type$, $m2_l8_b1_title$Iterable$m2_l8_b1_title$, $m2_l8_b1_content$Когда ты пишешь `for item in items`, Python берёт у объекта итератор и вызывает `next()` до конца. Списки, строки и словари — итерируемые объекты.$m2_l8_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l8_b2_type$practice$m2_l8_b2_type$, $m2_l8_b2_title$iter/next$m2_l8_b2_title$, $m2_l8_b2_content$**Коротко:** перебери список вручную.

### Условие

Дан список `numbers = [1, 2, 3]`. Создай итератор через `iter(numbers)` и выведи три значения через `next()`.

### Выход

```text
1
2
3
```$m2_l8_b2_content$, $m2_l8_b2_task_title$iter/next$m2_l8_b2_task_title$, NULL::jsonb),
  (3, $m2_l8_b3_type$theory$m2_l8_b3_type$, $m2_l8_b3_title$Свой iter$m2_l8_b3_title$, $m2_l8_b3_content$Итератор должен иметь методы `__iter__` и `__next__`. Когда значений больше нет, `__next__` выбрасывает `StopIteration`.$m2_l8_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l8_b4_type$practice$m2_l8_b4_type$, $m2_l8_b4_title$Counter$m2_l8_b4_title$, $m2_l8_b4_content$**Коротко:** сделай итератор чисел.

### Условие

Создай класс `Counter`, который выдаёт числа от `1` до `limit`.

```python
counter = Counter(3)
for number in counter:
    print(number)
```

### Выход

```text
1
2
3
```$m2_l8_b4_content$, $m2_l8_b4_task_title$Counter$m2_l8_b4_task_title$, NULL::jsonb),
  (5, $m2_l8_b5_type$practice$m2_l8_b5_type$, $m2_l8_b5_title$Paginator$m2_l8_b5_title$, $m2_l8_b5_content$**Коротко:** сделай итератор страниц.

### Условие

Создай класс `Paginator`. Он принимает список элементов и размер страницы. При переборе возвращает страницы.

```python
p = Paginator([1, 2, 3, 4, 5], 2)
```

Вывод:

```text
[1, 2]
[3, 4]
[5]
```

---$m2_l8_b5_content$, $m2_l8_b5_task_title$Paginator$m2_l8_b5_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 9: Генераторы
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 9
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 9
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l9_t2_title$my_range$m2_l9_t2_title$, $m2_l9_t2_statement$**Коротко:** создай генератор диапазона.

### Условие

Напиши генератор `my_range(n)`, который выдаёт числа от `1` до `n`. Для `n = 3` выведи все числа.

### Выход

```text
1
2
3
```$m2_l9_t2_statement$, $m2_l9_t2_starter$$m2_l9_t2_starter$, $m2_l9_t2_solution$def my_range(n):
    for number in range(1, n + 1):
        yield number

for number in my_range(3):
    print(number)
$m2_l9_t2_solution$, 2, 50, $m2_l9_t2_topic$Месяц 2. Python Hard — Генераторы$m2_l9_t2_topic$, $m2_l9_t2_lang$python$m2_l9_t2_lang$, $m2_l9_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l9_t2_policy$::jsonb),
  ($m2_l9_t4_title$even$m2_l9_t4_title$, $m2_l9_t4_statement$**Коротко:** фильтруй чётные числа.

### Условие

Напиши генератор `even_numbers(numbers)`, который выдаёт только чётные числа из `[1, 2, 3, 4, 5, 6]`.

### Выход

```text
2
4
6
```$m2_l9_t4_statement$, $m2_l9_t4_starter$$m2_l9_t4_starter$, $m2_l9_t4_solution$def even_numbers(numbers):
    for number in numbers:
        if number % 2 == 0:
            yield number

for number in even_numbers([1, 2, 3, 4, 5, 6]):
    print(number)
$m2_l9_t4_solution$, 2, 50, $m2_l9_t4_topic$Месяц 2. Python Hard — Генераторы$m2_l9_t4_topic$, $m2_l9_t4_lang$python$m2_l9_t4_lang$, $m2_l9_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l9_t4_policy$::jsonb),
  ($m2_l9_t5_title$pages$m2_l9_t5_title$, $m2_l9_t5_statement$**Коротко:** генератор страниц.

### Условие

Напиши генератор `pages(items, size)`, который выдаёт части списка.

```python
for page in pages([1, 2, 3, 4, 5], 2):
    print(page)
```

### Выход

```text
[1, 2]
[3, 4]
[5]
```

---$m2_l9_t5_statement$, $m2_l9_t5_starter$$m2_l9_t5_starter$, $m2_l9_t5_solution$def pages(items, size):
    for index in range(0, len(items), size):
        yield items[index:index + size]

for page in pages([1, 2, 3, 4, 5], 2):
    print(page)
$m2_l9_t5_solution$, 2, 50, $m2_l9_t5_topic$Месяц 2. Python Hard — Генераторы$m2_l9_t5_topic$, $m2_l9_t5_lang$python$m2_l9_t5_lang$, $m2_l9_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l9_t5_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 9
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l9_ttitle_2$my_range$m2_l9_ttitle_2$,
    $m2_l9_ttitle_4$even$m2_l9_ttitle_4$,
    $m2_l9_ttitle_5$pages$m2_l9_ttitle_5$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 9
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l9_test_2_1_title$my_range$m2_l9_test_2_1_title$, $m2_l9_test_2_1_input$$m2_l9_test_2_1_input$, $m2_l9_test_2_1_expected$1
2
3$m2_l9_test_2_1_expected$, FALSE, 1),
  ($m2_l9_test_4_1_title$even$m2_l9_test_4_1_title$, $m2_l9_test_4_1_input$$m2_l9_test_4_1_input$, $m2_l9_test_4_1_expected$2
4
6$m2_l9_test_4_1_expected$, FALSE, 1),
  ($m2_l9_test_5_1_title$pages$m2_l9_test_5_1_title$, $m2_l9_test_5_1_input$$m2_l9_test_5_1_input$, $m2_l9_test_5_1_expected$[1, 2]
[3, 4]
[5]$m2_l9_test_5_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 9
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l9_b1_type$theory$m2_l9_b1_type$, $m2_l9_b1_title$yield$m2_l9_b1_title$, $m2_l9_b1_content$Генератор — функция, которая возвращает значения постепенно.

```python
def numbers():
    yield 1
    yield 2
    yield 3
```

`yield` ставит функцию на паузу, а не завершает её навсегда.$m2_l9_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l9_b2_type$practice$m2_l9_b2_type$, $m2_l9_b2_title$my_range$m2_l9_b2_title$, $m2_l9_b2_content$**Коротко:** создай генератор диапазона.

### Условие

Напиши генератор `my_range(n)`, который выдаёт числа от `1` до `n`. Для `n = 3` выведи все числа.

### Выход

```text
1
2
3
```$m2_l9_b2_content$, $m2_l9_b2_task_title$my_range$m2_l9_b2_task_title$, NULL::jsonb),
  (3, $m2_l9_b3_type$theory$m2_l9_b3_type$, $m2_l9_b3_title$Lazy$m2_l9_b3_title$, $m2_l9_b3_content$Генератор не хранит все значения сразу. Он создаёт их по одному. Это важно для больших файлов, больших списков и потоковой обработки данных.$m2_l9_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l9_b4_type$practice$m2_l9_b4_type$, $m2_l9_b4_title$even$m2_l9_b4_title$, $m2_l9_b4_content$**Коротко:** фильтруй чётные числа.

### Условие

Напиши генератор `even_numbers(numbers)`, который выдаёт только чётные числа из `[1, 2, 3, 4, 5, 6]`.

### Выход

```text
2
4
6
```$m2_l9_b4_content$, $m2_l9_b4_task_title$even$m2_l9_b4_task_title$, NULL::jsonb),
  (5, $m2_l9_b5_type$practice$m2_l9_b5_type$, $m2_l9_b5_title$pages$m2_l9_b5_title$, $m2_l9_b5_content$**Коротко:** генератор страниц.

### Условие

Напиши генератор `pages(items, size)`, который выдаёт части списка.

```python
for page in pages([1, 2, 3, 4, 5], 2):
    print(page)
```

### Выход

```text
[1, 2]
[3, 4]
[5]
```

---$m2_l9_b5_content$, $m2_l9_b5_task_title$pages$m2_l9_b5_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 10: Декораторы
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 10
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 10
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l10_t3_title$log$m2_l10_t3_title$, $m2_l10_t3_statement$**Коротко:** сделай логирующий декоратор.

### Условие

Создай декоратор `log`, который перед вызовом функции печатает `Вызов функции`. Примени его к функции `hello()`, которая печатает `Привет`.

### Выход

```text
Вызов функции
Привет
```$m2_l10_t3_statement$, $m2_l10_t3_starter$$m2_l10_t3_starter$, $m2_l10_t3_solution$def log(func):
    def wrapper():
        print("Вызов функции")
        func()
    return wrapper

@log
def hello():
    print("Привет")

hello()
$m2_l10_t3_solution$, 2, 50, $m2_l10_t3_topic$Месяц 2. Python Hard — Декораторы$m2_l10_t3_topic$, $m2_l10_t3_lang$python$m2_l10_t3_lang$, $m2_l10_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l10_t3_policy$::jsonb),
  ($m2_l10_t5_title$repeat$m2_l10_t5_title$, $m2_l10_t5_statement$**Коротко:** повтори функцию два раза.

### Условие

Создай декоратор `repeat_twice`, который вызывает функцию два раза.

### Выход

```text
Hi
Hi
```$m2_l10_t5_statement$, $m2_l10_t5_starter$$m2_l10_t5_starter$, $m2_l10_t5_solution$def repeat_twice(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper

@repeat_twice
def hello():
    print("Hi")

hello()
$m2_l10_t5_solution$, 2, 50, $m2_l10_t5_topic$Месяц 2. Python Hard — Декораторы$m2_l10_t5_topic$, $m2_l10_t5_lang$python$m2_l10_t5_lang$, $m2_l10_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l10_t5_policy$::jsonb),
  ($m2_l10_t6_title$count$m2_l10_t6_title$, $m2_l10_t6_statement$**Коротко:** измерь число вызовов.

### Условие

Создай декоратор `count_calls`. После каждого вызова он печатает `Вызов N`. Для двух вызовов должно быть:

```text
Вызов 1
Вызов 2
```

---$m2_l10_t6_statement$, $m2_l10_t6_starter$$m2_l10_t6_starter$, $m2_l10_t6_solution$def count_calls(func):
    calls = 0

    def wrapper(*args, **kwargs):
        nonlocal calls
        calls += 1
        print("Вызов", calls)
        return func(*args, **kwargs)

    return wrapper

@count_calls
def empty():
    pass

empty()
empty()
$m2_l10_t6_solution$, 2, 50, $m2_l10_t6_topic$Месяц 2. Python Hard — Декораторы$m2_l10_t6_topic$, $m2_l10_t6_lang$python$m2_l10_t6_lang$, $m2_l10_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l10_t6_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 10
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l10_ttitle_3$log$m2_l10_ttitle_3$,
    $m2_l10_ttitle_5$repeat$m2_l10_ttitle_5$,
    $m2_l10_ttitle_6$count$m2_l10_ttitle_6$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 10
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l10_test_3_1_title$log$m2_l10_test_3_1_title$, $m2_l10_test_3_1_input$$m2_l10_test_3_1_input$, $m2_l10_test_3_1_expected$Вызов функции
Привет$m2_l10_test_3_1_expected$, FALSE, 1),
  ($m2_l10_test_5_1_title$repeat$m2_l10_test_5_1_title$, $m2_l10_test_5_1_input$$m2_l10_test_5_1_input$, $m2_l10_test_5_1_expected$Hi
Hi$m2_l10_test_5_1_expected$, FALSE, 1),
  ($m2_l10_test_6_1_title$count$m2_l10_test_6_1_title$, $m2_l10_test_6_1_input$$m2_l10_test_6_1_input$, $m2_l10_test_6_1_expected$Вызов 1
Вызов 2$m2_l10_test_6_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 10
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l10_b1_type$theory$m2_l10_b1_type$, $m2_l10_b1_title$func object$m2_l10_b1_title$, $m2_l10_b1_content$В Python функцию можно передать как значение.

```python
def hello():
    print("Привет")

func = hello
func()
```$m2_l10_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l10_b2_type$theory$m2_l10_b2_type$, $m2_l10_b2_title$wrapper$m2_l10_b2_title$, $m2_l10_b2_content$Декоратор принимает функцию и возвращает новую функцию.

```python
def decorator(func):
    def wrapper():
        print("До")
        func()
        print("После")
    return wrapper
```$m2_l10_b2_content$, NULL, NULL::jsonb),
  (3, $m2_l10_b3_type$practice$m2_l10_b3_type$, $m2_l10_b3_title$log$m2_l10_b3_title$, $m2_l10_b3_content$**Коротко:** сделай логирующий декоратор.

### Условие

Создай декоратор `log`, который перед вызовом функции печатает `Вызов функции`. Примени его к функции `hello()`, которая печатает `Привет`.

### Выход

```text
Вызов функции
Привет
```$m2_l10_b3_content$, $m2_l10_b3_task_title$log$m2_l10_b3_task_title$, NULL::jsonb),
  (4, $m2_l10_b4_type$theory$m2_l10_b4_type$, $m2_l10_b4_title$args$m2_l10_b4_title$, $m2_l10_b4_content$Чтобы декоратор работал с любыми аргументами, используют `*args` и `**kwargs`.

```python
def log(func):
    def wrapper(*args, **kwargs):
        print("Вызов")
        return func(*args, **kwargs)
    return wrapper
```$m2_l10_b4_content$, NULL, NULL::jsonb),
  (5, $m2_l10_b5_type$practice$m2_l10_b5_type$, $m2_l10_b5_title$repeat$m2_l10_b5_title$, $m2_l10_b5_content$**Коротко:** повтори функцию два раза.

### Условие

Создай декоратор `repeat_twice`, который вызывает функцию два раза.

### Выход

```text
Hi
Hi
```$m2_l10_b5_content$, $m2_l10_b5_task_title$repeat$m2_l10_b5_task_title$, NULL::jsonb),
  (6, $m2_l10_b6_type$practice$m2_l10_b6_type$, $m2_l10_b6_title$count$m2_l10_b6_title$, $m2_l10_b6_content$**Коротко:** измерь число вызовов.

### Условие

Создай декоратор `count_calls`. После каждого вызова он печатает `Вызов N`. Для двух вызовов должно быть:

```text
Вызов 1
Вызов 2
```

---$m2_l10_b6_content$, $m2_l10_b6_task_title$count$m2_l10_b6_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 11: Context
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 11
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 11
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l11_t2_title$open$m2_l11_t2_title$, $m2_l11_t2_statement$**Коротко:** запиши и прочитай файл.

### Условие

Создай файл `data.txt`, запиши в него `Hello`, затем прочитай и выведи содержимое.

### Выход

```text
Hello
```$m2_l11_t2_statement$, $m2_l11_t2_starter$$m2_l11_t2_starter$, $m2_l11_t2_solution$with open("data.txt", "w", encoding="utf-8") as file:
    file.write("Hello")

with open("data.txt", "r", encoding="utf-8") as file:
    print(file.read())
$m2_l11_t2_solution$, 2, 50, $m2_l11_t2_topic$Месяц 2. Python Hard — Context$m2_l11_t2_topic$, $m2_l11_t2_lang$python$m2_l11_t2_lang$, $m2_l11_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l11_t2_policy$::jsonb),
  ($m2_l11_t4_title$Message$m2_l11_t4_title$, $m2_l11_t4_statement$**Коротко:** сделай простой контекст.

### Условие

Создай контекстный менеджер `Message`. При входе печатает `start`, при выходе `end`. Внутри блока выведи `work`.

### Выход

```text
start
work
end
```$m2_l11_t4_statement$, $m2_l11_t4_starter$$m2_l11_t4_starter$, $m2_l11_t4_solution$class Message:
    def __enter__(self):
        print("start")

    def __exit__(self, exc_type, exc, tb):
        print("end")

with Message():
    print("work")
$m2_l11_t4_solution$, 2, 50, $m2_l11_t4_topic$Месяц 2. Python Hard — Context$m2_l11_t4_topic$, $m2_l11_t4_lang$python$m2_l11_t4_lang$, $m2_l11_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l11_t4_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 11
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l11_ttitle_2$open$m2_l11_ttitle_2$,
    $m2_l11_ttitle_4$Message$m2_l11_ttitle_4$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 11
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l11_test_2_1_title$open$m2_l11_test_2_1_title$, $m2_l11_test_2_1_input$$m2_l11_test_2_1_input$, $m2_l11_test_2_1_expected$Hello$m2_l11_test_2_1_expected$, FALSE, 1),
  ($m2_l11_test_4_1_title$Message$m2_l11_test_4_1_title$, $m2_l11_test_4_1_input$$m2_l11_test_4_1_input$, $m2_l11_test_4_1_expected$start
work
end$m2_l11_test_4_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 11
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l11_b1_type$theory$m2_l11_b1_type$, $m2_l11_b1_title$Зачем with$m2_l11_b1_title$, $m2_l11_b1_content$`with` нужен для ресурсов, которые нужно закрывать.

```python
with open("data.txt", "r", encoding="utf-8") as file:
    text = file.read()
```

Файл закроется автоматически, даже если внутри блока возникнет ошибка.$m2_l11_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l11_b2_type$practice$m2_l11_b2_type$, $m2_l11_b2_title$open$m2_l11_b2_title$, $m2_l11_b2_content$**Коротко:** запиши и прочитай файл.

### Условие

Создай файл `data.txt`, запиши в него `Hello`, затем прочитай и выведи содержимое.

### Выход

```text
Hello
```$m2_l11_b2_content$, $m2_l11_b2_task_title$open$m2_l11_b2_task_title$, NULL::jsonb),
  (3, $m2_l11_b3_type$theory$m2_l11_b3_type$, $m2_l11_b3_title$__enter__$m2_l11_b3_title$, $m2_l11_b3_content$Контекстный менеджер — объект с методами `__enter__` и `__exit__`.

```python
class Manager:
    def __enter__(self):
        print("Вход")

    def __exit__(self, exc_type, exc, tb):
        print("Выход")
```$m2_l11_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l11_b4_type$practice$m2_l11_b4_type$, $m2_l11_b4_title$Message$m2_l11_b4_title$, $m2_l11_b4_content$**Коротко:** сделай простой контекст.

### Условие

Создай контекстный менеджер `Message`. При входе печатает `start`, при выходе `end`. Внутри блока выведи `work`.

### Выход

```text
start
work
end
```$m2_l11_b4_content$, $m2_l11_b4_task_title$Message$m2_l11_b4_task_title$, NULL::jsonb),
  (5, $m2_l11_b5_type$theory$m2_l11_b5_type$, $m2_l11_b5_title$contextmanager$m2_l11_b5_title$, $m2_l11_b5_content$Контекстный менеджер можно сделать функцией через `contextlib.contextmanager`.

```python
from contextlib import contextmanager

@contextmanager
def message():
    print("start")
    yield
    print("end")
```$m2_l11_b5_content$, NULL, NULL::jsonb),
  (6, $m2_l11_b6_type$practice$m2_l11_b6_type$, $m2_l11_b6_title$Resource$m2_l11_b6_title$, $m2_l11_b6_content$**Коротко:** безопасный ресурс.

### Условие

Создай контекстный менеджер `Resource`. При входе печатает `open`, при выходе `close`, внутри блока `use`.

---$m2_l11_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 12: Threads
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 12
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 12
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l12_t6_title$Lock$m2_l12_t6_title$, $m2_l12_t6_statement$**Коротко:** защити общий счётчик.

### Условие

Создай `counter = 0` и `lock = threading.Lock()`. В функции `increase()` увеличивай счётчик внутри `with lock`. Запусти 10 потоков. Выведи итог.

### Выход

```text
10
```$m2_l12_t6_statement$, $m2_l12_t6_starter$$m2_l12_t6_starter$, $m2_l12_t6_solution$import threading

counter = 0
lock = threading.Lock()

def increase():
    global counter
    with lock:
        counter += 1

threads = []
for _ in range(10):
    thread = threading.Thread(target=increase)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print(counter)
$m2_l12_t6_solution$, 2, 50, $m2_l12_t6_topic$Месяц 2. Python Hard — Threads$m2_l12_t6_topic$, $m2_l12_t6_lang$python$m2_l12_t6_lang$, $m2_l12_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l12_t6_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 12
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l12_ttitle_6$Lock$m2_l12_ttitle_6$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 12
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l12_test_6_1_title$Lock$m2_l12_test_6_1_title$, $m2_l12_test_6_1_input$$m2_l12_test_6_1_input$, $m2_l12_test_6_1_expected$10$m2_l12_test_6_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 12
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l12_b1_type$theory$m2_l12_b1_type$, $m2_l12_b1_title$Поток$m2_l12_b1_title$, $m2_l12_b1_content$Поток — часть процесса, которая может выполнять работу параллельно с другими потоками. В Python потоки особенно полезны для I/O-задач: сеть, файлы, ожидание API, ожидание БД.$m2_l12_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l12_b2_type$practice$m2_l12_b2_type$, $m2_l12_b2_title$Start$m2_l12_b2_title$, $m2_l12_b2_content$**Коротко:** запусти функцию в потоке.

### Условие

Создай функцию `worker`, которая печатает `work`. Запусти её через `threading.Thread`.$m2_l12_b2_content$, NULL, NULL::jsonb),
  (3, $m2_l12_b3_type$theory$m2_l12_b3_type$, $m2_l12_b3_title$join$m2_l12_b3_title$, $m2_l12_b3_content$`join()` заставляет основную программу дождаться завершения потока.

```python
thread.start()
thread.join()
```$m2_l12_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l12_b4_type$practice$m2_l12_b4_type$, $m2_l12_b4_title$I/O пример$m2_l12_b4_title$, $m2_l12_b4_content$**Коротко:** запусти несколько потоков.

### Условие

Создай три потока. Каждый должен напечатать `done`. Итоговый вывод должен содержать три строки `done`.$m2_l12_b4_content$, NULL, NULL::jsonb),
  (5, $m2_l12_b5_type$theory$m2_l12_b5_type$, $m2_l12_b5_title$Race$m2_l12_b5_title$, $m2_l12_b5_content$Race condition — ситуация, когда несколько потоков меняют одни и те же данные, и результат зависит от порядка выполнения.

```python
counter += 1
```

Эта операция состоит из чтения, изменения и записи. Между ними может вмешаться другой поток.$m2_l12_b5_content$, NULL, NULL::jsonb),
  (6, $m2_l12_b6_type$practice$m2_l12_b6_type$, $m2_l12_b6_title$Lock$m2_l12_b6_title$, $m2_l12_b6_content$**Коротко:** защити общий счётчик.

### Условие

Создай `counter = 0` и `lock = threading.Lock()`. В функции `increase()` увеличивай счётчик внутри `with lock`. Запусти 10 потоков. Выведи итог.

### Выход

```text
10
```$m2_l12_b6_content$, $m2_l12_b6_task_title$Lock$m2_l12_b6_task_title$, NULL::jsonb),
  (7, $m2_l12_b7_type$project$m2_l12_b7_type$, $m2_l12_b7_title$Выбор$m2_l12_b7_title$, $m2_l12_b7_content$### Ученик видит

Коротко: объясни выбор потоков.

**Задание**

Ответь письменно: для каких задач лучше использовать потоки, а для каких — нет?

---$m2_l12_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 13: Processes
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 13
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 13
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l13_t3_title$map$m2_l13_t3_title$, $m2_l13_t3_statement$**Коротко:** посчитай квадраты.

### Условие

Используй `multiprocessing.Pool`, чтобы посчитать квадраты чисел `[1, 2, 3]`. Выведи результат.

### Выход

```text
[1, 4, 9]
```$m2_l13_t3_statement$, $m2_l13_t3_starter$$m2_l13_t3_starter$, $m2_l13_t3_solution$from multiprocessing import Pool

def square(x):
    return x * x

if __name__ == "__main__":
    with Pool() as pool:
        result = pool.map(square, [1, 2, 3])
    print(result)
$m2_l13_t3_solution$, 2, 50, $m2_l13_t3_topic$Месяц 2. Python Hard — Processes$m2_l13_t3_topic$, $m2_l13_t3_lang$python$m2_l13_t3_lang$, $m2_l13_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l13_t3_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 13
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l13_ttitle_3$map$m2_l13_ttitle_3$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 13
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l13_test_3_1_title$map$m2_l13_test_3_1_title$, $m2_l13_test_3_1_input$$m2_l13_test_3_1_input$, $m2_l13_test_3_1_expected$[1, 4, 9]$m2_l13_test_3_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 13
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l13_b1_type$theory$m2_l13_b1_type$, $m2_l13_b1_title$Процесс$m2_l13_b1_title$, $m2_l13_b1_content$Процесс — отдельная запущенная программа со своей памятью. Процессы тяжелее потоков, но лучше подходят для CPU-bound задач и могут использовать несколько ядер.$m2_l13_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l13_b2_type$theory$m2_l13_b2_type$, $m2_l13_b2_title$Pool$m2_l13_b2_title$, $m2_l13_b2_content$`multiprocessing.Pool` распределяет работу между процессами.

```python
from multiprocessing import Pool

def square(x):
    return x * x

with Pool() as pool:
    result = pool.map(square, [1, 2, 3])
```$m2_l13_b2_content$, NULL, NULL::jsonb),
  (3, $m2_l13_b3_type$practice$m2_l13_b3_type$, $m2_l13_b3_title$map$m2_l13_b3_title$, $m2_l13_b3_content$**Коротко:** посчитай квадраты.

### Условие

Используй `multiprocessing.Pool`, чтобы посчитать квадраты чисел `[1, 2, 3]`. Выведи результат.

### Выход

```text
[1, 4, 9]
```$m2_l13_b3_content$, $m2_l13_b3_task_title$map$m2_l13_b3_task_title$, NULL::jsonb),
  (4, $m2_l13_b4_type$quiz$m2_l13_b4_type$, $m2_l13_b4_title$Плюсы/минусы$m2_l13_b4_title$, $m2_l13_b4_content$1. Что лучше для ожидания HTTP-запросов? Ответ: threads/asyncio.
2. Что лучше для тяжёлых CPU-вычислений? Ответ: multiprocessing.
3. Главный минус процессов? Ответ: тяжелее, отдельная память, сложнее обмен данными.$m2_l13_b4_content$, NULL, NULL::jsonb),
  (5, $m2_l13_b5_type$project$m2_l13_b5_type$, $m2_l13_b5_title$Выбор$m2_l13_b5_title$, $m2_l13_b5_content$Для каждой задачи выбери: threads, processes или asyncio.

1. Скачать 100 страниц сайта.
2. Посчитать миллионы хэшей.
3. Обработать 1000 одновременных API-запросов.
4. Прочитать 10 больших файлов.

Объясни выбор.

---$m2_l13_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 14: Asyncio
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 14
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 14
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l14_t6_title$Контроль$m2_l14_t6_title$, $m2_l14_t6_statement$**Коротко:** собери результаты async-задач.

### Условие

Создай async-функцию `double(x)`, которая возвращает `x * 2`. Через `asyncio.gather` получи результаты для `1`, `2`, `3`. Выведи список.

### Выход

```text
[2, 4, 6]
```

---$m2_l14_t6_statement$, $m2_l14_t6_starter$$m2_l14_t6_starter$, $m2_l14_t6_solution$import asyncio

async def double(x):
    return x * 2

async def main():
    result = await asyncio.gather(double(1), double(2), double(3))
    print(list(result))

asyncio.run(main())
$m2_l14_t6_solution$, 2, 50, $m2_l14_t6_topic$Месяц 2. Python Hard — Asyncio$m2_l14_t6_topic$, $m2_l14_t6_lang$python$m2_l14_t6_lang$, $m2_l14_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l14_t6_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 14
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l14_ttitle_6$Контроль$m2_l14_ttitle_6$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 14
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l14_test_6_1_title$Контроль$m2_l14_test_6_1_title$, $m2_l14_test_6_1_input$$m2_l14_test_6_1_input$, $m2_l14_test_6_1_expected$[2, 4, 6]$m2_l14_test_6_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 14
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l14_b1_type$theory$m2_l14_b1_type$, $m2_l14_b1_title$Event loop$m2_l14_b1_title$, $m2_l14_b1_content$Event loop — цикл событий. Он переключается между задачами, пока одни задачи ждут. Асинхронность полезна для HTTP-запросов, БД, очередей и сокетов.$m2_l14_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l14_b2_type$theory$m2_l14_b2_type$, $m2_l14_b2_title$async/await$m2_l14_b2_title$, $m2_l14_b2_content$Асинхронная функция объявляется через `async def`.

```python
async def main():
    print("start")
```

Запуск:

```python
import asyncio
asyncio.run(main())
```

`await` говорит: «здесь можно переключиться на другие задачи, пока мы ждём».$m2_l14_b2_content$, NULL, NULL::jsonb),
  (3, $m2_l14_b3_type$practice$m2_l14_b3_type$, $m2_l14_b3_title$sleep$m2_l14_b3_title$, $m2_l14_b3_content$**Коротко:** запусти async-функцию.

### Условие

Создай async-функцию `main`, которая печатает `start`, делает `await asyncio.sleep(0)`, затем печатает `end`.$m2_l14_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l14_b4_type$practice$m2_l14_b4_type$, $m2_l14_b4_title$gather$m2_l14_b4_title$, $m2_l14_b4_content$**Коротко:** запусти задачи вместе.

### Условие

Создай async-функцию `worker(name)`, которая печатает имя. Запусти три задачи через `asyncio.gather`: `A`, `B`, `C`.$m2_l14_b4_content$, NULL, NULL::jsonb),
  (5, $m2_l14_b5_type$practice$m2_l14_b5_type$, $m2_l14_b5_title$Ошибка await$m2_l14_b5_title$, $m2_l14_b5_content$**Коротко:** исправь запуск async-кода.$m2_l14_b5_content$, NULL, NULL::jsonb),
  (6, $m2_l14_b6_type$practice$m2_l14_b6_type$, $m2_l14_b6_title$Контроль$m2_l14_b6_title$, $m2_l14_b6_content$**Коротко:** собери результаты async-задач.

### Условие

Создай async-функцию `double(x)`, которая возвращает `x * 2`. Через `asyncio.gather` получи результаты для `1`, `2`, `3`. Выведи список.

### Выход

```text
[2, 4, 6]
```

---$m2_l14_b6_content$, $m2_l14_b6_task_title$Контроль$m2_l14_b6_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 15: Алгоритмы
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 15
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 15
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m2_l15_t3_title$Поиск$m2_l15_t3_title$, $m2_l15_t3_statement$**Коротко:** найди индекс элемента.

### Условие

Напиши функцию `find_index(items, target)`. Если элемент найден, верни индекс. Если нет — верни `-1`.

Для `[10, 20, 30]` и цели `20` выведи:

```text
1
```$m2_l15_t3_statement$, $m2_l15_t3_starter$$m2_l15_t3_starter$, $m2_l15_t3_solution$def find_index(items, target):
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1

print(find_index([10, 20, 30], 20))
$m2_l15_t3_solution$, 2, 50, $m2_l15_t3_topic$Месяц 2. Python Hard — Алгоритмы$m2_l15_t3_topic$, $m2_l15_t3_lang$python$m2_l15_t3_lang$, $m2_l15_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l15_t3_policy$::jsonb),
  ($m2_l15_t4_title$Stack$m2_l15_t4_title$, $m2_l15_t4_statement$**Коротко:** реализуй стек.

### Условие

Создай класс `Stack` с методами `push`, `pop`, `is_empty`. Добавь `1`, `2`, затем выведи два `pop()`.

### Выход

```text
2
1
```$m2_l15_t4_statement$, $m2_l15_t4_starter$$m2_l15_t4_starter$, $m2_l15_t4_solution$class Stack:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)

    def pop(self):
        return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

stack = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())
print(stack.pop())
$m2_l15_t4_solution$, 2, 50, $m2_l15_t4_topic$Месяц 2. Python Hard — Алгоритмы$m2_l15_t4_topic$, $m2_l15_t4_lang$python$m2_l15_t4_lang$, $m2_l15_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l15_t4_policy$::jsonb),
  ($m2_l15_t5_title$Queue$m2_l15_t5_title$, $m2_l15_t5_statement$**Коротко:** реализуй очередь.

### Условие

Создай очередь через `collections.deque`. Добавь `1`, `2`, `3`. Достань два элемента слева.

### Выход

```text
1
2
```$m2_l15_t5_statement$, $m2_l15_t5_starter$$m2_l15_t5_starter$, $m2_l15_t5_solution$from collections import deque

queue = deque()
queue.append(1)
queue.append(2)
queue.append(3)

print(queue.popleft())
print(queue.popleft())
$m2_l15_t5_solution$, 2, 50, $m2_l15_t5_topic$Месяц 2. Python Hard — Алгоритмы$m2_l15_t5_topic$, $m2_l15_t5_lang$python$m2_l15_t5_lang$, $m2_l15_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l15_t5_policy$::jsonb),
  ($m2_l15_t7_title$Скобки$m2_l15_t7_title$, $m2_l15_t7_statement$**Коротко:** проверь скобки.

### Условие

Напиши функцию `is_valid(text)`. Она проверяет круглые скобки.

Для строки `"(()())"` выведи:

```text
True
```

---$m2_l15_t7_statement$, $m2_l15_t7_starter$$m2_l15_t7_starter$, $m2_l15_t7_solution$def is_valid(text):
    stack = []
    for char in text:
        if char == "(":
            stack.append(char)
        elif char == ")":
            if not stack:
                return False
            stack.pop()
    return len(stack) == 0

print(is_valid("(()())"))
$m2_l15_t7_solution$, 2, 50, $m2_l15_t7_topic$Месяц 2. Python Hard — Алгоритмы$m2_l15_t7_topic$, $m2_l15_t7_lang$python$m2_l15_t7_lang$, $m2_l15_t7_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m2_l15_t7_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 15
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m2_l15_ttitle_3$Поиск$m2_l15_ttitle_3$,
    $m2_l15_ttitle_4$Stack$m2_l15_ttitle_4$,
    $m2_l15_ttitle_5$Queue$m2_l15_ttitle_5$,
    $m2_l15_ttitle_7$Скобки$m2_l15_ttitle_7$
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
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 15
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m2_l15_test_3_1_title$Поиск$m2_l15_test_3_1_title$, $m2_l15_test_3_1_input$$m2_l15_test_3_1_input$, $m2_l15_test_3_1_expected$1$m2_l15_test_3_1_expected$, FALSE, 1),
  ($m2_l15_test_4_1_title$Stack$m2_l15_test_4_1_title$, $m2_l15_test_4_1_input$$m2_l15_test_4_1_input$, $m2_l15_test_4_1_expected$2
1$m2_l15_test_4_1_expected$, FALSE, 1),
  ($m2_l15_test_5_1_title$Queue$m2_l15_test_5_1_title$, $m2_l15_test_5_1_input$$m2_l15_test_5_1_input$, $m2_l15_test_5_1_expected$1
2$m2_l15_test_5_1_expected$, FALSE, 1),
  ($m2_l15_test_7_1_title$Скобки$m2_l15_test_7_1_title$, $m2_l15_test_7_1_input$$m2_l15_test_7_1_input$, $m2_l15_test_7_1_expected$True$m2_l15_test_7_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 15
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l15_b1_type$theory$m2_l15_b1_type$, $m2_l15_b1_title$Big O$m2_l15_b1_title$, $m2_l15_b1_content$Big O показывает, как растёт время или память при росте входных данных.

```text
O(1)       не зависит от размера
O(n)       один проход
O(n²)      вложенные циклы
O(log n)   делим задачу пополам
O(n log n) типичная сортировка
```

Big O не считает секунды. Он показывает характер роста.$m2_l15_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l15_b2_type$quiz$m2_l15_b2_type$, $m2_l15_b2_title$O-тест$m2_l15_b2_title$, $m2_l15_b2_content$1. Поиск элемента простым перебором — `O(n)`.
2. Доступ к элементу списка по индексу — обычно `O(1)`.
3. Два вложенных цикла по одному списку — часто `O(n²)`.$m2_l15_b2_content$, NULL, NULL::jsonb),
  (3, $m2_l15_b3_type$practice$m2_l15_b3_type$, $m2_l15_b3_title$Поиск$m2_l15_b3_title$, $m2_l15_b3_content$**Коротко:** найди индекс элемента.

### Условие

Напиши функцию `find_index(items, target)`. Если элемент найден, верни индекс. Если нет — верни `-1`.

Для `[10, 20, 30]` и цели `20` выведи:

```text
1
```$m2_l15_b3_content$, $m2_l15_b3_task_title$Поиск$m2_l15_b3_task_title$, NULL::jsonb),
  (4, $m2_l15_b4_type$practice$m2_l15_b4_type$, $m2_l15_b4_title$Stack$m2_l15_b4_title$, $m2_l15_b4_content$**Коротко:** реализуй стек.

### Условие

Создай класс `Stack` с методами `push`, `pop`, `is_empty`. Добавь `1`, `2`, затем выведи два `pop()`.

### Выход

```text
2
1
```$m2_l15_b4_content$, $m2_l15_b4_task_title$Stack$m2_l15_b4_task_title$, NULL::jsonb),
  (5, $m2_l15_b5_type$practice$m2_l15_b5_type$, $m2_l15_b5_title$Queue$m2_l15_b5_title$, $m2_l15_b5_content$**Коротко:** реализуй очередь.

### Условие

Создай очередь через `collections.deque`. Добавь `1`, `2`, `3`. Достань два элемента слева.

### Выход

```text
1
2
```$m2_l15_b5_content$, $m2_l15_b5_task_title$Queue$m2_l15_b5_task_title$, NULL::jsonb),
  (6, $m2_l15_b6_type$theory$m2_l15_b6_type$, $m2_l15_b6_title$Hash$m2_l15_b6_title$, $m2_l15_b6_content$Хэш-таблица лежит в основе `dict` и `set`. Она позволяет быстро искать по ключу.

```python
users = {"a@mail.com": "Анна"}
print(users["a@mail.com"])
```

Ключ словаря должен быть хэшируемым. Список не подходит как ключ, потому что он изменяемый.$m2_l15_b6_content$, NULL, NULL::jsonb),
  (7, $m2_l15_b7_type$practice$m2_l15_b7_type$, $m2_l15_b7_title$Скобки$m2_l15_b7_title$, $m2_l15_b7_content$**Коротко:** проверь скобки.

### Условие

Напиши функцию `is_valid(text)`. Она проверяет круглые скобки.

Для строки `"(()())"` выведи:

```text
True
```

---$m2_l15_b7_content$, $m2_l15_b7_task_title$Скобки$m2_l15_b7_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 2, lesson 16: Проект bot
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 16
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 2 AND l.position = 16
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m2_l16_b1_type$theory$m2_l16_b1_type$, $m2_l16_b1_title$ТЗ$m2_l16_b1_title$, $m2_l16_b1_content$Нужно сделать один из вариантов:

1. Telegram-бот задач.
2. Локальный async-сервис очереди задач без Telegram.

Минимальные функции:

```text
/add задача
/list
/done id
/delete id
/help
```

Если внешний сервис не подключается, делай локальную async-версию. Важнее архитектура, а не конкретный API.$m2_l16_b1_content$, NULL, NULL::jsonb),
  (2, $m2_l16_b2_type$theory$m2_l16_b2_type$, $m2_l16_b2_title$Архитектура$m2_l16_b2_title$, $m2_l16_b2_content$Рекомендуемая структура:

```text
project/
  app/
    main.py
    models.py
    services.py
    storage.py
  tests/
    test_tasks.py
  README.md
```

Логика задач должна быть отдельно от интерфейса бота.$m2_l16_b2_content$, NULL, NULL::jsonb),
  (3, $m2_l16_b3_type$practice$m2_l16_b3_type$, $m2_l16_b3_title$Команды$m2_l16_b3_title$, $m2_l16_b3_content$### Условие

Реализуй команды `add`, `list`, `done`, `delete`. Каждая команда должна вызывать сервис, а не менять данные напрямую в обработчике.$m2_l16_b3_content$, NULL, NULL::jsonb),
  (4, $m2_l16_b4_type$practice$m2_l16_b4_type$, $m2_l16_b4_title$Storage$m2_l16_b4_title$, $m2_l16_b4_content$### Условие

Сохраняй задачи в JSON.

```json
{
  "id": 1,
  "title": "Task",
  "done": false,
  "created_at": "2026-01-01T12:00:00"
}
```$m2_l16_b4_content$, NULL, NULL::jsonb),
  (5, $m2_l16_b5_type$practice$m2_l16_b5_type$, $m2_l16_b5_title$Async$m2_l16_b5_title$, $m2_l16_b5_content$### Условие

Добавь асинхронную функцию обработки команды.

```python
async def handle_command(command: str) -> str:
    ...
```

Функция должна возвращать текст ответа.$m2_l16_b5_content$, NULL, NULL::jsonb),
  (6, $m2_l16_b6_type$practice$m2_l16_b6_type$, $m2_l16_b6_title$Tests$m2_l16_b6_title$, $m2_l16_b6_content$### Условие

Напиши минимум 5 тестов:

- добавление задачи;
- список задач;
- выполнение задачи;
- удаление задачи;
- неправильный id.$m2_l16_b6_content$, NULL, NULL::jsonb),
  (7, $m2_l16_b7_type$practice$m2_l16_b7_type$, $m2_l16_b7_title$README$m2_l16_b7_title$, $m2_l16_b7_content$### Условие

README должен содержать описание проекта, запуск, команды, примеры, структуру проекта, сложности и идеи улучшений.$m2_l16_b7_content$, NULL, NULL::jsonb),
  (8, $m2_l16_b8_type$project$m2_l16_b8_type$, $m2_l16_b8_title$Защита$m2_l16_b8_title$, $m2_l16_b8_content$Отправь проект на проверку.

---

# Экзамен месяца 2

**В интерфейсе:** Экзамен 2  
**Формат:** автозадачи + AI-review проекта.

## Обязательные задачи

1. Класс `User` с `__str__`.
2. Класс `Cart` с методами `add`, `total`, `clear`.
3. Исключение для неправильного ввода.
4. Генератор страниц.
5. Декоратор логирования.
6. Асинхронный запуск трёх задач.
7. Стек или проверка скобок.

## Маршрут восстановления

Если ученик провалил:

- ООП → уроки 1–5;
- типы/исключения → уроки 6–7;
- генераторы/декораторы/context → уроки 8–11;
- конкурентность → уроки 12–14;
- алгоритмы → урок 15.
# Месяц 3. SQL, базы данных, SQL с Python, сети и интернет

Цель месяца: ученик умеет проектировать простую реляционную схему, писать SQL-запросы, понимать транзакции и индексы, подключать Python к БД, объяснять HTTP/REST и строить API-контракты.

## Сетка месяца

| Урок | Название | Фокус | Проверка |
|---:|---|---|---|
| 1 | БД | зачем БД, таблицы, строки, связи | тест |
| 2 | SELECT | выборка колонок | SQL-runner |
| 3 | WHERE | фильтры, сортировка, LIMIT | SQL-runner |
| 4 | JOIN | связи таблиц | SQL-runner |
| 5 | GROUP BY | агрегации, HAVING | SQL-runner |
| 6 | CTE | подзапросы, WITH | SQL-runner |
| 7 | Schema | DDL, constraints, нормализация | SQL-runner + AI |
| 8 | DML | INSERT, UPDATE, DELETE | SQL-runner |
| 9 | ACID | транзакции | тест + SQL |
| 10 | Isolation | изоляция и блокировки | тест + кейсы |
| 11 | Indexes | индексы, EXPLAIN | SQL + AI |
| 12 | sqlite3 | SQL с Python | Python-runner |
| 13 | SQLAlchemy | Core, ORM, Session | Python-runner |
| 14 | NoSQL | Redis, Mongo, ClickHouse, S3 | тест |
| 15 | Сети | TCP/UDP, DNS, HTTP/HTTPS | тест |
| 16 | REST | методы, коды, идемпотентность | тест + контракт |
| 17 | Протоколы | SOAP, GraphQL, gRPC, WS | тест |
| 18 | Проект DB | БД + Python script | AI-check |

---

# Учебная база данных

Для большинства SQL-задач используется одна схема: учебный интернет-магазин.

## Таблицы

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    age INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    price INTEGER NOT NULL,
    in_stock BOOLEAN NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## Данные

```sql
INSERT INTO users VALUES
(1, 'Анна', 'Москва', 20, TRUE),
(2, 'Олег', 'Казань', 17, TRUE),
(3, 'Мария', 'Москва', 31, FALSE),
(4, 'Иван', 'Сочи', 25, TRUE),
(5, 'Даша', 'Казань', 28, TRUE);

INSERT INTO categories VALUES
(1, 'Книги'),
(2, 'Техника'),
(3, 'Канцелярия');

INSERT INTO products VALUES
(1, 'Python Book', 1, 1200, TRUE),
(2, 'Notebook', 3, 200, TRUE),
(3, 'Keyboard', 2, 3500, TRUE),
(4, 'Mouse', 2, 1500, FALSE),
(5, 'SQL Book', 1, 1000, TRUE);

INSERT INTO orders VALUES
(1, 1, 'paid', '2026-01-10'),
(2, 2, 'new', '2026-01-11'),
(3, 1, 'cancelled', '2026-01-12'),
(4, 4, 'paid', '2026-01-13');

INSERT INTO order_items VALUES
(1, 1, 1, 1200),
(1, 2, 3, 200),
(2, 3, 1, 3500),
(3, 5, 2, 1000),
(4, 1, 1, 1200),
(4, 3, 1, 3500);
```

---$m2_l16_b8_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3: Месяц 3. SQL и сети
WITH module_ref AS (
  SELECT m.id AS module_id
  FROM modules m
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3
), lesson_seed(position, title, content_md) AS (
  VALUES
  (1, $m3_l1_title$БД$m3_l1_title$, $m3_l1_content$Зачем нужны базы данных и как они устроены.$m3_l1_content$),
  (2, $m3_l2_title$SELECT$m3_l2_title$, $m3_l2_content$Получаем данные из таблицы.$m3_l2_content$),
  (3, $m3_l3_title$WHERE$m3_l3_title$, $m3_l3_content$Фильтруем, сортируем и ограничиваем результат.$m3_l3_content$),
  (4, $m3_l4_title$JOIN$m3_l4_title$, $m3_l4_content$Соединяем таблицы.$m3_l4_content$),
  (5, $m3_l5_title$GROUP BY$m3_l5_title$, $m3_l5_content$Группируем строки и считаем агрегаты.$m3_l5_content$),
  (6, $m3_l6_title$CTE$m3_l6_title$, $m3_l6_content$Подзапросы и временные результаты.$m3_l6_content$),
  (7, $m3_l7_title$Schema$m3_l7_title$, $m3_l7_content$Создаём таблицы и ограничения.$m3_l7_content$),
  (8, $m3_l8_title$DML$m3_l8_title$, $m3_l8_content$Добавляем, меняем и удаляем данные.$m3_l8_content$),
  (9, $m3_l9_title$ACID$m3_l9_title$, $m3_l9_content$Транзакции защищают данные.$m3_l9_content$),
  (10, $m3_l10_title$Isolation$m3_l10_title$, $m3_l10_content$Что происходит при параллельных транзакциях.$m3_l10_content$),
  (11, $m3_l11_title$Indexes$m3_l11_title$, $m3_l11_content$Индексы ускоряют поиск, но не бесплатны.$m3_l11_content$),
  (12, $m3_l12_title$sqlite3$m3_l12_title$, $m3_l12_content$Выполняем SQL из Python.$m3_l12_content$),
  (13, $m3_l13_title$SQLAlchemy$m3_l13_title$, $m3_l13_content$Работаем с БД через Python-объекты.$m3_l13_content$),
  (14, $m3_l14_title$NoSQL$m3_l14_title$, $m3_l14_content$Когда реляционная БД не единственный вариант.$m3_l14_content$),
  (15, $m3_l15_title$Сети$m3_l15_title$, $m3_l15_content$Как клиент общается с сервером.$m3_l15_content$),
  (16, $m3_l16_title$REST$m3_l16_title$, $m3_l16_content$Проектируем понятные API.$m3_l16_content$),
  (17, $m3_l17_title$Протоколы$m3_l17_title$, $m3_l17_content$SOAP, GraphQL, gRPC и WebSockets.$m3_l17_content$),
  (18, $m3_l18_title$Проект DB$m3_l18_title$, $m3_l18_content$Поднять БД и наполнить её Python-скриптом.$m3_l18_content$)
)
INSERT INTO lessons(module_id, title, content_md, position, is_published)
SELECT mr.module_id, ls.title, ls.content_md, ls.position, TRUE
FROM module_ref mr
CROSS JOIN lesson_seed ls
ON CONFLICT (module_id, position) DO UPDATE
SET title = EXCLUDED.title,
    content_md = EXCLUDED.content_md,
    is_published = TRUE,
    updated_at = NOW();

-- Module 3, lesson 1: БД
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 1
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 1
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l1_b1_type$theory$m3_l1_b1_type$, $m3_l1_b1_title$Зачем БД$m3_l1_b1_title$, $m3_l1_b1_content$Файл подходит, когда данных мало и с ними работает одна программа. База данных нужна, когда данных больше, есть поиск, связи, несколько пользователей, транзакции и требования к надёжности.

Пример: список задач можно хранить в JSON. Но интернет-магазин с пользователями, заказами и товарами лучше хранить в БД.$m3_l1_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l1_b2_type$theory$m3_l1_b2_type$, $m3_l1_b2_title$Таблица$m3_l1_b2_title$, $m3_l1_b2_content$Таблица похожа на таблицу в Excel:

```text
users
id | name | city
1  | Анна | Москва
2  | Олег | Казань
```

Строка — одна запись. Колонка — поле записи.$m3_l1_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l1_b3_type$theory$m3_l1_b3_type$, $m3_l1_b3_title$Ключи$m3_l1_b3_title$, $m3_l1_b3_content$`PRIMARY KEY` — уникальный идентификатор строки.

```sql
id INTEGER PRIMARY KEY
```

`FOREIGN KEY` — ссылка на строку в другой таблице.

```sql
user_id INTEGER REFERENCES users(id)
```

Так заказ связывается с пользователем.$m3_l1_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l1_b4_type$theory$m3_l1_b4_type$, $m3_l1_b4_title$Связи$m3_l1_b4_title$, $m3_l1_b4_content$Основные связи:

```text
one-to-one      один к одному
one-to-many     один ко многим
many-to-many    многие ко многим
```

Пример:

- один пользователь может иметь много заказов;
- один заказ может содержать много товаров;
- один товар может входить в разные заказы.

Для many-to-many нужна промежуточная таблица. В нашем магазине это `order_items`.$m3_l1_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l1_b5_type$quiz$m3_l1_b5_type$, $m3_l1_b5_title$SQL или файл$m3_l1_b5_title$, $m3_l1_b5_content$1. Где лучше хранить 5 заметок одного пользователя? Ответ: файл тоже подойдёт.
2. Где лучше хранить заказы магазина? Ответ: БД.
3. Что такое `PRIMARY KEY`? Ответ: уникальный идентификатор строки.
4. Что такое `FOREIGN KEY`? Ответ: ссылка на другую таблицу.$m3_l1_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l1_b6_type$project$m3_l1_b6_type$, $m3_l1_b6_title$Схема$m3_l1_b6_title$, $m3_l1_b6_content$### Ученик видит

Коротко: предложи схему БД.

**Задание**

Нужно хранить студентов, курсы и записи студентов на курсы. Предложи таблицы и связи.

---$m3_l1_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 2: SELECT
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 2
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 2
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l2_b1_type$theory$m3_l2_b1_type$, $m3_l2_b1_title$SELECT$m3_l2_b1_title$, $m3_l2_b1_content$`SELECT` получает данные из таблицы.

```sql
SELECT name
FROM users;
```

`*` означает все колонки:

```sql
SELECT *
FROM users;
```

В реальной работе лучше явно указывать нужные колонки.$m3_l2_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l2_b2_type$practice$m3_l2_b2_type$, $m3_l2_b2_title$Все строки$m3_l2_b2_title$, $m3_l2_b2_content$**Коротко:** выбери всех пользователей.

### Условие

Напиши SQL-запрос, который возвращает все колонки из таблицы `users`.$m3_l2_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l2_b3_type$practice$m3_l2_b3_type$, $m3_l2_b3_title$Колонки$m3_l2_b3_title$, $m3_l2_b3_content$**Коротко:** выбери имя и город.

### Условие

Выведи только `name` и `city` из таблицы `users`.

**Ожидаемые первые строки**

```text
Анна | Москва
Олег | Казань
```$m3_l2_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l2_b4_type$theory$m3_l2_b4_type$, $m3_l2_b4_title$AS$m3_l2_b4_title$, $m3_l2_b4_content$`AS` задаёт псевдоним колонки.

```sql
SELECT name AS user_name
FROM users;
```

Это удобно в отчётах и сложных запросах.$m3_l2_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l2_b5_type$practice$m3_l2_b5_type$, $m3_l2_b5_title$Имена$m3_l2_b5_title$, $m3_l2_b5_content$**Коротко:** выведи названия товаров.

### Условие

Выведи колонку `title` из таблицы `products`. Назови колонку `product_title`.

---$m3_l2_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 3: WHERE
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 3
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 3
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l3_b1_type$theory$m3_l3_b1_type$, $m3_l3_b1_title$Фильтр$m3_l3_b1_title$, $m3_l3_b1_content$`WHERE` оставляет только строки, которые подходят под условие.

```sql
SELECT name
FROM users
WHERE city = 'Москва';
```

Строки пишутся в одинарных кавычках.$m3_l3_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l3_b2_type$practice$m3_l3_b2_type$, $m3_l3_b2_title$Активные$m3_l3_b2_title$, $m3_l3_b2_content$**Коротко:** выбери активных пользователей.

### Условие

Выведи `name` пользователей, у которых `is_active = TRUE`.$m3_l3_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l3_b3_type$theory$m3_l3_b3_type$, $m3_l3_b3_title$AND/OR$m3_l3_b3_title$, $m3_l3_b3_content$`AND` требует, чтобы оба условия были истинны. `OR` требует хотя бы одно условие.

```sql
SELECT name
FROM users
WHERE city = 'Казань' AND age >= 18;
```$m3_l3_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l3_b4_type$practice$m3_l3_b4_type$, $m3_l3_b4_title$Цена$m3_l3_b4_title$, $m3_l3_b4_content$**Коротко:** найди товары дороже 1000.

### Условие

Выведи `title` и `price` товаров, у которых `price > 1000` и `in_stock = TRUE`.$m3_l3_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l3_b5_type$theory$m3_l3_b5_type$, $m3_l3_b5_title$ORDER BY$m3_l3_b5_title$, $m3_l3_b5_content$`ORDER BY` сортирует результат.

```sql
SELECT title, price
FROM products
ORDER BY price DESC;
```

`ASC` — по возрастанию. `DESC` — по убыванию.$m3_l3_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l3_b6_type$practice$m3_l3_b6_type$, $m3_l3_b6_title$TOP$m3_l3_b6_title$, $m3_l3_b6_content$**Коротко:** найди самый дорогой товар.

### Условие

Выведи `title` и `price` самого дорогого товара.$m3_l3_b6_content$, NULL, NULL::jsonb),
  (7, $m3_l3_b7_type$practice$m3_l3_b7_type$, $m3_l3_b7_title$Контроль$m3_l3_b7_title$, $m3_l3_b7_content$**Коротко:** активные взрослые.

### Условие

Выведи `name` и `age` активных пользователей старше или равных 18 лет. Отсортируй по возрасту по возрастанию.

---$m3_l3_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 4: JOIN
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 4
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 4
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l4_b1_type$theory$m3_l4_b1_type$, $m3_l4_b1_title$Зачем JOIN$m3_l4_b1_title$, $m3_l4_b1_content$Данные часто хранятся в разных таблицах.

`orders` хранит `user_id`, но имя пользователя лежит в `users`.

```sql
SELECT users.name, orders.status
FROM orders
JOIN users ON users.id = orders.user_id;
```

`JOIN` соединяет строки по условию.$m3_l4_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l4_b2_type$practice$m3_l4_b2_type$, $m3_l4_b2_title$user orders$m3_l4_b2_title$, $m3_l4_b2_content$**Коротко:** выведи заказы с именами.

### Условие

Выведи `orders.id`, `users.name`, `orders.status` для всех заказов.$m3_l4_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l4_b3_type$theory$m3_l4_b3_type$, $m3_l4_b3_title$INNER/LEFT$m3_l4_b3_title$, $m3_l4_b3_content$`INNER JOIN` возвращает строки, где есть совпадение в обеих таблицах.

`LEFT JOIN` возвращает все строки из левой таблицы, даже если справа совпадения нет.

Пример: показать всех пользователей, даже если у них нет заказов.

```sql
SELECT users.name, orders.id
FROM users
LEFT JOIN orders ON orders.user_id = users.id;
```$m3_l4_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l4_b4_type$practice$m3_l4_b4_type$, $m3_l4_b4_title$products$m3_l4_b4_title$, $m3_l4_b4_content$**Коротко:** товар и категория.

### Условие

Выведи название товара и название категории.

Колонки:

```text
product_title
category_title
```$m3_l4_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l4_b5_type$theory$m3_l4_b5_type$, $m3_l4_b5_title$many-to-many$m3_l4_b5_title$, $m3_l4_b5_content$Заказ содержит много товаров. Товар может быть в разных заказах. Это связь many-to-many.

Для неё нужна промежуточная таблица:

```text
orders → order_items → products
```

`order_items` хранит:

- `order_id`;
- `product_id`;
- `quantity`;
- `price` на момент покупки.$m3_l4_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l4_b6_type$practice$m3_l4_b6_type$, $m3_l4_b6_title$order total$m3_l4_b6_title$, $m3_l4_b6_content$**Коротко:** сумма каждого заказа.

### Условие

Выведи `order_id` и сумму заказа.

Сумма строки заказа:

```text
quantity * price
```

Отсортируй по `order_id`.

---$m3_l4_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 5: GROUP BY
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 5
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 5
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l5_b1_type$theory$m3_l5_b1_type$, $m3_l5_b1_title$Агрегаты$m3_l5_b1_title$, $m3_l5_b1_content$Агрегатные функции считают значение по набору строк.

```sql
COUNT(*)
SUM(price)
AVG(age)
MIN(price)
MAX(price)
```$m3_l5_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l5_b2_type$practice$m3_l5_b2_type$, $m3_l5_b2_title$count$m3_l5_b2_title$, $m3_l5_b2_content$**Коротко:** посчитай пользователей.

### Условие

Выведи количество пользователей.$m3_l5_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l5_b3_type$theory$m3_l5_b3_type$, $m3_l5_b3_title$group$m3_l5_b3_title$, $m3_l5_b3_content$`GROUP BY` объединяет строки в группы.

```sql
SELECT city, COUNT(*)
FROM users
GROUP BY city;
```

Так можно посчитать пользователей по городам.$m3_l5_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l5_b4_type$practice$m3_l5_b4_type$, $m3_l5_b4_title$by city$m3_l5_b4_title$, $m3_l5_b4_content$**Коротко:** пользователи по городам.

### Условие

Выведи город и количество пользователей в нём. Отсортируй по городу.$m3_l5_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l5_b5_type$theory$m3_l5_b5_type$, $m3_l5_b5_title$having$m3_l5_b5_title$, $m3_l5_b5_content$`WHERE` фильтрует строки до группировки. `HAVING` фильтрует группы после группировки.

```sql
SELECT city, COUNT(*)
FROM users
GROUP BY city
HAVING COUNT(*) >= 2;
```$m3_l5_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l5_b6_type$practice$m3_l5_b6_type$, $m3_l5_b6_title$revenue$m3_l5_b6_title$, $m3_l5_b6_content$**Коротко:** выручка по статусу заказа.

### Условие

Выведи статус заказа и сумму строк заказа. Учитывай только статусы из таблицы `orders`. Соедини `orders` и `order_items`. Отсортируй по статусу.

---$m3_l5_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 6: CTE
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 6
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 6
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l6_b1_type$theory$m3_l6_b1_type$, $m3_l6_b1_title$Subquery$m3_l6_b1_title$, $m3_l6_b1_content$Подзапрос — запрос внутри другого запроса.

```sql
SELECT title, price
FROM products
WHERE price > (
    SELECT AVG(price)
    FROM products
);
```$m3_l6_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l6_b2_type$practice$m3_l6_b2_type$, $m3_l6_b2_title$expensive$m3_l6_b2_title$, $m3_l6_b2_content$**Коротко:** товары дороже среднего.

### Условие

Выведи `title` и `price` товаров, цена которых выше средней цены всех товаров.$m3_l6_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l6_b3_type$theory$m3_l6_b3_type$, $m3_l6_b3_title$WITH$m3_l6_b3_title$, $m3_l6_b3_content$CTE через `WITH` помогает разбить сложный запрос на понятные части.

```sql
WITH order_totals AS (
    SELECT order_id, SUM(quantity * price) AS total
    FROM order_items
    GROUP BY order_id
)
SELECT *
FROM order_totals;
```$m3_l6_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l6_b4_type$practice$m3_l6_b4_type$, $m3_l6_b4_title$totals$m3_l6_b4_title$, $m3_l6_b4_content$**Коротко:** заказы дороже 3000.

### Условие

Через CTE посчитай сумму каждого заказа и выведи только заказы с суммой больше `3000`.$m3_l6_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l6_b5_type$practice$m3_l6_b5_type$, $m3_l6_b5_title$Контроль$m3_l6_b5_title$, $m3_l6_b5_content$**Коротко:** пользователи с оплаченной суммой.

### Условие

Через CTE посчитай сумму только оплаченных заказов (`status = 'paid'`) по каждому пользователю. Выведи имя пользователя и сумму.

---$m3_l6_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 7: Schema
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 7
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 7
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l7_b1_type$theory$m3_l7_b1_type$, $m3_l7_b1_title$CREATE TABLE$m3_l7_b1_title$, $m3_l7_b1_content$Таблица создаётся через `CREATE TABLE`.

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL
);
```

Типы зависят от СУБД, но идея одна: каждая колонка имеет имя и тип.$m3_l7_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l7_b2_type$theory$m3_l7_b2_type$, $m3_l7_b2_title$NOT NULL$m3_l7_b2_title$, $m3_l7_b2_content$Ограничения защищают данные от неправильного состояния.

```sql
name TEXT NOT NULL
email TEXT UNIQUE
age INTEGER CHECK (age >= 0)
```

Если не поставить ограничения, плохие данные попадут в базу.$m3_l7_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l7_b3_type$theory$m3_l7_b3_type$, $m3_l7_b3_title$Keys$m3_l7_b3_title$, $m3_l7_b3_content$`PRIMARY KEY` уникально определяет строку.

`FOREIGN KEY` связывает таблицы.

```sql
CREATE TABLE enrollments (
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id)
);
```$m3_l7_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l7_b4_type$practice$m3_l7_b4_type$, $m3_l7_b4_title$Student$m3_l7_b4_title$, $m3_l7_b4_content$**Коротко:** создай таблицу студентов.

### Условие

Создай таблицу `students`:

- `id` — primary key;
- `name` — text, not null;
- `age` — integer, age >= 0;
- `email` — text, unique.$m3_l7_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l7_b5_type$theory$m3_l7_b5_type$, $m3_l7_b5_title$Normal form$m3_l7_b5_title$, $m3_l7_b5_content$Нормализация помогает не дублировать данные.

Плохо:

```text
order_id | user_name | user_city | product_title
```

Если город пользователя изменится, его придётся менять во многих строках.

Лучше разделить:

```text
users
orders
products
order_items
```$m3_l7_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l7_b6_type$project$m3_l7_b6_type$, $m3_l7_b6_title$Design$m3_l7_b6_title$, $m3_l7_b6_content$### Ученик видит

Коротко: спроектируй схему.

**Задание**

Нужно хранить блог: пользователи, статьи, комментарии, теги. Предложи таблицы и связи.

---$m3_l7_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 8: DML
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 8
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 8
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l8_b1_type$theory$m3_l8_b1_type$, $m3_l8_b1_title$INSERT$m3_l8_b1_title$, $m3_l8_b1_content$`INSERT` добавляет строки.

```sql
INSERT INTO users (id, name, city, age, is_active)
VALUES (6, 'Пётр', 'Тула', 22, TRUE);
```

Лучше явно указывать колонки.$m3_l8_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l8_b2_type$practice$m3_l8_b2_type$, $m3_l8_b2_title$Add user$m3_l8_b2_title$, $m3_l8_b2_content$**Коротко:** добавь пользователя.

### Условие

Добавь пользователя:

```text
id = 6
name = Пётр
city = Тула
age = 22
is_active = TRUE
```

Затем выведи его имя и город.$m3_l8_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l8_b3_type$theory$m3_l8_b3_type$, $m3_l8_b3_title$UPDATE$m3_l8_b3_title$, $m3_l8_b3_content$`UPDATE` изменяет строки.

```sql
UPDATE users
SET city = 'Москва'
WHERE id = 2;
```

Без `WHERE` изменятся все строки. Это частая опасная ошибка.$m3_l8_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l8_b4_type$practice$m3_l8_b4_type$, $m3_l8_b4_title$Activate$m3_l8_b4_title$, $m3_l8_b4_content$**Коротко:** активируй пользователя.

### Условие

Пользователь с `id = 3` неактивен. Сделай его активным и выведи `name`, `is_active`.$m3_l8_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l8_b5_type$theory$m3_l8_b5_type$, $m3_l8_b5_title$DELETE$m3_l8_b5_title$, $m3_l8_b5_content$`DELETE` удаляет строки.

```sql
DELETE FROM users
WHERE id = 5;
```

Без `WHERE` удалятся все строки. В реальной работе перед `DELETE` полезно сначала написать `SELECT` с тем же условием.$m3_l8_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l8_b6_type$practice$m3_l8_b6_type$, $m3_l8_b6_title$Safe delete$m3_l8_b6_title$, $m3_l8_b6_content$**Коротко:** безопасное удаление.

### Условие

Удалять ничего не нужно. Напиши запрос `SELECT`, который показывает, какие заказы будут удалены, если удалить заказы со статусом `cancelled`.

---$m3_l8_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 9: ACID
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 9
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 9
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l9_b1_type$theory$m3_l9_b1_type$, $m3_l9_b1_title$Transaction$m3_l9_b1_title$, $m3_l9_b1_content$Транзакция — группа операций, которая должна выполниться целиком или не выполниться вообще.

Пример: перевод денег.

```text
1. Списать 100 с Алисы.
2. Добавить 100 Бобу.
```

Если первая операция прошла, а вторая нет, данные сломаны. Поэтому нужен единый блок.$m3_l9_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l9_b2_type$practice$m3_l9_b2_type$, $m3_l9_b2_title$BEGIN/COMMIT$m3_l9_b2_title$, $m3_l9_b2_content$**Коротко:** оформи транзакцию.

### Условие

Напиши SQL-транзакцию, которая меняет статус заказа `id = 2` на `paid`.$m3_l9_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l9_b3_type$theory$m3_l9_b3_type$, $m3_l9_b3_title$ROLLBACK$m3_l9_b3_title$, $m3_l9_b3_content$`ROLLBACK` отменяет изменения в транзакции.

```sql
BEGIN;
UPDATE users SET city = 'Test';
ROLLBACK;
```

После `ROLLBACK` изменения не сохранятся.$m3_l9_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l9_b4_type$theory$m3_l9_b4_type$, $m3_l9_b4_title$ACID$m3_l9_b4_title$, $m3_l9_b4_content$ACID — свойства транзакций:

- Atomicity — всё или ничего;
- Consistency — данные остаются корректными;
- Isolation — параллельные транзакции не ломают друг друга;
- Durability — после commit данные сохранены.$m3_l9_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l9_b5_type$practice$m3_l9_b5_type$, $m3_l9_b5_title$Transfer$m3_l9_b5_title$, $m3_l9_b5_content$**Коротко:** опиши транзакцию перевода.

### Условие

Есть таблица:

```sql
accounts(id, balance)
```

Напиши транзакцию: списать `100` со счёта `1` и добавить `100` на счёт `2`.

---$m3_l9_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 10: Isolation
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 10
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 10
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l10_b1_type$theory$m3_l10_b1_type$, $m3_l10_b1_title$Проблема$m3_l10_b1_title$, $m3_l10_b1_content$Если две транзакции работают с одними данными одновременно, возможны странные эффекты:

- одна читает незакоммиченные данные другой;
- одно и то же чтение даёт разные результаты;
- появляются новые строки между чтениями.

Изоляция управляет тем, насколько транзакции видят друг друга.$m3_l10_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l10_b2_type$theory$m3_l10_b2_type$, $m3_l10_b2_title$Dirty read$m3_l10_b2_title$, $m3_l10_b2_content$Dirty read — чтение данных, которые другая транзакция ещё не сохранила через `COMMIT`.

Если другая транзакция сделает `ROLLBACK`, ты прочитал данные, которых как будто не было.$m3_l10_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l10_b3_type$theory$m3_l10_b3_type$, $m3_l10_b3_title$Non-repeatable$m3_l10_b3_title$, $m3_l10_b3_content$Non-repeatable read: ты дважды читаешь одну строку в транзакции, но между чтениями другая транзакция изменила её.$m3_l10_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l10_b4_type$theory$m3_l10_b4_type$, $m3_l10_b4_title$Phantom$m3_l10_b4_title$, $m3_l10_b4_content$Phantom read: ты дважды читаешь набор строк по условию, и во второй раз появляются новые строки.$m3_l10_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l10_b5_type$quiz$m3_l10_b5_type$, $m3_l10_b5_title$Levels$m3_l10_b5_title$, $m3_l10_b5_content$1. Какой уровень чаще используется по умолчанию во многих БД? Ответ: Read Committed.
2. Что сильнее: Read Committed или Serializable? Ответ: Serializable.
3. Чем выше изоляция, тем обычно ниже параллельность? Ответ: да.$m3_l10_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l10_b6_type$theory$m3_l10_b6_type$, $m3_l10_b6_title$Locks$m3_l10_b6_title$, $m3_l10_b6_content$Блокировка не даёт другим транзакциям одновременно менять данные опасным образом.

Пример идеи:

```sql
SELECT *
FROM accounts
WHERE id = 1
FOR UPDATE;
```

Так строка блокируется для обновления до конца транзакции.$m3_l10_b6_content$, NULL, NULL::jsonb),
  (7, $m3_l10_b7_type$project$m3_l10_b7_type$, $m3_l10_b7_title$Case$m3_l10_b7_title$, $m3_l10_b7_content$### Ученик видит

Коротко: объясни риск.

**Задание**

Два пользователя одновременно покупают последний товар на складе. В таблице `products.stock = 1`. Оба процесса читают `stock = 1` и оба создают заказ. Что может пойти не так? Как защититься?

---$m3_l10_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 11: Indexes
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 11
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 11
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l11_b1_type$theory$m3_l11_b1_type$, $m3_l11_b1_title$Зачем индекс$m3_l11_b1_title$, $m3_l11_b1_content$Индекс похож на оглавление в книге. Без индекса БД может просматривать много строк. С индексом она быстрее находит нужные.

Пример:

```sql
SELECT *
FROM users
WHERE email = 'a@mail.com';
```

Для частого поиска по `email` полезен индекс.$m3_l11_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l11_b2_type$practice$m3_l11_b2_type$, $m3_l11_b2_title$CREATE INDEX$m3_l11_b2_title$, $m3_l11_b2_content$**Коротко:** создай индекс.

### Условие

Создай индекс `idx_users_city` на колонку `city` таблицы `users`.$m3_l11_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l11_b3_type$theory$m3_l11_b3_type$, $m3_l11_b3_title$B-tree$m3_l11_b3_title$, $m3_l11_b3_content$B-tree индекс хорошо подходит для:

- `=`;
- диапазонов `>`, `<`, `BETWEEN`;
- сортировки;
- поиска по префиксу в некоторых случаях.

Hash-индекс обычно про точное равенство. В прикладной разработке чаще начинай с B-tree.$m3_l11_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l11_b4_type$theory$m3_l11_b4_type$, $m3_l11_b4_title$Минусы$m3_l11_b4_title$, $m3_l11_b4_content$Индекс ускоряет чтение, но замедляет запись.

Почему: при `INSERT`, `UPDATE`, `DELETE` нужно обновить не только таблицу, но и индекс.

Индексы также занимают место на диске.$m3_l11_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l11_b5_type$theory$m3_l11_b5_type$, $m3_l11_b5_title$Explain$m3_l11_b5_title$, $m3_l11_b5_content$`EXPLAIN` показывает, как БД планирует выполнить запрос.

```sql
EXPLAIN
SELECT *
FROM users
WHERE city = 'Москва';
```

На курсе важно не стать DBA, а понять: план запроса помогает искать медленные места.$m3_l11_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l11_b6_type$project$m3_l11_b6_type$, $m3_l11_b6_title$Выбор$m3_l11_b6_title$, $m3_l11_b6_content$### Ученик видит

Коротко: выбери индекс.

**Задание**

Есть запросы:

```sql
SELECT * FROM orders WHERE user_id = ?;
SELECT * FROM orders WHERE status = ? AND created_at >= ?;
```

Какие индексы ты предложишь и почему?

---$m3_l11_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 12: sqlite3
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 12
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 12
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m3_l12_t2_title$create$m3_l12_t2_title$, $m3_l12_t2_statement$**Коротко:** создай таблицу из Python.

### Условие

Создай SQLite-базу в памяти и таблицу `users(id, name)`. Выведи `OK`.

### Выход

```text
OK
```$m3_l12_t2_statement$, $m3_l12_t2_starter$$m3_l12_t2_starter$, $m3_l12_t2_solution$import sqlite3

connection = sqlite3.connect(":memory:")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
""")

print("OK")
$m3_l12_t2_solution$, 2, 50, $m3_l12_t2_topic$Месяц 3. SQL и сети — sqlite3$m3_l12_t2_topic$, $m3_l12_t2_lang$python$m3_l12_t2_lang$, $m3_l12_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m3_l12_t2_policy$::jsonb),
  ($m3_l12_t5_title$select$m3_l12_t5_title$, $m3_l12_t5_statement$**Коротко:** прочитай пользователя.

### Условие

Создай таблицу, добавь `Анна`, затем выбери имя из БД и выведи его.

### Выход

```text
Анна
```$m3_l12_t5_statement$, $m3_l12_t5_starter$$m3_l12_t5_starter$, $m3_l12_t5_solution$import sqlite3

connection = sqlite3.connect(":memory:")
cursor = connection.cursor()

cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
cursor.execute("INSERT INTO users (name) VALUES (?)", ("Анна",))
connection.commit()

cursor.execute("SELECT name FROM users WHERE id = ?", (1,))
row = cursor.fetchone()
print(row[0])
$m3_l12_t5_solution$, 2, 50, $m3_l12_t5_topic$Месяц 3. SQL и сети — sqlite3$m3_l12_t5_topic$, $m3_l12_t5_lang$python$m3_l12_t5_lang$, $m3_l12_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m3_l12_t5_policy$::jsonb),
  ($m3_l12_t6_title$transaction$m3_l12_t6_title$, $m3_l12_t6_statement$**Коротко:** используй транзакцию.

### Условие

Создай таблицу `accounts(id, balance)`. Добавь два счёта: `1 = 100`, `2 = 0`. Сделай перевод `50` со счёта 1 на счёт 2 в транзакции. Выведи балансы.

### Выход

```text
50
50
```$m3_l12_t6_statement$, $m3_l12_t6_starter$$m3_l12_t6_starter$, $m3_l12_t6_solution$import sqlite3

connection = sqlite3.connect(":memory:")
cursor = connection.cursor()

cursor.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER NOT NULL)")
cursor.execute("INSERT INTO accounts VALUES (1, 100)")
cursor.execute("INSERT INTO accounts VALUES (2, 0)")

try:
    cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (50, 1))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (50, 2))
    connection.commit()
except Exception:
    connection.rollback()
    raise

cursor.execute("SELECT balance FROM accounts ORDER BY id")
for row in cursor.fetchall():
    print(row[0])
$m3_l12_t6_solution$, 2, 50, $m3_l12_t6_topic$Месяц 3. SQL и сети — sqlite3$m3_l12_t6_topic$, $m3_l12_t6_lang$python$m3_l12_t6_lang$, $m3_l12_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m3_l12_t6_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 12
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m3_l12_ttitle_2$create$m3_l12_ttitle_2$,
    $m3_l12_ttitle_5$select$m3_l12_ttitle_5$,
    $m3_l12_ttitle_6$transaction$m3_l12_ttitle_6$
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
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 12
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m3_l12_test_2_1_title$create$m3_l12_test_2_1_title$, $m3_l12_test_2_1_input$$m3_l12_test_2_1_input$, $m3_l12_test_2_1_expected$OK$m3_l12_test_2_1_expected$, FALSE, 1),
  ($m3_l12_test_5_1_title$select$m3_l12_test_5_1_title$, $m3_l12_test_5_1_input$$m3_l12_test_5_1_input$, $m3_l12_test_5_1_expected$Анна$m3_l12_test_5_1_expected$, FALSE, 1),
  ($m3_l12_test_6_1_title$transaction$m3_l12_test_6_1_title$, $m3_l12_test_6_1_input$$m3_l12_test_6_1_input$, $m3_l12_test_6_1_expected$50
50$m3_l12_test_6_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 12
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l12_b1_type$theory$m3_l12_b1_type$, $m3_l12_b1_title$connect$m3_l12_b1_title$, $m3_l12_b1_content$Модуль `sqlite3` встроен в Python. Он позволяет работать с SQLite-базой.

```python
import sqlite3

connection = sqlite3.connect("app.db")
cursor = connection.cursor()
```

`connection` — соединение с БД. `cursor` выполняет SQL-запросы.$m3_l12_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l12_b2_type$practice$m3_l12_b2_type$, $m3_l12_b2_title$create$m3_l12_b2_title$, $m3_l12_b2_content$**Коротко:** создай таблицу из Python.

### Условие

Создай SQLite-базу в памяти и таблицу `users(id, name)`. Выведи `OK`.

### Выход

```text
OK
```$m3_l12_b2_content$, $m3_l12_b2_task_title$create$m3_l12_b2_task_title$, NULL::jsonb),
  (3, $m3_l12_b3_type$practice$m3_l12_b3_type$, $m3_l12_b3_title$insert$m3_l12_b3_title$, $m3_l12_b3_content$**Коротко:** добавь пользователя.

### Условие

Создай таблицу `users(id, name)`, добавь пользователя `Анна`, сохрани изменения и выведи `OK`.$m3_l12_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l12_b4_type$theory$m3_l12_b4_type$, $m3_l12_b4_title$params$m3_l12_b4_title$, $m3_l12_b4_content$Нельзя подставлять пользовательские данные в SQL через f-string.

Плохо:

```python
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")
```

Правильно:

```python
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
```

Так ты защищаешься от SQL-инъекций.$m3_l12_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l12_b5_type$practice$m3_l12_b5_type$, $m3_l12_b5_title$select$m3_l12_b5_title$, $m3_l12_b5_content$**Коротко:** прочитай пользователя.

### Условие

Создай таблицу, добавь `Анна`, затем выбери имя из БД и выведи его.

### Выход

```text
Анна
```$m3_l12_b5_content$, $m3_l12_b5_task_title$select$m3_l12_b5_task_title$, NULL::jsonb),
  (6, $m3_l12_b6_type$practice$m3_l12_b6_type$, $m3_l12_b6_title$transaction$m3_l12_b6_title$, $m3_l12_b6_content$**Коротко:** используй транзакцию.

### Условие

Создай таблицу `accounts(id, balance)`. Добавь два счёта: `1 = 100`, `2 = 0`. Сделай перевод `50` со счёта 1 на счёт 2 в транзакции. Выведи балансы.

### Выход

```text
50
50
```$m3_l12_b6_content$, $m3_l12_b6_task_title$transaction$m3_l12_b6_task_title$, NULL::jsonb),
  (7, $m3_l12_b7_type$practice$m3_l12_b7_type$, $m3_l12_b7_title$Контроль$m3_l12_b7_title$, $m3_l12_b7_content$**Коротко:** мини-репозиторий задач.

### Условие

Создай таблицу `tasks(id, title, done)`. Добавь две задачи. Обнови первую как выполненную. Выведи все задачи в формате:

```text
1 Task A 1
2 Task B 0
```

---$m3_l12_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 13: SQLAlchemy
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 13
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 13
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m3_l13_t5_title$CRUD$m3_l13_t5_title$, $m3_l13_t5_statement$**Коротко:** добавь и прочитай пользователя.

### Условие

Через SQLAlchemy ORM создай пользователя `Анна`, сохрани, затем прочитай и выведи имя.

### Выход

```text
Анна
```$m3_l13_t5_statement$, $m3_l13_t5_starter$$m3_l13_t5_starter$, $m3_l13_t5_solution$from sqlalchemy import create_engine, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add(User(name="Анна"))
    session.commit()

with Session(engine) as session:
    user = session.scalar(select(User).where(User.name == "Анна"))
    print(user.name)
$m3_l13_t5_solution$, 2, 50, $m3_l13_t5_topic$Месяц 3. SQL и сети — SQLAlchemy$m3_l13_t5_topic$, $m3_l13_t5_lang$python$m3_l13_t5_lang$, $m3_l13_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m3_l13_t5_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 13
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m3_l13_ttitle_5$CRUD$m3_l13_ttitle_5$
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
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 13
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m3_l13_test_5_1_title$CRUD$m3_l13_test_5_1_title$, $m3_l13_test_5_1_input$$m3_l13_test_5_1_input$, $m3_l13_test_5_1_expected$Анна$m3_l13_test_5_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 13
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l13_b1_type$theory$m3_l13_b1_type$, $m3_l13_b1_title$Core/ORM$m3_l13_b1_title$, $m3_l13_b1_content$SQLAlchemy даёт два основных подхода:

- Core — ближе к SQL, работа с таблицами и выражениями;
- ORM — таблицы представлены Python-классами.

В backend-разработке часто используют ORM, но SQL всё равно нужно понимать.$m3_l13_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l13_b2_type$theory$m3_l13_b2_type$, $m3_l13_b2_title$Engine$m3_l13_b2_title$, $m3_l13_b2_content$`engine` — объект, который знает, как подключиться к БД.

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///app.db")
```

Для PostgreSQL строка подключения будет другой.$m3_l13_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l13_b3_type$practice$m3_l13_b3_type$, $m3_l13_b3_title$Model$m3_l13_b3_title$, $m3_l13_b3_content$**Коротко:** создай ORM-модель.

### Условие

Создай модель `User` с колонками:

- `id`;
- `name`.$m3_l13_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l13_b4_type$theory$m3_l13_b4_type$, $m3_l13_b4_title$Session$m3_l13_b4_title$, $m3_l13_b4_content$`Session` — рабочая единица для операций с ORM.

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    session.add(user)
    session.commit()
```

`commit()` сохраняет изменения. Без commit данные могут не попасть в БД.$m3_l13_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l13_b5_type$practice$m3_l13_b5_type$, $m3_l13_b5_title$CRUD$m3_l13_b5_title$, $m3_l13_b5_content$**Коротко:** добавь и прочитай пользователя.

### Условие

Через SQLAlchemy ORM создай пользователя `Анна`, сохрани, затем прочитай и выведи имя.

### Выход

```text
Анна
```$m3_l13_b5_content$, $m3_l13_b5_task_title$CRUD$m3_l13_b5_task_title$, NULL::jsonb),
  (6, $m3_l13_b6_type$theory$m3_l13_b6_type$, $m3_l13_b6_title$Relationships$m3_l13_b6_title$, $m3_l13_b6_content$Связи ORM связывают классы так же, как foreign key связывает таблицы.

```python
class Order(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship()
```

Важно понимать: ORM не отменяет SQL. Она генерирует SQL за тебя.$m3_l13_b6_content$, NULL, NULL::jsonb),
  (7, $m3_l13_b7_type$project$m3_l13_b7_type$, $m3_l13_b7_title$Контроль$m3_l13_b7_title$, $m3_l13_b7_content$### Ученик видит

Коротко: спроектируй ORM-модели.

**Задание**

Опиши ORM-модели для задачника:

- `User`;
- `Task`;
- у пользователя много задач.

---$m3_l13_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 14: NoSQL
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 14
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 14
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l14_b1_type$theory$m3_l14_b1_type$, $m3_l14_b1_title$Что такое NoSQL$m3_l14_b1_title$, $m3_l14_b1_content$NoSQL — не одна технология, а группа разных подходов к хранению данных.

Основные типы:

- документоориентированные;
- ключ-значение;
- колоночные;
- поисковые;
- blob/object storage.$m3_l14_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l14_b2_type$theory$m3_l14_b2_type$, $m3_l14_b2_title$Mongo$m3_l14_b2_title$, $m3_l14_b2_content$MongoDB хранит документы, похожие на JSON.

Подходит, когда данные гибкие и не всегда имеют одинаковую структуру.

Риск: если использовать без проектирования, можно получить хаос вместо схемы.$m3_l14_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l14_b3_type$theory$m3_l14_b3_type$, $m3_l14_b3_title$Redis$m3_l14_b3_title$, $m3_l14_b3_content$Redis — хранилище ключ-значение в памяти.

Частые применения:

- кэш;
- сессии;
- rate limiting;
- очереди;
- временные данные.

Кэш нужно инвалидировать: удалять или обновлять, когда исходные данные изменились.$m3_l14_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l14_b4_type$theory$m3_l14_b4_type$, $m3_l14_b4_title$ClickHouse$m3_l14_b4_title$, $m3_l14_b4_content$ClickHouse — колоночная БД для аналитики.

OLTP — много небольших операций: заказы, пользователи, платежи.  
OLAP — аналитика по большим объёмам: отчёты, метрики, события.

PostgreSQL чаще используют для OLTP, ClickHouse — для OLAP.$m3_l14_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l14_b5_type$theory$m3_l14_b5_type$, $m3_l14_b5_title$S3$m3_l14_b5_title$, $m3_l14_b5_content$S3/MinIO — object storage. Там удобно хранить файлы:

- изображения;
- видео;
- выгрузки;
- архивы;
- большие документы.

В БД обычно хранят ссылку на файл, а не сам большой файл.$m3_l14_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l14_b6_type$quiz$m3_l14_b6_type$, $m3_l14_b6_title$Выбор$m3_l14_b6_title$, $m3_l14_b6_content$1. Кэш с TTL — Redis.
2. Аналитика событий — ClickHouse.
3. Изображения пользователей — S3/MinIO.
4. Основные заказы магазина — PostgreSQL.
5. Гибкие документы — MongoDB, если это оправдано.

---$m3_l14_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 15: Сети
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 15
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 15
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l15_b1_type$theory$m3_l15_b1_type$, $m3_l15_b1_title$Client/server$m3_l15_b1_title$, $m3_l15_b1_content$Клиент отправляет запрос. Сервер возвращает ответ.

```text
браузер/API-клиент → HTTP-запрос → сервер → HTTP-ответ
```

Backend-разработчик пишет серверную часть: принимает запросы, проверяет данные, работает с БД и возвращает ответ.$m3_l15_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l15_b2_type$theory$m3_l15_b2_type$, $m3_l15_b2_title$DNS$m3_l15_b2_title$, $m3_l15_b2_content$DNS превращает доменное имя в IP-адрес.

```text
example.com → 93.184.216.34
```

Без DNS пользователям пришлось бы помнить IP-адреса.$m3_l15_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l15_b3_type$theory$m3_l15_b3_type$, $m3_l15_b3_title$TCP/UDP$m3_l15_b3_title$, $m3_l15_b3_content$TCP — надёжнее: устанавливает соединение, следит за доставкой и порядком данных.

UDP — проще и быстрее, но без гарантий доставки.

Примеры:

```text
HTTP/HTTPS обычно поверх TCP
DNS часто использует UDP
стриминг/игры могут использовать UDP
```$m3_l15_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l15_b4_type$theory$m3_l15_b4_type$, $m3_l15_b4_title$HTTP$m3_l15_b4_title$, $m3_l15_b4_content$HTTP-запрос состоит из:

- метода: `GET`, `POST`, `PUT`, `DELETE`;
- адреса;
- заголовков;
- тела, если оно нужно.

HTTP-ответ содержит:

- статус-код;
- заголовки;
- тело ответа.$m3_l15_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l15_b5_type$theory$m3_l15_b5_type$, $m3_l15_b5_title$HTTPS$m3_l15_b5_title$, $m3_l15_b5_content$HTTPS — это HTTP поверх защищённого соединения TLS.

Он нужен, чтобы:

- шифровать данные;
- защищать логины, токены и пароли;
- подтверждать, что пользователь общается с нужным сервером.$m3_l15_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l15_b6_type$quiz$m3_l15_b6_type$, $m3_l15_b6_title$Проверка$m3_l15_b6_title$, $m3_l15_b6_content$1. Что делает DNS? Ответ: преобразует домен в IP.
2. Что надёжнее для HTTP: TCP или UDP? Ответ: TCP.
3. Что добавляет HTTPS? Ответ: шифрование и проверку подлинности сервера.
4. Что пишет backend-разработчик? Ответ: серверную логику.

---$m3_l15_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 16: REST
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 16
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 16
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l16_b1_type$theory$m3_l16_b1_type$, $m3_l16_b1_title$Resource$m3_l16_b1_title$, $m3_l16_b1_content$REST обычно строится вокруг ресурсов.

```text
/users
/users/1
/tasks
/tasks/10
```

Ресурс — объект предметной области: пользователь, задача, заказ, товар.$m3_l16_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l16_b2_type$theory$m3_l16_b2_type$, $m3_l16_b2_title$Methods$m3_l16_b2_title$, $m3_l16_b2_content$Методы HTTP:

```text
GET     получить
POST    создать
PUT     заменить полностью
PATCH   изменить частично
DELETE  удалить
```

Пример:

```text
GET /tasks        список задач
POST /tasks       создать задачу
GET /tasks/1      получить задачу
PATCH /tasks/1    изменить задачу
DELETE /tasks/1   удалить задачу
```$m3_l16_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l16_b3_type$theory$m3_l16_b3_type$, $m3_l16_b3_title$Status$m3_l16_b3_title$, $m3_l16_b3_content$Статус-коды:

```text
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
500 Internal Server Error
```

Код должен помогать клиенту понять, что произошло.$m3_l16_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l16_b4_type$theory$m3_l16_b4_type$, $m3_l16_b4_title$Idempotent$m3_l16_b4_title$, $m3_l16_b4_content$Идемпотентность: повторный одинаковый запрос даёт тот же эффект.

Обычно идемпотентны:

```text
GET
PUT
DELETE
```

Обычно не идемпотентен:

```text
POST
```

Если два раза отправить `POST /orders`, можно создать два заказа.$m3_l16_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l16_b5_type$theory$m3_l16_b5_type$, $m3_l16_b5_title$JSON/XML$m3_l16_b5_title$, $m3_l16_b5_content$JSON — основной формат обмена данными в современных API.

```json
{
  "id": 1,
  "title": "Task",
  "done": false
}
```

XML встречается в старых системах и некоторых интеграциях.$m3_l16_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l16_b6_type$practice$m3_l16_b6_type$, $m3_l16_b6_title$Contract$m3_l16_b6_title$, $m3_l16_b6_content$**Коротко:** спроектируй API задач.

### Условие

Опиши API для задач:

- создать задачу;
- получить список;
- отметить выполненной;
- удалить.

Для каждого endpoint укажи метод, путь, тело запроса и статус ответа.

---$m3_l16_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 17: Протоколы
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 17
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 17
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l17_b1_type$theory$m3_l17_b1_type$, $m3_l17_b1_title$SOAP$m3_l17_b1_title$, $m3_l17_b1_content$SOAP — старый строгий протокол на XML. Его можно встретить в enterprise-системах, банках, государственных интеграциях.

Не нужно начинать с SOAP, но нужно знать, что он существует.$m3_l17_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l17_b2_type$theory$m3_l17_b2_type$, $m3_l17_b2_title$GraphQL$m3_l17_b2_title$, $m3_l17_b2_content$GraphQL позволяет клиенту запросить ровно те поля, которые нужны.

Пример идеи:

```graphql
query {
  user(id: 1) {
    name
    orders {
      id
    }
  }
}
```

Это удобно для сложных фронтендов, но добавляет сложность на backend.$m3_l17_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l17_b3_type$theory$m3_l17_b3_type$, $m3_l17_b3_title$gRPC$m3_l17_b3_title$, $m3_l17_b3_content$gRPC часто используют для общения сервисов между собой. Он основан на строгих контрактах и Protocol Buffers.

Для новичка важна идея: REST — не единственный способ строить API.$m3_l17_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l17_b4_type$theory$m3_l17_b4_type$, $m3_l17_b4_title$WebSocket$m3_l17_b4_title$, $m3_l17_b4_content$WebSocket держит постоянное соединение между клиентом и сервером.

Подходит для:

- чатов;
- уведомлений;
- онлайн-игр;
- real-time dashboards.$m3_l17_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l17_b5_type$quiz$m3_l17_b5_type$, $m3_l17_b5_title$Когда что$m3_l17_b5_title$, $m3_l17_b5_content$1. Чат в реальном времени — WebSocket.
2. Простое публичное API — REST.
3. Сложный frontend хочет выбирать поля — GraphQL.
4. Внутреннее общение микросервисов с контрактом — gRPC.
5. Старые enterprise-интеграции — SOAP.

---$m3_l17_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 3, lesson 18: Проект DB
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 18
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 3 AND l.position = 18
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m3_l18_b1_type$theory$m3_l18_b1_type$, $m3_l18_b1_title$ТЗ$m3_l18_b1_title$, $m3_l18_b1_content$Нужно сделать проект: БД учебного сервиса.

Минимальные сущности:

```text
users
courses
lessons
enrollments
submissions
```

Нужно:

1. создать схему;
2. наполнить данными через Python-скрипт;
3. написать 10 SQL-запросов;
4. объяснить индексы;
5. оформить README.$m3_l18_b1_content$, NULL, NULL::jsonb),
  (2, $m3_l18_b2_type$practice$m3_l18_b2_type$, $m3_l18_b2_title$Schema$m3_l18_b2_title$, $m3_l18_b2_content$### Условие

Создай SQL-файл `schema.sql`.

В нём должны быть таблицы и связи:

- пользователь записывается на много курсов;
- курс содержит много уроков;
- пользователь отправляет решения.$m3_l18_b2_content$, NULL, NULL::jsonb),
  (3, $m3_l18_b3_type$practice$m3_l18_b3_type$, $m3_l18_b3_title$Seed$m3_l18_b3_title$, $m3_l18_b3_content$### Условие

Создай Python-скрипт `seed.py`, который добавляет тестовые данные:

- 5 пользователей;
- 3 курса;
- 10 уроков;
- минимум 10 отправок решений.$m3_l18_b3_content$, NULL, NULL::jsonb),
  (4, $m3_l18_b4_type$practice$m3_l18_b4_type$, $m3_l18_b4_title$Queries$m3_l18_b4_title$, $m3_l18_b4_content$### Условие

Напиши файл `queries.sql` с запросами:

1. все активные пользователи;
2. курсы пользователя;
3. количество уроков в курсе;
4. средний балл по курсу;
5. топ-3 ученика;
6. ученики без отправок;
7. последний сабмит каждого ученика;
8. количество сабмитов по дням;
9. курс с максимальным числом записей;
10. пользователи, которые прошли больше 70% уроков.$m3_l18_b4_content$, NULL, NULL::jsonb),
  (5, $m3_l18_b5_type$practice$m3_l18_b5_type$, $m3_l18_b5_title$Python$m3_l18_b5_title$, $m3_l18_b5_content$### Условие

Напиши Python-скрипт `report.py`, который подключается к БД, выполняет 3 запроса и выводит отчёт в консоль.

Обязательно используй параметризованные запросы.$m3_l18_b5_content$, NULL, NULL::jsonb),
  (6, $m3_l18_b6_type$practice$m3_l18_b6_type$, $m3_l18_b6_title$Report$m3_l18_b6_title$, $m3_l18_b6_content$### Условие

README должен содержать:

- описание схемы;
- как создать БД;
- как наполнить БД;
- примеры запросов;
- какие индексы добавлены и почему;
- что можно улучшить.$m3_l18_b6_content$, NULL, NULL::jsonb),
  (7, $m3_l18_b7_type$project$m3_l18_b7_type$, $m3_l18_b7_title$Защита$m3_l18_b7_title$, $m3_l18_b7_content$Отправь проект на проверку.

---

# Экзамен месяца 3

**В интерфейсе:** Экзамен 3

## Формат

1. 8 SQL-задач с автопроверкой.
2. 2 задачи SQL+Python.
3. 10 вопросов по сетям и REST.
4. Проект DB.

## Обязательные навыки

- `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`;
- `JOIN`;
- `GROUP BY`, `HAVING`;
- подзапросы и CTE;
- `INSERT`, `UPDATE`, безопасный `DELETE`;
- транзакции и ACID;
- индексы и их цена;
- параметризованные SQL-запросы из Python;
- базовый REST-контракт.

## Маршрут восстановления

- Ошибки в SELECT/WHERE → уроки 2–3.
- Ошибки в JOIN/GROUP BY → уроки 4–5.
- Ошибки в CTE/сложных запросах → урок 6.
- Ошибки в транзакциях/индексах → уроки 9–11.
- Ошибки в Python+SQL → уроки 12–13.
- Ошибки в сетях/REST → уроки 15–17.
# Месяц 4. FastAPI, SQLAlchemy, тестирование и DevOps

Цель месяца: ученик создаёт backend API, подключает БД, пишет тесты, контейнеризует приложение и настраивает базовый CI/CD.

## Сетка месяца

| Урок | Название | Фокус | Проверка |
|---:|---|---|---|
| 1 | Poetry | зависимости, pyproject, venv | чеклист |
| 2 | FastAPI start | приложение, route, docs | HTTP-runner |
| 3 | Request data | path, query, body | HTTP-runner |
| 4 | Pydantic | схемы, валидация, response model | HTTP-runner |
| 5 | CRUD memory | CRUD без БД | HTTP-runner |
| 6 | Layers | router, service, repository | AI-check |
| 7 | SQLAlchemy API | engine, session, ORM | HTTP + Python |
| 8 | Alembic | миграции | чеклист |
| 9 | Auth | password hash, JWT, Depends | HTTP-runner + AI |
| 10 | Depends | зависимости и ресурсы | HTTP-runner |
| 11 | PyTest | unit/API tests | pytest-runner |
| 12 | Postman | ручное API-тестирование | чеклист |
| 13 | Dockerfile | image, container | docker-runner |
| 14 | Compose | app + db + healthcheck | docker-compose |
| 15 | Logs/config | env, logs, settings | AI-check |
| 16 | CI/CD | GitHub Actions/GitLab CI | YAML-check |
| 17 | Mini CRUD | проект месяца | AI-check |

---$m3_l18_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4: Месяц 4. FastAPI и DevOps
WITH module_ref AS (
  SELECT m.id AS module_id
  FROM modules m
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4
), lesson_seed(position, title, content_md) AS (
  VALUES
  (1, $m4_l1_title$Poetry$m4_l1_title$, $m4_l1_content$Управляем зависимостями проекта.$m4_l1_content$),
  (2, $m4_l2_title$FastAPI start$m4_l2_title$, $m4_l2_content$Создаём первый API.$m4_l2_content$),
  (3, $m4_l3_title$Request data$m4_l3_title$, $m4_l3_content$Получаем path, query и body.$m4_l3_content$),
  (4, $m4_l4_title$Pydantic$m4_l4_title$, $m4_l4_content$Валидируем вход и управляем ответом.$m4_l4_content$),
  (5, $m4_l5_title$CRUD memory$m4_l5_title$, $m4_l5_content$CRUD без базы данных.$m4_l5_content$),
  (6, $m4_l6_title$Layers$m4_l6_title$, $m4_l6_content$Разделяем API, логику и данные.$m4_l6_content$),
  (7, $m4_l7_title$SQLAlchemy API$m4_l7_title$, $m4_l7_content$Подключаем API к базе.$m4_l7_content$),
  (8, $m4_l8_title$Alembic$m4_l8_title$, $m4_l8_content$Миграции управляют изменениями схемы.$m4_l8_content$),
  (9, $m4_l9_title$Auth$m4_l9_title$, $m4_l9_content$Регистрация, логин и JWT.$m4_l9_content$),
  (10, $m4_l10_title$Depends$m4_l10_title$, $m4_l10_content$Переиспользуем зависимости.$m4_l10_content$),
  (11, $m4_l11_title$PyTest$m4_l11_title$, $m4_l11_content$Проверяем код автоматически.$m4_l11_content$),
  (12, $m4_l12_title$Postman$m4_l12_title$, $m4_l12_content$Проверяем API руками.$m4_l12_content$),
  (13, $m4_l13_title$Dockerfile$m4_l13_title$, $m4_l13_content$Упаковываем приложение в контейнер.$m4_l13_content$),
  (14, $m4_l14_title$Compose$m4_l14_title$, $m4_l14_content$Запускаем API и БД вместе.$m4_l14_content$),
  (15, $m4_l15_title$Logs/config$m4_l15_title$, $m4_l15_content$Настройки, env и логи.$m4_l15_content$),
  (16, $m4_l16_title$CI/CD$m4_l16_title$, $m4_l16_content$Автоматически проверяем проект.$m4_l16_content$),
  (17, $m4_l17_title$Mini CRUD$m4_l17_title$, $m4_l17_content$Проект месяца: CRUD-сервис.$m4_l17_content$)
)
INSERT INTO lessons(module_id, title, content_md, position, is_published)
SELECT mr.module_id, ls.title, ls.content_md, ls.position, TRUE
FROM module_ref mr
CROSS JOIN lesson_seed ls
ON CONFLICT (module_id, position) DO UPDATE
SET title = EXCLUDED.title,
    content_md = EXCLUDED.content_md,
    is_published = TRUE,
    updated_at = NOW();

-- Module 4, lesson 1: Poetry
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 1
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 1
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l1_b1_type$theory$m4_l1_b1_type$, $m4_l1_b1_title$Зачем venv$m4_l1_b1_title$, $m4_l1_b1_content$Виртуальное окружение изолирует зависимости проекта. Без него разные проекты могут конфликтовать версиями библиотек.

```text
project-a → fastapi одной версии
project-b → fastapi другой версии
```

Окружение позволяет каждому проекту жить отдельно.$m4_l1_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l1_b2_type$theory$m4_l1_b2_type$, $m4_l1_b2_title$pyproject$m4_l1_b2_title$, $m4_l1_b2_content$`pyproject.toml` описывает проект и зависимости.

Пример:

```toml
[tool.poetry]
name = "task-api"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "*"
uvicorn = "*"
```$m4_l1_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l1_b3_type$practice$m4_l1_b3_type$, $m4_l1_b3_title$poetry add$m4_l1_b3_title$, $m4_l1_b3_content$**Коротко:** добавь зависимости.

### Условие

Добавь зависимости:

```bash
poetry add fastapi uvicorn sqlalchemy pydantic-settings
poetry add --group dev pytest httpx ruff
```$m4_l1_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l1_b4_type$practice$m4_l1_b4_type$, $m4_l1_b4_title$scripts$m4_l1_b4_title$, $m4_l1_b4_content$**Коротко:** добавь команду запуска.

### Условие

Добавь в README команду:

```bash
poetry run uvicorn app.main:app --reload
```

Объясни, что означает:

- `app.main`;
- `app`;
- `--reload`.$m4_l1_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l1_b5_type$summary$m4_l1_b5_type$, $m4_l1_b5_title$Контроль$m4_l1_b5_title$, $m4_l1_b5_content$Проект готов, если:

- есть `pyproject.toml`;
- зависимости установлены;
- есть папка `app`;
- есть `README.md`;
- команда запуска записана.

---$m4_l1_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 2: FastAPI start
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 2
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 2
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m4_l2_t5_title$health$m4_l2_t5_title$, $m4_l2_t5_statement$**Коротко:** добавь healthcheck.

### Условие

Добавь endpoint:

```text
GET /health
```

Он должен вернуть:

```json
{"status": "ok"}
```

---$m4_l2_t5_statement$, $m4_l2_t5_starter$$m4_l2_t5_starter$, $m4_l2_t5_solution$$m4_l2_t5_solution$, 2, 50, $m4_l2_t5_topic$Месяц 4. FastAPI и DevOps — FastAPI start$m4_l2_t5_topic$, $m4_l2_t5_lang$python$m4_l2_t5_lang$, $m4_l2_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m4_l2_t5_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 2
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m4_l2_ttitle_5$health$m4_l2_ttitle_5$
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 2
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m4_l2_test_5_1_title$health$m4_l2_test_5_1_title$, $m4_l2_test_5_1_input$$m4_l2_test_5_1_input$, $m4_l2_test_5_1_expected$GET /health$m4_l2_test_5_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 2
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l2_b1_type$theory$m4_l2_b1_type$, $m4_l2_b1_title$Что такое API$m4_l2_b1_title$, $m4_l2_b1_content$API — способ программам общаться друг с другом.

FastAPI-приложение принимает HTTP-запрос и возвращает HTTP-ответ.

```text
GET /tasks → список задач
POST /tasks → создать задачу
```$m4_l2_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l2_b2_type$practice$m4_l2_b2_type$, $m4_l2_b2_title$app$m4_l2_b2_title$, $m4_l2_b2_content$**Коротко:** создай приложение.$m4_l2_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l2_b3_type$practice$m4_l2_b3_type$, $m4_l2_b3_title$GET /$m4_l2_b3_title$, $m4_l2_b3_content$**Коротко:** добавь первый endpoint.

### Условие

Добавь обработчик `GET /`, который возвращает:

```json
{"message": "Hello API"}
```$m4_l2_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l2_b4_type$theory$m4_l2_b4_type$, $m4_l2_b4_title$docs$m4_l2_b4_title$, $m4_l2_b4_content$FastAPI автоматически создаёт документацию:

```text
/docs
/redoc
```

Через `/docs` можно вручную отправлять запросы и смотреть ответы.$m4_l2_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l2_b5_type$practice$m4_l2_b5_type$, $m4_l2_b5_title$health$m4_l2_b5_title$, $m4_l2_b5_content$**Коротко:** добавь healthcheck.

### Условие

Добавь endpoint:

```text
GET /health
```

Он должен вернуть:

```json
{"status": "ok"}
```

---$m4_l2_b5_content$, $m4_l2_b5_task_title$health$m4_l2_b5_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 3: Request data
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 3
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 3
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m4_l3_t2_title$GET item$m4_l3_t2_title$, $m4_l3_t2_statement$**Коротко:** получи id задачи.

### Условие

Добавь endpoint:

```text
GET /tasks/{task_id}
```

Он должен вернуть:

```json
{"task_id": 5}
```

если запрос `/tasks/5`.$m4_l3_t2_statement$, $m4_l3_t2_starter$$m4_l3_t2_starter$, $m4_l3_t2_solution$$m4_l3_t2_solution$, 2, 50, $m4_l3_t2_topic$Месяц 4. FastAPI и DevOps — Request data$m4_l3_t2_topic$, $m4_l3_t2_lang$python$m4_l3_t2_lang$, $m4_l3_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m4_l3_t2_policy$::jsonb),
  ($m4_l3_t4_title$Search$m4_l3_t4_title$, $m4_l3_t4_statement$**Коротко:** верни query-параметры.

### Условие

Endpoint `GET /search` принимает `q` и `limit`. Верни их в JSON.

Пример:

```text
/search?q=python&limit=3
```

Ответ:

```json
{"q": "python", "limit": 3}
```$m4_l3_t4_statement$, $m4_l3_t4_starter$$m4_l3_t4_starter$, $m4_l3_t4_solution$$m4_l3_t4_solution$, 2, 50, $m4_l3_t4_topic$Месяц 4. FastAPI и DevOps — Request data$m4_l3_t4_topic$, $m4_l3_t4_lang$python$m4_l3_t4_lang$, $m4_l3_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m4_l3_t4_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 3
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m4_l3_ttitle_2$GET item$m4_l3_ttitle_2$,
    $m4_l3_ttitle_4$Search$m4_l3_ttitle_4$
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 3
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m4_l3_test_2_1_title$GET item$m4_l3_test_2_1_title$, $m4_l3_test_2_1_input$$m4_l3_test_2_1_input$, $m4_l3_test_2_1_expected$GET /tasks/{task_id}$m4_l3_test_2_1_expected$, FALSE, 1),
  ($m4_l3_test_4_1_title$Search$m4_l3_test_4_1_title$, $m4_l3_test_4_1_input$$m4_l3_test_4_1_input$, $m4_l3_test_4_1_expected$/search?q=python&limit=3$m4_l3_test_4_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 3
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l3_b1_type$theory$m4_l3_b1_type$, $m4_l3_b1_title$Path$m4_l3_b1_title$, $m4_l3_b1_content$Path-параметр — часть адреса.

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

FastAPI преобразует `user_id` в `int`, если тип указан.$m4_l3_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l3_b2_type$practice$m4_l3_b2_type$, $m4_l3_b2_title$GET item$m4_l3_b2_title$, $m4_l3_b2_content$**Коротко:** получи id задачи.

### Условие

Добавь endpoint:

```text
GET /tasks/{task_id}
```

Он должен вернуть:

```json
{"task_id": 5}
```

если запрос `/tasks/5`.$m4_l3_b2_content$, $m4_l3_b2_task_title$GET item$m4_l3_b2_task_title$, NULL::jsonb),
  (3, $m4_l3_b3_type$theory$m4_l3_b3_type$, $m4_l3_b3_title$Query$m4_l3_b3_title$, $m4_l3_b3_content$Query-параметры идут после `?`.

```text
/tasks?done=true&limit=10
```

В FastAPI:

```python
@app.get("/tasks")
def list_tasks(done: bool | None = None, limit: int = 10):
    ...
```$m4_l3_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l3_b4_type$practice$m4_l3_b4_type$, $m4_l3_b4_title$Search$m4_l3_b4_title$, $m4_l3_b4_content$**Коротко:** верни query-параметры.

### Условие

Endpoint `GET /search` принимает `q` и `limit`. Верни их в JSON.

Пример:

```text
/search?q=python&limit=3
```

Ответ:

```json
{"q": "python", "limit": 3}
```$m4_l3_b4_content$, $m4_l3_b4_task_title$Search$m4_l3_b4_task_title$, NULL::jsonb),
  (5, $m4_l3_b5_type$theory$m4_l3_b5_type$, $m4_l3_b5_title$Body$m4_l3_b5_title$, $m4_l3_b5_content$Тело запроса обычно используется в `POST`, `PUT`, `PATCH`.

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str

@app.post("/tasks")
def create_task(data: TaskCreate):
    return data
```$m4_l3_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l3_b6_type$practice$m4_l3_b6_type$, $m4_l3_b6_title$Create$m4_l3_b6_title$, $m4_l3_b6_content$**Коротко:** создай задачу.

### Условие

Создай endpoint `POST /tasks`. Он принимает JSON:

```json
{"title": "Учить FastAPI"}
```

и возвращает:

```json
{"id": 1, "title": "Учить FastAPI", "done": false}
```

---$m4_l3_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 4: Pydantic
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 4
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 4
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l4_b1_type$theory$m4_l4_b1_type$, $m4_l4_b1_title$BaseModel$m4_l4_b1_title$, $m4_l4_b1_content$Pydantic-модель описывает форму данных.

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    priority: int = 1
```

FastAPI автоматически проверит входные данные.$m4_l4_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l4_b2_type$practice$m4_l4_b2_type$, $m4_l4_b2_title$Validate$m4_l4_b2_title$, $m4_l4_b2_content$**Коротко:** создай модель задачи.

### Условие

Создай модель `TaskCreate` с полями `title: str` и `priority: int = 1`. Endpoint `POST /tasks` должен вернуть полученные данные.$m4_l4_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l4_b3_type$theory$m4_l4_b3_type$, $m4_l4_b3_title$Response$m4_l4_b3_title$, $m4_l4_b3_content$Отдельные модели для входа и выхода помогают не отдавать лишние данные.

```python
class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
```

Пароль не должен попадать в ответ.$m4_l4_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l4_b4_type$practice$m4_l4_b4_type$, $m4_l4_b4_title$Models$m4_l4_b4_title$, $m4_l4_b4_content$**Коротко:** раздели input и output.

### Условие

Создай `UserCreate(email, password)` и `UserOut(id, email)`. Endpoint `POST /users` принимает пароль, но возвращает только `id` и `email`.$m4_l4_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l4_b5_type$theory$m4_l4_b5_type$, $m4_l4_b5_title$Ошибка 422$m4_l4_b5_title$, $m4_l4_b5_content$Если тело запроса не соответствует модели, FastAPI вернёт `422 Unprocessable Entity`.

Это нормально: API защищает себя от неправильных данных.$m4_l4_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l4_b6_type$practice$m4_l4_b6_type$, $m4_l4_b6_title$Контроль$m4_l4_b6_title$, $m4_l4_b6_content$**Коротко:** модель товара.

### Условие

Создай endpoint `POST /products`, который принимает:

```json
{"title": "Book", "price": 1000}
```

и возвращает:

```json
{"id": 1, "title": "Book", "price": 1000}
```

`price` должен быть больше 0.

---$m4_l4_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 5: CRUD memory
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 5
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 5
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l5_b1_type$theory$m4_l5_b1_type$, $m4_l5_b1_title$CRUD$m4_l5_b1_title$, $m4_l5_b1_content$CRUD — четыре базовые операции:

```text
Create  создать
Read    прочитать
Update  изменить
Delete  удалить
```

Для задач:

```text
POST /tasks
GET /tasks
GET /tasks/{id}
PATCH /tasks/{id}
DELETE /tasks/{id}
```

## Шаги 2–6. Практика$m4_l5_b1_content$, NULL, NULL::jsonb),
  (7, $m4_l5_b7_type$theory$m4_l5_b7_type$, $m4_l5_b7_title$Контроль$m4_l5_b7_title$, $m4_l5_b7_content$Отправь приложение на автопроверку. Проверка выполнит серию HTTP-запросов к твоему API.

---$m4_l5_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 6: Layers
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 6
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 6
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l6_b1_type$theory$m4_l6_b1_type$, $m4_l6_b1_title$Зачем слои$m4_l6_b1_title$, $m4_l6_b1_content$Если весь код лежит в `main.py`, проект быстро становится нечитаемым.

Рекомендуемая структура:

```text
app/
  main.py
  routers/tasks.py
  schemas/tasks.py
  services/tasks.py
  repositories/tasks.py
```$m4_l6_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l6_b2_type$theory$m4_l6_b2_type$, $m4_l6_b2_title$Router$m4_l6_b2_title$, $m4_l6_b2_content$Router отвечает за HTTP-слой: пути, методы, статусы.

```python
router = APIRouter(prefix="/tasks")
```

Он не должен содержать сложную бизнес-логику.$m4_l6_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l6_b3_type$theory$m4_l6_b3_type$, $m4_l6_b3_title$Service$m4_l6_b3_title$, $m4_l6_b3_content$Service содержит бизнес-логику:

- создать задачу;
- проверить права;
- изменить статус;
- применить правило.$m4_l6_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l6_b4_type$theory$m4_l6_b4_type$, $m4_l6_b4_title$Repository$m4_l6_b4_title$, $m4_l6_b4_content$Repository отвечает за доступ к данным: БД, файл, внешнее API.

Так сервис не зависит от того, где хранятся данные.$m4_l6_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l6_b5_type$project$m4_l6_b5_type$, $m4_l6_b5_title$Refactor$m4_l6_b5_title$, $m4_l6_b5_content$### Ученик видит

Коротко: разнеси CRUD по слоям.

**Задание**

Возьми CRUD из прошлого урока и вынеси код в файлы:

```text
routers/tasks.py
schemas/tasks.py
services/tasks.py
```

---$m4_l6_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 7: SQLAlchemy API
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 7
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 7
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l7_b1_type$theory$m4_l7_b1_type$, $m4_l7_b1_title$DB session$m4_l7_b1_title$, $m4_l7_b1_content$В API нельзя создавать новое глобальное соединение для каждого действия вручную. Обычно используют зависимость, которая выдаёт `Session` на запрос.

```python
def get_session():
    with Session(engine) as session:
        yield session
```$m4_l7_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l7_b2_type$practice$m4_l7_b2_type$, $m4_l7_b2_title$Model$m4_l7_b2_title$, $m4_l7_b2_content$### Условие

Создай ORM-модель `Task`:

- `id`;
- `title`;
- `done`.$m4_l7_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l7_b3_type$theory$m4_l7_b3_type$, $m4_l7_b3_title$Depends db$m4_l7_b3_title$, $m4_l7_b3_content$`Depends` внедряет зависимость в endpoint.

```python
@app.get("/tasks")
def list_tasks(session: Session = Depends(get_session)):
    ...
```

FastAPI сам вызовет `get_session`.$m4_l7_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l7_b4_type$practice$m4_l7_b4_type$, $m4_l7_b4_title$Create DB$m4_l7_b4_title$, $m4_l7_b4_content$**Коротко:** создай задачу в БД.

### Условие

`POST /tasks` должен сохранять задачу в БД и возвращать созданную задачу.$m4_l7_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l7_b5_type$practice$m4_l7_b5_type$, $m4_l7_b5_title$List DB$m4_l7_b5_title$, $m4_l7_b5_content$**Коротко:** прочитай задачи из БД.

### Условие

`GET /tasks` должен возвращать список задач из базы данных.$m4_l7_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l7_b6_type$theory$m4_l7_b6_type$, $m4_l7_b6_title$Контроль$m4_l7_b6_title$, $m4_l7_b6_content$Проверка создаст несколько задач и проверит, что они сохраняются и читаются из БД.

---$m4_l7_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 8: Alembic
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 8
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 8
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l8_b1_type$theory$m4_l8_b1_type$, $m4_l8_b1_title$Зачем миграции$m4_l8_b1_title$, $m4_l8_b1_content$Когда проект растёт, схема БД меняется. Миграции позволяют хранить историю изменений схемы в коде.

Пример изменений:

```text
добавили колонку description
создали индекс
добавили таблицу comments
```

## Шаги 2–4. Практика$m4_l8_b1_content$, NULL, NULL::jsonb),
  (5, $m4_l8_b5_type$theory$m4_l8_b5_type$, $m4_l8_b5_title$rollback$m4_l8_b5_title$, $m4_l8_b5_content$Откат миграции:

```bash
alembic downgrade -1
```

В реальной разработке откат нужно проверять, а не писать формально.$m4_l8_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l8_b6_type$summary$m4_l8_b6_type$, $m4_l8_b6_title$Контроль$m4_l8_b6_title$, $m4_l8_b6_content$Добавь колонку `description` в таблицу задач через миграцию. Примените миграцию и проверь, что приложение запускается.

---$m4_l8_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 9: Auth
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 9
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 9
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l9_b1_type$theory$m4_l9_b1_type$, $m4_l9_b1_title$Auth vs authz$m4_l9_b1_title$, $m4_l9_b1_content$Authentication — кто ты?  
Authorization — что тебе разрешено?

Пример:

```text
логин по email/password → authentication
доступ только к своим задачам → authorization
```$m4_l9_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l9_b2_type$theory$m4_l9_b2_type$, $m4_l9_b2_title$Password hash$m4_l9_b2_title$, $m4_l9_b2_content$Пароли нельзя хранить в открытом виде. Нужно хранить хэш.

```text
password → hash → database
```

При логине мы сравниваем введённый пароль с хэшем.$m4_l9_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l9_b3_type$practice$m4_l9_b3_type$, $m4_l9_b3_title$Register$m4_l9_b3_title$, $m4_l9_b3_content$### Условие

Реализуй `POST /auth/register`.

### Вход

```json
{"email": "a@mail.com", "password": "secret"}
```

Ответ не должен содержать пароль.$m4_l9_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l9_b4_type$practice$m4_l9_b4_type$, $m4_l9_b4_title$Login$m4_l9_b4_title$, $m4_l9_b4_content$### Условие

Реализуй `POST /auth/login`. Если email/password правильные, верни access token.$m4_l9_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l9_b5_type$theory$m4_l9_b5_type$, $m4_l9_b5_title$JWT$m4_l9_b5_title$, $m4_l9_b5_content$JWT — токен, который клиент отправляет в заголовке:

```text
Authorization: Bearer <token>
```

Сервер проверяет токен и понимает, какой пользователь делает запрос.$m4_l9_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l9_b6_type$practice$m4_l9_b6_type$, $m4_l9_b6_title$Protected$m4_l9_b6_title$, $m4_l9_b6_content$### Условие

Защити endpoint `GET /me`. Он должен возвращать текущего пользователя только при валидном токене.$m4_l9_b6_content$, NULL, NULL::jsonb),
  (7, $m4_l9_b7_type$project$m4_l9_b7_type$, $m4_l9_b7_title$Контроль$m4_l9_b7_title$, $m4_l9_b7_content$Отправь auth-код на проверку безопасности.

---$m4_l9_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 10: Depends
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 10
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 10
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l10_b1_type$theory$m4_l10_b1_type$, $m4_l10_b1_title$DI$m4_l10_b1_title$, $m4_l10_b1_content$Dependency Injection — способ сказать endpoint, что ему нужно: БД, текущий пользователь, настройки, сервис.

```python
def get_current_user():
    ...

@app.get("/me")
def me(user = Depends(get_current_user)):
    return user
```

Endpoint не создаёт зависимость сам. FastAPI передаёт её.

## Шаги 2–4. Практика$m4_l10_b1_content$, NULL, NULL::jsonb),
  (5, $m4_l10_b5_type$theory$m4_l10_b5_type$, $m4_l10_b5_title$Контроль$m4_l10_b5_title$, $m4_l10_b5_content$Endpoint `GET /protected` должен работать только с текущим пользователем из зависимости.

---$m4_l10_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 11: PyTest
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 11
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 11
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l11_b1_type$theory$m4_l11_b1_type$, $m4_l11_b1_title$Пирамида$m4_l11_b1_title$, $m4_l11_b1_content$Пирамида тестирования:

```text
много unit-тестов
меньше integration-тестов
ещё меньше end-to-end-тестов
```

Unit-тест проверяет маленькую функцию. API-тест проверяет endpoint.$m4_l11_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l11_b2_type$practice$m4_l11_b2_type$, $m4_l11_b2_title$Unit$m4_l11_b2_title$, $m4_l11_b2_content$### Условие

Напиши тест для функции:

```python
def add(a, b):
    return a + b
```

Тест:

```python
def test_add():
    assert add(2, 3) == 5
```$m4_l11_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l11_b3_type$theory$m4_l11_b3_type$, $m4_l11_b3_title$Fixture$m4_l11_b3_title$, $m4_l11_b3_content$Fixture готовит данные для теста.

```python
@pytest.fixture
def user():
    return {"id": 1, "email": "a@mail.com"}
```$m4_l11_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l11_b4_type$practice$m4_l11_b4_type$, $m4_l11_b4_title$API test$m4_l11_b4_title$, $m4_l11_b4_content$**Коротко:** протестируй healthcheck.

### Условие

Напиши тест, который делает `GET /health` и проверяет:

- status code 200;
- JSON `{"status": "ok"}`.$m4_l11_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l11_b5_type$practice$m4_l11_b5_type$, $m4_l11_b5_title$DB test$m4_l11_b5_title$, $m4_l11_b5_content$### Условие

Для тестов БД используй отдельную тестовую базу. Не тестируй на production-данных.

Минимум: SQLite in-memory или отдельный контейнер Postgres для тестов.$m4_l11_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l11_b6_type$theory$m4_l11_b6_type$, $m4_l11_b6_title$Контроль$m4_l11_b6_title$, $m4_l11_b6_content$Напиши тесты:

- создать задачу;
- получить список;
- получить задачу по id;
- 404 для неизвестной задачи;
- удалить задачу.

---$m4_l11_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 12: Postman
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 12
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 12
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m4_l12_t3_title$Env$m4_l12_t3_title$, $m4_l12_t3_statement$### Условие

Создай переменную окружения:

```text
base_url = http://localhost:8000
```

Используй её в запросах:

```text
{{base_url}}/health
```$m4_l12_t3_statement$, $m4_l12_t3_starter$$m4_l12_t3_starter$, $m4_l12_t3_solution$$m4_l12_t3_solution$, 2, 50, $m4_l12_t3_topic$Месяц 4. FastAPI и DevOps — Postman$m4_l12_t3_topic$, $m4_l12_t3_lang$python$m4_l12_t3_lang$, $m4_l12_t3_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m4_l12_t3_policy$::jsonb),
  ($m4_l12_t4_title$Auth header$m4_l12_t4_title$, $m4_l12_t4_statement$### Условие

Для защищённых запросов добавь заголовок:

```text
Authorization: Bearer <token>
```$m4_l12_t4_statement$, $m4_l12_t4_starter$$m4_l12_t4_starter$, $m4_l12_t4_solution$$m4_l12_t4_solution$, 2, 50, $m4_l12_t4_topic$Месяц 4. FastAPI и DevOps — Postman$m4_l12_t4_topic$, $m4_l12_t4_lang$python$m4_l12_t4_lang$, $m4_l12_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m4_l12_t4_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 12
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m4_l12_ttitle_3$Env$m4_l12_ttitle_3$,
    $m4_l12_ttitle_4$Auth header$m4_l12_ttitle_4$
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 12
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m4_l12_test_3_1_title$Env$m4_l12_test_3_1_title$, $m4_l12_test_3_1_input$$m4_l12_test_3_1_input$, $m4_l12_test_3_1_expected$base_url = http://localhost:8000$m4_l12_test_3_1_expected$, FALSE, 1),
  ($m4_l12_test_4_1_title$Auth header$m4_l12_test_4_1_title$, $m4_l12_test_4_1_input$$m4_l12_test_4_1_input$, $m4_l12_test_4_1_expected$Authorization: Bearer <token>$m4_l12_test_4_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 12
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l12_b1_type$theory$m4_l12_b1_type$, $m4_l12_b1_title$Зачем Postman$m4_l12_b1_title$, $m4_l12_b1_content$Postman помогает вручную отправлять HTTP-запросы: GET, POST, PATCH, DELETE. Это удобно для проверки API до написания автоматических тестов.$m4_l12_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l12_b2_type$practice$m4_l12_b2_type$, $m4_l12_b2_title$Collection$m4_l12_b2_title$, $m4_l12_b2_content$### Условие

Создай коллекцию `Task API` и запросы:

- health;
- register;
- login;
- create task;
- list tasks;
- update task;
- delete task.$m4_l12_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l12_b3_type$practice$m4_l12_b3_type$, $m4_l12_b3_title$Env$m4_l12_b3_title$, $m4_l12_b3_content$### Условие

Создай переменную окружения:

```text
base_url = http://localhost:8000
```

Используй её в запросах:

```text
{{base_url}}/health
```$m4_l12_b3_content$, $m4_l12_b3_task_title$Env$m4_l12_b3_task_title$, NULL::jsonb),
  (4, $m4_l12_b4_type$practice$m4_l12_b4_type$, $m4_l12_b4_title$Auth header$m4_l12_b4_title$, $m4_l12_b4_content$### Условие

Для защищённых запросов добавь заголовок:

```text
Authorization: Bearer <token>
```$m4_l12_b4_content$, $m4_l12_b4_task_title$Auth header$m4_l12_b4_task_title$, NULL::jsonb),
  (5, $m4_l12_b5_type$practice$m4_l12_b5_type$, $m4_l12_b5_title$Чеклист$m4_l12_b5_title$, $m4_l12_b5_content$### Условие

Отправь скрин/экспорт коллекции. Должны быть запросы для полного CRUD и auth.

---$m4_l12_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 13: Dockerfile
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 13
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 13
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m4_l13_t4_title$run$m4_l13_t4_title$, $m4_l13_t4_statement$### Условие

Запусти контейнер:

```bash
docker run -p 8000:8000 task-api
```

Проверь:

```text
http://localhost:8000/health
```$m4_l13_t4_statement$, $m4_l13_t4_starter$$m4_l13_t4_starter$, $m4_l13_t4_solution$$m4_l13_t4_solution$, 2, 50, $m4_l13_t4_topic$Месяц 4. FastAPI и DevOps — Dockerfile$m4_l13_t4_topic$, $m4_l13_t4_lang$python$m4_l13_t4_lang$, $m4_l13_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m4_l13_t4_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 13
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m4_l13_ttitle_4$run$m4_l13_ttitle_4$
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 13
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m4_l13_test_4_1_title$run$m4_l13_test_4_1_title$, $m4_l13_test_4_1_input$$m4_l13_test_4_1_input$, $m4_l13_test_4_1_expected$http://localhost:8000/health$m4_l13_test_4_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 13
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l13_b1_type$theory$m4_l13_b1_type$, $m4_l13_b1_title$Image/container$m4_l13_b1_title$, $m4_l13_b1_content$Image — шаблон приложения. Container — запущенный экземпляр image.

```text
Dockerfile → image → container
```

Docker нужен, чтобы приложение запускалось одинаково у всех.$m4_l13_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l13_b2_type$practice$m4_l13_b2_type$, $m4_l13_b2_title$Dockerfile$m4_l13_b2_title$, $m4_l13_b2_content$### Условие

Минимальный Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```$m4_l13_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l13_b3_type$practice$m4_l13_b3_type$, $m4_l13_b3_title$build$m4_l13_b3_title$, $m4_l13_b3_content$### Условие

Собери image:

```bash
docker build -t task-api .
```$m4_l13_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l13_b4_type$practice$m4_l13_b4_type$, $m4_l13_b4_title$run$m4_l13_b4_title$, $m4_l13_b4_content$### Условие

Запусти контейнер:

```bash
docker run -p 8000:8000 task-api
```

Проверь:

```text
http://localhost:8000/health
```$m4_l13_b4_content$, $m4_l13_b4_task_title$run$m4_l13_b4_task_title$, NULL::jsonb),
  (5, $m4_l13_b5_type$theory$m4_l13_b5_type$, $m4_l13_b5_title$.dockerignore$m4_l13_b5_title$, $m4_l13_b5_content$`.dockerignore` исключает лишние файлы из сборки.

```text
.venv
__pycache__
.git
.pytest_cache
.env
```

`.env` нельзя случайно копировать в image.$m4_l13_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l13_b6_type$theory$m4_l13_b6_type$, $m4_l13_b6_title$Контроль$m4_l13_b6_title$, $m4_l13_b6_content$Собери image и запусти контейнер. Healthcheck должен отвечать `200`.

---$m4_l13_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 14: Compose
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 14
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 14
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l14_b1_type$theory$m4_l14_b1_type$, $m4_l14_b1_title$Зачем compose$m4_l14_b1_title$, $m4_l14_b1_content$Docker Compose запускает несколько сервисов вместе:

```text
api
postgres
redis
nginx
```

Для backend-проекта обычно нужны минимум API и БД.$m4_l14_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l14_b2_type$theory$m4_l14_b2_type$, $m4_l14_b2_title$services$m4_l14_b2_title$, $m4_l14_b2_content$Compose-файл описывает сервисы:

```yaml
services:
  api:
    build: .
  db:
    image: postgres:16
```$m4_l14_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l14_b3_type$practice$m4_l14_b3_type$, $m4_l14_b3_title$app + db$m4_l14_b3_title$, $m4_l14_b3_content$### Условие

Создай `docker-compose.yml` с сервисами:

- `api`;
- `db` на PostgreSQL;
- volume для данных БД.$m4_l14_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l14_b4_type$practice$m4_l14_b4_type$, $m4_l14_b4_title$healthcheck$m4_l14_b4_title$, $m4_l14_b4_content$### Условие

Добавь healthcheck для БД:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 5s
  timeout: 5s
  retries: 5
```$m4_l14_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l14_b5_type$theory$m4_l14_b5_type$, $m4_l14_b5_title$depends_on$m4_l14_b5_title$, $m4_l14_b5_content$`depends_on` задаёт порядок запуска, но сам по себе не гарантирует, что БД уже готова принимать подключения. Поэтому полезен healthcheck.$m4_l14_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l14_b6_type$theory$m4_l14_b6_type$, $m4_l14_b6_title$Контроль$m4_l14_b6_title$, $m4_l14_b6_content$Запусти проект:

```bash
docker compose up --build
```

API должен отвечать на `/health`, а БД должна быть доступна приложению.

---$m4_l14_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 15: Logs/config
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 15
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 15
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m4_l15_t2_title$env$m4_l15_t2_title$, $m4_l15_t2_statement$### Условие

Создай `.env.example`:

```text
DATABASE_URL=postgresql://postgres:postgres@db:5432/app
SECRET_KEY=change-me
```

Настоящий `.env` не коммить.$m4_l15_t2_statement$, $m4_l15_t2_starter$$m4_l15_t2_starter$, $m4_l15_t2_solution$$m4_l15_t2_solution$, 2, 50, $m4_l15_t2_topic$Месяц 4. FastAPI и DevOps — Logs/config$m4_l15_t2_topic$, $m4_l15_t2_lang$python$m4_l15_t2_lang$, $m4_l15_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m4_l15_t2_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 15
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m4_l15_ttitle_2$env$m4_l15_ttitle_2$
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 15
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m4_l15_test_2_1_title$env$m4_l15_test_2_1_title$, $m4_l15_test_2_1_input$$m4_l15_test_2_1_input$, $m4_l15_test_2_1_expected$DATABASE_URL=postgresql://postgres:postgres@db:5432/app
SECRET_KEY=change-me$m4_l15_test_2_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 15
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l15_b1_type$theory$m4_l15_b1_type$, $m4_l15_b1_title$12-factor$m4_l15_b1_title$, $m4_l15_b1_content$Настройки не должны быть зашиты в код.

Плохо:

```python
DATABASE_URL = "postgresql://postgres:secret@db/app"
```

Лучше читать из env:

```python
DATABASE_URL = os.getenv("DATABASE_URL")
```$m4_l15_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l15_b2_type$practice$m4_l15_b2_type$, $m4_l15_b2_title$env$m4_l15_b2_title$, $m4_l15_b2_content$### Условие

Создай `.env.example`:

```text
DATABASE_URL=postgresql://postgres:postgres@db:5432/app
SECRET_KEY=change-me
```

Настоящий `.env` не коммить.$m4_l15_b2_content$, $m4_l15_b2_task_title$env$m4_l15_b2_task_title$, NULL::jsonb),
  (3, $m4_l15_b3_type$practice$m4_l15_b3_type$, $m4_l15_b3_title$Settings$m4_l15_b3_title$, $m4_l15_b3_content$### Условие

Создай класс настроек через `pydantic-settings`.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
```$m4_l15_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l15_b4_type$practice$m4_l15_b4_type$, $m4_l15_b4_title$logging$m4_l15_b4_title$, $m4_l15_b4_content$### Условие

Добавь логирование важных событий:

- старт приложения;
- создание задачи;
- ошибка подключения к БД;
- ошибка авторизации.

Не логируй пароли и токены.$m4_l15_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l15_b5_type$project$m4_l15_b5_type$, $m4_l15_b5_title$Ошибки$m4_l15_b5_title$, $m4_l15_b5_content$Отправь конфиг на проверку.

---$m4_l15_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 16: CI/CD
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 16
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 16
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l16_b1_type$theory$m4_l16_b1_type$, $m4_l16_b1_title$Что такое CI$m4_l16_b1_title$, $m4_l16_b1_content$CI — автоматическая проверка кода после push/PR.

Минимум:

```text
установить зависимости
запустить линтер
запустить тесты
собрать Docker image
```

CD — автоматическая доставка/деплой.$m4_l16_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l16_b2_type$practice$m4_l16_b2_type$, $m4_l16_b2_title$workflow$m4_l16_b2_title$, $m4_l16_b2_content$### Условие

Создай `.github/workflows/ci.yml`.

Минимальная структура:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
```$m4_l16_b2_content$, NULL, NULL::jsonb),
  (3, $m4_l16_b3_type$practice$m4_l16_b3_type$, $m4_l16_b3_title$tests$m4_l16_b3_title$, $m4_l16_b3_content$### Условие

Добавь шаги установки Python, зависимостей и запуска тестов.$m4_l16_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l16_b4_type$practice$m4_l16_b4_type$, $m4_l16_b4_title$lint$m4_l16_b4_title$, $m4_l16_b4_content$### Условие

Добавь запуск `ruff check .` или другого линтера.$m4_l16_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l16_b5_type$practice$m4_l16_b5_type$, $m4_l16_b5_title$build image$m4_l16_b5_title$, $m4_l16_b5_content$### Условие

Добавь проверку сборки Docker image:

```bash
docker build -t task-api .
```$m4_l16_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l16_b6_type$theory$m4_l16_b6_type$, $m4_l16_b6_title$Контроль$m4_l16_b6_title$, $m4_l16_b6_content$Отправь workflow на проверку. Он должен запускаться на push и pull request, проверять тесты, линтер и сборку image.

---$m4_l16_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 4, lesson 17: Mini CRUD
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 17
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 17
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m4_l17_t2_title$API$m4_l17_t2_title$, $m4_l17_t2_statement$### Условие

Опиши API-контракт в README. Должны быть endpoints:

```text
POST /auth/register
POST /auth/login
GET /items
POST /items
GET /items/{id}
PATCH /items/{id}
DELETE /items/{id}
```$m4_l17_t2_statement$, $m4_l17_t2_starter$$m4_l17_t2_starter$, $m4_l17_t2_solution$$m4_l17_t2_solution$, 2, 50, $m4_l17_t2_topic$Месяц 4. FastAPI и DevOps — Mini CRUD$m4_l17_t2_topic$, $m4_l17_t2_lang$python$m4_l17_t2_lang$, $m4_l17_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m4_l17_t2_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 17
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m4_l17_ttitle_2$API$m4_l17_ttitle_2$
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
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 17
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m4_l17_test_2_1_title$API$m4_l17_test_2_1_title$, $m4_l17_test_2_1_input$$m4_l17_test_2_1_input$, $m4_l17_test_2_1_expected$POST /auth/register
POST /auth/login
GET /items
POST /items
GET /items/{id}
PATCH /items/{id}
DELETE /items/{id}$m4_l17_test_2_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 4 AND l.position = 17
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m4_l17_b1_type$theory$m4_l17_b1_type$, $m4_l17_b1_title$ТЗ$m4_l17_b1_title$, $m4_l17_b1_content$Сделай CRUD-сервис для одной предметной области:

- задачи;
- заявки;
- книги;
- привычки;
- расходы;
- клиенты.

Минимум:

```text
FastAPI
PostgreSQL или SQLite для упрощённого варианта
SQLAlchemy
Pydantic-схемы
Auth
PyTest
Dockerfile
docker-compose.yml
CI
README
```$m4_l17_b1_content$, NULL, NULL::jsonb),
  (2, $m4_l17_b2_type$practice$m4_l17_b2_type$, $m4_l17_b2_title$API$m4_l17_b2_title$, $m4_l17_b2_content$### Условие

Опиши API-контракт в README. Должны быть endpoints:

```text
POST /auth/register
POST /auth/login
GET /items
POST /items
GET /items/{id}
PATCH /items/{id}
DELETE /items/{id}
```$m4_l17_b2_content$, $m4_l17_b2_task_title$API$m4_l17_b2_task_title$, NULL::jsonb),
  (3, $m4_l17_b3_type$practice$m4_l17_b3_type$, $m4_l17_b3_title$DB$m4_l17_b3_title$, $m4_l17_b3_content$### Условие

Создай модели БД и миграции. У каждого пользователя должны быть только свои записи.$m4_l17_b3_content$, NULL, NULL::jsonb),
  (4, $m4_l17_b4_type$practice$m4_l17_b4_type$, $m4_l17_b4_title$Auth$m4_l17_b4_title$, $m4_l17_b4_content$### Условие

Добавь регистрацию, логин и защиту CRUD. Пользователь не должен видеть чужие записи.$m4_l17_b4_content$, NULL, NULL::jsonb),
  (5, $m4_l17_b5_type$practice$m4_l17_b5_type$, $m4_l17_b5_title$Tests$m4_l17_b5_title$, $m4_l17_b5_content$### Условие

Минимум 10 тестов:

- health;
- register;
- login;
- create item;
- list own items;
- get item;
- update item;
- delete item;
- 404 unknown item;
- запрет доступа к чужому item.$m4_l17_b5_content$, NULL, NULL::jsonb),
  (6, $m4_l17_b6_type$practice$m4_l17_b6_type$, $m4_l17_b6_title$Docker$m4_l17_b6_title$, $m4_l17_b6_content$### Условие

Добавь Dockerfile и docker-compose. Команда запуска:

```bash
docker compose up --build
```$m4_l17_b6_content$, NULL, NULL::jsonb),
  (7, $m4_l17_b7_type$practice$m4_l17_b7_type$, $m4_l17_b7_title$CI$m4_l17_b7_title$, $m4_l17_b7_content$### Условие

CI должен запускать тесты, линтер и docker build.$m4_l17_b7_content$, NULL, NULL::jsonb),
  (8, $m4_l17_b8_type$project$m4_l17_b8_type$, $m4_l17_b8_title$Защита$m4_l17_b8_title$, $m4_l17_b8_content$Отправь проект на проверку.

---

# Экзамен месяца 4

**В интерфейсе:** Экзамен 4

## Формат

1. HTTP-задачи по FastAPI.
2. Задача на Pydantic-схемы.
3. Задача на Depends.
4. Задача на тест API.
5. Docker/Compose чеклист.
6. Проект Mini CRUD.

## Маршрут восстановления

- Не понимает routes/path/query/body → уроки 2–3.
- Ошибки Pydantic → урок 4.
- Нет CRUD-логики → урок 5.
- Всё в main.py → урок 6.
- БД/SQLAlchemy → уроки 7–8.
- Auth → урок 9–10.
- Тесты → уроки 11–12.
- Docker/CI → уроки 13–16.
# Месяц 5. Финальный проект, AI-интеграция, вайбкодинг и деплой

Цель месяца: довести ученика до полного цикла backend-разработки: ТЗ, архитектура, API, БД, тесты, Docker, CI/CD, AI-интеграция, деплой на VPS и защита.

## Сетка месяца

| Урок | Название | Фокус | Проверка |
|---:|---|---|---|
| 1 | No vibe | проект без AI-подсказок | AI-check + ревью |
| 2 | Code review | качество кода | AI-check |
| 3 | AI API | OpenAI/Anthropic API | Python-runner + AI |
| 4 | Structured | JSON/structured output | Python-runner |
| 5 | RAG | документы, чанки, embeddings | AI-check |
| 6 | Vector DB | поиск по векторам | AI-check |
| 7 | LangChain | когда нужен фреймворк | проект |
| 8 | LangGraph | графы и агенты | проект |
| 9 | Vibe coding | безопасный AI-процесс | AI-check |
| 10 | Final spec | ТЗ финального проекта | AI-check |
| 11 | Sprint 1 | API + DB | ревью |
| 12 | Sprint 2 | AI-фича + tests | ревью |
| 13 | VPS | сервер и безопасность | чеклист |
| 14 | Nginx SSL | домен, reverse proxy, TLS | чеклист |
| 15 | Autodeploy | деплой через CI/CD | чеклист |
| 16 | Defense | защита проекта | AI + ментор |

---$m4_l17_b8_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5: Месяц 5. Финальный проект, AI и деплой
WITH module_ref AS (
  SELECT m.id AS module_id
  FROM modules m
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5
), lesson_seed(position, title, content_md) AS (
  VALUES
  (1, $m5_l1_title$No vibe$m5_l1_title$, $m5_l1_content$Небольшой проект без вайбкодинга.$m5_l1_content$),
  (2, $m5_l2_title$Code review$m5_l2_title$, $m5_l2_content$Учимся видеть качество кода.$m5_l2_content$),
  (3, $m5_l3_title$AI API$m5_l3_title$, $m5_l3_content$Подключаем LLM API из Python.$m5_l3_content$),
  (4, $m5_l4_title$Structured$m5_l4_title$, $m5_l4_content$Просим модель вернуть строгий JSON.$m5_l4_content$),
  (5, $m5_l5_title$RAG$m5_l5_title$, $m5_l5_content$Отвечаем по своим документам.$m5_l5_content$),
  (6, $m5_l6_title$Vector DB$m5_l6_title$, $m5_l6_content$Храним и ищем embeddings.$m5_l6_content$),
  (7, $m5_l7_title$LangChain$m5_l7_title$, $m5_l7_content$Когда нужен AI-фреймворк.$m5_l7_content$),
  (8, $m5_l8_title$LangGraph$m5_l8_title$, $m5_l8_content$Агент как граф шагов.$m5_l8_content$),
  (9, $m5_l9_title$Vibe coding$m5_l9_title$, $m5_l9_content$Используем AI как инженер, а не как пассажир.$m5_l9_content$),
  (10, $m5_l10_title$Final spec$m5_l10_title$, $m5_l10_content$Формулируем ТЗ финального проекта.$m5_l10_content$),
  (11, $m5_l11_title$Sprint 1$m5_l11_title$, $m5_l11_content$Реализуем основу: API и БД.$m5_l11_content$),
  (12, $m5_l12_title$Sprint 2$m5_l12_title$, $m5_l12_content$Добавляем AI-фичу, тесты и качество.$m5_l12_content$),
  (13, $m5_l13_title$VPS$m5_l13_title$, $m5_l13_content$Сервер, пользователь и базовая безопасность.$m5_l13_content$),
  (14, $m5_l14_title$Nginx SSL$m5_l14_title$, $m5_l14_content$Домен, reverse proxy и HTTPS.$m5_l14_content$),
  (15, $m5_l15_title$Autodeploy$m5_l15_title$, $m5_l15_content$Деплой через CI/CD.$m5_l15_content$),
  (16, $m5_l16_title$Defense$m5_l16_title$, $m5_l16_content$Защита финального проекта.$m5_l16_content$)
)
INSERT INTO lessons(module_id, title, content_md, position, is_published)
SELECT mr.module_id, ls.title, ls.content_md, ls.position, TRUE
FROM module_ref mr
CROSS JOIN lesson_seed ls
ON CONFLICT (module_id, position) DO UPDATE
SET title = EXCLUDED.title,
    content_md = EXCLUDED.content_md,
    is_published = TRUE,
    updated_at = NOW();

-- Module 5, lesson 1: No vibe
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 1
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 1
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l1_b1_type$theory$m5_l1_b1_type$, $m5_l1_b1_title$Зачем без AI$m5_l1_b1_title$, $m5_l1_b1_content$Перед финальным проектом нужно доказать, что ты можешь писать код сам. AI можно использовать для объяснений, но нельзя просить его написать проект целиком.

Цель: проверить реальное понимание.$m5_l1_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l1_b2_type$theory$m5_l1_b2_type$, $m5_l1_b2_title$ТЗ$m5_l1_b2_title$, $m5_l1_b2_content$Выбери один проект:

1. API заметок.
2. API расходов.
3. API привычек.
4. API книг.

Минимум:

```text
FastAPI
CRUD
SQLite/PostgreSQL
SQLAlchemy
Pydantic
5 тестов
README
```$m5_l1_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l1_b3_type$project$m5_l1_b3_type$, $m5_l1_b3_title$Реализация$m5_l1_b3_title$, $m5_l1_b3_content$Реализуй проект без генерации полного кода через AI. Разрешено спрашивать:

```text
Объясни ошибку
Проверь архитектуру
Дай похожий пример
Задай вопросы по ТЗ
```

Запрещено:

```text
Напиши весь проект
Сделай все файлы
Исправь всё сам
```$m5_l1_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l1_b4_type$practice$m5_l1_b4_type$, $m5_l1_b4_title$Тесты$m5_l1_b4_title$, $m5_l1_b4_content$### Условие

Напиши минимум 5 тестов:

- health;
- create;
- list;
- update;
- delete.$m5_l1_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l1_b5_type$project$m5_l1_b5_type$, $m5_l1_b5_title$Самооценка$m5_l1_b5_title$, $m5_l1_b5_content$Ответь письменно:

1. Что ты сделал сам?
2. Где использовал AI?
3. Какие ошибки были?
4. Как ты проверил проект?
5. Что улучшил бы?

---$m5_l1_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 2: Code review
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 2
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 2
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m5_l2_t4_title$Refactor$m5_l2_t4_title$, $m5_l2_t4_statement$### Условие

Выбери 3 проблемы и исправь их. В README добавь раздел:

```text
Что было улучшено после ревью
```$m5_l2_t4_statement$, $m5_l2_t4_starter$$m5_l2_t4_starter$, $m5_l2_t4_solution$$m5_l2_t4_solution$, 2, 50, $m5_l2_t4_topic$Месяц 5. Финальный проект, AI и деплой — Code review$m5_l2_t4_topic$, $m5_l2_t4_lang$python$m5_l2_t4_lang$, $m5_l2_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m5_l2_t4_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 2
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m5_l2_ttitle_4$Refactor$m5_l2_ttitle_4$
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 2
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m5_l2_test_4_1_title$Refactor$m5_l2_test_4_1_title$, $m5_l2_test_4_1_input$$m5_l2_test_4_1_input$, $m5_l2_test_4_1_expected$Что было улучшено после ревью$m5_l2_test_4_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 2
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l2_b1_type$theory$m5_l2_b1_type$, $m5_l2_b1_title$Ревью$m5_l2_b1_title$, $m5_l2_b1_content$Code review — не поиск виноватых. Это проверка качества решения.

Смотрим:

- работает ли код;
- понятна ли структура;
- нет ли дублирования;
- есть ли тесты;
- не утекли ли секреты;
- правильно ли обработаны ошибки.$m5_l2_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l2_b2_type$theory$m5_l2_b2_type$, $m5_l2_b2_title$Smells$m5_l2_b2_title$, $m5_l2_b2_content$Частые признаки плохого кода:

```text
функция на 100 строк
всё в main.py
магические числа
дублирование
голый except
пароли в коде
нет тестов
```$m5_l2_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l2_b3_type$practice$m5_l2_b3_type$, $m5_l2_b3_title$Checklist$m5_l2_b3_title$, $m5_l2_b3_content$### Условие

Проверь свой проект по чеклисту:

- структура файлов понятна;
- endpoints короткие;
- бизнес-логика не в router;
- SQL-запросы параметризованы;
- пароли не возвращаются;
- тесты проходят;
- README объясняет запуск.$m5_l2_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l2_b4_type$practice$m5_l2_b4_type$, $m5_l2_b4_title$Refactor$m5_l2_b4_title$, $m5_l2_b4_content$### Условие

Выбери 3 проблемы и исправь их. В README добавь раздел:

```text
Что было улучшено после ревью
```$m5_l2_b4_content$, $m5_l2_b4_task_title$Refactor$m5_l2_b4_task_title$, NULL::jsonb),
  (5, $m5_l2_b5_type$project$m5_l2_b5_type$, $m5_l2_b5_title$Review$m5_l2_b5_title$, $m5_l2_b5_content$Отправь проект на AI-review. Применить нужно не все советы, а только полезные. Напиши, какие советы принял и почему.

---$m5_l2_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 3: AI API
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 3
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 3
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m5_l3_t6_title$Контроль$m5_l3_t6_title$, $m5_l3_t6_statement$### Условие

Сделай endpoint:

```text
POST /ai/summarize
```

### Вход

```json
{"text": "длинный текст"}
```

Ответ:

```json
{"summary": "краткое содержание"}
```

В sandbox можно использовать mock.

---$m5_l3_t6_statement$, $m5_l3_t6_starter$$m5_l3_t6_starter$, $m5_l3_t6_solution$$m5_l3_t6_solution$, 2, 50, $m5_l3_t6_topic$Месяц 5. Финальный проект, AI и деплой — AI API$m5_l3_t6_topic$, $m5_l3_t6_lang$python$m5_l3_t6_lang$, $m5_l3_t6_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m5_l3_t6_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 3
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m5_l3_ttitle_6$Контроль$m5_l3_ttitle_6$
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 3
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m5_l3_test_6_1_title$Контроль$m5_l3_test_6_1_title$, $m5_l3_test_6_1_input$$m5_l3_test_6_1_input$, $m5_l3_test_6_1_expected$POST /ai/summarize$m5_l3_test_6_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 3
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l3_b1_type$theory$m5_l3_b1_type$, $m5_l3_b1_title$Что такое API$m5_l3_b1_title$, $m5_l3_b1_content$AI API — это HTTP/API-интерфейс к модели. Ты отправляешь запрос с текстом, получаешь ответ модели.

В backend-проекте AI может:

- классифицировать текст;
- отвечать на вопросы;
- извлекать структуру;
- помогать искать по документам;
- генерировать краткие резюме;
- быть частью агента.$m5_l3_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l3_b2_type$theory$m5_l3_b2_type$, $m5_l3_b2_title$API key$m5_l3_b2_title$, $m5_l3_b2_content$API-ключ нельзя хранить в коде.

Плохо:

```python
API_KEY = "sk-..."
```

Правильно:

```python
import os
api_key = os.getenv("OPENAI_API_KEY")
```

или для Anthropic:

```python
api_key = os.getenv("ANTHROPIC_API_KEY")
```

Ключи добавляют в `.env`, а `.env` — в `.gitignore`.$m5_l3_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l3_b3_type$practice$m5_l3_b3_type$, $m5_l3_b3_title$First call$m5_l3_b3_title$, $m5_l3_b3_content$**Коротко:** сделай первый вызов AI API.

### Условие

Создай функцию:

```python
def ask_ai(prompt: str) -> str:
    ...
```

Она должна отправить запрос к выбранному провайдеру и вернуть текст ответа.

Если в платформе нет внешнего доступа к API, используй mock-функцию:

```python
def ask_ai(prompt: str) -> str:
    return "mock response"
```$m5_l3_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l3_b4_type$theory$m5_l3_b4_type$, $m5_l3_b4_title$Errors$m5_l3_b4_title$, $m5_l3_b4_content$AI API может вернуть ошибку:

- нет ключа;
- превышен лимит;
- слишком большой запрос;
- сеть недоступна;
- модель недоступна;
- неверный формат запроса.

В production-коде нужно обрабатывать ошибки и не ломать весь сервис.$m5_l3_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l3_b5_type$theory$m5_l3_b5_type$, $m5_l3_b5_title$Cost$m5_l3_b5_title$, $m5_l3_b5_content$AI-запросы стоят денег и имеют лимиты. Нужно:

- ограничивать длину ввода;
- кэшировать повторные ответы, где это уместно;
- логировать usage без персональных данных;
- не отправлять секреты и пароли в модель.$m5_l3_b5_content$, NULL, NULL::jsonb),
  (6, $m5_l3_b6_type$practice$m5_l3_b6_type$, $m5_l3_b6_title$Контроль$m5_l3_b6_title$, $m5_l3_b6_content$### Условие

Сделай endpoint:

```text
POST /ai/summarize
```

### Вход

```json
{"text": "длинный текст"}
```

Ответ:

```json
{"summary": "краткое содержание"}
```

В sandbox можно использовать mock.

---$m5_l3_b6_content$, $m5_l3_b6_task_title$Контроль$m5_l3_b6_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 4: Structured
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 4
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 4
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m5_l4_t5_title$Контроль$m5_l4_t5_title$, $m5_l4_t5_statement$### Условие

Добавь endpoint:

```text
POST /ai/classify
```

### Вход

```json
{"text": "Срочно оплатить счёт"}
```

Ответ:

```json
{"category": "finance", "priority": 3}
```

---$m5_l4_t5_statement$, $m5_l4_t5_starter$$m5_l4_t5_starter$, $m5_l4_t5_solution$$m5_l4_t5_solution$, 2, 50, $m5_l4_t5_topic$Месяц 5. Финальный проект, AI и деплой — Structured$m5_l4_t5_topic$, $m5_l4_t5_lang$python$m5_l4_t5_lang$, $m5_l4_t5_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m5_l4_t5_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 4
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m5_l4_ttitle_5$Контроль$m5_l4_ttitle_5$
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 4
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m5_l4_test_5_1_title$Контроль$m5_l4_test_5_1_title$, $m5_l4_test_5_1_input$$m5_l4_test_5_1_input$, $m5_l4_test_5_1_expected$POST /ai/classify$m5_l4_test_5_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 4
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l4_b1_type$theory$m5_l4_b1_type$, $m5_l4_b1_title$Зачем JSON$m5_l4_b1_title$, $m5_l4_b1_content$Для backend-проекта ответ модели должен быть предсказуемым. Свободный текст сложно обрабатывать. JSON удобно валидировать.

Плохо:

```text
Кажется, это задача со средней важностью...
```

Лучше:

```json
{"category": "task", "priority": 2}
```$m5_l4_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l4_b2_type$theory$m5_l4_b2_type$, $m5_l4_b2_title$Schema$m5_l4_b2_title$, $m5_l4_b2_content$Схема описывает ожидаемый формат.

```python
class Classification(BaseModel):
    category: str
    priority: int
```

После ответа модели проверь данные через Pydantic.$m5_l4_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l4_b3_type$practice$m5_l4_b3_type$, $m5_l4_b3_title$Extract$m5_l4_b3_title$, $m5_l4_b3_content$**Коротко:** извлеки данные из текста.

### Условие

Сделай функцию `extract_task(text)`, которая возвращает словарь:

```python
{"title": "...", "priority": 1}
```

Если API недоступен, сделай mock.$m5_l4_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l4_b4_type$practice$m5_l4_b4_type$, $m5_l4_b4_title$Validate$m5_l4_b4_title$, $m5_l4_b4_content$### Условие

Проверь ответ модели через Pydantic-модель. Если модель вернула неправильный JSON, верни ошибку API `400` или безопасный fallback.$m5_l4_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l4_b5_type$practice$m5_l4_b5_type$, $m5_l4_b5_title$Контроль$m5_l4_b5_title$, $m5_l4_b5_content$### Условие

Добавь endpoint:

```text
POST /ai/classify
```

### Вход

```json
{"text": "Срочно оплатить счёт"}
```

Ответ:

```json
{"category": "finance", "priority": 3}
```

---$m5_l4_b5_content$, $m5_l4_b5_task_title$Контроль$m5_l4_b5_task_title$, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 5: RAG
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 5
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 5
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l5_b1_type$theory$m5_l5_b1_type$, $m5_l5_b1_title$Что такое RAG$m5_l5_b1_title$, $m5_l5_b1_content$RAG — подход, где модель отвечает не только из своей памяти, а с опорой на найденные документы.

```text
вопрос → поиск релевантных фрагментов → ответ с учётом фрагментов
```

Это полезно для:

- базы знаний;
- внутренней документации;
- FAQ;
- учебных материалов;
- поддержки пользователей.$m5_l5_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l5_b2_type$theory$m5_l5_b2_type$, $m5_l5_b2_title$Chunks$m5_l5_b2_title$, $m5_l5_b2_content$Документ делят на фрагменты — чанки. Если чанк слишком большой, поиск хуже. Если слишком маленький, теряется контекст.

Пример:

```text
документ → абзацы → chunks по 300–800 слов
```$m5_l5_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l5_b3_type$theory$m5_l5_b3_type$, $m5_l5_b3_title$Embeddings$m5_l5_b3_title$, $m5_l5_b3_content$Embedding — числовое представление текста. Похожие тексты имеют похожие векторы.

Поиск:

```text
вопрос → embedding → найти похожие chunks → передать модели
```$m5_l5_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l5_b4_type$practice$m5_l5_b4_type$, $m5_l5_b4_title$Retrieve$m5_l5_b4_title$, $m5_l5_b4_content$**Коротко:** сделай простой поиск без векторов.

### Условие

Пока без embeddings. Есть список документов. Найди документы, где встречается слово из запроса.$m5_l5_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l5_b5_type$practice$m5_l5_b5_type$, $m5_l5_b5_title$Generate$m5_l5_b5_title$, $m5_l5_b5_content$**Коротко:** собери prompt с контекстом.

### Условие

Сделай функцию:

```python
def build_prompt(question: str, chunks: list[str]) -> str:
    ...
```

Prompt должен содержать:

- вопрос;
- найденные фрагменты;
- правило: отвечать только по контексту.$m5_l5_b5_content$, NULL, NULL::jsonb),
  (6, $m5_l5_b6_type$project$m5_l5_b6_type$, $m5_l5_b6_title$Контроль$m5_l5_b6_title$, $m5_l5_b6_content$Спроектируй RAG для FAQ учебной платформы. Опиши:

- откуда берутся документы;
- как делятся на chunks;
- где хранятся embeddings;
- как формируется ответ;
- что делать, если ответа нет в документах.

---$m5_l5_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 6: Vector DB
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 6
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 6
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l6_b1_type$theory$m5_l6_b1_type$, $m5_l6_b1_title$Зачем vector DB$m5_l6_b1_title$, $m5_l6_b1_content$Обычная БД хорошо ищет точные значения. Векторная БД ищет похожий смысл.

Пример:

```text
вопрос: как сбросить пароль?
документ: восстановление доступа к аккаунту
```

Слова разные, смысл похожий.$m5_l6_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l6_b2_type$theory$m5_l6_b2_type$, $m5_l6_b2_title$Similarity$m5_l6_b2_title$, $m5_l6_b2_content$Поиск похожести обычно сравнивает векторы. Чем ближе векторы, тем релевантнее документ.

Для курса достаточно понимать идею, не углубляясь в математику.$m5_l6_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l6_b3_type$practice$m5_l6_b3_type$, $m5_l6_b3_title$Store$m5_l6_b3_title$, $m5_l6_b3_content$### Условие

Сделай структуру для хранения документа:

```python
{
    "id": "doc-1",
    "text": "...",
    "embedding": [...],
    "metadata": {"source": "faq.md"}
}
```$m5_l6_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l6_b4_type$practice$m5_l6_b4_type$, $m5_l6_b4_title$Search$m5_l6_b4_title$, $m5_l6_b4_content$### Условие

Если в платформе нет vector DB, реализуй mock-поиск: возвращай top-3 документа по простому совпадению слов.

Если vector DB доступна, реализуй настоящий similarity search.$m5_l6_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l6_b5_type$theory$m5_l6_b5_type$, $m5_l6_b5_title$Metadata$m5_l6_b5_title$, $m5_l6_b5_content$Metadata помогает фильтровать и цитировать результаты.

```python
metadata = {
    "source": "faq.md",
    "page": 2,
    "course": "python"
}
```

Без metadata сложно объяснить, откуда взялся ответ.$m5_l6_b5_content$, NULL, NULL::jsonb),
  (6, $m5_l6_b6_type$project$m5_l6_b6_type$, $m5_l6_b6_title$Контроль$m5_l6_b6_title$, $m5_l6_b6_content$Опиши, какие metadata нужны для RAG по учебным материалам курса.

---$m5_l6_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 7: LangChain
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 7
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 7
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m5_l7_t4_title$RAG chain$m5_l7_t4_title$, $m5_l7_t4_statement$### Условие

Собери цепочку:

```text
question → retriever → context → prompt → model → answer
```

В sandbox можно mock-нуть model и retriever.$m5_l7_t4_statement$, $m5_l7_t4_starter$$m5_l7_t4_starter$, $m5_l7_t4_solution$$m5_l7_t4_solution$, 2, 50, $m5_l7_t4_topic$Месяц 5. Финальный проект, AI и деплой — LangChain$m5_l7_t4_topic$, $m5_l7_t4_lang$python$m5_l7_t4_lang$, $m5_l7_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m5_l7_t4_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 7
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m5_l7_ttitle_4$RAG chain$m5_l7_ttitle_4$
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 7
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m5_l7_test_4_1_title$RAG chain$m5_l7_test_4_1_title$, $m5_l7_test_4_1_input$$m5_l7_test_4_1_input$, $m5_l7_test_4_1_expected$question → retriever → context → prompt → model → answer$m5_l7_test_4_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 7
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l7_b1_type$theory$m5_l7_b1_type$, $m5_l7_b1_title$Зачем framework$m5_l7_b1_title$, $m5_l7_b1_content$AI-фреймворки помогают быстро собирать цепочки: prompt, model, parser, retriever, tools.

Но сначала нужно понимать базовые идеи руками. Иначе фреймворк будет магией.$m5_l7_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l7_b2_type$theory$m5_l7_b2_type$, $m5_l7_b2_title$Chain$m5_l7_b2_title$, $m5_l7_b2_content$Chain — последовательность шагов:

```text
input → prompt → model → parser → output
```$m5_l7_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l7_b3_type$practice$m5_l7_b3_type$, $m5_l7_b3_title$Prompt$m5_l7_b3_title$, $m5_l7_b3_content$### Условие

Собери prompt-template для классификации задачи по категории и приоритету.$m5_l7_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l7_b4_type$practice$m5_l7_b4_type$, $m5_l7_b4_title$RAG chain$m5_l7_b4_title$, $m5_l7_b4_content$### Условие

Собери цепочку:

```text
question → retriever → context → prompt → model → answer
```

В sandbox можно mock-нуть model и retriever.$m5_l7_b4_content$, $m5_l7_b4_task_title$RAG chain$m5_l7_b4_task_title$, NULL::jsonb),
  (5, $m5_l7_b5_type$theory$m5_l7_b5_type$, $m5_l7_b5_title$Риски$m5_l7_b5_title$, $m5_l7_b5_content$Риски фреймворков:

- много абстракций;
- сложнее дебажить;
- версии меняются;
- легко скопировать код без понимания.

Используй framework, когда понимаешь, какую проблему он решает.

---$m5_l7_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 8: LangGraph
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 8
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 8
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l8_b1_type$theory$m5_l8_b1_type$, $m5_l8_b1_title$Graph$m5_l8_b1_title$, $m5_l8_b1_content$Граф удобен, когда агент не просто отвечает, а проходит шаги:

```text
получить вопрос → найти документы → решить, нужен ли tool → вызвать tool → собрать ответ
```$m5_l8_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l8_b2_type$theory$m5_l8_b2_type$, $m5_l8_b2_title$State$m5_l8_b2_title$, $m5_l8_b2_content$State — состояние агента. В нём можно хранить:

- вопрос;
- найденный контекст;
- промежуточный план;
- вызовы инструментов;
- финальный ответ.$m5_l8_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l8_b3_type$theory$m5_l8_b3_type$, $m5_l8_b3_title$Nodes$m5_l8_b3_title$, $m5_l8_b3_content$Node — один шаг графа:

```text
retrieve_docs
classify_intent
call_tool
generate_answer
```

Edge — переход между шагами.$m5_l8_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l8_b4_type$practice$m5_l8_b4_type$, $m5_l8_b4_title$Agent plan$m5_l8_b4_title$, $m5_l8_b4_content$### Условие

Опиши граф агента поддержки учебной платформы.

Минимальные узлы:

- classify question;
- retrieve lesson context;
- decide if mentor needed;
- generate answer;
- log interaction.$m5_l8_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l8_b5_type$project$m5_l8_b5_type$, $m5_l8_b5_title$Контроль$m5_l8_b5_title$, $m5_l8_b5_content$Отправь схему агента на проверку. AI проверит, нет ли бесконечного цикла, где хранится state и когда агент должен отказаться от ответа.

---$m5_l8_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 9: Vibe coding
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 9
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 9
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l9_b1_type$theory$m5_l9_b1_type$, $m5_l9_b1_title$Правило$m5_l9_b1_title$, $m5_l9_b1_content$Вайбкодинг допустим только после того, как ты понимаешь архитектуру и можешь проверить результат.

AI может ускорить:

- черновик кода;
- тесты;
- рефакторинг;
- объяснение ошибок;
- документацию.

Но ответственность за код на тебе.$m5_l9_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l9_b2_type$theory$m5_l9_b2_type$, $m5_l9_b2_title$ТЗ сначала$m5_l9_b2_title$, $m5_l9_b2_content$Перед запросом к AI напиши:

```text
цель
ограничения
структуру проекта
контракт API
модель данных
критерии готовности
```

Без ТЗ AI будет генерировать случайную архитектуру.$m5_l9_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l9_b3_type$theory$m5_l9_b3_type$, $m5_l9_b3_title$Малые шаги$m5_l9_b3_title$, $m5_l9_b3_content$Не проси «сделай весь проект». Проси маленькие шаги:

```text
Сгенерируй Pydantic-схемы по этому контракту.
Напиши тесты для этого endpoint.
Проверь, нет ли проблемы с транзакцией.
```$m5_l9_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l9_b4_type$practice$m5_l9_b4_type$, $m5_l9_b4_title$Проверка$m5_l9_b4_title$, $m5_l9_b4_content$### Условие

Возьми код, сгенерированный AI, и проверь:

- запускается ли;
- проходят ли тесты;
- нет ли секретов;
- нет ли лишней сложности;
- можешь ли ты объяснить каждую часть.$m5_l9_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l9_b5_type$project$m5_l9_b5_type$, $m5_l9_b5_title$Античит$m5_l9_b5_title$, $m5_l9_b5_content$Ответь:

1. Какие части проекта AI помог написать?
2. Как ты проверил эти части?
3. Какие ошибки AI допустил?
4. Что ты изменил вручную?

---$m5_l9_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 10: Final spec
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 10
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 10
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l10_b1_type$theory$m5_l10_b1_type$, $m5_l10_b1_title$Варианты$m5_l10_b1_title$, $m5_l10_b1_content$Выбери один финальный проект:

1. Helpdesk с AI-классификацией заявок.
2. Учебная платформа с AI-помощником по урокам.
3. Финансовый трекер с AI-анализом расходов.
4. CRM с AI-резюме по клиентам.
5. Документный ассистент с RAG.
6. Трекер задач с AI-планировщиком.$m5_l10_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l10_b2_type$theory$m5_l10_b2_type$, $m5_l10_b2_title$Требования$m5_l10_b2_title$, $m5_l10_b2_content$Минимум финального проекта:

```text
FastAPI
PostgreSQL
SQLAlchemy
Alembic
Auth
CRUD
Тесты
Docker/Compose
CI
AI-фича
README
Деплой
```$m5_l10_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l10_b3_type$practice$m5_l10_b3_type$, $m5_l10_b3_title$API spec$m5_l10_b3_title$, $m5_l10_b3_content$### Условие

Опиши API-контракт:

- endpoints;
- методы;
- request body;
- response body;
- status codes;
- auth requirements.$m5_l10_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l10_b4_type$practice$m5_l10_b4_type$, $m5_l10_b4_title$DB spec$m5_l10_b4_title$, $m5_l10_b4_content$### Условие

Опиши схему БД:

- таблицы;
- поля;
- ключи;
- связи;
- индексы;
- ограничения.$m5_l10_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l10_b5_type$practice$m5_l10_b5_type$, $m5_l10_b5_title$AI spec$m5_l10_b5_title$, $m5_l10_b5_content$### Условие

Опиши AI-фичу:

- что делает модель;
- какие данные получает;
- какой формат ответа;
- что делать при ошибке;
- какие данные нельзя отправлять;
- как проверяется качество ответа.$m5_l10_b5_content$, NULL, NULL::jsonb),
  (6, $m5_l10_b6_type$project$m5_l10_b6_type$, $m5_l10_b6_title$Approval$m5_l10_b6_title$, $m5_l10_b6_content$Отправь ТЗ на проверку до начала разработки.

---$m5_l10_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 11: Sprint 1
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 11
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 11
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l11_b1_type$theory$m5_l11_b1_type$, $m5_l11_b1_title$Plan$m5_l11_b1_title$, $m5_l11_b1_content$Цель спринта 1 — рабочий backend без AI-фичи.

Готово, если:

- API запускается;
- есть БД;
- миграции работают;
- CRUD работает;
- auth работает;
- тесты проходят.$m5_l11_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l11_b2_type$practice$m5_l11_b2_type$, $m5_l11_b2_title$Models$m5_l11_b2_title$, $m5_l11_b2_content$### Условие

Создай ORM-модели по ТЗ. Добавь связи и ограничения.$m5_l11_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l11_b3_type$practice$m5_l11_b3_type$, $m5_l11_b3_title$Migrations$m5_l11_b3_title$, $m5_l11_b3_content$### Условие

Создай и примени миграции. Проверь, что новая база создаётся с нуля.$m5_l11_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l11_b4_type$practice$m5_l11_b4_type$, $m5_l11_b4_title$CRUD$m5_l11_b4_title$, $m5_l11_b4_content$### Условие

Реализуй CRUD основного ресурса. Пользователь должен работать только со своими данными.$m5_l11_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l11_b5_type$practice$m5_l11_b5_type$, $m5_l11_b5_title$Auth$m5_l11_b5_title$, $m5_l11_b5_content$### Условие

Добавь регистрацию, логин, получение текущего пользователя и защиту endpoints.$m5_l11_b5_content$, NULL, NULL::jsonb),
  (6, $m5_l11_b6_type$practice$m5_l11_b6_type$, $m5_l11_b6_title$Tests$m5_l11_b6_title$, $m5_l11_b6_content$### Условие

Напиши минимум 12 тестов. Тесты должны проверять успешные и ошибочные сценарии.$m5_l11_b6_content$, NULL, NULL::jsonb),
  (7, $m5_l11_b7_type$project$m5_l11_b7_type$, $m5_l11_b7_title$Review$m5_l11_b7_title$, $m5_l11_b7_content$Отправь Sprint 1 на ревью.

---$m5_l11_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 12: Sprint 2
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 12
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 12
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l12_b1_type$theory$m5_l12_b1_type$, $m5_l12_b1_title$AI plan$m5_l12_b1_title$, $m5_l12_b1_content$AI-фича должна решать понятную задачу, а не быть украшением.

Примеры:

- классифицировать заявку;
- кратко резюмировать клиента;
- отвечать по базе знаний;
- предложить план задачи;
- извлечь структуру из текста.$m5_l12_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l12_b2_type$practice$m5_l12_b2_type$, $m5_l12_b2_title$Provider$m5_l12_b2_title$, $m5_l12_b2_content$### Условие

Создай слой `ai_provider.py`. Он должен скрывать детали конкретного провайдера.

```python
class AIProvider:
    def generate(self, prompt: str) -> str:
        ...
```

Так проект проще тестировать и менять.$m5_l12_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l12_b3_type$practice$m5_l12_b3_type$, $m5_l12_b3_title$AI endpoint$m5_l12_b3_title$, $m5_l12_b3_content$### Условие

Добавь endpoint для AI-фичи. Он должен:

- проверять auth;
- валидировать вход;
- ограничивать длину текста;
- вызывать AI-provider;
- возвращать структурированный ответ;
- обрабатывать ошибки.$m5_l12_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l12_b4_type$practice$m5_l12_b4_type$, $m5_l12_b4_title$RAG/tool$m5_l12_b4_title$, $m5_l12_b4_content$### Условие

Если проект RAG: добавь поиск по документам. Если проект агентный: добавь один безопасный tool.

Tool не должен выполнять опасные операции без подтверждения.$m5_l12_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l12_b5_type$practice$m5_l12_b5_type$, $m5_l12_b5_title$Tests$m5_l12_b5_title$, $m5_l12_b5_content$### Условие

Тестируй AI-фичу через mock. Не делай реальные платные API-запросы в unit-тестах.

Проверь:

- успешный ответ;
- ошибка провайдера;
- слишком длинный ввод;
- нет токена;
- неправильный формат ответа.$m5_l12_b5_content$, NULL, NULL::jsonb),
  (6, $m5_l12_b6_type$project$m5_l12_b6_type$, $m5_l12_b6_title$Safety$m5_l12_b6_title$, $m5_l12_b6_content$Проверь AI-фичу на безопасность:

- секреты не отправляются в модель;
- персональные данные минимизированы;
- prompt injection учитывается;
- есть fallback;
- ответ модели валидируется.$m5_l12_b6_content$, NULL, NULL::jsonb),
  (7, $m5_l12_b7_type$project$m5_l12_b7_type$, $m5_l12_b7_title$Review$m5_l12_b7_title$, $m5_l12_b7_content$Отправь Sprint 2 на ревью.

---$m5_l12_b7_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 13: VPS
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 13
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 13
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m5_l13_t4_title$Firewall$m5_l13_t4_title$, $m5_l13_t4_statement$### Условие

Открой только нужные порты:

```text
22  SSH
80  HTTP
443 HTTPS
```

Порт приложения `8000` наружу обычно не открывают. Его закрывает Nginx как reverse proxy.$m5_l13_t4_statement$, $m5_l13_t4_starter$$m5_l13_t4_starter$, $m5_l13_t4_solution$$m5_l13_t4_solution$, 2, 50, $m5_l13_t4_topic$Месяц 5. Финальный проект, AI и деплой — VPS$m5_l13_t4_topic$, $m5_l13_t4_lang$python$m5_l13_t4_lang$, $m5_l13_t4_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m5_l13_t4_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 13
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m5_l13_ttitle_4$Firewall$m5_l13_ttitle_4$
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 13
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m5_l13_test_4_1_title$Firewall$m5_l13_test_4_1_title$, $m5_l13_test_4_1_input$$m5_l13_test_4_1_input$, $m5_l13_test_4_1_expected$22  SSH
80  HTTP
443 HTTPS$m5_l13_test_4_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 13
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l13_b1_type$theory$m5_l13_b1_type$, $m5_l13_b1_title$Что такое VPS$m5_l13_b1_title$, $m5_l13_b1_content$VPS — виртуальный сервер. На нём можно запустить backend, базу, nginx и docker compose.

В курсе используем минимальный production-like деплой, а не сложную Kubernetes-инфраструктуру.$m5_l13_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l13_b2_type$theory$m5_l13_b2_type$, $m5_l13_b2_title$SSH$m5_l13_b2_title$, $m5_l13_b2_content$SSH — способ подключиться к серверу.

```bash
ssh user@server_ip
```

Лучше использовать SSH-ключи, а не пароль.$m5_l13_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l13_b3_type$practice$m5_l13_b3_type$, $m5_l13_b3_title$User$m5_l13_b3_title$, $m5_l13_b3_content$### Условие

Создай отдельного пользователя для проекта. Не работай постоянно под root.$m5_l13_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l13_b4_type$practice$m5_l13_b4_type$, $m5_l13_b4_title$Firewall$m5_l13_b4_title$, $m5_l13_b4_content$### Условие

Открой только нужные порты:

```text
22  SSH
80  HTTP
443 HTTPS
```

Порт приложения `8000` наружу обычно не открывают. Его закрывает Nginx как reverse proxy.$m5_l13_b4_content$, $m5_l13_b4_task_title$Firewall$m5_l13_b4_task_title$, NULL::jsonb),
  (5, $m5_l13_b5_type$practice$m5_l13_b5_type$, $m5_l13_b5_title$Updates$m5_l13_b5_title$, $m5_l13_b5_content$### Условие

Обнови пакеты сервера и установи Docker/Compose по инструкции провайдера или официальной документации.$m5_l13_b5_content$, NULL, NULL::jsonb),
  (6, $m5_l13_b6_type$practice$m5_l13_b6_type$, $m5_l13_b6_title$Checklist$m5_l13_b6_title$, $m5_l13_b6_content$### Условие

Сервер готов, если:

- вход по SSH работает;
- есть отдельный пользователь;
- firewall включён;
- открыты только 22/80/443;
- Docker установлен;
- проект можно склонировать.

---$m5_l13_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 14: Nginx SSL
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 14
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 14
), task_seed(title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy) AS (
  VALUES
  ($m5_l14_t2_title$Domain$m5_l14_t2_title$, $m5_l14_t2_statement$### Условие

Настрой A-запись домена на IP сервера.

```text
api.example.com → server_ip
```$m5_l14_t2_statement$, $m5_l14_t2_starter$$m5_l14_t2_starter$, $m5_l14_t2_solution$$m5_l14_t2_solution$, 2, 50, $m5_l14_t2_topic$Месяц 5. Финальный проект, AI и деплой — Nginx SSL$m5_l14_t2_topic$, $m5_l14_t2_lang$python$m5_l14_t2_lang$, $m5_l14_t2_policy${"language":"python","emptySourceMessage":"Код пока пуст. Добавьте решение и запустите проверку снова.","ignoreCommentOnlyLines":true,"hints":[],"ai_hint_config":{"mode":"socratic","no_full_solution":true}}$m5_l14_t2_policy$::jsonb)
)
INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language, source_policy, is_published)
SELECT lr.lesson_id, ts.title, ts.statement_md, ts.starter_code, ts.solution_code, ts.difficulty, ts.xp_reward, ts.topic, ts.language, ts.source_policy, TRUE
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 14
), target_tasks AS (
  SELECT t.id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
  WHERE t.title IN (
    $m5_l14_ttitle_2$Domain$m5_l14_ttitle_2$
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
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 14
), task_lookup AS (
  SELECT t.id AS task_id, t.title
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), test_seed(task_title, input_data, expected_output, is_hidden, position) AS (
  VALUES
  ($m5_l14_test_2_1_title$Domain$m5_l14_test_2_1_title$, $m5_l14_test_2_1_input$$m5_l14_test_2_1_input$, $m5_l14_test_2_1_expected$api.example.com → server_ip$m5_l14_test_2_1_expected$, FALSE, 1)
)
INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
SELECT tl.task_id, ts.input_data, ts.expected_output, ts.is_hidden, ts.position
FROM test_seed ts
JOIN task_lookup tl ON tl.title = ts.task_title
ORDER BY tl.task_id, ts.position;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 14
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l14_b1_type$theory$m5_l14_b1_type$, $m5_l14_b1_title$Reverse proxy$m5_l14_b1_title$, $m5_l14_b1_content$Nginx принимает запросы на 80/443 и проксирует их в приложение.

```text
client → nginx → fastapi:8000
```

Так приложение не торчит напрямую в интернет.$m5_l14_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l14_b2_type$practice$m5_l14_b2_type$, $m5_l14_b2_title$Domain$m5_l14_b2_title$, $m5_l14_b2_content$### Условие

Настрой A-запись домена на IP сервера.

```text
api.example.com → server_ip
```$m5_l14_b2_content$, $m5_l14_b2_task_title$Domain$m5_l14_b2_task_title$, NULL::jsonb),
  (3, $m5_l14_b3_type$practice$m5_l14_b3_type$, $m5_l14_b3_title$Nginx config$m5_l14_b3_title$, $m5_l14_b3_content$### Условие

Минимальная идея конфига:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```$m5_l14_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l14_b4_type$practice$m5_l14_b4_type$, $m5_l14_b4_title$SSL$m5_l14_b4_title$, $m5_l14_b4_content$### Условие

Подключи HTTPS-сертификат через certbot или другой инструмент провайдера. После настройки API должен быть доступен по `https://`.$m5_l14_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l14_b5_type$practice$m5_l14_b5_type$, $m5_l14_b5_title$Checklist$m5_l14_b5_title$, $m5_l14_b5_content$### Условие

Готово, если:

- домен ведёт на сервер;
- Nginx проксирует запросы;
- `/health` доступен через домен;
- HTTPS работает;
- порт 8000 не открыт наружу.

---$m5_l14_b5_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 15: Autodeploy
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 15
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 15
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l15_b1_type$theory$m5_l15_b1_type$, $m5_l15_b1_title$Strategy$m5_l15_b1_title$, $m5_l15_b1_content$Простой деплой:

```text
push в main → CI запускает тесты → сервер получает новую версию → docker compose up -d --build
```

Сначала тесты, потом деплой.$m5_l15_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l15_b2_type$theory$m5_l15_b2_type$, $m5_l15_b2_title$Secrets$m5_l15_b2_title$, $m5_l15_b2_content$Секреты CI:

```text
SSH_HOST
SSH_USER
SSH_KEY
DEPLOY_PATH
```

Секреты нельзя хранить в репозитории.$m5_l15_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l15_b3_type$practice$m5_l15_b3_type$, $m5_l15_b3_title$SSH deploy$m5_l15_b3_title$, $m5_l15_b3_content$### Условие

Настрой workflow, который подключается к серверу по SSH и выполняет команды деплоя.$m5_l15_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l15_b4_type$practice$m5_l15_b4_type$, $m5_l15_b4_title$Compose pull$m5_l15_b4_title$, $m5_l15_b4_content$### Условие

Минимальные команды на сервере:

```bash
cd /path/to/project
git pull
docker compose up -d --build
```$m5_l15_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l15_b5_type$theory$m5_l15_b5_type$, $m5_l15_b5_title$Rollback$m5_l15_b5_title$, $m5_l15_b5_content$Rollback — возврат к прошлой рабочей версии. Минимум: знать предыдущий commit и уметь откатиться.

В реальном production нужен более строгий процесс.$m5_l15_b5_content$, NULL, NULL::jsonb),
  (6, $m5_l15_b6_type$practice$m5_l15_b6_type$, $m5_l15_b6_title$Checklist$m5_l15_b6_title$, $m5_l15_b6_content$### Условие

Автодеплой готов, если:

- CI запускает тесты;
- деплой идёт только после успешных тестов;
- секреты хранятся в CI;
- сервер обновляет проект;
- `/health` работает после деплоя.

---$m5_l15_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

-- Module 5, lesson 16: Defense
WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 16
)
UPDATE lesson_blocks lb
SET is_published = FALSE,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id;

WITH lesson_ref AS (
  SELECT l.id AS lesson_id
  FROM lessons l
  JOIN modules m ON m.id = l.module_id
  JOIN courses c ON c.id = m.course_id
  WHERE c.slug = 'python-zero' AND m.position = 5 AND l.position = 16
), task_lookup AS (
  SELECT t.title, t.id AS task_id
  FROM tasks t
  JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
), block_seed(position, block_type, title, content_md, task_title, quiz_payload) AS (
  VALUES
  (1, $m5_l16_b1_type$project$m5_l16_b1_type$, $m5_l16_b1_title$Demo$m5_l16_b1_title$, $m5_l16_b1_content$Покажи проект:

- ссылка на API/docs;
- регистрация/логин;
- CRUD;
- AI-фича;
- один ошибочный сценарий;
- тесты;
- CI;
- деплой.$m5_l16_b1_content$, NULL, NULL::jsonb),
  (2, $m5_l16_b2_type$project$m5_l16_b2_type$, $m5_l16_b2_title$Code$m5_l16_b2_title$, $m5_l16_b2_content$Отправь репозиторий на code review.$m5_l16_b2_content$, NULL, NULL::jsonb),
  (3, $m5_l16_b3_type$project$m5_l16_b3_type$, $m5_l16_b3_title$Tests$m5_l16_b3_title$, $m5_l16_b3_content$Покажи, что тесты проходят. Объясни, какие сценарии они проверяют.$m5_l16_b3_content$, NULL, NULL::jsonb),
  (4, $m5_l16_b4_type$summary$m5_l16_b4_type$, $m5_l16_b4_title$Deploy$m5_l16_b4_title$, $m5_l16_b4_content$Проверь:

- домен работает;
- HTTPS работает;
- `/health` отвечает;
- docs доступны или намеренно закрыты;
- секреты не в репозитории;
- CI зелёный.$m5_l16_b4_content$, NULL, NULL::jsonb),
  (5, $m5_l16_b5_type$summary$m5_l16_b5_type$, $m5_l16_b5_title$Questions$m5_l16_b5_title$, $m5_l16_b5_content$Будь готов ответить:

1. Почему такая схема БД?
2. Где транзакции?
3. Какие индексы нужны?
4. Как работает auth?
5. Как тестируется AI-фича?
6. Что будет, если AI API недоступен?
7. Как деплоится проект?
8. Какие риски безопасности?
9. Что бы ты улучшил дальше?$m5_l16_b5_content$, NULL, NULL::jsonb),
  (6, $m5_l16_b6_type$summary$m5_l16_b6_type$, $m5_l16_b6_title$Final score$m5_l16_b6_title$, $m5_l16_b6_content$---

# Итог курса

Выпускник должен иметь финальный проект, который можно показать как backend-портфолио:

```text
FastAPI
PostgreSQL
SQLAlchemy
Alembic
Auth
PyTest
Docker Compose
CI/CD
AI feature
VPS deploy
README
```

Главный критерий: ученик не просто запускает проект, а может объяснить, почему он устроен именно так.
# Автопроверка и AI-рубрики

Этот файл нужен разработчикам платформы, методистам и менторам. Ученику его не показывать.

## 1. Типы проверок

| Тип | Где используется | Как проверять |
|---|---|---|
| Python stdout | базовые задачи | точный stdout |
| Python unit | функции/классы | импорт решения + pytest |
| SQL runner | SQL-запросы | результат запроса |
| HTTP runner | FastAPI | HTTP-запросы к приложению |
| YAML-check | CI/CD | структура workflow |
| Docker-check | Dockerfile/Compose | build/run/health |
| AI-check | проекты, архитектура | рубрика |
| Mentor-review | финальные проекты | выборочная ручная проверка |

## 2. Правила stdout

Игнорировать:

- финальный перенос строки;
- пробелы в конце строк.

Не игнорировать:

- лишний текст;
- лишние строки;
- неправильный регистр;
- лишние пробелы внутри строки;
- другой порядок, если в задаче порядок фиксирован.

## 3. Python-задачи

Для задач первых месяцев использовать шаблоны кода. Чем дальше курс, тем меньше шаблонов.

Пример тестов для функции:

```python
def test_find_index_first():
    assert find_index([1, 2, 3], 1) == 0

def test_find_index_last():
    assert find_index([1, 2, 3], 3) == 2

def test_find_index_missing():
    assert find_index([1, 2, 3], 10) == -1
```

## 4. SQL-задачи

Для SQL-runner перед каждым запуском:

1. создать учебную БД;
2. загрузить fixture-данные;
3. выполнить запрос ученика;
4. сравнить результат.

Проверять:

- строки;
- колонки;
- порядок, если есть `ORDER BY`;
- отсутствие запрещённых команд.

Для задач на `JOIN` и `GROUP BY` обязательно иметь скрытые тесты с изменёнными данными.

## 5. HTTP-задачи FastAPI

Проверка должна запускать приложение и отправлять HTTP-запросы.

Минимальные проверки:

```text
GET /health → 200
POST /tasks → 201/200
GET /tasks → список
GET /tasks/{id} → объект
PATCH /tasks/{id} → изменение
DELETE /tasks/{id} → 204
GET unknown id → 404
```

Для auth:

```text
без токена → 401
с токеном → 200
чужие данные → 403/404
пароль не возвращается
```

## 6. Docker-check

Проверка:

```bash
docker build -t project-test .
docker run -p 8000:8000 project-test
curl /health
```

Для Compose:

```bash
docker compose up --build -d
curl /health
docker compose down -v
```

## 7. AI-подсказка

AI-подсказка не выдаёт полное решение до нескольких попыток.

### Уровень 1

Объяснить, что проверить.

```text
Проверь, преобразуешь ли ты input() в число перед сложением.
```

### Уровень 2

Указать место ошибки.

```text
Проблема в строках, где ты читаешь a и b. Сейчас это строки, не числа.
```

### Уровень 3

Дать маленький фрагмент.

```python
a = int(input())
```

### Уровень 4

После сдачи показать эталон и разбор.

## 8. AI-check проектов

AI должен оценивать по рубрике и возвращать структурированный результат:

```json
{
  "score": 82,
  "critical_issues": [],
  "strengths": [],
  "improvements": [],
  "questions_for_student": [],
  "verdict": "pass"
}
```

AI не должен:

- ставить оценку без критериев;
- переписывать весь проект;
- игнорировать безопасность;
- хвалить неработающий код;
- пропускать hardcoded secrets.

## 9. Рубрика финального проекта

| Критерий | Баллы |
|---|---:|
| API и бизнес-логика | 15 |
| БД, миграции, индексы | 15 |
| Auth и безопасность | 15 |
| AI-интеграция | 15 |
| Тесты | 10 |
| Docker/Compose/CI | 10 |
| Деплой/VPS/HTTPS | 10 |
| README и документация | 5 |
| Защита и объяснение | 5 |

Критичные ошибки, которые блокируют зачёт:

- проект не запускается;
- нет БД при требовании БД;
- пароли хранятся открыто;
- секреты в репозитории;
- чужие данные доступны без проверки владельца;
- AI-фича отправляет секреты в модель;
- ученик не может объяснить собственный код.

## 10. Античит

Сигналы риска:

- резкий скачок сложности кода без промежуточных попыток;
- ученик не может объяснить код;
- одинаковые проекты у нескольких учеников;
- много неиспользуемых абстракций;
- зависимости, которые не объяснены в README;
- код с комментариями/названиями, не соответствующими стилю курса.

Что делать:

1. Не обвинять сразу.
2. Дать 5 вопросов по коду.
3. Попросить изменить часть функциональности вживую.
4. Попросить написать маленькую похожую функцию без AI.
5. При необходимости отправить на ручную защиту.
# Операционная модель потока на 200 учеников

## Команда

| Роль | Количество | Ответственность |
|---|---:|---|
| Главный преподаватель | 1 | программа, вебинары, сложные разборы |
| Методист | 1 | качество уроков, правки, аналитика |
| Технический лидер | 1 | раннеры, автотесты, DevOps sandbox |
| Менторы | 7–8 | группы по 25–30 учеников |
| Проверяющие проектов | 2–3 | ревью проектов и защит |
| Support | 1–2 | доступы, платформенные вопросы |

## Нагрузка недели

```text
2 учебных занятия
1 практический разбор
1 Q&A
домашка
автозадачи
проектный спринт раз в месяц
```

## Группы

200 учеников делятся на 8 групп по 25 человек.

Каждая группа имеет:

- ментора;
- чат;
- еженедельный слот Q&A;
- таблицу риска;
- проектные дедлайны.

## Метрики риска

Ученик попадает в риск, если:

- не заходил 5 дней;
- не решил базовые задачи урока;
- открыл много подсказок, но не сдал задачи;
- провалил контрольную задачу;
- не сдал проектный milestone;
- задаёт вопросы уровня «ничего не понял» после нескольких тем;
- не может объяснить свой код.

## Реакция на риск

| Риск | Действие |
|---|---|
| не заходил | автонапоминание + сообщение ментора |
| не решает задачи | remedial-блок |
| провалил тему | диагностика на 5 задач |
| застрял в проекте | 20-минутный созвон или письменный план |
| подозрение на копирование | короткая защита кода |

## SLA менторов

| Событие | SLA |
|---|---:|
| вопрос по уроку | до 24 часов |
| критический блокер проекта | до 12 часов |
| проверка домашки | 48–72 часа |
| проверка проекта | до 5 дней |

## Аналитика платформы

Отслеживать:

- процент прохождения каждого шага;
- среднее число попыток по задаче;
- процент открытий подсказок;
- задачи с провалом выше 40%;
- время до первой успешной задачи;
- скорость ответа менторов;
- долю учеников сданного проекта месяца;
- активность по группам.

## Контроль качества материалов

Каждую неделю методист смотрит:

1. Где ученики чаще всего падают.
2. Какие формулировки вызывают вопросы.
3. Какие автотесты слишком строгие или слабые.
4. Где AI-подсказка даёт слишком много.
5. Где менторы отвечают одно и то же много раз.

По итогам недели обновляются:

- FAQ;
- подсказки;
- скрытые тесты;
- формулировки задач;
- remedial-блоки.

## Ритм проектов

Каждый месяц завершается проектом:

1. Месяц 1 — CLI Task Manager.
2. Месяц 2 — async bot/service.
3. Месяц 3 — DB + Python script.
4. Месяц 4 — FastAPI CRUD service.
5. Месяц 5 — финальный deployed AI backend.

Без проекта месяц не закрывается.

## Почему курс не проходится за пару недель

Даже если ученик быстро решает автозадачи, сертификат требует:

- проекты;
- ревью;
- тесты;
- деплой;
- объяснение кода;
- защиту;
- отсутствие критичных проблем безопасности.

Автозадачи проверяют навык. Проекты проверяют разработку.$m5_l16_b6_content$, NULL, NULL::jsonb)
), resolved AS (
  SELECT bs.position, bs.block_type, bs.title, bs.content_md, tl.task_id, bs.quiz_payload
  FROM block_seed bs
  LEFT JOIN task_lookup tl ON tl.title = bs.task_title
)
INSERT INTO lesson_blocks(lesson_id, block_type, title, content_md, task_id, quiz_payload, position, is_published)
SELECT lr.lesson_id, r.block_type, r.title, r.content_md, r.task_id, r.quiz_payload, r.position, TRUE
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

