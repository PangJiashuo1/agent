"""
对话路由
POST   /chat/stream           - SSE 流式对话
GET    /chat/sessions         - 获取当前用户会话列表
DELETE /chat/session/{id}     - 删除会话
"""

import json
import uuid
import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.common.redis_client import get_redis_client
from app.middleware.auth_middleware import get_current_user
from app.graph.chat_agent import get_chat_graph

router = APIRouter(prefix="/chat", tags=["对话"])


# ---------------------------------------------------------------------------
# SSE 流式对话
# ---------------------------------------------------------------------------
@router.post("/stream")
async def chat_stream(
    request: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    接收用户消息，通过 LangGraph 工作流生成回复，以 SSE 流式返回。

    请求体:
        {
            "thread_id": "可选，留空则新建会话",
            "user_message": "用户输入内容"
        }
    """
    graph, _ = get_chat_graph()
    thread_id = request.get("thread_id") or str(uuid.uuid4())
    user_message = request.get("user_message", "")

    if not user_message.strip():
        return {"error": "user_message 不能为空"}

    async def event_generator():
        # 构建初始状态（与文档保持一致）
        initial_state = {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().isoformat(),
                }
            ],
            "user_message": user_message,
            "intent": "",
            "extracted_info": {},
            "current_task": "",
            "task_result": "",
            "response": "",
            "conversation_context": {
                "user_id": current_user.get("username"),
                "user_role": current_user.get("role"),
                "user_department": current_user.get("department"),
                "user_name": current_user.get("name"),
            },
            "needs_search": False,
            "search_results": "",
            "iteration_count": 0,
        }
        config = {"configurable": {"thread_id": thread_id}}

        # 在线程池中执行 LangGraph（避免阻塞事件循环）
        result = await asyncio.to_thread(graph.invoke, initial_state, config)

        # 打字机效果：每 3 个字符发送一次
        response_text = result.get("response", "")
        for i in range(0, len(response_text), 3):
            chunk = response_text[i : i + 3]
            yield f"event: token\ndata: {json.dumps({'token': chunk}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)

        # 完成事件
        yield (
            f"event: complete\ndata: "
            f"{json.dumps({'thread_id': thread_id, 'response': response_text}, ensure_ascii=False)}\n\n"
        )

        # 更新会话元数据到 Redis
        redis_client = get_redis_client()
        metadata_key = f"session_metadata:{current_user['username']}"
        redis_client.hset(
            metadata_key,
            thread_id,
            json.dumps(
                {
                    "last_message": user_message[:50],
                    "updated_at": datetime.now().isoformat(),
                },
                ensure_ascii=False,
            ),
        )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


# ---------------------------------------------------------------------------
# 会话列表
# ---------------------------------------------------------------------------
@router.get("/sessions")
async def list_sessions(current_user: dict = Depends(get_current_user)):
    """获取当前用户的所有会话元数据"""
    redis_client = get_redis_client()
    metadata_key = f"session_metadata:{current_user['username']}"
    sessions_raw = redis_client.hgetall(metadata_key)

    sessions = []
    for thread_id, meta_json in sessions_raw.items():
        meta = json.loads(meta_json)
        sessions.append({"thread_id": thread_id, **meta})

    # 按更新时间倒序
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return {"sessions": sessions}


# ---------------------------------------------------------------------------
# 删除会话
# ---------------------------------------------------------------------------
@router.delete("/session/{thread_id}")
async def delete_session(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
):
    """删除指定会话及其所有 Checkpoint"""
    redis_client = get_redis_client()

    # 1. 删除业务元数据
    metadata_key = f"session_metadata:{current_user['username']}"
    redis_client.hdel(metadata_key, thread_id)

    # 2. 使用 LangGraph 官方方法删除 Checkpoint
    graph, _ = get_chat_graph()
    if hasattr(graph, "checkpointer"):
        graph.checkpointer.delete_thread(thread_id)

    return {"message": f"会话 {thread_id} 已删除"}
