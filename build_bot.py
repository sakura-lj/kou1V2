from PyInstaller.__main__ import run
from pathlib import Path
import shutil
import os

if __name__ == '__main__':
    current_dir = Path(__file__).parent.absolute()

    # 清理构建目录
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    opts = [
        '--noconfirm',
        '--clean',
        '--onefile',
        "--windowed",
        # 路径配置
        '--paths', str(current_dir),

        # 数据文件配置
        '--add-data', '.env;.',
        '--add-data', 'awesome_bot/plugins;awesome_bot/plugins',
        '--add-data', 'pyproject.toml;.',

        # 工作目录和输出配置
        '--workpath', './build',
        '--distpath', './dist',
        '--specpath', str(current_dir),


        # 依赖导入
        '--hidden-import', 'loguru',
        '--hidden-import', 'nonebot',
        '--hidden-import', 'nonebot.plugins',
        '--hidden-import', 'nonebot.adapters.onebot.v11',
        '--hidden-import', 'nonebot.drivers',
        '--hidden-import', 'nonebot.drivers.fastapi',
        '--hidden-import', 'fastapi',
        '--hidden-import', 'uvicorn',
        '--hidden-import', 'nonebot_plugin_apscheduler',
        '--hidden-import', 'awesome_bot.plugins',
        '--hidden-import', 'awesome_bot',
        '--runtime-hook', 'runtime_hook.py',
        # 主程序
        'bot.py'
    ]

    run(opts)