"""
对话状态定义
定义 LangGraph 工作流中传递的 ChatState 结构
"""

from typing import TypedDict, List, Annotated
from langgraph.graph import add_messages


class ChatState(TypedDict):
    """
    对话主图状态
    - messages: 对话消息历史，由 add_messages 自动追加（不会覆盖）
    - 其余字段按需由各节点读写
    """

    messages: Annotated[List[dict], add_messages]  # 对话消息历史（自动追加）
    user_message: str  # 用户当前消息
    intent: str  # 识别的意图
    extracted_info: dict  # 提取的关键信息（请假日期、类型等）
    current_task: str  # 当前任务类型
    task_result: str  # 任务执行结果
    response: str  # AI 最终响应
    conversation_context: dict  # 对话上下文（user_id / role / department）
    needs_search: bool  # 是否需要联网搜索
    search_results: str  # 搜索结果
    iteration_count: int  # 循环迭代次数（防止无限循环）
