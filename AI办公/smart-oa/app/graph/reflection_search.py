"""
反思补搜子图
generate → evaluate → [search → regenerate] → output

当前为骨架实现，后续可接入完整反思补搜工作流
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END


class ReflectionState(TypedDict):
    """反思补搜状态"""
    application_info: dict  # 申请信息
    context: dict  # 上下文
    current_suggestion: str  # 当前建议
    evaluation_score: float  # 评估分数（0-1）
    needs_more_info: bool  # 是否需要补充信息
    search_results: str  # 补充搜索结果
    final_suggestion: str  # 最终建议
    iteration_count: int  # 迭代次数


def _generate_node(state: ReflectionState) -> dict:
    """生成初步建议"""
    # TODO: 接入 LLM 生成初步审批建议
    return {
        "current_suggestion": "（初步建议占位）",
        "iteration_count": 0,
    }


def _evaluate_node(state: ReflectionState) -> dict:
    """自我评估：判断建议是否充分"""
    # TODO: 接入 LLM 评估建议质量
    score = 0.8  # 占位分数
    return {
        "evaluation_score": score,
        "needs_more_info": score < 0.7,
    }


def _search_node(state: ReflectionState) -> dict:
    """补充搜索（RAG / 联网）"""
    # TODO: 接入向量检索或 Tavily 搜索
    return {"search_results": ""}


def _regenerate_node(state: ReflectionState) -> dict:
    """根据补充信息优化建议"""
    # TODO: 接入 LLM 重新生成建议
    return {
        "current_suggestion": "（优化后建议占位）",
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


def _output_node(state: ReflectionState) -> dict:
    """输出最终建议"""
    return {"final_suggestion": state.get("current_suggestion", "")}


def _should_search(state: ReflectionState) -> str:
    """条件路由：是否需要补充搜索"""
    if state.get("needs_more_info", False) and state.get("iteration_count", 0) < 3:
        return "search"
    return "output"


def build_reflection_graph():
    """构建反思补搜子图"""
    builder = StateGraph(ReflectionState)

    builder.set_entry_point("generate")
    builder.add_node("generate", _generate_node)
    builder.add_node("evaluate", _evaluate_node)
    builder.add_node("search", _search_node)
    builder.add_node("regenerate", _regenerate_node)
    builder.add_node("output", _output_node)

    builder.add_edge("generate", "evaluate")
    builder.add_conditional_edges(
        "evaluate",
        _should_search,
        {"search": "search", "output": "output"},
    )
    builder.add_edge("search", "regenerate")
    builder.add_edge("regenerate", "evaluate")
    builder.add_edge("output", END)

    return builder.compile()


def run_reflection_search(application_info: dict, context: dict) -> str:
    """
    运行反思补搜子图，返回最终建议
    供 suggestion 节点调用
    """
    graph = build_reflection_graph()
    result = graph.invoke({
        "application_info": application_info,
        "context": context,
        "current_suggestion": "",
        "evaluation_score": 0.0,
        "needs_more_info": False,
        "search_results": "",
        "final_suggestion": "",
        "iteration_count": 0,
    })
    return result.get("final_suggestion", "暂无建议")
