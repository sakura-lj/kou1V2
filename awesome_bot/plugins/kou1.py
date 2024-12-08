from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import driver
import asyncio
import os
import sys
import json
import re
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from nonebot import on_command, on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.plugin import on_keyword
from nonebot.typing import T_State

__plugin_meta__ = PluginMetadata(
    name="kou1",
    description="自动扣1插件",
    usage="检测群消息并自动扣1",
)

# 全局变量
group_ids: List[str] = []
keywords: List[str] = []
YOUR_QQ_NUMBER: int = 0
send_word: str = "1"

@driver.on_startup
async def _():
    print("kou1 插件已加载")
    load_config()

def load_config():
    global group_ids, keywords, YOUR_QQ_NUMBER, send_word
    try:
        # 获取配置文件路径
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            data_path = Path(base_path) / 'data.json'
        else:
            data_path = Path(sys.executable).parent / 'data.json'
        
        print(f"当前读取的json文件路径是: {data_path}")
        
        if data_path.exists():
            data = json.loads(data_path.read_text(encoding='utf-8'))
            
            # 验证并加载配置
            if all(key in data for key in ['group', 'keyword', 'qq', 'send_word']):
                group_ids = [str(g) for g in data['group']]
                keywords = data['keyword']
                YOUR_QQ_NUMBER = int(data['qq'])
                send_word = str(data['send_word'])
                print(f"成功加载配置: 群组={group_ids}, 关键词={keywords}, QQ={YOUR_QQ_NUMBER}")
                return True
            else:
                print("配置文件缺少必要字段")
                return False
    except Exception as e:
        print(f"加载配置文件错误: {e}")
        return False

# 群消息处理
group_msg = on_message(priority=5)

@group_msg.handle()
async def handle_group_message(bot: Bot, event: GroupMessageEvent, state: T_State):
    try:
        group_id = str(event.group_id)
        
        # 检查群号
        if group_id not in group_ids:
            return
        
        message = str(event.get_message())
        
        # 检查关键词
        if not any(keyword in message.lower() for keyword in keywords):
            return
            
        sender_id = event.user_id
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 发送群消息
        await bot.send_group_msg(group_id=int(group_id), message=send_word)
        
        # 获取详细信息
        group_info = await bot.get_group_info(group_id=int(group_id))
        sender_info = await bot.get_stranger_info(user_id=sender_id)
        # 构建反馈消息
        feedback_msg = (
            f"群名称: {group_info['group_name']}\n"
            f"发送者: {sender_info['nickname']} (QQ: {sender_id})\n"
            f"发送时间: {time}\n"
            f"触发消息: {message}\n"
            f"已发送: {send_word},请点击下方群聊查看是否撤回！！！"
        )
        cq_code = f"[CQ:contact,type=group,id={group_id}]"


        # 发送私聊消息给指定QQ
        if YOUR_QQ_NUMBER > 0:
            for i in range(2):  # 循环3次
                try:
                    # 添加发送次数到消息中
                    current_msg = f"[第{i+1}次提示]\n{feedback_msg}"
                    
                    await bot.send_private_msg(
                        user_id=YOUR_QQ_NUMBER,
                        message=current_msg
                    )
                    print(f"已发送第{i+1}次提示消息到 QQ: {YOUR_QQ_NUMBER}")
                    
                    # 添加短暂延迟，避免消息发送太快
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"发送第{i+1}次私聊消息失败: {e}")
            await bot.send_private_msg(user_id=YOUR_QQ_NUMBER, message=cq_code)
    except Exception as e:
        print(f"处理消息时发生错误: {e}")
