import asyncio
import datetime
import uuid

import cv2
import numpy as np
import os
import urllib
import requests
import time
import csv
from bs4 import BeautifulSoup
import logging

from pymongo import MongoClient

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

reqbsWelcome = requests.get('http://bsr.twse.com.tw/bshtm/bsWelcome.aspx')
soupWelcome = BeautifulSoup(reqbsWelcome.content, "html5lib")
s = soupWelcome.find("span", {'id': 'Label_Date'})
date = str(s.string).replace('/', '')
path = 'daily/TWSE/{0}'.format(date)
sleep_time = 0.8
date = datetime.datetime.now().strftime("%Y%m%d")

loop = asyncio.get_event_loop()
dropList = []


async def get_html_data():
    req = requests.Request('GET', 'http://bsr.twse.com.tw/bshtm/bsMenu.aspx')
    s = requests.Session()
    prepare = req.prepare()
    response = s.send(prepare)
    if response.status_code != 200:
        await get_html_data()

    cookieString = None
    for co in response.cookies:
        cookieString = co.value
    soup = BeautifulSoup(response.content, "html5lib")

    viewState = urllib.parse.quote_plus(soup.find("input", {"id": "__VIEWSTATE"})['value'])
    eventValidation = urllib.parse.quote_plus(soup.find("input", {"id": "__EVENTVALIDATION"})['value'])
    imgs = soup.findAll("img")
    imagePath = None
    for img in imgs:
        if img['src'].find("CaptchaImage") != -1:
            imagePath = "http://bsr.twse.com.tw/bshtm/{0}".format(img['src'])
    urllib.request.urlretrieve(imagePath, "tmp/CaptchaImage.jpg")
    return viewState, eventValidation, cookieString, date


def mse(img1, img2):
    try:
        type1 = img1.astype("float")
        type2 = img2.astype("float")
        err = np.sum((type1 - type2) ** 2)
        err /= float(img1.shape[0] * img1.shape[1])
        return err
    except Exception as e:
        return 999999999999
        print("except no {0}".format(e))


def get_number(pic):
    ary = []
    png_ary = []

    for png in os.listdir('alphabet'):
        if png != '.DS_Store':
            png_ary.append(png)
            ref = cv2.imread("alphabet/" + png)
            m = mse(ref, pic)
            ary.append(m)
    min_index = ary.index(min(ary))
    return png_ary[min_index]


def remove_all_png():
    for png in os.listdir('tmp'):
        os.unlink("tmp/{0}".format(png))


