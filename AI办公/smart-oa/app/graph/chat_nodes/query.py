"""
查询节点
处理查询我的申请状态 和 查询待审批事项
"""

from app.graph.chat_state import ChatState
from app.tools.leave_service import LeaveService


def create_query_node():
    """工厂函数：返回查询申请状态节点"""

    def query(state: ChatState) -> dict:
        context = state.get("conversation_context", {})
        service = LeaveService()

        applications = service.query_by_employee(context.get("user_id", ""))

        if not applications:
            return {"task_result": "您目前没有请假申请记录。"}

        lines = ["📋 您的请假申请：\n"]
        for app in applications:
            status_icon = {
                "pending": "⏳",
                "approved": "✅",
                "rejected": "❌",
                "finished": "🏁",
            }.get(app["status"], "❓")
            lines.append(
                f"- {status_icon} [{app['id']}] {app['leave_type']} "
                f"{app['start_date']} ~ {app['end_date']}（{app['leave_days']}天）"
                f"  状态: {app['status']}"
            )

        return {"task_result": "\n".join(lines)}

    return query


def create_query_pending_node():
    """工厂函数：返回查询待审批事项节点"""

    def query_pending(state: ChatState) -> dict:
        context = state.get("conversation_context", {})
        service = LeaveService()

        applications = service.query_pending(context.get("user_role", ""))

        if not applications:
            return {"task_result": "目前没有待审批的申请。"}

        lines = ["📋 待审批申请列表：\n"]
        for app in applications:
            lines.append(
                f"- 📝 [{app['id']}] {app['employee_name']}（{app['department']}）"
                f"\n  {app['leave_type']} {app['start_date']} ~ {app['end_date']}"
                f"（{app['leave_days']}天）"
                f"\n  原因: {app.get('reason', '无')}"
            )

        return {"task_result": "\n".join(lines)}

    return query_pending
