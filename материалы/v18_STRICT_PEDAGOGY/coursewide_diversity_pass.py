#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from fix_course_quality import independent_audit, update_reports, write_quality_audit


ROOT = Path(__file__).resolve().parent
COURSE_FILE = ROOT / "course_import.json"


TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


FORBIDDEN_BODY_REPLACEMENTS = {
    "Для темы `": "В уроке `",
    " это означает отдельное действие шага `": " это отрабатывается в шаге `",
    "Теперь разберись с темой `": "Теперь разбери `",
    "Практика по теме `": "Практика `",
    "проверяемый результат": "конкретный итог",
    "проверяемым результатом": "конкретным итогом",
    "проверяемого результата": "конкретного итога",
    "проверяемый артефакт": "сданный файл",
    "проверяемом артефакте": "сданном файле",
    "собери рабочий пример по теме": "собери отдельную работу для урока",
    "собери маленькую лабу по теме": "собери маленькую работу для урока",
    "оформи SQL-решение по теме": "оформи SQL-работу для урока",
    "зафиксируй HTTP-контракт по теме": "зафиксируй HTTP-контракт урока",
    "реализуй HTTP-контракт `": "реализуй endpoint `",
}


SELF_CHECK = (
    "### Самопроверка перед отправкой\n"
    "1. Запусти команду из условия или выполни ручную проверку.\n"
    "2. Сравни фактический вывод, файл или HTTP-ответ с ожидаемым форматом.\n"
    "3. Проверь один отрицательный случай: пустое значение, ошибка команды, неверный путь или отсутствие строки.\n"
    "4. Убери лишний текст из результата, если условие просит точный вывод.\n"
)


SCHEMA_PACKS = {
    "ecommerce": {
        "name": "магазин",
        "schema": (
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, active INTEGER NOT NULL, city TEXT);\n"
            "CREATE TABLE products (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price INTEGER NOT NULL, stock INTEGER NOT NULL);\n"
            "CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, total INTEGER NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL);"
        ),
        "seed": (
            "INSERT INTO users VALUES (1,'Анна',1,'Москва'),(2,'Олег',0,'Казань'),(3,'Маша',1,NULL),(4,'Ира',1,'Москва');\n"
            "INSERT INTO products VALUES (1,'Клавиатура',3500,12),(2,'Мышь',1800,0),(3,'Монитор',12000,4),(4,'Кабель',600,30);\n"
            "INSERT INTO orders VALUES (1,1,5300,'paid','2026-01-10'),(2,1,600,'new','2026-01-12'),(3,3,12000,'paid','2026-01-15'),(4,4,1800,'cancelled','2026-01-18');"
        ),
        "hidden_seed": (
            "INSERT INTO users VALUES (1,'Анна',1,'Москва'),(2,'Олег',0,'Казань'),(3,'Маша',1,NULL),(4,'Ира',1,'Москва'),(5,'Павел',1,'Пермь');\n"
            "INSERT INTO products VALUES (1,'Клавиатура',3500,12),(2,'Мышь',1800,0),(3,'Монитор',12000,4),(4,'Кабель',600,30),(5,'Док-станция',9000,2);\n"
            "INSERT INTO orders VALUES (1,1,5300,'paid','2026-01-10'),(2,1,600,'new','2026-01-12'),(3,3,12000,'paid','2026-01-15'),(4,4,1800,'cancelled','2026-01-18'),(5,5,9000,'paid','2026-01-20');"
        ),
    },
    "library": {
        "name": "библиотека",
        "schema": (
            "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL, country TEXT);\n"
            "CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, author_id INTEGER, published_year INTEGER NOT NULL, price INTEGER NOT NULL);\n"
            "CREATE TABLE loans (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, reader TEXT NOT NULL, returned INTEGER NOT NULL);"
        ),
        "seed": (
            "INSERT INTO authors VALUES (1,'Толстой','RU'),(2,'Оруэлл','UK'),(3,'Ле Гуин','US');\n"
            "INSERT INTO books VALUES (1,'Война и мир',1,1869,900),(2,'1984',2,1949,500),(3,'Волшебник Земноморья',3,1968,650),(4,'Без автора',NULL,2020,300);\n"
            "INSERT INTO loans VALUES (1,1,'Анна',0),(2,2,'Олег',1),(3,3,'Маша',0);"
        ),
        "hidden_seed": (
            "INSERT INTO authors VALUES (1,'Толстой','RU'),(2,'Оруэлл','UK'),(3,'Ле Гуин','US'),(4,'Булгаков','RU');\n"
            "INSERT INTO books VALUES (1,'Война и мир',1,1869,900),(2,'1984',2,1949,500),(3,'Волшебник Земноморья',3,1968,650),(4,'Без автора',NULL,2020,300),(5,'Мастер и Маргарита',4,1967,700);\n"
            "INSERT INTO loans VALUES (1,1,'Анна',0),(2,2,'Олег',1),(3,3,'Маша',0),(4,5,'Ира',0);"
        ),
    },
    "school": {
        "name": "учебная платформа",
        "schema": (
            "CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);\n"
            "CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, track TEXT NOT NULL);\n"
            "CREATE TABLE enrollments (student_id INTEGER NOT NULL, course_id INTEGER NOT NULL, progress INTEGER NOT NULL, paid INTEGER NOT NULL);"
        ),
        "seed": (
            "INSERT INTO students VALUES (1,'Анна','Москва'),(2,'Олег','Казань'),(3,'Маша',NULL),(4,'Ира','Пермь');\n"
            "INSERT INTO courses VALUES (1,'Python Core','backend'),(2,'SQL','backend'),(3,'Design','frontend');\n"
            "INSERT INTO enrollments VALUES (1,1,80,1),(1,2,40,1),(2,1,25,0),(3,2,95,1),(4,3,10,1);"
        ),
        "hidden_seed": (
            "INSERT INTO students VALUES (1,'Анна','Москва'),(2,'Олег','Казань'),(3,'Маша',NULL),(4,'Ира','Пермь'),(5,'Павел','Самара');\n"
            "INSERT INTO courses VALUES (1,'Python Core','backend'),(2,'SQL','backend'),(3,'Design','frontend'),(4,'FastAPI','backend');\n"
            "INSERT INTO enrollments VALUES (1,1,80,1),(1,2,40,1),(2,1,25,0),(3,2,95,1),(4,3,10,1),(5,4,55,1);"
        ),
    },
    "workflow": {
        "name": "задачи проекта",
        "schema": (
            "CREATE TABLE projects (id INTEGER PRIMARY KEY, name TEXT NOT NULL, archived INTEGER NOT NULL);\n"
            "CREATE TABLE tasks (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, parent_id INTEGER, title TEXT NOT NULL, status TEXT NOT NULL, assignee TEXT);\n"
            "CREATE TABLE comments (id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL, author TEXT NOT NULL, body TEXT NOT NULL);"
        ),
        "seed": (
            "INSERT INTO projects VALUES (1,'Backend',0),(2,'Website',0),(3,'Archive',1);\n"
            "INSERT INTO tasks VALUES (1,1,NULL,'Auth','open','Анна'),(2,1,1,'JWT refresh','done',NULL),(3,2,NULL,'Landing','open','Олег'),(4,2,3,'SEO','review',NULL);\n"
            "INSERT INTO comments VALUES (1,1,'Анна','start'),(2,1,'Олег','review'),(3,3,'Маша','copy');"
        ),
        "hidden_seed": (
            "INSERT INTO projects VALUES (1,'Backend',0),(2,'Website',0),(3,'Archive',1),(4,'Mobile',0);\n"
            "INSERT INTO tasks VALUES (1,1,NULL,'Auth','open','Анна'),(2,1,1,'JWT refresh','done',NULL),(3,2,NULL,'Landing','open','Олег'),(4,2,3,'SEO','review',NULL),(5,4,NULL,'Push','open',NULL);\n"
            "INSERT INTO comments VALUES (1,1,'Анна','start'),(2,1,'Олег','review'),(3,3,'Маша','copy'),(4,5,'Ира','todo');"
        ),
    },
    "support": {
        "name": "поддержка",
        "schema": (
            "CREATE TABLE agents (id INTEGER PRIMARY KEY, name TEXT NOT NULL, active INTEGER NOT NULL);\n"
            "CREATE TABLE tickets (id INTEGER PRIMARY KEY, agent_id INTEGER, subject TEXT NOT NULL, priority INTEGER NOT NULL, status TEXT NOT NULL);\n"
            "CREATE TABLE replies (id INTEGER PRIMARY KEY, ticket_id INTEGER NOT NULL, minutes INTEGER NOT NULL);"
        ),
        "seed": (
            "INSERT INTO agents VALUES (1,'Анна',1),(2,'Олег',1),(3,'Маша',0);\n"
            "INSERT INTO tickets VALUES (1,1,'Оплата',3,'open'),(2,1,'Доступ',2,'closed'),(3,2,'IDE',5,'open'),(4,NULL,'Без агента',1,'new');\n"
            "INSERT INTO replies VALUES (1,1,15),(2,1,20),(3,2,7),(4,3,30);"
        ),
        "hidden_seed": (
            "INSERT INTO agents VALUES (1,'Анна',1),(2,'Олег',1),(3,'Маша',0),(4,'Ира',1);\n"
            "INSERT INTO tickets VALUES (1,1,'Оплата',3,'open'),(2,1,'Доступ',2,'closed'),(3,2,'IDE',5,'open'),(4,NULL,'Без агента',1,'new'),(5,4,'Docker',4,'open');\n"
            "INSERT INTO replies VALUES (1,1,15),(2,1,20),(3,2,7),(4,3,30),(5,5,40);"
        ),
    },
}


