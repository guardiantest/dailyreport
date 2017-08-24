from operator import itemgetter

import requests
import csv

import asyncio
from dateutil.relativedelta import relativedelta
from settings import *
from pymongo import MongoClient
import json
from datetime import datetime

client = MongoClient('localhost', 27017)
db = client['stock']
collectStock = db['stock']
collectTWSE = db['twse_list']
dateTime = ''
tw_dateTime = ''
insert_json_array = []
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36"}

client = MongoClient('localhost', 27017)
db = client['stock']
collect = db['stock']


async def parse_twse(json_data):
    if json_data['stat'] == 'OK':
        data = json_data['data']
        count_data = len(data)
        for index, item in enumerate(data):
            ritem = [t.replace('--', '0').replace(',', '') for t in item]

            dates = str(ritem[0]).split('/')
            year = int(dates[0]) + 1911
            date = '{0}{1}{2}'.format(year, dates[1], dates[2])
            new_date = datetime.strptime(date + '00:00:00', '%Y%m%d%H:%M:%S')

            json_set = {'date': new_date,
                        'dealValue': float(ritem[1]),
                        'dealPrice': float(ritem[2]),
                        'openPrice': float(ritem[3]),
                        'highPrice': float(ritem[4]),
                        'lowPrice': float(ritem[5]),
                        'closePrice': float(ritem[6]),
                        'changePrice': ritem[7],
                        'dealCount': float(ritem[8]),
                        'buySell': 0.0,
                        'buyBrokerageCount': 0.0
                        }

            # json_set.update(fund_set)

            insert_json_array.append(json_set)


async def parse_one_twse(json_data, stock_no):
    if json_data['stat'] == 'OK':

        json_set_array = []
        twse = collect.find_one({'stockNo': stock_no})
        details = twse['details']
        details.sort(key=itemgetter('date'), reverse=False)
        db_date = details[-1]['date']

        data = json_data['data']
        for index, item in enumerate(data):

            ritem = [t.replace('--', '0').replace(',', '') for t in item]
            date_str = '{0:%Y%m%d}'.format(datetime.today())

            dates = str(ritem[0]).split('/')

            year = int(dates[0]) + 1911
            date = '{0}{1}{2}'.format(year, dates[1], dates[2])
            new_date = datetime.strptime(date + '00:00:00', '%Y%m%d%H:%M:%S')

            if new_date > db_date:
                json_set = {'date': new_date,
                            'dealValue': float(ritem[1]),
                            'dealPrice': float(ritem[2]),
                            'openPrice': float(ritem[3]),
                            'highPrice': float(ritem[4]),
                            'lowPrice': float(ritem[5]),
                            'closePrice': float(ritem[6]),
                            'changePrice': ritem[7],
                            'dealCount': float(ritem[8]),
                            'buySell': 0.0,
                            'buyBrokerageCount': 0.0
                            }
                json_set_array.append(json_set)

        return json_set_array


async def download_twse(stock_no, month=0):
    if month == 0:
        url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo={0}&date=20170608".format(stock_no)
        res = requests.post(url)
        try:
            d = json.loads(res.text)
            json_set_ary = await parse_one_twse(d, stock_no)
            if json_set_ary is not None:
                for dt in json_set_ary:
                    collectStock.update({"stockNo": stock_no},
                                        {'$push': {'details': dt}})
        except Exception as e:
            print("except no {0}".format(e))
    else:
        for m in range(month):
            new_date = datetime.today() - relativedelta(months=m)
            date_str = '{0:%Y%m%d}'.format(new_date)

            url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY?" \
                  "response=json&stockNo={0}&date={1}".format(stock_no, date_str)
            res = requests.post(url)

            try:
                d = json.loads(res.text)
                await parse_twse(d)
            except Exception as e:
                print("except no {0}".format(e))

        collectStock.find_and_modify(query={"stockNo": stock_no}, update={"$set": {'details': insert_json_array}})
        insert_json_array.clear()
        # collectStock.update({"stockNo": stock_no}, {"$push": {"details": insert_json_array}})


async def main():
    twse = collectTWSE.find()
    row_count = twse.count()

    for index, item in enumerate(twse):

        stock_no = item['stock_id']
        stock_name = item['stock_name']
        cr = collectStock.find({'stockNo': stock_no})
        if cr.count() == 0:
            stock_data = {
                'stockNo': stock_no,
                'stockName': stock_name
            }
            collectStock.insert_one(stock_data)

            await download_twse(stock_no, 6)
            print('insert {1}/{2} : {0} '.format(item, index, row_count))
        else:
            for items in cr:
                if 'details' in items:
                    d = items['details']
                    if len(d) == 0:
                        await download_twse(stock_no, 6)
                        print('insert {1}/{2} : {0} '.format(item, index, row_count))
                    else:
                        await download_twse(stock_no)
                        print('insert {1}/{2} : {0} -- details count : {3}'.format(item, index, row_count, len(d)))
                else:
                    await download_twse(stock_no)
                    print('insert {1}/{2} : {0} '.format(item, index, row_count))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
