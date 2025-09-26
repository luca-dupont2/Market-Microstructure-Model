import math
import uuid
from .base_strategy import BaseStrategy
from .execution import ExecutionStrategy
from ..engine.order import Order, OrderSide
from ..engine.book import LimitOrderBook
from ..engine.events import EventType, TradeEvent, Event
from ..orderflow.generator import round_to_tick


# Base symmetric market making strategy
class SymmetricMaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy: ExecutionStrategy,
        config: dict,
        quote_size: int | None = None,
        max_inventory: int | None = None,
        quote_update_interval: int | None = None,  # in multiples of dt
        **kwargs,
    ):
        """Initialize the symmetric market maker strategy.

        Args:
            execution_strategy (ExecutionStrategy): The execution strategy to use.
            config (dict): The configuration dictionary.
            quote_size (int, optional): The size of the quotes. Defaults to 10.
            max_inventory (int, optional): The maximum inventory level. Defaults to 100.
            quote_update_interval (int, optional): The quote update interval. Defaults to 10.
        """
        super().__init__(execution_strategy, **kwargs)
        self.quote_size = (
            quote_size or config["STRATEGY_PARAMS"]["market_maker"]["quote_size"]
        )
        self.max_inventory = (
            max_inventory
            or config["STRATEGY_PARAMS"]["market_maker"]["inventory_limit"]
        )

        self.dt = config["SIM_PARAMS"]["dt"]
        self.tick_size = config["SIM_PARAMS"]["tick_size"]
        self.quote_update_interval = (
            quote_update_interval
            or config["STRATEGY_PARAMS"]["market_maker"]["quote_update_interval"]
        ) * self.dt

        self.quotes = {"bid": [], "ask": []}

        # Next time to refresh quotes
        self.next_quote_time = 0.0

    def step(
        self, time: float, book: LimitOrderBook, history: dict
    ) -> tuple[list[Order], list[Order]]:
        """Process a trading step.

        Args:
            time (float): The current simulation time.
            book (LimitOrderBook): The current state of the limit order book.
            history (dict): The historical data for the simulation. From metrics.data

        Returns:
            tuple[list[Order], list[Order]]: A tuple containing the list of orders to place and the list of orders to cancel.
        """
        orders = []
        cancels = []

        if time >= self.next_quote_time:
            self.next_quote_time = time + self.quote_update_interval

            # Cancel existing quotes
            for quote in self.quotes["bid"]:
                cancel_order = self._create_cancel_order(quote.id)
                cancels.append(cancel_order)

            for quote in self.quotes["ask"]:
                cancel_order = self._create_cancel_order(quote.id)
                cancels.append(cancel_order)

            self.quotes = {"bid": [], "ask": []}

            mid_price = book.mid_price()
            book_spread = book.get_spread()

            if book_spread == float("inf") or mid_price == 0:
                return cancels, []  # Cannot quote without a valid spread or mid price

            # Determine new quote prices
            bid_price = mid_price - book_spread / 2
            bid_price = round_to_tick(bid_price, self.tick_size)

            ask_price = mid_price + book_spread / 2
            ask_price = round_to_tick(ask_price, self.tick_size)

            # Place new quotes
            bid_order = self._create_limit_order(
                volume=self.quote_size,
                side=OrderSide.BUY,
                price=bid_price,
                parent_id=uuid.uuid4().int,
            )
            ask_order = self._create_limit_order(
                volume=self.quote_size,
                side=OrderSide.SELL,
                price=ask_price,
                parent_id=uuid.uuid4().int,
            )

            if (
                self.inventory + self.quote_size < self.max_inventory
                and self.validate_order(bid_order, book)
            ):
                orders.append(bid_order)
                self.quotes["bid"].append(bid_order)

            if (
                self.inventory - self.quote_size > -self.max_inventory
                and self.validate_order(ask_order, book)
            ):
                orders.append(ask_order)
                self.quotes["ask"].append(ask_order)

        return cancels, orders

    def on_trade(
        self, trade: TradeEvent, time: float
    ):  # No slippage handling for limit orders
        """Handle a trade event.

        Args:
            trade (TradeEvent): The trade event to handle.
            time (float): The time at which the trade occurred.
        """
        self.trades.append((time, trade))

    def update(self, time: float, events: list[Event]):
        """Update the strategy state based on the current time and events.

        Args:
            time (float): The current simulation time.
            events (list[Event]): The list of events to process.
        """
        if not events:
            return
        for event in events:
            if not isinstance(event, TradeEvent):
                continue

            # Type checking for IDs to avoid mismatches
            if type(self.id) != type(event.buy_order_id) and type(self.id) != type(
                event.sell_order_id
            ):
                continue  # ID types do not match

            buy_compare_id = None
            sell_compare_id = None
            if type(self.id) == str and type(event.buy_order_id) == str:
                buy_compare_id = event.buy_order_id[
                    : len(self.id)
                ]  # Truncate id to strategy name for comparison
            elif type(self.id) == str and type(event.sell_order_id) == str:
                sell_compare_id = event.sell_order_id[: len(self.id)]
            else:
                buy_compare_id = event.buy_order_id
                sell_compare_id = event.sell_order_id

            if buy_compare_id == self.id:
                # Bought
                self.inventory += event.size
                self.cash -= event.size * event.price
                self.quotes["bid"] = [
                    q for q in self.quotes["bid"] if q.id != event.buy_order_id
                ]
                self.on_trade(event, time)
            elif sell_compare_id == self.id:
                # Sold
                self.inventory -= event.size
                self.cash += event.size * event.price
                self.quotes["ask"] = [
                    q for q in self.quotes["ask"] if q.id != event.sell_order_id
                ]
                self.on_trade(event, time)


