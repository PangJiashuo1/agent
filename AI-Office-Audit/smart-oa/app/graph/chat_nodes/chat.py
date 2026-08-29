"""
日常对话节点
处理问候、闲聊等非业务意图
"""

from app.graph.chat_state import ChatState


def create_general_chat_node(llm):
    """工厂函数：返回日常对话节点"""

    def general_chat(state: ChatState) -> dict:
        user_message = state.get("user_message", "")
        context = state.get("conversation_context", {})
        search_results = state.get("search_results", "")

        system_prompt = (
            f"你是「小滴智能OA」的AI助手，服务于{context.get('user_department', '')}的"
            f"{context.get('user_name', '用户')}（角色：{context.get('user_role', 'employee')}）。\n"
            "你的职责：\n"
            "- 用自然语言帮助用户完成请假申请、审批、查询等OA操作\n"
            "- 回答工作相关问题\n"
            "- 语气亲切专业，简洁明了\n"
        )

        if search_results:
            system_prompt += f"\n联网搜索结果供参考：\n{search_results}\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        response = llm.invoke(messages)
        return {"task_result": response.content}

    return general_chat
