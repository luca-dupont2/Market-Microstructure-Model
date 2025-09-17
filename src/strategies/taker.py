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

    def on_trade(self, trade):
        self.record_trade_slippage(trade)

    def reset(self, initial_cash=None, initial_inventory=0):
        self.cash = initial_cash or self.initial_cash
        self.inventory = initial_inventory
        self.slippage = []
        self.parent_order_dict = {}
        self.schedule = []
        self.slippage = []
