from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time
import json
import os
from datetime import datetime, timedelta
import re

from financial_assistance.src.utils.load_config import PROJECT_ROOT_DIR


def cookie_manager(url, manual_cookie: str = None):
    """
    管理cookie文件，支持自动登录保存或手动保存cookie
    
    参数:
        url (str): 需要访问的网站URL
        manual_cookie (str, optional): 手动提供的cookie字符串，格式为 "key1=value1; key2=value2"
    
    返回:
        str: cookie文件路径
    """
    url_key = extract_base_url_from_url(url)
    if url_key is None:
        print("当前url找不到key")
    output_dir = os.path.join(PROJECT_ROOT_DIR, 'financial_assistance', 'res', 'cookies')
    cookie_file_path = os.path.join(output_dir, f"{url_key}.json")
    
    # 如果提供了手动cookie，直接保存
    if manual_cookie:
        print(f"[cookie_manager] 检测到手动cookie，正在保存...")
        save_manual_cookie(url, cookie_file_path, manual_cookie)
        return cookie_file_path
    if os.path.exists(cookie_file_path) and is_cookie_valid(cookie_file_path):
        return cookie_file_path
    return None
    #
    # # 如果没有提供手动cookie，检查现有cookie是否有效
    # if not os.path.exists(cookie_file_path) or not is_cookie_valid(cookie_file_path):
    #     save_cookies_after_login(url, cookie_file_path, wait_time=30)
    # return cookie_file_path


def save_manual_cookie(url, cookie_file_path, cookie_string: str):
    """
    手动保存cookie字符串到文件
    
    参数:
        url (str): 需要访问的网站URL
        cookie_file_path (str): cookie保存的文件路径
        cookie_string (str): cookie字符串，格式为 "key1=value1; key2=value2"
    
    返回:
        bool: 保存成功返回True，失败返回False
    """
    print(f"[save_manual_cookie] 开始执行，目标URL: {url}")
    print(f"[save_manual_cookie] Cookie将保存到: {cookie_file_path}")
    
    try:
        # 从URL中提取域名
        url_key = extract_base_url_from_url(url)
        if url_key is None:
            # 如果提取失败，尝试从URL中提取域名
            match = re.match(r'^[^:]+://([^/]+)', url)
            if match:
                url_key = match.group(1)
            else:
                print(f"[save_manual_cookie] 无法从URL中提取域名")
                url_key = "unknown"
        
        # 解析cookie字符串，格式为 "key1=value1; key2=value2"
        cookies = []
        cookie_pairs = cookie_string.split(';')
        
        for pair in cookie_pairs:
            pair = pair.strip()  # 去除前后空格
            if not pair:
                continue
            
            # 分割键值对
            if '=' in pair:
                key, value = pair.split('=', 1)  # 只分割第一个等号
                key = key.strip()
                value = value.strip()
                
                # 构建Selenium格式的cookie字典
                cookie_dict = {
                    'name': key,
                    'value': value,
                    'domain': url_key,  # 使用提取的域名
                    'path': '/',  # 默认路径
                }
                cookies.append(cookie_dict)
            else:
                print(f"[save_manual_cookie] 警告：跳过无效的cookie项: {pair}")
        
        if not cookies:
            print(f"[save_manual_cookie] 错误：未解析到任何有效的cookie")
            return False
        
        # 准备保存的数据结构
        cookie_data = {
            'url': url,  # 保存原始URL
            'cookies': cookies,  # 保存cookies列表
            'save_time': datetime.now().isoformat(),  # 保存时间
            'expires_at': None  # 过期时间，初始为None
        }
        
        # 由于手动提供的cookie字符串通常不包含过期时间，默认设置为7天后过期
        cookie_data['expires_at'] = (datetime.now() + timedelta(days=7)).isoformat()
        print(f"[save_manual_cookie] Cookie过期时间设置为: {cookie_data['expires_at']} (默认7天后)")
        
        # 确保目录存在
        cookie_dir = os.path.dirname(cookie_file_path)
        if cookie_dir and not os.path.exists(cookie_dir):
            os.makedirs(cookie_dir, exist_ok=True)
        
        # 保存cookies到文件
        print(f"[save_manual_cookie] 正在保存cookies到文件...")
        with open(cookie_file_path, 'w', encoding='utf-8') as f:
            json.dump(cookie_data, f, ensure_ascii=False, indent=2)
        
        print(f"[save_manual_cookie] Cookies已成功保存到: {cookie_file_path}")
        print(f"[save_manual_cookie] 共保存 {len(cookies)} 个cookies")
        return True
        
    except Exception as e:
        print(f"[save_manual_cookie] 发生错误: {str(e)}")
        return False


