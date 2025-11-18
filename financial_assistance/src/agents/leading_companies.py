from financial_assistance.src.utils.call_baidu_search import search_by_baidu_web_search
from financial_assistance.src.utils.call_llm import call_llm
from financial_assistance.src.utils.load_config import CURRENT_PROJECT
from financial_assistance.src.utils.safe_load_json import safe_load_json_from_str


def find_leading_companies(industry: str, industry_chain_info: str = "") -> list:
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
你需要找出指定行业相关的龙头企业的公司名称，注意，请不要包含除公司名称意外的其他描述。
输出格式为json:
{
    companies: ["公司名称1", "公司名称2", "公司名称3", ...]
}"""  # 系统提示内容
        },
        {
            'role': 'user',  # 用户角色消息
            'content': user_content  # 用户查询内容
        }
    ]
    
    # 调用LLM并返回响应
    companies_str = call_llm(messages)
    companies = safe_load_json_from_str(companies_str).get("companies", [])
    return companies


def search_and_output_leading_companies(industry: str, industry_chain_info: str = ""):
    if not industry_chain_info:
        industry_chain_info = "相关报道信息：\n"
        industry_chain_infos = search_by_baidu_web_search(f"{industry}相关龙头企业有哪些")
        for industry_chain in industry_chain_infos:
            if len(industry_chain_info) > CURRENT_PROJECT["max_token"]:
                break
            industry_chain_info += f"{industry_chain['title']}: {industry_chain['content']}\n\n"
    return find_leading_companies(industry, industry_chain_info)


if __name__ == "__main__":
    print(search_and_output_leading_companies("AI计算卡"))

