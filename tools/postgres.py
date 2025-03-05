import mcp.types as types
import psycopg2
import psycopg2.extras
from tabulate import tabulate
import json


async def connect_to_database(
    host: str,
    database: str,
    user: str,
    password: str,
    port: int = 5432
):
    """连接到PostgreSQL数据库"""
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        return conn
    except Exception as e:
        raise ConnectionError(f"无法连接到数据库: {str(e)}")


async def get_table_list(conn):
    """获取数据库中的表列表"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name
        """)
        tables = cursor.fetchall()
        cursor.close()
        
        # 格式化结果
        result = "## 数据库表格列表\n\n"
        result += tabulate(
            tables, 
            headers=["Schema", "Table Name"], 
            tablefmt="pipe"
        )
        
        return result
    except Exception as e:
        return f"获取表格列表时出错: {str(e)}"


async def get_table_schema(conn, table_name, schema="public"):
    """获取表结构"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema, table_name))
        columns = cursor.fetchall()
        cursor.close()
        
        if not columns:
            return f"表 {schema}.{table_name} 未找到或没有列。"
        
        # 格式化结果
        result = f"## {schema}.{table_name} 表结构\n\n"
        result += tabulate(
            columns, 
            headers=["列名", "数据类型", "允许空值", "默认值"], 
            tablefmt="pipe"
        )
        
        return result
    except Exception as e:
        return f"获取表结构时出错: {str(e)}"


async def execute_query(conn, query, limit=100):
    """执行SQL查询并返回结果"""
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query)
        
        # 检查是否是SELECT查询
        if cursor.description is not None:
            rows = cursor.fetchmany(limit)
            
            if not rows:
                return "查询执行成功，但没有返回数据。"
            
            # 从DictCursor中获取列名
            headers = [desc[0] for desc in cursor.description]
            
            # 将行转换为列表
            data = [dict(row) for row in rows]
            
            # 格式化结果
            result = f"## 查询结果 (最多显示 {limit} 行)\n\n"
            result += tabulate(
                [list(row.values()) for row in data], 
                headers=headers, 
                tablefmt="pipe"
            )
            
            # 如果有更多行
            if cursor.rowcount > limit:
                result += f"\n\n*注: 共有 {cursor.rowcount} 行，仅显示前 {limit} 行*"
            
            cursor.close()
            return result
        else:
            # 对于非SELECT查询，返回影响的行数
            row_count = cursor.rowcount
            cursor.close()
            conn.commit()
            return f"查询执行成功，影响了 {row_count} 行。"
            
    except Exception as e:
        return f"执行查询时出错: {str(e)}"


async def get_database_info(conn):
    """获取数据库基本信息"""
    try:
        cursor = conn.cursor()
        
        # 获取PostgreSQL版本
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        # 获取数据库大小
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        size = cursor.fetchone()[0]
        
        # 获取表数量
        cursor.execute("""
            SELECT count(*) 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """)
        table_count = cursor.fetchone()[0]
        
        cursor.close()
        
        # 格式化结果
        result = "## 数据库信息\n\n"
        result += f"- **PostgreSQL版本**: {version}\n"
        result += f"- **数据库大小**: {size}\n"
        result += f"- **表格数量**: {table_count}\n"
        
        return result
    except Exception as e:
        return f"获取数据库信息时出错: {str(e)}"


async def postgres_query(
    action: str,
    host: str,
    database: str,
    user: str,
    password: str,
    port: int = 5432,
    table_name: str = None,
    schema: str = "public",
    query: str = None,
    limit: int = 100
) -> list[types.TextContent]:
    """查询PostgreSQL数据库"""
    try:
        print(f"执行PostgreSQL {action}操作")
        
        # 连接数据库
        conn = await connect_to_database(host, database, user, password, port)
        
        # 根据操作类型执行不同的操作
        if action == "table_list":
            result = await get_table_list(conn)
        elif action == "table_schema":
            if not table_name:
                raise ValueError("查询表结构时必须提供table_name参数")
            result = await get_table_schema(conn, table_name, schema)
        elif action == "execute_query":
            if not query:
                raise ValueError("执行查询时必须提供query参数")
            result = await execute_query(conn, query, limit)
        elif action == "database_info":
            result = await get_database_info(conn)
        else:
            raise ValueError(f"不支持的操作类型: {action}")
        
        # 关闭连接
        conn.close()
        
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        error_msg = f"PostgreSQL查询失败: {str(e)}"
        return [types.TextContent(type="text", text=error_msg)]


async def postgres_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "postgres":
        raise ValueError(f"Unknown tool: {name}")
    
    # 检查必需参数
    required_params = ["action", "host", "database", "user", "password"]
    for param in required_params:
        if param not in arguments:
            raise ValueError(f"Missing required argument '{param}'")
    
    # 获取参数
    action = arguments["action"]
    host = arguments["host"]
    database = arguments["database"]
    user = arguments["user"]
    password = arguments["password"]
    port = int(arguments.get("port", 5432))
    table_name = arguments.get("table_name")
    schema = arguments.get("schema", "public")
    query = arguments.get("query")
    limit = int(arguments.get("limit", 100))
    
    # 调用查询函数
    return await postgres_query(
        action, host, database, user, password, port, table_name, schema, query, limit
    )


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="postgres",
            description="查询PostgreSQL数据库信息，执行SQL查询",
            inputSchema={
                "type": "object",
                "required": ["action", "host", "database", "user", "password"],
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "操作类型",
                        "enum": ["table_list", "table_schema", "execute_query", "database_info"],
                    },
                    "host": {
                        "type": "string",
                        "description": "数据库主机地址",
                    },
                    "database": {
                        "type": "string",
                        "description": "数据库名称",
                    },
                    "user": {
                        "type": "string",
                        "description": "数据库用户名",
                    },
                    "password": {
                        "type": "string",
                        "description": "数据库密码",
                    },
                    "port": {
                        "type": "integer",
                        "description": "数据库端口，默认为5432",
                        "default": 5432,
                    },
                    "table_name": {
                        "type": "string",
                        "description": "表名（对于table_schema操作必需）",
                    },
                    "schema": {
                        "type": "string",
                        "description": "模式名称，默认为public",
                        "default": "public",
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL查询语句（对于execute_query操作必需）",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "查询结果最大行数，默认为100",
                        "default": 100,
                    },
                },
            },
        )
    ] 