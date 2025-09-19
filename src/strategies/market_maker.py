from .base_strategy import BaseStrategy


class MarketMaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy,
        base_spread: float,  # in price units (e.g. $0.05)
        quote_size: int = 10,
        max_inventory: int = 100,
        gamma: float = 0.001,
        tick_size: float = 0.01,
        quote_update_interval: float = 1.0,
        *args,
        **kwargs,
    ):
        super().__init__(execution_strategy, *args, **kwargs)
        self.base_spread = base_spread
        self.quote_size = quote_size
        self.max_inventory = max_inventory
        self.gamma = gamma
        self.tick_size = tick_size
        self.quote_update_interval = quote_update_interval

        # Track currently posted quotes: {side: order_id}
        self.my_quotes = {"bid": None, "ask": None}
        # Map my order id -> parent_id or metadata
        self.my_order_meta = {}
        # Next time to refresh quotes
        self.next_quote_time = 0.0
