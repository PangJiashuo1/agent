"""
任务路由节点
根据意图识别结果，设置 current_task 字段
"""

from app.graph.chat_state import ChatState


def create_task_router_node():
    """工厂函数：返回任务路由节点"""

    # 意图 → 任务类型的映射表
    INTENT_TASK_MAP = {
        "submit_leave": "submit_leave",
        "delete_application": "delete_application",
        "approve": "approve",
        "query_status": "query",
        "query_pending": "query_pending",
        "get_suggestion": "suggestion",
        "needs_search": "general_chat",
        "general_chat": "general_chat",
    }

    def task_router(state: ChatState) -> dict:
        intent = state.get("intent", "general_chat")
        current_task = INTENT_TASK_MAP.get(intent, "general_chat")
        return {"current_task": current_task}

    return task_router


def create_route_task_execution():
    """
    条件路由函数
    根据 current_task 决定下一跳节点名称
    """

    def route_task_execution(state: ChatState) -> str:
        current_task = state.get("current_task", "general_chat")

        route_map = {
            "submit_leave": "submit_leave",
            "approve": "approve",
            "query": "query",
            "query_pending": "query_pending",
            "delete_application": "delete",
            "suggestion": "suggestion",
            "general_chat": "general_chat",
        }
        return route_map.get(current_task, "general_chat")

    return route_task_execution
