from collections import defaultdict
import pandas as pd
from numpy import prod
from tabulate import tabulate

ANNUAL_TIME_SECONDS = 252 * 6.5 * 60 * 60


class StrategyMetrics:
    def __init__(self):
        self.data = defaultdict(list)
        self.time = []

    def record(self, t, strategy, order_book):
        """Record strategy performance metrics at simulation time t."""

        realized_pnl = strategy.realized_pnl()
        unrealized_pnl = strategy.unrealized_pnl(order_book)
        total_pnl = strategy.total_pnl(order_book)

        equity = strategy.cash + strategy.inventory * order_book.mid_price()

        avg_slippage = strategy.compute_average_slippage()
        total_slippage = strategy.compute_total_slippage()

        n_trades = len(strategy.trades)

        # Record values
        self.time.append(t)
        self.data["cash"].append(strategy.cash)
        self.data["inventory"].append(strategy.inventory)
        self.data["realized_pnl"].append(realized_pnl)
        self.data["unrealized_pnl"].append(unrealized_pnl)
        self.data["total_pnl"].append(total_pnl)
        self.data["equity"].append(equity)
        self.data["avg_slippage"].append(avg_slippage)
        self.data["total_slippage"].append(total_slippage)
        self.data["n_trades"].append(n_trades)

    def get_dataframe(self):
        df = pd.DataFrame(self.data)
        df["time"] = self.time
        return df

    def get_returns(self) -> pd.Series:
        equity = self.data.get("equity", [])
        if len(equity) < 2:
            return pd.Series(dtype=float)

        returns = pd.Series(equity).pct_change(fill_method=None).dropna()
        return returns

    def get_equity_curve(self) -> pd.Series:
        """Return normalized equity curve starting at 1.0."""
        equity = pd.Series(self.data.get("equity", []))
        if equity.empty:
            return equity

        return equity / equity.iloc[0]

    def get_annualized_volatility(self) -> float:
        returns = self.get_returns()
        if returns.empty:
            return 0.0

        time_interval = self.time[1] - self.time[0] if len(self.time) > 1 else 1.0
        return returns.std() * (ANNUAL_TIME_SECONDS / time_interval) ** 0.5

    def get_annualized_return(self) -> float:
        returns = self.get_returns()
        if returns.empty:
            return 0.0

        cum_return = prod(1 + returns)
        total_time = self.time[-1] - self.time[0] if len(self.time) > 1 else 1.0
        return cum_return ** (ANNUAL_TIME_SECONDS / total_time) - 1

    def get_max_drawdown(self) -> float:
        equity = pd.Series(self.data.get("equity", []))
        if equity.empty:
            return 0.0

        curve = equity / equity.iloc[0]
        peak = curve.cummax()
        drawdown = (curve - peak) / peak
        return drawdown.min()

    def get_annualized_sharpe(self, risk_free_rate: float = 0.0) -> float:
        ann_ret = self.get_annualized_return()
        ann_vol = self.get_annualized_volatility()
        if ann_vol == 0:
            return 0.0
        return (ann_ret - risk_free_rate) / ann_vol

    def print_summary(self):
        metrics = {
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
            "Annualized Return": f"{100*self.get_annualized_return():.5f} %",
            "Annualized Volatility": f"{100*self.get_annualized_volatility():.2f} %",
            "Sharpe Ratio": f"{self.get_annualized_sharpe():.2f}",
            "Max Drawdown": f"{100*self.get_max_drawdown():.2f} %",
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
        self.data = defaultdict(list)
        self.time = []
