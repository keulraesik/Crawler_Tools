# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import datetime

DEBUG = True

if DEBUG:
    dbuser = 'root'
    dbpass = 'zjz4818774'
    dbname = 'HKEX'
    dbhost = '127.0.0.1'
    dbport = '3306'
else:
    dbuser = 'root'
    dbpass = 'zjz4818774'
    dbname = 'HKEX'
    dbhost = 'localhost'
    dbport = '3306'


class HkexPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(user=dbuser, passwd=dbpass, db=dbname, host=dbhost, charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        #清空表：
        self.cursor.execute("truncate table four_market_version2;")
        self.conn.commit()

    def process_item(self, item, spider):

        current_time = datetime.datetime.now()

        try:

            self.cursor.execute("""INSERT INTO four_market_version2 (response_url, date, flag_id, market, 
                                                                     rank, stock_code, stock_name, 
                                                                     buy_turnover, sell_turnover, total_turnover, 
                                                                     update_time)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
                                item['response_url'].encode('utf-8'),
                                item['date'].encode('utf-8'),
                                item['flag_id'].encode('utf-8'),
                                item['market'].encode('utf-8'),
                                item['rank'].encode('utf-8'),
                                item['stock_code'].encode('utf-8'),
                                item['stock_name'].encode('utf-8'),
                                item['buy_turnover'].encode('utf-8'),
                                item['sell_turnover'].encode('utf-8'),
                                item['total_turnover'].encode('utf-8'),
                                current_time,
                            )
            )
            self.conn.commit()

            # 不能关闭，不然会报错
            # self.cursor.close()
            # self.conn.close()

        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))

        return item