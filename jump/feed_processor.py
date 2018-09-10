from abc import ABC, abstractmethod

from jump.book import Book
from jump.error import InvalidMessageError
from jump.order import Order
from jump.trade import Trade


class MessageProcessor(ABC):

    @abstractmethod
    def process(self, row):
        ...


class AddProcessor(MessageProcessor):
    def __init__(self, book: Book = None):
        self.book = book

    def process(self, message):
        order = Order(id=int(message[1]), side=message[2], quantity=int(message[3]), price=float(message[4]),
                      action=message[0])
        self.book.add_order(order)


class RemoveProcessor(MessageProcessor):
    def __init__(self, book: Book = None):
        self.book = book

    def process(self, message):
        order = Order(id=int(message[1]), side=message[2], quantity=int(message[3]), price=float(message[4]),
                      action=message[0])
        self.book.remove_order(order)


class ModifyProcessor(MessageProcessor):
    def __init__(self, book: Book = None):
        self.book = book

    def process(self, message):
        order = Order(id=int(message[1]), side=message[2], quantity=int(message[3]), price=float(message[4]),
                      action=message[0])
        self.book.modify_order(order)


class TradeProcessor(MessageProcessor):
    def __init__(self, book: Book = None):
        self.book = book

    def process(self, message):
        trade = Trade(quantity=int(message[1]), price=float(message[2]))
        self.book.add_trade(trade)


class ProcessorFactory(object):
    @staticmethod
    def create_processor(message, book: Book) -> MessageProcessor:
        if len(message) == 5:
            action = message[0]
            if action == 'A':
                return AddProcessor(book=book)
            elif action == 'X':
                return RemoveProcessor(book=book)
            elif action == 'M':
                return ModifyProcessor(book=book)
        elif len(message) == 3 and message[0] == 'T':
            return TradeProcessor(book=book)

        raise InvalidMessageError('Invalid message: {}'.format(message))
