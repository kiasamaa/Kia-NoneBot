import nonebot

import asyncio

from nonebot.adapters.onebot.v11 import (
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
    PokeNotifyEvent,
    Bot,
)

from openai import AsyncOpenAI



AI_API_KEY = "sk-d95378ea73e6431b97dd55458b376e82"
AI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
AI_MODEL = "qwen3.5-plus"

client = AsyncOpenAI(
    api_key= AI_API_KEY,
    base_url= AI_BASE_URL,
)


class Model:
    def __init__(
        self,
        bot,
        event,
    ):
        self.bot = bot
        self.event = event

    async def sender(self) -> str:

        raw_msg = self.event.get_plaintext().strip()

        # 3. 可选：记录用户会话历史（此处简化，每次只发当前消息）
        messages = [
            {"role": "system", "content": "你是一个可爱的群聊助手，请用轻松友好的语气回答。"},
            {"role": "user", "content": raw_msg}
        ]

        # 4. 调用大模型 API
        try:
            # 设置超时，避免长时间阻塞
            resp = await asyncio.wait_for(
                client.chat.completions.create(
                    model=AI_MODEL,
                    messages=messages,
                    stream=False
                ),
                timeout=30  # 30秒超时
            )
            if content := resp.choices[0].message.content:
                reply = content.strip()
            else:
                reply = "没有返回值哦，哪里出错了？"
        except asyncio.TimeoutError:
            reply = "抱歉，思考超时了，请稍后再试。"
        except Exception as e:
            # 打印错误日志，方便调试
            print(f"AI 调用失败：{e}")
            reply = "啊哦，暂时无法回复，请稍后再试。"
        
        return reply