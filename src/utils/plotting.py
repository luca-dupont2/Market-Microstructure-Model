import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import numpy as np


def plot_price(df, title="Price Evolution"):
    fig, ax = plt.subplots(figsize=(12, 6))

    line_colors = ["blue", "green", "red"]
    lines = {}
    (lines["Mid Price"],) = ax.plot(
        df["time"], df["mid_price"], label="Mid Price", color=line_colors[0]
    )
    (lines["Best Bid"],) = ax.plot(
        df["time"],
        df["best_bid"],
        label="Best Bid",
        color=line_colors[1],
        linestyle="--",
    )
    (lines["Best Ask"],) = ax.plot(
        df["time"],
        df["best_ask"],
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


def plot_spread(df, title="Average Spread (20 Buckets)"):
    fig, ax = plt.subplots(figsize=(10, 5))

    # Bin into 20 buckets
    time = df["time"].to_numpy()
    spread = df["spread"].to_numpy()
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


def plot_volume(df, title="Average Volume (20 Buckets)"):
    fig, ax = plt.subplots(figsize=(10, 5))

    # Bin into 20 buckets
    time = df["time"].to_numpy()
    volume = df["volume"].to_numpy()
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


def plot_depth(df, title="Order Book Depth"):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["time"], df["depth_bid"], label="Bid Depth", color="green")
    ax.plot(df["time"], df["depth_ask"], label="Ask Depth", color="red")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Number of Orders")
    ax.set_title(title)
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.show()


def plot_order_size_and_price_hists(
    snapshot_df, size_title="Order Size Histogram", price_title="Order Price Histogram"
):
    """Plot side-by-side histograms for order sizes and order price levels from a snapshot."""
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


def plot_all(metrics_df, snapshot_df=None):
    """Convenience function to plot multiple key metrics."""
    plot_price(metrics_df)
    plot_spread(metrics_df)
    plot_volume(metrics_df)
    plot_depth(metrics_df)

    if snapshot_df is not None:
        plot_order_size_and_price_hists(snapshot_df)
