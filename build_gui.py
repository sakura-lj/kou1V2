from PyInstaller.__main__ import run
import os
from pathlib import Path

#打包扣1神器
if __name__ == '__main__':
    opts = [
            '--windowed',
            '--name', '扣1神器v2.0',
            '--add-data', 'bot.exe;.',
            '--add-binary','bot.exe;.',
            'gui.py'
            ]
#先构建bot.exe，再构建扣1神器
    run(opts)