import nonebot
from collections import defaultdict, deque
from nonebot import get_driver
import asyncio
import time
import random

from nonebot.adapters.onebot.v11 import (
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
    PokeNotifyEvent,
    Bot,
)

from nonebot.log import logger
from openai import AsyncOpenAI
from .config import global_config
from .context import context_manager


class AIClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key= global_config.ai_api_key,
            base_url= global_config.ai_base_url,
        )
        self.model = global_config.ai_model
        
    async def chat(self, user_input: str, history: list[dict], raw_message=None) -> str:
        """
        user_input: 当前用户输入的文本
        history: 历史消息列表 [{"role": "user", "content": "..."}, ...]
        raw_message: 原始消息段（用于提取图片等）
        """
        # 如果有图片且模型支持多模态，可以调用专门的函数
        # 这里简单处理：将图片描述拼接到 user_input
        if raw_message and self._has_image(raw_message):
            # 假设有一个函数 image_to_description 调用多模态模型或 OCR
            img_desc = await self.image_to_description(raw_message)
            user_input = f"{user_input}\n[图片描述: {img_desc}]"
        

        messages = [
            {"role": "system", "content": "你是一个可爱的群聊助手，请用轻松友好的语气回答。"},
            *history[-global_config.max_history:],   # 根据配置数量显示最近历史信息
            {"role": "user", "content": user_input},
        ]
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=1.0,
                max_tokens=1000,
            )
            content = resp.choices[0].message.content
            return content.strip() if content else "抱歉，我没有理解你的意思。"
        except Exception as e:
            logger.info(f"API 调用失败: {e}")
            return "error"


    async def try_active_speak(self, bot: Bot, event: GroupMessageEvent, user_text: str):
        """判断是否主动发言，若是则生成并发送"""
        group_id = event.group_id
        if not context_manager.can_active_speak(group_id):
            return
        
        # 概率触发或关键词触发
        should_act = (random.random() < global_config.active_prob) or \
                    any(keyword in user_text for keyword in global_config.active_keywords)
        
        if not should_act:
            return
        
        # 获取最近历史（用于生成自然的主动发言）
        history = await context_manager.get_history(group_id)

        # 调用 AI 生成主动发言（使用单独的prompt）
        active_reply = await self.chat(user_text, history)

        if active_reply:
            context_manager.record_active_speak(group_id)
            await bot.send_group_msg(group_id=group_id, message=active_reply)


    def _has_image(self, message):
        # 检查消息中是否包含图片段
        for seg in message:
            if seg.type == "image":
                return True
        return False
    
    async def image_to_description(self, message):
        # TODO: 调用多模态模型（如 GPT-4V）或 OCR 获取图片描述
        # 返回文本描述
        return "这是一张图片"

ai_client = AIClient()