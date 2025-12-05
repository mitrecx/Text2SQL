# Text2SQL (LangChain 1.x, PostgreSQL)

一个基于 LangChain 1.x 的 Text2SQL Agent, 支持通过自然语言查询 PostgreSQL 数据库中的数据。

## 前提条件:
- 已安装 PostgreSQL 数据库
- 已创建数据库用户并授予查询权限
- 已安装 Python 3.11 或以上版本
- 已安装必要的 Python 库（见 `requirements.txt`）

## 测试数据:
- 数据库名称: `shop_db`
- 表结构: `test_tables_ddl.sql`
- 测试数据: `test_tables_dml.sql`
- 数据库用户: `xxx`
- 数据库密码: `xxx`

## 手动运行:
```python
python main.py
```
结果: 
```text
================================ Human Message =================================

数据库中一共有多少个用户?
================================== Ai Message ==================================

我来帮您查询数据库中一共有多少个用户。首先，我需要了解数据库中有哪些表。
Tool Calls:
  list_tables (call_00_0VvycL5MhME4wxsfikbKeGzZ)
 Call ID: call_00_0VvycL5MhME4wxsfikbKeGzZ
  Args:
================================= Tool Message =================================
Name: list_tables

数据库中共有4张表, 分别是:
1. 表名:orders
   描述:订单表, 存储用户下单信息
2. 表名:role
   描述:角色表, 存储系统中的角色定义
3. 表名:user_account
   描述:用户表, 存储系统用户的基础信息
4. 表名:user_role
   描述:用户与角色关联关系表, 多对多关系

================================== Ai Message ==================================

我看到有一个`user_account`表，这应该是存储用户信息的表。让我查看一下这个表的结构：
Tool Calls:
  table_schema (call_00_HuPuRzxy1FRcWjKFxaXuP2iO)
 Call ID: call_00_HuPuRzxy1FRcWjKFxaXuP2iO
  Args:
    table_names: user_account
================================= Tool Message =================================
Name: table_schema

表名: user_account
列信息:
    id BIGINT (主键) -- [注释:]  用户主键ID
    username VARCHAR(50)  -- [注释:]  登录用户名, 全局唯一
    password VARCHAR(255)  -- [注释:]  用户登录密码(加密存储)
    email VARCHAR(100)  -- [注释:]  用户邮箱
    phone VARCHAR(20)  -- [注释:]  用户手机号
    status SMALLINT  -- [注释:]  用户状态: 1-正常, 0-禁用
    created_at TIMESTAMP  -- [注释:]  创建时间
    updated_at TIMESTAMP  -- [注释:]  更新时间
索引:
    索引: user_account_username_key (username)(唯一索引)

================================== Ai Message ==================================

现在我需要查询用户总数。让我先生成SQL查询语句并检查：
Tool Calls:
  sql_query_checker (call_00_gusnJCRNCS7Hlwf33WQgjgem)
 Call ID: call_00_gusnJCRNCS7Hlwf33WQgjgem
  Args:
    query: SELECT COUNT(*) as total_users FROM user_account
================================= Tool Message =================================
Name: sql_query_checker

SQL语句可以正常执行
================================== Ai Message ==================================

现在执行查询：
Tool Calls:
  sql_query (call_00_e91DxqU5XIzanb0RUvtjdWdK)
 Call ID: call_00_e91DxqU5XIzanb0RUvtjdWdK
  Args:
    query: SELECT COUNT(*) as total_users FROM user_account
================================= Tool Message =================================
Name: sql_query

[
  {
    "total_users": 4
  }
]
================================== Ai Message ==================================

根据查询结果，数据库中一共有 **4个用户**。
```

## 本地 langgraph 运行:
```python
langgraph dev --port 8000 --allow-blocking 
```