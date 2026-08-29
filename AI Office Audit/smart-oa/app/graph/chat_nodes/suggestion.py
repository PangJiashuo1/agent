"""
审批建议节点
调用反思补搜子图，生成高质量审批建议
"""

from app.graph.chat_state import ChatState
from app.common.mysql_client import execute_query


def _get_employee_leave_stats(employee_id: str) -> dict:
    """查询员工本年度请假统计"""
    stats = {
        "approved_days": 0,      # 已批准天数
        "pending_count": 0,      # 待审批数量
        "approved_count": 0,     # 已批准次数
        "recent_leaves": [],     # 最近请假记录
    }

    # 已批准的请假天数（本年度）
    result = execute_query(
        """SELECT COALESCE(SUM(leave_days), 0) as total
           FROM leave_applications
           WHERE employee_id = %s AND status = 'approved'
           AND YEAR(start_date) = YEAR(CURDATE())""",
        (employee_id,),
    )
    if result:
        stats["approved_days"] = result[0]["total"]

    # 待审批数量
    result = execute_query(
        """SELECT COUNT(*) as cnt FROM leave_applications
           WHERE employee_id = %s AND status = 'pending'""",
        (employee_id,),
    )
    if result:
        stats["pending_count"] = result[0]["cnt"]

    # 已批准次数
    result = execute_query(
        """SELECT COUNT(*) as cnt FROM leave_applications
           WHERE employee_id = %s AND status = 'approved'
           AND YEAR(start_date) = YEAR(CURDATE())""",
        (employee_id,),
    )
    if result:
        stats["approved_count"] = result[0]["cnt"]

    # 最近 3 条请假记录
    recent = execute_query(
        """SELECT leave_type, leave_days, start_date, end_date, status
           FROM leave_applications
           WHERE employee_id = %s
           ORDER BY created_at DESC LIMIT 3""",
        (employee_id,),
    )
    stats["recent_leaves"] = recent

    return stats


def _get_team_leave_conflicts(department: str, start_date: str, end_date: str) -> list:
    """查询同期同部门其他人的请假情况"""
    if not department or not start_date or not end_date:
        return []

    conflicts = execute_query(
        """SELECT employee_name, leave_type, leave_days, start_date, end_date
           FROM leave_applications
           WHERE department = %s AND status IN ('approved', 'pending')
           AND start_date <= %s AND end_date >= %s""",
        (department, end_date, start_date),
    )
    return conflicts


def create_suggestion_node(llm):
    """
    工厂函数：返回审批建议节点
    当前为简化实现（直接用 LLM 生成建议），
    后续接入 reflection_search.py 反思补搜子图
    """

    def suggestion(state: ChatState) -> dict:
        info = state.get("extracted_info", {})
        context = state.get("conversation_context", {})
        user_message = state.get("user_message", "")

        employee_id = context.get("user_id", "")

        # 从数据库查询员工请假统计
        leave_stats = _get_employee_leave_stats(employee_id)

        # 查询同期同部门请假冲突
        conflicts = _get_team_leave_conflicts(
            context.get("user_department", ""),
            info.get("start_date", ""),
            info.get("end_date", ""),
        )

        # 构造冲突信息
        conflict_text = "无"
        if conflicts:
            lines = []
            for c in conflicts:
                lines.append(
                    f"  - {c['employee_name']}: {c['leave_type']} "
                    f"{c['start_date']}~{c['end_date']}（{c['leave_days']}天，{c['status']}）"
                )
            conflict_text = "\n".join(lines)

        # 构造最近请假记录
        recent_text = "无"
        if leave_stats["recent_leaves"]:
            lines = []
            for r in leave_stats["recent_leaves"]:
                lines.append(
                    f"  - {r['leave_type']} {r['start_date']}~{r['end_date']}"
                    f"（{r['leave_days']}天，{r['status']}）"
                )
            recent_text = "\n".join(lines)

        prompt = f"""你是一位专业的HR顾问，请根据以下信息给出审批建议：

当前用户：{context.get('user_name', '')}（{context.get('user_role', '')}，{context.get('user_department', '')}）

请假信息：
- 类型：{info.get('leave_type', '未知')}
- 天数：{info.get('leave_days', '未知')}
- 日期：{info.get('start_date', '未知')} ~ {info.get('end_date', '未知')}
- 原因：{info.get('reason', '未说明')}

员工本年度请假统计：
- 已批准天数：{leave_stats['approved_days']}天
- 已批准次数：{leave_stats['approved_count']}次
- 待审批数量：{leave_stats['pending_count']}条
- 最近请假记录：
{recent_text}

同期同部门请假情况（可能影响排班）：
{conflict_text}

用户问题：{user_message}

请给出：
1. 建议是否批准
2. 理由（结合年假余额、团队排班等因素）
3. 需要注意的事项
简洁明了，不超过300字。"""

        response = llm.invoke(prompt)

        # TODO: 后续接入反思补搜子图
        # from app.graph.reflection_search import run_reflection_search
        # suggestion = run_reflection_search(info, context)

        return {"task_result": response.content}

    return suggestion
