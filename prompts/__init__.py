import importlib
import inspect
import sys
import os
import mcp.types as types
from typing import Callable, Dict, List, Optional

# Prompt注册表
_REGISTERED_PROMPTS = {}

def _import_all_prompt_modules():
    """自动导入prompts目录下的所有模块"""
    # 获取prompts目录的路径
    prompts_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 遍历prompts目录中的所有Python文件
    for filename in os.listdir(prompts_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # 去掉.py后缀
            module_path = f"prompts.{module_name}"
            try:
                importlib.import_module(module_path)
            except ImportError as e:
                print(f"无法导入模块 {module_path}: {e}")

def register_all_prompts():
    """获取所有注册的prompts"""
    prompts_list = []
    
    # 确保所有prompt模块都已导入
    _import_all_prompt_modules()
    
    # 遍历prompts包中的所有模块
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('prompts.') and module_name != 'prompts.__init__':
            module = sys.modules[module_name]
            
            # 查找模块中的get_prompts函数
            if hasattr(module, 'get_prompts'):
                prompts_list.extend(module.get_prompts())
    
    return prompts_list

def get_prompt_by_name(name: str) -> Optional[types.Prompt]:
    """根据名称获取特定的prompt"""
    # 获取所有prompts
    all_prompts = register_all_prompts()
    
    # 查找匹配名称的prompt
    for prompt in all_prompts:
        if prompt.name == name:
            return prompt
    
    return None

async def execute_prompt(name: str, arguments: dict = None) -> types.GetPromptResult:
    """执行指定名称的prompt"""
    if arguments is None:
        arguments = {}
    
    # 获取prompt对象
    prompt = get_prompt_by_name(name)
    if prompt is None:
        raise ValueError(f"未找到名为 '{name}' 的prompt")
    
    # 调用prompt函数
    try:
        result = prompt.func(**arguments)
        
        # 如果结果已经是一个GetPromptResult，直接返回
        if isinstance(result, types.GetPromptResult):
            return result
        
        # 否则，根据返回类型构建GetPromptResult
        if isinstance(result, list) and all(isinstance(msg, types.Message) for msg in result):
            # 结果是消息列表
            return types.GetPromptResult(
                messages=result,
                description=prompt.description
            )
        else:
            # 结果是字符串或其他格式
            return types.GetPromptResult(
                messages=[types.AssistantMessage(result)],
                description=prompt.description
            )
    except Exception as e:
        raise ValueError(f"执行prompt '{name}' 时出错: {str(e)}")

# 在导入时自动导入所有prompt模块
_import_all_prompt_modules()

__all__ = ["register_all_prompts", "get_prompt_by_name", "execute_prompt"] 