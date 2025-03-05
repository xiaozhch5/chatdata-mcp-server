import mcp.types as types
import httpx
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse


async def scrape_webpage(
    url: str,
    selector: str = None,
    extract_type: str = "text"
) -> list[types.TextContent]:
    """
    从网页中抓取内容
    支持抓取全部内容或通过CSS选择器抓取特定内容
    可以提取文本、HTML或链接
    """
    print(f"抓取网页: {url}, 选择器: {selector}, 提取类型: {extract_type}")
    
    # 验证URL
    if not url.startswith(('http://', 'https://')):
        return [types.TextContent(
            type="text", 
            text="错误: URL必须以'http://'或'https://'开头"
        )]
    
    try:
        # 设置请求头，模拟浏览器行为
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        
        # 发送HTTP请求
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()  # 如果请求失败，抛出异常
            
            # 获取网页内容
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 获取网页标题
            title = soup.title.string if soup.title else "无标题"
            
            # 根据提供的选择器提取内容
            if selector:
                elements = soup.select(selector)
                if not elements:
                    return [types.TextContent(
                        type="text", 
                        text=f"错误: 未找到匹配选择器 '{selector}' 的元素"
                    )]
            else:
                # 如果没有选择器，处理整个body
                elements = [soup.body] if soup.body else [soup]
            
            # 根据提取类型获取内容
            result = ""
            
            if extract_type == "text":
                # 提取纯文本
                for element in elements:
                    # 移除script和style内容
                    for script in element.find_all(["script", "style"]):
                        script.decompose()
                    text = element.get_text(separator="\n").strip()
                    # 删除多余空行
                    text = re.sub(r'\n\s*\n', '\n\n', text)
                    result += text + "\n\n"
                
            elif extract_type == "html":
                # 提取HTML代码
                for element in elements:
                    result += str(element) + "\n"
                
            elif extract_type == "links":
                # 提取链接
                links = []
                base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))
                
                for element in elements:
                    for link in element.find_all('a', href=True):
                        href = link['href']
                        # 处理相对URL
                        if href.startswith('/'):
                            full_url = base_url + href
                        elif not href.startswith(('http://', 'https://')):
                            full_url = url.rstrip('/') + '/' + href.lstrip('/')
                        else:
                            full_url = href
                        
                        link_text = link.get_text().strip()
                        if link_text and full_url not in links:
                            links.append(f"[{link_text}]({full_url})")
                
                result = "\n".join(links)
            
            else:
                return [types.TextContent(
                    type="text", 
                    text=f"错误: 不支持的提取类型 '{extract_type}'"
                )]
            
            # 如果结果太长，进行截断
            if len(result) > 7000:
                result = result[:7000] + "...\n\n[内容已截断，因为超过了最大长度限制]"
            
            # 构建输出
            output = f"## 网页抓取结果\n\n"
            output += f"URL: {url}\n\n"
            output += f"标题: {title}\n\n"
            
            if selector:
                output += f"选择器: `{selector}`\n\n"
                
            output += f"提取类型: {extract_type}\n\n"
            output += "---\n\n"
            output += result
            
            return [types.TextContent(type="text", text=output)]
            
    except httpx.RequestError as e:
        return [types.TextContent(
            type="text", 
            text=f"请求错误: {str(e)}"
        )]
    except httpx.HTTPStatusError as e:
        return [types.TextContent(
            type="text", 
            text=f"HTTP错误: {e.response.status_code} {e.response.reason_phrase}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text", 
            text=f"发生错误: {str(e)}"
        )]


async def web_scraper_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "web_scraper":
        raise ValueError(f"Unknown tool: {name}")
    
    if "url" not in arguments:
        raise ValueError("Missing required argument 'url'")
    
    url = arguments["url"]
    selector = arguments.get("selector", None)
    extract_type = arguments.get("extract_type", "text")
    
    return await scrape_webpage(url, selector, extract_type)


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="web_scraper",
            description="从网页中抓取内容，支持抓取全部或特定元素",
            inputSchema={
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要抓取的网页URL",
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS选择器，用于选择特定元素，例如'div.content'或'#main'",
                    },
                    "extract_type": {
                        "type": "string",
                        "description": "要提取的内容类型: text(文本), html(HTML代码), links(链接)",
                        "enum": ["text", "html", "links"],
                        "default": "text"
                    }
                },
            },
        )
    ] 