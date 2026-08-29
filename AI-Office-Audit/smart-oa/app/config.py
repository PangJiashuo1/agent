"""
小滴智能OA - 配置管理
从 .env 文件加载所有配置项
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# 定位 .env 文件（位于 app/ 目录下）
ENV_PATH = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    """应用全局配置"""

    # --- LLM ---
    llm_api_key: str = ""
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen3.5-plus"

    # --- MySQL ---
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "root123"
    db_name: str = "oa_system"

    # --- Redis ---
    redis_url: str = "redis://127.0.0.1:6379"

    # --- Tavily ---
    tavily_api_key: str = ""

    # --- JWT ---
    jwt_secret_key: str = "smart-oa-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    # --- Server ---
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    @property
    def mysql_connection_config(self) -> dict:
        return {
            "host": self.db_host,
            "port": self.db_port,
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name,
            "charset": "utf8mb4",
        }

    model_config = {"env_file": str(ENV_PATH), "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
