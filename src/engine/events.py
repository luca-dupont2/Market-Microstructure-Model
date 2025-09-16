from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from .order import OrderSide, OrderType, Order
import uuid
from collections import deque
from collections.abc import Iterator


class EventType(Enum):
    """
    Enumeration of event types.
    """

    NEW_ORDER = 0
    CANCEL_ORDER = 1
    TRADE = 2


@dataclass
class Event:
    """
    Base class for all events.

    Attributes
    ----------
    type : EventType
        The type of the event.
    timestamp : datetime
        The timestamp of the event.
    """

    type: EventType
    timestamp: datetime


class EventQueue:
    """
    Queue for publishing and consuming events.

    Attributes
    ----------
    queue : collections.deque
        Internal queue storing events.
    """

    def __init__(self):
        self.queue = deque()

    def publish(self, event: Event) -> None:
        """
        Publish an event to the queue.

        Parameters
        ----------
        event : Event
            The event to be added to the queue.
        """
        self.queue.append(event)

    def consume(self) -> Iterator[Event]:
        """
        Consume events from the queue in FIFO order.

        Yields
        ------
        Event
            The next event in the queue.
        """
        while self.queue:
            yield self.queue.popleft()


@dataclass
class NewOrderEvent(Event):
    """
    Event representing a new order.

    Attributes
    ----------
    order_id : int or str
        Unique identifier for the order.
    side : OrderSide
        Side of the order (buy/sell).
    size : int
        Size of the order.
    price : float or None
        Price of the order.
    order_type : OrderType
        Type of the order (limit/market).
    parent_order_id : int or str or None
        Identifier for the parent order, if any.
    """

    order_id: int | str
    side: OrderSide
    size: int
    price: float | None
    order_type: OrderType
    parent_order_id: int | str | None

    def __repr__(self) -> str:
        return f"NewOrderEvent(order_id={self.order_id}, side={self.side}, size={self.size}, price={self.price}, order_type={self.order_type}, timestamp={self.timestamp})"


@dataclass
class CancelOrderEvent(Event):
    """
    Event representing an order cancellation.

    Attributes
    ----------
    order_id : int or str
        Unique identifier for the order being cancelled.
    """

    order_id: int | str

    def __repr__(self) -> str:
        return f"CancelOrderEvent(order_id={self.order_id}, timestamp={self.timestamp})"


@dataclass
class TradeEvent(Event):
    """
    Event representing a trade.

    Attributes
    ----------
    trade_id : int or str
        Unique identifier for the trade.
    price : float
        Price at which the trade occurred.
    size : int
        Size of the trade.
    buy_order_id : int or str
        Identifier for the buy order.
    sell_order_id : int or str
        Identifier for the sell order.
    parent_order_id : int or str or None
        Identifier for the parent order, if any.
    """

    trade_id: int | str
    price: float
    size: int
    buy_order_id: int | str
    sell_order_id: int | str
    parent_order_id: int | str | None

    def __repr__(self) -> str:
        return f"TradeEvent(trade_id={self.trade_id}, price={self.price}, size={self.size}, buy_order_id={self.buy_order_id}, sell_order_id={self.sell_order_id}, timestamp={self.timestamp})"


def create_trade_event(
    price: float,
    size: int,
    buy_order: Order,
    sell_order: Order,
    timestamp: datetime,
    parent_order_id: int | str | None,
) -> TradeEvent:
    """
    Create a TradeEvent instance.

    Parameters
    ----------
    price : float
        Price at which the trade occurred.
    size : int
        Size of the trade.
    buy_order : Order
        Buy order involved in the trade.
    sell_order : Order
        Sell order involved in the trade.
    timestamp : datetime
        Timestamp of the trade event.
    parent_order_id : int or str or None
        Identifier for the parent order, if any.

    Returns
    -------
    TradeEvent
        The created trade event.
    """
    return TradeEvent(
        type=EventType.TRADE,
        timestamp=timestamp,
        trade_id=uuid.uuid4().int,
        price=price,
        size=size,
        buy_order_id=buy_order.id,
        sell_order_id=sell_order.id,
        parent_order_id=parent_order_id,
    )


def create_new_order_event(order: Order, timestamp: datetime) -> NewOrderEvent:
    """
    Create a NewOrderEvent instance.

    Parameters
    ----------
    order : Order
        The order to create an event for.
    timestamp : datetime
        Timestamp of the new order event.

    Returns
    -------
    NewOrderEvent
        The created new order event.
    """
    return NewOrderEvent(
        type=EventType.NEW_ORDER,
        timestamp=timestamp,
        order_id=order.id,
        side=order.side,
        size=order.size,
        price=order.price,
        order_type=order.type,
        parent_order_id=order.parent_id,
    )


def create_cancel_order_event(order: Order, timestamp: datetime) -> CancelOrderEvent:
    """
    Create a CancelOrderEvent instance.

    Parameters
    ----------
    order : Order
        The order to cancel.
    timestamp : datetime
        Timestamp of the cancellation event.

    Returns
    -------
    CancelOrderEvent
        The created cancel order event.
    """
    return CancelOrderEvent(
        type=EventType.CANCEL_ORDER, timestamp=timestamp, order_id=order.id
    )
