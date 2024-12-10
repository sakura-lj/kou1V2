import nonebot
import sys
import os
from nonebot.adapters.onebot.v11 import Adapter
from nonebot import logger
from pathlib import Path
from typing import Union
from nonebot.log import logger_id
#以下为日志功能，debug的时候用

# def setup_logging(
#     log_level: Union[str, int] = "INFO",
#     log_format: str = "<g>{time:YYYY-MM-DD HH:mm:ss}</g> [<lvl>{level}</lvl>] <c><u>{name}</u></c> | {message}",
# ):
#     """
#     配置日志系统
    
#     Args:
#         log_level: 日志级别
#         log_format: 日志格式
#     """
#     try:
#         # 获取日志目录
#         if getattr(sys, 'frozen', False):
#             base_path = os.path.dirname(sys.executable)
#         else:
#             base_path = os.path.dirname(os.path.abspath(__file__))
        
#         # 创建logs目录
#         log_dir = os.path.join(base_path, "logs")
#         os.makedirs(log_dir, exist_ok=True)
        
#         # 配置日志文件路径
#         log_path = os.path.join(log_dir, "bot_{time:YYYY-MM-DD}.log")
        
#         # 移除所有已存在的处理器
#         logger.remove(logger_id)
        
#         # 添加文件处理器
#         logger.add(
#             log_path,
#             level=log_level,
#             format=log_format,
#             rotation="00:00",  # 每天零点创建新文件
#             retention="30 days",  # 保留30天的日志
#             compression="zip",  # 压缩旧日志
#             encoding="utf-8",
#             enqueue=True,  # 异步写入
#             diagnose=True,  # 显示完整的异常堆栈
#             catch=True,  # 捕获异常
#         )
        
#         # 如果不是窗口模式，添加控制台输出
#         if not getattr(sys, 'frozen', False) or '--console' in sys.argv:
#             logger.add(
#                 sys.stdout,
#                 level=log_level,
#                 format=log_format,
#                 diagnose=True,
#                 catch=True
#             )
            
#         # 记录启动信息
#         logger.success("日志系统初始化成功")
#         logger.info(f"日志级别: {log_level}")
#         logger.info(f"日志目录: {log_dir}")
        
#         return True
        
#     except Exception as e:
#         print(f"日志系统初始化失败: {e}")
#         return False

def init_nonebot():
    try:
        # 初始化日志
        # if not setup_logging(log_level="INFO"):
        #     return False

        # 初始化NoneBot
        nonebot.init()

        # 注册适配器
        driver = nonebot.get_driver()
        driver.register_adapter(Adapter)

        # 获取项目根目录的绝对路径
        root_path = os.path.dirname(os.path.abspath(__file__))
        print(f"根目录: {root_path}")

        # 设置插件目录路径
        plugins_path = os.path.join(root_path, "awesome_bot", "plugins")
        plugins_path = os.path.abspath(plugins_path)
        # 添加插件目录到Python路径
        sys.path.insert(0, os.path.dirname(plugins_path))
        
        print(f"插件路径: {plugins_path}")
        
        # 确保插件目录存在
        if not os.path.exists(plugins_path):
            print(f"警告: 插件目录不存在: {plugins_path}")
            os.makedirs(plugins_path, exist_ok=True)
        print(f"之前工作目录: {os.getcwd()}")
        # 切换到插件目录的父目录
        # os.chdir(os.path.dirname(plugins_path))
        os.chdir(root_path)
        # 打印当前工作目录
        print(f"当前工作目录: {os.getcwd()}")

        print("开始加载插件")
        
        # 使用相对于awesome_bot的模块路径加载插件
        nonebot.load_plugins("awesome_bot/plugins")

        return True
    except Exception as e:
        print(f"初始化错误: {e}")
        return False
if __name__ == "__main__":
    if init_nonebot():
        try:
            nonebot.run()
        except Exception as e:
            print(f"运行时错误: {e}")
            input("按回车键退出...")
            sys.exit(1)
    else:
        input("初始化失败，按回车键退出...")
        sys.exit(1)