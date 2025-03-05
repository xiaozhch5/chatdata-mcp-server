import mcp.types as types
import black
import autopep8
import textwrap


async def format_python_code(
    code: str,
    formatter: str = "black"
) -> list[types.TextContent]:
    """使用指定的格式化工具格式化Python代码"""
    print(f"使用 {formatter} 格式化代码")
    
    try:
        if formatter.lower() == "black":
            # 使用black格式化（简单模式）
            formatted_code = black.format_str(code, mode=black.Mode())
            
        elif formatter.lower() == "autopep8":
            # 使用autopep8格式化
            formatted_code = autopep8.fix_code(code)
            
        else:
            # 默认使用一个简单的缩进格式化
            formatted_code = textwrap.dedent(code).strip()
        
        result = f"格式化工具: {formatter}\n\n"
        result += "格式化后的代码:\n"
        result += "```python\n"
        result += formatted_code
        result += "\n```"
        
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        error_msg = f"格式化代码时出错: {str(e)}"
        return [types.TextContent(type="text", text=error_msg)]


async def code_formatter_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "code_formatter":
        raise ValueError(f"Unknown tool: {name}")
    
    # 检查必需参数
    if "code" not in arguments:
        raise ValueError("Missing required argument 'code'")
    
    # 获取参数
    code = arguments["code"]
    formatter = arguments.get("formatter", "black")
    
    # 调用格式化函数
    return await format_python_code(code, formatter)


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="code_formatter",
            description="格式化Python代码",
            inputSchema={
                "type": "object",
                "required": ["code"],
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "需要格式化的Python代码",
                    },
                    "formatter": {
                        "type": "string",
                        "description": "使用的格式化工具，支持'black'或'autopep8'，默认为'black'",
                        "enum": ["black", "autopep8", "simple"],
                        "default": "black"
                    }
                },
            },
        )
    ] 