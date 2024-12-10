from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import driver
import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State

__plugin_meta__ = PluginMetadata(
    name="auto_reply",
    description="自动回复插件",
    usage="检测群消息并自动回复",
)

# 全局变量
config = {}

@driver.on_startup
async def _():
    print("auto_reply 插件已加载")
    load_config()

def load_config():
    global config
    try:
        # 获取配置文件路径
        if getattr(sys, 'frozen', False):
            data_path = Path(sys.executable).parent / 'data.json'
        else:
            data_path = Path(os.path.dirname(os.path.abspath(__file__))) / 'data.json'
        
        print(f"当前读取的json文件路径是: {data_path}")
        
        if data_path.exists():
            config = json.loads(data_path.read_text(encoding='utf-8'))
            print("成功加载配置")
            return True
    except Exception as e:
        print(f"加载配置文件错误: {e}")
        return False

# 群消息处理
group_msg = on_message(priority=5)

@group_msg.handle()
async def handle_group_message(bot: Bot, event: GroupMessageEvent, state: T_State):
    try:
        group_id = str(event.group_id)
        message = str(event.get_message())
        sender_id = event.user_id
        
        # 遍历检查规则
        matched = False
        for check in config['checks']:
            if group_id == check['group'] and check['keyword'] in message:
                matched = True
                await bot.send_group_msg(
                    group_id=int(group_id),
                    message=check['send_word']
                )
                
                # 获取详细信息
                group_info = await bot.get_group_info(group_id=int(group_id))
                sender_info = await bot.get_stranger_info(user_id=sender_id)
                time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 构建反馈消息
                feedback_msg = (
                    f"群名称: {group_info['group_name']}\n"
                    f"发送者: {sender_info['nickname']} (QQ: {sender_id})\n"
                    f"发送时间: {time}\n"
                    f"触发消息: {message}\n"
                    f"已发送: {check['send_word']},请点击下方群聊查看是否撤回！！！"
                )
                
                # 发送私聊反馈
                if config['FeedBackqq']:
                    feedback_qq = int(config['FeedBackqq'])
                    cq_code = f"[CQ:contact,type=group,id={group_id}]"
                    
                    for i in range(2):
                        try:
                            current_msg = f"[第{i+1}次提示]\n{feedback_msg}"
                            await bot.send_private_msg(
                                user_id=feedback_qq,
                                message=current_msg
                            )
                            print(f"已发送第{i+1}次提示消息到 QQ: {feedback_qq}")
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"发送第{i+1}次私聊消息失败: {e}")
                    
                    await bot.send_private_msg(user_id=feedback_qq, message=cq_code)
                break
                
    except Exception as e:
        print(f"处理消息时发生错误: {e}")