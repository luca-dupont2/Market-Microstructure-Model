import math
import uuid
from .base_strategy import BaseStrategy
from ..engine.order import Order, OrderType, OrderSide
from ..orderflow.generator import round_to_tick


# Base symmetric market making strategy
class SymmetricMaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy,
        config: dict,
        look_back: int = 10,  # for volatility estimation
        quote_size: int = 10,
        max_inventory: int = 100,
        quote_update_interval: int = 10,  # in multiples of dt
        *args,
        **kwargs,
    ):
        super().__init__(execution_strategy, *args, **kwargs)
        self.quote_size = quote_size
        self.max_inventory = max_inventory
        self.look_back = look_back

        self.dt = config["SIM_PARAMS"]["dt"]
        self.tick_size = config["SIM_PARAMS"]["tick_size"]
        self.quote_update_interval = quote_update_interval * self.dt

        self.quotes = {"bid": [], "ask": []}

        # Next time to refresh quotes
        self.next_quote_time = 0.0

    def step(self, time, book, history):
        if time >= self.next_quote_time:
            self.next_quote_time = time + self.quote_update_interval

            # Cancel existing quotes
            cancels = []
            for quote in self.quotes["bid"] + self.quotes["ask"]:
                cancel_order = self._create_cancel_order(quote.id)
                cancels.append(cancel_order)
            self.quotes = {"bid": [], "ask": []}

            mid_price = book.mid_price()
            book_spread = book.get_spread()

            if book_spread == float("inf") or mid_price == 0:
                return  # Cannot quote without a valid spread or mid price

            # Determine new quote prices
            bid_price = mid_price - book_spread / 2
            bid_price = round_to_tick(bid_price, self.tick_size)

            ask_price = mid_price + book_spread / 2
            ask_price = round_to_tick(ask_price, self.tick_size)

            # Place new quotes
            bid_order_id = self._create_limit_order(
                volume=self.quote_size,
                side=OrderSide.BUY,
                price=bid_price,
                parent_id=uuid.uuid4().int,
            )
            ask_order_id = self._create_limit_order(
                volume=self.quote_size,
                side=OrderSide.SELL,
                price=ask_price,
                parent_id=uuid.uuid4().int,
            )

            self.quotes["bid"].append(bid_order_id)
            self.quotes["ask"].append(ask_order_id)


# Market making strategy with Avellaneda-Stoikov pricing model
class InventoryMaker(SymmetricMaker):
    def __init__(
        self,
        execution_strategy,
        config: dict,
        base_spread: float,  # in price units (e.g. $0.05)
        look_back: int = 10,  # for volatility estimation
        quote_size: int = 10,
        max_inventory: int = 100,
        tick_size: float = 0.01,
        quote_update_interval: float = 5.0,
        *args,
        **kwargs,
    ):
        super().__init__(execution_strategy, *args, **kwargs)
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

    def step(self, time, book, history):
        pass
