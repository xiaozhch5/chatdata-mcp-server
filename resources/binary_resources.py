import mcp.types as types
from pydantic import FileUrl
import base64

# 样本二进制资源内容（这里使用base64编码的示例数据）
BINARY_RESOURCES = {
    "sample_image": base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC"
    ),  # 1x1 PNG图像
    "sample_binary": b"Hello, this is a binary resource example!",
    "sample_json": b'{"name": "ChatData MCP", "version": "1.0", "type": "resource_demo"}'
}

def get_resources() -> list[types.Resource]:
    """返回此模块中的所有二进制资源定义"""
    resources = []
    
    # 添加图像资源
    resources.append(
        types.Resource(
            uri=FileUrl("file:///sample_image.png"),
            name="sample_image",
            description="示例图像资源",
            mimeType="image/png",
        )
    )
    
    # 添加二进制资源
    resources.append(
        types.Resource(
            uri=FileUrl("file:///sample_binary.bin"),
            name="sample_binary",
            description="示例二进制资源",
            mimeType="application/octet-stream",
        )
    )
    
    # 添加JSON资源
    resources.append(
        types.Resource(
            uri=FileUrl("file:///sample_json.json"),
            name="sample_json",
            description="示例JSON资源",
            mimeType="application/json",
        )
    )
    
    return resources

def read_resource(name: str) -> bytes:
    """读取指定名称的二进制资源内容"""
    if name in BINARY_RESOURCES:
        return BINARY_RESOURCES[name]
    
    # 处理带扩展名的请求
    if name == "sample_image.png":
        return BINARY_RESOURCES["sample_image"]
    elif name == "sample_binary.bin":
        return BINARY_RESOURCES["sample_binary"]
    elif name == "sample_json.json":
        return BINARY_RESOURCES["sample_json"]
    
    return None 