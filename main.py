#!/usr/bin/env python3
"""
ChatData MCP 服务器主入口
这个脚本提供了一个简单的入口点，用于启动MCP服务器
"""

import sys
import os
from server.server import main as server_main

def main():
    """
    主入口函数，用于启动MCP服务器
    默认调用server.server.main函数
    """
    print("启动 ChatData MCP 服务器...")
    
    # 检查环境变量
    check_environment()
    
    # 调用服务器主函数
    return server_main()

def check_environment():
    """检查环境变量和依赖"""
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 12):
        print(f"警告: 推荐使用Python 3.12或更高版本。当前版本: {python_version.major}.{python_version.minor}")
    
    # 检查是否存在.env文件
    if not os.path.exists(".env"):
        print("提示: 未找到.env文件。某些功能可能需要环境变量配置。")
    
    # 打印调试信息
    if 'DEBUG' in os.environ and os.environ['DEBUG'].lower() in ('1', 'true'):
        print(f"Python版本: {sys.version}")
        print(f"工作目录: {os.getcwd()}")

if __name__ == "__main__":
    sys.exit(main())
