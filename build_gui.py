from PyInstaller.__main__ import run
import os
from pathlib import Path
import shutil
#打包扣1神器
if __name__ == '__main__':

    # 清理构建目录
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    opts = [
            '--windowed',
            '--name', '扣1神器v2.0.0',
            '--add-data', 'bot.exe;.',
            '--add-binary','bot.exe;.',
            'gui.py'
        ]
#先构建bot.exe，再构建扣1神器
    run(opts)