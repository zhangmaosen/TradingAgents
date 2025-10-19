#!/usr/bin/env python3
"""
交易历史查看器快速启动脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.view_trades import app

if __name__ == "__main__":
    app()
