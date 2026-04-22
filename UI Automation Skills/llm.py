import os

import asyncio

import dotenv
from langchain_classic.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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
                - 如果用户想执行关于电商，淘宝，自动化，UI，脚本等任务时 → 返回 JSON: {{"intent": "run_taobao_skill"}}
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

tools = []

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=False,
    handle_parsing_errors=True
)


# 对外接口，供 FastAPI 调用
async def llm_chat_and_intent(user_msg: str):
    try:
        result = await agent_executor.ainvoke({"input": user_msg})
        print(result)
        return result["output"].strip()
    except Exception as e:
        print(f"Error: {str(e)}")
        return "LLM服务暂时不可用"


async def test():
    #测试
    print("你好")
    print(await llm_chat_and_intent("你好"))


if __name__ == "__main__":
    asyncio.run(test())
