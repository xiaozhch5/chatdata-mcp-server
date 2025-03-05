import mcp.types as types
import re


async def summarize_text(
    text: str, 
    max_sentences: int = 3
) -> list[types.TextContent]:
    """生成文本摘要（简单版本）"""
    print(f"生成摘要，最大句子数: {max_sentences}")
    
    # 分割文本为句子
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # 简单的摘要生成 - 取前几句话
    # 注意：这只是一个非常简单的摘要方法，实际应用中可能需要更复杂的算法
    if len(sentences) <= max_sentences:
        summary = text
    else:
        summary = ' '.join(sentences[:max_sentences])
    
    # 添加摘要说明
    result = f"原始文本长度: {len(text)} 字符, {len(sentences)} 句话\n"
    result += f"摘要 ({max_sentences} 句话):\n{summary}"
    
    return [types.TextContent(type="text", text=result)]


async def text_summary_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "text_summary":
        raise ValueError(f"Unknown tool: {name}")
    if "text" not in arguments:
        raise ValueError("Missing required argument 'text'")
    
    max_sentences = arguments.get("max_sentences", 3)
    try:
        max_sentences = int(max_sentences)
    except (ValueError, TypeError):
        max_sentences = 3
    
    return await summarize_text(arguments["text"], max_sentences)


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="text_summary",
            description="为文本生成简短摘要",
            inputSchema={
                "type": "object",
                "required": ["text"],
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "需要摘要的原始文本",
                    },
                    "max_sentences": {
                        "type": "integer",
                        "description": "摘要最大句子数，默认为3",
                        "default": 3
                    }
                },
            },
        )
    ] 