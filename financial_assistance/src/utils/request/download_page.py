"""
网页内容抓取模块
负责读取request_map.json中的URL配置，循环访问网页并提取文字信息
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time


def load_request_map(json_path: str) -> List[Dict]:
    """
    从JSON文件中加载URL配置信息
    
    参数:
        json_path: JSON文件路径
        
    返回:
        包含URL配置信息的列表，每个元素包含url、cookie、username、password等字段
    """
    # 检查文件是否存在
    if not os.path.exists(json_path):
        print(f"错误：文件 {json_path} 不存在")
        return []
    
    try:
        # 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 确保返回的是列表格式
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # 如果是字典，转换为列表
            return [data]
        else:
            print("错误：JSON格式不正确，应为列表或字典")
            return []
    except json.JSONDecodeError as e:
        print(f"错误：JSON解析失败 - {e}")
        return []
    except Exception as e:
        print(f"错误：读取文件失败 - {e}")
        return []


def get_page_text(url: str, cookie: Optional[str] = None,
                  username: Optional[str] = None, 
                  password: Optional[str] = None, 
                  timeout: int = 10) -> Optional[str]:
    """
    访问网页并提取文字内容
    
    参数:
        url: 目标网页URL
        cookie: Cookie字符串（可选，优先于username/password使用）
        username: 用户名（可选，用于基本认证，当无cookie时使用）
        password: 密码（可选，用于基本认证，当无cookie时使用）
        timeout: 请求超时时间（秒）
        
    返回:
        提取的网页文字内容，失败时返回None
    """
    try:
        # 创建会话对象
        session = requests.Session()
        
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 认证优先级：cookie > username/password
        # 如果提供了cookie，使用cookie进行认证
        if cookie:
            headers['Cookie'] = cookie
            auth = None
        # 如果提供了用户名和密码且没有cookie，使用基本认证
        elif username and password:
            auth = (username, password)
        else:
            auth = None
        
        # 发送GET请求
        response = session.post(url, headers=headers, auth=auth, timeout=timeout)
        
        # 检查响应状态码
        response.raise_for_status()
        
        # 设置响应编码
        response.encoding = response.apparent_encoding or 'utf-8'
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除script和style标签（这些标签中的内容不是我们需要的文字）
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 提取所有文字内容
        text = soup.get_text()
        
        # 清理文字：去除多余的空行和空白字符
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except requests.exceptions.Timeout:
        print(f"错误：访问 {url} 超时")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"错误：访问 {url} 失败，HTTP状态码：{e.response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"错误：访问 {url} 时发生网络错误：{e}")
        return None
    except Exception as e:
        print(f"错误：处理 {url} 时发生未知错误：{e}")
        return None


def save_text_to_file(text: str, url: str, output_dir: str = "output") -> str:
    """
    将提取的文字内容保存到文件
    
    参数:
        text: 要保存的文字内容
        url: 源URL（用于生成文件名）
        output_dir: 输出目录
        
    返回:
        保存的文件路径
    """
    # 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 从URL生成文件名（移除协议和特殊字符）
    filename = url.replace("https://", "").replace("http://", "")
    filename = filename.replace("/", "_").replace("?", "_").replace("&", "_")
    filename = filename.replace(":", "_").replace("*", "_").replace("|", "_")
    # 限制文件名长度
    if len(filename) > 200:
        filename = filename[:200]
    filename = f"{filename}.txt"
    
    # 完整文件路径
    filepath = os.path.join(output_dir, filename)
    
    # 写入文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"来源URL: {url}\n")
            f.write("=" * 80 + "\n\n")
            f.write(text)
        print(f"成功保存到：{filepath}")
        return filepath
    except Exception as e:
        print(f"错误：保存文件失败 - {e}")
        return ""


def crawl_pages(json_path: str = "request_map.json", 
                output_dir: str = "output",
                delay: float = 1.0) -> None:
    """
    主函数：读取JSON配置，循环访问所有URL并提取文字信息
    
    参数:
        json_path: JSON配置文件路径
        output_dir: 输出目录
        delay: 每次请求之间的延迟时间（秒），避免请求过快
    """
    print("=" * 80)
    print("开始网页内容抓取任务")
    print("=" * 80)
    
    # 加载URL配置
    print(f"\n正在加载配置文件：{json_path}")
    url_list = load_request_map(json_path)
    
    if not url_list:
        print("没有找到有效的URL配置，程序退出")
        return
    
    print(f"共找到 {len(url_list)} 个URL配置\n")
    
    # 统计信息
    success_count = 0
    fail_count = 0
    
    # 循环处理每个URL
    for index, config in enumerate(url_list, 1):
        url = config.get('url', '')
        cookie = config.get('cookie', None)
        username = config.get('username', None)
        password = config.get('password', None)
        description = config.get('description', '')
        
        if not url:
            print(f"[{index}/{len(url_list)}] 跳过：URL为空")
            fail_count += 1
            continue
        
        print(f"[{index}/{len(url_list)}] 正在处理：{url}")
        if description:
            print(f"  描述：{description}")
        
        # 提取网页文字（优先使用cookie，否则使用username/password）
        text = get_page_text(url, cookie=cookie, username=username, password=password)
        
        if text:
            # 保存到文件
            save_text_to_file(text, url, output_dir)
            success_count += 1
            print(f"  成功提取 {len(text)} 个字符的文字内容\n")
        else:
            fail_count += 1
            print(f"  提取失败\n")
        
        # 延迟，避免请求过快
        if index < len(url_list):
            time.sleep(delay)
    
    # 输出统计信息
    print("=" * 80)
    print("任务完成")
    print(f"成功：{success_count} 个，失败：{fail_count} 个")
    print("=" * 80)


if __name__ == "__main__":
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "request_map.json")
    
    # 执行爬取任务
    crawl_pages(json_path=json_path, output_dir="output", delay=1.0)

