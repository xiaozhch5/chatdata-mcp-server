import mcp.types as types
import math
import numpy as np
import sympy


async def calculate_expression(
    expression: str,
    mode: str = "basic"
) -> list[types.TextContent]:
    """
    计算数学表达式
    支持基础计算、科学计算和符号计算
    """
    print(f"计算表达式: '{expression}', 模式: {mode}")
    
    result = ""
    explanation = ""
    
    try:
        # 基础模式: 使用Python内置的eval
        if mode == "basic":
            # 创建安全的环境，只允许使用基本数学函数
            safe_globals = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "pow": pow,
                "math": math
            }
            
            # 计算结果
            numeric_result = eval(expression, {"__builtins__": {}}, safe_globals)
            result = f"{numeric_result}"
            explanation = "使用Python基础计算引擎"
        
        # 科学计算模式: 使用NumPy
        elif mode == "scientific":
            # 替换一些常用函数名
            expression = expression.replace("^", "**")
            
            # 创建NumPy环境
            np_globals = {
                "np": np,
                "sin": np.sin,
                "cos": np.cos,
                "tan": np.tan,
                "exp": np.exp,
                "log": np.log,
                "log10": np.log10,
                "sqrt": np.sqrt,
                "pi": np.pi,
                "e": np.e
            }
            
            # 计算结果
            numeric_result = eval(expression, {"__builtins__": {}}, np_globals)
            
            # 如果结果是数组，转换为列表
            if isinstance(numeric_result, np.ndarray):
                result = str(numeric_result.tolist())
            else:
                result = f"{numeric_result}"
                
            explanation = "使用NumPy科学计算引擎"
        
        # 符号计算模式: 使用SymPy
        elif mode == "symbolic":
            # 使用SymPy进行符号运算
            symbolic_result = sympy.sympify(expression)
            
            # 尝试计算结果
            result = str(symbolic_result)
            
            # 如果可以求值，也给出数值结果
            try:
                numeric_result = float(symbolic_result.evalf())
                result += f"\n数值结果: {numeric_result}"
            except:
                pass
                
            explanation = "使用SymPy符号计算引擎"
            
            # 如果表达式包含导数或积分，尝试计算
            if "diff" in expression or "integrate" in expression:
                explanation += "\n注意: 此表达式包含高级运算，建议直接使用SymPy语法"
                
        else:
            return [types.TextContent(type="text", text=f"不支持的计算模式: {mode}")]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"计算错误: {str(e)}\n\n请检查表达式语法是否正确。")]
    
    # 构建输出
    output = f"## 计算结果\n\n"
    output += f"表达式: `{expression}`\n\n"
    output += f"结果: **{result}**\n\n"
    output += f"计算模式: {mode} ({explanation})"
    
    return [types.TextContent(type="text", text=output)]


async def calculator_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "calculator":
        raise ValueError(f"Unknown tool: {name}")
    
    if "expression" not in arguments:
        raise ValueError("Missing required argument 'expression'")
    
    expression = arguments["expression"]
    mode = arguments.get("mode", "basic")
    
    return await calculate_expression(expression, mode)


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="calculator",
            description="计算数学表达式，支持基础、科学和符号计算",
            inputSchema={
                "type": "object",
                "required": ["expression"],
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，例如 '2+2' 或 'sin(pi/4)'",
                    },
                    "mode": {
                        "type": "string",
                        "description": "计算模式: basic(基础), scientific(科学), symbolic(符号)",
                        "enum": ["basic", "scientific", "symbolic"],
                        "default": "basic"
                    }
                },
            },
        )
    ] 