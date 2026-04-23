import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")


class FeishuBot:
    def __init__(self):
        # 初始化飞书应用的 ID 和密钥
        self.app_id = APP_ID
        self.app_secret = APP_SECRET
        # 创建异步 HTTP 客户端
        self.client = httpx.AsyncClient()
        # print(f"App ID: {self.app_id}, App Secret: {self.app_secret}")
        # 缓存飞书接口调用凭证
        self.tenant_access_token = None

    async def get_token(self):
        if self.tenant_access_token:
            return self.tenant_access_token
        # 调用飞书官方接口获取 token
        resp = await self.client.post(
            url="https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": self.app_id, "app_secret": self.app_secret}
        )
        # 解析并保存 token
        if resp.status_code == 200:
            data = resp.json()
            self.tenant_access_token = data.get("tenant_access_token")
            return self.tenant_access_token
        else:
            print(f"获取token失败：{resp.text} | 状态码：{resp.status_code}")
            return None

    async def reply(self, open_id: str, text: str):
        token = await self.get_token()
        if not token:
            print("无法获取token，无法发消息")
            return None

        # 构造飞书消息格式
        body = {
            "receive_id": open_id,  # 消息接收人ID
            "msg_type": "text",  # 消息类型：文本
            "content": json.dumps({"text": text})  # 消息内容
        }

        # 调用飞书消息发送接口
        response = await self.client.post(
            url="https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
            headers={"Authorization": f"Bearer {token}"},
            json=body
        )

        # 返回字典
        return response.json()
