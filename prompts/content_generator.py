import mcp.types as types
from mcp.types import Prompt
import mcp


def generate_content(prompt: str, tone: str = None, length: str = None) -> str:
    """生成内容，可以指定语气和长度"""
    result = f"基于提示生成内容:\n\n{prompt}"
    
    if tone:
        result += f"\n\n使用的语气: {tone}"
    
    if length:
        result += f"\n\n长度要求: {length}"
    
    return result


def get_prompts() -> list[Prompt]:
    """返回此模块中的所有prompts"""
    return [
        Prompt(
            name="generate_content",
            description="生成指定内容，可以选择语气和长度",
            func=generate_content,
            arguments=[
                types.PromptArgument(
                    name="prompt",
                    description="生成内容的主题或提示",
                    required=True,
                ),
                types.PromptArgument(
                    name="tone",
                    description="内容的语气（如：正式、幽默、专业等）",
                    required=False,
                ),
                types.PromptArgument(
                    name="length",
                    description="内容长度（如：短、中、长等）",
                    required=False,
                ),
            ],
        )
    ] 