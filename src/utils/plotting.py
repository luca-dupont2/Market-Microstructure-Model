import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import widgets
import numpy as np
from datetime import datetime


def plot_price(
    book_metrics_df: pd.DataFrame, title: str = "Price Evolution", save: bool = False
):
    """Plot the price evolution of the order book.

    Args:
        book_metrics_df (pd.DataFrame): DataFrame containing the order book metrics.
        title (str, optional): Title of the plot. Defaults to "Price Evolution".
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    line_colors = ["blue", "green", "red"]
    lines = {}
    (lines["Mid Price"],) = ax.plot(
        book_metrics_df["time"],
        book_metrics_df["mid_price"],
        label="Mid Price",
        color=line_colors[0],
    )
    (lines["Best Bid"],) = ax.plot(
        book_metrics_df["time"],
        book_metrics_df["best_bid"],
        label="Best Bid",
        color=line_colors[1],
        linestyle="--",
    )
    (lines["Best Ask"],) = ax.plot(
        book_metrics_df["time"],
        book_metrics_df["best_ask"],
        label="Best Ask",
        color=line_colors[2],
        linestyle="--",
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Price")
    ax.set_title(title)
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.grid(True, alpha=0.3)

    # Place interactive checkboxes to toggle lines
    rax = plt.axes((0.85, 0.5, 0.15, 0.15))  # x, y, width, height in figure coords
    labels = list(lines.keys())
    visibility = [line.get_visible() for line in lines.values()]
    check = widgets.CheckButtons(
        rax,
        labels,
        visibility,
        label_props={"color": line_colors},
        frame_props={"edgecolor": line_colors},
        check_props={"facecolor": line_colors},
    )

    def toggle(label):
        line = lines[label]
        line.set_visible(not line.get_visible())
        plt.draw()

    check.on_clicked(toggle)
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/price_evolution_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved price evolution plot as {filename}")


def plot_spread(
    book_metrics_df: pd.DataFrame,
    title: str = "Average Spread (20 Buckets)",
    save: bool = False,
):
    """Plot the average spread of the order book.

    Args:
        book_metrics_df (pd.DataFrame): DataFrame containing the order book metrics.
        title (str, optional): Title of the plot. Defaults to "Average Spread (20 Buckets)".
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    # Bin into 20 buckets
    time = book_metrics_df["time"].to_numpy()
    spread = book_metrics_df["spread"].to_numpy()
    bins = np.linspace(time.min(), time.max(), 21)  # 20 equal bins
    inds = np.digitize(time, bins) - 1

    avg_spreads = [
        spread[inds == i].mean() if np.any(inds == i) else 0 for i in range(20)
    ]
    bin_centers = (bins[:-1] + bins[1:]) / 2

    ax.bar(bin_centers, avg_spreads, width=(bins[1] - bins[0]) * 0.8, color="purple")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Average Spread")
    ax.set_title(title)
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.grid(True, which="both", axis="y", alpha=0.3)
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/average_spread_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved average spread plot as {filename}")


