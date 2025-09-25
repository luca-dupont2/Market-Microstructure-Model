from collections import defaultdict
from .book import LimitOrderBook
from .events import TradeEvent, Event
import pandas as pd
from numpy import prod
from tabulate import tabulate

ANNUAL_TIME_SECONDS = 252 * 6.5 * 60 * 60  # 252 trading days, 6.5 hours each


class Metrics:
    def __init__(self):
        # Stores metrics as lists over time
        self.data = defaultdict(list)
        self.time = []

    def record(self, t, order_book: LimitOrderBook, events: list[Event] | None = None):
        """Record metrics at simulation time t.

        Args:
            t (float): Simulation time.
            order_book (LimitOrderBook): Current state of the order book.
            events (list[Event] | None, optional): List of events that occurred at time t. Defaults to None.
        """

        best_bid = order_book.best_bid().get_price() if order_book.bid_orders else None
        best_ask = order_book.best_ask().get_price() if order_book.ask_orders else None

        mid_price = order_book.mid_price() if best_bid and best_ask else None
        spread = order_book.get_spread() if best_bid and best_ask else None

        total_bid_size = order_book.get_bid_size()
        total_ask_size = order_book.get_ask_size()

        depth_bid = order_book.get_bid_depth()
        depth_ask = order_book.get_ask_depth()

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

    def get_dataframe(self) -> pd.DataFrame:
        """Return a pandas DataFrame for analysis or plotting.

        Returns:
            pd.DataFrame: DataFrame containing the recorded metrics.
        """
        import pandas as pd

        df = pd.DataFrame(self.data)
        df["time"] = self.time
        return df

    def get_returns(self) -> pd.Series:
        """Calculate and return the list of returns of the mid_price.

        Returns:
            pd.Series: Series containing the returns of the mid_price.
        """
        mid_prices = self.data.get("mid_price", [])
        if len(mid_prices) < 2:
            return pd.Series(dtype=float)

        returns = pd.Series(mid_prices).pct_change(fill_method=None).dropna()
        return returns

    def get_annualized_volatility(self) -> float:
        """Calculate and return the annualized volatility of the mid_price. Returns as a fraction.

        Returns:
            float: Annualized volatility of the mid_price.
        """
        returns = self.get_returns()
        if returns.empty:
            return 0.0

        time_interval = self.time[1] - self.time[0] if len(self.time) > 1 else 1.0

        std = returns.std()

        return (
            std * (ANNUAL_TIME_SECONDS / time_interval) ** 0.5
        )  # Annualized volatility

    def get_annualized_return(self) -> float:
        """Calculate and return the annualized return of the mid_price. Returns as a fraction.

        Returns:
            float: Annualized return of the mid_price.
        """
        returns = self.get_returns()
        if returns.empty:
            return 0.0

        cum_return = prod(1 + returns)

        total_time = self.time[-1] - self.time[0] if len(self.time) > 1 else 1.0

        return (
            (cum_return) ** (ANNUAL_TIME_SECONDS / total_time)
        ) - 1  # Annualized return

    def get_max_drawdown(self) -> float:
        """Calculate and return the maximum drawdown of the mid_price. Returns as a fraction.

        Returns:
            float: Maximum drawdown of the mid_price.
        """
        prices = pd.Series(self.data.get("mid_price", []))
        if prices.empty:
            return 0.0

        cum_returns = prices / prices.iloc[0]
        peak = cum_returns.cummax()

        drawdown = (cum_returns - peak) / peak
        return -drawdown.min()

    def get_annualized_sharpe(self, risk_free_rate: float = 0.0) -> float:
        """Calculate and return the annualized Sharpe ratio of the mid_price.

        Args:
            risk_free_rate (float, optional): Risk-free rate to use in the calculation. Defaults to 0.0.

        Returns:
            float: Annualized Sharpe ratio of the mid_price.
        """
        annualized_return = self.get_annualized_return()
        annualized_volatility = self.get_annualized_volatility()

        if annualized_volatility == 0:
            return 0.0

        return (annualized_return - risk_free_rate) / annualized_volatility

    def get_total_volume(self) -> float:
        """Calculate and return the total volume traded.

        Returns:
            float: Total volume traded.
        """
        return sum(self.data.get("volume", []))

    def get_number_of_trades(self) -> int:
        """Calculate and return the total number of trades executed.

        Returns:
            int: Total number of trades executed.
        """
        return sum(self.data.get("n_trades", []))

    def print_summary(self):
        """Print a summary of key metrics."""
        metrics = {
            "Annualized Return": f"{self.get_annualized_return():.3%}",
            "Annualized Volatility": f"{self.get_annualized_volatility():.2%}",
            "Sharpe Ratio": f"{self.get_annualized_sharpe():.2f}",
            "Max Drawdown": f"{self.get_max_drawdown():.2%}",
            "Total Volume": f"{self.get_total_volume()} shares",
            "Number of Trades": f"{self.get_number_of_trades()}",
        }

        print(
            tabulate(
                metrics.items(), headers=["Metric", "Value"], tablefmt="fancy_grid"
            )
        )

    def reset(self):
        """Reset all recorded metrics."""
        self.data = defaultdict(list)
        self.time = []
