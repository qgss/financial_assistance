from openai import OpenAI

# 初始化OpenAI客户端，使用ModelScope的API
client = OpenAI(
    api_key="ms-021ea8b4-3584-4e24-a5ab-f5f8fb666f15",  # ModelScope Token
    base_url="https://api-inference.modelscope.cn/v1"  # ModelScope API基础URL
)

def generate_messages(user_query: str) -> str:
    """
    生成用于调用LLM的消息列表并获取响应
    
    参数:
        user_query: 用户的查询内容（字符串）
    
    返回:
        str: LLM返回的响应内容
    """
    # 构建消息列表
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': """You are a helpful assistant that can help me analyze the industry and find the next big thing.
你需要输出一些搜索关键字，这些关键字的长度不能超过10个字符，要包含行业背景和具体产业，例如"电池"需要包含新能源汽车的行业北京，所以关键字为新能源汽车电池发展或新能源汽车电池技术。
输出格式为json的list格式，如
```json
["关键词1", "关键词2", "关键词3"]
```"""  # 系统提示内容
        },
        {
            'role': 'user',  # 用户角色消息
            'content': user_query  # 用户查询内容
        }
    ]
    
    # 调用LLM并返回响应
    return call_llm(messages)

def call_llm(messages: list) -> str:
    """
    调用大语言模型API，获取响应内容
    
    参数:
        messages: 消息列表，每个消息为字典格式，包含'role'和'content'字段
                 例如: [{'role': 'system', 'content': '...'}, {'role': 'user', 'content': '...'}]
    
    返回:
        str: 模型返回的完整响应内容
    """
    # 调用API创建聊天完成请求，使用流式输出
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",  # ModelScope模型ID
        messages=messages,  # 传入的消息列表
        stream=True  # 启用流式输出
    )
    
    # 初始化响应内容字符串
    full_content = ""
    
    # 遍历流式响应的每个chunk
    for chunk in response:
        # 获取当前chunk的内容（可能为None）
        delta_content = chunk.choices[0].delta.content
        # 如果内容不为None，则追加到完整响应中
        if delta_content is not None:
            full_content += delta_content
    
    # 返回完整的响应内容
    return full_content

if __name__ == "__main__":
    print(generate_messages("针对当下的热门产业新能源汽车，你需要指出该行业所涉及的产业，分析出接下来需要重点发展突破的产业"))