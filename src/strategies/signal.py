from ..engine.book import LimitOrderBook
from math import tanh


class BaseSignal:
    """Base class for trading signals."""

    def compute(self, book: LimitOrderBook, history: dict) -> float:
        """Compute the trading signal.

        Args:
            book (LimitOrderBook): The current state of the limit order book.
            history (dict): The historical data for the simulation.

        Raises:
            NotImplementedError: If the method is not implemented.

        Returns:
            float: The computed trading signal.
        """
        raise NotImplementedError


class MomentumSignal(BaseSignal):
    def __init__(self, look_back: int = 10, alpha: float = 20.0):
        """Momentum trading signal.

        Args:
            look_back (int, optional): The look-back period for momentum calculation. Defaults to 10.
            alpha (float, optional): The sensitivity factor for the signal. Defaults to 20.0.
        """
        self.look_back = look_back
        self.alpha = alpha

    def compute(self, book: LimitOrderBook, history: dict) -> float:
        """Compute the momentum trading signal.

        Args:
            book (LimitOrderBook): The current state of the limit order book.
            history (dict): The historical data for the simulation.

        Returns:
            float: The computed trading signal.
        """
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
        """Imbalance trading signal.

        Args:
            levels (int, optional): The number of levels to consider for the imbalance calculation. Defaults to 10.
        """
        self.levels = levels

    def compute(self, book: LimitOrderBook, history: dict) -> float:
        """Compute the imbalance trading signal.

        Args:
            book (LimitOrderBook): The current state of the limit order book.
            history (dict): The historical data for the simulation.

        Returns:
            float: The computed trading signal.
        """
        bid_size = book.get_bid_size(levels=self.levels)
        ask_size = book.get_ask_size(levels=self.levels)

        if bid_size + ask_size == 0:
            return 0.0  # Avoid division by zero

        imbalance = (bid_size - ask_size) / (bid_size + ask_size)

        return imbalance
