from collections import defaultdict
import pandas as pd
from numpy import prod
from .base_strategy import BaseStrategy
from tabulate import tabulate
from ..engine import LimitOrderBook

ANNUAL_TIME_SECONDS = 252 * 6.5 * 60 * 60


class StrategyMetrics:
    def __init__(self, id: str | int):
        """Initialize strategy metrics.

        Args:
            id (str | int): Identifier for the strategy.
        """
        self.data = defaultdict(list)
        self.time = []
        self.id = id

    def record(self, time: float, strategy: BaseStrategy, order_book: LimitOrderBook):
        """Record strategy performance metrics at simulation time t.

        Args:
            time (float): The simulation time.
            strategy (BaseStrategy): The trading strategy being evaluated.
            order_book (LimitOrderBook): The current state of the limit order book.
        """
        realized_pnl = strategy.realized_pnl()
        unrealized_pnl = strategy.unrealized_pnl(order_book)
        total_pnl = strategy.total_pnl(order_book)

        equity = strategy.cash + strategy.inventory * order_book.mid_price()

        avg_slippage = strategy.compute_average_slippage()
        total_slippage = strategy.compute_total_slippage()

        n_trades = len(strategy.trades)

        # Record values
        self.time.append(time)
        self.data["cash"].append(strategy.cash)
        self.data["inventory"].append(strategy.inventory)
        self.data["realized_pnl"].append(realized_pnl)
        self.data["unrealized_pnl"].append(unrealized_pnl)
        self.data["total_pnl"].append(total_pnl)
        self.data["equity"].append(equity)
        self.data["avg_slippage"].append(avg_slippage)
        self.data["total_slippage"].append(total_slippage)
        self.data["n_trades"].append(n_trades)

    def get_dataframe(self) -> pd.DataFrame:
        """Get the strategy performance metrics as a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the recorded metrics.
        """
        df = pd.DataFrame(self.data)
        df["time"] = self.time
        return df

    def get_returns(self) -> pd.Series:
        """Get the strategy returns.

        Returns:
            pd.Series: Series of strategy returns.
        """
        equity = self.data.get("equity", [])
        if len(equity) < 2:
            return pd.Series(dtype=float)

        returns = pd.Series(equity).pct_change(fill_method=None).dropna()
        return returns

    def get_equity_curve(self) -> pd.Series:
        """Get the normalized equity curve starting at 1.0.

        Returns:
            pd.Series: Normalized equity curve.
        """
        equity = pd.Series(self.data.get("equity", []))
        if equity.empty:
            return equity

        return equity / equity.iloc[0]

    def get_annualized_volatility(self) -> float:
        """Get the annualized volatility of the strategy returns.

        Returns:
            float: Annualized volatility.
        """
        returns = self.get_returns()
        if returns.empty:
            return 0.0

        time_interval = self.time[1] - self.time[0] if len(self.time) > 1 else 1.0
        return returns.std() * (ANNUAL_TIME_SECONDS / time_interval) ** 0.5

    def get_annualized_return(self) -> float:
        """Get the annualized return of the strategy.

        Returns:
            float: Annualized return.
        """
        returns = self.get_returns()
        if returns.empty:
            return 0.0

        cum_return = prod(1 + returns)
        total_time = self.time[-1] - self.time[0] if len(self.time) > 1 else 1.0
        return cum_return ** (ANNUAL_TIME_SECONDS / total_time) - 1

    def get_max_drawdown(self) -> float:
        """Get the maximum drawdown of the strategy.

        Returns:
            float: Maximum drawdown.
        """
        equity = pd.Series(self.data.get("equity", []))
        if equity.empty:
            return 0.0

        curve = equity / equity.iloc[0]
        peak = curve.cummax()
        drawdown = (curve - peak) / peak
        return drawdown.min()

    def get_annualized_sharpe(self, risk_free_rate: float = 0.0) -> float:
        """Get the annualized Sharpe ratio of the strategy.

        Args:
            risk_free_rate (float, optional): Risk-free rate. Defaults to 0.0.

        Returns:
            float: Annualized Sharpe ratio.
        """
        ann_ret = self.get_annualized_return()
        ann_vol = self.get_annualized_volatility()
        if ann_vol == 0:
            return 0.0
        return (ann_ret - risk_free_rate) / ann_vol

    def print_summary(self):
        """Print a summary of the strategy performance metrics."""
        metrics = {
            "Strategy ID": self.id,
            "Final Cash": f"${self.data['cash'][-1]:.2f}" if self.data["cash"] else "-",
            "Final Inventory": (
                f"{self.data['inventory'][-1]} shares"
                if self.data["inventory"]
                else "-"
            ),
            "Realized PnL": (
                f"${self.data['realized_pnl'][-1]:.2f}"
                if self.data["realized_pnl"]
                else "-"
            ),
            "Unrealized PnL": (
                f"${self.data['unrealized_pnl'][-1]:.2f}"
                if self.data["unrealized_pnl"]
                else "-"
            ),
            "Total PnL": (
                f"${self.data['total_pnl'][-1]:.2f}" if self.data["total_pnl"] else "-"
            ),
            "Annualized Return": f"{self.get_annualized_return():.3%}",
            "Annualized Volatility": f"{self.get_annualized_volatility():.2%}",
            "Sharpe Ratio": f"{self.get_annualized_sharpe():.2f}",
            "Max Drawdown": f"{self.get_max_drawdown():.2%}",
            "Average Slippage": (
                f"{self.data['avg_slippage'][-1]:.4f}"
                if self.data["avg_slippage"]
                else "-"
            ),
            "Total Slippage": (
                f"{self.data['total_slippage'][-1]:.2f}"
                if self.data["total_slippage"]
                else "-"
            ),
            "Number of Trades": (
                f"{self.data['n_trades'][-1]}" if self.data["n_trades"] else "0"
            ),
        }

        print(
            tabulate(
                metrics.items(), headers=["Metric", "Value"], tablefmt="fancy_grid"
            )
        )

    def reset(self):
        """Reset the strategy metrics."""
        self.data = defaultdict(list)
        self.time = []
