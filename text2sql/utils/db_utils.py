from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.sql import text
from typing import List, Optional
import json
from pathlib import Path
from .log_utils import log

class PostgresDatabaseManager:
    """Postgres Database Manager, 负责数据库连接和基本操作"""
    def __init__(self, connection_string: str):
        """
        初始化数据库连接
        
        Args:
            connection_string (str): 数据库连接字符串，格式为：
                "postgresql://username:password@host:port/database_name"
        """
        self.engine = create_engine(connection_string, pool_size=5, pool_recycle=3600)
        
        
    def get_table_names(self) -> list[str]:
        """获取数据库中所有表的名称"""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            log.exception(f"获取表名失败: {e}")
            raise ValueError(f"获取表名失败: {e}")
        
    def get_tables_with_comments(self) -> List[dict]:
        """
        获取数据库中所有表的名称和描述信息
        
        Returns:
            List[dict]: 每个元素是一个字典，包含表名和描述信息，例如：
                [{"table_name": "table1", "table_comment": "这是表1"}, {"table_name": "table2", "table_comment": "这是表2"}]
        """
        try:
            query = text("""
            SELECT
                t.tablename as table_name,
                obj_description(c.oid, 'pg_class') as table_comment
            FROM
                pg_catalog.pg_tables t
            JOIN
                pg_catalog.pg_class c ON t.tablename = c.relname
            WHERE
                t.schemaname = 'public' 
            ORDER BY
                t.tablename;
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query)
                return [{"table_name": row[0], "table_comment": row[1]} for row in result]
        except Exception as e:
            log.exception(f"获取表注释失败: {e}")
            raise ValueError(f"获取表注释失败: {e}")
        
    def get_table_schema(self, table_names: Optional[List[str]] = None) -> str:
        """
        获取数据库中指定表的模式信息(包含字段注释)
        
        Args:
            table_names (Optional[List[str]]): 要获取模式的表名列表。如果为None，则获取所有表的模式
        
        Returns:
            str: 包含所有表模式的SQL语句
        """
        try:
            inspector = inspect(self.engine)
            schema_info = []
            tables_to_process = table_names if table_names else self.get_table_names()
            
            for table_name in tables_to_process:
                columns = inspector.get_columns(table_name)
                # 主键和外键
                pk_constraints = inspector.get_pk_constraint(table_name)
                primary_keys = pk_constraints["constrained_columns"] if pk_constraints else []
                foreign_keys = inspector.get_foreign_keys(table_name)
                # 索引
                indexes = inspector.get_indexes(table_name)
                
                # 构建模式信息
                table_schema = f"表名: {table_name}\n"
                table_schema += "列信息:\n"
                for col in columns:
                    pk_indicator = "(主键)" if col["name"] in primary_keys else ""
                    comment = col.get("comment", "无注释")
                    table_schema += f"    {col['name']} {col['type']} {pk_indicator} -- [注释:]  {comment}\n"
                    
                if foreign_keys:
                    table_schema += "外键约束:\n"
                    for fk in foreign_keys:
                        table_schema += f"    外键: {fk['constrained_columns']} -> {fk['referred_table']}({fk['referred_columns']})\n"
                
                if indexes:
                    table_schema += "索引:\n"
                    for idx in indexes:
                        table_schema += f"    索引: {idx['name']} ({', '.join(idx['column_names'])}){'(唯一索引)' if idx['unique'] else ''}\n"
                
                schema_info.append(table_schema)
            
            return "\n\n".join(schema_info)
        except Exception as e:
            log.exception(f"获取表模式失败: {e}")
            raise ValueError(f"获取表模式失败: {e}")
        
    def execute_query(self, query: str) -> str:
        """
        执行SQL查询并返回结果
        
        Args:
            query (str): 要执行的SQL查询语句
        
        Returns:
            str: 查询结果的字符串表示
        """
        # 禁止包含危险操作关键字
        forbidden_keywords = ["drop", "delete", "truncate", "create", "alter", "insert", "update", "grant"]
        query_lower = query.lower().strip()
        
        if not query_lower.startswith(("select", "with")) and any(keyword in query_lower for keyword in forbidden_keywords):
            raise ValueError("查询包含危险操作关键字，已被拒绝")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                
                # 获取列
                columns = result.keys()
                # 获取数据
                rows = result.fetchmany(100)
                if not rows:
                    return "查询结果为空"
                
                # 构建结果字符串
                result_data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        try:
                            # 检查是否可序列化: 尝试将非None值转换为JSON字符串
                            if row[i] is not None:
                                json.dumps(row[i])
                            row_dict[col] = row[i]
                        except Exception as e:
                            row_dict[col] = str(row[i])
                    result_data.append(row_dict)
                return json.dumps(result_data, ensure_ascii=False, indent=2)
                
        except Exception as e:
            log.exception(f"查询执行失败: {e}")
            raise ValueError(f"查询执行失败: {e}")
        
    def check_query_syntax(self, query: str) -> str:
        """
        验证SQL查询是否安全
        
        Args:
            query (str): 要验证的SQL查询语句
        
        Returns:
            str: 验证结果，"错误"或"SQL语句可以正常执行"
        """
        if not query or not query.strip():
            return "错误: 查询不能为空"
        query_lower = query.lower().strip()
        if not query_lower.startswith(("select", "with")):
            return "错误: SQL语句必须以SELECT或WITH开头, 不支持其他操作"
        # 解析查询语句是否正确
        try: 
            with self.engine.begin() as conn:
                # 不执行, 只验证执行计划
                conn.execute(text(f"EXPLAIN {query_lower}"))
            return "SQL语句可以正常执行"
        except Exception as e:
            return f"错误: SQL查询解析失败 - {e}"
        
        
def load_db_config(config_path: Optional[str] = None) -> dict:
    p = Path(config_path) if config_path else (Path(__file__).resolve().parent.parent / "config.json")
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("db", data)


def build_connection_string(cfg: dict) -> str:
    return f"postgresql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"


if __name__ == "__main__":
    cfg = load_db_config()
    db_manager = PostgresDatabaseManager(build_connection_string(cfg))
    print(db_manager.get_table_names())
    print(db_manager.get_tables_with_comments())
    print(db_manager.get_table_schema(['orders']))
    # print(db_manager.get_table_schema())
    # print(db_manager.check_query_syntax("SELECT * FROM orders"))
    # print(db_manager.execute_query("SELECT * FROM orders"))
