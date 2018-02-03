#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib2
import urllib
import requests
import datetime
# url = "http://www.iresearch.cn/include/ajax/user_ajax.ashx?work=idown&rid=3100"

def urllib_download_pdf_file(href_number,file_name,year):

    print "downloading " + file_name
    url = 'http://www.iresearch.cn/include/ajax/user_ajax.ashx?work=idown&rid=' + href_number
    file_path =  year+"/"+file_name+".pdf"
    u = urllib2.urlopen(url)
    f = open(file_path, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_path, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % \
                 (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status

    f.close()

class ProgressBar(object):

    def __init__(self, title,
                 count=0.0,
                 run_status=None,
                 fin_status=None,
                 total=100.0,
                 unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "【%s】%s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.status)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (self.title, self.status, self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        try:
            print self.__get_info()
            print end_str
        except Exception as e:
            print "print errors, not affect the result"

def requests_download_pdf_file(href_number,file_name,year):
    from contextlib import closing
    url = 'http://www.iresearch.cn/include/ajax/user_ajax.ashx?work=idown&rid=' + href_number
    with closing(requests.get(url, stream=True)) as response:
        chunk_size = 10240  # 单次请求最大值
        content_size = int(response.headers['content-length'])  # 内容体总大小
        progress = ProgressBar(file_name, total=content_size,
                               unit="KB", chunk_size=chunk_size, run_status="正在下载", fin_status="下载完成")
        with open(year+"/"+file_name+".pdf", "wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                progress.refresh(count=len(data))

def pdf_file(url,file_name,year):
    from contextlib import closing
    # print url
    # print file_name
    # file_name = url[-4:]
    # year = "2017"
    with closing(requests.get(url, stream=True)) as response:
        chunk_size = 10240  # 单次请求最大值
        content_size = int(response.headers['content-length'])  # 内容体总大小
        progress = ProgressBar(file_name, total=content_size,
                               unit="KB", chunk_size=chunk_size, run_status="正在下载", fin_status="下载完成")
        with open(year+"/"+file_name+".pdf", "wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                progress.refresh(count=len(data))

if __name__ == '__main__':
    # download_pdf_file(href_number = "3101",file_name = "3101",year = "2017")
    file_name = 'try'
    year = "2017"
    href_number = "2889"
    url = 'http://www.iresearch.cn/include/ajax/user_ajax.ashx?work=idown&rid=' + href_number
    # try:
    #     print "downloading " + file_name
    #
    #     url = 'http://www.iresearch.cn/include/ajax/user_ajax.ashx?work=idown&rid=' + href_number
    #     # url = 'http://www.iresearch.cn/include/ajax/user_ajax.ashx?work=idown&rid=3100'
    #     r = requests.get(url, verify=False)
    #     with open(href_number+".pdf", "wb") as code:
    #         code.write(r.content)
    # except Exception as e:
    #     print "errors in downloading " +year+" "+file_name
    start = datetime.datetime.now().replace(microsecond=0)
    requests_download_pdf_file(href_number, file_name, year)
    end = datetime.datetime.now().replace(microsecond=0)
    print "用时: "
    print(end - start)