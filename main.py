from text2sql.text_to_sql_agent import agent

for step in agent.stream(
    input = {'messages': [{'role': 'user', 'content': '数据库中一共有多少个用户?'}]},
    stream_mode="values"
):
    step['messages'][-1].pretty_print()