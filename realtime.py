import json
import time
import requests


class RealTime(object):
    def __init__(self, targets, max_stock_per_crawler=50):
        self.crawlers = []

        for index in range(0, len(targets), max_stock_per_crawler):
            crawler = Crawler(targets[index:index + max_stock_per_crawler])
            self.crawlers.append(crawler)

    def run(self):
        data = []
        for crawler in self.crawlers:
            data.extend(crawler.get_data())
        return data


class Crawler(object):
    '''Request to Market Information System'''

    def __init__(self, targets):
        endpoint = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp'
        # Add 1000 seconds for prevent time inaccuracy
        timestamp = int(time.time() * 1000 + 1000000)
        channels = '|'.join('tse_{}.tw'.format(target) for target in targets)
        self.query_url = '{}?_={}&ex_ch={}'.format(endpoint, timestamp, channels)

    def get_data(self):
        try:
            # Get original page to get session
            req = requests.session()
            req.get('http://mis.twse.com.tw/stock/index.jsp', headers={'Accept-Language': 'zh-TW'})

            response = req.get(self.query_url)
            content = json.loads(response.text)
        except Exception as err:
            print(err)
            data = []
        else:
            data = content['msgArray']

        return data


class Recorder(object):
    def record_to_csv(self, data):
        for row in data:
            print('\r\n')
            print('{1} : {0}'.format(row['n'], '名稱'))
            print('{1} : {0}'.format(row['c'], '代號'))
            print('{1} : {0}'.format(row['t'], '資料時間'))
            print('{1} : {0}'.format(row['z'], '最近成交價'))
            print('{1} : {0}'.format(row['tv'], '當盤成交量'))
            print('{1} : {0}'.format(row['fv'], '單量'))
            print('{1} : {0}'.format(row['v'], '當日累計成交量'))
            a = str(row['a']).split('_')[:-1]
            f = str(row['f']).split('_')[:-1]
            b = str(row['b']).split('_')[:-1]
            g = str(row['g']).split('_')[:-1]

            print('| 買進          賣出 '.format(b[0], g[0], a[0], b[0]))
            print('| {0} : {1}    {2} : {3} |'.format(b[0], g[0], a[0], b[0]))
            print('| {0} : {1}    {2} : {3} |'.format(b[1], g[1], a[1], b[1]))
            print('| {0} : {1}    {2} : {3} |'.format(b[2], g[2], a[2], b[2]))
            print('| {0} : {1}    {2} : {3} |'.format(b[3], g[3], a[3], b[3]))
            print('| {0} : {1}    {2} : {3} |'.format(b[4], g[4], a[4], b[4]))
            print('{1} : {0}'.format(a, '最佳五檔賣出價格'))
            print('{1} : {0}'.format(f, '最價五檔賣出數量'))
            print('{1} : {0}'.format(b, '最佳五檔買入價格'))
            print('{1} : {0}'.format(g, '最佳五檔買入數量'))


targets = []
targets.append('3346')
targets.append('2337')
while (True):
    try:
        real_time = RealTime(targets)
        data = real_time.run()
        r = Recorder()
        r.record_to_csv(data)
        time.sleep(5)
    except Exception as e:
        print(e)
