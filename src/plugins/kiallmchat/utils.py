import nonebot
from nonebot.log import logger
from random import choice
from pathlib import Path
from os import listdir
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from traceback import format_exc
import re

# bot的nickname
Bot_NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]  

# 消息格式处理函数

async def message_format(bot, event) -> dict:
    
    # logger.info(event)

    if reply := event.reply:
        logger.info(reply)
    

    if message := event.get_message():
        logger.info(message)


    return event.get_message()