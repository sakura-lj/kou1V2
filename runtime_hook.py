import os
import sys

def setup_environment():
    if getattr(sys, 'frozen', False):
        # 确保sys.stderr存在
        if sys.stderr is None:
            sys.stderr = open(os.devnull, 'w')
        # 确保sys.stdout存在
        if sys.stdout is None:
            sys.stdout = open(os.devnull, 'w')

setup_environment()