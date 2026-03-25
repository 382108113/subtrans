#!/usr/bin/env python3
"""
SubTrans 启动脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from subtrans.main import main

if __name__ == '__main__':
    main()
