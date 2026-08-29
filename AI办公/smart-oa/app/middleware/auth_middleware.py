"""
JWT 认证中间件
负责生成和校验 JWT Token
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成 JWT Access Token"""
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码并验证 JWT Token"""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """
    FastAPI 依赖注入：从 Authorization 头提取并验证当前用户
    返回格式：{"username": "...", "role": "...", "department": "..."}
    """
    token = credentials.credentials
    payload = decode_token(token)

    username: str = payload.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Token 中缺少用户名")

    return {
        "username": username,
        "role": payload.get("role", "employee"),
        "department": payload.get("department", ""),
        "name": payload.get("name", username),
    }
