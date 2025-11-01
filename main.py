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
    # 注册指令的装饰器。指令名为 查询饰品。
    @filter.command("饰品模糊查询")
    async def find_id(self, event: AstrMessageEvent):
        """这是一个 饰品模糊查询 指令"""
        message_str = event.message_str[7:] # 用户发的纯文本消息字符串
        # 构造请求
        url = "https://api.csqaq.com/api/v1/search/suggest?text="+message_str   
        payload={}
        headers = {
            'ApiToken': ApiToken 
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        # 解析响应
        obj = json.loads(response.text)
        data_map = {item['id']: item['value'] for item in obj['data']}
        # 构造结果字符串
        result_str = "\n".join(f"{key}: {value}" for key, value in data_map.items())
        if not result_str:
            yield event.plain_result(f"未找到与 '{message_str}' 相关的饰品")
        else:
            yield event.plain_result(result_str) # 发送结果给用户
    @filter.command("饰品精确查询")
    async def find_proid(self, event: AstrMessageEvent):
        """这是一个 饰品精确查询 指令"""
        message_str = event.message_str[7:] # 用户发的纯文本消息字符串
        # 构造请求
        url = "https://api.csqaq.com/api/v1/info/get_good_id"

        payload = json.dumps({
        "page_index": 1,
        "page_size": 20,
        "search": message_str
        })
        headers = {
        'ApiToken': ApiToken,
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(response.text)
        # 解析响应
        obj = json.loads(response.text)
        data_map = {item['id']: item['name'] for item in obj['data']['data'].values()}
        logger.info(data_map)
        # # 构造结果字符串
        result_str = "\n".join(f"{key}: {value}" for key, value in data_map.items())
        if not result_str:
            yield event.plain_result(f"未找到与 '{message_str}' 相关的饰品")
        else:
            yield event.plain_result(result_str) # 发送结果给用户
    @filter.command("饰品价格查询")
    async def find_price(self, event: AstrMessageEvent):
        """这是一个 饰品价格查询 指令"""
        message_str = event.message_str[7:] # 用户发的纯文本消息字符串
        # 判断 message_str 是否为纯数字字符串
        if not message_str.isdigit():
            # 如果不是纯数字，则返回提示并结束处理
            yield event.plain_result(f"请提供纯数字的饰品ID，当前输入: '{message_str}'")
            return
        # 构造请求
        url = "https://api.csqaq.com/api/v1/info/good?id=" + message_str
        payload={}
        headers = {
            'ApiToken': ApiToken
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        logger.info(response.text)
        # 解析响应
        obj = json.loads(response.text)
        data_map = obj['data']
        if not data_map:
            yield event.plain_result(f"未找到ID为 '{message_str}' 的饰品")
            return
        #构造结果字符串
        result_str = f"饰品ID:{data_map['goods_info']['id']}\n\
{data_map['goods_info']['name']}\n\
存世量:{data_map['goods_info']['statistic']} 品质:{data_map['goods_info']['rarity_localized_name']}\n\
steam\n\
成交量:{data_map['goods_info']['turnover_number']}均价${data_map['goods_info']['turnover_avg_price']}\n\
挂刀比例:{data_map['goods_info']['steam_buff_sell_conversion']}\n\
buff\n\
在售价:{data_map['goods_info']['buff_sell_price']}元 数量{data_map['goods_info']['buff_sell_num']}\n\
求购价: {data_map['goods_info']['buff_buy_price']}元 数量{data_map['goods_info']['buff_buy_num']}\n\
yyyp\n\
在售价:{data_map['goods_info']['yyyp_sell_price']}元 数量{data_map['goods_info']['yyyp_sell_num']}\n\
求购价: {data_map['goods_info']['yyyp_buy_price']}元 数量{data_map['goods_info']['yyyp_buy_num']}\n\
短租：{data_map['goods_info']['yyyp_lease_price']}元 长租{data_map['goods_info']['yyyp_long_lease_price']}元\n\
涨跌幅\n\
7天{data_map['goods_info']['sell_price_rate_7']}% 30天{data_map['goods_info']['sell_price_rate_30']}%\n\
180天{data_map['goods_info']['sell_price_rate_180']}% 365天{data_map['goods_info']['sell_price_rate_365']}%\n\
所属武器箱/收藏品\n\
武器箱id:{data_map['container'][0]['id']}\n\
{data_map['container'][0]['name']}\n\
价格:{data_map['container'][0]['price'] if data_map['container'][0]['price'] is not None else '不可购买'}"    
        yield event.plain_result(result_str) # 发送结果给用户
    #1.挂刀/反向挂刀 2.最低价 3.最高价 4.成交量
    @filter.command("挂刀查询")
    async def find_hangdao(self, event: AstrMessageEvent):
        """这是一个 挂刀查询 指令"""
        args = event.message_str.replace("挂刀查询", "").split()
        if len(args)<4:
            yield event.plain_result("参数不足，请依次提供四个参数，用空格分隔：\n1.挂刀/反向挂刀(0/1)\n2.最低价(不指定填0)\n3.最高价(不指定填0)\n4.最低成交量(不指定填0)")
            return
        option :int= int(args[-4]) if args[-4].isdigit() else -1
        price_min :int= int(args[-3]) if args[-3].isdigit() else -1
        price_max :int= int(args[-2]) if args[-2].isdigit() else -1
        turnover :int= int(args[-1]) if args[-1].isdigit() else -1
        # 构造请求
        url = "https://api.csqaq.com/api/v1/info/exchange_detail"
        payload = json.dumps({
            "page_index": 1,
            "res": option,
            "platforms": "BUFF-YYYP",
            "sort_by": 1,
            "min_price": price_min,
            "max_price": price_max,
            "turnover": turnover if turnover>0 else 10
        })
        headers = {
            'ApiToken': ApiToken,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        # 解析响应
        obj = json.loads(response.text)
        data_map = obj['data']
        if not data_map:
            yield event.plain_result("未找到符合条件的饰品")
            return
        result_str = ""
        for i in range(min(10, len(data_map))):  # 从0到9
            result_str += f"饰品ID:{data_map[i]['id']}\n\
{data_map[i]['name']}\n\
steam\n\
求购价:{data_map[i]['steam_buy_price']}\n\
今日成交量:{data_map[i]['turnover_number']}\n\
到手余额:{data_map[i]['steam_buy_price'] * 0.87}\n\
buff\n\
在售价:{data_map[i]['buff_sell_price']}元 数量{data_map[i]['buff_sell_num']}\n\
求购价: {data_map[i]['buff_buy_price']}元 数量{data_map[i]['buff_buy_num']}\n\
挂刀比例:\n\
在售:{round(data_map[i]['buff_sell_price'] / data_map[i]['steam_buy_price'], 3)}\n\
求购:{round(data_map[i]['buff_buy_price'] / data_map[i]['steam_buy_price'], 3)}\n\
yyyp\n\
在售价:{data_map[i]['yyyp_sell_price']}元 数量{data_map[i]['yyyp_sell_num']}\n\
求购价: {data_map[i]['yyyp_buy_price']}元 数量{data_map[i]['yyyp_buy_num']}\n\
挂刀比例:\n\
在售:{round(data_map[i]['yyyp_sell_price'] / data_map[i]['steam_buy_price'], 3)}\n\
求购:{round(data_map[i]['yyyp_buy_price'] / data_map[i]['steam_buy_price'], 3)}\n"

        # 输出结果
        yield event.plain_result(result_str)   
    @filter.command("指数查询")
    async def find_zhishu(self, event: AstrMessageEvent):
        url = "https://api.csqaq.com/api/v1/current_data?type=init"
        payload={}
        headers = {
        'ApiToken': ApiToken
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        obj = json.loads(response.text)
        data_map = obj['data']['sub_index_data']
        if not data_map:
            yield event.plain_result("当前指数数据不可用")
            return
        result_str = ""
        for i in range(min(11, len(data_map))):  # 取前11个项，确保不会越界
            name = data_map[i]["name"]
            market_index = data_map[i]["market_index"]
            chg_rate = data_map[i]["chg_rate"]
            
            # 格式化变动率，正数前加加号
            chg_rate_str = f"+{chg_rate}" if chg_rate > 0 else f"{chg_rate}"
            
            # 拼接字符串
            result_str += f"{name}\n当前指数:{market_index}\n今日变动率:{chg_rate_str}\n"
        result_str = "更新时间:\n"+data_map[0]['updated_at'] + "\n" + result_str
        result_str += f"市场情绪:{obj['data']['greedy'][-1][-1]}\n"
        result_str += f"当前在线人数:{obj['data']['online_number']['current_number']}\n本周人数涨幅:{obj['data']['online_number']['rate_week']}%"
        yield event.plain_result(result_str)