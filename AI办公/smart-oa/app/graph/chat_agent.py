"""
对话主图构建
创建 LangGraph StateGraph，注册所有节点和边，返回编译后的图实例
"""

from functools import lru_cache

from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.common.redis_client import get_redis_client
from app.graph.chat_state import ChatState
from app.graph.chat_nodes import (
    create_intent_recognition_node,
    create_search_node,
    create_task_router_node,
    create_route_task_execution,
    create_leave_submit_node,
    create_approve_node,
    create_query_node,
    create_query_pending_node,
    create_delete_node,
    create_general_chat_node,
    create_suggestion_node,
    create_response_generator_node,
)


def _build_chat_graph():
    """
    构建并返回 (graph, store) 元组
    - graph: 编译后的 LangGraph 可执行图
    - store: RedisStore 实例（预留，当前未使用）
    """
    settings = get_settings()

    # ------------------------------------------------------------------
    # 1. 初始化 LLM
    # ------------------------------------------------------------------
    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=0.7,
        openai_api_key=settings.llm_api_key,
        openai_api_base=settings.llm_base_url,
    )

    # ------------------------------------------------------------------
    # 2. 初始化 Redis（Checkpoint + Store）
    # ------------------------------------------------------------------
    redis_client = get_redis_client()

    # RedisStore 用于共享知识存储（预留）
    from langgraph.store.redis import RedisStore
    store = RedisStore(redis_client)

    # RedisSaver 用于对话 Checkpoint 持久化
    from langgraph.checkpoint.redis import RedisSaver
    checkpointer = RedisSaver(redis_client=redis_client)

    # ------------------------------------------------------------------
    # 3. 创建所有节点
    # ------------------------------------------------------------------
    nodes = {
        "intent_recognition": create_intent_recognition_node(llm),
        "search": create_search_node(settings.tavily_api_key or None),
        "task_router": create_task_router_node(),
        "task_executor": lambda state: {},  # 占位，仅用于条件路由的源节点
        "submit_leave": create_leave_submit_node(),
        "approve": create_approve_node(),
        "query": create_query_node(),
        "query_pending": create_query_pending_node(),
        "delete": create_delete_node(),
        "suggestion": create_suggestion_node(llm),
        "general_chat": create_general_chat_node(llm),
        "response_generator": create_response_generator_node(llm),
    }

    # 条件路由函数单独取出
    route_func = create_route_task_execution()

    # ------------------------------------------------------------------
    # 4. 构建 StateGraph
    # ------------------------------------------------------------------
    builder = StateGraph(ChatState)

    # 注册节点（排除路由函数）
    for node_name, node_func in nodes.items():
        builder.add_node(node_name, node_func)

    # 配置边
    builder.set_entry_point("intent_recognition")
    builder.add_edge("intent_recognition", "search")
    builder.add_edge("search", "task_router")
    builder.add_edge("task_router", "task_executor")

    # 条件边：task_executor → 具体业务节点
    builder.add_conditional_edges(
        "task_executor",
        route_func,
        {
            "submit_leave": "submit_leave",
            "approve": "approve",
            "query": "query",
            "query_pending": "query_pending",
            "delete": "delete",
            "suggestion": "suggestion",
            "general_chat": "general_chat",
        },
    )

    # 所有业务节点 → response_generator → END
    builder.add_edge("submit_leave", "response_generator")
    builder.add_edge("approve", "response_generator")
    builder.add_edge("query", "response_generator")
    builder.add_edge("query_pending", "response_generator")
    builder.add_edge("delete", "response_generator")
    builder.add_edge("suggestion", "response_generator")
    builder.add_edge("general_chat", "response_generator")

    # response_generator 为终止节点（不添加额外边，自动到 END）

    # ------------------------------------------------------------------
    # 5. 编译图
    # ------------------------------------------------------------------
    graph = builder.compile(checkpointer=checkpointer, store=store)

    return graph, store


@lru_cache()
def get_chat_graph():
    """
    获取全局图实例（单例）
    返回 (graph, store) 元组
    """
    return _build_chat_graph()
