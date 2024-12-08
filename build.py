from PyInstaller.__main__ import run
import os
from pathlib import Path


#构建bot.exe
# if __name__ == '__main__':
#     conda_prefix = os.environ.get('CONDA_PREFIX', '')
#     current_dir = Path(__file__).parent.absolute()
    
#     opts = [
#         '--onefile',
#         '--paths', os.path.join(conda_prefix, 'Lib', 'site-packages'),
        
#         # 基本配置
#         '--noconfirm',
#         '--clean',
#         # '--debug=all',
        
#         # 数据文件
#         '--add-data', f'{current_dir}/awesome_bot;awesome_bot',
#         '--add-data', f'{current_dir}/.env;.',
        
#         # 依赖导入
#         '--hidden-import', 'nonebot',
#         '--hidden-import', 'nonebot.adapters.onebot.v11',
#         '--hidden-import', 'nonebot.drivers',
#         '--hidden-import', 'nonebot.drivers.fastapi',
#         '--hidden-import', 'fastapi',
#         '--hidden-import', 'uvicorn',
#         '--hidden-import', 'nonebot_plugin_apscheduler',
#         '--hidden-import', 'awesome_bot.plugins.kou1',
        
#         # 主程序
#         'bot.py'
#     ]
#     run(opts)

#打包扣1神器
if __name__ == '__main__':
    opts = [
            # '--windowed',
            '--name', '扣1神器v2.0',
            '--add-data', 'bot.exe;.',
            '--add-binary','bot.exe;.',
            'main.py'
            ]
#先构建bot.exe，再构建扣1神器
    run(opts)