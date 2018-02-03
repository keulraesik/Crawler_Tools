# coding=utf8


import requests
import re
import json
import gc
import traceback

from pyquery import PyQuery as pq
from multiprocessing.dummy import Pool
from threading import Lock

"""
    [:title, :location, :salary, :job_desc, :skill_tags,
    :job_function, :industry, :experience, :career_level, :education]
"""

thread_num = 12
th_lock = Lock()
slice_num = 0
slice_size = 1000  # for VPS with small memory size
data_list = []


def parse_page(page_data, ga_channel):
    global slice_num
    global data_list
    job_list = pq(page_data)('.result-list-job')
    for job in job_list:
        pdata = pq(job)
        title = pdata('.job-title').text()
        loc = pdata('.job-desc-loc').text()
        salary = pdata('.job-desc-salary').text()
        experience = pdata('.job-desc-work-exp').text()
        each_job_title_url = pdata('input[name=each_job_title_url]').val()
        job_id = pdata('input[name=job_id]').val()
        if ga_channel == "ct" or ga_channel == "":
            url = 'https://www.ctgoodjobs.hk/job/'+each_job_title_url+'/'+job_id+'/preview'
        else:
            url = 'https://www.ctgoodjobs.hk/job/'+each_job_title_url+'/'+job_id+'-'+ga_channel+'/preview'
        job_detail_page = requests.get(url).content
        detail_pdata = pq(job_detail_page)
        job_desc = detail_pdata('.job-detail').text()
        skill_tags = detail_pdata('.skill-tag-blk').contents()
        job_function = [i.text_content() for i in
                        detail_pdata('.job-info table tbody tr:nth-child(3) td:nth-child(2) li')]
        industry = detail_pdata('.job-info table tbody tr:nth-child(4) td:nth-child(2)').text()
        career_level = detail_pdata('.job-info table tbody tr:nth-child(7) td:nth-child(2)').text()
        education = detail_pdata('.job-info table tbody tr:nth-child(8) td:nth-child(2)').text()

        with th_lock:
            data_list.append({
                'title': title, 'loc': loc, 'salary': salary, 'experience': experience,
                'job_desc': job_desc, 'skill_tags': skill_tags, 'job_function': job_function,
                'industry': industry, 'career_level': career_level, 'education': education
            })
            if len(data_list) % 50 == 0:
                print len(data_list) + slice_size * slice_num

            if len(data_list) == slice_size:
                with open('ctgoodjobs/ctgoodjobs-{}.json'.format(slice_num), 'wb') as f:
                    json.dump(data_list, f)
                slice_num += 1
                data_list = []
                gc.collect()


def page_job(job):
    try:
        job_list_url = 'https://www.ctgoodjobs.hk/english/search/joblist.asp'
        job_cate, page = job
        payload = {'sp_crit': job_cate, 'page': page}
        page_text = requests.get(job_list_url, params=payload).content
        parse_page(page_text, job_cate)
    except Exception:
        print traceback.print_exc()


def main():
    job_list_url = 'https://www.ctgoodjobs.hk/english/search/joblist.asp'
    job_cates = ['']
    last_page_num_regx = re.compile('page=(\d+)')

    for job_cate in job_cates:
        payload = {'sp_crit': job_cate, 'page': 1}
        first_page = requests.get(job_list_url, params=payload).content
        last_page_elem = pq(first_page)('.last-page')
        if last_page_elem:
            last_page_url = last_page_elem[0].attrib['href']
            last_page_num = int(last_page_num_regx.findall(last_page_url)[0])
            print 'total page num = {}'.format(last_page_num)
            parse_page(first_page, job_cate)
            if thread_num <= 1:
                for page in range(2, last_page_num + 1):
                    page_job((job_cate, page))
            else:
                pool = Pool(thread_num)
                pool.map(page_job, [(job_cate, page) for page in range(2, last_page_num + 1)])

    with open('ctgoodjobs/ctgoodjobs-{}.json'.format(slice_num), 'wb') as f:
        json.dump(data_list, f)


if __name__ == '__main__':
    main()

