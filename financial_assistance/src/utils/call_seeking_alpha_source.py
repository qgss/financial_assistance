import json

from financial_assistance.src.utils.request.simple_spider import request_page_by_selenium

def get_seeking_alpha_news(news_num_limit=10):
    request_url = "https://seekingalpha.com/api/v3/news?fields[news]=title%2Cdate%2Ccomment_count%2Ccontent%2CprimaryTickers%2CsecondaryTickers%2Ctag%2CgettyImageUrl%2CpublishOn&fields[tag]=slug%2Cname&filter[category]=market-news%3A%3Aall&filter[since]=0&filter[until]=0&include=primaryTickers%2CsecondaryTickers&isMounting=true&page[size]=25&page[number]=1"

    news_list = request_page_by_selenium(request_url)
    json_data = {}
    try:
        json_data = json.loads(news_list.find_all("pre")[0].text)
    except:
        print("当前方式无法格式数据，尝试基本方式")
    try:
        json_data = json.loads(news_list.text)
    except:
        print("尝试基本方式无法奏效，放弃")
    news_dict_list = []
    if "data" in json_data:
        for item in json_data["data"]:
            try:
                cur_new = {
                    "title": item["attributes"]["title"],
                    "date": item["attributes"]["publishOn"],
                    "self": item["links"]["self"],
                }
                news_dict_list.append(cur_new)
                if len(news_dict_list) > news_num_limit:
                    break
            except Exception as e:
                print(f"在取数据 {str(item)} 时遇到 {str(e)} 的故障")
    return news_dict_list


def download_seeking_pages(news_list):
    base_url = "https://seekingalpha.com"
    download_result = []
    for item in news_list:
        url = base_url + item["self"]
        response_str = "网页搜索无法返回任何有效结果。"
        try:
            response = request_page_by_selenium(url)
            response_str = response.text
        except Exception as e:
            print(f"在下载 {url} 时遇到 {str(e)} 的故障")
        cur_new = {
            "title": item["attributes"]["title"],
            "content": response_str,
            "date": item["attributes"]["publishOn"],
        }
        download_result.append(cur_new)
    return download_result


def get_seeking_alpha_analysis():
    base_url = "https://seekingalpha.com/api/v3/"
    request_url = "https://seekingalpha.com/latest-articles"
    example_url = "https://seekingalpha.com/article/4844609-acadia-realty-trust-undervalued-reit-with-strong-growth-ahead#source=section%3Aanalysis%7Csection_asset%3Aheadline%7Curl_first_level%3Alatest-articles"


if __name__ == '__main__':
    response = request_page_by_selenium("https://seekingalpha.com/news/4522989-verrica-targets-european-expansion-for-ycanth-as-phase-iii-programs-advance-and-sales-force")

    print()
