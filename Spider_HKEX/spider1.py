# coding=utf8
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.common.exceptions import NoSuchElementException


import re
from pyquery import PyQuery as pq
from config import *

from bs4 import BeautifulSoup
import pandas as pd
import pymysql
import time
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

browser = webdriver.Chrome(service_args=SERVICE_ARGS)
wait = WebDriverWait(browser, 10)


def set_mysql():
    conn = pymysql.connect(host='localhost', user='root', passwd='zjz4818774', db='HKdata', charset='utf8')
    cur = conn.cursor()
    return {'conn': conn, 'cur': cur}

def close_mysql(conn,cur):
    cur.close()
    conn.close()

def remove_space(str):
    str = str.replace('/n', '')
    pattern = re.compile('\s+')
    str = re.sub(pattern, '', str)
    return str

def store(riqi, code, stockname, equity, num, participant, volume, percent):
    mysql = set_mysql()
    conn = mysql['conn']
    cur = mysql['cur']

    times = cur.execute("select * from data1 WHERE riqi = %s and code = %s and participant=%s", (riqi,code,participant))
    print('times',times)
    if (times == 0):
        cur.execute("INSERT INTO data1(riqi, code, stockname, equity, num, participant, volume, percent) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(riqi, code, stockname, equity, num, participant, volume, percent))
        cur.connection.commit()
        # print("Successful %s,%s,%s,%s,%s,%s,%s,%s" % (riqi, code, stockname, equity, num, participant, volume, percent))
        print('-------------')


def use_chrome_browser():
    print("Use Chrome Browser")
    #增加headers
    options = webdriver.ChromeOptions()
    options.add_argument(
        'User-Agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"')
    try:
        browser.get("http://www.hkexnews.hk/sdw/search/searchsdw_c.aspx")
        input = wait.until(
            EC.presence_of_element_located((By.XPATH,'//*[@id="txtStockCode"]'))
        )
        submit1 = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btnSearch"]'))
        )
        return browser
    except TimeoutException:
        return use_chrome_browser()

def change_page_date(browser, year, month, day, KEYWORD):
    #获取调整年，月，日的按钮，查找元素
    chang_day = Select(browser.find_element_by_xpath('//*[@id="ddlShareholdingDay"]'))
    change_month = Select(browser.find_element_by_xpath('//*[@id="ddlShareholdingMonth"]'))
    change_year = Select(browser.find_element_by_xpath('//*[@id="ddlShareholdingYear"]'))
    #调整年，月，日
    chang_day.select_by_index(day-1)
    change_month.select_by_index(month-1)
    if year==2017:
        pass
    else:
        change_year.select_by_index(1)
    #提交股票代码并搜寻
    input = browser.find_element_by_xpath('//*[@id="txtStockCode"]')
    submit1 = browser.find_element_by_xpath('//*[@id="btnSearch"]')
    submit2 = browser.find_element_by_xpath('//*[@id="pnlSearch"]')

    input.send_keys(KEYWORD)  # KEYWORD不能有''
    submit1.click()
    print 'wait sub_html'
    #等待加载子网页成功
    wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="Table1"]/tbody'))
    )
    print 'get compile and store html'
    get_one_page(browser)
    #返回原网页
    browser.back()
    return browser