def extract_base_url_from_url(url: str) -> str:
    """
    从类似 abcd://xxxx/abcd 的字符串中提取 xxxx
    abcd 和 xxxx 可以是任意字符，:// 和 / 为关键字
    """
    match = re.match(r'^[^:]+://([^/]+)/[^/]+', url)
    if match:
        return match.group(1)
    return None


def get_edge_options(headless=False):
    """
    获取Edge浏览器的配置选项
    
    参数:
        headless (bool): 是否使用无头模式，默认为False
    
    返回:
        Options: Edge浏览器配置选项对象
    """
    edge_options = Options()
    if headless:
        edge_options.add_argument('--headless')  # 无头模式
    edge_options.add_argument('--disable-gpu')  # 禁用GPU加速
    edge_options.add_argument('--no-sandbox')  # 禁用沙箱模式
    edge_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
    )  # 设置用户代理
    return edge_options


def save_cookies_after_login(url, cookie_file_path, wait_time=30):
    """
    手动登录网站并保存cookie到本地文件
    
    参数:
        url (str): 需要登录的网站URL
        cookie_file_path (str): cookie保存的文件路径
        wait_time (int): 等待手动登录的时间（秒），默认30秒
    
    返回:
        bool: 保存成功返回True，失败返回False
    """
    print(f"[save_cookies_after_login] 开始执行，目标URL: {url}")
    print(f"[save_cookies_after_login] Cookie将保存到: {cookie_file_path}")
    print(f"[save_cookies_after_login] 正在初始化Edge浏览器（非无头模式，方便手动登录）...")
    
    # 使用非无头模式，方便用户手动登录
    edge_options = get_edge_options(headless=False)
    driver = webdriver.Edge(options=edge_options)
    print(f"[save_cookies_after_login] 浏览器初始化完成")
    
    try:
        print(f"[save_cookies_after_login] 正在访问登录页面...")
        driver.get(url)  # 访问登录页面
        print(f"[save_cookies_after_login] 请在浏览器中完成登录操作...")
        print(f"[save_cookies_after_login] 等待 {wait_time} 秒，请在此期间完成登录...")
        
        # 等待用户手动登录
        time.sleep(wait_time)
        
        print(f"[save_cookies_after_login] 正在获取cookies...")
        cookies = driver.get_cookies()  # 获取所有cookies
        
        if not cookies:
            print(f"[save_cookies_after_login] 警告：未获取到任何cookies，可能登录失败")
            return False
        
        # 准备保存的数据结构
        cookie_data = {
            'url': url,  # 保存原始URL
            'cookies': cookies,  # 保存cookies列表
            'save_time': datetime.now().isoformat(),  # 保存时间
            'expires_at': None  # 过期时间，初始为None
        }
        
        # 检查cookies中的过期时间，取最早过期的cookie时间
        expires_times = []
        for cookie in cookies:
            if 'expiry' in cookie:  # 如果cookie有过期时间
                expires_times.append(cookie['expiry'])
        
        if expires_times:
            # 找到最早的过期时间
            earliest_expiry = min(expires_times)
            # 转换为datetime对象
            expires_datetime = datetime.fromtimestamp(earliest_expiry)
            cookie_data['expires_at'] = expires_datetime.isoformat()
            print(f"[save_cookies_after_login] Cookie过期时间: {expires_datetime}")
        else:
            print(f"[save_cookies_after_login] 警告：未找到cookie过期时间，将使用默认过期时间（7天后）")
            # 如果没有过期时间，默认7天后过期
            cookie_data['expires_at'] = (datetime.now() + timedelta(days=7)).isoformat()
        
        # 确保目录存在
        cookie_dir = os.path.dirname(cookie_file_path)
        if cookie_dir and not os.path.exists(cookie_dir):
            os.makedirs(cookie_dir, exist_ok=True)
        
        # 保存cookies到文件
        print(f"[save_cookies_after_login] 正在保存cookies到文件...")
        with open(cookie_file_path, 'w', encoding='utf-8') as f:
            json.dump(cookie_data, f, ensure_ascii=False, indent=2)
        
        print(f"[save_cookies_after_login] Cookies已成功保存到: {cookie_file_path}")
        print(f"[save_cookies_after_login] 共保存 {len(cookies)} 个cookies")
        return True
        
    except Exception as e:
        print(f"[save_cookies_after_login] 发生错误: {str(e)}")
        return False
    finally:
        print(f"[save_cookies_after_login] 正在关闭浏览器...")
        driver.quit()
        print(f"[save_cookies_after_login] 浏览器已关闭")


