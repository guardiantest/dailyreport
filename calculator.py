import talib
import numpy


class Calculator(object):
    def __init__(self, price):
        self._price = numpy.array(price)

    def MACD(self):
        macd, macdsignal, macdhist = talib.MACD(self._price, fastperiod=12, slowperiod=26, signalperiod=9)
        return macd, macdsignal, macdhist

    def BISA(self):
        BISA = self.check_moving_average_bias_ratio(self.moving_average_bias_ratio(5, 10)[0], True)[0]

    def BBANDSZip(self, upper, lower):
        """
        布林壓縮
        :return: 
        """
        oitems = self.__serial_price()
        items = self.__serial_price()[-20:]
        for index, item in enumerate(self.__serial_price()):
            bzip = upper[index] / lower[index]

    def BBANDS(self):
        """
        布林通道
        :return: upper, middle, lower
        """
        upper, middle, lower = talib.BBANDS(self._price, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
        return upper, middle, lower

    def KDJ(self):
        """
        KDJ 随机指标

        rsv = (CLOSE - LLV(LOW, N)) / (HHV(HIGH, N) - LLV(LOW, N)) * 100
        k = EMA(rsv, (M1 * 2 - 1))
        d = EMA(k, (M2 * 2 - 1))
        j = k * 3 - D * 2

        hhigh = history(30, '1d', 'high')[stock]
        hlow = history(30, '1d', 'low')[stock]
        hclose = history(30, '1d', 'close')[stock]
        """
        hhigh = max(self.data)
        hlow = min(self.data)
        hclose = max(self.data)
        slowk, slowd = talib.STOCH(hhigh.values,
                                   hlow.values,
                                   hclose.values,
                                   fastk_period=9,
                                   slowk_period=3,
                                   slowk_matype=0,
                                   slowd_period=3,
                                   slowd_matype=0)
        return slowk, slowd
