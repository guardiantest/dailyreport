from operator import attrgetter, itemgetter
import numpy
import talib
from pymongo import MongoClient

import line_messageer
from strategy.bull_market import BullMarket
from strategy.force_sell import ForceSell
from strategy.foreign_investor_total import GoldKDJ
from strategy.main_force import MainForce
from strategy.strategy import Strategy
from strategy.value_avg_up import ValueUp
from strategy.value_concentrated import ValueConcentrated

client = MongoClient('localhost', 27017)
db = client['stock']
collect = db['stock']
collectTWSE = db['twse_list']
collectAnalysis = db['analysis']
analysisItems = []


def get_change_price(details):
    changePrice = []
    for detail in details:
        cp = detail['changePrice']
        if '+' in cp:
            cp = str(cp).replace('+', '▲ ')
        else:
            cp = '▼ ' + cp

        changePrice.append(cp)
    return changePrice


def get_date(details):
    date = []
    for detail in details:
        date_str = '{0:%Y/%m/%d}'.format(detail['date'])
        date.append(date_str)
    return date


def get_value(details):
    value = []
    for detail in details:
        try:
            v = float(detail['dealValue'])
        except Exception as e:
            print("except no {0}".format(e))
            v = 0.0
        value.append(v)
    nvalue = numpy.array(value)
    return nvalue


def get_price(details):
    price = []
    for detail in details:
        try:
            p = float(detail['closePrice'])
        except Exception as e:
            print("except no {0}".format(e))
            p = 0.0
        price.append(p)
    nprice = numpy.array(price)
    return nprice, price[-1]


def get_high_price(details):
    price = []
    for detail in details:
        try:
            p = float(detail['highPrice'])
        except Exception as e:
            print("except no {0}".format(e))
            p = 0.0
        price.append(p)
    nprice = numpy.array(price)
    return nprice


def get_low_price(details):
    price = []
    for detail in details:
        try:
            p = float(detail['lowPrice'])
        except Exception as e:
            print("except no {0}".format(e))
            p = 0.0
        price.append(p)
    nprice = numpy.array(price)
    return nprice


twse = collect.find()

for item in twse:

    stock = item['stockNo']
    name = item['stockName']
    details = item['details']
    details.sort(key=itemgetter('date'), reverse=False)

    price, close_price = get_price(details)
    high = get_high_price(details)
    low = get_low_price(details)
    values = get_value(details)
    date = get_date(details)
    change_price = get_change_price(details)

    strategy = []

    strategy.append(BullMarket(price, 5, 20, 60))
    strategy.append(ForceSell(details))
    strategy.append(GoldKDJ(details))
    strategy.append(ValueConcentrated(details, concentrated=1, percentage=15))
    count = 0
    for s in strategy:
        if s.run():
            count += 1
    if count == len(strategy):
        print('{0} - {1}'.format(name, stock))


# collectAnalysis.insert_one(analysis)


"""

post = collect.aggregate([
    {
        '$project': {
            "stockNo": 1,
            "stockName": 1,
            'details': {
                '$filter': {
                    'input': "$details",
                    'as': "item",
                    'cond': {'$and': [
                        {"$gt": ["$$item.buySell", 1]},
                        {"$lt": ["$$item.buyBrokerageCount", 0]},
                        {"$gt": ["$$item.investment_trust_total", 1]},
                    ]}
                }
            }
        }
    }
])


for p in post:
    details = p['details']
    stock = p['stockNo']
    if len(details) > 3:
        details.sort(key=itemgetter('date'), reverse=True)
        print(stock)
        print(len(details))

date = []
price = []
value = []
buySell = []
investment_trust_total = []
text = '投信 主力買'

post = collect.find()

for items in post:
    stock = items['stockNo']

    try:
        details = items['details']

        details.sort(key=itemgetter('date'), reverse=False)

        for detail in details:

            v = str(detail['dealValue']).replace(',', '')
            d = detail['date']
            date.append(detail['date'])
            buySell.append(detail['buySell'])
            if 'investment_trust_total' in detail:
                investment_trust_total.append(detail['investment_trust_total'])
            try:

                p = float(detail['closePrice'])
            except Exception as e:
                print("except no {0}".format(e))
                p = 0.0

            price.append(p)

        nprice = numpy.array(price)
        ndate = numpy.array(date)

        value = numpy.array(value)
        avg5 = talib.SMA(nprice, timeperiod=5)
        upper, middle, lower = talib.BBANDS(nprice, timeperiod=20, nbdevup=2.1, nbdevdn=2.1, matype=0)

        BBANDS = price[-1] >= upper[-1]

        new_price = price[-30:-1]
        last_price = price[-1]
        if BBANDS and last_price >= max(new_price):
            text += '\r\n {0}, price {1} upper {2} date{3}'.format(stock, price[-1], upper[-1], date[-1])

        price.clear()
        date.clear()
        price.clear()
        buySell.clear()
        investment_trust_total.clear()
    except Exception as e:
        print(stock)

line_messageer.send_message(text)
print(text)



    if 2 < len(d) < 4:
    close = []
    for v in d:
        close.append(v['closePrice'])

    diff = float(close[1]) - float(close[0])

    if diff > 0:
        if diff / float(close[0]) / diff < 1:
            print(s)
            print(v)
            text += '\r\n' + s
"""
