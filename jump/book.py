from collections import Iterable
from heapq import heappop, heappush, heapify
from typing import Dict, List, IO

from jump.error import *
from jump.order import Order
from jump.trade import Trade


class Book(object):
    def __init__(self, file: IO = None):
        super().__init__()
        self.file = file
        self.trades: Dict[float, List[Trade]] = {}
        self.orders: Dict[int, Order] = {}
        # Keep an index of order ids based on price for fast lookup
        self.price_index: Dict[str, List[int]] = {}
        # these lists are used as stacks so we know the best prices at any given time
        self.best_buy = []
        self.best_sell = []
        self.expected_trade_count = 0
        self.total_quantity = 0
        self.last_trade_price = None
        self.buy_prices = []
        self.sell_prices = []

    def add_order(self, order: Order):
        if not order.validate():
            raise InvalidOrderError('Invalid order, missing or invalid data', order_id=order.id)
        elif order.id in self.orders:
            raise DuplicateOrderError('Duplicate order', order_id=order.id)

        self.orders[order.id] = order
        key = self.price_index_key(order.price, order.side)
        self.price_index[key] = self.price_index[key] if key in self.price_index else []
        self.price_index[key].append(order.id)
        self.update_best(order)
        self.add_price(order)

    def add_price(self, order):
        if order.side == Order.BUY_SIDE and order.price not in self.buy_prices:
            heappush(self.buy_prices, order.price)
        if order.side == Order.SELL_SIDE and order.price not in self.sell_prices:
            heappush(self.sell_prices, order.price)

    def add_price_old(self, order):
        if order.side == Order.BUY_SIDE and order.price not in self.buy_prices:
            self.buy_prices.append(order.price)
            self.buy_prices = sorted(self.buy_prices, reverse=True)
        if order.side == Order.SELL_SIDE and order.price not in self.sell_prices:
            self.sell_prices.append(order.price)
            self.sell_prices = sorted(self.sell_prices)

    def remove_order(self, order: Order):
        if not order.validate():
            raise InvalidOrderError('Invalid order, missing or invalid data', order_id=order.id)

        existing_order = self.orders[order.id] if order.id in self.orders else None
        if not existing_order:
            raise OrderDoesNotExistError('Order does not exist', order_id=order.id)

        self.add_price(order)

        if existing_order.quantity >= order.quantity:
            existing_order.quantity -= order.quantity
            # delete the order if quantity goes down to 0
            if not existing_order.quantity:
                del self.orders[order.id]
                self.price_index[self.price_index_key(order.price, order.side)].remove(order.id)
                if not self.price_index[self.price_index_key(order.price, order.side)]:
                    # remove from index if list is empty
                    del self.price_index[self.price_index_key(order.price, order.side)]
                    # check to see the order we are removing has the best buy/sell
                    self.remove_price(order)
                self.update_best(order)

    def remove_price(self, order):
        a = []
        heap = self.buy_prices if order.side == Order.BUY_SIDE else self.sell_prices

        a.append(heappop(heap))
        while self.peek(a) != order.price:
            a.append(heappop(heap))

        for x in a:
            if x != order.price:
                heappush(heap, x)

    def remove_price_old(self, order):
        if order.side == Order.BUY_SIDE:
            self.buy_prices.remove(order.price)
        elif order.side == Order.SELL_SIDE:
            self.sell_prices.remove(order.price)

    def modify_order(self, order: Order):
        if not order.validate():
            raise InvalidOrderError('Invalid order, missing or invalid data', order_id=order.id)

        self.add_price(order)

        existing_order = self.orders[order.id] if order.id in self.orders else None
        if existing_order:
            existing_order.quantity = order.quantity
            self.update_best(order)

    def add_trade(self, trade: Trade):
        self.match(trade)
        self.trades[trade.price] = self.trades[trade.price] if trade.price in self.trades else []
        self.trades[trade.price].append(trade)
        if trade.price != self.last_trade_price:
            self.last_trade_price = trade.price
            self.total_quantity = 0
        self.total_quantity += trade.quantity
        if self.file:
            self.file.write("{}@{}\n".format(self.total_quantity, self.last_trade_price))

    def match(self, trade: Trade) -> List[Order]:
        # use list comprehension to get order ids for possible sell matches and flatten the list of lists
        possible_matches = self.flatten([self.price_index[o] for o in self.price_index if
                                         o.endswith('-{}'.format(Order.SELL_SIDE)) and float(
                                             o.split('-')[0]) <= trade.price])
        # pull matching order objects and sort them by order_datetime ascending
        matched_orders = sorted([self.orders[o] for o in possible_matches], key=lambda order: order.order_datetime)
        if not matched_orders:
            raise TradeNotMatchedError('Cannot match trade with order(s)', price=trade.price, quantity=trade.quantity)

        # make sure we can fill the order
        quantity_left = sum([order.quantity for order in matched_orders])
        if trade.quantity > quantity_left:
            raise TradeNotMatchedError('Not enough to match trade with order(s)', price=trade.price,
                                       quantity=trade.quantity)
        return matched_orders

    def output_state(self, file: IO):
        def out(header, side):
            file.write("{}:\n".format(header))
            data = [o for o in self.price_index if o.endswith('-{}'.format(side))]
            for key in data:
                price = float(key.split('-')[0])
                orders = ""
                for order_id in self.price_index[self.price_index_key(price, side)]:
                    quantity = self.orders[order_id].quantity
                    orders += "{},".format(str(quantity))

                file.write("{},{}\n".format('{0:.2f}'.format(price), orders[:-1]))

        out("SELLS", Order.SELL_SIDE)
        out("BUYS", Order.BUY_SIDE)

    def midquote(self, file: IO):
        if self.buy_prices and self.sell_prices:
            bb = max(self.buy_prices)
            bs = min(self.sell_prices)
            mid = (bb + bs) / 2
            file.write('{:.2f}\n'.format(mid))
        else:
            file.write('NaN\n')

    def midquote_old2(self, file: IO):
        if self.buy_prices and self.sell_prices:
            mid = (self.buy_prices[0] + self.sell_prices[0]) / 2
            file.write('{:.2f}\n'.format(mid))
        else:
            file.write('NaN\n')

    def midquote_old(self, file: IO):
        if self.best_buy and self.best_sell:
            buy = self.peek(self.best_buy)
            sell = self.peek(self.best_sell)
            mid = (buy + sell) / 2
            # self.best_buy.append(buy)
            # self.best_sell.append(sell)
            file.write('{0:.2f}\n'.format(mid))
        else:
            file.write('NaN\n')

    def update_best_old(self, order: Order):
        if order.side == Order.BUY_SIDE:
            if not self.best_buy_price or order.price > self.best_buy_price:
                self.best_buy_price = order.price
        else:
            if not self.best_sell_price or order.price < self.best_sell_price:
                self.best_sell_price = order.price

    def update_best(self, order: Order):
        if order.side == Order.BUY_SIDE:
            if not self.best_buy or order.price > self.peek(self.best_buy):
                self.best_buy.append(order.price)
            elif order.action == Order.ACTION_REMOVE and order.price == self.peek(self.best_buy):
                self.best_buy.pop()
        else:
            if not self.best_sell or order.price < self.peek(self.best_sell):
                self.best_sell.append(order.price)
            elif order.action == Order.ACTION_REMOVE and order.price < self.peek(self.best_sell):
                self.best_sell.pop()

        bs = self.peek(self.best_sell)
        bb = self.peek(self.best_buy)
        if bs and bb and bs <= bb:
            self.expected_trade_count += 1

    def expected_trades(self):
        if self.expected_trade_count and not self.trades:
            raise BestPriceButNoTradeError(
                'Expected at least {} trade(s), but got none'.format(self.expected_trade_count))
        return True

    @staticmethod
    def peek(l):
        return l[len(l) - 1] if l else None

    @staticmethod
    def price_index_key(price, side):
        return "{}-{}".format(price, side)

    @staticmethod
    def flatten(l):
        for el in l:
            if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
                yield from Book.flatten(el)
            else:
                yield el
