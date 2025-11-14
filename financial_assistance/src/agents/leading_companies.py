from financial_assistance.src.utils.call_llm import call_llm

def find_leading_companies(industry: str, industry_chain_info: str = "") -> str:
    """
    找出相关行业龙头企业
    
    参数:
        industry: 待分析的行业名称（字符串）
        industry_chain_info: 产业链分析信息（可选字符串，默认为空）
    
    返回:
        str: LLM返回的龙头企业列表和分析结果
    """
    # 构建用户查询内容
    user_content = f"请找出{industry}行业相关的龙头企业，包括公司名称、主营业务、市场地位等信息"
    # 如果提供了产业链信息，则添加到查询中
    if industry_chain_info:
        user_content += f"\n\n相关产业链信息：\n{industry_chain_info}"
    
    # 构建消息列表
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': """You are a helpful assistant that can help me find leading companies in industries.
你需要找出指定行业相关的龙头企业，包括公司名称、主营业务、市场地位、技术优势等信息。
输出格式为结构化的文本或JSON格式，清晰展示各个龙头企业的情况。"""  # 系统提示内容
        },
        {
            'role': 'user',  # 用户角色消息
            'content': user_content  # 用户查询内容
        }
    ]
    
    # 调用LLM并返回响应
    return call_llm(messages)


if __name__ == "__main__":
    print(find_leading_companies("新能源汽车"))

