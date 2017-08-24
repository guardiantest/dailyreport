import csv
import os
from pymongo import MongoClient
import operator
from datetime import datetime

client = MongoClient('localhost', 27017)
db = client['stock']
collectReport = db['daily_report']
collectStock = db['stock']
folder = 'daily/TWSE'

for f in os.listdir(folder):
    stock_no = f.split('.')[0]
    result = {}
    if '.DS_Store' in f:
        continue
    dateTime = f
    folder_path = 'daily/TWSE/{0}'.format(f)
    for file in os.listdir(folder_path):
        stock_no = file.split('.')[0]
        if '.DS_Store' in file:
            continue
        with open(folder_path + '/{0}'.format(file)) as csv_file:
            csv_data = csv.reader(csv_file)
            data_list = []

            columnList = []
            for index, item in enumerate(csv_data):
                try:
                    if index < 3:
                        item = [value.strip().replace(',', '') for value in item]
                    else:
                        item = [value.strip().replace('\u3000', '') for value in item]
                        column1 = item[:5]
                        column2 = item[6:]
                        columnList.append(column1)
                        columnList.append(column2)

                except Exception as e:
                    print("except on {0}".format(e))
                    continue

            sellList = dict()
            buyList = dict()
            totalBuy = 0
            totalSell = 0
            for item in columnList:
                try:
                    if len(item) < 0:
                        continue
                    if item[0] == '':
                        continue
                    item = [value.strip().replace('\u3000', '') for value in item]
                    brokerageId = str(item[1])[:4]
                    brokerageName = str(item[1])[4:]
                    price = float(item[2])
                    buy = float(item[3])
                    sell = float(item[4])
                    totalBuy += buy
                    totalSell += sell

                    if buy > 0:
                        if brokerageId not in buyList:
                            buyList[brokerageId] = buy
                        else:
                            newBuy = buyList[brokerageId] + buy
                            buyList.update({brokerageId: newBuy})
                    if sell > 0:
                        if brokerageId not in sellList:
                            sellList[brokerageId] = sell
                        else:
                            newSell = sellList[brokerageId] + sell
                            sellList.update({brokerageId: newSell})

                    data = {
                        'brokerage': brokerageId + brokerageName,
                        'price': float(price),
                        'buy': float(buy),
                        'sell': float(sell)
                    }
                    data_list.append(data)
                except Exception as e:
                    print("stock_no : {0}  except {1}".format(stock_no, e))
                    continue

            buyBrokerageCount = len(buyList) - len(sellList)

            sortedBuyList = sorted(buyList.items(), key=operator.itemgetter(1), reverse=True)[:15]
            sortedSellList = sorted(sellList.items(), key=operator.itemgetter(1), reverse=True)[:15]

            totalBuy = 0
            for buy in sortedBuyList:
                totalBuy += buy[1]

            totalSell = 0
            for sell in sortedSellList:
                totalSell += sell[1]

            buySell = (totalBuy - totalSell)

            new_date = datetime.strptime(dateTime + '00:00:00', '%Y%m%d%H:%M:%S')

            jsonData = {'date': new_date, 'list': data_list}

            collectStock.update({"stockNo": stock_no, "details.date": new_date},
                                {'$set': {"details.$.buySell": buySell,
                                          "details.$.buyBrokerageCount": buyBrokerageCount}})
            print('insert : {0} {1}'.format(stock_no, new_date))
            columnList.clear()

            # stock_collect_date = collectReport.find({'stockNo': stock_no, 'details.date': new_date})
            # if stock_collect_date.count() == 0:
            # post_id = collectReport.update_one({"stockNo": stock_no}, {"$push": {"details": jsonData}}).upserted_id

