from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_message
from nonebot.log import logger
from nonebot.rule import to_me
from .config import Config



from nonebot.adapters.onebot.v11 import (
    GROUP,
    Message,
    MessageEvent,
    MessageSegment,
    GroupMessageEvent,
    PokeNotifyEvent,
    Bot,
)

from .utils import message_format
from .llm import Model

__plugin_meta__ = PluginMetadata(
    name="kiallmchat",
    description="专用于群聊场景的AI插件，快来打造最谐星的bot群友吧。",
    usage="application",
    config=Config,
)

config = get_plugin_config(Config)

# 接受所有消息，用于保存一定量的历史记录
message_matcher = on_message(permission=GROUP, priority=1, block=False)

@message_matcher.handle()
async def context_log(bot: Bot, event: MessageEvent):
    # if event.message.extract_plain_text().strip():  # 有文字才记录

    if message_dict := await message_format(bot, event):
            # sender_name = event.sender.card or event.sender.nickname
            # llm.context_dict[event.group_id].append(
            #     f"{sender_name}:{''.join(message_dict['text'])}"
            # )
        logger.info("收到message")

        
        # 概率主动发
        # if random.randint(1, 100) == 1:
        #     llm = llm.MoeLlm(
        # bot, event, message_dict,is_objective=True, temperament='默认')
        #     reply = await llm.handle_llm()


# 接受at机器人的所有消息，优先级999，需在所有其他插件响应之后响应
tome_message_matcher = on_message(rule=to_me(), permission=GROUP, priority=999, block=True)


@tome_message_matcher.handle()
async def handle_llmchat(bot: Bot, event: MessageEvent):

    # 空消息不处理
    raw_msg = event.get_plaintext().strip()
    if not raw_msg:
        return  

    model = Model(bot, event)

    reply = await model.sender()

    # 5. 发送回复
    # 可选：在回复中@发送者（让群友知道回复谁）
    await bot.send(
        event,
        Message([
            MessageSegment.at(event.user_id),
            MessageSegment.text(f"\n{reply}")
        ])
    )