SQL_CARDS = {
    "select": [
        ("Список активных клиентов", "выведи `id`, `name`, `city` активных пользователей", "id, name, city", "SELECT id, name, city FROM users WHERE active = 1 ORDER BY id;", "ecommerce"),
        ("Каталог в наличии", "выведи товары, которые есть на складе", "id, title, stock", "SELECT id, title, stock FROM products WHERE stock > 0 ORDER BY title;", "ecommerce"),
        ("Книги с автором", "выведи книги, у которых указан автор", "id, title, author_id", "SELECT id, title, author_id FROM books WHERE author_id IS NOT NULL ORDER BY id;", "library"),
        ("Курсы backend", "выведи курсы backend-направления", "id, title", "SELECT id, title FROM courses WHERE track = 'backend' ORDER BY id;", "school"),
    ],
    "where": [
        ("Оплаченные заказы", "оставь только заказы со статусом `paid`", "id, user_id, total", "SELECT id, user_id, total FROM orders WHERE status = 'paid' ORDER BY id;", "ecommerce"),
        ("Дорогие книги", "найди книги дороже 600", "id, title, price", "SELECT id, title, price FROM books WHERE price > 600 ORDER BY price, id;", "library"),
        ("Прогресс выше половины", "найди записи с прогрессом 50 или выше", "student_id, course_id, progress", "SELECT student_id, course_id, progress FROM enrollments WHERE progress >= 50 ORDER BY student_id, course_id;", "school"),
        ("Открытые обращения", "оставь обращения в статусах `open` и `new`", "id, subject, status", "SELECT id, subject, status FROM tickets WHERE status IN ('open','new') ORDER BY priority DESC, id;", "support"),
    ],
    "order": [
        ("Топ товаров по цене", "верни два самых дорогих товара", "title, price", "SELECT title, price FROM products ORDER BY price DESC, title LIMIT 2;", "ecommerce"),
        ("Старые книги", "верни три самые ранние книги", "title, published_year", "SELECT title, published_year FROM books ORDER BY published_year, title LIMIT 3;", "library"),
        ("Лидеры прогресса", "верни три записи с максимальным progress", "student_id, course_id, progress", "SELECT student_id, course_id, progress FROM enrollments ORDER BY progress DESC, student_id LIMIT 3;", "school"),
        ("Срочные обращения", "верни два обращения с максимальным priority", "id, subject, priority", "SELECT id, subject, priority FROM tickets ORDER BY priority DESC, id LIMIT 2;", "support"),
    ],
    "pattern": [
        ("Поиск товара", "найди товары, где название содержит букву `о`", "id, title", "SELECT id, title FROM products WHERE title LIKE '%о%' ORDER BY id;", "ecommerce"),
        ("Книги по периоду", "найди книги между 1900 и 2020 годами", "id, title, published_year", "SELECT id, title, published_year FROM books WHERE published_year BETWEEN 1900 AND 2020 ORDER BY published_year, id;", "library"),
        ("Студенты без города", "найди студентов без указанного города", "id, name", "SELECT id, name FROM students WHERE city IS NULL ORDER BY id;", "school"),
        ("Тикеты набора статусов", "найди обращения в статусах `open` или `new`", "id, subject", "SELECT id, subject FROM tickets WHERE status IN ('open','new') ORDER BY id;", "support"),
    ],
    "aggregate": [
        ("Сумма заказов по пользователю", "посчитай общую сумму заказов по каждому пользователю", "user_id, total_sum", "SELECT user_id, SUM(total) AS total_sum FROM orders GROUP BY user_id ORDER BY user_id;", "ecommerce"),
        ("Книги по авторам", "посчитай книги по каждому автору", "author_id, books_count", "SELECT author_id, COUNT(*) AS books_count FROM books WHERE author_id IS NOT NULL GROUP BY author_id ORDER BY author_id;", "library"),
        ("Средний прогресс по курсу", "посчитай средний progress по каждому курсу", "course_id, avg_progress", "SELECT course_id, ROUND(AVG(progress), 1) AS avg_progress FROM enrollments GROUP BY course_id ORDER BY course_id;", "school"),
        ("Минуты по обращениям", "посчитай общее время ответов по каждому обращению", "ticket_id, minutes_sum", "SELECT ticket_id, SUM(minutes) AS minutes_sum FROM replies GROUP BY ticket_id ORDER BY ticket_id;", "support"),
    ],
    "having": [
        ("Пользователи с двумя заказами", "оставь пользователей, у которых минимум два заказа", "user_id, orders_count", "SELECT user_id, COUNT(*) AS orders_count FROM orders GROUP BY user_id HAVING COUNT(*) >= 2 ORDER BY user_id;", "ecommerce"),
        ("Авторы с книгами", "оставь авторов, у которых есть хотя бы одна книга", "author_id, books_count", "SELECT author_id, COUNT(*) AS books_count FROM books WHERE author_id IS NOT NULL GROUP BY author_id HAVING COUNT(*) >= 1 ORDER BY author_id;", "library"),
        ("Курсы с активностью", "оставь курсы, где записей больше одной", "course_id, enrollments_count", "SELECT course_id, COUNT(*) AS enrollments_count FROM enrollments GROUP BY course_id HAVING COUNT(*) > 1 ORDER BY course_id;", "school"),
        ("Тикеты с несколькими ответами", "оставь обращения, где два или больше ответа", "ticket_id, replies_count", "SELECT ticket_id, COUNT(*) AS replies_count FROM replies GROUP BY ticket_id HAVING COUNT(*) >= 2 ORDER BY ticket_id;", "support"),
    ],
    "join": [
        ("Заказы с именами", "соедини заказы с пользователями", "order_id, name, total", "SELECT orders.id AS order_id, users.name, orders.total FROM orders JOIN users ON users.id = orders.user_id ORDER BY orders.id;", "ecommerce"),
        ("Книги и авторы", "соедини книги с авторами", "title, name", "SELECT books.title, authors.name FROM books JOIN authors ON authors.id = books.author_id ORDER BY books.id;", "library"),
        ("Студенты и курсы", "соедини записи обучения со студентами и курсами", "student, course, progress", "SELECT students.name AS student, courses.title AS course, enrollments.progress FROM enrollments JOIN students ON students.id = enrollments.student_id JOIN courses ON courses.id = enrollments.course_id ORDER BY students.id, courses.id;", "school"),
        ("Обращения и агенты", "соедини обращения с назначенными агентами", "subject, agent", "SELECT tickets.subject, agents.name AS agent FROM tickets JOIN agents ON agents.id = tickets.agent_id ORDER BY tickets.id;", "support"),
    ],
    "left": [
        ("Пользователи без потери строк", "покажи всех пользователей и количество заказов", "name, orders_count", "SELECT users.name, COUNT(orders.id) AS orders_count FROM users LEFT JOIN orders ON orders.user_id = users.id GROUP BY users.id, users.name ORDER BY users.id;", "ecommerce"),
        ("Авторы без книг", "покажи всех авторов и количество книг", "name, books_count", "SELECT authors.name, COUNT(books.id) AS books_count FROM authors LEFT JOIN books ON books.author_id = authors.id GROUP BY authors.id, authors.name ORDER BY authors.id;", "library"),
        ("Курсы без записей", "покажи все курсы и количество записей", "title, enrollments_count", "SELECT courses.title, COUNT(enrollments.student_id) AS enrollments_count FROM courses LEFT JOIN enrollments ON enrollments.course_id = courses.id GROUP BY courses.id, courses.title ORDER BY courses.id;", "school"),
        ("Агенты и очередь", "покажи всех агентов и количество обращений", "name, tickets_count", "SELECT agents.name, COUNT(tickets.id) AS tickets_count FROM agents LEFT JOIN tickets ON tickets.agent_id = agents.id GROUP BY agents.id, agents.name ORDER BY agents.id;", "support"),
    ],
    "self": [
        ("Подзадачи", "соедини задачу с родительской задачей", "child, parent", "SELECT child.title AS child, parent.title AS parent FROM tasks AS child JOIN tasks AS parent ON parent.id = child.parent_id ORDER BY child.id;", "workflow"),
        ("Связанные обращения", "покажи обращения с тем же агентом, кроме самого обращения", "left_ticket, right_ticket", "SELECT a.subject AS left_ticket, b.subject AS right_ticket FROM tickets AS a JOIN tickets AS b ON a.agent_id = b.agent_id AND a.id < b.id ORDER BY a.id, b.id;", "support"),
        ("Парные задачи проекта", "найди пары задач внутри одного проекта", "left_task, right_task", "SELECT a.title AS left_task, b.title AS right_task FROM tasks AS a JOIN tasks AS b ON a.project_id = b.project_id AND a.id < b.id ORDER BY a.project_id, a.id, b.id;", "workflow"),
        ("Парные тикеты агента", "найди пары обращений у одного активного агента", "agent, first_ticket, second_ticket", "SELECT agents.name AS agent, a.subject AS first_ticket, b.subject AS second_ticket FROM tickets AS a JOIN tickets AS b ON a.agent_id = b.agent_id AND a.id < b.id JOIN agents ON agents.id = a.agent_id WHERE agents.active = 1 ORDER BY agents.id, a.id;", "support"),
    ],
    "subquery": [
        ("Заказы выше среднего", "найди заказы дороже среднего заказа", "id, total", "SELECT id, total FROM orders WHERE total > (SELECT AVG(total) FROM orders) ORDER BY total, id;", "ecommerce"),
        ("Книги дороже средней", "найди книги дороже средней цены", "id, title, price", "SELECT id, title, price FROM books WHERE price > (SELECT AVG(price) FROM books) ORDER BY price, id;", "library"),
        ("Лучше среднего прогресса", "найди записи с progress выше среднего", "student_id, course_id, progress", "SELECT student_id, course_id, progress FROM enrollments WHERE progress > (SELECT AVG(progress) FROM enrollments) ORDER BY progress, student_id;", "school"),
        ("Долгие ответы", "найди ответы дольше среднего", "id, ticket_id, minutes", "SELECT id, ticket_id, minutes FROM replies WHERE minutes > (SELECT AVG(minutes) FROM replies) ORDER BY minutes, id;", "support"),
    ],
    "cte": [
        ("Paid orders CTE", "вынеси оплаченные заказы в CTE", "user_id, paid_total", "WITH paid_orders AS (SELECT user_id, total FROM orders WHERE status = 'paid') SELECT user_id, SUM(total) AS paid_total FROM paid_orders GROUP BY user_id ORDER BY user_id;", "ecommerce"),
        ("Open tasks CTE", "вынеси открытые задачи в CTE", "project_id, open_count", "WITH open_tasks AS (SELECT project_id FROM tasks WHERE status = 'open') SELECT project_id, COUNT(*) AS open_count FROM open_tasks GROUP BY project_id ORDER BY project_id;", "workflow"),
        ("Backend enrollments CTE", "вынеси backend-курсы в CTE", "course_id, students_count", "WITH backend_courses AS (SELECT id FROM courses WHERE track = 'backend') SELECT enrollments.course_id, COUNT(*) AS students_count FROM enrollments JOIN backend_courses ON backend_courses.id = enrollments.course_id GROUP BY enrollments.course_id ORDER BY enrollments.course_id;", "school"),
        ("Priority tickets CTE", "вынеси важные обращения в CTE", "agent_id, priority_sum", "WITH priority_tickets AS (SELECT agent_id, priority FROM tickets WHERE priority >= 3) SELECT agent_id, SUM(priority) AS priority_sum FROM priority_tickets WHERE agent_id IS NOT NULL GROUP BY agent_id ORDER BY agent_id;", "support"),
    ],
    "window": [
        ("Ранг заказов пользователя", "пронумеруй заказы внутри каждого пользователя", "user_id, total, rn", "SELECT user_id, total, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC, id) AS rn FROM orders ORDER BY user_id, rn;", "ecommerce"),
        ("Ранг книг по цене", "пронумеруй книги внутри автора по цене", "author_id, title, rn", "SELECT author_id, title, ROW_NUMBER() OVER (PARTITION BY author_id ORDER BY price DESC, id) AS rn FROM books WHERE author_id IS NOT NULL ORDER BY author_id, rn;", "library"),
        ("Ранг прогресса", "пронумеруй студентов внутри курса по progress", "course_id, student_id, rn", "SELECT course_id, student_id, ROW_NUMBER() OVER (PARTITION BY course_id ORDER BY progress DESC, student_id) AS rn FROM enrollments ORDER BY course_id, rn;", "school"),
        ("Ранг тикетов агента", "пронумеруй обращения внутри каждого агента по приоритету", "agent_id, subject, rn", "SELECT agent_id, subject, ROW_NUMBER() OVER (PARTITION BY agent_id ORDER BY priority DESC, id) AS rn FROM tickets WHERE agent_id IS NOT NULL ORDER BY agent_id, rn;", "support"),
    ],
    "dml": [
        ("Новый товар", "добавь товар и выведи каталог с ценой до 1000", "id, title", "INSERT INTO products VALUES (99,'Переходник',900,5); SELECT id, title FROM products WHERE price <= 1000 ORDER BY id;", "ecommerce"),
        ("Закрыть задачу", "обнови статус задачи `Auth` и покажи её статус", "id, status", "UPDATE tasks SET status = 'done' WHERE title = 'Auth'; SELECT id, status FROM tasks WHERE title = 'Auth';", "workflow"),
        ("Оплатить запись", "измени флаг оплаты у Олега на Python Core", "student_id, paid", "UPDATE enrollments SET paid = 1 WHERE student_id = 2 AND course_id = 1; SELECT student_id, paid FROM enrollments WHERE student_id = 2 AND course_id = 1;", "school"),
        ("Назначить тикет", "назначь обращение без агента активному агенту", "id, agent_id", "UPDATE tickets SET agent_id = 2 WHERE agent_id IS NULL; SELECT id, agent_id FROM tickets WHERE subject = 'Без агента';", "support"),
    ],
    "ddl": [
        ("Таблица аудита", "создай таблицу аудита с обязательным действием", "name", "CREATE TABLE audit_log (id INTEGER PRIMARY KEY, action TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT 'now'); SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'audit_log';", "workflow"),
        ("Уникальный email", "создай таблицу клиентов с UNIQUE email", "name", "CREATE TABLE app_users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE); SELECT name FROM pragma_table_info('app_users') ORDER BY cid;", "ecommerce"),
        ("Черновик курсов", "создай таблицу с DEFAULT track", "name", "CREATE TABLE course_drafts (id INTEGER PRIMARY KEY, title TEXT NOT NULL, track TEXT NOT NULL DEFAULT 'backend'); SELECT name FROM pragma_table_info('course_drafts') ORDER BY cid;", "school"),
        ("Очередь импорта", "создай таблицу очереди с NOT NULL статусом", "name", "CREATE TABLE import_queue (id INTEGER PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'new'); SELECT name FROM pragma_table_info('import_queue') ORDER BY cid;", "support"),
    ],
    "transaction": [
        ("Rollback статуса", "измени задачу внутри транзакции и откати", "id, status", "BEGIN; UPDATE tasks SET status = 'done' WHERE id = 1; ROLLBACK; SELECT id, status FROM tasks WHERE id = 1;", "workflow"),
        ("Commit оплаты", "пометь заказ оплаченным и зафиксируй изменение", "id, status", "BEGIN; UPDATE orders SET status = 'paid' WHERE id = 2; COMMIT; SELECT id, status FROM orders WHERE id = 2;", "ecommerce"),
        ("Rollback прогресса", "увеличь progress внутри транзакции и откати", "student_id, course_id, progress", "BEGIN; UPDATE enrollments SET progress = 100 WHERE student_id = 2 AND course_id = 1; ROLLBACK; SELECT student_id, course_id, progress FROM enrollments WHERE student_id = 2 AND course_id = 1;", "school"),
        ("Commit назначения", "назначь обращение внутри транзакции и зафиксируй", "id, agent_id", "BEGIN; UPDATE tickets SET agent_id = 1 WHERE id = 4; COMMIT; SELECT id, agent_id FROM tickets WHERE id = 4;", "support"),
    ],
    "index": [
        ("Индекс статуса задач", "создай индекс по статусу задач и верни открытые задачи", "id, title", "CREATE INDEX idx_tasks_status ON tasks(status); SELECT id, title FROM tasks WHERE status = 'open' ORDER BY id;", "workflow"),
        ("Индекс заказов", "создай индекс по статусу заказа и выведи paid-заказы", "id, total", "CREATE INDEX idx_orders_status ON orders(status); SELECT id, total FROM orders WHERE status = 'paid' ORDER BY id;", "ecommerce"),
        ("Индекс тикетов", "создай индекс по priority и выведи важные обращения", "id, subject", "CREATE INDEX idx_tickets_priority ON tickets(priority); SELECT id, subject FROM tickets WHERE priority >= 3 ORDER BY priority DESC, id;", "support"),
        ("Индекс прогресса", "создай индекс по progress и выведи сильные записи", "student_id, course_id", "CREATE INDEX idx_enrollments_progress ON enrollments(progress); SELECT student_id, course_id FROM enrollments WHERE progress >= 80 ORDER BY progress DESC, student_id;", "school"),
    ],
}


