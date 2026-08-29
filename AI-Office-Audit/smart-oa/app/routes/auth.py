"""
认证路由
POST /auth/login  - 用户登录，返回 JWT Token
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
import bcrypt

from app.common.mysql_client import execute_query
from app.middleware.auth_middleware import create_access_token
from app.models.user import UserLogin, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLogin):
    """用户登录"""
    # 1. 查询用户
    users = execute_query(
        "SELECT * FROM users WHERE username = %s",
        (request.username,),
    )
    if not users:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    user = users[0]

    # 2. 校验密码（bcrypt）
    if not bcrypt.checkpw(
        request.password.encode("utf-8"),
        user["password"].encode("utf-8"),
    ):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 3. 生成 JWT
    token_data = {
        "username": user["username"],
        "role": user["role"],
        "department": user["department"] or "",
        "name": user["name"],
    }
    access_token = create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user["id"],
            username=user["username"],
            name=user["name"],
            role=user["role"],
            department=user["department"],
            position=user["position"],
        ),
    )
