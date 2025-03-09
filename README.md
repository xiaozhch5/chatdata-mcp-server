# ChatData MCP 服务器

ChatData MCP 服务器是一个基于 Model Control Protocol (MCP) 的服务应用程序，提供了丰富的工具集和提示系统，用于增强大型语言模型的能力。

## 项目简介

该项目提供了一个灵活的服务器框架，允许通过MCP协议与大型语言模型进行交互。该服务器可以：

- 执行各种工具函数，扩展模型的能力
- 提供预设的提示模板，简化常见任务
- 支持通过标准输入/输出或SSE方式进行通信
- 自动发现和注册新添加的工具和提示

## 核心组件

### 工具系统 (`tools/`)

工具模块提供了各种功能扩展，使语言模型能够执行具体任务：

- **网络工具**：
  - `web_scraper.py` - 网页内容抓取工具
  - `ip_info.py` - IP地址信息查询工具
  - `http_client.py` - HTTP请求客户端
  - `fetch.py` - 简单网页获取工具
  - `browser_use.py` - 基于browser_use获取网络信息
  
- **数据处理工具**：
  - `data_converter.py` - 数据格式转换工具(JSON/YAML/XML)
  - `text_summary.py` - 文本摘要生成工具
  - `calculator.py` - 高级数学计算工具
  
- **开发辅助工具**：
  - `code_formatter.py` - 代码格式化工具
  - `postgres.py` - PostgreSQL数据库查询工具
  
- **多媒体工具**：
  - `image_gen.py` - 图像生成工具
  
- **其他实用工具**：
  - `translator.py` - 文本翻译工具
  - `weather.py` - 天气查询工具
  - `echo.py` - 简单的回显工具

### 提示系统 (`prompts/`)

提示模块提供了各种预设的提示模板，用于快速生成高质量的回复：

- `simple.py` - 基本提示模板
- `content_generator.py` - 内容生成提示
- `code_review.py` - 代码审查提示
- `utils.py` - 提示工具函数

### 服务器组件 (`server/`)

服务器模块处理客户端请求和响应，支持多种通信方式：

- 标准输入/输出 (stdio) 模式
- 服务器发送事件 (SSE) 模式

## 安装与使用
```
uv venv --python 3.12
```

### 安装依赖

```bash
pip install -e .
```

或使用 `uv`：

```bash
uv pip install -e .
```

安装playwright

```bash
playwright install
```

### 启动服务器

#### stdio 模式（默认）

```bash
server
```

#### SSE 模式

```bash
server --transport sse --port 8000
```

## 开发指南

### 添加新工具

1. 在 `tools/` 目录中创建新的 Python 文件
2. 实现一个主函数和一个工具调用函数
3. 提供 `get_tools()` 函数返回工具定义

示例：

```python
import mcp.types as types

async def my_function(param1, param2):
    # 实现功能
    return [types.TextContent(type="text", text="结果")]

async def my_tool(name: str, arguments: dict):
    if name != "my_tool":
        raise ValueError(f"Unknown tool: {name}")
    
    # 提取参数
    param1 = arguments.get("param1")
    param2 = arguments.get("param2")
    
    return await my_function(param1, param2)

def get_tools():
    return [
        types.Tool(
            name="my_tool",
            description="工具描述",
            inputSchema={
                "type": "object",
                "required": ["param1"],
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "参数1描述",
                    },
                    "param2": {
                        "type": "string",
                        "description": "参数2描述",
                    }
                },
            },
        )
    ]
```

### 添加新提示

1. 在 `prompts/` 目录中创建新的 Python 文件
2. 实现提示生成函数
3. 提供 `get_prompts()` 函数返回提示定义

示例：

```python
import mcp.types as types
from .utils import create_messages

def my_prompt(context=None, topic=None):
    messages = create_messages(context, topic)
    
    return types.GetPromptResult(
        messages=messages,
        description="提示描述"
    )

def get_prompts():
    return [
        types.Prompt(
            name="my_prompt",
            description="提示描述",
            func=my_prompt,
            args={
                "context": {
                    "type": "string",
                    "description": "上下文信息"
                },
                "topic": {
                    "type": "string",
                    "description": "主题"
                }
            }
        )
    ]
```

## 许可证

MIT
