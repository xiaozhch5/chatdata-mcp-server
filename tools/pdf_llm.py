import mcp.types as types
import httpx
import tempfile
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import pdfplumber
from typing import List, Optional

# 加载环境变量
load_dotenv()

# 初始化LLM
llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",
    max_completion_tokens=4096,
)

# 定义分析提示模板
PDF_ANALYSIS_PROMPT = """
请分析以下PDF文档内容，并回答以下问题：

1. 文档的主要主题是什么？
2. 文档的关键点有哪些？
3. 文档的结构如何？
4. 文档中是否有重要的数据或统计信息？
5. 文档的结论或建议是什么？

PDF内容：
{content}

请以结构化的方式回答上述问题，并用中文回答。
"""

USER_DEFINED_PROMPT = """
请根据以下提示分析PDF文档内容：

{user_defined_prompt}

PDF内容：
{content}

请以结构化的方式回答，并用中文回答。
"""

async def analyze_pdf(
    pdf_url: str,
    max_pages: Optional[int] = 10,
    analysis_type: str = "summary",
    user_defined_prompt: Optional[str] = None
) -> List[types.TextContent]:
    """
    下载并分析PDF文档
    
    Args:
        pdf_url: PDF文件的URL
        max_pages: 最大分析页数，默认为10页
        analysis_type: 分析类型，可以是"summary"或"detailed"或"user_defined"
        user_defined_prompt: 用户自定义分析提示，当analysis_type为user_defined时必填
    
    Returns:
        分析结果列表
    """
    print(f"开始分析PDF: {pdf_url}")
    
    # 验证URL
    if not pdf_url.startswith(('http://', 'https://')):
        return [types.TextContent(
            type="text",
            text="错误: URL必须以'http://'或'https://'开头"
        )]
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_path = temp_file.name
            
            # 下载PDF文件
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(pdf_url)
                response.raise_for_status()
                temp_file.write(response.content)
        
        # 提取PDF内容
        content = ""
        with pdfplumber.open(temp_path) as pdf:
            # 限制分析的页数
            pages_to_analyze = min(len(pdf.pages), max_pages)
            for i in range(pages_to_analyze):
                page = pdf.pages[i]
                content += f"\n\n--- 第 {i+1} 页 ---\n\n"
                content += page.extract_text() or "无法提取文本内容"
        
        # 清理临时文件
        os.unlink(temp_path)
        
        # 如果内容为空
        if not content.strip():
            return [types.TextContent(
                type="text",
                text="错误: 无法从PDF中提取文本内容"
            )]
        
        # 根据分析类型选择提示模板
        if analysis_type == "detailed":
            prompt = PromptTemplate(
                template=PDF_ANALYSIS_PROMPT,
                input_variables=["content"]
            )
            chain = LLMChain(llm=llm, prompt=prompt)
            result = await chain.arun(content=content)
        elif analysis_type == "user_defined":
            if not user_defined_prompt:
                return [types.TextContent(
                    type="text",
                    text="错误: 用户自定义分析类型需要提供user_defined_prompt参数"
                )]
            prompt = PromptTemplate(
                template=USER_DEFINED_PROMPT,
                input_variables=["user_defined_prompt", "content"]
            )
            chain = LLMChain(llm=llm, prompt=prompt)
            result = await chain.arun(user_defined_prompt=user_defined_prompt, content=content)
        else:  # summary
            prompt = PromptTemplate(
                template="请为以下PDF内容生成一个简洁的摘要，并用中文回答：\n\n{content}",
                input_variables=["content"]
            )
            chain = LLMChain(llm=llm, prompt=prompt)
            result = await chain.arun(content=content)
        
        # 构建输出
        output = f"## PDF分析结果\n\n"
        output += f"**PDF URL**: {pdf_url}\n\n"
        output += f"**分析类型**: {analysis_type}\n\n"
        if analysis_type == "user_defined":
            output += f"**用户提示**: {user_defined_prompt}\n\n"
        output += f"**分析页数**: {pages_to_analyze}\n\n"
        output += "---\n\n"
        output += result
        
        return [types.TextContent(type="text", text=output)]
        
    except httpx.RequestError as e:
        return [types.TextContent(
            type="text",
            text=f"下载PDF时发生错误: {str(e)}"
        )]
    except pdfplumber.PDFSyntaxError:
        return [types.TextContent(
            type="text",
            text="错误: 无效的PDF文件格式"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"分析PDF时发生错误: {str(e)}"
        )]


async def pdf_llm_tool(
    name: str, arguments: dict
) -> List[types.TextContent]:
    if name != "pdf_llm":
        raise ValueError(f"Unknown tool: {name}")
    
    if "pdf_url" not in arguments:
        raise ValueError("Missing required argument 'pdf_url'")
    
    pdf_url = arguments["pdf_url"]
    max_pages = arguments.get("max_pages", 10)
    analysis_type = arguments.get("analysis_type", "summary")
    user_defined_prompt = arguments.get("user_defined_prompt")
    
    return await analyze_pdf(pdf_url, max_pages, analysis_type, user_defined_prompt)


def get_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="pdf_llm",
            description="分析PDF文档内容，支持URL下载和LLM分析",
            inputSchema={
                "type": "object",
                "required": ["pdf_url"],
                "properties": {
                    "pdf_url": {
                        "type": "string",
                        "description": "PDF文件的URL地址",
                    },
                    "max_pages": {
                        "type": "integer",
                        "description": "最大分析页数，默认为10页",
                        "default": 10
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "分析类型：summary(摘要)或detailed(详细分析)或user_defined(用户自定义分析)",
                        "enum": ["summary", "detailed", "user_defined"],
                        "default": "summary"
                    },
                    "user_defined_prompt": {
                        "type": "string",
                        "description": "用户自定义分析提示，当analysis_type为user_defined时必填",
                        "default": None
                    }
                },
            },
        )
    ]
