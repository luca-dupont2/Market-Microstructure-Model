from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from .order import OrderSide, OrderType
import uuid
from collections import deque


class EventType(Enum):
    NEW_ORDER = 0
    CANCEL_ORDER = 1
    TRADE = 2


class EventQueue:
    def __init__(self):
        self.queue = deque()

    def publish(self, event):
        self.queue.append(event)

    def consume(self):
        while self.queue:
            yield self.queue.popleft()


@dataclass
class Event:
    type: EventType
    timestamp: datetime


@dataclass
class NewOrderEvent(Event):
    order_id: int
    side: OrderSide
    size: int
    price: float | None
    order_type: OrderType

    def __repr__(self) -> str:
        return f"NewOrderEvent(order_id={self.order_id}, side={self.side}, size={self.size}, price={self.price}, order_type={self.order_type}, timestamp={self.timestamp})"


@dataclass
class CancelOrderEvent(Event):
    order_id: int

    def __repr__(self) -> str:
        return f"CancelOrderEvent(order_id={self.order_id}, timestamp={self.timestamp})"


@dataclass
class TradeEvent(Event):
    trade_id: int
    price: float
    size: int
    buy_order_id: int
    sell_order_id: int

    def __repr__(self) -> str:
        return f"TradeEvent(trade_id={self.trade_id}, price={self.price}, size={self.size}, buy_order_id={self.buy_order_id}, sell_order_id={self.sell_order_id}, timestamp={self.timestamp})"


def create_trade_event(price, size, buy_order, sell_order, timestamp):
    return TradeEvent(
        type=EventType.TRADE,
        timestamp=timestamp,
        trade_id=uuid.uuid4().int,
        price=price,
        size=size,
        buy_order_id=buy_order.id,
        sell_order_id=sell_order.id,
    )


def create_new_order_event(order, timestamp):
    return NewOrderEvent(
        type=EventType.NEW_ORDER,
        timestamp=timestamp,
        order_id=order.id,
        side=order.side,
        size=order.size,
        price=order.price,
        order_type=order.type,
    )


def create_cancel_order_event(order, timestamp):
    return CancelOrderEvent(
        type=EventType.CANCEL_ORDER, timestamp=timestamp, order_id=order.id
    )