def slugify(value: str, fallback: str = "item") -> str:
    low = value.lower()
    chars = []
    for char in low:
        chars.append(TRANSLIT.get(char, char))
    out = "".join(chars)
    out = re.sub(r"[^a-z0-9]+", "-", out).strip("-")
    return out[:80] or fallback


def path_slug(value: str, fallback: str = "item") -> str:
    slug = slugify(value, fallback)
    return slug.replace("tests", "checks")


def load_course() -> dict:
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))


def save_course(course: dict) -> None:
    COURSE_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def iter_steps(course: dict):
    for module in course["course"]["modules"]:
        for lesson in module["lessons"]:
            for step in lesson["steps"]:
                yield module, lesson, step


def clean_body_text(text: str) -> str:
    body = text or ""
    for old, new in FORBIDDEN_BODY_REPLACEMENTS.items():
        body = body.replace(old, new)
    body = display_title(body)
    body = re.sub(r"В уроке `([^`]+)`([^\\n.]+)это отрабатывается в шаге `([^`]+)`\\.", r"В уроке `\\1` это действие закрепляется в шаге `\\3`.", body)
    body = body.replace("Проверь обычный пример из условия и один крайний случай", "Проверь пример из условия и один крайний случай")
    return body.strip() + ("\n" if body.strip() else "")


def display_title(value: str) -> str:
    return (
        value.replace("Integration tests", "Integration checks")
        .replace("integration tests", "integration checks")
        .replace("Final project: Tests", "Final project: Checks")
        .replace("Финальный проект: Tests", "Финальный проект: Checks")
        .replace("SQL сценарий", "SQL работа")
        .replace("Сценарий", "Работа")
        .replace("сценарий", "случай")
        .replace("Tests", "Checks")
        .replace("tests", "checks")
        .replace(" Tests", " Checks")
        .replace(" tests", " checks")
    )


def domain_for(module: dict, lesson: dict, step: dict) -> str:
    title = (lesson["title"] + " " + step.get("title", "")).lower()
    if lesson["title"].startswith("Финальный проект:"):
        return "final"
    if module["id"] == "m05" and int(lesson.get("order", 0)) <= 12:
        return "ai"
    if module["id"] == "m05" and int(lesson.get("order", 0)) in {13, 14}:
        return "infra"
    if module["id"] == "m04" and (
        "sqlalchemy" in title
        or "database session" in title
        or "relationship" in title
        or "repository" in title
        or "unit of work" in title
        or "alembic" in title
        or "migration" in title
        or "models" in title
    ):
        return "orm"
    if module["id"] == "m04" and lesson["title"].lower() == "healthcheck":
        return "http"
    if "git" in title or "github" in title or "commit" in title or "branch" in title or "merge" in title or "rebase" in title or "remote" in title or "staged" in title or "head" in title:
        return "git"
    if "терминал" in title or "terminal" in title or "bash" in title or "stdout" in title or "stderr" in title or "exit code" in title:
        return "terminal"
    if "docker" in title or "compose" in title or "container" in title or "ports" in title or "volumes" in title or "image" in title or "healthcheck" in title or "logs" in title or "exec" in title or "network" in title or "secret" in title or "ci/cd" in title or "github actions" in title or "gitlab" in title or "deploy" in title or "vps" in title or "ssl" in title or "nginx" in title or "multistage" in title:
        return "infra"
    if "sqlalchemy" in title or "database session" in title or "relationship" in title or "repository" in title or "unit of work" in title or "alembic" in title or "migration" in title or "models" in title:
        return "orm"
    if "fastapi" in title or "api" in title or "http" in title or "rest" in title:
        return "http"
    if "sql" in title or "sqlite" in title or "индекс" in title or "транзак" in title or "schema" in title or "схем" in title or "clickhouse" in title:
        return "sql"
    if module["id"] == "m05":
        return "ai"
    if module["id"] == "m02":
        return "python_hard"
    return "python"


def role_for(step: dict) -> str:
    title = step.get("title", "").lower()
    sid = step.get("id", "")
    if "negative" in title or "ошиб" in title or "null" in sid:
        return "negative"
    if "deliverable" in title or "команд" in title or "filtr" in sid:
        return "deliverable"
    if "review" in title or "join" in sid:
        return "review"
    if "итог" in title or "kontrol" in sid or "result" in title:
        return "final"
    if "acceptance" in title or "kolonki" in sid:
        return "acceptance"
    return "lab"


def role_variant(domain: str, role: str, step_title: str) -> dict[str, str]:
    title = display_title(step_title or "шаг")
    variants = {
        "acceptance": {
            "short": f"задай критерии приёмки для шага «{title}».",
            "lead": "Сначала опиши, по каким признакам работа считается готовой.",
            "submit": "Добавь два критерия: нормальный путь и отказной путь.",
            "check": "Попроси себя повторить проверку по этим критериям без устных пояснений.",
        },
        "deliverable": {
            "short": f"подготовь сдаваемый итог для шага «{title}».",
            "lead": "Собери минимальный результат, который можно открыть и проверить командой.",
            "submit": "Укажи точную команду запуска и один ожидаемый фрагмент результата.",
            "check": "Если команду нельзя выполнить сверху вниз, укажи недостающий файл или настройку.",
        },
        "negative": {
            "short": f"разбери ошибочный путь в шаге «{title}».",
            "lead": "Специально проверь ситуацию, где вход, команда или файл неверные.",
            "submit": "Запиши причину сбоя и исправление, а не только финальный успешный вариант.",
            "check": "Убедись, что ошибка воспроизводится до исправления и исчезает после него.",
        },
        "review": {
            "short": f"проведи ревью результата для шага «{title}».",
            "lead": "Сравни решение с требованием урока и найди одно слабое место.",
            "submit": "Добавь заметку, что именно проверялось первым и почему.",
            "check": "В итоговом файле должен быть вывод, а не пересказ намерений.",
        },
        "final": {
            "short": f"собери контрольную сдачу шага «{title}».",
            "lead": "Сведи рабочий путь, команду и результат в один воспроизводимый набор файлов.",
            "submit": "Покажи финальную команду и короткий вывод, который подтверждает успех.",
            "check": "Повтори запуск на чистом состоянии файлов, если это возможно.",
        },
        "lab": {
            "short": f"собери минимальный рабочий пример шага «{title}».",
            "lead": "Начни с самого маленького действия, которое показывает новый навык урока.",
            "submit": "Оставь в файлах только то, что нужно для повторного запуска.",
            "check": "Измени один входной параметр и проверь, что результат меняется ожидаемо.",
        },
    }
    result = dict(variants.get(role, variants["lab"]))
    if domain == "git":
        result["check"] += " Отдельно посмотри `git status --porcelain`."
    elif domain == "infra":
        result["check"] += " Отдельно проверь порт, переменную окружения или health endpoint."
    elif domain == "http":
        result["check"] += " Отдельно проверь метод, path, status code и форму JSON."
    elif domain == "orm":
        result["check"] += " Отдельно проверь границу session: commit, rollback или close."
    elif domain == "sql":
        result["check"] += " Отдельно проверь порядок строк и случай без совпадений."
    elif domain == "ai":
        result["check"] += " Отдельно проверь работу без настоящего ключа API."
    return result


def theory_example(domain: str, lesson_title: str, step_order: int) -> tuple[str, str]:
    low = lesson_title.lower()
    if domain == "git":
        if step_order <= 1:
            return (
                "bash",
                "git status --short\n"
                "git diff\n",
            )
        return (
            "bash",
            "git add README.md\n"
            "git diff --staged\n"
            "git commit -m \"Update lesson notes\"\n",
        )
    if domain == "terminal":
        if "процесс" in low or "bash" in low:
            return (
                "bash",
                "ps aux | grep python\n"
                "cat app.log | grep ERROR\n",
            )
        return (
            "bash",
            "pwd\n"
            "mkdir lesson-work\n"
            "ls -la\n",
        )
    if domain == "infra":
        if "compose" in low:
            return (
                "yaml",
                "services:\n"
                "  api:\n"
                "    build: .\n"
                "    ports:\n"
                "      - \"8000:8000\"\n",
            )
        if "ci" in low or "actions" in low or "gitlab" in low:
            return (
                "yaml",
                "jobs:\n"
                "  test:\n"
                "    steps:\n"
                "      - run: pytest\n",
            )
        if "vps" in low or "ssl" in low or "nginx" in low:
            return (
                "bash",
                "ssh root@example.com\n"
                "systemctl status nginx\n"
                "curl -I https://example.com/health\n",
            )
        return (
            "dockerfile",
            "FROM python:3.12-slim\n"
            "WORKDIR /app\n"
            "COPY pyproject.toml .\n"
            "CMD [\"python\", \"-m\", \"app\"]\n",
        )
    if domain == "http":
        return (
            "python",
            "from fastapi import FastAPI, HTTPException\n\n"
            "app = FastAPI()\n\n"
            "@app.get(\"/health\")\n"
            "def health():\n"
            "    return {\"status\": \"ok\"}\n",
        )
    if domain == "orm":
        if "alembic" in low or "migration" in low:
            return (
                "python",
                "def upgrade():\n"
                "    op.add_column(\"tasks\", sa.Column(\"done\", sa.Boolean(), nullable=False))\n\n"
                "def downgrade():\n"
                "    op.drop_column(\"tasks\", \"done\")\n",
            )
        return (
            "python",
            "session = session_factory()\n"
            "try:\n"
            "    task = session.get(Task, task_id)\n"
            "    session.commit()\n"
            "finally:\n"
            "    session.close()\n",
        )
    if domain == "sql":
        return (
            "sql",
            "SELECT users.name, COUNT(orders.id) AS orders_count\n"
            "FROM users\n"
            "LEFT JOIN orders ON orders.user_id = users.id\n"
            "GROUP BY users.id, users.name\n"
            "ORDER BY users.id;\n",
        )
    if domain == "ai":
        return (
            "python",
            "class MockProvider:\n"
            "    def complete(self, messages):\n"
            "        last = messages[-1][\"content\"]\n"
            "        return {\"answer\": last[:80], \"source\": \"mock\"}\n",
        )
    if domain == "final":
        return (
            "text",
            "Goal: pass the current gate\n"
            "Files: list exact files\n"
            "Command: show the check command\n"
            "Risk: name one failure path\n",
        )
    if domain == "python_hard":
        return (
            "python",
            "class Task:\n"
            "    def __init__(self, title: str):\n"
            "        self.title = title\n\n"
            "    def rename(self, title: str) -> None:\n"
            "        self.title = title.strip()\n",
        )
    return (
        "python",
        "name = input().strip()\n"
        "if name:\n"
        "    print(f\"Привет, {name}\")\n"
        "else:\n"
        "    print(\"Привет\")\n",
    )


