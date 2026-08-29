"""
Redis 连接管理
提供全局 Redis 客户端，供 Checkpoint、Store、会话元数据使用
"""

import redis
from app.config import get_settings

_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    """获取全局 Redis 客户端（懒加载单例）"""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _redis_client


def close_redis_client():
    """关闭 Redis 连接（应用退出时调用）"""
    global _redis_client
    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
