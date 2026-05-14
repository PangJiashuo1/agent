from fastapi import FastAPI, Request
import json
from bot import FeishuBot
from skill import TaobaoUISkill
from llm import agent_executor

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


    # 返回llm回答
    product_info_response = await agent_executor.ainvoke({
        "input": user_text
    })
    print(product_info_response["output"])

    # 假设输出格式为 '价格，商品名称'
    product_info = product_info_response["output"].strip()
    # 分割输出字符串
    try:
        product_name, price_condition = product_info.split(',')
    except ValueError:
        print("输出格式不正确，请检查。")
        return {"code": 0}  # 返回错误状态

    if product_name:
        print(f"\n测试：搜索商品 '{product_name}'，价格条件: '{price_condition}'")
        skill_result = await TaobaoUISkill().run(search_term=product_name, filters=int(price_condition))  # 将商品名称和价格条件传入技能
        reply = skill_result["message"]  # 从技能结果中构建回复
    else:
        print("没有提取到商品名称。")
        reply = "未能提取商品名称，请重新输入。"

    await bot.reply(open_id, reply)
    return {"code": 0}


# 启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
