from financial_assistance.src.utils.call_llm import ge_llm_input, call_llm


def summary_seeking_news(news_dict_list: list):
    summary_result = []
    for i, item in enumerate(news_dict_list):
        cur_input = f"# 当前为第{i}篇新闻报道\n"
        cur_input += f"## {item['title']}\n"
        cur_input += f"## {item['date']}\n"
        cur_input += f"## {item['content']}\n\n"
        messages = [
            {
                'role': 'system',  # 系统角色消息
                'content': '请帮我用中文markdown格式总结归纳当前的新闻主体内容'  # 系统提示内容You are a helpful assistant.
            },
            {
                'role': 'user',  # 用户角色消息
                'content': cur_input  # 用户查询内容
            }
        ]
        result = call_llm(messages)
        summary_result.append({
            "title": item['title'],
            "content": result,
            "date": item['date']
        })
    return summary_result

