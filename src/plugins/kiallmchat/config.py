from pydantic import BaseModel, BaseSettings, Field
from nonebot import get_driver
import nonebot_plugin_localstore as store
from pathlib import Path
import json
  

class BaseConfig(BaseModel):
    #同时设置默认值
    ai_api_key: str = Field(..., alias="AI_API_KEY")
    ai_base_url: str = Field("https://api.openai.com/v1", alias="AI_BASE_URL")
    ai_model: str = Field("gpt-3.5-turbo", alias="AI_MODEL")
    max_history: int = Field(30, alias="MAX_HISTORY")
    active_prob: float = Field(0.03, alias="ACTIVE_PROB")
    active_keywords: list[str] = Field(["机器人", "小助手", "帮帮我"], alias="ACTIVE_KEYWORDS")
    active_interval: int = Field(600, alias="ACTIVE_INTERVAL")
    nickname: str = list(Field(["bot"], alias="NICKNAME"))[0]
    emotions_dir:str = Field("", alias="EMOTIONS_DIR")

#读取本地配置
config_path: Path = store.get_plugin_config_dir()

# 默认使用.env配置
driver = get_driver()
plugin_config = driver.config
env_config = BaseConfig(**plugin_config.model_dump())   # '**'是函数字典参数收集符号


# 动态配置（可运行时修改，保存在本地 JSON 文件）
class Config:
    def __init__(self):
        self.config_path = Path(config_path / "config.json")
        self.config = self.load()
    
    def load(self) -> BaseConfig:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return env_config.model_validate_json(json.load(f))
            except FileNotFoundError:
                return self.config_init() #初次启动时，在对应目录生成配置文件
        else:
            return env_config
                    
    
    def config_init(self) -> BaseConfig:
        import json
        with open(self.config_path, "w") as f:
            json.dump(plugin_config.model_dump, f, indent=4, ensure_ascii=False)
        return env_config.model_validate(plugin_config)
    
    @property
    def get_config(self):
        return self.config

global_config = Config().config