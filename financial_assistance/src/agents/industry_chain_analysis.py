import json
import os
import random
import time
import urllib
from urllib import parse
import pandas as pd

from financial_assistance.src.utils.call_llm import call_llm
from financial_assistance.src.utils.request.simple_spider import request_page_by_selenium


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
    result_list = search_toutiao_with_selenium(industry)
    if output_dir:
        with open(os.path.join(output_dir, f"{industry}_request_result.json"), "w") as f:
            json.dump(result_list, f)
    dict_list = download_pages(result_list, industry)
    if output_dir:
        df = pd.DataFrame(dict_list)
        print(f"[download_pages] 已转换为DataFrame，形状: {df.shape}")
        df.to_csv(os.path.join(output_dir, f"{industry}_request_result.csv"), index=False)
    return industry, dict_list


def search_toutiao_with_selenium(industry):
    """
    使用 Selenium 模拟浏览器访问今日头条搜索页，返回页面内容
    """
    print(f"[search_toutiao_with_selenium] 开始执行今日头条搜索（使用Selenium）")
    # 将industry转换为url编码
    industry_url = urllib.parse.quote(industry)
    payload = f"dvpf=pc&source=input&keyword={industry_url}&page_num=0&pd=synthesis"
    base_url = "https://so.toutiao.com/search?"
    url = base_url + payload
    print(f"[search_toutiao_with_selenium] 目标URL: {url}")

    data_list = []

    print(f"[search_toutiao_with_selenium] 正在请求页面...")
    result = request_page_by_selenium(url)
    print(f"[search_toutiao_with_selenium] 正在查找JSON数据脚本标签...")
    result = result.find_all("script", {"data-for": "s-result-json"})
    print(f"[search_toutiao_with_selenium] 找到 {len(result)} 个JSON脚本标签")
    try:
        for i, s in enumerate(result):
            print(f"[search_toutiao_with_selenium] 正在解析第 {i + 1} 个JSON数据...")
            data_list.append(json.loads(s.next))
        print(f"[search_toutiao_with_selenium] 成功解析 {len(data_list)} 条数据")
    except Exception as e:
        print(f"[search_toutiao_with_selenium] 解析JSON时发生错误: {e}")
    print(f"[search_toutiao_with_selenium] 执行完成，返回 {len(data_list)} 条数据")
    return data_list


def download_pages(data_list, industry):
    print(f"[download_pages] 开始下载页面，共 {len(data_list)} 条数据需要处理")
    result_dict_list = []
    for idx, data in enumerate(data_list, 1):
        print(f"[download_pages] 正在处理第 {idx}/{len(data_list)} 条数据...")
        if "data" in data and "open_url" in data["data"]:
            cur_data = data["data"]
            open_url = cur_data["open_url"]
            title = cur_data["title"]
            print(f"[download_pages] 标题: {title}")
            print(f"[download_pages] URL: {open_url}")
            # 进行一个3-10s的随机时间sleep
            sleep_time = random.randint(3, 10)
            print(f"[download_pages] 随机等待 {sleep_time} 秒...")
            time.sleep(sleep_time)
            print(f"[download_pages] 开始下载页面内容...")
            result = request_page_by_selenium(open_url)
            print(f"[download_pages] 正在查找文章内容...")
            contents = result.find_all("div", {"class": "article-content"})
            print(f"[download_pages] 找到 {len(contents)} 个文章内容块")
            for i, content in enumerate(contents):
                cur = {
                    "title": title,
                    "content": content.text,
                }
                result_dict_list.append(cur)
            print(f"[download_pages] 第 {idx} 条数据处理完成，已提取 {len(contents)} 个内容块")
        else:
            print(f"[download_pages] 警告：第 {idx} 条数据中 open_url 不存在，跳过")
    print(f"[download_pages] 所有页面下载完成，共提取 {len(result_dict_list)} 条内容")
    return result_dict_list



