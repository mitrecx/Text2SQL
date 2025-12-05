from langchain.tools import BaseTool
from text2sql.utils.db_utils import PostgresDatabaseManager
from text2sql.utils.log_utils import log
from pydantic import Field, create_model
from typing import Optional



class ListTablesTool(BaseTool):
    name: str = "list_tables"
    description: str = "列出数据库中的所有表名及描述信息. 当需要查询数据库中的所有表时, 请使用此工具."

    db_manager: PostgresDatabaseManager
    
    def _run(self) -> str:
        try:
            tables_info = self.db_manager.get_tables_with_comments()
            result = f"数据库中共有{len(tables_info)}张表, 分别是:\n"
            for i, table in enumerate(tables_info):
                table_name = table.get("table_name")
                comment = table.get("table_comment") or "无描述"
                result += f"{i+1}. 表名:{table_name}\n   描述:{comment}\n"
            return result
        except Exception as e:
            log.exception(e)
            raise ValueError(f"列出数据库中的所有表名及描述信息失败: {e}")

    async def _arun(self) -> str:
        return self._run()
    
    
class TableSchemaTool(BaseTool):
    name: str = "table_schema"
    description: str = "获取数据库中指定表的结构信息. 当需要查询数据库中表的字段名、数据类型、是否主键等信息时, 请使用此工具. 输入参数为表名, 多个表名之间用逗号分隔."

    db_manager: PostgresDatabaseManager
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.args_schema = create_model(
            "TableSchemaToolArgs",
            table_names=(str, Field(..., description="表名, 多个表名之间用逗号分隔")),
        )
    
    def _run(self, table_names: Optional[str] = None) -> str:
        """返回表的结构信息, 包括字段名、数据类型、是否主键等"""
        try:
            table_list = None
            if table_names:
                table_list = [name.strip() for name in table_names.split(",") if name.strip()]
            else:
                table_list = self.db_manager.get_table_names()
            schema_info = self.db_manager.get_table_schema(table_list)
            return schema_info if schema_info else "指定的表不存在"
        except Exception as e:
            log.exception(e)
            raise ValueError(f"获取数据库中指定表的结构信息失败: {e}")

    async def _arun(self, table_names: Optional[str] = None) -> str:
        return self._run(table_names)
    
    
class SQLQueryTool(BaseTool):
    name: str = "sql_query"
    description: str = "执行SQL查询语句. 当需要根据数据库中的数据进行查询时, 请使用此工具. 输入参数为SQL查询语句."

    db_manager: PostgresDatabaseManager
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.args_schema = create_model(
            "SQLQueryToolArgs",
            query=(str, Field(..., description="SQL查询语句")),
        )
    
    def _run(self, query: Optional[str] = None) -> str:
        """执行SQL查询语句"""
        try:
            if not query:
                raise ValueError("SQL查询语句不能为空")
            result = self.db_manager.execute_query(query)
            return result if result else "查询结果为空"
        except Exception as e:
            log.exception(e)
            raise ValueError(f"执行SQL查询语句失败: {e}")

    async def _arun(self, query: Optional[str] = None) -> str:
        return self._run(query)
    
    
class SQLQueryCheckerTool(BaseTool):
    name: str = "sql_query_checker"
    description: str = "检查SQL查询语句是否符合语法规范. 当需要检查SQL查询语句是否正确时, 请使用此工具. 输入参数为SQL查询语句."

    db_manager: PostgresDatabaseManager
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.args_schema = create_model(
            "SQLQueryCheckerToolArgs",
            query=(str, Field(..., description="SQL查询语句")),
        )
    
    def _run(self, query: Optional[str] = None) -> str:
        """检查SQL查询语句是否符合语法规范"""
        try:
            if not query:
                raise ValueError("SQL查询语句不能为空")
            result = self.db_manager.check_query_syntax(query)
            return result if result else "查询语句符合语法规范"
        except Exception as e:
            log.exception(e)
            raise ValueError(f"检查SQL查询语句是否符合语法规范失败: {e}")

    async def _arun(self, query: Optional[str] = None) -> str:
        return self._run(query)
    
if __name__ == "__main__":
    DB_CONFIG={
        "host": "localhost",
        "port": 5432,
        "database": "shop_db",
        "user": "xxx",
        "password": "xxx",
    }
    db_manager = PostgresDatabaseManager(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    # tool = ListTablesTool(db_manager=db_manager)
    # print(tool.invoke({}))
    
    # tool = TableSchemaTool(db_manager=db_manager)
    # print(tool.invoke({"table_names": "orders, role"}))
    
    # tool = SQLQueryTool(db_manager=db_manager)
    # print(tool.invoke({"query": "SELECT * FROM orders"}))
    
    tool = SQLQueryCheckerTool(db_manager=db_manager)
    print(tool.invoke({"query": "SELECT count(1) FROM orders"}))