def create_captcha_image():
    img = cv2.imread('tmp/CaptchaImage.jpg', 0)
    kernel = np.ones((4, 4), np.uint8)

    erosion = cv2.erode(img, kernel, iterations=1)

    blurred = cv2.GaussianBlur(erosion, (5, 5), 0)

    edged = cv2.Canny(blurred, 30, 150)

    dilation = cv2.dilate(edged, kernel, iterations=1)

    image, contours, hierarchy = cv2.findContours(dilation.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted([(c, cv2.boundingRect(c)[0]) for c in contours], key=lambda x: x[1])
    ary = []

    for (c, _) in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        if w > 15 and h > 15:
            ary.append((x, y, w, h))

    # fig = plt.figure()
    for i, (x, y, w, h) in enumerate(ary):
        roi = dilation[y:y + h, x:x + w]
        thresh = roi.copy()
        # fig.add_subplot(5, len(ary), i + 1)
        # plt.imshow(thresh)
        res = cv2.resize(thresh, (50, 50))
        cv2.imwrite("tmp/%d.png" % i, res)

    # plt.show()
    code = ""
    for png in os.listdir('tmp'):
        if png != "CaptchaImage.jpg":
            pic = cv2.imread("tmp/{0}".format(png))
            imgName = get_number(pic)
            text = imgName.split(".")[0]
            code += text
    return code
    # erosion = cv2.erode(img, kernel, iterations=1)
    # blurred = cv2.GaussianBlur(erosion, (5, 5), 0)
    # edged = cv2.Canny(blurred, 30, 150)
    # dilation = cv2.dilate(edged, kernel, iterations=1)


def save_error_code_image(code):
    if len(code) == 5:
        move_path = "error/%s" % str(uuid.uuid4())
        os.makedirs(move_path)
        for png in os.listdir('tmp'):
            img = cv2.imread('tmp/{0}'.format(png), 0)
            if png == 'CaptchaImage.jpg':
                png = code + '.png'
            cv2.imwrite(move_path + '/' + png, img)

async def error_code(stock_no, retry_count, code):
    if retry_count < 10:

        #if len(code) == 5:
            #save_error_code_image(code)

        print('驗證碼錯誤 code : {0}'.format(code))
        time.sleep(sleep_time)
        retry_count += 1
        await download_report(stock_no, retry_count)
    else:
        dropList.append(stock_no)
        print('drop stock no : {0}'.format(stock_no))


async def html_error(stock_no, retry_count):
    try:
        print('content error stock : {0}'.format(stock_no))
        time.sleep(sleep_time)
        retry_count += 1
        await download_report(stock_no, retry_count)
    except Exception as e:
        print("except no htmlError {0}".format(e))


async def store_file(stock_no, code, text):
    try:
        csv_files = csv.reader(StringIO(text))
        file_path = path + '/{0}.csv'.format(stock_no)
        f = open(file_path, "w")
        w = csv.writer(f)
        w.writerows(csv_files)
        f.close()
        print('{0} 下載完成，驗證碼為 : {1}'.format(stock_no, code))
    except Exception as e:
        dropList.append(stock_no)
        print("except no storeFile {0}".format(e))


async def download_report(stock_no, retry_count=0):
    remove_all_png()
    view_state, event_validation, cookie_string, dateTime = await get_html_data()

    code = create_captcha_image()
    if len(code) != 5:
        time.sleep(sleep_time)
        await download_report(stock_no, retry_count)
    else:
        post_data = "__EVENTTARGET=" \
                      "&__EVENTARGUMENT=" \
                      "&__LASTFOCUS=" \
                      "&__VIEWSTATE={0}" \
                      "&__EVENTVALIDATION={1}" \
                      "&RadioButton_Normal=RadioButton_Normal" \
                      "&TextBox_Stkno={2}" \
                      "&CaptchaControl1={3}" \
                      "&btnOK=%E6%9F%A5%E8%A9%A2".format(view_state, event_validation, stock_no, code)

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:53.0) Gecko/20100101 Firefox/53.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Cookie': 'ASP.NET_SessionId={0}'.format(cookie_string),
                   'Host': 'bsr.twse.com.tw',
                   'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Accept-Encoding': 'gzip, deflate',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post('http://bsr.twse.com.tw/bshtm/bsMenu.aspx', data=post_data, headers=headers)
        content = response.text

        if 'HyperLink_DownloadCSV' in content:
            data = requests.post('http://bsr.twse.com.tw/bshtm/bsContent.aspx', data=post_data, headers=headers)
            if '券商買賣股票成交價量資訊' not in data.text:
                await html_error(stock_no, retry_count)
            else:
                text = data.text
                await store_file(stock_no, code, text)
        elif '驗證碼錯誤' in content:
            await error_code(stock_no, retry_count, code)
        elif '查無資料' in content:
            print('查無資料 : {0}'.format(stock_no))
        else:
            if retry_count < 5:
                logging.warning('HTTP error')
                time.sleep(sleep_time)
                retry_count += 1
                await download_report(stock_no)
            else:
                dropList.append(stock_no)



client = MongoClient('localhost', 27017)
db = client['stock']
collectTWSE = db['twse_list']

async def main():
    if not os.path.exists(path):
        os.makedirs(path)

    file_list = []
    stock_no_list = []

    for file in os.listdir(path):
        if '.DS_Store' not in file:
            file_list.append(file)

    stocks = collectTWSE.find()

    for item in stocks:
        stock = '{0}.csv'.format(item['stock_id'])
        if stock not in file_list:
            stock_no_list.append(item['stock_id'])

    totalCount = len(stock_no_list)

    for index, item in enumerate(stock_no_list):
        try:
            print("\r\nStart download {0} ".format(item))
            await download_report(item)
            time.sleep(sleep_time)
            print("Processing {0} / {1}".format(index + 1, totalCount))

        except Exception as e:
            print("except on {0}".format(e))
            dropList.append(item)
            continue

    if len(dropList) > 0:
        print('\r\n \r\ndownload dropList')
        print(dropList)
        dropList.clear()


loop.run_until_complete(main())
