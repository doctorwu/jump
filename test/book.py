import unittest

from jump.book import Book
from jump.error import TradeNotMatchedError
from jump.order import Order
from jump.trade import Trade


class TestBook(unittest.TestCase):
    def test_no_match_quantity(self):
        book = Book()
        sell1 = Order(side='S', price=1030, id=1000, quantity=2, action='A')
        sell2 = Order(side='S', price=1025, id=1001, quantity=5, action='A')
        sell3 = Order(side='S', price=1035, id=1002, quantity=5, action='A')
        buy1 = Order(side='B', price=1030, id=1003, quantity=2, action='A')
        trade = Trade(price=1030, quantity=10)
        book.add_order(sell1)
        book.add_order(sell2)
        book.add_order(sell3)
        book.add_order(buy1)
        with self.assertRaises(TradeNotMatchedError):
            book.add_trade(trade)

    def test_no_match(self):
        book = Book()
        sell1 = Order(side='S', price=1030, id=1000, quantity=2, action='A')
        sell2 = Order(side='S', price=1025, id=1001, quantity=5, action='A')
        sell3 = Order(side='S', price=1035, id=1002, quantity=5, action='A')
        buy1 = Order(side='B', price=1030, id=1003, quantity=2, action='A')
        trade = Trade(price=1000, quantity=1)
        book.add_order(sell1)
        book.add_order(sell2)
        book.add_order(sell3)
        book.add_order(buy1)
        with self.assertRaises(TradeNotMatchedError):
            book.add_trade(trade)

    def test_match(self):
        book = Book()
        sell1 = Order(side='S', price=1030, id=1000, quantity=2, action='A')
        sell2 = Order(side='S', price=1025, id=1001, quantity=5, action='A')
        sell3 = Order(side='S', price=1035, id=1002, quantity=5, action='A')
        buy1 = Order(side='B', price=1030, id=1003, quantity=2, action='A')
        trade = Trade(price=1030, quantity=1)
        book.add_order(sell1)
        book.add_order(sell2)
        book.add_order(sell3)
        book.add_order(buy1)
        book.add_trade(trade)

    def test_best_buy(self):
        book = Book()
        buy1 = Order(side='B', price=1030, id=1000, quantity=2, action='A')
        buy2 = Order(side='B', price=1035, id=1001, quantity=5, action='A')
        buy3 = Order(side='B', price=1025, id=1002, quantity=5, action='A')
        book.add_order(buy1)
        book.add_order(buy2)
        book.add_order(buy3)
        self.assertEqual(book.best_buy.pop(), 1035)

    def test_best_sell(self):
        book = Book()
        sell1 = Order(side='S', price=1030, id=1000, quantity=2, action='A')
        sell2 = Order(side='S', price=1025, id=1001, quantity=5, action='A')
        sell3 = Order(side='S', price=1035, id=1002, quantity=5, action='A')
        book.add_order(sell1)
        book.add_order(sell2)
        book.add_order(sell3)
        self.assertEqual(book.best_sell.pop(), 1025)

    def test_add_trade(self):
        book = Book()
        sell1 = Order(side='S', price=1025, id=1000, quantity=2)
        sell2 = Order(side='S', price=1025, id=1001, quantity=5)
        buy = Order(side='B', price=1025, id=1002, quantity=3)
        book.add_order(sell1)
        book.add_order(sell2)
        book.add_order(buy)
        trade1 = Trade(price=1025, quantity=2)
        trade2 = Trade(price=1025, quantity=1)
        book.add_trade(trade1)
        book.add_trade(trade2)
        self.assertEqual(len(book.trades[1025]), 2)

    def test_remove(self):
        order1 = Order(side='B', price=1025, id=10000, quantity=1)
        order2 = Order(side='B', price=1025, id=10001, quantity=1)
        book = Book()
        book.add_order(order1)
        book.add_order(order2)
        book.remove_order(order1)
        self.assertEqual(len(book.orders), 1)

    def test_add_duplicate_order(self):
        from jump.error import DuplicateOrderError
        order1 = Order(side='B', price=1025, id=10000, quantity=1)
        order2 = Order(side='B', price=1025, id=10000, quantity=1)
        book = Book()
        book.add_order(order1)
        with self.assertRaises(DuplicateOrderError):
            book.add_order(order2)

    def test_remove_with_no_order(self):
        from jump.error import OrderDoesNotExistError
        book = Book()
        order1 = Order(side='B', price=1025, id=10000, quantity=1)
        with self.assertRaises(OrderDoesNotExistError):
            book.remove_order(order1)

    def test_modify(self):
        order1 = Order(side='B', price=1025, id=10000, quantity=1)
        book = Book()
        book.add_order(order1)
        order1_mod = Order(side='B', price=1025, id=10000, quantity=5)
        book.modify_order(order1_mod)
        self.assertEqual(book.orders[10000].quantity, 5)

    def test_bad_message(self):
        from jump.feed_processor import ProcessorFactory
        from jump.error import InvalidMessageError
        with self.assertRaises(InvalidMessageError):
            ProcessorFactory.create_processor('BADMESSAGE', Book())

    def test_best_with_no_trades(self):
        from jump.error import BestPriceButNoTradeError
        book = Book()
        sell = Order(side='S', price=1025, id=1000, quantity=2)
        buy = Order(side='B', price=1025, id=1002, quantity=2)
        book.add_order(sell)
        book.add_order(buy)
        with self.assertRaises(BestPriceButNoTradeError):
            book.expected_trades()

    def test_invalid_order(self):
        from jump.error import InvalidOrderError
        book = Book()
        sell = Order()
        with self.assertRaises(InvalidOrderError):
            book.add_order(sell)


if __name__ == '__main__':
    unittest.main()
