import nonebot
import sys
import os
from nonebot.adapters.onebot.v11 import Adapter
from pathlib import Path

def init_nonebot():
    try:
        # 初始化 NoneBot
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
        os.chdir(os.path.dirname(plugins_path))
        # 打印当前工作目录
        print(f"当前工作目录: {os.getcwd()}")

        print("开始加载插件")
        
        # 使用相对于awesome_bot的模块路径加载插件
        nonebot.load_plugins("plugins")

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