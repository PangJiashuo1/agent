"""
请假业务服务层
封装所有请假相关的数据库操作
"""

import uuid
from datetime import datetime
from app.common.mysql_client import execute_query, execute_update


class LeaveService:
    """请假申请业务服务"""

    def create_application(
        self,
        employee_id: str,
        employee_name: str,
        employee_role: str,
        department: str,
        leave_type: str,
        leave_days: int,
        start_date: str,
        end_date: str,
        reason: str,
    ) -> dict:
        """
        创建请假申请
        返回 {"success": bool, "message": str, "app_id": str}
        """
        # 参数校验
        if not all([employee_id, employee_name, leave_type, start_date, end_date]):
            return {"success": False, "message": "缺少必填信息，请提供：请假类型、开始日期、结束日期"}

        if leave_days <= 0:
            return {"success": False, "message": "请假天数必须大于0"}

        app_id = f"leave_{uuid.uuid4().hex[:12]}"

        sql = """
            INSERT INTO leave_applications
            (id, employee_id, employee_name, employee_role, department,
             leave_type, leave_days, start_date, end_date, reason, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """
        try:
            execute_update(
                sql,
                (
                    app_id, employee_id, employee_name, employee_role, department,
                    leave_type, leave_days, start_date, end_date, reason,
                ),
            )
            return {
                "success": True,
                "message": f"✅ 请假申请提交成功！\n申请编号：{app_id}\n类型：{leave_type}\n日期：{start_date} ~ {end_date}（{leave_days}天）",
                "app_id": app_id,
            }
        except Exception as e:
            return {"success": False, "message": f"提交失败：{str(e)}"}

    def approve_application(
        self,
        app_id: str,
        approver_role: str,
        decision: str,
        comments: str = "",
    ) -> dict:
        """
        审批请假申请
        - manager 角色更新 manager_approval
        - hr 角色更新 hr_approval
        """
        # 查询申请
        apps = execute_query(
            "SELECT * FROM leave_applications WHERE id = %s", (app_id,)
        )
        if not apps:
            return {"success": False, "message": f"申请 {app_id} 不存在"}

        app = apps[0]
        if app["status"] != "pending":
            return {"success": False, "message": f"申请 {app_id} 已处理（状态：{app['status']}），无法重复审批"}

        if approver_role == "manager":
            execute_update(
                "UPDATE leave_applications SET manager_approval = %s, comments = %s WHERE id = %s",
                (decision, comments, app_id),
            )
        elif approver_role in ("hr", "admin"):
            execute_update(
                "UPDATE leave_applications SET hr_approval = %s, comments = %s WHERE id = %s",
                (decision, comments, app_id),
            )
        else:
            return {"success": False, "message": "您没有审批权限"}

        # 检查是否所有审批都完成
        updated = execute_query(
            "SELECT * FROM leave_applications WHERE id = %s", (app_id,)
        )[0]

        final_status = None
        if updated["manager_approval"] == "approved" and updated["hr_approval"] == "approved":
            final_status = "approved"
        elif "rejected" in (updated["manager_approval"], updated["hr_approval"]):
            final_status = "rejected"

        if final_status:
            execute_update(
                "UPDATE leave_applications SET status = %s WHERE id = %s",
                (final_status, app_id),
            )
            icon = "✅" if final_status == "approved" else "❌"
            return {"success": True, "message": f"{icon} 申请 {app_id} 已{final_status}（审批意见：{comments}）"}

        return {"success": True, "message": f"✅ 您的审批意见已记录，申请 {app_id} 等待其他审批人处理"}

    def query_by_employee(self, employee_id: str) -> list[dict]:
        """查询某员工的所有请假申请"""
        return execute_query(
            "SELECT * FROM leave_applications WHERE employee_id = %s ORDER BY created_at DESC",
            (employee_id,),
        )

    def query_pending(self, role: str) -> list[dict]:
        """查询待审批申请"""
        if role == "manager":
            return execute_query(
                "SELECT * FROM leave_applications WHERE manager_approval = 'pending' AND status = 'pending' ORDER BY created_at ASC"
            )
        elif role in ("hr", "admin"):
            return execute_query(
                "SELECT * FROM leave_applications WHERE hr_approval = 'pending' AND status = 'pending' ORDER BY created_at ASC"
            )
        return []

    def delete_application(self, app_id: str, employee_id: str) -> dict:
        """删除/撤回请假申请（仅限本人且 pending 状态）"""
        apps = execute_query(
            "SELECT * FROM leave_applications WHERE id = %s AND employee_id = %s",
            (app_id, employee_id),
        )
        if not apps:
            return {"success": False, "message": "申请不存在或不属于您"}

        app = apps[0]
        if app["status"] != "pending":
            return {"success": False, "message": f"申请已处理（{app['status']}），无法撤回"}

        execute_update("DELETE FROM leave_applications WHERE id = %s", (app_id,))
        return {"success": True, "message": f"✅ 申请 {app_id} 已撤回"}
