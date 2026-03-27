import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

import asyncio


nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)


nonebot.load_from_toml("pyproject.toml")

# 加载插件
nonebot.load_builtin_plugins("echo")  # 内置插件
# nonebot.load_plugins("src/plugins")  # 本地插件

if __name__ == "__main__":
    nonebot.run()