def is_cookie_valid(cookie_file_path):
    """
    检查cookie文件是否存在且未过期
    
    参数:
        cookie_file_path (str): cookie文件路径
    
    返回:
        bool: cookie有效返回True，无效或过期返回False
    """
    # 检查文件是否存在
    if not os.path.exists(cookie_file_path):
        print(f"[is_cookie_valid] Cookie文件不存在: {cookie_file_path}")
        return False
    
    try:
        # 读取cookie文件
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
        
        # 检查是否有过期时间
        if 'expires_at' not in cookie_data or not cookie_data['expires_at']:
            print(f"[is_cookie_valid] Cookie文件中没有过期时间信息")
            return False
        
        # 解析过期时间
        expires_at = datetime.fromisoformat(cookie_data['expires_at'])
        current_time = datetime.now()
        
        # 检查是否过期（提前5分钟判断为过期，避免边界情况）
        if current_time >= expires_at - timedelta(minutes=5):
            print(f"[is_cookie_valid] Cookie已过期或即将过期")
            print(f"[is_cookie_valid] 过期时间: {expires_at}, 当前时间: {current_time}")
            return False
        
        print(f"[is_cookie_valid] Cookie有效，过期时间: {expires_at}")
        return True
        
    except Exception as e:
        print(f"[is_cookie_valid] 检查cookie时发生错误: {str(e)}")
        return False


def load_cookies_and_login(url, cookie_file_path, headless=True):
    """
    加载本地保存的cookie并自动登录网站
    
    参数:
        url (str): 需要访问的网站URL
        cookie_file_path (str): cookie文件路径
        headless (bool): 是否使用无头模式，默认为True
    
    返回:
        webdriver.Edge: 已登录的浏览器驱动对象，失败返回None
    """
    print(f"[load_cookies_and_login] 开始执行，目标URL: {url}")
    print(f"[load_cookies_and_login] Cookie文件路径: {cookie_file_path}")
    
    # 检查cookie是否有效
    if not is_cookie_valid(cookie_file_path):
        print(f"[load_cookies_and_login] Cookie无效或已过期，请重新登录")
        return None
    
    try:
        # 读取cookie文件
        print(f"[load_cookies_and_login] 正在读取cookie文件...")
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
        
        cookies = cookie_data.get('cookies', [])
        if not cookies:
            print(f"[load_cookies_and_login] Cookie文件中没有cookies数据")
            return None
        
        print(f"[load_cookies_and_login] 正在初始化Edge浏览器...")
        edge_options = get_edge_options(headless=headless)
        driver = webdriver.Edge(options=edge_options)
        print(f"[load_cookies_and_login] 浏览器初始化完成")
        
        # # 先访问网站主页，确保域名正确
        # print(f"[load_cookies_and_login] 正在访问网站主页...")
        # driver.get(url)
        # time.sleep(2)  # 等待页面加载
        
        # 添加cookies
        print(f"[load_cookies_and_login] 正在加载cookies...")
        for cookie in cookies:
            try:
                # 删除可能导致问题的字段
                cookie_to_add = cookie.copy()
                # 移除可能导致问题的字段
                cookie_to_add.pop('sameSite', None)
                cookie_to_add.pop('httpOnly', None)
                cookie_to_add.pop('secure', None)
                
                driver.add_cookie(cookie_to_add)
            except Exception as e:
                print(f"[load_cookies_and_login] 添加cookie时发生错误（跳过）: {str(e)}")
                continue
        
        # 刷新页面以应用cookies
        print(f"[load_cookies_and_login] 正在刷新页面以应用cookies...")
        driver.refresh()
        time.sleep(2)  # 等待页面加载
        
        print(f"[load_cookies_and_login] Cookie登录完成")
        return driver
        
    except Exception as e:
        print(f"[load_cookies_and_login] 发生错误: {str(e)}")
        return None


def get_driver_with_cookies(url, cookie_file_path, headless=True, auto_login=True):
    """
    获取带有cookie的浏览器驱动，如果cookie过期则提示重新登录
    
    参数:
        url (str): 需要访问的网站URL
        cookie_file_path (str): cookie文件路径
        headless (bool): 是否使用无头模式，默认为True
        auto_login (bool): 如果cookie有效是否自动登录，默认为True
    
    返回:
        webdriver.Edge: 已登录的浏览器驱动对象，失败返回None
    """
    print(f"[get_driver_with_cookies] 开始执行")
    
    # 如果cookie有效且需要自动登录
    if auto_login and is_cookie_valid(cookie_file_path):
        print(f"[get_driver_with_cookies] Cookie有效，正在自动登录...")
        return load_cookies_and_login(url, cookie_file_path, headless=headless)
    else:
        print(f"[get_driver_with_cookies] Cookie无效或已过期，请先调用save_cookies_after_login进行登录")
        return None


