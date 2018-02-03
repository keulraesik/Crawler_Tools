# coding=utf8


import requests
import json
import math
import traceback

from pyquery import PyQuery as pq
from multiprocessing.dummy import Pool
from threading import Lock

"""
    [:title, :location, :salary, :job_desc,:job_function,:industry,:career_level,:qualification,:exp]
"""

thread_num = 12
th_lock = Lock()
slice_num = 0
slice_size = 1000  # for VPS with small memory size
data_list = []


def parse_page(page_data):
    global slice_num
    global data_list
    job_list = pq(page_data)('#JobListingSection .result-sherlock-cell')
    for job in job_list:
        pdata = pq(job)
        title = pdata('.job-title').text()
        location = pdata('.job-location').text()
        url = pdata('.job-title .posLink').attr('href')
        salary = pdata('.job-quickinfo-salary').text()
        job_detail_page = requests.get(url).content
        detail_pdata = pq(job_detail_page)
        job_desc = detail_pdata('.jobad-primary-details').text()
        exp = detail_pdata('.jobad-primary-meta .meta-exp .meta-item').text()
        job_function1 = detail_pdata('.jobad-primary-meta .meta-jobfunction a:even').contents()
        job_function2 = detail_pdata('.jobad-primary-meta .meta-jobfunction a:odd').contents()
        job_function = [i + ' > ' + j for i, j in zip(job_function1, job_function2)]
        industry = detail_pdata('.jobad-primary-meta .meta-industry .meta-link').text()
        career_level = detail_pdata('.jobad-primary-meta .meta-lv .meta-item').text()
        qualification = detail_pdata('.jobad-primary-meta .meta-edu .meta-item').text()

        with th_lock:
            data_list.append({
                'title': title, 'location': location, 'salary': salary, 'job_desc': job_desc,
                'job_function': job_function, 'exp': exp, 'industry': industry,
                'career_level': career_level, 'qualification': qualification
            })
            if len(data_list) % 50 == 0:
                print len(data_list) + slice_size * slice_num

            if len(data_list) == slice_size:
                with open('jobsdb/jobsdb-{}.json'.format(slice_num), 'wb') as f:
                    json.dump(data_list, f)
                slice_num += 1
                data_list = []


def page_job(page):
    try:
        job_list_url = 'https://hk.jobsdb.com/hk/jobs/full-time-employment'
        payload = {'page': page}
        page_text = requests.get(job_list_url, params=payload).content
        parse_page(page_text)
    except Exception:
        print traceback.print_exc()


def main():
    job_list_url = 'https://hk.jobsdb.com/hk/jobs/full-time-employment'
    first_page = requests.get(job_list_url).content
    pdata = pq(first_page)
    total_jobs = int(pdata('#firstLineCriteriaContainer em').text())
    total_pages = int(math.ceil(total_jobs / len(pdata('#JobListingSection .result-sherlock-cell'))))
    print 'total page num = {}'.format(total_pages)
    parse_page(first_page)
    if thread_num <= 1:
        for page in range(2, total_pages + 1):
            page_job(page)
    else:
        pool = Pool(thread_num)
        pool.map(page_job, range(2, total_pages + 1))

    with open('jobsdb/jobsdb-{}.json'.format(slice_num), 'wb') as f:
        json.dump(data_list, f)


if __name__ == '__main__':
    main()

