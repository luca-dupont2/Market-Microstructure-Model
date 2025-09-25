from enum import Enum
from datetime import datetime
import uuid


class OrderSide(Enum):
    """Represents the side of an order (buy or sell).

    Args:
        Enum (Enum): Enum class to represent order sides.
    """

    BUY = 0
    SELL = 1


class OrderType(Enum):
    """Represents the type of an order (limit, market, cancel).

    Args:
        Enum (Enum): Enum class to represent order types.
    """

    LIMIT = 0
    MARKET = 1
    CANCEL = 2


class Order:
    """Represents a market order in the order book."""

    def __init__(
        self,
        side: OrderSide,
        price: float | None,
        size: int,
        type: OrderType,
        id: int | str | None = None,
        parent_id: int | str | None = None,
    ):
        """Initialize an order.

        Args:
            side (OrderSide): The side of the order (buy or sell).
            price (float | None): The price of the order.
            size (int): The size of the order.
            type (OrderType): The type of the order (limit, market, cancel).
            id (int | str | None, optional): The ID of the order. Defaults to None.
            parent_id (int | str | None, optional): The parent ID of the order. Defaults to None.
        """

        self.side = side
        self.price = price

        if self.price and self.side == OrderSide.BUY:
            self.price *= -1

        self.size = size
        self.type = type

        self.parent_id = parent_id or uuid.uuid4().int

        self.id = id or uuid.uuid4().int
        self.timestamp = datetime.now()

    def get_price(self) -> float | None:
        """Get the price of the order.

        Returns:
            float | None: The price of the order.
        """
        if self.id == -1:
            return 0
        if not self.price:
            return 0

        if self.side == OrderSide.BUY:
            return -self.price
        return self.price

    def __lt__(self, other):
        if self.price != other.price:
            return self.price < other.price

        return self.timestamp < other.timestamp

    def __repr__(self):
        return f"Order(id={self.id}, parent_id={self.parent_id}, side={self.side}, price={self.price}, size={self.size}, type={self.type}, timestamp={self.timestamp})"
