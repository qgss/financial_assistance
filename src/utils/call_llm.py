from openai import OpenAI

# 初始化OpenAI客户端，使用ModelScope的API
client = OpenAI(
    api_key="ms-021ea8b4-3584-4e24-a5ab-f5f8fb666f15",  # ModelScope Token
    base_url="https://api-inference.modelscope.cn/v1"  # ModelScope API基础URL
)


def generate_messages(user_query: str) -> list:
    """
    生成用于调用LLM的消息列表
    
    参数:
        user_query: 用户的查询内容（字符串）
    
    返回:
        list: 消息列表，包含system和user角色的消息
             格式: [{'role': 'system', 'content': '...'}, {'role': 'user', 'content': '...'}]
    """
    # 构建消息列表
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': 'You are a helpful assistant.'  # 系统提示内容
        },
        {
            'role': 'user',  # 用户角色消息
            'content': user_query  # 用户查询内容
        }
    ]
    
    # 返回消息列表
    return messages


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