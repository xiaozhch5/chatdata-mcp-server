import mcp.types as types
from mcp.types import Prompt, GetPromptResult
import mcp
from .utils import create_messages


def simple(context: str = None, topic: str = None) -> types.GetPromptResult:
    """一个简单的prompt，可以接受可选的上下文和主题参数"""
    messages = create_messages(context=context, topic=topic)
    
    return GetPromptResult(
        messages=messages,
        description="一个带有可选上下文和主题参数的简单prompt"
    )


def get_prompts() -> list[Prompt]:
    """返回此模块中的所有prompts"""
    return [
        Prompt(
            name="simple",
            description="一个带有可选上下文和主题参数的简单prompt",
            arguments=[
                types.PromptArgument(
                    name="context",
                    description="需要考虑的额外上下文",
                    required=False,
                ),
                types.PromptArgument(
                    name="topic",
                    description="要关注的特定主题",
                    required=False,
                ),
            ],
        )
    ] 