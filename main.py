from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig
import requests
import json
@register(
    "astrbot_plugin_cs_skins",
    "wsryhc", 
    "cs饰品查询",
    "0.0.1"
    )
class MyPlugin(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context)
        global ApiToken
        ApiToken = config.get("apitoken","")
        logger.info(f"Api-Token: {ApiToken}")
    default_api = "https://api.csqaq.com/api/v1"
    # 注册指令的装饰器。指令名为 查询饰品。
    @filter.command("饰品模糊查询")
    async def find_id(self, event: AstrMessageEvent):
        """这是一个 饰品模糊查询 指令"""
        user_name = event.get_sender_name()
        message_str = event.message_str[6:] # 用户发的纯文本消息字符串
        logger.info(message_str)
        url = "https://api.csqaq.com/api/v1/search/suggest?text="+message_str
        payload={}
        headers = {
            'ApiToken': ApiToken
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        obj = json.loads(response.text)
        data_map = {item['id']: item['value'] for item in obj['data']}
        logger.info(data_map)
        result_str = "\n".join(f"{key}: {value}" for key, value in data_map.items())
        if not result_str:
            yield event.plain_result(f"未找到与 '{message_str}' 相关的饰品")
        else:
            yield event.plain_result(result_str) # 发送一条纯文本消息