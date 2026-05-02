INSERT INTO users VALUES (1, 'Анна', 1), (2, 'Олег', 1), (3, 'Маша', 0), (4, 'Лена', 1);
INSERT INTO products VALUES (1, 'Книга', 700), (2, 'Курс', 5000), (3, 'Мышь', 1200);
INSERT INTO orders VALUES (1, 1, 5700, 'paid'), (2, 2, 1200, 'new'), (3, 1, 700, 'paid');
INSERT INTO order_items VALUES (1, 1, 1, 1), (2, 1, 2, 1), (3, 2, 3, 1), (4, 3, 1, 1);
INSERT INTO payments VALUES (1, 1, 5700, 'paid'), (2, 2, 1200, 'pending'), (3, 3, 700, 'paid');
