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

    def schedule_order(self, *args, **kwargs):
        self.schedule += self.execution_strategy.schedule_order(*args, **kwargs)

        self.schedule.sort(key=lambda x: x[0])  # Sort by time

    def on_trade(self, trade):
        parent_price = self.parent_order_dict[trade.parent_order_id]

        slippage = parent_price - trade.price

        slippage *= -1 if trade.sell_order_id == self.id else 1

        self.slippage.append((slippage, trade.size))

    def step(self, time, book):
        if not self.schedule:
            return None

        if time >= self.schedule[0][0]:
            _, volume, side, parent_id = self.schedule.pop(0)

            order = Order(
                type=OrderType.MARKET,
                side=side,
                size=volume,
                price=None,
                id=self.id,
                parent_id=parent_id,
            )

            if parent_id not in self.parent_order_dict:
                current_best = (
                    book.best_bid() if side == OrderSide.SELL else book.best_ask()
                )
                self.parent_order_dict[parent_id] = current_best.get_price()

            return order

        return None

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
