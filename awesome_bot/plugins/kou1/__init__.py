from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import driver
import asyncio
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent
from nonebot.typing import T_State
from typing import Dict, Optional
from nonebot.rule import startswith

# 常量定义
RECALL_TIMEOUT = 120  # 撤回超时时间(秒)
MAX_FEEDBACK_ATTEMPTS = 2  # 最大反馈尝试次数

class Config:
    """配置类"""
    def __init__(self):
        self.data = {}
        self.load()
    
    def load(self) -> bool:
        try:
            data_path = self._get_config_path()
            if data_path.exists():
                self.data = json.loads(data_path.read_text(encoding='utf-8'))
                print("成功加载配置")
                print(f'配置文件路径为: {data_path}')
                return True
            return False
        except Exception as e:
            print(f"加载配置文件错误: {e}")
            return False
    
    @staticmethod
    def _get_config_path() -> Path:
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent / 'data.json'
        return Path(os.path.dirname(os.path.abspath(__file__))) / 'data.json'

class AutoReplyHandler:
    def __init__(self, bot: Bot, config: Config):
        self.bot = bot
        self.config = config
        # 修改数据结构为: Dict[int, List[Dict]]
        self.pending_recalls: Dict[int, list] = {}

    async def send_feedback(self, feedback_qq: int, feedback_msg: str, group_id: str, message_id: int):
        """发送反馈消息"""
        recall_info = {
            'message_id': message_id,
            'group_id': int(group_id),
            'timestamp': time.time(),
            'content': feedback_msg.split('\n')[0][:20] + '...'  # 保存消息预览
        }
        
        if feedback_qq not in self.pending_recalls:
            self.pending_recalls[feedback_qq] = []
        self.pending_recalls[feedback_qq].append(recall_info)

        # 清理超时消息
        self._clean_expired_messages(feedback_qq)
        
        for i in range(MAX_FEEDBACK_ATTEMPTS):
            try:
                current_msg = f"扣1神器[第{i+1}次提示]\n{feedback_msg}"
                await self.bot.send_private_msg(user_id=feedback_qq, message=current_msg)
                await asyncio.sleep(1)
            except Exception as e:
                print(f"发送第{i+1}次私聊消息失败: {e}")

        cq_code = f"[CQ:contact,type=group,id={group_id}]"
        await self.bot.send_private_msg(user_id=feedback_qq, message=cq_code)

    def _clean_expired_messages(self, user_id: int):
        """清理超时消息"""
        if user_id not in self.pending_recalls:
            return
            
        current_time = time.time()
        self.pending_recalls[user_id] = [
            msg for msg in self.pending_recalls[user_id] 
            if current_time - msg['timestamp'] <= RECALL_TIMEOUT
        ]
        
        if not self.pending_recalls[user_id]:
            del self.pending_recalls[user_id]

    async def list_recalls(self, user_id: int) -> str:
        """列出待撤回消息"""
        if user_id not in self.pending_recalls:
            return "没有待撤回的消息"
            
        self._clean_expired_messages(user_id)
        if user_id not in self.pending_recalls:
            return "没有待撤回的消息"
            
        msg_list = []
        for idx, msg in enumerate(self.pending_recalls[user_id], 1):
            remaining = RECALL_TIMEOUT - (time.time() - msg['timestamp'])
            if remaining > 0:
                msg_list.append(
                    f"{idx}. {msg['content']} (剩余{int(remaining)}秒)"
                )
                
        return "待撤回消息列表：\n" + "\n".join(msg_list) + "\n发送 “/撤回 序号” 撤回指定消息例如：/撤回 1"

    async def handle_recall(self, user_id: int, msg_index: str = "") -> str:
        """处理撤回请求"""
        if user_id not in self.pending_recalls:
            return "没有待撤回的消息"
            
        self._clean_expired_messages(user_id)
        if user_id not in self.pending_recalls:
            return "没有待撤回的消息"

        # 如果没有指定序号，显示消息列表
        if not msg_index:
            return await self.list_recalls(user_id)

        try:
            idx = int(msg_index) - 1
            if idx < 0 or idx >= len(self.pending_recalls[user_id]):
                return f"无效的序号: {msg_index}"
                
            recall_info = self.pending_recalls[user_id][idx]
            
            if time.time() - recall_info['timestamp'] > RECALL_TIMEOUT:
                self.pending_recalls[user_id].pop(idx)
                if not self.pending_recalls[user_id]:
                    del self.pending_recalls[user_id]
                return "该消息已超时，无法撤回"

            await self.bot.delete_msg(message_id=recall_info['message_id'])
            self.pending_recalls[user_id].pop(idx)
            if not self.pending_recalls[user_id]:
                del self.pending_recalls[user_id]
            return "已成功撤回消息"
        except ValueError:
            return f"无效的序号格式: {msg_index}"
        except Exception as e:
            return f"撤回失败: {str(e)}"

# 全局实例
config = Config()
handler = None

@driver.on_startup
async def _():
    print("kou1 插件已加载")
    global config
    config.load()

@on_message(priority=5).handle()
async def handle_group_message(bot: Bot, event: GroupMessageEvent, state: T_State):
    global handler
    if handler is None:
        handler = AutoReplyHandler(bot, config)

    try:
        group_id = str(event.group_id)
        message = str(event.get_message())
        
        for check in config.data['checks']:
            if group_id == check['group'] and check['keyword'] in message:
                msg_result = await bot.send_group_msg(
                    group_id=int(group_id),
                    message=check['send_word']
                )
                
                if config.data.get('FeedBackqq'):
                    feedback_msg = await _build_feedback_message(bot, event, check, message)
                    await handler.send_feedback(
                        int(config.data['FeedBackqq']),
                        feedback_msg,
                        group_id,
                        msg_result['message_id']
                    )
                break
    except Exception as e:
        print(f"处理消息时发生错误: {e}")

@on_message(rule=startswith("/"), priority=5).handle()
async def handle_private_message(bot: Bot, event: PrivateMessageEvent):
    global handler
    if handler is None:
        handler = AutoReplyHandler(bot, config)

    user_id = event.user_id
    message = str(event.get_message()).strip()

    if not config.data.get('FeedBackqq') or user_id != int(config.data['FeedBackqq']):
        await bot.send_private_msg(user_id=user_id, message="您没有权限执行此操作")
        return

    if message.startswith("/撤回"):
        # 解析可能的序号
        parts = message.split()
        msg_index = parts[1] if len(parts) > 1 else ""
        result = await handler.handle_recall(user_id, msg_index)
        await bot.send_private_msg(user_id=user_id, message=result)

async def _build_feedback_message(bot: Bot, event: GroupMessageEvent, check: dict, message: str) -> str:
    """构建反馈消息"""
    group_info = await bot.get_group_info(group_id=event.group_id)
    sender_info = await bot.get_stranger_info(user_id=event.user_id)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return (
        f"群名称: {group_info['group_name']}\n"
        f"发送者: {sender_info['nickname']} (QQ: {event.user_id})\n"
        f"发送时间: {current_time}\n"
        f"触发消息: {message}\n"
        f"已发送: {check['send_word']},请点击下方群聊查看是否撤回！！！"
    )