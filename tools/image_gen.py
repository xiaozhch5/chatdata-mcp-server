import mcp.types as types
import httpx
import base64


async def generate_placeholder_image(
    width: int,
    height: int,
    text: str = None,
    background_color: str = None,
    text_color: str = None
) -> list[types.ImageContent]:
    """生成一个占位图像，可以自定义尺寸和文字"""
    # 使用placekitten或placehold.co等服务
    
    # 基础URL
    base_url = "https://placehold.co"
    
    # 添加尺寸
    url = f"{base_url}/{width}x{height}"
    
    # 添加背景颜色（如果提供）
    if background_color:
        # 去掉#号（如果有）
        background_color = background_color.lstrip('#')
        url += f"/{background_color}"
    
    # 添加文本颜色（如果提供） 
    if text_color and background_color:
        # 去掉#号（如果有）
        text_color = text_color.lstrip('#')
        url += f"/{text_color}"
    
    # 添加文本（如果提供）
    if text:
        url += f"?text={text}"
    
    print(f"正在生成图像: {url}")
    
    # 获取图像
    headers = {"User-Agent": "MCP Test Server (github.com/modelcontextprotocol/python-sdk)"}
    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        # 返回图像内容
        image_data = response.content
        
        # 转换为base64编码
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        # 返回图像内容
        return [types.ImageContent(
            type="image",
            data=base64_data,
            mime_type="image/png"
        )]


async def image_gen_tool(
    name: str, arguments: dict
) -> list[types.ImageContent]:
    if name != "image_gen":
        raise ValueError(f"Unknown tool: {name}")
    
    # 检查必需参数
    if "width" not in arguments:
        raise ValueError("Missing required argument 'width'")
    if "height" not in arguments:
        raise ValueError("Missing required argument 'height'")
    
    # 获取参数
    width = int(arguments["width"])
    height = int(arguments["height"])
    text = arguments.get("text")
    background_color = arguments.get("background_color")
    text_color = arguments.get("text_color")
    
    # 调用生成函数
    return await generate_placeholder_image(
        width, height, text, background_color, text_color
    )


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="image_gen",
            description="生成自定义尺寸和内容的占位图像",
            inputSchema={
                "type": "object",
                "required": ["width", "height"],
                "properties": {
                    "width": {
                        "type": "integer",
                        "description": "图像宽度（像素）",
                    },
                    "height": {
                        "type": "integer",
                        "description": "图像高度（像素）",
                    },
                    "text": {
                        "type": "string",
                        "description": "显示在图像上的文字（可选）",
                    },
                    "background_color": {
                        "type": "string",
                        "description": "背景颜色，十六进制值，如'ff0000'表示红色（可选）",
                    },
                    "text_color": {
                        "type": "string",
                        "description": "文字颜色，十六进制值，如'ffffff'表示白色（可选）",
                    }
                },
            },
        )
    ] 