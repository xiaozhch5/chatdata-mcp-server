import importlib
import inspect
import sys
import os
import mcp.types as types
from typing import Callable, Dict, List, Optional
from pydantic import FileUrl

# 资源注册表
_REGISTERED_RESOURCES = {}

def _import_all_resource_modules():
    """自动导入resources目录下的所有模块"""
    # 获取resources目录的路径
    resources_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 遍历resources目录中的所有Python文件
    for filename in os.listdir(resources_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # 去掉.py后缀
            module_path = f"resources.{module_name}"
            try:
                importlib.import_module(module_path)
            except ImportError as e:
                print(f"无法导入模块 {module_path}: {e}")

def register_all_resources() -> list[types.Resource]:
    """获取所有注册的resources"""
    # 创建一个字典来存储所有resources
    resources_dict = {}
    
    # 确保所有resource模块都已导入
    _import_all_resource_modules()
    
    # 遍历resources包中的所有模块
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('resources.') and module_name != 'resources.__init__':
            module = sys.modules[module_name]
            
            # 查找模块中的get_resources函数
            if hasattr(module, 'get_resources'):
                resources = module.get_resources()
                # 将每个resource添加到字典中，使用name作为key
                for resource in resources:
                    resources_dict[resource.name] = resource
    
    # 将字典中的resource列表化并返回
    resources_list = list(resources_dict.values())
    return resources_list

def get_resource_by_uri(uri: FileUrl) -> Optional[bytes | str]:
    """根据URI获取资源内容"""
    # 从URI路径中提取资源名称
    path = uri.path.lstrip('/')
    if path.endswith('.txt'):
        name = path[:-4]  # 去掉.txt后缀
    else:
        name = path
    
    # 遍历所有模块查找资源处理函数
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('resources.') and module_name != 'resources.__init__':
            module = sys.modules[module_name]
            
            # 查找模块中的read_resource函数
            if hasattr(module, 'read_resource'):
                try:
                    # 尝试读取资源
                    content = module.read_resource(name)
                    if content is not None:
                        return content
                except:
                    # 如果这个模块不能处理此资源，继续尝试下一个
                    continue
    
    # 如果没有找到资源，抛出异常
    raise ValueError(f"未找到资源: {uri}")

# 在导入时自动导入所有resource模块
_import_all_resource_modules()

__all__ = ["register_all_resources", "get_resource_by_uri"] 