def plot_volume(
    book_metrics_df: pd.DataFrame,
    title: str = "Average Volume (20 Buckets)",
    save: bool = False,
):
    """Plot the average volume of the order book.

    Args:
        book_metrics_df (pd.DataFrame): DataFrame containing the order book metrics.
        title (str, optional): Title of the plot. Defaults to "Average Volume (20 Buckets)".
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    # Bin into 20 buckets
    time = book_metrics_df["time"].to_numpy()
    volume = book_metrics_df["volume"].to_numpy()
    bins = np.linspace(time.min(), time.max(), 21)  # 20 equal bins
    inds = np.digitize(time, bins) - 1

    avg_volumes = [
        volume[inds == i].mean() if np.any(inds == i) else 0 for i in range(20)
    ]
    bin_centers = (bins[:-1] + bins[1:]) / 2

    ax.bar(bin_centers, avg_volumes, width=(bins[1] - bins[0]) * 0.8, color="orange")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Average Volume")
    ax.set_title(title)
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.grid(True, which="both", axis="y", alpha=0.3)
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/average_volume_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved average volume plot as {filename}")


def plot_depth(
    book_metrics_df: pd.DataFrame,
    title: str = "Order Book Depth",
    save: bool = False,
):
    """Plot the depth of the order book.

    Args:
        book_metrics_df (pd.DataFrame): DataFrame containing the order book metrics.
        title (str, optional): Title of the plot. Defaults to "Order Book Depth".
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        book_metrics_df["time"],
        book_metrics_df["depth_bid"],
        label="Bid Depth",
        color="green",
    )
    ax.plot(
        book_metrics_df["time"],
        book_metrics_df["depth_ask"],
        label="Ask Depth",
        color="red",
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Number of Orders")
    ax.set_title(title)
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/order_book_depth_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved order book depth plot as {filename}")


def plot_order_size_and_price_hists(
    snapshot_df: pd.DataFrame,
    size_title: str = "Order Size Histogram",
    price_title: str = "Order Price Histogram",
    save: bool = False,
):
    """Plot side-by-side histograms for order sizes and order price levels from a snapshot.

    Args:
        snapshot_df (pd.DataFrame): DataFrame containing the snapshot data.
        size_title (str, optional): Title for the order size histogram. Defaults to "Order Size Histogram".
        price_title (str, optional): Title for the order price histogram. Defaults to "Order Price Histogram".
        save (_type_, optional): _description_. Defaults to False.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Order Size Histogram
    axes[0].hist(snapshot_df["size"], bins=10, color="skyblue", edgecolor="black")
    axes[0].set_xlabel("Order Size")
    axes[0].set_ylabel("Frequency")
    axes[0].set_title(size_title)
    axes[0].grid(True, linestyle="--", alpha=0.6)

    # Order Price Histogram
    axes[1].hist(snapshot_df["price"], bins=20, color="lightgreen", edgecolor="black")
    axes[1].set_xlabel("Price Level")
    axes[1].set_ylabel("Number of Orders")
    axes[1].set_title(price_title)
    axes[1].grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/order_size_price_histograms_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved order size and price histograms as {filename}")


def plot_book_drawdown(
    book_metrics_df: pd.DataFrame,
    title: str = "Mid Price Drawdown Curve",
    save: bool = False,
):
    """Plot the drawdown of the mid price over time.

    Args:
        book_metrics_df (pd.DataFrame): DataFrame containing the book metrics.
        title (str, optional): Title of the plot. Defaults to "Mid Price Drawdown Curve".
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    mid_prices = book_metrics_df["mid_price"].to_numpy()
    if mid_prices.size == 0:
        return

    curve = mid_prices / mid_prices[0]
    peak = np.maximum.accumulate(curve)
    drawdown = (curve - peak) / peak

    ax.fill_between(
        book_metrics_df["time"], drawdown, color="red", alpha=0.4, step="mid"
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Drawdown (fraction)")
    ax.set_title(title)

    max_dd = drawdown.min()
    ax.annotate(
        f"Max Drawdown: {max_dd:.2%}",
        xy=(book_metrics_df["time"].iloc[np.argmin(drawdown)], max_dd),
        xytext=(0.7, 0.9),
        textcoords="axes fraction",
        fontsize=12,
        color="darkred",
        arrowprops=dict(arrowstyle="->", color="darkred"),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="darkred", alpha=0.7),
    )
    ax.grid(True, alpha=0.3)
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/mid_price_drawdown_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved mid price drawdown plot as {filename}")


def plot_book_all(
    book_metrics_df: pd.DataFrame,
    snapshot_df: pd.DataFrame | None = None,
    save: bool = False,
):
    """Plot all relevant book metrics.

    Args:
        book_metrics_df (pd.DataFrame): DataFrame containing the book metrics.
        snapshot_df (pd.DataFrame | None, optional): DataFrame containing the snapshot data. Defaults to None.
        save (bool, optional): Whether to save the plots. Defaults to False.
    """
    plot_price(book_metrics_df, save=save)
    plot_book_drawdown(book_metrics_df, save=save)
    plot_spread(book_metrics_df, save=save)
    plot_volume(book_metrics_df, save=save)
    plot_depth(book_metrics_df, save=save)

    if snapshot_df is not None:
        plot_order_size_and_price_hists(snapshot_df, save=save)


def plot_equity_curve(
    strategy_metrics_df: pd.DataFrame,
    title: str = "Equity Curve",
    strategy_id: str | int | None = None,
    save: bool = False,
):
    """Plot the equity curve of a trading strategy.

    Args:
        strategy_metrics_df (pd.DataFrame): DataFrame containing the strategy metrics.
        title (str, optional): Title of the plot. Defaults to "Equity Curve".
        strategy_id (str | int | None, optional): ID of the strategy. Defaults to None.
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    if strategy_id is not None:
        title = f"{title} - {strategy_id}"

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        strategy_metrics_df["time"],
        strategy_metrics_df["equity"],
        label="Equity",
        color="blue",
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Equity ($)")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/equity_curve_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved equity curve plot as {filename}")


def plot_pnl(
    strategy_metrics_df: pd.DataFrame,
    title: str = "PnL Breakdown",
    strategy_id: str | int | None = None,
    save: bool = False,
):
    """Plot the PnL breakdown of a trading strategy.

    Args:
        strategy_metrics_df (pd.DataFrame): DataFrame containing the strategy metrics.
        title (str, optional): Title of the plot. Defaults to "PnL Breakdown".
        strategy_id (str | int | None, optional): ID of the strategy. Defaults to None.
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    if strategy_id is not None:
        title = f"{title} - {strategy_id}"

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        strategy_metrics_df["time"],
        strategy_metrics_df["realized_pnl"],
        label="Realized PnL",
        color="green",
    )
    ax.plot(
        strategy_metrics_df["time"],
        strategy_metrics_df["unrealized_pnl"],
        label="Unrealized PnL",
        color="orange",
    )
    ax.plot(
        strategy_metrics_df["time"],
        strategy_metrics_df["total_pnl"],
        label="Total PnL",
        color="blue",
        linewidth=2,
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("PnL ($)")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/pnl_breakdown_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved PnL breakdown plot as {filename}")


def plot_inventory_and_cash(
    strategy_metrics_df: pd.DataFrame,
    title: str = "Cash & Inventory Evolution",
    strategy_id: str | int | None = None,
    save: bool = False,
):
    """Plot the cash and inventory evolution of a trading strategy.

    Args:
        strategy_metrics_df (pd.DataFrame): DataFrame containing the strategy metrics.
        title (str, optional): Title of the plot. Defaults to "Cash & Inventory Evolution".
        strategy_id (str | int | None, optional): ID of the strategy. Defaults to None.
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    if strategy_id is not None:
        title = f"{title} - {strategy_id}"

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        strategy_metrics_df["time"],
        strategy_metrics_df["cash"],
        label="Cash",
        color="blue",
    )
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Cash ($)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    ax2 = ax1.twinx()
    ax2.plot(
        strategy_metrics_df["time"],
        strategy_metrics_df["inventory"],
        label="Inventory",
        color="red",
    )
    ax2.set_ylabel("Inventory (shares)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    fig.suptitle(title)
    ax1.grid(True, alpha=0.3)
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/cash_inventory_evolution_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved cash and inventory evolution plot as {filename}")


def plot_strategy_drawdown(
    strategy_metrics_df: pd.DataFrame,
    title: str = "Drawdown Curve",
    strategy_id: str | int | None = None,
    save: bool = False,
):
    """Plot the drawdown curve of a trading strategy.

    Args:
        strategy_metrics_df (pd.DataFrame): DataFrame containing the strategy metrics.
        title (str, optional): Title of the plot. Defaults to "Drawdown Curve".
        strategy_id (str | int | None, optional): ID of the strategy. Defaults to None.
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    if strategy_id is not None:
        title = f"{title} - {strategy_id}"

    equity = strategy_metrics_df["equity"].to_numpy()
    if equity.size == 0:
        return

    curve = equity / equity[0]
    peak = np.maximum.accumulate(curve)
    drawdown = (curve - peak) / peak

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.fill_between(
        strategy_metrics_df["time"], drawdown, color="red", alpha=0.4, step="mid"
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Drawdown (fraction)")
    ax.set_title(title)

    max_dd = drawdown.min()
    ax.annotate(
        f"Max Drawdown: {max_dd:.2%}",
        xy=(strategy_metrics_df["time"].iloc[np.argmin(drawdown)], max_dd),
        xytext=(0.7, 0.9),
        textcoords="axes fraction",
        fontsize=12,
        color="darkred",
        arrowprops=dict(arrowstyle="->", color="darkred"),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="darkred", alpha=0.7),
    )

    ax.grid(True, alpha=0.3)
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/strategy_drawdown_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved strategy drawdown plot as {filename}")


def plot_return_histogram(
    strategy_metrics_df: pd.DataFrame,
    title: str = "Distribution of Returns",
    strategy_id: str | int | None = None,
    save: bool = False,
):
    """Plot the distribution of returns for a trading strategy.

    Args:
        strategy_metrics_df (pd.DataFrame): DataFrame containing the strategy metrics.
        title (str, optional): Title of the plot. Defaults to "Distribution of Returns".
        strategy_id (str | int | None, optional): ID of the strategy. Defaults to None.
        save (bool, optional): Whether to save the plot. Defaults to False.
    """
    if strategy_id is not None:
        title = f"{title} - {strategy_id}"

    equity = strategy_metrics_df["equity"].to_numpy()
    if equity.size < 2:
        return

    returns = np.diff(equity) / equity[:-1]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(returns, bins=30, color="purple", edgecolor="black", alpha=0.7)
    ax.set_xlabel("Return")
    ax.set_ylabel("Frequency")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    plt.show()

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"images/return_histogram_{timestamp}.png"
        fig.savefig(filename)
        print(f"Saved return histogram plot as {filename}")


def plot_strategy_all(
    strategy_metrics_df: pd.DataFrame,
    strategy_id: str | int | None = None,
    save: bool = False,
):
    """Plot all relevant metrics for a trading strategy.

    Args:
        strategy_metrics_df (pd.DataFrame): DataFrame containing the strategy metrics.
        strategy_id (str | int | None, optional): ID of the strategy. Defaults to None.
        save (bool, optional): Whether to save the plots. Defaults to False.
    """
    plot_equity_curve(strategy_metrics_df, strategy_id=strategy_id, save=save)
    plot_pnl(strategy_metrics_df, strategy_id=strategy_id, save=save)
    plot_inventory_and_cash(strategy_metrics_df, strategy_id=strategy_id, save=save)
    plot_strategy_drawdown(strategy_metrics_df, strategy_id=strategy_id, save=save)
    plot_return_histogram(strategy_metrics_df, strategy_id=strategy_id, save=save)


def plot_all(
    book_metrics_df: pd.DataFrame,
    snapshot_df: pd.DataFrame | None,
    strategy_metrics_df: pd.DataFrame,
    strategy_id: str | int | None = None,
    save: bool = False,
):
    """Plot all relevant metrics for a trading strategy.

    Args:
        book_metrics_df (pd.DataFrame): DataFrame containing the book metrics.
        snapshot_df (pd.DataFrame | None): DataFrame containing the snapshot metrics.
        strategy_metrics_df (pd.DataFrame): DataFrame containing the strategy metrics.
        strategy_id (str | int | None, optional): ID of the strategy. Defaults to None.
        save (bool, optional): Whether to save the plots. Defaults to False.
    """
    plot_book_all(book_metrics_df, snapshot_df, save=save)
    plot_strategy_all(strategy_metrics_df, strategy_id=strategy_id, save=save)
