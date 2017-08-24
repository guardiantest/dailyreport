import csv
from pymongo import MongoClient

stock_list = []
client = MongoClient('localhost', 27017)
db = client['stock']
collectStock = db['stock']
dateTime = '20170519'
path = 'daily/TWSE/{0}'.format(dateTime)

with open('twse_list.csv') as csv_file:
    csv_data = csv.reader(csv_file)
    for i in csv_data:
        stock_list.append(i[0])

for stock in stock_list:
    path = 'history/TWSE/{0}'.format(stock + '.csv')
    with open(path) as csv_file:
        csv_data = csv.reader(csv_file)
        tolist = []
        for i in csv_data:
            cr = collectStock.find({'stock': i[0]})
            if cr.count() == 0:
                stockDetailData = [{
                    'date': dateTime,
                    'value': 0,
                    'macd': 0,
                    'kd': 0,
                    'rsi': 0,
                    'price': 0,
                    'high': 0,
                    'low': 0,
                    'buySell': buySell,
                    'buyBrokerageCount': buyBrokerageCount
                }]
                stockData = {
                    'stock': stock_no,
                    'details': stockDetailData
                }
                post_id = collectStock.insert_one(stockData).inserted_id


            i = [value.strip().replace(',', '') for value in i]
            try:
                for value in (1, 2, 3, 4, 5, 6, 8):
                    i[value] = float(i[value])
            except (IndexError, ValueError):
                pass
            tolist.append(i)

        for stock_info in tolist[2:]:
            dateAry = str(stock_info[0]).split('/')
            date = str(int(dateAry[0]) + 1911) + dateAry[1] + dateAry[2]
            dealValue = stock_info[1]
            dealPrice = stock_info[2]
            openPrice = stock_info[3]
            highPrice = stock_info[4]
            lowPrice = stock_info[5]
            closePrice = stock_info[6]
            changePrice = stock_info[7]
            dealCount = stock_info[8]
            collectStock.update({"stock": stock, "details.date": date},
                                {'$set': {"details.$.value": dealValue, "details.$.price": closePrice,
                                          "details.$.high": highPrice, "details.$.low": lowPrice}})
            print(stock)
