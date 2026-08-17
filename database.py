import sqlite3
from pathlib import Path
from datetime import datetime
from uuid import uuid4

DB_FILE = Path(__file__).with_name("study.db")  # 数据库文件

def get_connection():  # 创建数据库连接
    connection = sqlite3.connect(DB_FILE) # 创建数据库连接
    connection.row_factory = sqlite3.Row  # 让查询结果支持按列名访问
    return connection

def init_db():  # 初始化数据库
    connection = get_connection() # 创建数据库连接

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS records(
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
                    CHECK (completed IN (0, 1)),
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
            """
        )
        connection.commit()
    finally:
        connection.close()

def insert_record(content):
    record_id = str(uuid4())

    created_at = (
        datetime.now()
        .astimezone()
        .isoformat(timespec="seconds")
    )

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO records (
                id,
                content,
                completed,
                created_at,
                updated_at
            )
            VALUES (?,?,?,?,?)
            """,
            (
                record_id,
                content,
                False,
                created_at,
                None
            )
        )
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "id": record_id,
        "content": content,
        "completed": False,
        "created_at": created_at,
        "updated_at": None
    }

def row_to_record(row): # 将数据库行转换成字典
    if row is None: # 判断行是否为空(提前处理)
        return None

    record = dict(row)  # 将行转换为字典
    record["completed"] = bool(record["completed"])

    return record

def count_records(
        q : str | None = None,  # 查询条件
        completed : bool | None = None
):

    connection = get_connection()

    sql = """
        SELECT COUNT(*) AS total
        FROM records
    """

    conditions = []
    values = []

    if q is not None:
        conditions.append("content LIKE ?")
        values.append(f"%{q}%")

    if completed is not None:
       conditions.append("completed = ?")
       values.append(int(completed))

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    try:
        row = connection.execute(
            sql,
            tuple(values)
        ).fetchone()

        return row["total"]

    finally:
        connection.close()

def list_records(
        q: str | None = None,
        completed : bool | None = None,
        limit : int = 10,
        offset : int = 0

):
    connection = get_connection()

    sql = """
        SELECT
            id,
            content,
            completed,
            created_at,
            updated_at
        FROM records
    """

    conditions = []
    values = []

    if q is not None:
        conditions.append("content LIKE ?")
        values.append(f"%{q}%")

    if completed is not None:
        conditions.append("completed = ?")
        values.append(int(completed))

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY created_at DESC"
    sql += " LIMIT ? OFFSET ?"
    values.extend([limit, offset])

    try:
        rows = connection.execute(
            sql,
            tuple(values)
        ).fetchall()  # 获取所有行

        return [
            row_to_record(row)
            for row in rows
        ]  #返回一个字典组成的列表

    finally:
        connection.close()

def get_record_by_id(record_id):  # 根据ID获取一条记录
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                content,
                completed,
                created_at,
                updated_at
            FROM records
            WHERE id = ?
            """,
            (record_id,)
        ).fetchone()

        return row_to_record(row)  # 将行转换为字典

    finally:
        connection.close()

def update_record_by_id(record_id,updates):
    #动态字段
    set_parts = []
    values = []

    if "content" in updates:
        set_parts.append("content = ?")
        values.append(updates["content"])

    if "completed" in updates:
        set_parts.append("completed = ?")
        values.append(updates["completed"])

    if not set_parts:
        raise ValueError("没有可以修改的字段")

    updated_at= (
        datetime.now()
        .astimezone()
        .isoformat(timespec="seconds")
    )

    set_parts.append("updated_at = ?")
    values.append(updated_at)
    values.append(record_id)

    sql =f"""
        UPDATE records
        SET {",".join(set_parts)}
        WHERE id = ?
    """

    connection = get_connection()

    try:
        cursor = connection.execute(
            sql,
            tuple(values)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return None

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()

    return get_record_by_id(record_id)

def delete_record_by_id(record_id):
    connection = get_connection()  # 创建数据库连接

    try:
        row = connection.execute(
            """
            SELECT
                id,
                content,
                completed,
                created_at,
                updated_at
            FROM records
            WHERE id = ?
            """,
            (record_id,)
        ).fetchone()

        if row is None:
            return None

        delete_record = row_to_record(row)

        connection.execute(
            """
            DELETE FROM records
            WHERE id = ?
            """,
            (record_id,)
        )

        connection.commit()

        return delete_record

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()





if __name__ == "__main__":
    init_db()
    print("数据库初始化完成")
