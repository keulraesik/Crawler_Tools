#coding=utf8
import requests
import pandas as pd

def stock_code():
    r = requests.get(url='http://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=hk')    # 最基本的GET请求
    # print(r.status_code)    # 获取返回状态
    # print(r.url)
    # print(r.text)   #解码后的返回数据
    
    original_html = pd.read_html(r.text)
    # print original_html[0]
    # print original_html[1]
    table_df = original_html[2]
    # print table_df
    
    print table_df.index
    print table_df.columns
    print table_df[0].tolist()[2:]

    return table_df[0].tolist()[2:]

if __name__ == '__main__':
	stock_code()