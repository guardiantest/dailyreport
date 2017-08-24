import csv
import os
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def mx_line(train_x, train_y):
    mx = LinearRegression()
    mx.fit(train_x, train_y)
    return mx


def pred():
    fs0 = 'tmp/3443_'
    x_train = pd.read_csv(fs0 + 'xtrain.csv')
    y_train = pd.read_csv(fs0 + 'ytrain.csv')
    x_test = pd.read_csv(fs0 + 'xtest.csv', index_col=False)
    y_test = pd.read_csv(fs0 + 'ytest.csv', index_col=False)

    xlst = ['xid', 'buy', 'sell']

    nx_train = x_train[xlst]
    nx_test = x_test[xlst]

    df9 = x_test.copy()
    mx = mx_line(nx_train.values, y_train.values)

    # x_test.index.name, y_test.index.name = 'xid', 'xid'

    y_pred = mx.predict(nx_test.values)

    df9['y_predsr'] = y_pred

    df9['y_test'], df9['y_pred'] = y_test, y_pred
    df9['y_pred'] = round(df9['y_predsr']).astype(int)
    print(df9)
    print(df9.tail())
    dacc = ai_acc_xed(df9, 1, False)
    print('mx:mx_sum,kok:{0:.2f}%'.format(dacc))


def file_path():
    df = pd.read_csv("tmp/file_path.csv")

    xlst, ysgn = ['store', 'buy', 'sell'], 'price'
    x, y = df[xlst], df[ysgn]
    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=1)
    g = x_train.groupby('store')

    index = g.tail().index.astype(int), g.tail()['store']
    index1 = index[1]

    for ii, i in enumerate(index1):
        x_train.loc[x_train['store'] == i, 'xid'] = ii
        print(ii)

    g = x_test.groupby('store')
    index = g.tail().index, g.tail()['store']

    for ii, i in enumerate(index[1]):
        x_test.loc[x_test['store'] == i, 'xid'] = ii
        print(ii)

    fs0 = 'tmp/3443_'
    x_train.to_csv(fs0 + 'xtrain.csv', index=False)
    x_test.to_csv(fs0 + 'xtest.csv', index=False)
    y_train.to_csv(fs0 + 'ytrain.csv', index=False, header=True)
    y_test.to_csv(fs0 + 'ytest.csv', index=False, header=True)


def formateFile():
    folder = 'daily/TWSE'

    columnList = []
    for f in os.listdir(folder):
        stock_no = f.split('.')[0]
        result = {}
        if '.DS_Store' in f:
            continue
        dateTime = f
        folder_path = 'daily/TWSE/{0}'.format(f)
        with open(folder_path + '/3443.csv') as csv_file:
            csv_data = csv.reader(csv_file)

            for index, item in enumerate(csv_data):
                try:
                    if index < 3:
                        continue
                    else:
                        item = [value.strip().replace('\u3000', '') for value in item]
                        column1 = item[1:5]
                        column2 = item[7:]

                        column1[0] = column1[0][:4]
                        column2[0] = column2[0][:4]

                        columnList.append(column1)
                        columnList.append(column2)

                except Exception as e:
                    print("except on {0}".format(e))
                    continue

    print(columnList)
    df = pd.DataFrame(columnList)
    df.to_csv("tmp/file_path.csv")


pred()
