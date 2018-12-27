import pandas as pd
import pymysql
from pyecharts import Bar, Page, Grid

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

class OperateMySQL:
    def __init__(self, table_name):
        self.conn = pymysql.connect(user=dbuser, passwd=dbpass, db=dbname, host=dbhost, charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()
        self.table_name = table_name

    def create_table(self):
        sql   =    '''
                    CREATE TABLE `%s` (
                      `response_url` varchar(300) DEFAULT NULL,
                      `date` varchar(30) DEFAULT NULL,
                      `flag_id` int(11) DEFAULT NULL,
                      `market` varchar(30) DEFAULT NULL,
                      `rank` varchar(30) DEFAULT NULL,
                      `stock_code` varchar(30) DEFAULT NULL,
                      `stock_name` varchar(30) DEFAULT NULL,
                      `buy_turnover` varchar(30) DEFAULT NULL,
                      `sell_turnover` varchar(30) DEFAULT NULL,
                      `total_turnover` varchar(30) DEFAULT NULL,
                      `update_time` datetime DEFAULT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
                    ''' % self.table_name
        self.cursor.execute(sql)
        self.conn.commit()

    def get_top10_frequency(self):

        try:
            sql_query = 'SELECT market, stock_code, stock_name, count(stock_code) AS frequency  FROM  %s  WHERE stock_code<>"-" GROUP BY market, stock_code, stock_name' % self.table_name

            df = pd.read_sql(sql_query, con=self.conn)

            # self.conn.close()  # 关掉后会导致下一个sql执行报错


        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))

        return df

    def get_market(self):
        try:
            sql_query = 'SELECT DISTINCT market FROM  %s' % self.table_name

            df = pd.read_sql(sql_query, con=self.conn)

            # self.conn.close()  # 关掉后会导致下一个sql执行报错

        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))

        return df

    def get_start_date(self, market):
        sql = 'SELECT DISTINCT date FROM  %s  WHERE market="%s"  ORDER BY date ASC LIMIT 1' % (self.table_name,market)
        self.cursor.execute(sql)
        start_date = self.cursor.fetchone()
        start_date = start_date[0]
        return start_date


    def get_end_date(self, market):
        sql = 'SELECT DISTINCT date FROM  %s  WHERE market="%s"  ORDER BY date DESC LIMIT 1' % (self.table_name,market)
        self.cursor.execute(sql)
        end_date = self.cursor.fetchone()
        end_date = end_date[0]
        return end_date


if __name__=="__main__":

    # table_name = 'four_market_temp'
    # operate_mysql = OperateMySQL(table_name)
    # operate_mysql.create_table()

    table_name = 'four_market_version2'
    operate_mysql = OperateMySQL(table_name)
    df_top10_frequency = operate_mysql.get_top10_frequency()
    # print(df_top10_frequency)

    df_market_name = operate_mysql.get_market()
    market_list = list(df_market_name["market"].values)

    page = Page()

    for market in market_list:
        # SSE Northbound
        # SSE Southbound
        # SZSE Northbound
        # SZSE Southbound

        df = df_top10_frequency[df_top10_frequency["market"] == market]
        print(df)

        start_date = operate_mysql.get_start_date(market)
        end_date = operate_mysql.get_end_date(market)

        attr = list(df["stock_name"].values)
        v1 = list(df["frequency"].values)
        # v2 = [10, 25, 8, 60, 20, 80]
        bar = Bar("%s \n前十大成交活跃股频数统计\n %s至%s" % (market, start_date, end_date))
        bar.add(market, attr, v1, is_stack=True)
        # bar.add("商家B", attr, v2, is_stack=True)
        # bar.render('test.html')  # 生成一个html文件
        page.add(bar)

    page.render('陆港通前十大成交活跃股频数统计.html') # 生成一个html文件














