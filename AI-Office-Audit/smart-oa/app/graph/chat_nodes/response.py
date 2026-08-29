"""
响应生成节点
将 task_result 包装为用户友好的最终响应
"""

from app.graph.chat_state import ChatState


def create_response_generator_node(llm):
    """工厂函数：返回响应生成节点"""

    def response_generator(state: ChatState) -> dict:
        task_result = state.get("task_result", "")
        user_message = state.get("user_message", "")
        intent = state.get("intent", "general_chat")
        context = state.get("conversation_context", {})

        # 如果 task_result 已经是完整的自然语言回复，直接使用
        # 否则让 LLM 润色
        if len(task_result) > 20 and intent in (
            "general_chat",
            "get_suggestion",
        ):
            final_response = task_result
        else:
            prompt = f"""你是小滴智能OA的AI助手，请将以下业务结果转化为友好的回复。

用户消息：{user_message}
用户角色：{context.get('user_role', 'employee')}
识别意图：{intent}
业务处理结果：
{task_result}

要求：
1. 语气亲切专业
2. 结果清晰明了
3. 如有申请编号，请展示给用户方便后续查询
4. 不超过300字"""

            response = llm.invoke(prompt)
            final_response = response.content

        return {
            "response": final_response,
            "messages": [
                {"role": "assistant", "content": final_response}
            ],
        }

    return response_generator
