import httpx
import mcp.types as types
import json


async def get_weather(
    city: str,
) -> list[types.TextContent]:
    """获取指定城市的天气信息"""
    # 这里使用的是一个免费的天气API，实际应用中可能需要注册获取API密钥
    url = f"https://wttr.in/{city}?format=j1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        print(f"获取天气数据: {city}")
        response = await client.get(url)
        response.raise_for_status()
        
        try:
            weather_data = response.json()
            # 提取一些基本信息
            current = weather_data.get("current_condition", [{}])[0]
            print(current)
            temp_c = current.get("temp_C", "未知")
            humidity = current.get("humidity", "未知")
            weather_desc = current.get("weatherDesc", [{}])[0].get("value", "未知")
            # 日期
            date = current.get("localObsDateTime", "未知")
            
            result = f"城市: {city}\n"
            result += f"天气: {weather_desc}\n"
            result += f"温度: {temp_c}°C\n"
            result += f"湿度: {humidity}%"
            result += f"日期: {date}\n"

            print(result)
            
            return [types.TextContent(type="text", text=result)]
        except (json.JSONDecodeError, KeyError) as e:
            return [types.TextContent(type="text", text=f"获取天气信息失败: {str(e)}")]


async def weather_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "weather":
        raise ValueError(f"Unknown tool: {name}")
    if "city" not in arguments:
        raise ValueError("Missing required argument 'city'")
    return await get_weather(arguments["city"])


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="weather",
            description="获取指定城市的天气信息",
            inputSchema={
                "type": "object",
                "required": ["city"],
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如'Beijing'、'Shanghai'等",
                    }
                },
            },
        )
    ] 