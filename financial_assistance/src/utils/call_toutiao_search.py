import json
import random
import time
import urllib
from enum import Enum
from urllib import parse

from financial_assistance.src.utils.request.simple_spider import request_page_by_selenium


# 头条搜索方式枚举
class ToutiaoSearchType(Enum):
    WEB = "web"
    FINANCIAL = "financial"
    NEWS = "news"

def search_toutiao_with_selenium(industry, search_type: str="") -> list:
    """
    使用 Selenium 模拟浏览器访问今日头条搜索页，返回页面内容
    """
    print(f"[search_toutiao_with_selenium] 开始执行今日头条搜索（使用Selenium）")
    # 将industry转换为url编码
    industry_url = urllib.parse.quote(industry)
    if search_type == ToutiaoSearchType.FINANCIAL.value:
        payload = f"dvpf=pc&source=input&keyword={industry_url}&page_num=0&pd=information&action_type=search_subtab_switch&search_id=&from=news&cur_tab_title=news"
    elif search_type == ToutiaoSearchType.WEB.value:
        payload = f"dvpf=pc&source=input&keyword={industry_url}&page_num=0&pd=synthesis"
    else:
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
        url = ""
        title = ""
        if "data" in data and "open_url" in data["data"]:
            url = data["data"]["open_url"]
            title = data["data"]["title"]
        elif "url" in data and "title" in data["data"]:
            url = data["data"]["url"]
            if not data["data"]["title"]:
                title = industry
        if url:
            cur_data = data["data"]
            url = cur_data["open_url"]
            print(f"[download_pages] 标题: {title}")
            print(f"[download_pages] URL: {url}")
            # 进行一个3-10s的随机时间sleep
            sleep_time = random.randint(3, 10)
            print(f"[download_pages] 随机等待 {sleep_time} 秒...")
            time.sleep(sleep_time)
            print(f"[download_pages] 开始下载页面内容...")
            result = request_page_by_selenium(url)
            print(f"[download_pages] 正在查找文章内容...")
            contents = result.find_all("div", {"class": "article-content"})
            if len(contents) >= 1:
                print(f"[download_pages] 找到 {len(contents)} 个文章内容块")
                for i, content in enumerate(contents):
                    cur = {
                        "title": title,
                        "content": content.text,
                    }
                    result_dict_list.append(cur)
                print(f"[download_pages] 第 {idx} 条数据处理完成，已提取 {len(contents)} 个内容块")
            else:
                result_dict_list.append({"title": title, "content": result.text})
        else:
            print(f"[download_pages] 警告：第 {idx} 条数据中 open_url 和 url 都不存在，跳过")
    print(f"[download_pages] 所有页面下载完成，共提取 {len(result_dict_list)} 条内容")
    return result_dict_list