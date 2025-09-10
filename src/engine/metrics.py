from collections import defaultdict
from .book import LimitOrderBook
from .events import Event, TradeEvent


class Metrics:
    def __init__(self):
        # Stores metrics as lists over time
        self.data = defaultdict(list)
        self.time = []

    def record(self, t, order_book: LimitOrderBook, events: list[Event] | None = None):
        """Record metrics at simulation time t."""
        best_bid = order_book.best_bid().get_price() if order_book.bid_orders else None
        best_ask = order_book.best_ask().get_price() if order_book.ask_orders else None

        mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else None
        spread = (best_ask - best_bid) if best_bid and best_ask else None

        total_bid_size = sum(o.size for o in order_book.bid_orders)
        total_ask_size = sum(o.size for o in order_book.ask_orders)

        depth_bid = len(order_book.bid_orders)
        depth_ask = len(order_book.ask_orders)

        trades = [e for e in events if type(e) is TradeEvent] if events else []

        volume = sum(trade.size for trade in trades) if trades else 0
        n_trades = len(trades) if trades else 0

        # Record values
        self.time.append(t)
        self.data["best_bid"].append(best_bid)
        self.data["best_ask"].append(best_ask)
        self.data["mid_price"].append(mid_price)
        self.data["spread"].append(spread)
        self.data["total_bid_size"].append(total_bid_size)
        self.data["total_ask_size"].append(total_ask_size)
        self.data["depth_bid"].append(depth_bid)
        self.data["depth_ask"].append(depth_ask)
        self.data["volume"].append(volume)
        self.data["n_trades"].append(n_trades)

    def get_dataframe(self):
        """Return a pandas DataFrame for analysis or plotting."""
        import pandas as pd

        df = pd.DataFrame(self.data)
        df["time"] = self.time
        return df
