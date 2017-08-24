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

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def get_html_data():
    req = requests.Request('GET', 'http://www.tpex.org.tw/web/stock/aftertrading/broker_trading/brokerBS.php?l=zh-tw')
    s = requests.Session()
    prepare = req.prepare()
    response = s.send(prepare)

    cookieString = None
    for co in response.cookies:
        cookieString = co.value
    soup = BeautifulSoup(response.content, "html5lib")
    imgs = soup.findAll("img")
    imagePath = None
    for img in imgs:
        if img['alt'].find("驗證碼") != -1:
            imagePath = "http://www.tpex.org.tw/{0}".format(img['src'])
    urllib.request.urlretrieve(imagePath, "tmp/CaptchaImage.jpg")
    create_captcha_image()


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


get_html_data()
