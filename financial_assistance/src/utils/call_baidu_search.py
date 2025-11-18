from openai import OpenAI
import requests
import json
import urllib
from urllib import parse

api_key = "bce-v3/ALTAK-2cit0vxdB5m6S5bIiWw5d/9188f8da8196b272dc8ad5a3ff574c5db3d88ca4"
client_baidu_search = OpenAI(api_key=api_key,  # 千帆AppBuilder平台的ApiKey
                             base_url="https://qianfan.baidubce.com/v2/ai_search") # 智能搜索生成V2版本接口


# def search_by_baidu_ai(message):
#     response = client_baidu_search.chat.completions.create(
#         model="deepseek-r1",
#         messages=[
#             {"role": "user", "content": message}
#         ],
#         stream=False
#     )
#     print(response.choices[0].message.content)


def search_by_baidu_web_search(message, api_key=None, top_k=5, site="", recency="year"):
    """
    使用requests库调用千帆 web_search 接口，搜索Baidu网页内容
    :param message: 用户查询内容 (str)
    :param api_key: 千帆AppBuilder API Key (str)，可选
    :param top_k: 返回网页条数 (int)
    :param site: 限定搜索的网站 (str)
    :param recency: 数据时效，如"year", "month"
    :return: 返回接口json响应 (dict)
    """
    if api_key is None:
        api_key = "bce-v3/ALTAK-2cit0vxdB5m6S5bIiWw5d/9188f8da8196b272dc8ad5a3ff574c5db3d88ca4"
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"
    headers = {
        "X-Appbuilder-Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [
            {
                "content": message,
                "role": "user"
            }
        ],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": top_k}],
        # "search_filter": {
        #     "match": {
        #         "site": [site]
        #     }
        # },
        "search_recency_filter": recency
    }
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    search_dict_list = []
    for ref in result.get("references", []):
        cur_search_result = {
            "title": urllib.parse.unquote(ref.get("title", "")),
            "content": urllib.parse.unquote(ref.get("content", "")),
            "date": ref.get("date", ""),
            "snippet": urllib.parse.unquote(ref.get("snippet", "")),
        }
        print(json.dumps(cur_search_result, indent=2))
        search_dict_list.append(cur_search_result)
    return search_dict_list



def search_by_baidu_ai_post(message, api_key=None, model="deepseek-r1"):
    """
    禁用，当前没有充钱
    使用requests库基于POST方式调用千帆AI搜索生成接口（流式请求）
    :param message: 用户查询内容 (str)
    :param api_key: AppBuilder API Key (str), 可选
    :param model: 调用的模型名称 (str), 默认为"deepseek-r1"
    :return: 返回接口响应内容 (str)，完整拼接后的字符串
    """
    if api_key is None:
        api_key = "bce-v3/ALTAK-2cit0vxdB5m6S5bIiWw5d/9188f8da8196b272dc8ad5a3ff574c5db3d88ca"
    url = "https://qianfan.baidubce.com/v2/ai_search/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {
                "content": message,
                "role": "user"
            }
        ],
        "stream": True,  # 改为流式请求
        "model": model,
        "instruction": "输出风格为markdown格式，如果有时间信息，请包含",
        "enable_corner_markers": True,
        "enable_deep_search": False,
        "search_recency_filter": "month" # 最近30天的数据
    }
    try:
        # 发送流式请求
        response = requests.post(url, headers=headers, json=payload, timeout=400, stream=True)
        response.raise_for_status()
        
        # 用于存储完整的内容
        full_content = ""
        
        # 逐行读取流式响应（SSE格式）
        for line in response.iter_lines():
            if line:
                # 解码字节为字符串
                line_str = line.decode('utf-8')
                
                # SSE格式通常以"data: "开头
                if line_str.startswith("data: "):
                    # 提取JSON数据部分
                    json_str = line_str[6:]  # 去掉"data: "前缀
                    
                    # 处理结束标记
                    if json_str.strip() == "[DONE]":
                        break
                    
                    try:
                        # 解析JSON数据
                        chunk_data = json.loads(json_str)
                        
                        # 提取content内容（根据实际API响应结构调整）
                        if "choices" in chunk_data and chunk_data["choices"]:
                            delta = chunk_data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                full_content += content
                        elif "result" in chunk_data:
                            # 如果直接返回result字段
                            full_content += str(chunk_data["result"])
                        elif "content" in chunk_data:
                            # 如果直接包含content字段
                            full_content += str(chunk_data["content"])
                    except json.JSONDecodeError:
                        # 如果解析失败，跳过该行
                        continue
        
        # 返回完整拼接后的内容
        if not full_content:
            full_content = ""
        return [{
            "title": message,
            "content": full_content,
        }]

        
    except Exception as e:
        print(f"[search_by_baidu_ai_post] 请求失败: {e}")
        return []

