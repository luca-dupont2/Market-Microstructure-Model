from .base import BaseStrategy
from ..engine.order import OrderType, OrderSide, Order


class TWAPSingleTaker(BaseStrategy):
    def __init__(self, rng, config, initial_cash=100_000, initial_inventory=0, id=None):
        super().__init__(
            id=id,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
            config=config,
        )
        self.rng = rng

        self.schedule = []

        self.slippage = []
        self.parent_start_price = 0.0

        self.duration = config["STRATEGY_PARAMS"]["taker"]["twap"]["duration"]
        self.intervals = config["STRATEGY_PARAMS"]["taker"]["twap"]["intervals"]

    def schedule_twap(
        self,
        schedule_time,
        current_price,
        total_volume,
        side: OrderSide,
    ):
        interval_volume = total_volume // self.intervals
        times = [
            schedule_time
            + i * (self.duration / self.intervals)
            + self.rng.uniform(0, self.duration / self.intervals)
            for i in range(self.intervals)
        ]

        self.schedule = [(t, interval_volume, side) for t in times]
        self.parent_start_price = current_price

    def on_trade(self, trade):
        slippage = self.parent_start_price - trade.price

        slippage *= 1 if trade.buy_order_id == self.id else -1

        self.slippage.append((slippage, trade.size))

    def step(self, time):
        if self.schedule and time >= self.schedule[0][0]:
            _, volume, side = self.schedule.pop(0)

            order = Order(
                type=OrderType.MARKET,
                side=side,
                size=volume,
                price=None,
                id=self.id,
            )

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
        self.slippage = []
        self.schedule = []
        self.parent_start_price = 0.0


class SingleTaker(BaseStrategy):
    def __init__(self, rng, config, initial_cash=100_000, initial_inventory=0, id=None):
        super().__init__(
            id=id,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
            config=config,
        )
        self.rng = rng
        self.order_placed = False

        self.slippage = []

        self.schedule = (0, 0, OrderSide.BUY)
        self.parent_start_price = 0.0

    def on_trade(self, trade):
        slippage = self.parent_start_price - trade.price

        slippage *= 1 if trade.buy_order_id == self.id else -1
        self.slippage.append((slippage, trade.size))

    def schedule_order(
        self,
        schedule_time,
        current_price,
        volume,
        side,
    ):
        self.schedule = (schedule_time, volume, side)
        self.parent_start_price = current_price
        self.order_placed = False

    def step(self, time):
        if time >= self.schedule[0] and not self.order_placed:
            self.order_placed = True

            order = Order(
                type=OrderType.MARKET,
                side=self.schedule[2],
                size=self.schedule[1],
                price=None,
                id=self.id,
            )

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
        self.order_placed = False
        self.slippage = []
        self.schedule = (0, 0, OrderSide.BUY)
        self.parent_start_price = 0.0
