import anyio
import click
import mcp.types as types
from mcp.server import Server
from pydantic import FileUrl

# 导入工具模块
from tools import call_tool, register_all_tools
# 导入prompt模块
from prompts import register_all_prompts, execute_prompt
# 导入resource模块
from resources import register_all_resources, get_resource_by_uri


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("mcp-website-fetcher")

    @app.call_tool()
    async def call_tool_handler(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        return await call_tool(name, arguments)

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return register_all_tools()

    # 注册所有prompts
    @app.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        prompts = register_all_prompts()
        # 为每个prompt添加key属性（如果mcp.types.Prompt允许额外字段）
        for prompt in prompts:
            setattr(prompt, "key", prompt.name)
        return prompts
    
    # 处理获取prompt
    @app.get_prompt()
    async def get_prompt(
        name: str, arguments: dict[str, str] | None = None
    ) -> types.GetPromptResult:
        try:
            return await execute_prompt(name, arguments)
        except ValueError as e:
            raise ValueError(f"处理prompt请求失败: {str(e)}")
    
    # 注册资源相关的处理函数
    @app.list_resources()
    async def list_resources() -> list[types.Resource]:
        """列出所有可用的资源"""
        return register_all_resources()
    
    @app.read_resource()
    async def read_resource(uri: FileUrl) -> str | bytes:
        """读取指定URI的资源内容"""
        try:
            return get_resource_by_uri(uri)
        except ValueError as e:
            raise ValueError(f"读取资源失败: {str(e)}")

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                return await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0


if __name__ == "__main__":
    main()