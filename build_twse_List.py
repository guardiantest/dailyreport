import csv
from io import StringIO

path = 'fund/TWSE/20170520.csv'

with open(path) as csv_file:
    csv_data = csv.reader(csv_file)
    items = []
    for i, t in enumerate(csv_data):
        if i > 1:
            try:
                stockNo = str(t[:2][0])
                stockName = str(t[:2][1])
                deStock = stockNo.replace('=', '').replace('"', '')
                deName = stockName.replace(' ', '')
                data = (deStock, deName)
                print(data)
                items.append(data)
            except Exception as e:
                print("except no {0}".format(e))

    f = open('twse_list.csv', "w")
    w = csv.writer(f)
    w.writerows((tuple(items)))
    f.close()
