import mcp.types as types
import httpx
import json
import re
from urllib.parse import urlparse
import base64


async def send_http_request(
    url: str,
    method: str = "GET",
    headers: dict = None,
    params: dict = None,
    data: str = None,
    json_data: dict = None,
    timeout: int = 30,
    follow_redirects: bool = True
) -> list[types.TextContent]:
    """
    发送HTTP请求并获取响应
    支持GET、POST、PUT、DELETE等方法
    可以自定义请求头、URL参数、请求体等
    """
    print(f"发送HTTP请求: {method} {url}")
    
    # 验证URL格式
    if not url.startswith(('http://', 'https://')):
        return [types.TextContent(
            type="text", 
            text="错误: URL必须以'http://'或'https://'开头"
        )]
    
    # 验证HTTP方法
    valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    if method.upper() not in valid_methods:
        return [types.TextContent(
            type="text", 
            text=f"错误: 不支持的HTTP方法 '{method}'. 支持的方法: {', '.join(valid_methods)}"
        )]
    
    # 设置默认请求头
    default_headers = {
        "User-Agent": "MCP-HttpClient/1.0",
        "Accept": "*/*"
    }
    
    # 合并用户提供的请求头
    if headers:
        # 将所有键转换为字符串
        headers = {str(k): str(v) for k, v in headers.items()}
        default_headers.update(headers)
    
    try:
        # 准备请求参数
        request_kwargs = {
            "method": method.upper(),
            "url": url,
            "headers": default_headers,
            "timeout": float(timeout),
            "follow_redirects": follow_redirects
        }
        
        # 添加查询参数
        if params:
            request_kwargs["params"] = params
        
        # 添加请求体
        if json_data:
            request_kwargs["json"] = json_data
        elif data:
            request_kwargs["content"] = data
        
        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.request(**request_kwargs)
            
            # 获取响应信息
            status_code = response.status_code
            response_headers = dict(response.headers)
            response_url = str(response.url)  # 最终URL（考虑重定向）
            
            # 尝试检测响应内容类型
            content_type = response_headers.get("Content-Type", "")
            content_length = int(response_headers.get("Content-Length", 0))
            
            # 获取响应体，但限制大小
            max_size = 10240  # 最大响应大小为10KB
            response_body = ""
            
            if content_length > max_size:
                response_truncated = True
                response_body = response.text[:max_size]
            else:
                response_truncated = False
                response_body = response.text
            
            # 检测是否为JSON并美化
            is_json = False
            json_body = None
            if "application/json" in content_type or response_body.strip().startswith(("{", "[")):
                try:
                    json_body = json.loads(response_body)
                    response_body = json.dumps(json_body, ensure_ascii=False, indent=2)
                    is_json = True
                except:
                    pass
            
            # 检测是否为图片等二进制数据
            is_binary = False
            if "image/" in content_type or "application/octet-stream" in content_type:
                is_binary = True
                try:
                    # 将二进制内容转换为Base64字符串表示
                    if len(response.content) <= max_size:
                        b64_content = base64.b64encode(response.content).decode('utf-8')
                        if "image/" in content_type:
                            img_type = content_type.split("/")[1].split(";")[0]
                            response_body = f"<图片数据: {len(response.content)} 字节>"
                    else:
                        response_body = f"<二进制数据太大: {len(response.content)} 字节>"
                except:
                    response_body = "<无法解析的二进制数据>"
            
            # 构建响应报告
            output = f"## HTTP请求结果\n\n"
            
            # 请求信息
            output += f"### 请求信息\n\n"
            output += f"**方法**: {method.upper()}\n\n"
            output += f"**URL**: {url}\n\n"
            
            if params:
                output += f"**查询参数**:\n```json\n{json.dumps(params, ensure_ascii=False, indent=2)}\n```\n\n"
            
            if headers:
                # 过滤掉敏感头部信息
                safe_headers = {k: v for k, v in headers.items() 
                               if not any(s in k.lower() for s in ["auth", "key", "token", "secret", "pass"])}
                if safe_headers:
                    output += f"**请求头**:\n```json\n{json.dumps(safe_headers, ensure_ascii=False, indent=2)}\n```\n\n"
            
            if json_data:
                output += f"**请求体(JSON)**:\n```json\n{json.dumps(json_data, ensure_ascii=False, indent=2)}\n```\n\n"
            elif data:
                if len(data) > 1000:
                    output += f"**请求体**: <{len(data)} 字节数据>\n\n"
                else:
                    output += f"**请求体**:\n```\n{data}\n```\n\n"
            
            # 响应信息
            output += f"### 响应信息\n\n"
            output += f"**状态码**: {status_code} {httpx.StatusCode(status_code).phrase}\n\n"
            
            if response_url != url:
                output += f"**最终URL**: {response_url}\n\n"
            
            # 过滤响应头中的敏感信息
            safe_resp_headers = {k: v for k, v in response_headers.items() 
                               if not any(s in k.lower() for s in ["auth", "key", "token", "secret", "pass"])}
            
            output += f"**响应头**:\n```json\n{json.dumps(dict(safe_resp_headers), ensure_ascii=False, indent=2)}\n```\n\n"
            
            # 响应体
            output += f"### 响应体\n\n"
            
            if is_binary:
                output += f"<二进制数据: {content_type}, {len(response.content)} 字节>\n\n"
            elif is_json:
                output += f"```json\n{response_body}\n```\n\n"
            else:
                if response_truncated:
                    output += f"```\n{response_body}...\n```\n\n<响应已截断，完整大小: {content_length} 字节>\n\n"
                else:
                    output += f"```\n{response_body}\n```\n\n"
            
            return [types.TextContent(type="text", text=output)]
            
    except httpx.TimeoutException:
        return [types.TextContent(
            type="text", 
            text=f"错误: 请求超时 (>{timeout}秒)"
        )]
    except httpx.RequestError as e:
        return [types.TextContent(
            type="text", 
            text=f"请求错误: {str(e)}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text", 
            text=f"发生错误: {str(e)}"
        )]


async def http_client_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "http_client":
        raise ValueError(f"Unknown tool: {name}")
    
    if "url" not in arguments:
        raise ValueError("Missing required argument 'url'")
    
    url = arguments["url"]
    method = arguments.get("method", "GET")
    headers = arguments.get("headers", None)
    params = arguments.get("params", None)
    data = arguments.get("data", None)
    json_data = arguments.get("json_data", None)
    timeout = arguments.get("timeout", 30)
    follow_redirects = arguments.get("follow_redirects", True)
    
    return await send_http_request(
        url=url,
        method=method,
        headers=headers,
        params=params,
        data=data,
        json_data=json_data,
        timeout=timeout,
        follow_redirects=follow_redirects
    )


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="http_client",
            description="发送HTTP请求并获取响应，支持多种HTTP方法和参数设置",
            inputSchema={
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "请求的URL地址",
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP请求方法",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                        "default": "GET"
                    },
                    "headers": {
                        "type": "object",
                        "description": "请求头，键值对形式",
                    },
                    "params": {
                        "type": "object",
                        "description": "URL查询参数，键值对形式",
                    },
                    "data": {
                        "type": "string",
                        "description": "请求体数据，字符串形式",
                    },
                    "json_data": {
                        "type": "object",
                        "description": "JSON格式的请求体数据，会被自动序列化",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "请求超时时间（秒）",
                        "default": 30
                    },
                    "follow_redirects": {
                        "type": "boolean",
                        "description": "是否自动跟随重定向",
                        "default": True
                    }
                },
            },
        )
    ] 