-- 013_python_lesson_quiz_and_copy_refresh.sql
--
-- Purpose:
-- 1) Replace static summary answers with an interactive final quiz (dropdown-ready payload).
-- 2) Clarify the wording of the "Почему получилось 105?" fix-code task.
-- 3) Keep all updates scoped to lesson 1 of course python-zero.

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero'
      AND m.position = 1
      AND l.position = 1
)
UPDATE tasks t
SET statement_md = $$
Исправьте программу так, чтобы она складывала **числа**, а не склеивала строки.

Что сейчас не так:
- `input()` возвращает текст;
- поэтому `a + b` даёт склейку строк (`10` и `5` превращаются в `105`).

Что нужно сделать:
1. Прочитайте два значения.
2. Преобразуйте каждое значение в число через `int(...)`.
3. Выведите сумму.

Входные данные:
- две строки, в каждой одно целое число.

Выходные данные:
- одно целое число: сумма введённых значений.

Пример:
Ввод:
10
5

Вывод:
15
$$,
    updated_at = NOW()
FROM lesson_ref lr
WHERE t.lesson_id = lr.lesson_id
  AND t.title = 'Почему получилось 105?';

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero'
      AND m.position = 1
      AND l.position = 1
)
UPDATE lesson_blocks lb
SET content_md = $$
Выберите вариант в каждом вопросе и нажмите «Проверить ответ».
$$,
    block_type = 'quiz',
    title = 'Итоговый тест',
    quiz_payload = jsonb_build_object(
        'questions', jsonb_build_array(
            jsonb_build_object(
                'id', 'q1',
                'question', 'Что делает команда print()?',
                'options', jsonb_build_array(
                    jsonb_build_object('id', 'A', 'text', 'Получает данные от пользователя'),
                    jsonb_build_object('id', 'B', 'text', 'Выводит данные на экран'),
                    jsonb_build_object('id', 'C', 'text', 'Создаёт переменную'),
                    jsonb_build_object('id', 'D', 'text', 'Преобразует текст в число')
                ),
                'correctOptionId', 'B'
            ),
            jsonb_build_object(
                'id', 'q2',
                'question', 'Что выведет код: print(2 + 3)?',
                'options', jsonb_build_array(
                    jsonb_build_object('id', 'A', 'text', '2 + 3'),
                    jsonb_build_object('id', 'B', 'text', '5'),
                    jsonb_build_object('id', 'C', 'text', '"5"'),
                    jsonb_build_object('id', 'D', 'text', 'Ошибку')
                ),
                'correctOptionId', 'B'
            ),
            jsonb_build_object(
                'id', 'q3',
                'question', 'Что выведет код: print("2 + 3")?',
                'options', jsonb_build_array(
                    jsonb_build_object('id', 'A', 'text', '5'),
                    jsonb_build_object('id', 'B', 'text', '2 + 3'),
                    jsonb_build_object('id', 'C', 'text', 'Ошибку'),
                    jsonb_build_object('id', 'D', 'text', 'Ничего')
                ),
                'correctOptionId', 'B'
            ),
            jsonb_build_object(
                'id', 'q4',
                'question', 'Что делает строка: name = input()?',
                'options', jsonb_build_array(
                    jsonb_build_object('id', 'A', 'text', 'Выводит имя на экран'),
                    jsonb_build_object('id', 'B', 'text', 'Считывает ввод и сохраняет его в переменную name'),
                    jsonb_build_object('id', 'C', 'text', 'Преобразует имя в число'),
                    jsonb_build_object('id', 'D', 'text', 'Удаляет переменную name')
                ),
                'correctOptionId', 'B'
            ),
            jsonb_build_object(
                'id', 'q5',
                'question', 'Как правильно получить целое число от пользователя?',
                'options', jsonb_build_array(
                    jsonb_build_object('id', 'A', 'text', 'age = input()'),
                    jsonb_build_object('id', 'B', 'text', 'age = int(input())'),
                    jsonb_build_object('id', 'C', 'text', 'age = print(input())'),
                    jsonb_build_object('id', 'D', 'text', 'age = text(input())')
                ),
                'correctOptionId', 'B'
            ),
            jsonb_build_object(
                'id', 'q6',
                'question', 'Почему код a = input(); b = input(); print(a + b) может дать 105?',
                'options', jsonb_build_array(
                    jsonb_build_object('id', 'A', 'text', 'Нельзя использовать две переменные'),
                    jsonb_build_object('id', 'B', 'text', 'input() возвращает текст, и + склеивает строки'),
                    jsonb_build_object('id', 'C', 'text', 'print() нельзя использовать с +'),
                    jsonb_build_object('id', 'D', 'text', 'Нужно написать print(input())')
                ),
                'correctOptionId', 'B'
            )
        )
    ),
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id
  AND lb.position = 24;
