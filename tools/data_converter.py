import mcp.types as types
import json
import xml.dom.minidom
import yaml
import xmltodict


async def convert_data(
    data: str,
    from_format: str,
    to_format: str
) -> list[types.TextContent]:
    """
    将数据从一种格式转换为另一种格式
    支持的格式: json, yaml, xml
    """
    print(f"转换数据，从 {from_format} 到 {to_format}")
    
    # 首先，将输入数据解析为Python对象
    try:
        if from_format.lower() == "json":
            parsed_data = json.loads(data)
        elif from_format.lower() in ["yaml", "yml"]:
            parsed_data = yaml.safe_load(data)
        elif from_format.lower() == "xml":
            parsed_data = xmltodict.parse(data)
        else:
            return [types.TextContent(type="text", text=f"不支持的源格式: {from_format}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"解析 {from_format} 数据失败: {str(e)}")]
    
    # 然后，将Python对象转换为目标格式
    try:
        if to_format.lower() == "json":
            result = json.dumps(parsed_data, indent=2, ensure_ascii=False)
        elif to_format.lower() in ["yaml", "yml"]:
            result = yaml.dump(parsed_data, allow_unicode=True, sort_keys=False)
        elif to_format.lower() == "xml":
            # 将数据转换为XML是比较特殊的
            if from_format.lower() == "xml":
                # 如果已经是XML，则尝试美化
                xml_dom = xml.dom.minidom.parseString(data)
                result = xml_dom.toprettyxml(indent="  ")
            else:
                # 需要一个根元素
                xml_data = {"root": parsed_data}
                result = xmltodict.unparse(xml_data, pretty=True)
        else:
            return [types.TextContent(type="text", text=f"不支持的目标格式: {to_format}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"转换到 {to_format} 格式失败: {str(e)}")]
    
    output = f"## 从 {from_format.upper()} 转换到 {to_format.upper()}\n\n"
    output += "```" + to_format.lower() + "\n"
    output += result
    output += "\n```"
    
    return [types.TextContent(type="text", text=output)]


async def data_converter_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "data_converter":
        raise ValueError(f"Unknown tool: {name}")
    
    if "data" not in arguments:
        raise ValueError("Missing required argument 'data'")
    if "from_format" not in arguments:
        raise ValueError("Missing required argument 'from_format'")
    if "to_format" not in arguments:
        raise ValueError("Missing required argument 'to_format'")
    
    data = arguments["data"]
    from_format = arguments["from_format"]
    to_format = arguments["to_format"]
    
    return await convert_data(data, from_format, to_format)


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="data_converter",
            description="在不同数据格式(JSON、YAML、XML)之间转换数据",
            inputSchema={
                "type": "object",
                "required": ["data", "from_format", "to_format"],
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "要转换的数据字符串",
                    },
                    "from_format": {
                        "type": "string",
                        "description": "源数据格式",
                        "enum": ["json", "yaml", "yml", "xml"],
                    },
                    "to_format": {
                        "type": "string",
                        "description": "目标数据格式",
                        "enum": ["json", "yaml", "yml", "xml"],
                    }
                },
            },
        )
    ] 