from financial_assistance.src.utils.call_llm import call_llm

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


if __name__ == "__main__":
    print(analyze_industry_chain("新能源汽车"))

