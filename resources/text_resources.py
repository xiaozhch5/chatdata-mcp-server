import mcp.types as types
from pydantic import FileUrl

# 样本资源内容
SAMPLE_RESOURCES = {
    "greeting": "你好！这是一个简单的文本资源示例。",
    "help": "该服务器提供了一些用于测试的文本资源。",
    "about": "这是ChatData MCP服务器的简单资源实现。",
    "guide": "使用MCP资源API可以访问各种预设文本和二进制资源。",
    "documentation": "# ChatData MCP 资源\n\n## 简介\n这是MCP资源系统的文档资源。\n\n## 可用资源\n- greeting: 问候语\n- help: 帮助信息\n- about: 关于信息\n- guide: 使用指南\n- documentation: 本文档"
}

def get_resources() -> list[types.Resource]:
    """返回此模块中的所有资源定义"""
    return [
        types.Resource(
            uri=FileUrl(f"file:///{name}.txt"),
            name=name,
            description=f"一个名为{name}的示例文本资源",
            mimeType="text/plain",
        )
        for name in SAMPLE_RESOURCES.keys()
    ]

def read_resource(name: str) -> str:
    """读取指定名称的资源内容"""
    if name in SAMPLE_RESOURCES:
        return SAMPLE_RESOURCES[name]
    return None 