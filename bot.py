import nonebot
from nonebot.adapters.onebot.v11 import Adapter as v11Adapter  # 避免重复命名

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(v11Adapter)

# 在这里加载插件
nonebot.load_builtin_plugins("echo")  # 内置插件
nonebot.load_plugin("awesome_bot.plugins.kou1")  # 使用相对于 bot.py 的完整路径
#nonebot.load_plugins("awesome_bot/plugins")  # 使用相对于 bot.py 的完整路径

if __name__ == "__main__":
    nonebot.run()