def request_page_by_selenium(url, cookie_file_path=None, headless=False):
    """
    使用Selenium请求页面并返回BeautifulSoup对象
    
    参数:
        url (str): 需要访问的页面URL
        cookie_file_path (str): 可选的cookie文件路径，如果提供则使用cookie登录
        headless (bool): 是否使用无头模式，默认为True
    
    返回:
        BeautifulSoup: 解析后的页面内容，失败返回None
    """
    print(f"[request_page_by_selenium] 开始执行，目标URL: {url}")
    if not cookie_file_path:
        cookie_file_path = cookie_manager(url)
    driver = None
    try:
        # 如果提供了cookie文件路径，尝试使用cookie登录
        if cookie_file_path and os.path.exists(cookie_file_path):
            print(f"[request_page_by_selenium] 检测到cookie文件，尝试使用cookie登录...")
            driver = load_cookies_and_login(url, cookie_file_path, headless=headless)
            if driver is None:
                print(f"[request_page_by_selenium] Cookie登录失败，使用普通模式访问...")
                # Cookie登录失败，使用普通模式
                edge_options = get_edge_options(headless=headless)
                driver = webdriver.Edge(options=edge_options)
                driver.get(url)
        else:
            # 没有cookie文件，使用普通模式
            print(f"[request_page_by_selenium] 正在初始化Edge浏览器...")
            edge_options = get_edge_options(headless=headless)
            driver = webdriver.Edge(options=edge_options)
            print(f"[request_page_by_selenium] 浏览器初始化完成")
            print(f"[request_page_by_selenium] 正在访问页面...")
            driver.get(url)
        
        print(f"[request_page_by_selenium] 等待页面动态加载（2秒）...")
        time.sleep(15)  # 等待页面动态加载内容
        print(f"[request_page_by_selenium] 正在获取页面源码...")
        page_source = driver.page_source
        print(f"[request_page_by_selenium] 正在解析页面内容...")
        soup = BeautifulSoup(page_source, 'html.parser')
        print(f"[request_page_by_selenium] 页面解析完成")
        return soup
    except Exception as e:
        print(f"[request_page_by_selenium] 发生错误: {str(e)}")
        return None
    finally:
        if driver:
            print(f"[request_page_by_selenium] 正在关闭浏览器...")
            driver.quit()
            print(f"[request_page_by_selenium] 浏览器已关闭")


