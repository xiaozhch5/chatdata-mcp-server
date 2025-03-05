import mcp.types as types


def create_messages(
    context: str | None = None, topic: str | None = None
) -> list[types.PromptMessage]:
    """创建prompt的消息列表。"""
    messages = []

    # 如果提供了上下文，则添加
    if context:
        messages.append(
            types.UserMessage(f"Here is some relevant context: {context}")
        )

    # 添加主要提示
    prompt = "请帮我解答"
    if topic:
        prompt += f"以下主题: {topic}"
    else:
        prompt += "我可能有的任何问题。"

    messages.append(
        types.UserMessage(prompt)
    )

    return messages 