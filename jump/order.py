from datetime import datetime


class Order(object):
    BUY_SIDE = 'B'
    SELL_SIDE = 'S'
    ACTION_ADD = 'A'
    ACTION_MODIFY = 'M'
    ACTION_REMOVE = 'X'

    def __init__(self, id=None, side=None, price=None, quantity=None, action=None):
        self.id = id
        self.side = side
        self.price = price
        self.quantity = quantity
        self.action = action
        self.order_datetime = datetime.utcnow()

    def validate(self):
        if not self.id:
            return False
        if not self.side:
            return False
        if not self.price or self.price < 0:
            return False
        if not self.quantity:
            return False

        return True

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return "Id: {}, Side: {}, Price: {}, Quantity: {}, Action: {}".format(self.id, self.side, self.price,
                                                                              self.quantity, self.action)