def get_one_page(browser):
    html = browser.page_source
    pattern1 = re.compile('<div\sid="pnlResultSummary".*?class="mobilezoom">\n\s+(.*?)</span>',re.S)
    totalequity = re.findall(pattern1,html)  #股份总数
    for equity in totalequity:
        print(equity)
        equity = equity.replace(',','')
        print(type(equity))
        equity = int(equity)
        # print(type(equity))

    # 采用BeautifulSoup方法
    soup = BeautifulSoup(html, 'lxml')

    for element in soup.find("div", {"id":"pnlResultHeader"}).find_all("tbody"):
        i = 0
        for ele in element.find_all("tr"):
            if (i == 2):
                j = 0
                for e in ele.find("td").find("tbody").find("tr").find_all("td"):
                    if (j == 1): #日期
                        riqi = remove_space(e.text)
                        riqi = time.strptime(riqi, '%d/%m/%Y')
                        riqi = time.strftime("%Y-%m-%d", riqi)
                        # riqi = datetime.datetime(riqi[0]-riqi[1]-riqi[2])
                        # y,m,d = riqi[0:3]
                        # print(datetime.datetime(y,m,d))
                        print(riqi)
                        print(type(riqi))

                    j = j + 1
            elif (i == 4):
                j = 0
                for e in ele.find("td").find("tbody").find("tr").find_all("td"):
                    if (j == 1):#股票代码
                        code = remove_space(e.text)
                        print(code)
                    elif (j == 3):
                        stockname =  remove_space(e.text) #股票名称
                        print(stockname)
                    j = j + 1
            i = i + 1

    for element in soup.find("table", {"id":"participantShareholdingList"}).find_all("tbody"):
        i = 0
        k = 0
        for ele in element.find_all("tr"):
            if i > 2 and k <20:
                k = k + 1
                j = 0
                for e in ele.find_all("td"):
                    if (j == 0):#券商编号
                        num = remove_space(e.text)
                    elif (j == 1):#券商名字
                        participant = remove_space(e.text)
                    elif (j == 3):#持股量
                        volume = remove_space(e.text)
                        volume = volume.replace(',', '')
                        volume = int(volume)
                    elif (j == 4):#百分比
                        percent = float(remove_space(e.text).split('%')[0])/100.0
                    j = j + 1
                store(riqi, code, stockname, equity, num, participant, volume, percent)
                print(num+" "+ participant+ " "+ str(volume) + " "+ str(percent))
            else:
                if i <3:
                    i = i + 1
                else:
                    break




    # 为什么直接用浏览器获得的xpath都不是有效的呢
    # riqi = browser.find_element_by_xpath('//*[@id="Table5"]/tbody/tr[2]/td/table/tbody/tr/td[2]/text()')
    # print(riqi)
    # # code = browser.find_element_by_xpath('//*[@id="Table5"]/tbody/tr[3]/td/table/tbody/tr/td[2]/span/text()')
    # # print(code.text)
    # # stockname = browser.find_element_by_xpath('//*[@id="Table5"]/tbody/tr[3]/td/table/tbody/tr/td[4]/text()')
    # # print(stockname.text)


    #采用pyquery方法
    # doc = pq(html)
    # print(doc('#participantShareholdingList > tbody > tr:nth-child(4)'))
    # items = doc('# participantShareholdingList').items
    # print(items)
    # lib = items.find('tbody')
    # print(lib)
    # for item in items.items():
    #     texts = item.find('td')

    # participantShareholdingList > tbody > tr:nth-child(4) > td:nth-child(1)
    # participantShareholdingList > tbody > tr:nth-child(1)


    # elements = browser.find_elements_by_xpath('//*[@id="participantShareholdingList"]/tbody/tr/')
    # for element in elements:
    # #     # num2 = browser.find_element_by_xpath('//*[@id="participantShareholdingList"]/tbody/tr/td[1]')
    #     print(element.text)



def crawl_by_date(start_date, end_date, KEYWORD):
    browser = use_chrome_browser()

    for date in pd.date_range(start_date, end_date):  # 对目标的时间进行逐个迭代
        year, month, day = date.year, date.month, date.day
        print("Crawling Date {}-{}-{} Page...".format(year, month, day))

        browser = change_page_date(browser, year, month, day, KEYWORD)  # 将页面切换到目标日期页面
        time.sleep(1)

if __name__ == '__main__':

    from get_stock_code import stock_code
    stock_code_set = stock_code()

    for code in stock_code_set:
        try:
            crawl_by_date("2016-12-03", "2016-12-10", code)
        except:
            print 'error in this stock_code: '+code