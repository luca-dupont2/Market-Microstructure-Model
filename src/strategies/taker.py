from .base_strategy import BaseStrategy
from ..engine.order import OrderType, OrderSide, Order


class ManualTaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy,
        id=None,
        initial_cash=10000,
        initial_inventory=0,
    ):
        super().__init__(
            execution_strategy=execution_strategy,
            id=id,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
        )
        self.slippage = []

    def on_trade(self, trade):
        parent_price = self.parent_order_dict[trade.parent_order_id]

        slippage = parent_price - trade.price

        slippage *= -1 if trade.sell_order_id == self.id else 1

        self.slippage.append((slippage, trade.size))

    def compute_average_slippage(self):
        if not self.slippage:
            return 0.0

        total_slippage = sum(slip * size for slip, size in self.slippage)
        total_size = sum(size for _, size in self.slippage)
        return total_slippage / total_size if total_size > 0 else 0.0

    def compute_total_slippage(self):
        return sum(slip * size for slip, size in self.slippage)

    def reset(self, initial_cash=None, initial_inventory=0):
        self.cash = initial_cash or self.initial_cash
        self.inventory = initial_inventory
        self.current_index = 0
        self.slippage = []
        self.parent_price = 0
        self.schedule = []
