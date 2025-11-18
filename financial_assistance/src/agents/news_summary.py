import datetime
import os

import pandas as pd

from financial_assistance.src.utils.call_llm import call_llm
from financial_assistance.src.utils.call_seeking_alpha_source import get_seeking_alpha_news, download_seeking_pages
from financial_assistance.src.utils.load_config import PROJECT_ROOT_DIR
from financial_assistance.src.utils.safe_load_json import safe_load_json_from_str


def summary_seeking_news(output_dir="", keyword=""):
    if not keyword:
        keyword = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    news = get_seeking_alpha_news(output_dir=output_dir, keyword=keyword)
    news_dict_list = download_seeking_pages(news, output_dir=output_dir, keyword=keyword)
    summary_result = []
    for i, item in enumerate(news_dict_list):
        cur_input = f"# 当前为第{i}篇新闻报道\n"
        cur_input += f"## {item['title']}\n"
        cur_input += f"## {item['date']}\n"
        cur_input += f"## {item['content']}\n\n"
        result = call_news_summary_llm(cur_input)
        classify_result = classify_news_summary_llm(result)
        summary_result.append({
            "title": item['title'],
            "content": item['content'],
            "date": item['date'],
            "url": item['url'],
            "llm_suumary": result,
            "classify": ",".join(classify_result),
        })
        print(f"已完成第{i}篇报道的总结。")
    if output_dir:
        file_path = os.path.join(output_dir, f"seeking_alpha_new_summary_{keyword}.csv")
        df = pd.DataFrame(summary_result)
        df.to_csv(file_path, index=False)
    return summary_result


def call_news_summary_llm(cur_input):
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': """请帮我用中文markdown格式总结归纳当前的新闻主体内容"""
        },
        {
            'role': 'user',  # 用户角色消息
            'content': cur_input  # 用户查询内容
        }
    ]
    result = call_llm(messages)
    return result


def classify_news_summary_llm(cur_input):
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': """帮我对新闻进行一个简单的分类，请找出最符合的类别，数量小于等于四个，具体分类如下：
    1. **时政新闻**：报道国家和地区的重大政策、决策、领导人讲话、重要会议等。
    2. **国际新闻**：报道国家与国家之间或和其他地区发生的重大事件、政治动态、国际关系变化等。
    3. **社会新闻**：涵盖社会各层面的新闻，如教育、文化、医疗、体育、娱乐等。
    4. **财经新闻**：报道经济数据、市场动态、公司财报、商业策略、投资理财等。
    5. **科技新闻**：报道最新的科学技术进展、科技成果、科技政策等。
    6. **健康与医学新闻**：报道疾病预防、治疗方法、健康生活方式等内容。
    7. **环境新闻**：报道气候变化、环境保护、生态建设等方面的信息。
    8. **法律新闻**：报道重大案件审理、法律政策变动、司法改革等。
    9. **体育新闻**：报道各类体育赛事、运动员表现、体育政策等。
    10. **娱乐新闻**：报道电影、音乐、戏剧、明星动态等娱乐行业信息。
    11. **地方新闻**：报道特定地区内的新闻事件和社会动态。
    
    请注意输出格式：不要输出除json内容之外的其他字符
    输出格式：json
    字段：classify
    内容：list
    实例：{"classify": ["classify_1", "classify_2", "classify_3"]}"""
        },
        {
            'role': 'user',  # 用户角色消息
            'content': cur_input  # 用户查询内容
        }
    ]
    result = call_llm(messages)
    result = safe_load_json_from_str(result).get("classify", [])
    return result

if __name__ == '__main__':
    output_dir = os.path.join(PROJECT_ROOT_DIR, 'financial_assistance', 'res', 'news_summary')
    os.makedirs(output_dir, exist_ok=True)
    keyword = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_result = summary_seeking_news(output_dir, keyword)

