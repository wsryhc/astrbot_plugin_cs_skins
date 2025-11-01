from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig
import httpx
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
        # 存储为实例属性，避免使用全局变量
        self.api_token = config.get("apitoken", "")
    # 注册指令的装饰器。指令名为 查询饰品。
    @filter.command("饰品模糊查询")
    async def find_id(self, event: AstrMessageEvent):
        """这是一个 饰品模糊查询 指令"""
        # 获取命令后的纯文本参数，优先使用 get_plain_text（如果事件对象提供），否则回退到 message_str
        if hasattr(event, 'get_plain_text'):
            message_str = event.get_plain_text().replace("饰品模糊查询", "", 1).strip()
        else:
            message_str = event.message_str.replace("饰品模糊查询", "", 1).strip()
        # 构造请求
        url = "https://api.csqaq.com/api/v1/search/suggest?text="+message_str   
        headers = {
            'ApiToken': self.api_token
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                # 解析响应
                obj = response.json()
        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {e}")
            yield event.plain_result("查询失败，请稍后再试。")
            return
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 状态错误: {e}")
            yield event.plain_result("查询失败，远端服务返回异常状态。")
            return
        except json.JSONDecodeError:
            logger.error("JSON 解析失败")
            yield event.plain_result("API响应格式错误，请联系管理员。")
            return
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
        # 获取命令后的纯文本参数，优先使用 get_plain_text（如果事件对象提供），否则回退到 message_str
        if hasattr(event, 'get_plain_text'):
            message_str = event.get_plain_text().replace("饰品精确查询", "", 1).strip()
        else:
            message_str = event.message_str.replace("饰品精确查询", "", 1).strip()
        # 构造请求
        url = "https://api.csqaq.com/api/v1/info/get_good_id"

        payload_obj = {
            "page_index": 1,
            "page_size": 20,
            "search": message_str
        }
        headers = {
            'ApiToken': self.api_token,
            'Content-Type': 'application/json'
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload_obj, timeout=10.0)
                response.raise_for_status()
                logger.info(response.text)
                # 解析响应
                obj = response.json()
        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {e}")
            yield event.plain_result("查询失败，请稍后再试。")
            return
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 状态错误: {e}")
            yield event.plain_result("查询失败，远端服务返回异常状态。")
            return
        except json.JSONDecodeError:
            logger.error("JSON 解析失败")
            yield event.plain_result("API响应格式错误，请联系管理员。")
            return
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
        # 获取命令后的纯文本参数，优先使用 get_plain_text（如果事件对象提供），否则回退到 message_str
        if hasattr(event, 'get_plain_text'):
            message_str = event.get_plain_text().replace("饰品价格查询", "", 1).strip()
        else:
            message_str = event.message_str.replace("饰品价格查询", "", 1).strip()
        # 判断 message_str 是否为纯数字字符串
        if not message_str.isdigit():
            # 如果不是纯数字，则返回提示并结束处理
            yield event.plain_result(f"请提供纯数字的饰品ID，当前输入: '{message_str}'")
            return
        # 构造请求
        url = "https://api.csqaq.com/api/v1/info/good?id=" + message_str
        headers = {
            'ApiToken': self.api_token
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                logger.info(response.text)
                # 解析响应
                obj = response.json()
        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {e}")
            yield event.plain_result("查询失败，请稍后再试。")
            return
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 状态错误: {e}")
            yield event.plain_result("查询失败，远端服务返回异常状态。")
            return
        except json.JSONDecodeError:
            logger.error("JSON 解析失败")
            yield event.plain_result("API响应格式错误，请联系管理员。")
            return
        data_map = obj.get('data')
        if not data_map:
            yield event.plain_result(f"未找到ID为 '{message_str}' 的饰品")
            return

        # 保险取值，避免 KeyError/IndexError
        goods = data_map.get('goods_info', {}) if isinstance(data_map, dict) else {}
        gid = goods.get('id', 'N/A')
        gname = goods.get('name', '')
        statistic = goods.get('statistic', 'N/A')
        rarity = goods.get('rarity_localized_name', 'N/A')
        turnover_number = goods.get('turnover_number', 'N/A')
        turnover_avg = goods.get('turnover_avg_price', 'N/A')
        steam_buff_conv = goods.get('steam_buff_sell_conversion', 'N/A')
        buff_sell_price = goods.get('buff_sell_price', 'N/A')
        buff_sell_num = goods.get('buff_sell_num', 'N/A')
        buff_buy_price = goods.get('buff_buy_price', 'N/A')
        buff_buy_num = goods.get('buff_buy_num', 'N/A')
        yyyp_sell_price = goods.get('yyyp_sell_price', 'N/A')
        yyyp_sell_num = goods.get('yyyp_sell_num', 'N/A')
        yyyp_buy_price = goods.get('yyyp_buy_price', 'N/A')
        yyyp_buy_num = goods.get('yyyp_buy_num', 'N/A')
        yyyp_lease_price = goods.get('yyyp_lease_price', 'N/A')
        yyyp_long_lease_price = goods.get('yyyp_long_lease_price', 'N/A')
        sell_rate_7 = goods.get('sell_price_rate_7', 'N/A')
        sell_rate_30 = goods.get('sell_price_rate_30', 'N/A')
        sell_rate_180 = goods.get('sell_price_rate_180', 'N/A')
        sell_rate_365 = goods.get('sell_price_rate_365', 'N/A')

        # 处理 container 列表可能为空的情况
        container_info = "无"
        containers = data_map.get('container') if isinstance(data_map, dict) else None
        if containers and isinstance(containers, list) and len(containers) > 0:
            c = containers[0]
            c_price = c.get('price') if isinstance(c, dict) else None
            c_price_str = c_price if c_price is not None else '不可购买'
            container_info = f"武器箱id:{c.get('id', 'N/A')}\n{c.get('name', '')}\n价格:{c_price_str}"

        # 对涨跌幅进行格式化：正数前加 '+'
        def _fmt_rate(v):
            try:
                fv = float(v)
                # 去掉多余的小数点
                if fv.is_integer():
                    sval = str(int(fv))
                else:
                    sval = str(fv)
                return f"+{sval}" if fv > 0 else sval
            except Exception:
                return str(v)

        sr7 = _fmt_rate(sell_rate_7)
        sr30 = _fmt_rate(sell_rate_30)
        sr180 = _fmt_rate(sell_rate_180)
        sr365 = _fmt_rate(sell_rate_365)

        # 构造结果字符串（使用安全取值）
        result_str = (
            f"饰品ID:{gid}\n"
            f"{gname}\n"
            f"存世量:{statistic} 品质:{rarity}\n"
            f"steam\n"
            f"成交量:{turnover_number} 均价${turnover_avg}\n"
            f"挂刀比例:{steam_buff_conv}\n"
            f"buff\n"
            f"在售价:{buff_sell_price}元 数量{buff_sell_num}\n"
            f"求购价: {buff_buy_price}元 数量{buff_buy_num}\n"
            f"yyyp\n"
            f"在售价:{yyyp_sell_price}元 数量{yyyp_sell_num}\n"
            f"求购价: {yyyp_buy_price}元 数量{yyyp_buy_num}\n"
            f"短租：{yyyp_lease_price}元 长租{yyyp_long_lease_price}元\n"
            f"涨跌幅\n"
            f"7天{sr7}% 30天{sr30}%\n"
            f"180天{sr180}% 365天{sr365}%\n"
            f"所属武器箱/收藏品\n"
            f"{container_info}"
        )
        yield event.plain_result(result_str) # 发送结果给用户
    #1.挂刀/反向挂刀 2.最低价 3.最高价 4.成交量
    @filter.command("挂刀查询")
    async def find_hangdao(self, event: AstrMessageEvent):
        """这是一个 挂刀查询 指令"""
        # 获取纯文本参数，优先使用 get_plain_text（如果事件对象提供），否则回退到 message_str
        if hasattr(event, 'get_plain_text'):
            args_text = event.get_plain_text().replace("挂刀查询", "", 1).strip()
        else:
            args_text = event.message_str.replace("挂刀查询", "", 1).strip()

        args = args_text.split()
        if len(args) < 4:
            yield event.plain_result("参数不足，请依次提供四个参数，用空格分隔：\n1.挂刀/反向挂刀(0/1)\n2.最低价(不指定填0)\n3.最高价(不指定填0)\n4.最低成交量(不指定填0)")
            return

        # 按顺序解析参数并捕获格式错误
        try:
            option = int(args[0])
            price_min = int(args[1])
            price_max = int(args[2])
            turnover = int(args[3])
        except ValueError:
            yield event.plain_result("参数格式错误，请确保所有参数均为数字。")
            return
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
            'ApiToken': self.api_token,
            'Content-Type': 'application/json'
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json={
                    "page_index": 1,
                    "res": option,
                    "platforms": "BUFF-YYYP",
                    "sort_by": 1,
                    "min_price": price_min,
                    "max_price": price_max,
                    "turnover": turnover if turnover>0 else 10
                }, timeout=10.0)
                response.raise_for_status()
                # 解析响应
                obj = response.json()
        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {e}")
            yield event.plain_result("查询失败，请稍后再试。")
            return
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 状态错误: {e}")
            yield event.plain_result("查询失败，远端服务返回异常状态。")
            return
        except json.JSONDecodeError:
            logger.error("JSON 解析失败")
            yield event.plain_result("API响应格式错误，请联系管理员。")
            return
        data_map = obj['data']
        if not data_map:
            yield event.plain_result("未找到符合条件的饰品")
            return
        result_str = ""
        for i in range(min(10, len(data_map))):  # 从0到9
            item = data_map[i]
            # 安全读取数值，防止 KeyError 或 非数值 导致异常
            sid = item.get('id', 'N/A')
            name = item.get('name', '')
            steam_buy_price = item.get('steam_buy_price')
            turnover_number = item.get('turnover_number', 'N/A')
            try:
                to_hand = round(steam_buy_price * 0.87, 2) if isinstance(steam_buy_price, (int, float)) else 'N/A'
            except Exception:
                to_hand = 'N/A'

            buff_sell_price = item.get('buff_sell_price')
            buff_sell_num = item.get('buff_sell_num', 'N/A')
            buff_buy_price = item.get('buff_buy_price')
            buff_buy_num = item.get('buff_buy_num', 'N/A')

            yyyp_sell_price = item.get('yyyp_sell_price')
            yyyp_sell_num = item.get('yyyp_sell_num', 'N/A')
            yyyp_buy_price = item.get('yyyp_buy_price')
            yyyp_buy_num = item.get('yyyp_buy_num', 'N/A')

            def safe_ratio(a, b):
                try:
                    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and b != 0:
                        return round(a / b, 3)
                except Exception:
                    pass
                return 'N/A'

            buff_on_sale_ratio = safe_ratio(buff_sell_price, steam_buy_price)
            buff_buy_ratio = safe_ratio(buff_buy_price, steam_buy_price)
            yyyp_on_sale_ratio = safe_ratio(yyyp_sell_price, steam_buy_price)
            yyyp_buy_ratio = safe_ratio(yyyp_buy_price, steam_buy_price)

            item_str = f"""饰品ID:{sid}
{name}
steam
求购价:{steam_buy_price}
今日成交量:{turnover_number}
到手余额:{to_hand}
buff
在售价:{buff_sell_price}元 数量{buff_sell_num}
求购价: {buff_buy_price}元 数量{buff_buy_num}
挂刀比例:
在售:{buff_on_sale_ratio}
求购:{buff_buy_ratio}
yyyp
在售价:{yyyp_sell_price}元 数量{yyyp_sell_num}
求购价: {yyyp_buy_price}元 数量{yyyp_buy_num}
挂刀比例:
在售:{yyyp_on_sale_ratio}
求购:{yyyp_buy_ratio}
"""

            result_str += item_str

        # 输出结果
        yield event.plain_result(result_str)   
    @filter.command("指数查询")
    async def find_zhishu(self, event: AstrMessageEvent):
        url = "https://api.csqaq.com/api/v1/current_data?type=init"
        payload={}
        headers = {
            'ApiToken': self.api_token
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                obj = response.json()
        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {e}")
            yield event.plain_result("查询失败，请稍后再试。")
            return
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 状态错误: {e}")
            yield event.plain_result("查询失败，远端服务返回异常状态。")
            return
        except json.JSONDecodeError:
            logger.error("JSON 解析失败")
            yield event.plain_result("API响应格式错误，请联系管理员。")
            return
        data_map = obj.get('data', {}).get('sub_index_data', [])
        if not data_map:
            yield event.plain_result("当前指数数据不可用")
            return

        result_str = ""
        for i in range(min(11, len(data_map))):  # 取前11个项，确保不会越界
            item = data_map[i]
            name = item.get("name", "")
            market_index = item.get("market_index", "N/A")
            chg_rate = item.get("chg_rate", 0)

            # 格式化变动率，正数前加加号
            chg_rate_str = f"+{chg_rate}" if isinstance(chg_rate, (int, float)) and chg_rate > 0 else f"{chg_rate}"

            # 拼接字符串
            result_str += f"{name}\n当前指数:{market_index}\n今日变动率:{chg_rate_str}\n"

        # 更新日期，安全取值
        updated_at = data_map[0].get('updated_at') if isinstance(data_map[0], dict) else None
        if updated_at:
            result_str = "更新时间:\n" + updated_at + "\n" + result_str

        # 安全取出市场情绪
        greedy_val = 'N/A'
        greedy = obj.get('data', {}).get('greedy')
        try:
            if greedy and isinstance(greedy, list) and len(greedy) > 0 and isinstance(greedy[-1], list) and len(greedy[-1]) > 0:
                greedy_val = greedy[-1][-1]
        except Exception:
            greedy_val = 'N/A'

        online_info = obj.get('data', {}).get('online_number', {})
        current_number = online_info.get('current_number', 'N/A')
        rate_week = online_info.get('rate_week', 'N/A')

        result_str += f"市场情绪:{greedy_val}\n"
        result_str += f"当前在线人数:{current_number}\n本周人数涨幅:{rate_week}%"
        yield event.plain_result(result_str)