import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time

def search_toutiao_once(headers):
    print(f"[search_toutiao_once] 开始执行今日头条搜索")
    payload = "dvpf=pc&source=input&keyword=%E6%96%B0%E8%83%BD%E6%BA%90%E6%B1%BD%E8%BD%A6&page_num=0&pd=synthesis"
    base_url = "https://so.toutiao.com/search?"
    url = base_url + payload
    print(f"[search_toutiao_once] 目标URL: {url}")
    with requests.Session() as session:
        # 发送登录请求
        # login_response = session.post(login_url, data=login_payload, headers=headers)
        # login_response.raise_for_status()

        # 登录后访问目标页面
        print(f"[search_toutiao_once] 正在发送GET请求...")
        response = session.get(url, headers=headers)
        response.raise_for_status()
        print(f"[search_toutiao_once] 请求成功，状态码: {response.status_code}")

        # 解析页面
        print(f"[search_toutiao_once] 正在解析页面内容...")
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"[search_toutiao_once] 页面解析完成")
        return soup



def request_page_by_selenium(url):
    print(f"[request_page_by_selenium] 开始执行，目标URL: {url}")
    print(f"[request_page_by_selenium] 正在初始化Edge浏览器...")
    edge_options = Options()
    # edge_options.add_argument('--headless')
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
    )
    driver = webdriver.Edge(options=edge_options)
    print(f"[request_page_by_selenium] 浏览器初始化完成")

    try:
        print(f"[request_page_by_selenium] 正在访问页面...")
        driver.get(url)
        print(f"[request_page_by_selenium] 等待页面动态加载（2秒）...")
        time.sleep(2)  # 等待页面动态加载内容
        print(f"[request_page_by_selenium] 正在获取页面源码...")
        page_source = driver.page_source
        print(f"[request_page_by_selenium] 正在解析页面内容...")
        soup = BeautifulSoup(page_source, 'html.parser')
        print(f"[request_page_by_selenium] 页面解析完成")
        return soup
    finally:
        print(f"[request_page_by_selenium] 正在关闭浏览器...")
        driver.quit()
        print(f"[request_page_by_selenium] 浏览器已关闭")

