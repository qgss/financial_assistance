from multiprocessing import Pool
from pathlib import Path

import pandas as pd

from financial_assistance.src.utils.call_llm import call_llm
from financial_assistance.src.utils.load_config import CURRENT_PROJECT
from financial_assistance.src.utils.safe_load_json import safe_load_json_from_str


def summary_development_direction(industry: str, industry_chain_info: str = "") -> str:
    """
    结合当前技术能力，分析重点发展方向
    
    参数:
        industry: 待分析的行业名称（字符串）
        industry_chain_info: 产业链分析信息（可选字符串，默认为空）
    
    返回:
        str: LLM返回的重点发展方向分析结果
    """
    # 构建用户查询内容
    user_content = f"请结合当前技术能力，分析{industry}行业接下来需要重点发展突破的方向"
    # 如果提供了产业链信息，则添加到查询中
    if industry_chain_info:
        user_content += f"\n\n相关产业链信息：\n{industry_chain_info}"
    
    # 构建消息列表
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': """You are a helpful assistant that can help me analyze development directions.
你需要结合当前技术能力和行业现状，分析指定行业接下来需要重点发展突破的方向。
输出格式为结构化的文本，不限于技术已发展/存在年限、技术突破点、发展方向、关键挑战等内容。"""  # 系统提示内容
        },
        {
            'role': 'user',  # 用户角色消息
            'content': user_content  # 用户查询内容
        }
    ]
    
    # 调用LLM并返回响应
    return call_llm(messages)


def summary_one_industry_chain(industry: str, industry_chains: list):
    # 准备模型输入
    industry_chain_info = ""
    for i, industry_chain in enumerate(industry_chains):
        if len(industry_chain_info) > CURRENT_PROJECT["max_token"]:
            break
        title = industry_chain['title']
        content = industry_chain['content']
        industry_chain_info += f"# 当前第{i}篇信息：\n{title}\n{content}\n"
    result = summary_development_direction(industry, industry_chain_info)
    return result
