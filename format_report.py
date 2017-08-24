import csv
import os

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
                    if index < 2:
                        item = [value.strip().replace(',', '') for value in item]
                    elif index == 2:
                        item = [value.strip().replace('\u3000', '').replace('券商', 'store').replace('價格', 'price').replace('買進股數', 'buy').replace(
                                '賣出股數', 'sell') for value in item]
                        column1 = item[1:5]
                        columnList.append(column1)
                    else:
                        item = [value.strip().replace('\u3000', '') for value in item]
                        column1 = item[1:5]
                        column2 = item[7:]
                        columnList.append(column1)
                        columnList.append(column2)

                except Exception as e:
                    print("except on {0}".format(e))
                    continue
            writer = csv.writer(open(folder_path + '/{0}'.format(file), 'w'))
            for row in columnList:
                writer.writerow(row)
