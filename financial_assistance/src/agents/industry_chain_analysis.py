import json
import os
import random
import time
import pandas as pd

from financial_assistance.src.utils.call_llm import call_llm
from financial_assistance.src.utils.call_toutiao_search import search_toutiao_with_selenium, ToutiaoSearchType, \
    download_pages


def analyze_industry_chain(industry: str) -> str:
    """
    分析相关产业链
    
    参数:
        industry: 待分析的行业名称（字符串）
    
    返回:
        str: LLM返回的产业链分析结果
    """
    # 构建消息列表
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': """You are a helpful assistant that can help me analyze industry chains.
你需要分析指定行业的相关产业链，包括上游、中游、下游各个环节，以及各个环节的关键企业和技术要点。
输出格式为结构化的文本，清晰展示产业链的各个环节。"""  # 系统提示内容
        },
        {
            'role': 'user',  # 用户角色消息
            'content': f"请分析{industry}行业的相关产业链，包括上游、中游、下游各个环节"  # 用户查询内容
        }
    ]
    
    # 调用LLM并返回响应
    return call_llm(messages)

def search_industry_info_tool(industry: str, output_dir="") -> tuple:
    """
    使用request 或其他互联网搜索工具搜索行业信息

    参数:
        industry: 待搜索的行业名称（字符串）

    返回:
        str: LLM返回的行业信息
    """
    time.sleep(random.randint(1,20))
    result_list = search_toutiao_with_selenium(industry, search_type=ToutiaoSearchType.FINANCIAL.value)
    if output_dir:
        with open(os.path.join(output_dir, f"{industry}_request_result.json"), "w") as f:
            json.dump(result_list, f)
    dict_list = download_pages(result_list, industry)
    if output_dir:
        df = pd.DataFrame(dict_list)
        print(f"[download_pages] 已转换为DataFrame，形状: {df.shape}")
        df.to_csv(os.path.join(output_dir, f"{industry}_request_result.csv"), index=False)
    return industry, dict_list


if __name__ == '__main__':
    r = search_industry_info_tool("华为技术有限公司股票代码")
    print(r)