from langchain.tools import BaseTool
from text2sql.utils.db_utils import PostgresDatabaseManager
from text2sql.tools.text_to_sql_tools import ListTablesTool, TableSchemaTool,SQLQueryTool, SQLQueryCheckerTool
from typing import List
from langchain_openai import ChatOpenAI
import os
from langchain.agents import create_agent


def get_tools(host: str, port: int, db_name: str, user: str, password: str) -> List[BaseTool]:
    """获取所有可用的工具."""
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    db_manager = PostgresDatabaseManager(connection_string)
    return [
        ListTablesTool(db_manager=db_manager),
        TableSchemaTool(db_manager=db_manager),
        SQLQueryTool(db_manager=db_manager),
        SQLQueryCheckerTool(db_manager=db_manager)
    ]

tools = get_tools(
    host="localhost",
    port=5432,
    db_name="shop_db",
    user="xxx",
    password="xxx"
)

system_prompt = """
你是一个专业的postgreSQL查询助手。

目标：根据用户的自然语言问题，使用提供的工具了解数据库结构，生成正确的SQL并调用工具执行，最终用中文自然语言总结结果。

你的工作步骤:
1. 先使用 list_tables 工具列出数据库中的所有表名及描述信息。
2. 根据用户的问题，使用 table_schema 工具获取相关表的结构信息。
3. 基于用户的问题和表结构，生成对应的SQL查询语句。
4. 使用 sql_query_checker 工具验证生成的SQL是否安全。
5. 若SQL没有报错，执行查询并返回结果。若报错，尝试修正SQL。
6. 调用 sql_query 工具执行SQL查询。
7. 根据查询结果，用中文自然语言总结答案。

你可以使用的工具：
  - list_tables：列出数据库中的所有表名及描述信息。
  - table_schema：获取数据库中指定表的结构信息。
  - sql_query：根据用户的自然语言问题，生成对应的SQL查询语句。
  - sql_query_checker：验证SQL查询是否安全。
  
原则：先探索schema（表名、字段），再编写并执行SQL。若执行错误，尝试纠正。
除非用户明确指定要获取的记录数，否则默认获取10条记录。
绝对不要对数据库进行任何写操作（INSERT、UPDATE、DELETE）以及任何会改变数据库结构的操作（如CREATE、ALTER、DROP）。
"""


llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
    temperature=0.1
)

agent = create_agent(
    llm,
    tools=tools,
    system_prompt=system_prompt
)

# 手动测试
# for step in agent.stream(
#     input = {'messages': [{'role': 'user', 'content': '数据库中一共有多少个用户?'}]},
#     stream_mode="values"
# ):
#     step['messages'][-1].pretty_print()

# langgraph 测试, 在终端运行: 
# langgraph dev --port 8000 --allow-blocking 


# 测试问题:
# 数据库中一共有多少个用户?
# 管理员用户有哪些?
# 一共有多少未付款的订单? 列出所有未付款订单的订单号
