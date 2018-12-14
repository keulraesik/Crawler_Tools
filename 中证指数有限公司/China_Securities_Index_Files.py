import requests
import json
from pyquery import PyQuery as pq

def pdf_file(url,file_name):
    response = requests.get(url)

    with open(file_name+".pdf", "wb") as file:
            file.write(response.content)

def download_file(base_url, code):

    url = base_url + code
    response = requests.get(url)
    html = response.text
    # print(html)
    doc = pq(html)
    name = doc('.d_title').text()

    stats_index_items = doc('.stats_index')
    print((stats_index_items.items()))
    for item in stats_index_items.items():
        file_url = item.attr('href')
        if item.text() == '编制方案':
            pdf_file(file_url,name)



if __name__=='__main__':
    # base_url = 'http://www.csindex.com.cn/zh-CN/indices/index-detail/'
    # code = 'H50042'
    # download_file(base_url,code)

    url = 'http://www.csindex.com.cn/zh-CN/indices/index?page=1&page_size=50&by=desc&order=%E6%8C%87%E6%95%B0%E4%BB%A3%E7%A0%81&data_type=json&class_1=1&class_2=2&class_3=3&class_7=7&class_8=8&class_9=9&class_10=10&class_26=26'

    base_url = 'http://www.csindex.com.cn/zh-CN/indices/index-detail/'

    response = requests.get(url)
    json_data = response.text
    json_obj = json.loads(json_data)

    print(json_obj)
    print(json_obj["list"])

    for item in json_obj["list"]:
        code = item["index_code"]
        name = item["indx_sname"]
        print(code, name)

        download_file(base_url, code)


