import importlib
import inspect
import sys
import os
import mcp.types as types

# 工具注册表
_REGISTERED_TOOLS = {}

def _import_all_tool_modules():
    """自动导入tools目录下的所有模块"""
    # 获取tools目录的路径
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 遍历tools目录中的所有Python文件
    for filename in os.listdir(tools_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # 去掉.py后缀
            module_path = f"tools.{module_name}"
            try:
                importlib.import_module(module_path)
            except ImportError as e:
                print(f"无法导入模块 {module_path}: {e}")

def register_all_tools():
    """获取所有注册工具的统一接口"""
    tools_list = []
    
    # 确保所有工具模块都已导入
    _import_all_tool_modules()
    print("Imported all tool modules")
    
    # 遍历tools包中的所有模块
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('tools.') and module_name != 'tools.__init__':
            module = sys.modules[module_name]
            
            # 查找模块中的get_tools函数
            if hasattr(module, 'get_tools'):
                tools_list.extend(module.get_tools())
    print(f"Found {len(tools_list)} tools")
    return tools_list

async def call_tool(name, arguments):
    """统一的工具调用接口"""
    # 确保所有工具模块都已导入
    _import_all_tool_modules()
    
    # 遍历tools包中的所有模块
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('tools.') and module_name != 'tools.__init__':
            module = sys.modules[module_name]
            
            # 查找模块中的工具函数
            for obj_name, obj in inspect.getmembers(module):
                if obj_name.endswith('_tool') and inspect.iscoroutinefunction(obj):
                    try:
                        # 尝试调用工具函数
                        return await obj(name, arguments)
                    except ValueError:
                        # 如果工具不匹配，继续查找下一个
                        continue
    
    # 没有找到匹配的工具
    raise ValueError(f"Unknown tool: {name}")

# 在导入时自动导入所有工具模块
_import_all_tool_modules()

__all__ = ["register_all_tools", "call_tool"] 