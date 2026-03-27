
import time
from collections import defaultdict, deque
from .config import global_config

class ContextManager:
    def __init__(self):
        self.max_len = global_config.max_history
        # 保存群聊近期聊天作为上下文
        self.context = defaultdict(lambda: deque(maxlen=self.max_len))
        # 存储每个群最后主动发言时间
        self.last_active_time = defaultdict(float)
    
    async def add_message(self, group_id: int, user_id: int, text: str, raw_message=None):
        """添加一条用户消息到上下文（只存用户消息，不存机器人回复）"""
        # 可以存储更丰富的信息，如用户ID、时间戳、是否包含图片等
        self.context[group_id].append({
            "role": "user",
            "content": text,
            "user_id": user_id,
            "timestamp": time.time(),
            "raw": raw_message   # 可选，用于后续处理图片等
        })
    
    async def get_history(self, group_id: int, limit: int = 30) -> list[dict]:
        """获取最近 limit 条历史（返回 OpenAI 格式的 messages 列表）"""
        hist = list(self.context[group_id])
        if limit:
            hist = hist[-limit:]
        return [{"role": msg["role"], "content": msg["content"]} for msg in hist]
    
    def can_active_speak(self, group_id: int, now: float, interval: int = 30) -> bool:
        """检查是否可以进行主动发言（距离上次主动发言超过 interval 秒）"""
        return now - self.last_active_time.get(group_id, 0) > interval
    
    def record_active_speak(self, group_id: int, now: float):
        self.last_active_time[group_id] = now

context_manager = ContextManager()