import mcp.types as types
import httpx
import json
import socket
import re


async def get_ip_info(
    ip_address: str = None
) -> list[types.TextContent]:
    """
    获取IP地址的详细信息
    如果不提供IP地址，则获取本机的公网IP信息
    """
    print(f"获取IP信息: {ip_address if ip_address else '当前IP'}")
    
    # 如果未提供IP地址，则获取当前公网IP
    if not ip_address:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.ipify.org?format=json")
                response.raise_for_status()
                ip_address = response.json()["ip"]
                print(f"获取到当前公网IP: {ip_address}")
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"获取当前IP地址失败: {str(e)}"
            )]
    
    # 验证IP地址格式
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ip_pattern, ip_address):
        return [types.TextContent(
            type="text",
            text=f"无效的IP地址格式: {ip_address}"
        )]
    
    try:
        # 尝试使用ip-api.com免费API获取IP信息
        api_url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,regionName,city,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "fail":
                return [types.TextContent(
                    type="text",
                    text=f"查询IP信息失败: {data.get('message', '未知错误')}"
                )]
            
            # 尝试进行域名反向解析
            hostname = "未知"
            try:
                hostname = socket.gethostbyaddr(ip_address)[0]
            except:
                pass
            
            # 构建输出
            output = f"## IP地址信息\n\n"
            output += f"**IP地址**: {data['query']}\n\n"
            
            if hostname != "未知":
                output += f"**主机名**: {hostname}\n\n"
            
            # 地理位置信息
            location_info = f"{data.get('city', '未知')}, {data.get('regionName', '未知')}, {data.get('country', '未知')}"
            output += f"**地理位置**: {location_info}\n\n"
            output += f"**经纬度**: {data.get('lat', '未知')}, {data.get('lon', '未知')}\n\n"
            output += f"**时区**: {data.get('timezone', '未知')}\n\n"
            
            # 网络信息
            output += f"**ISP**: {data.get('isp', '未知')}\n\n"
            output += f"**组织**: {data.get('org', '未知')}\n\n"
            output += f"**AS**: {data.get('as', '未知')}\n\n"
            
            # 其他信息
            output += f"**移动网络**: {'是' if data.get('mobile', False) else '否'}\n\n"
            output += f"**代理**: {'是' if data.get('proxy', False) else '否'}\n\n"
            output += f"**数据中心/主机服务**: {'是' if data.get('hosting', False) else '否'}\n\n"
            
            # 添加地图链接
            if 'lat' in data and 'lon' in data:
                map_url = f"https://www.openstreetmap.org/?mlat={data['lat']}&mlon={data['lon']}&zoom=12"
                output += f"**查看地图**: [OpenStreetMap]({map_url})\n\n"
            
            return [types.TextContent(type="text", text=output)]
            
    except httpx.RequestError as e:
        return [types.TextContent(
            type="text",
            text=f"请求错误: {str(e)}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"获取IP信息时发生错误: {str(e)}"
        )]


async def ip_info_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "ip_info":
        raise ValueError(f"Unknown tool: {name}")
    
    ip_address = arguments.get("ip_address", None)
    
    return await get_ip_info(ip_address)


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="ip_info",
            description="获取IP地址的详细信息，包括地理位置、ISP等",
            inputSchema={
                "type": "object",
                "properties": {
                    "ip_address": {
                        "type": "string",
                        "description": "要查询的IP地址，如不提供则获取当前IP信息",
                    },
                },
            },
        )
    ] 