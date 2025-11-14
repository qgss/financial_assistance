from financial_assistance.src.utils.call_llm import call_llm

def analyze_stock_trends(stock_info: str, stock_data: str = "") -> str:
    """
    下载股票信息，分析发展趋势
    
    参数:
        stock_info: 股票代码或股票相关信息（字符串）
        stock_data: 股票数据（可选字符串，默认为空，可以是下载的股票数据）
    
    返回:
        str: LLM返回的股票发展趋势分析结果
    """
    # 构建用户查询内容
    user_content = f"请分析以下股票的发展趋势：\n{stock_info}"
    # 如果提供了股票数据，则添加到查询中
    if stock_data:
        user_content += f"\n\n股票数据：\n{stock_data}"
    
    # 构建消息列表
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': """You are a helpful assistant that can help me analyze stock trends.
你需要根据提供的股票信息或数据，分析股票的发展趋势，包括价格走势、技术指标、基本面分析、未来预测等。
输出格式为结构化的文本，清晰展示分析结果和趋势判断。"""  # 系统提示内容
        },
        {
            'role': 'user',  # 用户角色消息
            'content': user_content  # 用户查询内容
        }
    ]
    
    # 调用LLM并返回响应
    return call_llm(messages)


if __name__ == "__main__":
    print(analyze_stock_trends("比亚迪(002594.SZ)"))

