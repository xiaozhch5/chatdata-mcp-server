import mcp.types as types


async def echo_website(
    message: str,
) -> list[types.TextContent]:
    """简单的回显功能"""
    return [types.TextContent(type="text", text=f"回显: {message}")]


async def echo_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "echo":
        raise ValueError(f"Unknown tool: {name}")
    if "message" not in arguments:
        raise ValueError("Missing required argument 'message'")
    return await echo_website(arguments["message"])


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="echo",
            description="简单回显输入的消息",
            inputSchema={
                "type": "object",
                "required": ["message"],
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "要回显的消息",
                    }
                },
            },
        )
    ]