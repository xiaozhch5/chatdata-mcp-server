import mcp.types as types
import httpx
import json


async def translate_text(
    text: str,
    target_lang: str,
    source_lang: str = "auto"
) -> list[types.TextContent]:
    """
    翻译文本到目标语言
    使用免费的翻译API
    """
    print(f"翻译文本，目标语言: {target_lang}, 源语言: {source_lang}")
    
    # 这里使用 LibreTranslate API，也可以替换为其他翻译服务
    # 如果需要使用其他服务，请替换以下URL和参数
    url = "https://libretranslate.de/translate"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=10.0)
            response.raise_for_status()
            
            result = response.json()
            translated_text = result.get("translatedText", "")
            
            if not translated_text:
                return [types.TextContent(type="text", text=f"翻译失败: {result.get('error', '未知错误')}")]
            
            output = f"原文 [{source_lang}]: {text}\n\n"
            output += f"译文 [{target_lang}]: {translated_text}"
            
            return [types.TextContent(type="text", text=output)]
            
    except Exception as e:
        fallback_output = f"翻译服务不可用，错误: {str(e)}\n\n"
        fallback_output += "提示: 这是一个演示工具，依赖于免费的公共API，可能受到限制。"
        return [types.TextContent(type="text", text=fallback_output)]


async def get_supported_languages() -> list[dict]:
    """获取支持的语言列表"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://libretranslate.de/languages")
            response.raise_for_status()
            
            languages = response.json()
            return languages
    except Exception as e:
        print(f"获取语言列表失败: {e}")
        # 返回一些常用语言作为备用
        return [
            {"code": "en", "name": "English"},
            {"code": "zh", "name": "Chinese"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "ru", "name": "Russian"},
            {"code": "es", "name": "Spanish"}
        ]


async def translator_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "translator":
        raise ValueError(f"Unknown tool: {name}")
    
    if "text" not in arguments:
        raise ValueError("Missing required argument 'text'")
    if "target_lang" not in arguments:
        raise ValueError("Missing required argument 'target_lang'")
    
    text = arguments["text"]
    target_lang = arguments["target_lang"]
    source_lang = arguments.get("source_lang", "auto")
    
    return await translate_text(text, target_lang, source_lang)


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="translator",
            description="将文本从一种语言翻译成另一种语言",
            inputSchema={
                "type": "object",
                "required": ["text", "target_lang"],
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "需要翻译的文本",
                    },
                    "target_lang": {
                        "type": "string",
                        "description": "目标语言代码，如'en'(英语), 'zh'(中文), 'fr'(法语), 'de'(德语), 'ja'(日语)等",
                    },
                    "source_lang": {
                        "type": "string",
                        "description": "源语言代码，默认为'auto'自动检测",
                        "default": "auto"
                    }
                },
            },
        )
    ] 