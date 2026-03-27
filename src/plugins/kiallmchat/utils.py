import nonebot
from nonebot.log import logger
from random import choice
from pathlib import Path
from os import listdir
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from traceback import format_exc
import re


# 消息格式处理函数
def message_format(event) -> str | None:
    text = event.get_plaintext().strip()
    # 如果消息只有 @ 机器人而无文字，也忽略（get_plaintext 已处理）
    if not text:
        return None
    if len(text) > 500:
        text = text[:500] + "…"
    return text


def is_command(message: str) -> bool:
    """判断是否为指令消息（以 / 开头）"""
    return message.startswith('/')

