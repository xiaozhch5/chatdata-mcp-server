import mcp.types as types
from langchain_openai import ChatOpenAI
from browser_use import Agent, BrowserConfig, Browser
from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatOpenAI(base_url=os.getenv("OPENAI_BASE_URL"),
                 api_key=os.getenv("OPENAI_API_KEY"),
                 model="gpt-4o")

config = BrowserConfig(
    headless=True,
    disable_security=True
)

browser = Browser(config=config)

async def run_agent(
    message: str,
) -> list[types.TextContent]:
    """返回执行结果"""
    agent = Agent(
        browser=browser,
        task=message,
        llm=llm,
    )
    result = await agent.run()
    return [types.TextContent(type="text", text=result.final_result())]


async def browser_use_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "browser_use":
        raise ValueError(f"Unknown tool: {name}")
    if "message" not in arguments:
        raise ValueError("Missing required argument 'message'")
    return await run_agent(arguments["message"])


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="browser_use",
            description="使用browser_use工具，根据用户输入的指令，返回执行结果",
            inputSchema={
                "type": "object",
                "required": ["message"],
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "用户输入的指令",
                    }
                },
            },
        )
    ]