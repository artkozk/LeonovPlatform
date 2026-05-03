import sqlite3
from solution import create_db, add_task, list_tasks


def test_add_task(tmp_path):
    db_path = tmp_path / 'tasks.db'
    create_db(db_path)
    add_task(db_path, 'Buy milk')
    assert list_tasks(db_path)[0]['title'] == 'Buy milk'
