import os

import asyncio

import dotenv
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel

from skill import TaobaoUISkill

# 加载环境变量
dotenv.load_dotenv()

# 配置 LLM
os.environ['OPENAI_API_KEY'] = os.getenv("vectorengine1_API_KEY")
os.environ['OPENAI_BASE_URL'] = os.getenv("vectorengine1_BASE_URL_1")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
                你是一个飞书机器人助手，可以闲聊，也可以执行任务。
                请判断用户意图并从用户输入中提取商品名称:
                - 当有人请求搜索给定价格内的商品时，只返回他所想找的商品名称和价格，不要有其他任何多余的文字。
                - 例如，如果用户说“我想找一件价格小于1000的Tshirt”，你只需要提取出“Tshirt,1000”。
                - 否则，继续正常聊天回答并返回纯文本。
                不要多余内容
                """),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    ("assistant", "{agent_scratchpad}")
])

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)


class EmptySchema(BaseModel):
    pass


taobao_skill = TaobaoUISkill()
tools = [
    StructuredTool(
        name=taobao_skill.name,
        description=taobao_skill.description,
        coroutine=taobao_skill.run,  # 异步函数
        args_schema=EmptySchema
    )
]

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=False,
    handle_parsing_errors=True
)



async def test():
    print("测试：你好")
    res = await agent_executor.ainvoke({"input": "你好"})
    print(res["output"])

    # 用户请求搜索商品
    user_input = "我想找一件价格小于1500的dress"
    print(f"测试：{user_input}")
    # 使用LLM推理商品名称和价格条件
    product_info_response = await agent_executor.ainvoke({"input": user_input})
    print(product_info_response["output"])
    # 假设输出格式为 '价格，商品名称'，我们需要正确分隔它
    product_info = product_info_response["output"].strip()  # '1000，T恤'

    # 分割输出字符串
    try:
        product_name, price_condition = product_info.split(',')  # 用 '，' 分隔
    except ValueError:
        print("输出格式不正确，请检查。")
        return

    if product_name:
        print(f"\n测试：搜索商品 '{product_name}'，价格条件: '{price_condition}'")
        skill_result = await taobao_skill.run(search_term=product_name, filters=int(price_condition))  # 去掉价格条件多余空白
        print(skill_result)
    else:
        print("没有提取到商品名称。")

if __name__ == "__main__":
    asyncio.run(test())
