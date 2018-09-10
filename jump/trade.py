class Trade(object):
    def __init__(self, price=None, quantity=None):
        super().__init__()
        self.price = price
        self.quantity = quantity