# strategies/base_strategy.py
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
        self.id = id or self.__class__.__name__
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.inventory = initial_inventory
        self.execution_strategy = execution_strategy
        self.schedule = []

    def on_trade(self, trade):
        """
        Callback when a trade involving this agent is executed.
        Allows strategy to update inventory, PnL, etc.
        """

        raise NotImplementedError("Subclasses must implement on_trade().")

    def update(self, trades):
        for trade in trades:
            if trade.buy_order_id == self.id:
                # Bought
                self.inventory += trade.size
                self.cash -= trade.size * trade.price
            elif trade.sell_order_id == self.id:
                # Sold
                self.inventory -= trade.size
                self.cash += trade.size * trade.price
            self.on_trade(trade)

    def reset(self, initial_cash=None, initial_inventory=0):
        self.cash = initial_cash or self.initial_cash
        self.inventory = initial_inventory

    def realized_pnl(self):
        return self.cash - self.initial_cash

    def unrealized_pnl(self, current_price):
        return self.inventory * current_price

    def total_pnl(self, current_price):
        return self.realized_pnl() + self.unrealized_pnl(current_price)
