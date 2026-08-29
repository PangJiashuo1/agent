"""
LangChain Tools 封装
将业务操作包装为 @tool 装饰器，供 LangGraph agent 调用
"""

import re
from langchain_core.tools import tool
from app.tools.leave_service import LeaveService

_leave_service = LeaveService()


@tool
def submit_leave_application(
    employee_id: str,
    employee_name: str,
    employee_role: str,
    department: str,
    leave_type: str,
    leave_days: int,
    start_date: str,
    end_date: str,
    reason: str,
) -> str:
    """提交请假申请。需要提供员工信息、请假类型、天数、日期和原因。"""
    result = _leave_service.create_application(
        employee_id, employee_name, employee_role, department,
        leave_type, leave_days, start_date, end_date, reason,
    )
    return result["message"]


@tool
def approve_leave_application(
    app_id: str,
    approver_role: str,
    decision: str,
    comments: str = "无",
) -> str:
    """审批请假申请（支持批量审批）。app_id 格式：leave_xxx，多个以逗号分隔。decision: approved 或 rejected。"""
    app_ids = re.findall(r"leave_\w+", app_id)
    results = []
    for single_id in app_ids:
        result = _leave_service.approve_application(single_id, approver_role, decision, comments)
        results.append(f"{single_id}: {result['message']}")
    return "\n".join(results) if results else "未找到有效的申请编号"


@tool
def query_my_applications(employee_id: str) -> str:
    """查询指定员工的所有请假申请列表。"""
    apps = _leave_service.query_by_employee(employee_id)
    if not apps:
        return "暂无请假申请记录"
    lines = []
    for a in apps:
        lines.append(
            f"[{a['id']}] {a['leave_type']} | {a['start_date']}~{a['end_date']} | {a['leave_days']}天 | 状态：{a['status']}"
        )
    return "\n".join(lines)


@tool
def query_pending_approvals(role: str) -> str:
    """查询待审批的请假申请。role 为 manager/hr/admin。"""
    apps = _leave_service.query_pending(role)
    if not apps:
        return "暂无待审批申请"
    lines = []
    for a in apps:
        lines.append(
            f"[{a['id']}] {a['employee_name']}({a['department']}) | {a['leave_type']} | {a['start_date']}~{a['end_date']} | {a['leave_days']}天"
        )
    return "\n".join(lines)


# 工具列表，供 agent 注册
all_tools = [
    submit_leave_application,
    query_my_applications,
    query_pending_approvals,
    approve_leave_application,
]
