import sqlite3
from solution import create_db, add_task


def test_add_task(tmp_path):
    db_path = tmp_path / 'tasks.db'
    create_db(db_path)
    add_task(db_path, 'Buy milk')
    conn = sqlite3.connect(db_path)
    rows = conn.execute('SELECT title, done FROM tasks').fetchall()
    assert rows == [('Buy milk', 0)]
