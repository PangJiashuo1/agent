"""
删除申请节点
员工撤回/删除自己的请假申请（仅限 pending 状态）
"""

import re
from app.graph.chat_state import ChatState
from app.tools.leave_service import LeaveService


def create_delete_node():
    """工厂函数：返回删除申请节点"""

    def delete_application(state: ChatState) -> dict:
        info = state.get("extracted_info", {})
        context = state.get("conversation_context", {})
        user_message = state.get("user_message", "")

        service = LeaveService()

        # 从消息或提取信息中获取申请编号
        app_id = info.get("app_id", "")
        app_ids = re.findall(r"leave_\w+", user_message)
        if not app_ids and app_id:
            app_ids = [app_id]

        if not app_ids:
            return {"task_result": "请提供要删除的申请编号（格式：leave_xxx）"}

        results = []
        for single_id in app_ids:
            result = service.delete_application(
                app_id=single_id,
                employee_id=context.get("user_id", ""),
            )
            results.append(f"{single_id}: {result.get('message', '操作失败')}")

        return {"task_result": "\n".join(results)}

    return delete_application