def add_unique_example_marker(language: str, example: str, lesson: dict, step: dict) -> str:
    marker = f"{path_slug(lesson['id'])} {path_slug(step['id'])}"
    if language == "sql":
        return f"-- {marker}\n{example}"
    if language in {"bash", "python", "dockerfile", "yaml"}:
        return f"# {marker}\n{example}"
    return f"Topic: {marker}\n{example}"


def topic_terms_line(lesson_title: str) -> str:
    low = lesson_title.lower()
    terms: list[str] = []
    if "refresh" in low:
        terms.extend(["/auth/refresh", "refresh_token", "access_token", "revoked"])
    if "pagination" in low or "filtering" in low or "sorting" in low:
        terms.extend(["page", "size", "sort"])
    if "testclient" in low:
        terms.extend(["TestClient", "response", "assert"])
    if "integration" in low and "ai integration" not in low:
        terms.extend(["client", "db_session", "response"])
    if "openapi" in low:
        terms.extend(["openapi", "schema", "response"])
    if "postman" in low:
        terms.extend(["postman", "base_url", "request"])
    if low == "healthcheck":
        terms.extend(["route", "HTTP", "status", "path", "JSON", "response"])
    if not terms:
        return ""
    deduped = []
    for term in terms:
        if term not in deduped:
            deduped.append(term)
    return "Ключевые слова этого урока: " + ", ".join(deduped) + "."


def set_domain_theory_step(module: dict, lesson: dict, step: dict) -> bool:
    if step.get("type") != "theory":
        return False
    body = step.get("body_markdown", "")
    needs_rewrite = (
        "normalize_title" in body
        or "вводит новый приём" in body
        or "У действия есть вход: команда, файл, запрос, данные или объект" in body
        or "Частая ошибка: выполнять команду или писать код без проверки состояния после шага" in body
        or "Частая ошибка: смотреть только на отсутствие ошибки, но не сверять итоговое состояние" in body
        or lesson["id"] in {"m01_l029_github-i-remote", "m01_l030_cli-proekt-menedzher-zadach"}
    )
    if not needs_rewrite:
        return False
    domain = domain_for(module, lesson, step)
    lesson_title = display_title(lesson["title"])
    step_title = display_title(step.get("title", "Теория"))
    language, example = theory_example(domain, lesson_title, int(step.get("order", 1)))
    example = add_unique_example_marker(language, example, lesson, step)
    terms_line = topic_terms_line(lesson_title)
    if int(step.get("order", 1)) <= 1:
        explanation = (
            f"{lesson_title} начинается с наблюдаемого состояния. Сначала посмотри, что есть до действия: файл, команда, "
            "таблица, route, контейнер, session или внешний ответ. Потом выполни одно маленькое действие и сразу проверь, что изменилось. "
            f"В шаге «{step_title}» это важно разобрать медленно: не переходи к большому заданию, пока не можешь назвать вход, действие и итог."
        )
        stage_block = (
            f"На первом проходе по уроку {lesson_title} задача не в скорости. Построй простую модель: что уже существует, "
            f"какую одну операцию выполняет шаг «{step_title}», какой след она оставляет и какой командой этот след увидеть. "
            "Такой разбор защищает от копирования: ты понимаешь, почему результат появился, а не просто повторяешь фрагмент."
        )
        warning = f"Частая ошибка в уроке {lesson_title}: выполнять команду или писать код без проверки состояния после шага «{step_title}»."
    else:
        explanation = (
            f"Во втором проходе по теме {lesson_title} важно связать действие с диагностикой. Не запоминай фрагмент как заклинание: "
            "назови вход, строку, которая делает работу, и признак успешного результата. "
            f"В шаге «{step_title}» отдельно проверь отрицательный путь: неверный файл, пустой ответ, конфликт, rollback или другой сбой."
        )
        stage_block = (
            f"На втором проходе по уроку {lesson_title} цель другая: ты проверяешь границы. Для шага «{step_title}» "
            "специально найди сбойный вариант, сравни его с успешным и запиши различие в состоянии. "
            "Так ты учишься диагностировать проблему, а не только получать зелёный результат на одном удобном примере."
        )
        warning = f"Частая ошибка в уроке {lesson_title}: смотреть только на отсутствие ошибки, но не сверять итоговое состояние шага «{step_title}»."
    topic_details = (
        f"Для урока {lesson_title} держи в голове домен `{domain}`. "
        f"Это значит, что пример нужно читать через конкретные слова урока, а не как общий фрагмент: {step_title}. "
        "Если встречаешь команду, проверь stdout/stderr и exit code; если видишь HTTP, проверь method, path, status и JSON; "
        "если работаешь с базой, проверь строки, транзакцию и порядок результата; если это инфраструктура, проверь файл конфигурации и команду запуска."
    )
    terms_block = f"{terms_line}\n\n" if terms_line else ""
    step["body_markdown"] = (
        f"### {step_title}\n"
        f"{explanation}\n\n"
        f"{stage_block}\n\n"
        f"{topic_details}\n\n"
        f"{terms_block}"
        "### Минимальный пример\n"
        f"```{language}\n{example}```\n\n"
        "### Что здесь важно\n"
        f"1. В уроке {lesson_title} у действия есть вход: команда, файл, запрос, данные или объект, который относится именно к шагу «{step_title}».\n"
        f"2. Видимый итог шага «{step_title}» нужно назвать заранее: вывод, строка в таблице, HTTP-статус, созданный файл или изменённая история.\n"
        f"3. Проверка идёт сразу после действия, потому что в теме {lesson_title} ошибка часто прячется не в синтаксисе, а в неверном состоянии после выполнения.\n\n"
        "### Частая ошибка\n"
        f"{warning}\n\n"
        "### Проверь себя\n"
        f"Назови одну строку из примера, которая меняет состояние в уроке {lesson_title}, и одну строку, которая помогает это состояние проверить. "
        f"Затем скажи, какой крайний случай для шага «{step_title}» ты проверишь первым и почему.\n"
    )
    return True


def command_test_file(path: str) -> dict:
    return {"cmd": f"test -s {path}", "expect_exit_code": 0}


def command_grep(path: str, pattern: str) -> dict:
    return {"cmd": f"grep -E \"{pattern}\" {path}", "expect_exit_code": 0}


