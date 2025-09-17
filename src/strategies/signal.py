from ..engine.book import LimitOrderBook
from math import tanh


class BaseSignal:
    def compute(self, book: LimitOrderBook, history: dict) -> float:
        """Return a signed signal.
        Positive = buy bias, Negative = sell bias, 0 = neutral."""
        raise NotImplementedError


class MomentumSignal(BaseSignal):
    def __init__(self, look_back: int = 10, alpha: float = 20.0):
        self.look_back = look_back
        self.alpha = alpha

    def compute(self, book: LimitOrderBook, history: dict) -> float:
        mid_prices = history.get("mid_price", [])
        if len(mid_prices) < self.look_back + 1:
            return 0.0  # Not enough data

        recent_prices = mid_prices[-(self.look_back + 1) :]

        if recent_prices[-1] is None or recent_prices[0] is None:
            return 0.0  # Avoid None values

        momentum = recent_prices[-1] - recent_prices[0]

        return tanh(self.alpha * (momentum / recent_prices[0]))  # Normalize


class ImbalanceSignal(BaseSignal):
    def __init__(self, levels: int = 10):
        self.levels = levels

    def compute(self, book: LimitOrderBook, history: dict) -> float:
        bid_size = book.get_bid_size(levels=self.levels)
        ask_size = book.get_ask_size(levels=self.levels)

        if bid_size + ask_size == 0:
            return 0.0  # Avoid division by zero

        imbalance = (bid_size - ask_size) / (bid_size + ask_size)

        return imbalance
