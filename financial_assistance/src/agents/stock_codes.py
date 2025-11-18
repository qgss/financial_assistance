import json
import os
import random
import time

import pandas as pd

from financial_assistance.src.utils.call_llm import call_llm
from financial_assistance.src.utils.call_toutiao_search import search_toutiao_with_selenium, ToutiaoSearchType, \
    download_pages
from financial_assistance.src.utils.load_config import CURRENT_PROJECT
from financial_assistance.src.utils.safe_load_json import safe_load_json_from_str


def find_stock_codes(companies: list, companies_chain_info:str="") -> list:
    """
    找出相关股票代码
    
    参数:
        companies: 公司名称列表或相关信息（字符串）
    
    返回:
        str: LLM返回的股票代码列表和分析结果
    """
    # 构建消息列表
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': """You are a helpful assistant that can help me find stock codes for companies.
你需要根据提供的公司名称，找出对应的股票代码（包括A股、港股、美股等）。
输出格式为JSON格式，包含公司名称、股票代码、交易所、股票简称等信息。
注意，有些公司是可能没有上市的，请不要列举没有上市的公司股票代码，可以输出为空，或将信息中的其他公司股票信息进行提取。
例如：
```json
{
    "company_stocks": [{"company": "公司名称", "stock_code": "股票代码", "exchange": "交易所", "stock_name": "股票简称"},...]
}
```"""  # 系统提示内容
        },
        {
            'role': 'user',  # 用户角色消息
            'content': f"请找出以下公司对应的股票代码：\n{companies}\n{companies_chain_info}"  # 用户查询内容
        }
    ]
    
    # 调用LLM并返回响应
    llm_result = call_llm(messages)
    stock_codes = safe_load_json_from_str(llm_result).get("company_stocks", [])
    return stock_codes

def search_stock_info_tool(industry: str, output_dir="") -> tuple:
    """
    使用request 或其他互联网搜索工具搜索企业股票信息

    参数:
        industry: 待搜索的行业名称（字符串）

    返回:
        str: LLM返回的行业信息
    """
    time.sleep(random.randint(1,20))
    result_list = search_toutiao_with_selenium(f"{industry}的股票代码", search_type=ToutiaoSearchType.WEB.value)
    if output_dir:
        with open(os.path.join(output_dir, f"{industry}_stock_request_result.json"), "w") as f:
            json.dump(result_list, f)
    dict_list = download_pages(result_list, industry)
    if output_dir:
        df = pd.DataFrame(dict_list)
        print(f"[download_pages] 已转换为DataFrame，形状: {df.shape}")
        df.to_csv(os.path.join(output_dir, f"{industry}_stock_request_result.csv"), index=False)
    return industry, dict_list

def find_stock_codes_chain(companies: list, companies_chain_info:str="", output_dir:str="") -> list:
    if not companies_chain_info:
        companies_chain_info = "有关公司/企业的股票信息\n"
        for company in companies:
            industry, dict_list = search_stock_info_tool(company, output_dir=output_dir)
            cur_company = f"当前企业{company}的查询报告\n"
            for stock_code in dict_list:
                cur_company += f"{stock_code['title']}: \n{stock_code['content']}\n\n"
            if len(companies_chain_info) + len(cur_company) < CURRENT_PROJECT["max_token"]:
                companies_chain_info += cur_company
    result_list = find_stock_codes(companies, companies_chain_info)
    return result_list


if __name__ == "__main__":
    print(find_stock_codes_chain(["比亚迪、宁德时代、特斯拉"]))

