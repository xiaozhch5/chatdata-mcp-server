import mcp.types as types
from mcp.types import Prompt
import mcp


def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


def get_prompts() -> list[Prompt]:
    """返回此模块中的所有prompts"""
    return [
        Prompt(
            name="review_code",
            description="审查代码并提供反馈",
            func=review_code,
            arguments=[
                types.PromptArgument(
                    name="code",
                    description="需要审查的代码",
                    required=True,
                ),
            ],
        )
    ] 