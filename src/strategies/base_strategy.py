from src.engine.order import Order, OrderSide, OrderType
from ..engine.events import EventType
from tabulate import tabulate


class BaseStrategy:
    """
    Abstract base class for trading strategies.
    Provides a consistent interface for Makers, Takers, or hybridsr.
    """

    def __init__(
        self,
        execution_strategy,
        cash_buffer: float = 0.2,
        sensitivity: float = 0.5,
        smoothing: float = 0.25,
        cooldown: float = 120.0,  # seconds. Should be > record interval
        signal=None,
        id=None,
        initial_cash=10000,
        initial_inventory=0,
    ):
        self.id = id or __class__.__name__
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.sensitivity = sensitivity
        self.cash_buffer = cash_buffer
        self.inventory = initial_inventory
        self.execution_strategy = execution_strategy
        self.signal = signal
        self.smoothing = smoothing
        self.cooldown = cooldown  # seconds
        self.signal_state = 0.0
        self.parent_order_dict = {}
        self.schedule = []
        self.slippage = []
        self.trades = []

    def record_trade_slippage(self, trade):
        """
        Record slippage for a trade involving this agent.
        """

        parent_price = self.parent_order_dict[trade.parent_order_id]

        slippage = parent_price - trade.price

        slippage *= -1 if trade.sell_order_id == self.id else 1

        self.slippage.append((slippage, trade.size))

    def on_trade(self, trade, time):
        self.record_trade_slippage(trade)
        self.trades.append((time, trade))

    def schedule_order(self, schedule_time, volume, side, *args, **kwargs):
        self.schedule += self.execution_strategy.schedule_order(
            schedule_time, volume, side, *args, **kwargs
        )

        self.schedule.sort(key=lambda x: x[0])  # Sort by time

    def validate_order(self, order, book):
        """
        Validate an order before submission.
        Can be overridden by subclasses for custom validation logic.
        """
        if order.size < 0:
            raise ValueError("Order size must be positive.")

        best_ask_price = book.best_ask().get_price()

        # Naive validation logic (no book pre-walking)
        if order.side == OrderSide.BUY:
            if order.type == OrderType.LIMIT:
                total_cost = order.size * order.price
                if self.cash < total_cost:
                    print("Insufficient cash for buy limit order.")
                    return False
            elif order.type == OrderType.MARKET:
                total_cost = order.size * best_ask_price
                if self.cash < total_cost:
                    print("Insufficient cash for buy market order.")
                    return False
        elif order.side == OrderSide.SELL:
            if order.size > self.inventory:
                print("Insufficient inventory for sell limit order.")
                return False

        return True

    def process_signal(self, book, history, time) -> None:
        if self.signal is None:
            return None

        if abs(self.sensitivity) > 1.0:
            raise ValueError("Sensitivity must be between 0 and 1.")

        last_trade_time = self.trades[-1][0] if self.trades else -float("inf")

        if time - last_trade_time < self.cooldown:
            return None  # In cooldown period

        signal_value = self.signal.compute(book, history)

        self.signal_state = (
            self.smoothing * signal_value + (1 - self.smoothing) * self.signal_state
        )

        if self.signal_state > self.sensitivity:
            best_ask = book.best_ask()
            if best_ask.id == -1:
                return

            budget = (self.cash * (1 - self.cash_buffer)) * self.signal_state
            volume = budget // best_ask.get_price()

            self.schedule_order(time, volume, OrderSide.BUY)

        elif self.signal_state < -self.sensitivity:
            volume = int(abs(self.signal_state) * self.inventory)

            self.schedule_order(time, volume, OrderSide.SELL)

    def step(self, time, book, history):
        self.process_signal(book, history, time)

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

            if not self.validate_order(order, book):
                return None

            if parent_id not in self.parent_order_dict:
                current_best = (
                    book.best_bid() if side == OrderSide.SELL else book.best_ask()
                )
                self.parent_order_dict[parent_id] = current_best.get_price()

            return order

        return None

    def update(self, time, events):
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
            self.on_trade(event, time)

    def compute_average_slippage(self):
        if not self.slippage:
            return 0.0

        total_slippage = sum(slip * size for slip, size in self.slippage)
        total_size = sum(size for _, size in self.slippage)
        return total_slippage / total_size if total_size > 0 else 0.0

    def compute_total_slippage(self):
        return sum(slip * size for slip, size in self.slippage)

    def realized_pnl(self):
        return self.cash - self.initial_cash

    def unrealized_pnl(self, book):
        return self.inventory * book.mid_price()

    def total_pnl(self, book):
        return self.realized_pnl() + self.unrealized_pnl(book)

    def print_summary(self, book):
        metrics = {
            "Strategy ID": self.id,
            "Final Cash": f"${self.cash:.2f}",
            "Final Inventory": f"{self.inventory} shares",
            "Realized PnL": f"${self.realized_pnl():.2f}",
            "Unrealized PnL": f"${self.unrealized_pnl(book):.2f}",
            "Total PnL": f"${self.total_pnl(book):.2f}",
            "Average Slippage": f"${self.compute_average_slippage():.4f}",
            "Total Slippage": f"${self.compute_total_slippage():.2f}",
            "Number of Trades": len(self.trades),
        }

        print(
            tabulate(
                metrics.items(), headers=["Metric", "Value"], tablefmt="fancy_grid"
            )
        )

    def reset(self, initial_cash=None, initial_inventory=0):
        self.cash = initial_cash or self.initial_cash
        self.inventory = initial_inventory
        self.parent_order_dict = {}
        self.schedule = []
        self.slippage = []
        self.trades = []
