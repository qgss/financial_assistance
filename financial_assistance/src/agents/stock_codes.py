from financial_assistance.src.utils.call_llm import call_llm

def find_stock_codes(companies: str) -> str:
    """
    找出相关股票代码
    
    参数:
        companies: 公司名称列表或相关信息（字符串）
    
    返回:
        str: LLM返回的股票代码列表和分析结果
    """
    # 构建消息列表
    messages = [
        {
            'role': 'system',  # 系统角色消息
            'content': """You are a helpful assistant that can help me find stock codes for companies.
你需要根据提供的公司名称，找出对应的股票代码（包括A股、港股、美股等）。
输出格式为JSON格式，包含公司名称、股票代码、交易所、股票简称等信息。
例如：
```json
[
  {"company": "公司名称", "stock_code": "股票代码", "exchange": "交易所", "stock_name": "股票简称"}
]
```"""  # 系统提示内容
        },
        {
            'role': 'user',  # 用户角色消息
            'content': f"请找出以下公司对应的股票代码：\n{companies}"  # 用户查询内容
        }
    ]
    
    # 调用LLM并返回响应
    return call_llm(messages)


if __name__ == "__main__":
    print(find_stock_codes("比亚迪、宁德时代、特斯拉"))

