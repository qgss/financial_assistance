# 网页内容抓取模块

## 功能概述

本模块负责从配置文件中读取网页URL信息，循环访问这些网页并提取其中的文字内容。支持基本HTTP认证（用户名/密码），适用于需要批量抓取网页文字信息的场景。

## 文件结构

```
info_collector/
├── download_page.py      # 主程序文件
├── request_map.json      # URL配置文件
└── README.md            # 本说明文件
```

## 核心功能

### 1. 配置文件读取
- 从 `request_map.json` 文件中读取URL配置信息
- 支持列表和字典两种JSON格式
- 自动处理文件不存在、格式错误等异常情况

### 2. 网页访问与认证
- 支持HTTP/HTTPS协议
- 支持基本HTTP认证（Basic Authentication）
- 模拟浏览器请求头，提高访问成功率
- 自动处理编码问题

### 3. 文字内容提取
- 使用BeautifulSoup解析HTML内容
- 自动移除script、style等标签
- 清理多余空白字符和空行
- 保留网页的主要文字内容

### 4. 结果保存
- 自动创建输出目录
- 根据URL自动生成文件名
- 保存时包含来源URL信息
- 支持UTF-8编码

### 5. 错误处理
- 网络超时处理
- HTTP错误状态码处理
- 文件读写异常处理
- 详细的错误信息输出

## 配置文件格式

`request_map.json` 文件采用JSON数组格式，每个元素包含以下字段：

```json
[
  {
    "url": "https://example.com/page1",    // 必需：目标网页URL
    "cookie": "session_id=abc123; token=xyz789",  // 可选：Cookie字符串，优先于username/password
    "username": "user1",                    // 可选：HTTP基本认证用户名（当无cookie时使用）
    "password": "pass1",                    // 可选：HTTP基本认证密码（当无cookie时使用）
    "description": "示例网页1"              // 可选：描述信息
  },
  {
    "url": "https://example.com/page2",
    "username": "user2",
    "password": "pass2",
    "description": "示例网页2"
  },
  {
    "url": "https://example.com/page3",
    "cookie": "auth_token=def456",
    "description": "使用Cookie认证的示例网页"
  }
]
```

### 字段说明

- **url** (必需): 要访问的网页地址，支持http和https协议
- **cookie** (可选): Cookie字符串，用于身份认证。当提供cookie时，将优先使用cookie进行访问，忽略username和password字段
- **username** (可选): 如果网页需要HTTP基本认证且未提供cookie，提供用户名
- **password** (可选): 如果网页需要HTTP基本认证且未提供cookie，提供密码
- **description** (可选): 该URL的描述信息，用于日志输出

**认证优先级**: cookie > username/password（当存在cookie时，username和password将被忽略）

## 使用方法

### 1. 安装依赖

在项目根目录执行：

```bash
pip install -r requirements.txt
```

主要依赖包：
- `requests`: HTTP请求库
- `beautifulsoup4`: HTML解析库
- `lxml`: XML/HTML解析器（BeautifulSoup的解析器）

### 2. 配置URL列表

编辑 `request_map.json` 文件，添加需要抓取的网页URL和认证信息。

### 3. 运行程序

在 `info_collector` 目录下执行：

```bash
python download_page.py
```

或者在项目根目录执行：

```bash
python info_collector/download_page.py
```

### 4. 查看结果

程序会在 `info_collector/output` 目录下生成文本文件，每个网页对应一个文件。文件名根据URL自动生成。

## 输出说明

### 输出目录

默认输出目录为 `info_collector/output`，如果目录不存在会自动创建。

### 输出文件格式

每个输出文件包含：
1. 第一行：来源URL信息
2. 分隔线
3. 提取的网页文字内容

示例：
```
来源URL: https://example.com/page1
================================================================================

网页文字内容...
```

### 文件命名规则

- 移除URL中的协议部分（http://、https://）
- 将特殊字符（/、?、&、:、*、|）替换为下划线
- 限制文件名长度不超过200个字符
- 文件扩展名为 `.txt`

## 程序参数

在 `download_page.py` 的 `main` 函数中，可以调整以下参数：

- **json_path**: JSON配置文件路径（默认：当前目录下的 `request_map.json`）
- **output_dir**: 输出目录（默认：`"output"`）
- **delay**: 每次请求之间的延迟时间，单位秒（默认：`1.0`秒）

修改示例：
```python
crawl_pages(json_path=json_path, output_dir="my_output", delay=2.0)
```

## 功能特性

✅ **批量处理**: 支持一次性处理多个URL  
✅ **认证支持**: 支持HTTP基本认证  
✅ **智能提取**: 自动过滤HTML标签，只提取文字内容  
✅ **错误容错**: 单个URL失败不影响其他URL的处理  
✅ **请求限速**: 支持设置请求间隔，避免请求过快  
✅ **统计信息**: 输出成功和失败的统计信息  
✅ **编码处理**: 自动识别和处理网页编码  

## 注意事项

1. **网络连接**: 确保网络连接正常，能够访问目标URL
2. **认证信息**: 如果网页需要登录，确保提供正确的用户名和密码
3. **请求频率**: 建议设置适当的延迟时间，避免对目标服务器造成过大压力
4. **超时设置**: 默认超时时间为10秒，可根据网络情况调整
5. **文件权限**: 确保程序有权限创建输出目录和写入文件

## 错误处理

程序会处理以下常见错误：

- 配置文件不存在或格式错误
- 网络连接超时
- HTTP错误状态码（如404、500等）
- 网页编码识别失败
- 文件写入权限问题

所有错误信息都会在控制台输出，方便排查问题。

## 扩展说明

如需扩展功能，可以修改以下函数：

- `get_page_text()`: 修改网页访问和内容提取逻辑
- `save_text_to_file()`: 修改文件保存格式或位置
- `crawl_pages()`: 修改主流程逻辑

## 版本信息

- Python版本要求: Python 3.6+
- 最后更新: 2024年



# 基本思维链
- 输入待分析热门行业
- 分析相关产业链
- 结合当前技术能力，分析重点发展方向
- 找出相关行业龙头企业
- 找出相关股票代码
- 下载股票信息，分析发展趋势