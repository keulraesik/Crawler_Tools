# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HkexItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    response_url = scrapy.Field()
    date = scrapy.Field() # 交易日期
    flag_id = scrapy.Field()  # 沪股通、沪港通、深股通、深港通的标示id
    market = scrapy.Field() # # 沪股通、沪港通、深股通、深港通的标示名称
    rank = scrapy.Field()  # 排名
    stock_code = scrapy.Field()   # 股票代码
    stock_name = scrapy.Field()  # 股票名称
    buy_turnover = scrapy.Field()  # 买入金额 RMB
    sell_turnover = scrapy.Field()   # 卖出金额 RMB
    total_turnover = scrapy.Field() # 买入及卖出金额 RMB

    '''
    response_url = scrapy.Field()
    flag_id = scrapy.Field()  # 沪股通、沪港通、深股通、深港通的标示id
    date = scrapy.Field()  # 交易日期
    market = scrapy.Field()  # # 沪股通、沪港通、深股通、深港通的标示名称
    data = scrapy.Field() # 1-10名的表格中的信息
    '''




