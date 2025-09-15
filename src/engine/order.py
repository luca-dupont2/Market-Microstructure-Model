from enum import Enum
from datetime import datetime
import uuid


class OrderSide(Enum):
    BUY = 0
    SELL = 1


class OrderType(Enum):
    LIMIT = 0
    MARKET = 1
    CANCEL = 2


class Order:
    def __init__(
        self, side: OrderSide, price, size, type: OrderType, id=None, parent_id=None
    ):

        self.side = side
        self.price = price

        if price is not None and side == OrderSide.BUY:
            self.price *= -1

        self.size = size
        self.type = type

        self.parent_id = parent_id

        self.id = id or uuid.uuid4().int
        self.timestamp = datetime.now()

    def get_price(self):
        if self.id == -1:
            return 0

        if self.side == OrderSide.BUY:
            return -self.price
        return self.price

    def round_price(self, tick_size):
        self.price = round(self.price / tick_size) * tick_size

    def __lt__(self, other):
        if self.price != other.price:
            return self.price < other.price

        return self.timestamp < other.timestamp

    def __repr__(self):
        return f"Order(id={self.id}, parent_id={self.parent_id}, side={self.side}, price={self.price}, size={self.size}, type={self.type}, timestamp={self.timestamp})"
