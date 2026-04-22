from fastapi import FastAPI, Request
import json
from bot import FeishuBot
from skill import TaobaoUISkill
from llm import llm_chat_and_intent

###运行前请打开ngork通道：ngrok http 8000

app = FastAPI()
processed_msg_ids = set()


@app.post("/feishu/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("收到飞书消息", data)

    # 飞书 URL 验证
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}

    event = data.get("event", {})
    message = event.get("message", {})
    msg_id = message.get("message_id")  # 拿消息ID

    # 消息去重
    if not msg_id or msg_id in processed_msg_ids:
        return {"code": 0}
    processed_msg_ids.add(msg_id)  # 标记已处理的消息

    # 解析消息
    msg_type = event.get("message", {}).get("message_type")
    content = event.get("message", {}).get("content", "")
    open_id = event.get("sender", {}).get("sender_id", {}).get("open_id")

    if not content or not open_id or msg_type != "text":
        return {"code": 0}

    try:
        user_text = json.loads(content).get("text", "")
    except:
        user_text = content.strip()

    bot = FeishuBot()

    # LLM 理解意图
    llm_result = await llm_chat_and_intent(user_text)

    # 判断是否要执行 Skill
    if "run_taobao_skill" in llm_result:
        await bot.reply(open_id, "LLM已识别意图：执行淘宝UI自动化\n开始执行中...")

        # agent 调用skill
        skill = TaobaoUISkill()
        res = await skill.run()

        # 构造结果
        steps = "\n".join(res["steps"])
        final_msg = f""" 
        执行完成
        结果：{res['message']}

        执行步骤：
                    {steps}"""
        await bot.reply(open_id, final_msg)
    else:
        # 普通聊天回复
        await bot.reply(open_id, llm_result)

    return {"code": 0}


# ==========================
# 启动
# ==========================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
