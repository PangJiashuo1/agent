"""
联网搜索节点
当前为占位实现，后续接入 Tavily 时替换内部逻辑即可
"""

from app.graph.chat_state import ChatState


def create_search_node(tavily_api_key: str = None):
    """工厂函数：返回搜索节点"""

    def search(state: ChatState) -> dict:
        needs_search = state.get("needs_search", False)

        if not needs_search or not tavily_api_key:
            return {"search_results": ""}

        # TODO: 接入 Tavily 搜索
        # from tavily import TavilyClient
        # client = TavilyClient(api_key=tavily_api_key)
        # results = client.search(state["user_message"])
        # return {"search_results": str(results)}

        return {"search_results": ""}

    return search
