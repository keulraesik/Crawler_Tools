#coding=utf-8
import sys
import requests
from bs4 import BeautifulSoup
import json

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
        print(path+' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path+' 目录已存在')
        return False

def download_html(url):
    try:
        page = requests.get(url)
        page.encoding = page.apparent_encoding
        html = page.text
    except Exception as e:
        print('Error fetching price data from ' + url)
        if hasattr(e, 'message'):
            print("Error message: " + e.message)
        else:
            print(e)
            sys.exit(1)

    return html

def extract_job_url(html):
    job_url_list_in_page = []
    soup = BeautifulSoup(html, 'html.parser')
    all_label = soup.find_all("label","job_title")

    for label_item in all_label:

        job_url_list_in_page.append((label_item.select('a')[0])['href'])

        # file_name_list.append(div_item.get_text("|", strip=True))
    # file_href_number_list = [(href[8:])[:-5] for href in file_href_list]

    return job_url_list_in_page

def extract_job_details(html,url,f):
    title = ""
    location = ""
    education =""
    industry = ""
    job_function = ""
    post_specification = ""
    soup = BeautifulSoup(html, 'html.parser')

    if soup.find("div","job_title") != None:
        title = soup.find("div","job_title").get_text(strip=True)
        title = str(title)
    else:
        title = ""
    # print(title)
    if soup.find("span", {"itemprop":"addressLocality"}) != None:
        location = soup.find("span", {"itemprop":"addressLocality"}).get_text(strip=True)
        location = str(location)
    else:
        location = ""
    # print(location)
    if soup.find("td",{"itemprop":"educationRequirements"}) != None:
        education =  soup.find("td",{"itemprop":"educationRequirements"}).get_text(strip=True)
        education = str(education)
    else:
        education = ""
    # print(education)
    if  soup.find("td",{"itemprop":"industry"}) != None:
        industry = soup.find("td", {"itemprop": "industry"}).get_text(strip=True)
        industry = str(industry)
    else:
        industry = ""
    # print(industry)
    if  soup.find("th",text="Job function") != None:
        job_function_td = soup.find("th", text="Job function").find_next("td")
        if job_function_td != None:
            job_function = job_function_td.get_text(strip=True)
            job_function = str(job_function)
    else:
        job_function = ""
    # print(job_function)

    if  soup.find("div", "desc") != None:
        post_specification = str(soup.find("div", "desc"))
    else:
        post_specification = ""
    # print(post_specification)
    current_url = url
    # print(current_url)
    save(f, title, location, education, industry, job_function, post_specification, current_url)

def save(f, title, location, education, industry, job_function, post_specification, current_url):
    d = {"title":title, "location":location, "education":education, "industry":industry, "job_function":job_function, "post_specification":post_specification,"current_url":current_url}
    j = json.dumps(d, indent=4)
    print(j + ',', file=f)


def generate_url_in_page(page):
    job_url_list = []
    page_url = "https://www.cpjobs.com/hk/SearchJobs#employment=1&page=" + str(page)
    print(page_url)
    page_html = download_html(page_url)
    job_url_list_in_page = extract_job_url(page_html)

    job_url_list_in_page = [ "https://www.cpjobs.com" + str(job_url)  for job_url in job_url_list_in_page]
    # / hk / job / assistant - key - account - manager - fmcg - brand - principal - 2065940
    # url = "https://www.cpjobs.com" + str(job_url)
    return job_url_list_in_page

def generate_url_all():
    job_url_list_all = []
    for i in range(1,883):
        job_url_list_in_page = generate_url_in_page(i)
        job_url_list_all += job_url_list_in_page

    return job_url_list_all

def download_store_data_by_job_url_list_all(job_url_list_all):

    for i in range(len(job_url_list_all)):
        try:
            f = open('json_data/'+str(i)+'.json', 'w')
            print('[', file=f)
            url = job_url_list_all[i]
            html = download_html(url)
            extract_job_details(html,url,f)
            print(']', file=f)
            f.close()
        except Exception as e:
            print("error in store data in "+str(url))
        try:
            print(" has finished " + str(i * 100.0 / len(job_url_list_all)) + "%")
            print ("complete to download " + url)
        except Exception as e:
            print("print errors, not affect the result")


def main():

    #创建文件夹
    mkdir("json_data")

    job_url_list_all = generate_url_all()
    print(job_url_list_all)
    download_store_data_by_job_url_list_all(job_url_list_all)

if __name__ == '__main__':
    main()

    # url = "https://www.cpjobs.com/hk/job/ui-engineer-%E5%B7%A5%E7%A8%8B%E5%B8%88-2045459"
    # html = download_html(url)
    # f = open('sample.json', 'w')
    # extract_job_details(html, url, f)

    # page = 1
    # job_url_list_in_page = generate_url_in_page(page)
    # print(job_url_list_in_page)