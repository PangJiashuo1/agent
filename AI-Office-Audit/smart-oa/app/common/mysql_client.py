"""
MySQL 连接池管理
基于 DBUtils PooledDB 提供线程安全的连接池
"""

import pymysql
from dbutils.pooled_db import PooledDB
from app.config import get_settings

_pool: PooledDB | None = None


def get_pool() -> PooledDB:
    """获取连接池（懒加载单例）"""
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = PooledDB(
            creator=pymysql,
            maxconnections=20,
            mincached=2,
            maxcached=5,
            blocking=True,
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    return _pool


def get_connection():
    """从连接池获取一个数据库连接"""
    return get_pool().connection()


def execute_query(sql: str, params: tuple = None) -> list[dict]:
    """执行查询 SQL，返回结果列表"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def execute_update(sql: str, params: tuple = None) -> int:
    """执行更新 SQL，返回影响行数"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            affected = cursor.execute(sql, params)
            conn.commit()
            return affected
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
