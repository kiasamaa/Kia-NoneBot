from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_message
from nonebot.rule import to_me

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="ping-test",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


message_machter = on_message(rule=to_me(), priority=999, block=True)

@message_machter.handle()
async def handle_message():
        await message_machter.finish("窝嫩叠")