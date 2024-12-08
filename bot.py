import nonebot
import sys
import os
from nonebot.adapters.onebot.v11 import Adapter
from pathlib import Path

try:
    # 初始化 NoneBot
    nonebot.init()

    # 注册适配器
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)

    # 设置插件路径
    if getattr(sys, 'frozen', False):   # 判断是否是打包后的可执行文件
        # 如果是打包后的可执行文件
        base_path = sys._MEIPASS
        print(f"当前路径base_path: {base_path}")
        sys.path.insert(0, base_path)   # 将当前路径添加到系统路径中
    else:
        # 如果是直接运行的Python脚本
        base_path = os.path.dirname(os.path.abspath(__file__))
        print(f"当前路径base_path: {base_path}")
        
    # 加载插件
    nonebot.load_plugin("awesome_bot.plugins.kou1")

    if __name__ == "__main__":
        nonebot.run()
except Exception as e:
    print(f"发生错误: {e}")
    input("按回车键退出...")
    sys.exit(1) 