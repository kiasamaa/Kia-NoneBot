from pydantic import BaseModel, Field
from nonebot import get_driver
import nonebot_plugin_localstore as store
from pathlib import Path
import json
  

# ===============
DEBUG = True
# ===============

class BaseConfig(BaseModel):
    """可修改的插件配置（存储在 JSON 中）"""
    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-3.5-turbo"
    max_history: int = 30
    active_prob: float = 0.03
    active_keywords: list[str] = ["机器人", "小助手", "帮帮我"]
    active_interval: int = 600
    emotions_dir:str = ""

#读取本地配置
config_path: Path = store.get_plugin_config_dir()

# 默认使用.env配置
driver = get_driver()
plugin_config = driver.config


# 动态配置（可运行时修改，保存在本地 JSON 文件）
class ConfigManager:
    def __init__(self):
        self.config_path = Path(config_path / "config.json")
        self._config = self.load()
        self._nickname = list(plugin_config.nickname)[0]
        self._superusers = plugin_config.superusers

    def load(self) -> BaseConfig:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                if DEBUG:
                    print(f"加载配置: {config}")

                return BaseConfig.model_validate(config)
              
            
        except FileNotFoundError:
            return self.config_init() #初次启动时，在对应目录生成配置文件
    
                    
    
    def config_init(self) -> BaseConfig:
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            config = BaseConfig()
            json.dump(config.model_dump(), f, indent=4, ensure_ascii=False)
        return config
    
    # 全局配置访问（只读，因为一般不运行时修改）

    @property
    def config(self):
        return self._config
    
    @property
    def nickname(self) -> str:
        """机器人的昵称（取第一个）"""
        return self._nickname if self._nickname else ""

    @property
    def superusers(self) -> set[str]:
        """超级用户列表"""
        return self._superusers

config_manager = ConfigManager()