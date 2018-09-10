class DuplicateOrderError(Exception):
    def __init__(self, *args, order_id=None):
        super().__init__(*args)
        self.order_id = order_id


class InvalidOrderError(Exception):
    def __init__(self, *args, order_id=None):
        super().__init__(*args)
        self.order_id = order_id


class OrderDoesNotExistError(Exception):
    def __init__(self, *args, order_id=None):
        super().__init__(*args)
        self.order_id = order_id


class TradeNotMatchedError(Exception):
    def __init__(self, *args, price=None, quantity=None):
        super().__init__(*args)
        self.price = price
        self.quantity = quantity


class BestPriceButNoTradeError(Exception):
    pass


class InvalidMessageError(Exception):
    pass
