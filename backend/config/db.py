import os
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Pool:
    def __init__(self):
        self._pool = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=1,
            blocking=True,
            host=os.environ.get("DB_HOST", "127.0.0.1").strip("[]"),
            user=os.environ.get("DB_USER", "root").strip("[]"),
            password=os.environ.get("DB_PASSWORD", "").strip("[]"),
            database=os.environ.get("DB_NAME", "hrms_db").strip("[]"),
            port=int(os.environ.get("DB_PORT", "3306")),
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=True,
        )

    def query(self, sql, params=None):
        conn = self._pool.connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or [])
                return cursor.fetchall()
        finally:
            conn.close()

    def execute(self, sql, params=None):
        conn = self._pool.connection()
        try:
            with conn.cursor() as cursor:
                affected = cursor.execute(sql, params or [])
                insert_id = cursor.lastrowid
                return {
                    "insert_id": insert_id,
                    "affected_rows": affected
                }
        finally:
            conn.close()


pool = Pool()