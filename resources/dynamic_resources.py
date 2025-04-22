import mcp.types as types
from pydantic import FileUrl
import json
import datetime
import platform
import psutil
import os

def get_resources() -> list[types.Resource]:
    """返回此模块中的所有动态资源定义"""
    resources = []
    
    # 系统信息资源
    resources.append(
        types.Resource(
            uri=FileUrl("file:///system_info.json"),
            name="system_info",
            description="动态生成的系统信息资源",
            mimeType="application/json",
        )
    )
    
    # 时间信息资源
    resources.append(
        types.Resource(
            uri=FileUrl("file:///current_time.txt"),
            name="current_time",
            description="当前时间信息",
            mimeType="text/plain",
        )
    )
    
    # 内存使用情况资源
    resources.append(
        types.Resource(
            uri=FileUrl("file:///memory_usage.json"),
            name="memory_usage",
            description="内存使用情况",
            mimeType="application/json",
        )
    )
    
    return resources

def read_resource(name: str) -> str | bytes:
    """读取指定名称的动态资源内容"""
    if name == "system_info" or name == "system_info.json":
        # 生成系统信息
        system_info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture(),
            "node": platform.node(),
            "machine": platform.machine(),
        }
        return json.dumps(system_info, indent=2)
    
    elif name == "current_time" or name == "current_time.txt":
        # 生成当前时间信息
        now = datetime.datetime.now()
        return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n时区: {datetime.datetime.now().astimezone().tzinfo}"
    
    elif name == "memory_usage" or name == "memory_usage.json":
        # 生成内存使用情况
        memory = psutil.virtual_memory()
        memory_data = {
            "total": f"{memory.total / (1024 ** 3):.2f} GB",
            "available": f"{memory.available / (1024 ** 3):.2f} GB",
            "used": f"{memory.used / (1024 ** 3):.2f} GB",
            "percent": f"{memory.percent}%",
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return json.dumps(memory_data, indent=2)
    
    return None 