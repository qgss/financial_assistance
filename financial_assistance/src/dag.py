import os
from multiprocessing import Pool

from financial_assistance.src.agents.development_direction import summary_one_industry_chain
from financial_assistance.src.agents.industry_analysis import analysis_keywords
from financial_assistance.src.agents.industry_chain_analysis import search_industry_info_tool


def analyze_one_industry_chain(industry: str, output_dir=""):
    search_industry_info_tool(industry, output_dir)
    return ""

def analysis_industry(idea):
    root_dir = os.path.dirname(__file__)
    output_dir = os.path.join(root_dir, "..", "res")

    industries_keywords = analysis_keywords(idea)
    str_keywords = ", ".join(industries_keywords)
    print(f"根据输入的idea，得到了以下搜索关键字: {str_keywords}")
    inputs = [(keyword, output_dir) for keyword in industries_keywords]
    with Pool(processes=4) as pool:
        search_results = pool.starmap(analyze_one_industry_chain, inputs)

    with Pool(processes=4) as pool:
        summary_results = pool.starmap(summary_one_industry_chain, search_results)

    for title, summary in summary_results:
        print(title)
        print(summary)
        print()

if __name__ == '__main__':
    analysis_industry("请帮我分析一下 新能源汽车 的相关产业信息")
