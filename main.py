# -*- coding:utf-8 -*-

"""
CoinMarketCap USD Price History

  Print the CoinMarketCap USD price history for a particular cryptocurrency in CSV format.
"""

import sys
import datetime
import coinmarketcap_usd_history

import requests
import pandas as pd
from bs4 import BeautifulSoup
def output_table():
    r = requests.get(url='https://coinmarketcap.com/coins/views/all/')
    # print(r.status_code)    # 获取返回状态
    # print(r.url)
    # print(r.text)   #解码后的返回数据
    original_html = pd.read_html(r.text)
    # print original_html[0]
    table_df = original_html[0]
    # print table_df
    # print table_df.index
    # print table_df.columns
    # print table_df[0].tolist()[2:]
    # return table_df[0].tolist()[2:]
def mkdir(path):
    # 传入创建的文件夹目录或者路径
    # mkpath="d:\\qttc\\web\\"
    # 引入模块
    import os
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path) 
        print path+' 创建成功'
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print path+' 目录已存在'
        return False

def get_id_of_coins():
    coin_id_list = []
    r = requests.get(url='https://coinmarketcap.com/coins/views/all/')
    soup = BeautifulSoup(r.text, 'html.parser')
    # tr = soup.find_all('tr')
    # print len(tr)
    # 第一个tr与coin无关
    # for item in soup.find_all("tr")[1:]:
    #     coin_id_list.append(item.get("id")[3:])
    coin_id_list = [item.get("id")[3:] for item in soup.find_all("tr")[1:]]
    return coin_id_list

if __name__ == '__main__':
  # If you just wish to have the CSV output returned as a string to another python module, simply omit the '--dataframe' parameter.
  # df = coinmarketcap_usd_history.main(['bitcoin','2017-01-01','2017-12-31','--dataframe'])
  # 2013-04-28是最早的一天
  # 虽然不是所有的加密货币的发行时间都是2013-04-28，网站默认自动返回最早的一天
  # 网站自身也是这么处理的
  # df = coinmarketcap_usd_history.main(['bitcoin-cash','2017-04-28','2018-01-16'])
  mkdir('csv_file')
  coin_id_list = get_id_of_coins()
  for coin_id in coin_id_list:
      print coin_id
      df = coinmarketcap_usd_history.main([coin_id,'2013-04-28','2018-01-16'])
