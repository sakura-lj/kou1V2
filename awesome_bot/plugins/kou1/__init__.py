from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import driver

from .config import Config
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
    name="kou1",    # 插件名称
    description="", # 插件描述
    usage="",    # 使用帮助
    config=Config,  # 配置对象
)

config = get_plugin_config(Config)

@driver.on_startup
async def _():
    print("kou1 插件已加载")

# 加载配置文件
try:
    data_path = Path(sys.executable).parent / 'data.json'
    print(f"当前读取的json文件路径是: {data_path}")
    
    if data_path.exists():
        data = json.loads(data_path.read_text(encoding='utf-8'))
        if all(key in data for key in ['group', 'keyword', 'qq', 'start_date']):
            group_ids: List[str] = data['group']
            keywords: List[str] = data['keyword']
            YOUR_QQ_NUMBER: int = data['qq']
            send_word: str = data['send_word']
        else:
            print("Error: data.json缺少必要的配置项")
            sys.exit(1)
except Exception as e:
    print(f"Error reading data: {e}")
    sys.exit(1)

# 群消息处理
group_msg = on_message(priority=5)

@group_msg.handle()
async def handle_group_message(bot: Bot, event: GroupMessageEvent, state: T_State):
    group_id = str(event.group_id)
    
    if group_id not in group_ids:
        return
    
    message = str(event.get_message())
    matched = False
    
    # 先检查是否包含关键词,避免无谓的API调用
    for keyword in keywords:
        if re.search(keyword, message, re.IGNORECASE):
            matched = True
            break
            
    if not matched:
        return
        
    sender_id = event.user_id
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # 并发执行API调用
        tasks = [
            bot.get_group_info(group_id=int(group_id)),
            bot.get_stranger_info(user_id=sender_id),
            bot.send_group_msg(group_id=int(group_id), message=send_word)
        ]
        results = await asyncio.gather(*tasks)
        group_info, sender_info, _ = results
        
        feedback_msg = (f'群名称: {group_info["group_name"]}\n'
                       f'发送者: {sender_info["nickname"]} (QQ: {sender_id})\n'
                       f'发送时间: {time}\n'
                       f'消息: {message}\n'
                       f'已对这个任务扣{send_word}，请核对行程看是否撤回！')
        
        # 发送3次
        for _ in range(3):
            await bot.send_private_msg(
                user_id=YOUR_QQ_NUMBER,
                message=feedback_msg
            )
        print('消息发送成功')
                
    except Exception as e:
        print(f'发送消息错误: {e}')