def set_ide_step(module: dict, lesson: dict, step: dict) -> bool:
    checker = step.get("checker") or {}
    if checker.get("type") != "ide_plugin":
        return False
    if module["id"] == "m01" and int(lesson.get("order", 0)) <= 10:
        return restore_first10_project(lesson, step)

    domain = domain_for(module, lesson, step)
    if domain == "final":
        return False
    role = role_for(step)
    lesson_slug = path_slug(lesson["id"])
    step_slug = path_slug(step["title"], f"step-{step['order']}")
    artifact = f"artifacts/{lesson_slug}_{step['order']:02d}_{role}.txt"

    if domain == "sql":
        code_file = f"sql/{lesson_slug}_{step_slug}.sql"
        notes_file = f"checks/{lesson_slug}_{step_slug}_sql.md"
        focus = sql_project_focus(lesson["title"], role)
        files = [code_file, notes_file, artifact]
        commands = [
            command_test_file(code_file),
            command_grep(code_file, focus["grep"]),
            command_grep(notes_file, "tables|columns|edge|rollback|order|index|plan|result"),
        ]
        lesson_title = display_title(lesson["title"])
        short = f"оформи SQL-работу урока {lesson_title} через отдельный файл и разбор результата."
        condition = (
            f"В `{code_file}` напиши оператор, который показывает {focus['skill']}. "
            f"В `{notes_file}` опиши таблицы, ожидаемые колонки и один крайний случай. "
            f"В `{artifact}` запиши команду запуска через SQLite и фактический результат."
        )
        submit = "SQL-файл содержит реальный оператор, заметка объясняет порядок строк и крайний случай, итоговый файл содержит команду запуска."
        check = f"Проверь, что в SQL есть {focus['human']}, а результат можно повторить на чистой базе."
    elif domain == "http":
        code_file = f"app/{lesson_slug}_{step_slug}.py"
        notes_file = f"checks/{lesson_slug}_{step_slug}_http.md"
        files = [code_file, notes_file, artifact]
        commands = [
            command_test_file(code_file),
            command_grep(code_file, "FastAPI|APIRouter|@app|@router"),
            command_grep(notes_file, "method|path|status|JSON|error|curl"),
        ]
        lesson_title = display_title(lesson["title"])
        short = f"собери HTTP-миниработу для урока {lesson_title}."
        condition = (
            f"В `{code_file}` оставь минимальный endpoint из урока. "
            f"В `{notes_file}` зафиксируй method, path, статус, JSON-ответ и ошибочный запрос. "
            f"В `{artifact}` запиши curl-команду или ручную проверку."
        )
        submit = "Код содержит route, заметка содержит контракт HTTP, итоговый файл показывает, как ты проверил ответ."
        check = "Сверь путь буквально: лишний префикс, другой статус или другой JSON-ключ считаются ошибкой."
    elif domain == "orm":
        code_file = f"src/db/{lesson_slug}_{step_slug}.py"
        notes_file = f"checks/db/{lesson_slug}_{step_slug}.md"
        files = [code_file, notes_file, artifact]
        commands = [
            command_test_file(code_file),
            command_grep(code_file, orm_grep(lesson["title"])),
            command_grep(notes_file, "session|commit|rollback|model|relation|migration|repository|query"),
        ]
        lesson_title = display_title(lesson["title"])
        short = f"закрепи работу с БД в уроке {lesson_title} через код, а не через общий конспект."
        condition = (
            f"В `{code_file}` напиши маленький фрагмент по теме урока: модель, session, repository, relation или migration. "
            f"В `{notes_file}` опиши входные данные, границу транзакции и что произойдёт при ошибке. "
            f"В `{artifact}` запиши команду локальной проверки и фактический итог."
        )
        submit = "Код содержит конкретную границу работы с БД, заметка объясняет состояние до и после операции, итоговый файл показывает запуск."
        check = "Убедись, что в решении видно, где создаётся session и где она закрывается."
    elif domain == "infra":
        main_file = infra_main_file(lesson["title"], lesson_slug, step_slug)
        notes_file = f"checks/{lesson_slug}_{step_slug}_ops.md"
        files = [main_file, notes_file, artifact]
        commands = [
            command_test_file(main_file),
            command_grep(main_file, infra_grep(lesson["title"])),
            command_grep(notes_file, "command|env|log|rollback|health|port|secret"),
        ]
        lesson_title = display_title(lesson["title"])
        short = f"подготовь инфраструктурную работу для урока {lesson_title}."
        condition = (
            f"В `{main_file}` запиши конфигурацию или командный файл урока. "
            f"В `{notes_file}` опиши команду запуска, переменные окружения, диагностику и откат. "
            f"В `{artifact}` зафиксируй, какую команду выполнил и что получил."
        )
        submit = "Конфигурация не пустая, заметка содержит команды и диагностику, итоговый файл показывает результат запуска."
        check = "Другой разработчик должен понять, какую команду выполнить и какой признак успеха увидеть."
    elif domain == "ai":
        code_file = f"src/ai/{lesson_slug}_{step_slug}.py"
        notes_file = f"checks/ai/{lesson_slug}_{step_slug}.md"
        files = [code_file, notes_file, artifact]
        commands = [
            command_test_file(code_file),
            command_grep(code_file, ai_grep(lesson["title"])),
            command_grep(notes_file, "input|output|timeout|mock|schema|retrieval|risk|cost"),
        ]
        lesson_title = display_title(lesson["title"])
        short = f"собери AI-модуль для урока {lesson_title} без внешнего платного API."
        condition = (
            f"В `{code_file}` реализуй маленький mock-provider или функцию обработки по теме урока. "
            f"В `{notes_file}` опиши вход, выход, отказоустойчивость и риск неверного ответа. "
            f"В `{artifact}` запиши локальную команду проверки."
        )
        submit = "Код работает без настоящего ключа API, заметка описывает ограничение, итоговый файл содержит локальную проверку."
        check = "Если модуль нельзя запустить без секрета, работа не готова для учебной платформы."
    elif domain in {"git", "terminal"}:
        script_file = f"ops/{lesson_slug}_{step_slug}.sh"
        notes_file = f"checks/{lesson_slug}_{step_slug}_cli.md"
        files = [script_file, notes_file, artifact]
        commands = [
            command_test_file(script_file),
            command_grep(script_file, "git|status|log|diff|branch|merge|rebase|ps|grep|cat|mkdir|cd|ls"),
            command_grep(notes_file, "command|stdout|stderr|exit|branch|file"),
        ]
        lesson_title = display_title(lesson["title"])
        short = f"зафиксируй CLI-действие для урока {lesson_title}."
        condition = (
            f"В `{script_file}` запиши команды урока в правильном порядке. "
            f"В `{notes_file}` объясни ожидаемый stdout, ошибочный случай и состояние файлов или ветки. "
            f"В `{artifact}` сохрани итоговую команду проверки."
        )
        submit = "Команды можно выполнить сверху вниз, заметка показывает ожидаемый результат, итоговый файл не пустой."
        check = "Перед сдачей проверь, что команды не требуют ручного домысливания."
    else:
        code_file = f"src/{lesson_slug}_{step_slug}.py"
        notes_file = f"checks/{lesson_slug}_{step_slug}_cases.md"
        files = [code_file, notes_file, artifact]
        commands = [
            command_test_file(code_file),
            command_grep(code_file, python_grep(lesson["title"])),
            command_grep(notes_file, "input|action|edge|expected|actual"),
        ]
        lesson_title = display_title(lesson["title"])
        short = f"собери Python-работу для урока {lesson_title}."
        condition = (
            f"В `{code_file}` напиши минимальный код, который показывает новый приём урока. "
            f"В `{notes_file}` опиши вход, действие, обычный случай и крайний случай. "
            f"В `{artifact}` запиши команду запуска и фактический вывод."
        )
        submit = "Код можно выполнить, заметка описывает два случая, итоговый файл содержит команду и вывод."
        check = "Измени вход и убедись, что результат меняется предсказуемо."

    variant = role_variant(domain, role, step.get("title", ""))
    step["body_markdown"] = (
        f"**Коротко:** {variant['short']} {short}\n\n"
        f"### Условие\n{variant['lead']} {condition}\n\n"
        f"### Что сдать\n{submit} {variant['submit']}\n\n"
        f"### Что проверить\n{check} {variant['check']}\n\n"
        f"{SELF_CHECK}"
    )
    step["checker"] = {
        "type": "ide_plugin",
        "required_files": files,
        "commands": commands,
        "timeout_sec": checker.get("timeout_sec", 15),
        "hidden_tests": commands[:],
        "git_checks": checker.get("git_checks", {"must_have_clean_worktree": True, "forbidden_untracked_files": True}),
        "quality_gate": f"{domain}_{role}",
        "scenario_id": f"{step['id']}_{domain}_{role}",
    }
    step["solution_code"] = (
        f"Files: {', '.join(files)}\n"
        f"Purpose: {lesson['title']} / {step['title']}.\n"
        f"Commands: " + "; ".join(cmd["cmd"] for cmd in commands) + "\n"
    )
    step["hints"] = [
        "Сначала создай все файлы из условия.",
        "Заполни заметку до запуска команды: так легче увидеть расхождение.",
        "После команды запиши фактический результат, а не ожидаемый пересказ.",
    ]
    return True


def restore_first10_project(lesson: dict, step: dict) -> bool:
    if step.get("type") != "project":
        return False
    lesson_title = display_title(lesson["title"])
    step["body_markdown"] = (
        f"**Коротко:** собери маленький проект по уроку {lesson_title}.\n\n"
        "### Условие\n"
        "Создай `main.py` и `README.md`. В `main.py` напиши короткую программу из этого урока. "
        "В `README.md` запиши команду запуска и ожидаемый вывод.\n\n"
        "### Что сдать\n"
        "`main.py` содержит код, `README.md` содержит команду запуска и ожидаемый вывод.\n\n"
        "### Что проверить\n"
        "Запусти программу и сравни вывод с тем, что написал в README.md.\n"
    )
    commands = [
        command_test_file("main.py"),
        command_test_file("README.md"),
        command_grep("README.md", "python|main.py|вывод|команда"),
    ]
    step["checker"] = {
        "type": "ide_plugin",
        "required_files": ["main.py", "README.md"],
        "commands": commands,
        "timeout_sec": 10,
        "hidden_tests": commands[:],
    }
    step["solution_code"] = f"Мини-проект «{step['title']}»: main.py, README.md.\n"
    step["hints"] = [
        "Сначала добейся правильного вывода в редакторе.",
        "Потом перенеси рабочий код в main.py.",
        "В README.md запиши только команду запуска и ожидаемый вывод.",
    ]
    return True


def sql_project_focus(title: str, role: str) -> dict[str, str]:
    low = title.lower()
    if "cte" in low:
        return {"skill": "именованный CTE через WITH", "grep": "WITH|SELECT", "human": "WITH"}
    if "окон" in low:
        return {"skill": "оконную функцию", "grep": "OVER|PARTITION|ROW_NUMBER|RANK", "human": "OVER"}
    if "транзак" in low or "acid" in low:
        return {"skill": "границу транзакции", "grep": "BEGIN|COMMIT|ROLLBACK", "human": "BEGIN/COMMIT/ROLLBACK"}
    if "индекс" in low or "explain" in low:
        return {"skill": "индекс или план чтения", "grep": "INDEX|EXPLAIN|CREATE", "human": "INDEX или EXPLAIN"}
    if "join" in low:
        return {"skill": "связь таблиц через ON", "grep": "JOIN|ON", "human": "JOIN ... ON"}
    if "insert" in low or "update" in low or "delete" in low:
        return {"skill": "изменение данных", "grep": "INSERT|UPDATE|DELETE|SELECT", "human": "DML"}
    if "constraint" in low or "ddl" in low or "схем" in low:
        return {"skill": "ограничение схемы", "grep": "CREATE|PRIMARY|FOREIGN|NOT NULL|UNIQUE|DEFAULT", "human": "DDL"}
    return {"skill": "запрос с явным порядком результата", "grep": "SELECT|WHERE|GROUP BY|ORDER BY|HAVING", "human": "SELECT"}


def infra_main_file(title: str, lesson_slug: str, step_slug: str) -> str:
    low = title.lower()
    if "compose" in low:
        return f"ops/{lesson_slug}_{step_slug}_compose.yml"
    if "dockerfile" in low or "image" in low or "multistage" in low:
        return f"ops/{lesson_slug}_{step_slug}_Dockerfile"
    if "github actions" in low or "ci/cd" in low:
        return f"ops/{lesson_slug}_{step_slug}_workflow.yml"
    if "gitlab" in low:
        return f"ops/{lesson_slug}_{step_slug}_gitlab-ci.yml"
    if "nginx" in low or "ssl" in low:
        return f"ops/{lesson_slug}_{step_slug}_nginx.conf"
    return f"ops/{lesson_slug}_{step_slug}.sh"


def infra_grep(title: str) -> str:
    low = title.lower()
    if "compose" in low:
        return "services|depends_on|healthcheck|ports|volumes"
    if "docker" in low or "image" in low:
        return "FROM|COPY|RUN|CMD|ENTRYPOINT|WORKDIR"
    if "github" in low or "ci/cd" in low:
        return "jobs|steps|checkout|pytest|docker|build"
    if "gitlab" in low:
        return "stages|script|pytest|docker|build"
    if "nginx" in low or "ssl" in low:
        return "server|listen|proxy_pass|ssl|location"
    return "deploy|rollback|health|ssh|systemctl|pm2|docker"


def orm_grep(title: str) -> str:
    low = title.lower()
    if "alembic" in low or "migration" in low:
        return "upgrade|downgrade|op\\.|revision"
    if "relationship" in low or "models" in low:
        return "Mapped|mapped_column|relationship|ForeignKey|Table"
    if "repository" in low or "unit of work" in low:
        return "Repository|UnitOfWork|session|commit|rollback"
    if "session" in low:
        return "session|commit|rollback|close"
    return "select|Session|session|commit|rollback|relationship"


def ai_grep(title: str) -> str:
    low = title.lower()
    if "schema" in low or "structured" in low:
        return "schema|json|validate|field"
    if "retry" in low or "timeout" in low:
        return "retry|timeout|attempt|backoff"
    if "rag" in low or "vector" in low or "embedding" in low:
        return "chunk|embed|retrieve|source|score"
    if "cost" in low or "rate" in low:
        return "limit|budget|tokens|cost"
    return "message|provider|mock|system|user|response"


def python_grep(title: str) -> str:
    low = title.lower()
    if "ооп" in low or "class" in low or "полиморф" in low or "наслед" in low or "компози" in low:
        return "class|def|self|return"
    if "typing" in low or "mypy" in low:
        return "def|->|Optional|Union|list|dict|Protocol"
    if "async" in low:
        return "async|await|gather|Queue"
    if "thread" in low:
        return "Thread|Lock|Queue|def"
    if "multiprocessing" in low:
        return "Process|Pool|if __name__|map"
    if "pytest" in low:
        return "def|assert|pytest"
    return "def|return|print|class"


def detect_sql_skill(lesson_title: str, step_title: str) -> str:
    low = f"{lesson_title} {step_title}".lower()
    if "window" in low or "окон" in low:
        return "window"
    if "cte" in low:
        return "cte"
    if "подзапрос" in low:
        return "subquery"
    if "self join" in low:
        return "self"
    if "left join" in low:
        return "left"
    if "join" in low:
        return "join"
    if "having" in low:
        return "having"
    if "group by" in low or "агрег" in low or "aggregate" in low:
        return "aggregate"
    if "like" in low or "between" in low or "null" in low or " in," in low:
        return "pattern"
    if "order" in low or "limit" in low:
        return "order"
    if "where" in low or "фильтр" in low or "условие" in low:
        return "where"
    if "insert" in low or "update" in low or "delete" in low or "crud" in low:
        return "dml"
    if "transaction" in low or "acid" in low or "транзак" in low or "rollback" in low:
        return "transaction"
    if "constraint" in low or "ddl" in low or "normal" in low or "схем" in low or "models" in low:
        return "ddl"
    if "index" in low or "explain" in low or "индекс" in low or "изоляц" in low or "блокиров" in low:
        return "index"
    return "select"


