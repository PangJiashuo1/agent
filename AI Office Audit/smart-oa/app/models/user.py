"""
用户相关 Pydantic 模型
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """登录请求"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    name: str
    role: str
    department: Optional[str] = None
    position: Optional[str] = None


class TokenResponse(BaseModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
