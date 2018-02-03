#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import requests
import urllib2
import urllib
import argparse
import datetime
from bs4 import BeautifulSoup
import download
import time
import threading
import multiprocessing

parser = argparse.ArgumentParser()

parser.add_argument("year",help="the argument is year when you want to download filess.", type=str)

def parse_options(args):
  """
  Extract parameters from command line.
  """
  year   = args.year
  return year

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

def urlretrieve_download_pdf_file(href_number,file_name,year):
    try:
        print "downloading " + file_name

        url = 'http://www.iresearch.cn/include/ajax/user_ajax.ashx?work=idown&rid=' + href_number
        # url = 'http://www.iresearch.cn/include/ajax/user_ajax.ashx?work=idown&rid=3100'
        urllib.urlretrieve(url, year+"/"+file_name+".pdf")
        # r = requests.get(url, verify=False)
        # with open( year+"/"+file_name+".pdf", "wb") as code:
        #     code.write(r.content)
    except Exception as e:
        print "errors in downloading " +year+" "+file_name

def download_html(url):

    try:
        page = urllib2.urlopen(url, timeout=10)
        if page.getcode() != 200:
            raise Exception('Failed to load page')
        html = page.read()
        page.close()

    except Exception as e:
        print('Error fetching price data from ' + url)
        if hasattr(e, 'message'):
            print("Error message: " + e.message)
        else:
            print(e)
            sys.exit(1)

    return html

def extract_data(html):
    """
    Extract the price history from the HTML.
    """
    # url = 'http://www.iresearch.com.cn/report/reportlist.aspx?page=1&year=2017'
    # r = requests.get(url)
    # soup = BeautifulSoup(r.text, 'html.parser')
    # print soup
    soup = BeautifulSoup(html, 'html.parser')
    all_div = soup.find_all("div","title13")
    # print len(all_div)
    file_name_list = []
    file_href_list = []
    # domain = "http://www.iresearch.com.cn"
    for div_item in all_div:

        file_href_list.append((div_item.select('a')[0])['href'])

        file_name_list.append(div_item.get_text("|", strip=True))

    file_href_number_list = [(href[8:])[:-5] for href in file_href_list]
    # print file_href_number_list
    return file_href_number_list,file_name_list

def extract_page_numbers(html):
    soup = BeautifulSoup(html, 'html.parser')
    page_tip = soup.find("li","page_tip").get_text("|", strip=True)
    total_page = page_tip[-2:-1]
    return total_page

def generate_all_file_url(page, year):
    file_url_list = []

    url = "http://www.iresearch.com.cn/report/reportlist.aspx?page=" + str(page) + "&year=" + str(year)
    html = download_html(url)
    file_href_list, file_name_list = extract_data(html)
    # print file_href_list
    if len(file_href_list) == len(file_name_list):
        for i in range(len(file_href_list)):
            href_number = file_href_list[i]
            url = 'http://www.iresearch.cn/include/ajax/user_ajax.ashx?work=idown&rid=' + href_number
            # print url
            file_url_list.append(url)
    return file_url_list,file_name_list

def download_by_page_year(page,year):
    url = "http://www.iresearch.com.cn/report/reportlist.aspx?page="+ page +"&year=" + year

    html = download_html(url)

    file_href_list, file_name_list = extract_data(html)

    if len(file_href_list) == len(file_name_list):

        for i in range(len(file_href_list)):

            start = time.clock()
            download.requests_download_pdf_file(file_href_list[i], file_name_list[i], year)
            elapsed = (time.clock() - start)
            print("Time used:", elapsed)
            # thread = threading.Thread(target=download.download_pdf_file, args=(file_href_list[i], file_name_list[i], year))
            # thread.start()
            # thread.join()
    else:
        print "len(file_href_list) != len(file_name_list)"

def download_file_by_all_file_url(all_file_url,all_file_name,year):
    threadID = 1
    if len(all_file_url) == len(all_file_name):
        for i in range(len(all_file_url)):
            url = all_file_url[i]
            file_name = all_file_name[i]

            download.pdf_file(url,file_name,year)
            try:
                print " has finished " + str(i * 100.0 / len(all_file_url)) + "%"
                print  "starts to download " + file_name
            except Exception as e:
                print "print errors, not affect the result"

            # t = threading.Thread(target=download.pdf_file, args=(url,file_name,year))
            # print "thread " + str(threadID) + " starts to download " + file_name
            # t.start()
            # threadID += 1
            # t.join()
    else:
        print "len(all_file_url) != len(all_file_name)"

def main(args=None):
    # assert that args is a list
    if (args is not None):
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    year = parse_options(args)
    #创建文件夹，用年份命名
    mkdir(year)
    url = "http://www.iresearch.com.cn/report/reportlist.aspx?year=" + year
    html = download_html(url)
    total_page = extract_page_numbers(html)
    print year + " total page is : "+ total_page

    all_file_url = []
    all_file_name = []
    for page in range(int(total_page)):
        file_url_list,file_name_list = generate_all_file_url(str(page+1), str(year))

        all_file_url  += file_url_list
        all_file_name += file_name_list
    print all_file_url
    print all_file_name
    download_file_by_all_file_url(all_file_url,all_file_name,year)
    # for page in range(int(total_page)):
    #     download_by_page_year(str(page), str(year))


if __name__ == '__main__':
    main()