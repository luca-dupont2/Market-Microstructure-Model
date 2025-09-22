import math
from .base_strategy import BaseStrategy


class MarketMaker(BaseStrategy):
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
        super().__init__(
            execution_strategy, *args, **kwargs
        )
        self.base_spread = base_spread
        self.quote_size = quote_size
        self.max_inventory = max_inventory
        self.gamma = 1 / max_inventory  # Risk aversion scales inversely with max inventory
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

        return variance/self.dt 

    def step(self, time, book, history):
        pass
