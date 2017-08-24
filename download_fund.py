import json
import os
from operator import itemgetter

import requests
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient
from datetime import datetime

stock_no_list = []

path = "fund/"
client = MongoClient('localhost', 27017)
db = client['stock']
collectStock = db['stock']
collectTWSE = db['twse_list']
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36"}

url4 = "http://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_download.php?l=zh-tw&d=20170522&se=EW&s=0,asc,0"
url2 = "http://www.twse.com.tw/ch/trading/exchange/MI_INDEX/MI_INDEX.php"
url3 = "http://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_download.php?l=zh-tw&se=EW&t=D&d=20170523&s=0,asc,0"

client = MongoClient('localhost', 27017)
db = client['stock']
collect = db['stock']


def download_fund(start, end):
    delta = end - start
    for d in range(delta.days):

        new_date = startDate + relativedelta(days=d)
        date_str = '{0:%Y%m%d}'.format(new_date)
        url = "http://www.twse.com.tw/fund/T86?response=json&date={0}&selectType=ALLBUT0999".format(date_str)
        res = requests.post(url, headers=headers)
        print('Start download date {0} file'.format(date_str))
        try:
            data = json.loads(res.text)
            parse(data)
        except Exception as e:
            print("except no {0}".format(e))


def parse(json_data):
    if json_data['stat'] == 'OK':
        date = json_data['date']
        data = json_data['data']

        total_count = len(data)
        for index, item in enumerate(data):
            item = [value.strip().replace(',', '').replace('"', '').replace('=', '').replace('--', '') for value in
                    item]

            new_date = datetime.strptime(date + '00:00:00', '%Y%m%d%H:%M:%S')
            stock_no = item[0]

            collectStock.update({"stockNo": stock_no, "details.date": new_date},
                                {'$set': {"details.$.foreign_investor_buy": int(item[2]),
                                          "details.$.foreign_investor_sell": int(item[3]),
                                          "details.$.foreign_investor_total": int(item[4]),
                                          "details.$.investment_trust_buy": int(item[5]),
                                          "details.$.investment_trust_sell": int(item[6]),
                                          "details.$.investment_trust_total": int(item[7]),
                                          "details.$.dealer_total": int(item[8]),
                                          "details.$.dealer_buy_self": int(item[9]),
                                          "details.$.dealer_sell_self": int(item[10]),
                                          "details.$.dealer_total_self": int(item[11]),
                                          "details.$.dealer_buy_hedge": int(item[12]),
                                          "details.$.dealer_sell_hedge": int(item[13]),
                                          "details.$.dealer_total_hedge": int(item[14]),
                                          'details.$.institutional_investors_total': int(item[15])}})
            print(' {0}/{1}   {2} : '.format(index, total_count, item))
    else:
        print(json_data['stat'])


date_format = "%m/%d/%Y"
startDate = datetime.strptime('6/12/2017', date_format)
endDate = datetime.today()
download_fund(startDate, endDate)