if __name__ == '__main__':
    url = "https://so.toutiao.com/search?dvpf=pc&source=search_subtab_switch&keyword=%E6%90%9C%E7%B4%A2&pd=information&action_type=search_subtab_switch&page_num=0&search_id=&from=news&cur_tab_title=news"
    cookie = """tt_webid=7572579517837149736; ttcid=5727e84c5a77462bb9835236555432dd36; local_city_cache=%E8%8B%8F%E5%B7%9E; csrftoken=c85338b5f678f87cbbf7f409fb57b4a7; _ga=GA1.1.876125235.1763128574; s_v_web_id=verify_mhyx8dbs_9ftjGYJk_0td4_4N8A_B2hz_M263g2uDyRTF; _S_DPR=1.5; _S_IPAD=0; notRedShot=1; gfkadpd=24,6457; _ga_QEHZPBE5HH=GS2.1.s1763395123$o10$g0$t1763395123$j60$l0$h0; passport_csrf_token=714c2b470f21ab1b3c37dbc1c4f956da; passport_csrf_token_default=714c2b470f21ab1b3c37dbc1c4f956da; passport_mfa_token=CjQA13r8RL311hGuag8N3qCGYtDGuU4V03D%2BjP1T5E89ywnoYEB5EPGmXm8Si50o9JH6SQP3GkoKPAAAAAAAAAAAAABPumK296fuItkvMhdj5v6XZmJHHVc1XVjhojE9maSlE2Zqd0DUC0L1sDUHbebPONSCshCo8oEOGPax0WwgAiIBA61cDYA%3D; d_ticket=7dc52cfa0e17aade0fe25d27b706d8039615b; n_mh=RpgsamB0nplRzqGsl5j2eOop-JNLImreL6J_LJhZB1E; sso_auth_status=5beb36bd7e1a7f2281448bf5013c2f42; sso_auth_status_ss=5beb36bd7e1a7f2281448bf5013c2f42; sso_uid_tt=78bef385fb9d5eb3028a1601b71ab4bb; sso_uid_tt_ss=78bef385fb9d5eb3028a1601b71ab4bb; toutiao_sso_user=423a4742828cde3fa45d9d7c7c550515; toutiao_sso_user_ss=423a4742828cde3fa45d9d7c7c550515; sid_ucp_sso_v1=1.0.0-KDQyYzQ1NDRhNTdlOGEzZmJkN2UyMDZiNjg0YTVlNjdjZDBlY2NjZTcKGwjSsLCZYBDKiPLIBhgYIA4wtOzVvQU4AkDxBxoCaGwiIDQyM2E0NzQyODI4Y2RlM2ZhNDVkOWQ3YzdjNTUwNTE1; ssid_ucp_sso_v1=1.0.0-KDQyYzQ1NDRhNTdlOGEzZmJkN2UyMDZiNjg0YTVlNjdjZDBlY2NjZTcKGwjSsLCZYBDKiPLIBhgYIA4wtOzVvQU4AkDxBxoCaGwiIDQyM2E0NzQyODI4Y2RlM2ZhNDVkOWQ3YzdjNTUwNTE1; passport_auth_status=9af224da4d3477ce20b5d9cc7b727076%2Cfca9d62eace2f3cfd71a35eec76002f3; passport_auth_status_ss=9af224da4d3477ce20b5d9cc7b727076%2Cfca9d62eace2f3cfd71a35eec76002f3; sid_guard=c15f08467cb5ba3d223f74dfb2214781%7C1763476554%7C5184002%7CSat%2C+17-Jan-2026+14%3A35%3A56+GMT; uid_tt=8a414d367a4aa8922a9b3d9599e876e5; uid_tt_ss=8a414d367a4aa8922a9b3d9599e876e5; sid_tt=c15f08467cb5ba3d223f74dfb2214781; sessionid=c15f08467cb5ba3d223f74dfb2214781; sessionid_ss=c15f08467cb5ba3d223f74dfb2214781; session_tlb_tag=sttt%7C8%7CwV8IRny1uj0iP3TfsiFHgf________-xL_2I6cQgUcb2yIc1l8msGsxFJXliMh0XM3fK7LRIrVM%3D; session_tlb_tag_bk=sttt%7C8%7CwV8IRny1uj0iP3TfsiFHgf________-xL_2I6cQgUcb2yIc1l8msGsxFJXliMh0XM3fK7LRIrVM%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGJjMmFkZWQ5ZGJiZDdhMjk5NWYyOWZkODFjZmVkY2FlNzFkZDRiNDEKFQjSsLCZYBDKiPLIBhgYIA44AkDxBxoCbHEiIGMxNWYwODQ2N2NiNWJhM2QyMjNmNzRkZmIyMjE0Nzgx; ssid_ucp_v1=1.0.0-KGJjMmFkZWQ5ZGJiZDdhMjk5NWYyOWZkODFjZmVkY2FlNzFkZDRiNDEKFQjSsLCZYBDKiPLIBhgYIA44AkDxBxoCbHEiIGMxNWYwODQ2N2NiNWJhM2QyMjNmNzRkZmIyMjE0Nzgx; odin_tt=7510b59acb8f234b6726beba76f21d2a142a7aa84f1e1396798539c78134c93bc50a5082b98895affbeda855eb4c371f; _S_WIN_WH=1912_1044; ttwid=1%7CbIAgNjPDB0fbc5MF3rZ9pi3biUeyC0Cojklh-SIlP4s%7C1763477479%7Ca7c8c89405eb811af5c6bdaba38c4249db310f51e8aa4df7bc95e70413db2227; tt_anti_token=wtCN60yKLcU-5d1f09915fd1914311d2cde18cbe6a3b98452b5114635ba176c668d6d8ca51be; tt_scid=lLpDCc8.U369e6u.Che3s8mn3ynhwkLXkMwiQ8zvpJcrnrHdLQhlipEbWXt6g.hI121d"""
    cookie_manager(url, cookie)

    # 测试代码
    # url = "https://seekingalpha.com/news/4522989-verrica-targets-european-expansion-for-ycanth-as-phase-iii-programs-advance-and-sales-force"
    # aa = request_page_by_selenium(url)
    # print()

