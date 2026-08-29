"""
审批节点
主管/HR 审批请假申请
"""

import re
from app.graph.chat_state import ChatState
from app.tools.leave_service import LeaveService


def create_approve_node():
    """工厂函数：返回审批节点"""

    def approve(state: ChatState) -> dict:
        info = state.get("extracted_info", {})
        context = state.get("conversation_context", {})
        user_message = state.get("user_message", "")

        service = LeaveService()

        app_id = info.get("app_id", "")
        # 尝试从消息中提取多个申请编号
        app_ids = re.findall(r"leave_\w+", user_message)
        if not app_ids and app_id:
            app_ids = [app_id]

        # 从消息中判断决策
        decision = info.get("decision", "")
        if not decision:
            if any(w in user_message for w in ["同意", "批准", "通过", "approve"]):
                decision = "approved"
            elif any(w in user_message for w in ["拒绝", "驳回", "不批", "reject"]):
                decision = "rejected"
            else:
                decision = "approved"

        comments = info.get("comments", "无")

        results = []
        for single_id in app_ids:
            result = service.approve_application(
                app_id=single_id,
                approver_role=context.get("user_role", ""),
                decision=decision,
                comments=comments,
            )
            results.append(f"{single_id}: {result.get('message', '操作失败')}")

        if not results:
            return {"task_result": "未找到要审批的申请编号，请提供申请编号（格式：leave_xxx）"}

        return {"task_result": "\n".join(results)}

    return approve
