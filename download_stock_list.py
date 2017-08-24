import csv

import requests
from pymongo import MongoClient
from io import StringIO
from bs4 import BeautifulSoup

client = MongoClient('localhost', 27017)
db = client['stock']
collectTWSE = db['twse_list']
collectOTC = db['otc_list']


def twse():
    res = requests.get('http://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y')
    data = res.content
    _de = data.decode('cp950', 'ignore')
    soup = BeautifulSoup(_de, "html5lib")

    stock_no = [tr.findAll('td')[2].text for tr in soup.findAll('tr')]
    stock_name = [tr.findAll('td')[3].text for tr in soup.findAll('tr')]
    category = [tr.findAll('td')[6].text for tr in soup.findAll('tr')]

    for index, item in enumerate(stock_no):
        if index > 0:
            data = {'stock_id': item, 'stock_name': stock_name[index], 'stock_category': category[index]}
            collectTWSE.insert_one(data)


def otc():
    res = requests.get(
        'http://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y')

    data = res.content
    _de = data.decode('cp950', 'ignore')
    soup = BeautifulSoup(_de, "html5lib")

    stock_no = [tr.findAll('td')[2].text for tr in soup.findAll('tr')]
    stock_name = [tr.findAll('td')[3].text for tr in soup.findAll('tr')]
    category = [tr.findAll('td')[6].text for tr in soup.findAll('tr')]

    for index, item in enumerate(stock_no):
        if index > 0:
            data = {'stock_id': item, 'stock_name': stock_name[index], 'stock_category': category[index]}
            collectOTC.insert_one(data)


twse()
otc()
