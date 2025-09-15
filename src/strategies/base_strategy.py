from uuid import uuid4
from ..engine.events import EventType


class BaseStrategy:
    """
    Abstract base class for trading strategies.
    Provides a consistent interface for Makers, Takers, or hybrids.
    """

    def __init__(
        self,
        execution_strategy,
        id=None,
        initial_cash=10000,
        initial_inventory=0,
    ):
        self.id = id or uuid4().int
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.inventory = initial_inventory
        self.execution_strategy = execution_strategy
        self.parent_order_dict = {}
        self.schedule = []

    def on_trade(self, trade):
        """
        Callback when a trade involving this agent is executed.
        Allows strategy to update inventory, PnL, etc.
        """

        raise NotImplementedError("Subclasses must implement on_trade().")

    def update(self, events):

        for event in events:
            if event.type != EventType.TRADE:
                continue
            if event.buy_order_id == self.id:
                # Bought
                self.inventory += event.size
                self.cash -= event.size * event.price
            elif event.sell_order_id == self.id:
                # Sold
                self.inventory -= event.size
                self.cash += event.size * event.price
            self.on_trade(event)

    def reset(self, initial_cash=None, initial_inventory=0):
        self.cash = initial_cash or self.initial_cash
        self.inventory = initial_inventory

    def realized_pnl(self):
        return self.cash - self.initial_cash

    def unrealized_pnl(self, current_price):
        return self.inventory * current_price

    def total_pnl(self, current_price):
        return self.realized_pnl() + self.unrealized_pnl(current_price)
