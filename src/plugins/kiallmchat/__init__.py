from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_message, on_notice
from nonebot.log import logger
from nonebot.rule import to_me
from .config import BaseConfig



from nonebot.adapters.onebot.v11 import (
    GROUP,
    Message,
    MessageEvent,
    MessageSegment,
    GroupMessageEvent,
    PokeNotifyEvent,
    NoticeEvent,
    Bot,
)

from .utils import message_format, is_command
from .models import ai_client
from .context import context_manager

__plugin_meta__ = PluginMetadata(
    name="kiallmchat",
    description="专用于群聊场景的AI插件，快来打造最谐星的bot群友吧。",
    usage="application",
    config=BaseConfig,
)

config = get_plugin_config(BaseConfig)

# 接受所有消息，不阻塞，仅用于保存一定量的历史记录
message_matcher = on_message(permission=GROUP, priority=1, block=False)

@message_matcher.handle()
async def context_record(bot: Bot, event: GroupMessageEvent):

    user_text = message_format(event)

    if user_text is None:
        return

    # 保存到上下文（包括图片等多媒体信息的简要描述）
    await context_manager.add_message(event.group_id, event.user_id, user_text, event.get_message())

    # 尝试主动发言
    await ai_client.try_active_speak(bot, event, user_text)



# 接受at机器人的所有消息，优先级999，需在所有其他插件响应之后响应
ai_matcher = on_message(rule=to_me(), permission=GROUP, priority=999, block=True)

@ai_matcher.handle()
async def handle_ai_reply(bot: Bot, event: GroupMessageEvent):

    user_text = message_format(event)
    # 忽略空信息和指令信息
    if not user_text or is_command(user_text):
        return

    # 获取上下文历史
    history = await context_manager.get_history(event.group_id, limit=10)
    # 调用AI生成回复
    reply = await ai_client.chat(user_text, history, event.get_message())
    await bot.send(
        event,
        reply,
        at_sender=True,
        reply_message=True
        )


# 处理戳一戳
poke_matcher = on_notice(rule=to_me(), priority=11, block=False)

@poke_matcher.handle()
async def handle_poke(bot: Bot, event: PokeNotifyEvent):
    await bot.call_api("send_poke", user_id=event.user_id, group_id=event.group_id)
