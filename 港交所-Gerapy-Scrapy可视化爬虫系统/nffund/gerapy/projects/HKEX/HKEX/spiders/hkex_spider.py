import scrapy
import json
from datetime import datetime, timedelta, date
from HKEX.items import HkexItem


class MySpider(scrapy.Spider):

    name = 'HKEX'

    # allowed_domains = ['sc.hkex.com.hk']

    # start_urls = []
    date = datetime(2017, 1, 1)

    base_url = 'https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/chi/csm/DailyStat/data_tab_daily_%sc.js'

    def start_requests(self):  # 默认的开始函数，用于提供要爬取的链接
        # 'https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/chi/csm/DailyStat/data_tab_daily_%sc.js' % 20181211
        # url = self.base_url % self.num

        while self.date < datetime.now():  # 自己控制下时间范围
            self.date += timedelta(days=1)
            yield scrapy.Request(url=self.base_url % self.date.strftime('%Y%m%d'),
                                # headers=self.headers,
                                 callback=self.parse)

    def parse(self, response):  # 默认的回调函数，用于链接下载完毕后调用来处理数据
        self.logger.info('A response from %s just arrived!, status is %s', response.url, response.status)

        hkex_item = HkexItem()

        json_str = response.text.split('=')[1]

        json_object = json.loads(json_str)

        for item in json_object:
            flag_id, date, market, data = self.deal_single_json(text=item,response=response)

            hkex_item['response_url'] = str(response.url)
            hkex_item['flag_id'] = str(flag_id)
            hkex_item['date'] = str(date)
            hkex_item['market'] = str(market)
            hkex_item['data'] = str(data)
            self.logger.info("!!!!! data is %s",  hkex_item['data'])

            yield hkex_item



    # def assemble_items(self,json_object,response):
    #
    #     for item in json_object:
    #         flag_id, date, market, rank, stock_code, stock_name, buy_turnover, sell_turnover, total_turnove = self.deal_response_text(text=item,response=response)

    def deal_single_json(self,text,response):
        self.logger.info('begin to deal reponse.text from %s', response.url)

        json_1 = text

        flag_id = json_1['id']
        date = json_1['date']
        market = json_1['market']
        top10_table = ''
        if json_1['content'][0]['style'] == 2 or json_1['content'][0]['style'] == "2":
            top10_table = json_1['content'][0]['table']
        if json_1['content'][1]['style'] == 2 or json_1['content'][1]['style'] == "2":
            top10_table = json_1['content'][1]['table']

        top10_table_tr = top10_table['tr']

        top10_list = []

        for td in top10_table_tr:
            row = td['td'][0]
            # print(td['td'][0])

            rank, stock_code, stock_name, buy_turnover, sell_turnover, total_turnover = row
            stock_name = stock_name.replace(" ", "").replace("\t", "").strip()
            top10_list.append([flag_id, date, market, rank, stock_code, stock_name, buy_turnover, sell_turnover, total_turnover])

        return str(flag_id), str(date), str(market), str(top10_list)


