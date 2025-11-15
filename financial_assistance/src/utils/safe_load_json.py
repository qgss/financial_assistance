import json
import re

def safe_load_json_from_str(text: str):
    """
    从字符串中解析出字典类型的JSON对象（仅支持{}包裹的dict）。
    支持从含有杂质内容中提取第1个合法的JSON字典对象（如: abc {"a":1} cde）。
    也支持以 ```json ... ``` 或 ``` ... ``` 代码块包裹的情况。
    参数:
        text (str): 含有JSON的字符串
    返回:
        dict: 解析后的JSON字典对象
    抛出:
        json.JSONDecodeError
        ValueError
    """
    # 尝试处理代码块包裹
    code_block_pattern = r"^```(?:json)?\s*([\s\S]*?)\s*```$"
    match = re.match(code_block_pattern, text.strip(), re.IGNORECASE)
    if match:
        json_str = match.group(1).strip()
        result = json.loads(json_str)
        # 确保返回的是字典类型
        if not isinstance(result, dict):
            raise ValueError("代码块中的JSON不是字典类型")
        return result

    # 查找第一个{}包裹的字典对象
    obj_pattern = re.compile(r'({[\s\S]*})')
    obj_match = obj_pattern.search(text)
    
    if not obj_match:
        raise ValueError("未找到可解析的JSON字典对象（未检测到{}包裹的结构）")
    
    json_candidate = obj_match.group(1)

    # 尝试解析(如果有多余的内容，json.loads会报错)
    # 逐步裁剪字符串直到能成功解析
    try:
        result = json.loads(json_candidate)
        # 确保返回的是字典类型
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        print(f"Error. 在处理字符串 {text} 时，无法解析出JSON字典对象")
    # 如果无法解析，抛出错误
    return {}


