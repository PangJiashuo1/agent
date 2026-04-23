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
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['OPENAI_BASE_URL'] = os.getenv("OPENAI_BASE_URL")
# LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
                你是一个飞书机器人助手，可以闲聊，也可以执行淘宝UI自动化任务。
                请判断用户意图：
                - 如果用户想执行关于电商，淘宝，自动化，UI，脚本等任务时调用工具
                - 其他情况正常聊天回答，返回纯文本
                不要多余内容。
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
        coroutine=taobao_skill.run, # 异步函数
        args_schema = EmptySchema
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

    print("\n测试：帮我执行淘宝自动化")
    res = await agent_executor.ainvoke({"input": "帮我执行淘宝自动化"})
    print(res["output"])


if __name__ == "__main__":
    asyncio.run(test())
