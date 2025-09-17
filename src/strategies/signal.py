from ..engine.book import LimitOrderBook
from ..engine.metrics import Metrics


class BaseSignal:
    def compute(self, book: LimitOrderBook, history: dict) -> float:
        """Return a signed signal.
        Positive = buy bias, Negative = sell bias, 0 = neutral."""
        raise NotImplementedError


class MomentumSignal(BaseSignal):
    def __init__(self, look_back: int = 10):
        self.look_back = look_back

    def compute(self, book: LimitOrderBook, history: dict) -> float:
        mid_prices = history.get("mid_price", [])
        if len(mid_prices) < self.look_back + 1:
            return 0.0  # Not enough data

        recent_prices = mid_prices[-(self.look_back + 1) :]
        momentum = recent_prices[-1] - recent_prices[0]

        return momentum
