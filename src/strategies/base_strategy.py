from datetime import datetime
from ..engine import (
    TradeEvent,
    Event,
    Order,
    OrderSide,
    OrderType,
    LimitOrderBook,
)
from .execution import ExecutionStrategy
from .signal import BaseSignal
import uuid


class BaseStrategy:
    """
    Abstract base class for trading strategies.
    Provides a consistent interface for Makers, Takers, or hybridsr.
    """

    def __init__(
        self,
        execution_strategy: ExecutionStrategy,
        cash_buffer: float = 0.2,
        sensitivity: float = 0.5,
        smoothing: float = 0.25,
        cooldown: float = 120.0,  # seconds. Should be > record interval
        record_metrics: bool = True,
        signal: BaseSignal | None = None,
        id: int | str | None = None,
        initial_cash: float = 10000,
        initial_inventory: int = 0,
    ):
        """Initialize the trading strategy.

        Args:
            execution_strategy (ExecutionStrategy): The execution strategy to use.
            cash_buffer (float, optional): The cash buffer to maintain. Defaults to 0.2.
            sensitivity (float, optional): The sensitivity of the strategy. Defaults to 0.5.
            smoothing (float, optional): The smoothing factor for the strategy. Defaults to 0.25.
            cooldown (float, optional): The cooldown period for the strategy. Defaults to 120.0.
            signal (BaseSignal | None, optional): The signal generator for the strategy. Defaults to None.
            id (int | str | None, optional): The ID of the strategy. Defaults to None.
            initial_cash (float, optional): The initial cash balance for the strategy. Defaults to 10000.
            initial_inventory (int, optional): The initial inventory for the strategy. Defaults to 0.
        """
        from .strategy_metrics import StrategyMetrics

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
        self.metrics = StrategyMetrics(self.id) if record_metrics else None

    def record_trade_slippage(self, trade: TradeEvent):
        """Record slippage for a trade involving this agent.

        Args:
            trade (TradeEvent): The trade event to record slippage for.
        """
        parent_price = self.parent_order_dict[trade.parent_order_id]

        slippage = parent_price - trade.price

        slippage *= -1 if trade.sell_order_id == self.id else 1

        self.slippage.append((slippage, trade.size))

    def on_trade(self, trade: TradeEvent, time: float):
        """Handle a trade event.

        Args:
            trade (TradeEvent): The trade event to handle.
            time (float): The current time.
        """
        self.record_trade_slippage(trade)
        self.trades.append((time, trade))

    def _create_market_order(
        self, volume: int, side: OrderSide, parent_id: int | str | None
    ) -> Order:
        """Create a market order.

        Args:
            volume (int): The volume of the order.
            side (OrderSide): The side of the order (buy/sell).
            parent_id (int | str | None): The parent order ID, if any.

        Returns:
            Order: The created market order.
        """
        if type(self.id) == int:
            order_id = self.id + uuid.uuid4().int
        elif type(self.id) == str:
            order_id = self.id + uuid.uuid4().hex[:6]
        else:
            order_id = None

        return Order(
            type=OrderType.MARKET,
            side=side,
            size=volume,
            price=None,
            id=order_id,
            parent_id=parent_id,
        )

    def _create_limit_order(
        self, volume: int, side: OrderSide, price: float, parent_id: int | str | None
    ) -> Order:
        """Create a limit order.

        Args:
            volume (int): The volume of the order.
            side (OrderSide): The side of the order (buy/sell).
            price (float): The limit price for the order.
            parent_id (int | str | None): The parent order ID, if any.

        Returns:
            Order: The created limit order.
        """
        if type(self.id) == int:
            order_id = self.id + uuid.uuid4().int
        elif type(self.id) == str:
            order_id = self.id + uuid.uuid4().hex[:6]
        else:
            order_id = None

        return Order(
            type=OrderType.LIMIT,
            side=side,
            size=volume,
            price=price,
            id=order_id,
            parent_id=parent_id,
        )

    def _create_cancel_order(self, order_id: int | str) -> Order:
        """Create a cancel order.

        Args:
            order_id (int | str): The ID of the order to cancel.

        Returns:
            Order: The created cancel order.
        """
        return Order(
            type=OrderType.CANCEL,
            side=OrderSide.BUY,  # side is irrelevant for cancel orders
            size=0,
            price=None,
            id=order_id,
        )

    def schedule_order(
        self, schedule_time: float, volume: int, side: OrderSide, *args, **kwargs
    ):
        """Schedule an order for execution.

        Args:
            schedule_time (float): The time at which to execute the order.
            volume (int): The volume of the order.
            side (OrderSide): The side of the order (buy/sell).
        """
        self.schedule += self.execution_strategy.schedule_order(
            schedule_time, volume, side, *args, **kwargs
        )

        self.schedule.sort(key=lambda x: x[0])  # Sort by time

    def validate_order(self, order: Order, book: LimitOrderBook) -> bool:
        """Validate an order before submission.

        Args:
            order (Order): The order to validate.
            book (LimitOrderBook): The order book to validate against.

        Raises:
            ValueError: If the order is invalid.

        Returns:
            bool: Whether the order is valid.
        """
        if order.size < 0:
            raise ValueError("Order size must be positive.")

        best_ask_price = book.best_ask().get_price()

        # Naive validation logic (no book pre-walking)
        if order.side == OrderSide.BUY:
            if order.type == OrderType.LIMIT:
                order_price = order.get_price()
                if order_price is not None:
                    total_cost = order.size * order_price
                    if self.cash < total_cost:
                        return False
            elif order.type == OrderType.MARKET:
                if best_ask_price is not None:
                    total_cost = order.size * best_ask_price
                    if self.cash < total_cost:
                        return False

        return True

    def process_signal(self, time: float, book: LimitOrderBook, history: dict) -> None:
        """Process the trading signal.

        Args:
            time (float): The current time in the simulation.
            book (LimitOrderBook): The current state of the limit order book.
            history (dict): A dictionary containing historical data.

        Raises:
            ValueError: If the signal is invalid.

        Returns:
            None

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
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
            ask_price = best_ask.get_price()
            if ask_price is None or ask_price <= 0:
                return
            volume = int(budget // ask_price)

            self.schedule_order(time, volume, OrderSide.BUY)

        elif self.signal_state < -self.sensitivity:
            volume = int(abs(self.signal_state) * self.inventory)

            self.schedule_order(time, volume, OrderSide.SELL)

    def step(
        self, time: float, book: LimitOrderBook, history: dict
    ) -> tuple[list[Order], list[Order]]:
        """Process a trading step.

        Args:
            time (float): The current time in the simulation.
            book (LimitOrderBook): The current state of the limit order book.
            history (dict): A dictionary containing historical data.

        Returns:
            tuple[list[Order], list[Order]]: A tuple containing two lists of orders:
                - The first list contains orders to be canceled.
                - The second list contains orders to be submitted.

        Returns:
            _type_: _description_
        """
        self.process_signal(time, book, history)

        if not self.schedule:
            return [], []

        if time >= self.schedule[0][0]:
            _, volume, side, parent_id = self.schedule.pop(0)

            order = self._create_market_order(volume, side, parent_id)

            if not self.validate_order(order, book):
                return [], []

            if parent_id not in self.parent_order_dict:
                current_best = (
                    book.best_bid() if side == OrderSide.SELL else book.best_ask()
                )
                self.parent_order_dict[parent_id] = current_best.get_price()

            return [], [order]

        return [], []

    def update(self, time: float, events: list[Event]):
        """Update the strategy state based on events.

        Args:
            time (float): The current time in the simulation.
            events (list[Event]): A list of events to process.
        """
        if not events:
            return
        id_len = len(self.id) if type(self.id) == str else 0
        for event in events:
            if not isinstance(event, TradeEvent):
                continue
            if type(event.buy_order_id) == str:
                buy_id = event.buy_order_id[:id_len]
            elif type(event.buy_order_id) == int:
                buy_id = event.buy_order_id
            else:
                buy_id = 0

            if type(event.sell_order_id) == str:
                sell_id = event.sell_order_id[:id_len]
            elif type(event.sell_order_id) == int:
                sell_id = event.sell_order_id
            else:
                sell_id = 0

            if buy_id == self.id:
                # Bought
                self.inventory += event.size
                self.cash -= event.size * event.price
                self.on_trade(event, time)
            elif sell_id == self.id:
                # Sold
                self.inventory -= event.size
                self.cash += event.size * event.price
                self.on_trade(event, time)

    def record_metrics(self, time: float, book: LimitOrderBook):
        """Record trading metrics.

        Args:
            time (float): The current time in the simulation.
            book (LimitOrderBook): The current state of the limit order book.
        """
        if self.metrics:
            self.metrics.record(time, self, book)

    def compute_average_slippage(self) -> float:
        """Compute the average slippage.

        Returns:
            float: The average slippage.
        """
        if not self.slippage:
            return 0.0

        total_slippage = sum(slip * size for slip, size in self.slippage)
        total_size = sum(size for _, size in self.slippage)
        return total_slippage / total_size if total_size > 0 else 0.0

    def compute_total_slippage(self) -> float:
        """Compute the total slippage.

        Returns:
            float: The total slippage.
        """
        return sum(slip * size for slip, size in self.slippage)

    def realized_pnl(self) -> float:
        """Compute the realized profit and loss.

        Returns:
            float: The realized profit and loss
        """
        return self.cash - self.initial_cash

    def unrealized_pnl(self, book: LimitOrderBook) -> float:
        """Compute the unrealized profit and loss.

        Args:
            book (LimitOrderBook): The current state of the limit order book.

        Returns:
            float: The unrealized profit and loss
        """
        return self.inventory * book.mid_price()

    def total_pnl(self, book: LimitOrderBook) -> float:
        """Compute the total profit and loss.

        Args:
            book (LimitOrderBook): The current state of the limit order book.

        Returns:
            float: The total profit and loss
        """
        return self.realized_pnl() + self.unrealized_pnl(book)

    def save_metrics(self, filename: str | None = None):
        """Save trading metrics to a CSV file.

        Args:
            filename (str | None, optional): The name of the file to save the metrics to. Defaults to None.
        """
        if not self.metrics:
            print("No metrics to save.")
            return

        df = self.metrics.get_dataframe()

        if not filename:
            now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            filename = f"data/{now}-{self.id}-metrics.csv"
        else:
            filename = f"data/{filename}.csv"

        df.to_csv(filename, index=False)
        print(f"Metrics saved in {filename}")

    def reset(self, initial_cash: float | None = None, initial_inventory: int = 0):
        """Reset the strategy's state.

        Args:
            initial_cash (float | None, optional): The initial cash balance. Defaults to None.
            initial_inventory (int, optional): The initial inventory level. Defaults to 0.
        """
        self.cash = initial_cash or self.initial_cash
        self.inventory = initial_inventory
        self.parent_order_dict = {}
        self.schedule = []
        self.slippage = []
        self.trades = []
