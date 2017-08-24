import datetime
import cv2
import csv
import os
import sys
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['stock']
collectStock = db['stock']

stock_no_list = []


def parse(date):
    path = 'fund/TWSE/{0}'.format(date)
    with open(path + '.csv') as csv_file:
        try:
            csv_data = csv.reader(csv_file)
            for index, item in enumerate(csv_data):
                if index == 0:
                    tw_date = str(item[0]).split('\u3000')[0]
                    year = int(tw_date.split('年')[0]) + 1911
                    month = tw_date.split('月')[0][-2:]
                    day = tw_date.split('日')[0][-2:]
                    dateTime = '{0}{1}{2}'.format(year, month, day)
                if index > 1:
                    """
                    <class 'list'>: ['證券代號', '證券名稱', '外資買進股數', '外資賣出股數', '外資買賣超股數', '投信買進股數', '投信賣出股數', '投信買賣超股數', '自營商買賣超股數', '自營商買進股數(自行買賣)', '自營商賣出股數(自行買賣)', '自營商買賣超股數(自行買賣)', '自營商買進股數(避險)', '自營商賣出股數(避險)', '自營商買賣超股數(避險)', '三大法人買賣超股數']
                    """
                    item = [value.strip().replace(',', '').replace('"', '').replace('=', '') for value in item]
                    storeList = item[:2]
                    stock_no_list.append(storeList)
                    stock_no = item[0]
                    foreign_investor_buy = int(item[2])
                    foreign_investor_sell = int(item[4])
                    foreign_investor_total = int(item[5])
                    investment_trust_buy = int(item[6])
                    investment_trust_sell = int(item[7])
                    investment_trust_total = int(item[8])
                    dealer_total = int(item[9])
                    dealer_buy_self = int(item[10])
                    dealer_sell_self = int(item[11])
                    dealer_total_self = int(item[12])
                    dealer_buy_hedge = int(item[13])
                    dealer_sell_hedge = int(item[14])
                    dealer_total_hedge = int(item[15])

                    collectStock.update({"stock": stock_no, "details.date": dateTime},
                                        {'$set': {"details.$.foreign_investor_buy": foreign_investor_buy,
                                                  "details.$.foreign_investor_sell": foreign_investor_sell,
                                                  "details.$.foreign_investor_total": foreign_investor_total,
                                                  "details.$.investment_trust_buy": investment_trust_buy,
                                                  "details.$.investment_trust_sell": investment_trust_sell,
                                                  "details.$.investment_trust_total": investment_trust_total,
                                                  "details.$.dealer_total": dealer_total,
                                                  "details.$.dealer_buy_self": dealer_buy_self,
                                                  "details.$.dealer_sell_self": dealer_sell_self,
                                                  "details.$.dealer_total_self": dealer_total_self,
                                                  "details.$.dealer_buy_hedge": dealer_buy_hedge,
                                                  "details.$.dealer_sell_hedge": dealer_sell_hedge,
                                                  "details.$.dealer_total_hedge": dealer_total_hedge}})

                    print(item)
        except Exception as e:
            print(e)


for file in os.listdir('fund/TWSE'):
    if file != '.DS_Store':
        dateTime = file.split('.')[0]
        parse(dateTime)
