import os
import sys
#处理无法输出日志时的报错
def setup_environment():
    if getattr(sys, 'frozen', False):
        for stream_name in ['stderr', 'stdout']:
            if getattr(sys, stream_name) is None:
                setattr(sys, stream_name, open(os.devnull, 'w'))

setup_environment()