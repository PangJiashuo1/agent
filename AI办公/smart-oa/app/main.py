"""
小滴智能OA - FastAPI 应用入口
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.common.redis_client import close_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 小滴智能OA 启动中...")
    settings = get_settings()
    print(f"   LLM 模型：{settings.llm_model}")
    print(f"   MySQL：{settings.db_host}:{settings.db_port}/{settings.db_name}")
    print(f"   Redis：{settings.redis_url}")
    yield
    # 关闭连接
    close_redis_client()
    print("👋 小滴智能OA 已关闭")


app = FastAPI(
    title="小滴智能OA办公审核AI系统",
    description="基于 LangGraph 的对话式OA系统，通过自然语言完成请假申请、审批、查询等操作",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置（允许前端 Vue3 跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "小滴智能OA办公审核AI系统",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
