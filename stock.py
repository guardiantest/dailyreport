

class Stock(object):
    def __init__(self):
        self._x = None
        self._price = 0
        self._brokerage = None

    @property
    def x(self):
        """I'm the 'x' property."""
        print("getter of x called")
        return self._x

    @x.setter
    def x(self, value):
        print("setter of x called")
        self._x = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def brokerage(self):
        return self._brokerage

    @brokerage.setter
    def brokerage(self, value):
        self._brokerage = value