#! TODO: Implement Avellaneda-Stoikov model
#! CLASS NOT IMPLEMENTED YET
# Market making strategy with Avellaneda-Stoikov pricing model
class InventoryMaker(SymmetricMaker):
    def __init__(
        self,
        execution_strategy: ExecutionStrategy,
        config: dict,
        base_spread: float,  # in price units (e.g. $0.05)
        look_back: int = 10,  # for volatility estimation
        quote_size: int = 10,
        max_inventory: int = 100,
        tick_size: float = 0.01,
        quote_update_interval: float = 5.0,
        **kwargs,
    ):
        """Initialize the InventoryMaker strategy.

        Args:
            execution_strategy (ExecutionStrategy): The execution strategy to use.
            config (dict): The configuration dictionary.
            base_spread (float): The base spread for quotes.
            max_inventory (int, optional): The maximum inventory level. Defaults to 100.
            tick_size (float, optional): The tick size for price movements. Defaults to 0.01.
            quote_update_interval (float, optional): The interval for updating quotes. Defaults to 5.0.
        """
        super().__init__(execution_strategy, **kwargs)
        self.base_spread = base_spread
        self.quote_size = quote_size
        self.max_inventory = max_inventory
        self.gamma = (
            1 / max_inventory
        )  # Risk aversion scales inversely with max inventory
        self.tick_size = tick_size
        self.look_back = look_back
        self.quote_update_interval = quote_update_interval
        self.horizon = config["SIM_PARAMS"]["horizon"]
        self.dt = config["SIM_PARAMS"]["dt"]

        # Track currently posted quotes: {side: order_id}
        self.my_quotes = {"bid": None, "ask": None}
        # Map my order id -> parent_id or metadata
        self.my_order_meta = {}
        # Next time to refresh quotes
        self.next_quote_time = 0.0
        self.last_book = []
        self.order_time_dict = {}  # Track time of each order
        self.A_k = (0.0, 0.0)  # Store last A and k estimates
        self.sigma2 = 0.0

    def estimate_A_k(self, last_book, book) -> tuple[float, float]:
        """Estimate A and k for Avellaneda-Stoikov pricing."""
        return 0.0, 0.0

    def get_recent_variance(self, history) -> float:
        """Estimate instantaneous variance (sigma^2) from mid-price history."""
        mid_prices = history.get("mid_price", [])
        if len(mid_prices) < self.look_back + 1:
            return 0.0

        mid_prices = mid_prices[-(self.look_back + 1) :]
        if any(p is None or p == 0 for p in mid_prices):
            return 0.0  # Avoid None values

        returns = [
            math.log(mid_prices[i] / mid_prices[i - 1])
            for i in range(1, len(mid_prices))
        ]

        if not returns:
            return 0.0

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)

        return variance / self.dt

    def step(self, time, book, history) -> tuple[list[Order], list[Order]]:
        orders = []
        cancels = []
        # Implement the market making logic here
        return cancels, orders
