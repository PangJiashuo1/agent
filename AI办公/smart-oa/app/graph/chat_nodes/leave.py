"""
提交请假节点
从状态中提取请假信息，调用工具层写入数据库
"""

from app.graph.chat_state import ChatState
from app.tools.leave_service import LeaveService


def create_leave_submit_node():
    """工厂函数：返回提交请假节点"""

    def submit_leave(state: ChatState) -> dict:
        info = state.get("extracted_info", {})
        context = state.get("conversation_context", {})

        service = LeaveService()

        result = service.create_application(
            employee_id=context.get("user_id", ""),
            employee_name=context.get("user_name", ""),
            employee_role=context.get("user_role", "employee"),
            department=context.get("user_department", ""),
            leave_type=info.get("leave_type", ""),
            leave_days=info.get("leave_days", 0),
            start_date=info.get("start_date", ""),
            end_date=info.get("end_date", ""),
            reason=info.get("reason", ""),
        )

        return {
            "task_result": result.get("message", "提交失败"),
        }

    return submit_leave
