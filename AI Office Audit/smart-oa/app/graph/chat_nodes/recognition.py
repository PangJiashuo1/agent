"""
意图识别节点
负责解析用户自然语言，输出意图 + 提取的信息 + 是否需要联网搜索
"""

import re
import json
from datetime import datetime
from app.graph.chat_state import ChatState


def create_intent_recognition_node(llm):
    """工厂函数：返回绑定了指定 LLM 的意图识别节点"""

    def intent_recognition(state: ChatState) -> dict:
        user_message = state.get("user_message", "")
        messages = state.get("messages", [])
        context = state.get("conversation_context", {})

        # 构建历史摘要（最近 3 条）
        history_lines = []
        for msg in messages[-6:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")[:100]
            history_lines.append(f"{role}: {content}")
        history_text = "\n".join(history_lines) if history_lines else "无历史"

        prompt = f"""你是一个OA系统智能助手，请识别用户的意图。

当前日期：{datetime.now().strftime('%Y-%m-%d %A')}

当前用户信息：
- 角色：{context.get('user_role', 'employee')}
- 部门：{context.get('user_department', '未知')}

最近对话历史：
{history_text}

用户当前消息：{user_message}

意图选项（只能选一个）：
- submit_leave: 提交请假申请（用户表达了请假意愿）
- delete_application: 删除/撤回请假申请
- approve: 审批操作（主管审批请假）
- query_status: 查询自己的申请状态
- query_pending: 查询待审批事项（主管查看待办）
- get_suggestion: 获取审批建议
- general_chat: 日常对话、闲聊、问候、其他

请提取关键信息（如有）：
- leave_type: 请假类型（年假/病假/事假/婚假/产假/丧假）
- leave_days: 请假天数
- start_date: 开始日期（转为 YYYY-MM-DD 格式，根据当前日期计算"下周一""后天"等相对日期）
- end_date: 结束日期
- reason: 请假原因
- app_id: 申请编号（审批/查询时可能提及）

严格以JSON格式返回，不要输出其他内容：
{{"intent": "...", "extracted_info": {{...}}, "needs_search": false}}"""

        response = llm.invoke(prompt)
        raw = response.content

        # 尝试提取 JSON 块
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            return {
                "intent": "general_chat",
                "extracted_info": {},
                "needs_search": False,
            }

        try:
            result = json.loads(json_match.group())
        except json.JSONDecodeError:
            return {
                "intent": "general_chat",
                "extracted_info": {},
                "needs_search": False,
            }

        return {
            "intent": result.get("intent", "general_chat"),
            "extracted_info": result.get("extracted_info", {}),
            "needs_search": result.get("needs_search", False),
        }

    return intent_recognition
