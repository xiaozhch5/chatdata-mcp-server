# ChatData MCP 资源系统

这个目录包含MCP服务器的资源实现。资源是可以由MCP客户端直接请求的数据对象，如文本、图像或其他二进制数据。

## 现有资源

当前实现了以下资源类型：

### 文本资源 (text_resources.py)
- `greeting.txt`: 问候语
- `help.txt`: 帮助信息
- `about.txt`: 关于信息
- `guide.txt`: 使用指南
- `documentation.txt`: 文档资源

### 二进制资源 (binary_resources.py)
- `sample_image.png`: 示例图像
- `sample_binary.bin`: 示例二进制数据
- `sample_json.json`: 示例JSON数据

### 动态资源 (dynamic_resources.py)
- `system_info.json`: 系统信息
- `current_time.txt`: 当前时间
- `memory_usage.json`: 内存使用情况

## 如何添加新资源

1. 在`resources`目录下创建新的Python模块（例如：`my_resources.py`）
2. 实现以下两个函数：
   - `get_resources()`: 返回资源定义的列表
   - `read_resource(name)`: 根据名称返回资源内容

## 资源定义示例

```python
import mcp.types as types
from pydantic import FileUrl

def get_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri=FileUrl("file:///my_resource.txt"),
            name="my_resource",
            description="我的自定义资源",
            mimeType="text/plain",
        )
    ]

def read_resource(name: str) -> str | bytes:
    if name == "my_resource" or name == "my_resource.txt":
        return "这是我的自定义资源内容"
    return None
```

## 注意事项

- 资源URI应使用`file:///`格式，后面跟着资源名称和适当的扩展名
- 确保`mimeType`正确匹配资源内容类型
- 对于二进制资源，返回类型应为`bytes`
- 对于文本资源，返回类型应为`str`
- 如果资源不存在，`read_resource`应返回`None` 