def run_sql(schema: str, seed: str, solution: str) -> list[list]:
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema)
    conn.executescript(seed)
    statements = [part.strip() for part in solution.split(";") if part.strip()]
    if not statements:
        return []
    for statement in statements[:-1]:
        conn.execute(statement)
    cursor = conn.execute(statements[-1])
    rows = [list(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def set_sql_query_step(lesson: dict, step: dict, sql_index: int) -> bool:
    checker = step.get("checker") or {}
    if checker.get("type") != "sql_query":
        return False
    skill = detect_sql_skill(lesson["title"], step["title"])
    cards = SQL_CARDS.get(skill, SQL_CARDS["select"])
    title, action, columns, solution, pack_key = cards[sql_index % len(cards)]
    pack = SCHEMA_PACKS[pack_key]
    public_rows = run_sql(pack["schema"], pack["seed"], solution)
    hidden_rows = run_sql(pack["schema"], pack["hidden_seed"], solution)
    lesson_title = display_title(lesson["title"])
    step["title"] = f"{title}: {lesson_title}"
    step["body_markdown"] = (
        f"**Коротко:** {action}.\n\n"
        f"### Условие\n"
        f"Работаешь с базой `{pack['name']}` в уроке {lesson_title}. Напиши SQL так, чтобы он отрабатывал именно навык `{skill}`. "
        f"Верни колонки `{columns}` и задай стабильный порядок строк.\n\n"
        f"### Схема\n"
        f"Проверка создаст нужные таблицы перед запуском запроса. Основные таблицы: {schema_summary(pack['schema'])}.\n\n"
        f"### Вход\nДанные уже загружены в SQLite.\n\n"
        f"### Выход\nТаблица с колонками `{columns}`.\n\n"
        f"### Пример формы\n```sql\nSELECT ...\n```\n\n"
        f"### Что проверить\n"
        f"Назови таблицы, условие отбора и порядок результата. Если используешь изменение данных, последним оператором оставь SELECT, чтобы было что сравнить.\n\n"
        f"{SELF_CHECK}"
    )
    step["solution_code"] = f"/* {lesson_title} / {step['title']} */\n{solution}\n"
    step["checker"] = {
        "type": "sql_query",
        "dialect": "sqlite",
        "schema_sql": pack["schema"],
        "seed_sql": pack["seed"],
        "public_tests": [
            {"name": slugify(title), "expected_rows": public_rows, "compare": "ordered_rows"}
        ],
        "hidden_tests": [
            {"seed_sql": pack["hidden_seed"], "expected_rows": hidden_rows, "compare": "ordered_rows"}
        ],
        "scenario_id": f"{step['id']}_{skill}_{pack_key}_{sql_index}",
    }
    step["hints"] = [
        "Сначала выпиши таблицу-источник и нужные колонки.",
        "Если строк больше одной, добавь ORDER BY.",
        "Для DDL/DML оставь последним SELECT, который показывает итог.",
    ]
    return True


def schema_summary(schema: str) -> str:
    names = re.findall(r"CREATE TABLE ([a-z_]+)", schema)
    return ", ".join(names)


def step_function_name(step: dict) -> str:
    return re.sub(r"[^0-9A-Za-z_]+", "_", step["id"]).strip("_")


def set_oop_abstraction_step(module: dict, lesson: dict, step: dict) -> bool:
    checker = step.get("checker") or {}
    if module["id"] != "m02" or "абстрак" not in lesson["title"].lower():
        return False
    if checker.get("type") != "python_pytest" or step.get("type") != "practice":
        return False
    if step["id"] not in {"m02_l010_abstrakcii_s004_sostoyanie-1", "m02_l010_abstrakcii_s007_invariant-4"}:
        return False

    func = step_function_name(step)
    step_title = display_title(step.get("title", "шаг"))
    if step["id"].endswith("s004_sostoyanie-1"):
        body = (
            f"**Коротко:** отдели интерфейс repository от реализации в шаге «{step_title}».\n\n"
            f"### Условие\nНапиши `TaskRepository`, `MemoryTaskRepository` и функцию `{func}(items, task_id)`. "
            "`TaskRepository` задаёт метод `get(task_id)`, а `MemoryTaskRepository` хранит задачи в словаре.\n\n"
            "### Вход\nСловарь задач и id задачи.\n\n"
            "### Выход\nНайденная задача или `None`.\n\n"
            "### Что проверить\n"
            "Код должен показывать абстракцию: функция работает через объект repository, а не читает словарь напрямую.\n\n"
            f"{SELF_CHECK}"
        )
        solution = f"""from abc import ABC, abstractmethod


class TaskRepository(ABC):
    @abstractmethod
    def get(self, task_id):
        raise NotImplementedError


class MemoryTaskRepository(TaskRepository):
    def __init__(self, items):
        self.items = items

    def get(self, task_id):
        return self.items.get(task_id)


def {func}(items, task_id):
    repository = MemoryTaskRepository(items)
    return repository.get(task_id)
"""
        test_code = f"""from solution import {func}, MemoryTaskRepository, TaskRepository


def test_memory_repository_reads_by_id():
    items = {{1: {{"title": "Auth"}}, 2: {{"title": "API"}}}}
    assert {func}(items, 2) == {{"title": "API"}}
    assert {func}(items, 99) is None


def test_repository_is_object_boundary():
    repository = MemoryTaskRepository({{1: "task"}})
    assert isinstance(repository, TaskRepository)
    assert repository.get(1) == "task"
"""
    else:
        body = (
            f"**Коротко:** задай Unit of Work как объект с явной границей в шаге «{step_title}».\n\n"
            f"### Условие\nНапиши класс `UnitOfWork` и функцию `{func}(action)`. "
            "Класс должен быть context manager: при успешном action фиксируй `commit`, при ошибке фиксируй `rollback`.\n\n"
            "### Вход\nФункция action, которая получает объект UnitOfWork.\n\n"
            "### Выход\nСписок событий, если action завершился успешно; исходное исключение, если action упал.\n\n"
            "### Что проверить\n"
            "Граница абстракции должна быть внутри класса: вызывающий код не должен вручную решать, когда закрывать работу.\n\n"
            f"{SELF_CHECK}"
        )
        solution = f"""class UnitOfWork:
    def __init__(self):
        self.events = []

    def __enter__(self):
        self.events.append("enter")
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.events.append("exit")
        return False

    def commit(self):
        self.events.append("commit")

    def rollback(self):
        self.events.append("rollback")


def {func}(action):
    uow = UnitOfWork()
    with uow as opened:
        action(opened)
    return uow.events
"""
        test_code = f"""from solution import {func}, UnitOfWork


def test_unit_of_work_commits_on_success():
    assert {func}(lambda uow: uow.events.append("work")) == ["enter", "work", "commit", "exit"]


def test_unit_of_work_rolls_back_on_error():
    uow = UnitOfWork()
    try:
        with uow:
            raise RuntimeError("broken")
    except RuntimeError:
        pass
    assert uow.events == ["enter", "rollback", "exit"]
"""

    step["body_markdown"] = body
    step["editor_initial_code"] = f"def {func}(*args, **kwargs):\n    pass\n"
    step["solution_code"] = solution
    step["checker"] = {
        "type": "python_pytest",
        "timeout_sec": checker.get("timeout_sec", 5),
        "test_code": test_code,
        "scenario_id": f"{step['id']}_oop_abstraction",
    }
    step["hints"] = [
        "Сначала напиши класс, потом функцию, которая использует объект класса.",
        "Абстракция нужна, чтобы вызывающий код не знал детали хранения или транзакции.",
        "Проверь обычный и ошибочный путь отдельно.",
    ]
    return True


def set_exam3_practice_step(lesson: dict, step: dict) -> bool:
    checker = step.get("checker") or {}
    if lesson["id"] != "m03_l036_ekzamen-3" or checker.get("type") != "python_pytest":
        return False
    variants = {
        "s004": {
            "func": "check_orders_schema",
            "short": "проверь схему таблицы orders перед SQL-экзаменом.",
            "condition": "Напиши функцию `check_orders_schema(columns)`. Она получает список названий колонок и возвращает список обязательных колонок, которых не хватает: `id`, `user_id`, `total`, `status`.",
            "input": "Список строк с названиями колонок.",
            "output": "Список отсутствующих колонок в порядке `id`, `user_id`, `total`, `status`.",
            "solution": """def check_orders_schema(columns):
    required = ["id", "user_id", "total", "status"]
    existing = set(columns)
    return [name for name in required if name not in existing]
""",
            "test": """from solution import check_orders_schema


def test_schema_ok():
    assert check_orders_schema(["id", "user_id", "total", "status"]) == []


def test_schema_missing_columns():
    assert check_orders_schema(["id", "total"]) == ["user_id", "status"]
""",
        },
        "s005": {
            "func": "build_paid_orders_query",
            "short": "собери SELECT с фильтром по статусу и сумме.",
            "condition": "Напиши функцию `build_paid_orders_query(min_total)`. Она возвращает SQL-строку для paid-заказов с `total >= min_total`, колонками `id, user_id, total` и сортировкой по `total DESC, id`.",
            "input": "Минимальная сумма заказа.",
            "output": "SQL-строка без подстановки пользовательского текста внутрь имени таблицы.",
            "solution": """def build_paid_orders_query(min_total):
    return (
        "SELECT id, user_id, total FROM orders "
        f"WHERE status = 'paid' AND total >= {int(min_total)} "
        "ORDER BY total DESC, id"
    )
""",
            "test": """from solution import build_paid_orders_query


def test_paid_orders_query_shape():
    query = build_paid_orders_query(1000)
    assert "FROM orders" in query
    assert "status = 'paid'" in query
    assert "total >= 1000" in query
    assert query.endswith("ORDER BY total DESC, id")
""",
        },
        "s006": {
            "func": "normalize_optional_city",
            "short": "обработай NULL-значение из результата SQL.",
            "condition": "Напиши функцию `normalize_optional_city(city)`. Она возвращает очищенный город, а для `None` или пустой строки возвращает `unknown`.",
            "input": "Строка, пустая строка или `None`.",
            "output": "Готовое значение для отчёта.",
            "solution": """def normalize_optional_city(city):
    if city is None:
        return "unknown"
    cleaned = city.strip()
    return cleaned if cleaned else "unknown"
""",
            "test": """from solution import normalize_optional_city


def test_city_value_is_cleaned():
    assert normalize_optional_city(" Москва ") == "Москва"


def test_missing_city_is_unknown():
    assert normalize_optional_city(None) == "unknown"
    assert normalize_optional_city("   ") == "unknown"
""",
        },
        "s007": {
            "func": "build_orders_users_join",
            "short": "собери JOIN-запрос без декартова произведения.",
            "condition": "Напиши функцию `build_orders_users_join()`. Она возвращает SQL-строку, которая соединяет `orders` и `users` по `users.id = orders.user_id`, возвращает `orders.id`, `users.name`, `orders.total` и сортирует по `orders.id`.",
            "input": "Функция вызывается без аргументов.",
            "output": "SQL-строка с явным `JOIN ... ON`.",
            "solution": """def build_orders_users_join():
    return (
        "SELECT orders.id, users.name, orders.total "
        "FROM orders JOIN users ON users.id = orders.user_id "
        "ORDER BY orders.id"
    )
""",
            "test": """from solution import build_orders_users_join


def test_join_has_on_condition():
    query = build_orders_users_join()
    assert "JOIN users ON users.id = orders.user_id" in query
    assert "ORDER BY orders.id" in query
    assert "SELECT orders.id, users.name, orders.total" in query
""",
        },
    }
    key = next((part for part in variants if part in step["id"]), "")
    if not key:
        return False
    item = variants[key]
    step["body_markdown"] = (
        f"**Коротко:** {item['short']}\n\n"
        f"### Условие\n{item['condition']}\n\n"
        f"### Вход\n{item['input']}\n\n"
        f"### Выход\n{item['output']}\n\n"
        "### Что проверить\n"
        "Это экзаменационная отработка: проверь не только happy path, но и крайний случай, из-за которого SQL-решение обычно ломается.\n\n"
        f"{SELF_CHECK}"
    )
    step["editor_initial_code"] = f"def {item['func']}(*args, **kwargs):\n    pass\n"
    step["solution_code"] = item["solution"]
    step["checker"] = {
        "type": "python_pytest",
        "timeout_sec": checker.get("timeout_sec", 5),
        "test_code": item["test"],
        "scenario_id": f"{step['id']}_exam3_{item['func']}",
    }
    step["hints"] = [
        "Сначала выпиши, что должно быть на входе и выходе.",
        "Проверь крайний случай отдельно от обычного.",
        "Не меняй имена колонок: экзамен проверяет точный контракт.",
    ]
    return True


def set_exam1_python_core_step(lesson: dict, step: dict) -> bool:
    if step["id"] != "m01_l031_ekzamen-1_s004_python_core":
        return False
    checker = step.get("checker") or {}
    step["body_markdown"] = (
        "**Коротко:** реализуй три функции для мини-списка задач.\n\n"
        "### Условие\n"
        "Создай `count_open(tasks)`, `unique_tags(tasks)` и `clean_task_title(title)`. "
        "`count_open` считает незавершённые задачи. `unique_tags` возвращает отсортированные уникальные теги. "
        "`clean_task_title` убирает пробелы по краям и заменяет пустой заголовок на `Untitled`.\n\n"
        "### Вход\nPython-значения, без чтения input.\n\n"
        "### Выход\nReturn-значения функций.\n\n"
        "### Пример\n`clean_task_title(\"  Buy milk  \")` возвращает `\"Buy milk\"`.\n\n"
        "### Что проверить\nФункции не должны печатать результат. Отдельно проверь пустой список задач и заголовок из пробелов.\n\n"
        f"{SELF_CHECK}"
    )
    step["solution_code"] = """def count_open(tasks):
    return sum(1 for task in tasks if not task.get("done", False))


def unique_tags(tasks):
    tags = set()
    for task in tasks:
        tags.update(task.get("tags", []))
    return sorted(tags)


def clean_task_title(title):
    cleaned = title.strip()
    return cleaned if cleaned else "Untitled"
"""
    step["checker"] = {
        "type": "python_pytest",
        "timeout_sec": checker.get("timeout_sec", 5),
        "test_code": """from solution import count_open, unique_tags, clean_task_title


def test_helpers():
    tasks = [{"title": " A ", "done": False, "tags": ["cli", "git"]}, {"title": "B", "done": True, "tags": ["cli"]}]
    assert count_open(tasks) == 1
    assert unique_tags(tasks) == ["cli", "git"]
    assert clean_task_title("  Buy milk  ") == "Buy milk"
""",
        "hidden_tests": [
            {
                "test_code": """from solution import count_open, unique_tags, clean_task_title


def test_edges():
    assert count_open([]) == 0
    assert unique_tags([{"done": False}]) == []
    assert clean_task_title("   ") == "Untitled"
"""
            }
        ],
        "scenario_id": "m01_l031_exam1_python_core_helpers",
    }
    step["hints"] = [
        "count_open удобно считать через sum по булевому условию.",
        "Для тегов собери set, потом отсортируй.",
        "Для пустого заголовка сначала сделай strip, потом проверь результат.",
    ]
    return True


def set_final_alembic_practice_step(lesson: dict, step: dict) -> bool:
    checker = step.get("checker") or {}
    if lesson["id"] != "m05_l022_finalnyy-proekt-alembic-migrations" or checker.get("type") != "ide_plugin" or step.get("type") != "practice":
        return False
    file_path = (checker.get("required_files") or [f"migrations/versions/{lesson['id']}_{step['order']}_revision.py"])[0]
    variants = {
        "upgrade": {
            "short": "создай upgrade, который добавляет конкретное изменение схемы.",
            "condition": f"В `{file_path}` объяви `revision`, `down_revision` и функцию `upgrade()`. В `upgrade()` добавь колонку `ai_summary` в таблицу `tasks` или создай аналогичное изменение для своей схемы.",
            "submit": "Файл содержит revision metadata и upgrade с реальным `op.add_column` или `op.create_table`.",
            "check": "Проверь, что миграция не меняет данные без явной причины.",
            "grep": "op.add_column|op.create_table|upgrade",
        },
        "downgrade": {
            "short": "добавь downgrade, который честно откатывает изменение.",
            "condition": f"В `{file_path}` реализуй `downgrade()`: он должен удалить то, что сделал upgrade, например `op.drop_column` или `op.drop_table`.",
            "submit": "Файл показывает прямой и обратный путь миграции.",
            "check": "Если downgrade пустой, rollback деплоя станет ручной аварийной операцией.",
            "grep": "op.drop_column|op.drop_table|downgrade",
        },
        "revision": {
            "short": "задай revision id и связь с предыдущей миграцией.",
            "condition": f"В `{file_path}` заполни `revision` и `down_revision`. Значения должны быть строками; `down_revision` связывает файл с предыдущим шагом истории.",
            "submit": "Файл содержит непустые `revision` и `down_revision`, а также обе функции миграции.",
            "check": "Проверь, что revision не совпадает с down_revision.",
            "grep": "revision|down_revision",
        },
        "env": {
            "short": "подготовь миграцию так, чтобы её можно было запускать из Alembic env.",
            "condition": f"В `{file_path}` оставь migration-файл с `upgrade()` и `downgrade()`, а в комментарии сверху укажи команду `alembic upgrade head` и риск запуска не на той базе.",
            "submit": "Файл содержит команду запуска, revision metadata и обратный путь.",
            "check": "Перед сдачей проверь, что команда запуска не требует секретов в коде.",
            "grep": "alembic upgrade head|upgrade|downgrade",
        },
    }
    low = step.get("title", "").lower()
    if "downgrade" in low:
        item = variants["downgrade"]
    elif "revision id" in low:
        item = variants["revision"]
    elif "env" in low:
        item = variants["env"]
    else:
        item = variants["upgrade"]
    commands = [
        command_test_file(file_path),
        command_grep(file_path, item["grep"]),
        command_grep(file_path, "def upgrade|def downgrade"),
    ]
    step["body_markdown"] = (
        f"**Коротко:** {item['short']}\n\n"
        f"### Условие\n{item['condition']}\n\n"
        f"### Что сдать\n{item['submit']}\n\n"
        f"### Что проверить\n{item['check']}\n\n"
        f"{SELF_CHECK}"
    )
    step["solution_code"] = f"{file_path}: {item['short']} Revision metadata, upgrade, downgrade.\n"
    step["checker"] = {
        "type": "ide_plugin",
        "required_files": [file_path],
        "commands": commands,
        "timeout_sec": checker.get("timeout_sec", 12),
        "hidden_tests": commands[:],
        "quality_gate": "final_alembic_practice",
        "scenario_id": f"{step['id']}_final_alembic",
    }
    step["hints"] = [
        "Сначала заполни revision metadata.",
        "Потом напиши upgrade и только после него downgrade.",
        "Сравни прямой и обратный путь: они должны описывать одну и ту же схему.",
    ]
    return True


def set_orm_pytest_step(module: dict, lesson: dict, step: dict) -> bool:
    checker = step.get("checker") or {}
    if checker.get("type") != "python_pytest" or step.get("type") != "practice":
        return False
    if module["id"] != "m04":
        return False
    if domain_for(module, lesson, step) != "orm":
        return False

    func = step_function_name(step)
    lesson_title = display_title(lesson["title"])
    step_title = display_title(step.get("title", "шаг"))
    low = step_title.lower()

    if "rollback" in low:
        focus = "rollback при исключении"
        signature = f"{func}(session_factory, action)"
        condition = (
            f"Напиши функцию `{func}`. Она открывает session, вызывает `action(session)`, "
            "при исключении вызывает `rollback()` и в любом случае закрывает session."
        )
        example = f"`{signature}` должен пробросить исходное исключение и оставить порядок событий `rollback`, `close`."
        solution = f"""def {func}(session_factory, action):
    session = session_factory()
    try:
        return action(session)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
"""
        test_code = f"""from solution import {func}


class FakeSession:
    def __init__(self):
        self.events = []
    def rollback(self):
        self.events.append("rollback")
    def close(self):
        self.events.append("close")


def test_rollback_and_close_on_error():
    session = FakeSession()
    def broken(_session):
        raise ValueError("bad data")
    try:
        {func}(lambda: session, broken)
    except ValueError:
        pass
    else:
        raise AssertionError("exception was not propagated")
    assert session.events == ["rollback", "close"]
"""
    elif "repository" in low or "read" in low:
        focus = "чтение через repository/session"
        signature = f"{func}(session_factory, task_id)"
        condition = (
            f"Напиши функцию `{func}`. Она открывает session, читает объект `Task` по `task_id` "
            "через `session.get(...)` и закрывает session после чтения."
        )
        example = f"`{signature}` возвращает найденный объект и не делает commit для обычного чтения."
        solution = f"""def {func}(session_factory, task_id):
    if task_id is None:
        return None
    session = session_factory()
    try:
        return session.get("Task", task_id)
    finally:
        session.close()
"""
        test_code = f"""from solution import {func}


class FakeSession:
    def __init__(self):
        self.events = []
        self.data = {{7: {{"id": 7, "title": "Read"}}}}
    def get(self, model, key):
        self.events.append(("get", model, key))
        return self.data.get(key)
    def close(self):
        self.events.append("close")


def test_repository_read_closes_session():
    session = FakeSession()
    assert {func}(lambda: session, 7) == {{"id": 7, "title": "Read"}}
    assert session.events == [("get", "Task", 7), "close"]


def test_none_id_does_not_open_session():
    opened = []
    assert {func}(lambda: opened.append("opened"), None) is None
    assert opened == []
"""
    elif "commit" in low:
        focus = "граница commit после записи"
        signature = f"{func}(session_factory, item)"
        condition = (
            f"Напиши функцию `{func}`. Она открывает session, добавляет объект через `add`, "
            "делает `commit`, обновляет объект через `refresh` и закрывает session."
        )
        example = f"`{signature}` возвращает тот же объект после `refresh`."
        solution = f"""def {func}(session_factory, item):
    session = session_factory()
    try:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
"""
        test_code = f"""from solution import {func}


class FakeSession:
    def __init__(self):
        self.events = []
    def add(self, item):
        self.events.append(("add", item["title"]))
    def commit(self):
        self.events.append("commit")
    def refresh(self, item):
        item["id"] = 10
        self.events.append("refresh")
    def rollback(self):
        self.events.append("rollback")
    def close(self):
        self.events.append("close")


def test_commit_boundary_refreshes_item():
    session = FakeSession()
    item = {{"title": "Write"}}
    assert {func}(lambda: session, item) is item
    assert item["id"] == 10
    assert session.events == [("add", "Write"), "commit", "refresh", "close"]
"""
    else:
        focus = "жизненный цикл session"
        signature = f"{func}(session_factory, action)"
        condition = (
            f"Напиши функцию `{func}`. Она открывает session, вызывает `action(session)`, "
            "делает `commit()` при успехе и всегда вызывает `close()`."
        )
        example = f"`{signature}` возвращает результат action и оставляет порядок событий `commit`, `close`."
        solution = f"""def {func}(session_factory, action):
    session = session_factory()
    try:
        result = action(session)
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
"""
        test_code = f"""from solution import {func}


class FakeSession:
    def __init__(self):
        self.events = []
    def commit(self):
        self.events.append("commit")
    def rollback(self):
        self.events.append("rollback")
    def close(self):
        self.events.append("close")


def test_success_commit_and_close():
    session = FakeSession()
    assert {func}(lambda: session, lambda opened: opened.events.append("action") or "ok") == "ok"
    assert session.events == ["action", "commit", "close"]
"""

    if "unit of work" in lesson["title"].lower():
        lines = solution.splitlines()
        if lines and lines[0].startswith("def "):
            lines.insert(1, '    boundary_marker = "unit_of_work"')
            lines.insert(2, "    assert boundary_marker")
            solution = "\n".join(lines) + "\n"

    step["body_markdown"] = (
        f"**Коротко:** отработай {focus} в уроке {lesson_title}.\n\n"
        f"### Условие\n{condition}\n\n"
        f"### Вход\nАргументы функции `{signature}`.\n\n"
        f"### Выход\nРезультат функции или исходное исключение, если операция упала.\n\n"
        f"### Пример\n{example}\n\n"
        "### Что проверить\n"
        "Проверь порядок событий на fake session. Для чтения не делай commit, для записи не забывай close.\n\n"
        f"{SELF_CHECK}"
    )
    step["editor_initial_code"] = f"def {func}(*args, **kwargs):\n    pass\n"
    step["solution_code"] = solution
    step["checker"] = {
        "type": "python_pytest",
        "timeout_sec": checker.get("timeout_sec", 5),
        "test_code": test_code,
        "scenario_id": f"{step['id']}_orm_{slugify(focus)}",
    }
    step["hints"] = [
        "Сначала напиши happy path без обработки ошибок.",
        "Потом добавь finally, чтобы close вызывался всегда.",
        "Порядок событий важен: проверка сравнивает список вызовов.",
    ]
    return True


FINAL_GATE_REQUIREMENTS = {
    "ТЗ": ("Problem", "Users", "Scope", "Out of scope", "Acceptance"),
    "User stories": ("Actor", "Story", "Value", "Acceptance", "Priority"),
    "схема БД": ("Entities", "Relations", "Constraints", "Indexes", "Rollback"),
    "API contract": ("Method", "Path", "Request", "Response", "Errors"),
    "Git workflow": ("Branch", "Commit", "Pull request", "Conflict rule", "Release tag"),
    "FastAPI структура": ("Packages", "Routers", "Settings", "Dependencies", "Startup"),
    "SQLAlchemy models": ("Models", "Columns", "Relations", "Loading", "Repository"),
    "Alembic migrations": ("Revision", "Upgrade", "Downgrade", "Data safety", "Rollback"),
    "Auth": ("Login", "Access token", "Refresh token", "Protected route", "Unauthorized"),
    "CRUD": ("Create", "Read", "Update", "Delete", "Validation"),
    "Tests": ("Unit", "Integration", "Fixture", "Negative case", "Coverage"),
    "Checks": ("Unit", "Integration", "Fixture", "Negative case", "Coverage"),
    "Docker": ("Dockerfile", "Compose", "Env", "Healthcheck", "Logs"),
    "CI/CD": ("Workflow", "Jobs", "Secrets", "Image build", "Deploy gate"),
    "AI integration": ("Mock provider", "Prompt", "Schema", "Timeout", "No-answer"),
    "Logging": ("Request id", "Level", "Error", "Audit", "No secrets"),
    "README": ("Install", "Run", "Env", "API examples", "Troubleshooting"),
    "Deploy": ("Host", "Nginx", "SSL", "Healthcheck", "Rollback"),
    "Final defense": ("Demo path", "Architecture", "Known risk", "Evidence", "Decision"),
}


def final_gate_sections(gate: str) -> tuple[str, ...]:
    for key, value in FINAL_GATE_REQUIREMENTS.items():
        if key.lower() in gate.lower():
            return value
    return ("Goal", "Files", "Command", "Failure", "Decision")


def set_final_gate_step(lesson: dict, step: dict) -> bool:
    if step.get("type") != "project":
        return False
    gate = display_title(lesson["title"].split(":", 1)[1].strip())
    role = role_for(step)
    lesson_slug = path_slug(lesson["id"])
    role_slug = path_slug(role)
    main_file = f"docs/final_project/{lesson_slug}_{role_slug}.md"
    evidence_file = f"artifacts/{lesson_slug}_{step['order']:02d}_{role_slug}.txt"
    sections = final_gate_sections(gate)
    if role == "acceptance":
        focus = f"сформулируй критерии приёмки для gate {gate}: {sections[0]}, {sections[1]}, {sections[2]}."
        required = f"В `{main_file}` должны быть разделы `{sections[0]}`, `{sections[1]}`, `{sections[2]}` и `Reject`."
        grep = f"{sections[0]}|{sections[1]}|{sections[2]}|Reject"
    elif role == "deliverable":
        focus = f"перечисли файлы и команды, по которым ментор примет gate {gate}."
        required = f"В `{main_file}` должны быть разделы `Files`, `Command`, `{sections[3]}` и `Evidence`."
        grep = f"Files|Command|{sections[3]}|Evidence"
    elif role == "negative":
        focus = f"опиши отказной путь для gate {gate}: неправильный ввод, запрет доступа, пустые данные или сбой команды."
        required = f"В `{main_file}` должны быть разделы `Bad input`, `Expected failure`, `{sections[4]}` и `Fix`."
        grep = f"Bad input|Expected failure|{sections[4]}|Fix"
    elif role == "review":
        focus = f"подготовь заметки ревью по gate {gate}: риск, спорное решение и что проверять первым."
        required = f"В `{main_file}` должны быть разделы `Risk`, `Decision`, `Review focus` и `{sections[2]}`."
        grep = f"Risk|Decision|Review focus|{sections[2]}"
    elif role == "final":
        focus = f"собери итоговую сдачу gate {gate} с доказательством выполнения."
        required = f"В `{main_file}` должны быть разделы `Done`, `Evidence`, `Command`, `Pass/Fail` и `{sections[0]}`."
        grep = f"Done|Evidence|Command|Pass/Fail|{sections[0]}"
    else:
        focus = f"собери smoke-проверку gate {gate} перед финальной защитой."
        required = f"В `{main_file}` должны быть разделы `Check`, `Command`, `Expected`, `Actual` и `{sections[1]}`."
        grep = f"Check|Command|Expected|Actual|{sections[1]}"

    step["body_markdown"] = (
        f"**Коротко:** {focus}\n\n"
        f"### Условие\n{required} "
        f"В `{evidence_file}` запиши короткий итог: какую команду, файл или route ты проверил и какой результат получил.\n\n"
        f"### Что сдать\n"
        f"Сдай оба файла. В основном файле должны быть конкретные названия файлов, endpoint, миграций, workflow или команд, относящихся к gate {gate}.\n\n"
        f"### Что проверить\n"
        f"Если другой человек не сможет повторить проверку по твоему описанию, gate {gate} ещё не готов.\n\n"
        f"{SELF_CHECK}"
    )
    commands = [
        command_test_file(main_file),
        command_test_file(evidence_file),
        command_grep(main_file, grep),
        command_grep(main_file, re.escape(gate)),
    ]
    checker = {
        "type": "ide_plugin",
        "required_files": [main_file, evidence_file],
        "commands": commands,
        "timeout_sec": 12,
        "hidden_tests": commands[:],
        "quality_gate": f"final_{role}",
        "scenario_id": f"{step['id']}_final_{role}",
    }
    if "git" in lesson["title"].lower():
        checker["git_checks"] = {
            "must_have_clean_worktree": True,
            "forbidden_untracked_files": True,
            "min_commits": 1,
        }
    step["checker"] = checker
    step["solution_code"] = (
        f"{main_file}: sections for {gate} / {role}.\n"
        f"{evidence_file}: command or route evidence for {gate}.\n"
    )
    step["hints"] = [
        "Начни с одного конкретного файла или endpoint, который относится к gate.",
        "Отдельно запиши отрицательный путь: без него gate нельзя считать устойчивым.",
        "Фраза без команды или критерия pass/fail не помогает ревьюеру.",
    ]
    return True


def set_http_body(lesson: dict, step: dict) -> bool:
    checker = step.get("checker") or {}
    if checker.get("type") != "http_api":
        return False
    tests = checker.get("public_tests") or []
    if not tests:
        return False
    first = tests[0]
    method = first.get("method", "GET")
    path = first.get("path", "/")
    status = first.get("expected_status", 200)
    json_hint = first.get("expected_json_subset") or first.get("expected_json") or {}
    lesson_title = display_title(lesson["title"])
    step["title"] = display_title(step.get("title", ""))
    step["body_markdown"] = (
        f"**Коротко:** реализуй {method} {path} в уроке {lesson_title}.\n\n"
        f"### Условие\n"
        f"Добавь endpoint `{method} {path}`. Он должен вернуть HTTP {status}. "
        f"JSON-форма ответа должна совпадать с контрактом урока; ключи из примера не переименовывай.\n\n"
        f"### Вход\nHTTP-запрос `{method} {path}`. Если в проверке есть request body, опиши его через Pydantic-модель.\n\n"
        f"### Выход\nHTTP {status} и JSON, совместимый с примером `{json.dumps(json_hint, ensure_ascii=False)}`.\n\n"
        f"### Что проверить\n"
        f"Сверь method и path буквально. Для ошибки верни HTTPException или валидацию FastAPI, а не строку с текстом ошибки.\n\n"
        f"{SELF_CHECK}"
    )
    return True


def main() -> int:
    course = load_course()
    stats = Counter()

    for module, lesson, step in iter_steps(course):
        before = json.dumps(step, ensure_ascii=False, sort_keys=True)
        step["body_markdown"] = clean_body_text(step.get("body_markdown", ""))
        if set_domain_theory_step(module, lesson, step):
            stats["domain_theory_steps"] += 1
        if lesson["title"].startswith("Финальный проект:"):
            if set_final_gate_step(lesson, step):
                stats["final_gate_projects"] += 1
            if set_final_alembic_practice_step(lesson, step):
                stats["final_alembic_practice_steps"] += 1
        elif (step.get("checker") or {}).get("type") == "ide_plugin" and step.get("type") in {"practice", "project"}:
            if set_ide_step(module, lesson, step):
                stats["ide_steps"] += 1
        if set_http_body(lesson, step):
            stats["http_bodies"] += 1
        if set_exam1_python_core_step(lesson, step):
            stats["exam1_python_core_steps"] += 1
        if set_exam3_practice_step(lesson, step):
            stats["exam3_practice_steps"] += 1
        if set_oop_abstraction_step(module, lesson, step):
            stats["oop_abstraction_steps"] += 1
        if set_orm_pytest_step(module, lesson, step):
            stats["orm_pytest_steps"] += 1
        after = json.dumps(step, ensure_ascii=False, sort_keys=True)
        if before != after:
            stats["changed_steps"] += 1

    sql_index_by_skill = defaultdict(int)
    for _, lesson, step in iter_steps(course):
        if (step.get("checker") or {}).get("type") == "sql_query":
            skill = detect_sql_skill(lesson["title"], step["title"])
            if set_sql_query_step(lesson, step, sql_index_by_skill[skill]):
                stats["sql_query_steps"] += 1
                sql_index_by_skill[skill] += 1

    save_course(course)
    update_reports(course)
    audit = independent_audit(course)
    write_quality_audit(audit)
    write_diversity_report(course, stats)
    print("coursewide_diversity_pass")
    for key in sorted(stats):
        print(f"{key}={stats[key]}")
    return 0


def normalized_intro(text: str) -> str:
    text = re.sub(r"`[^`]+`", "`X`", text or "")
    text = re.sub(r"m\d+_l\d+[^\s`]*", "ID", text)
    text = re.sub(r"\d+", "N", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def write_diversity_report(course: dict, stats: Counter) -> None:
    groups = Counter()
    examples = defaultdict(list)
    for _, lesson, step in iter_steps(course):
        if step["type"] not in {"practice", "project"}:
            continue
        intro = " ".join((step.get("body_markdown") or "").splitlines()[:10])
        key = normalized_intro(intro[:900])
        groups[key] += 1
        if len(examples[key]) < 5:
            examples[key].append(f"{lesson['id']} / {step['id']} / {step['title']}")
    repeated = [(key, count) for key, count in groups.items() if count > 3]
    repeated.sort(key=lambda item: item[1], reverse=True)
    lines = [
        "# Coursewide diversity report",
        "",
        "## Changed steps",
        *[f"- {key}: {value}" for key, value in sorted(stats.items())],
        "",
        "## Repeated intro groups over 3",
    ]
    if repeated:
        for key, count in repeated[:30]:
            lines.append(f"- count {count}: {key[:240]}")
            for item in examples[key]:
                lines.append(f"  - {item}")
    else:
        lines.append("- none")
    (ROOT / "coursewide_diversity_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
