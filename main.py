from src.engine import Simulator, OrderSide
from src.config import CONFIG
from src.utils import plotting, RNG
from src.strategies import TWAPSingleTaker, SingleTaker

import sys


def main(seed=42):
    CONFIG["SIM_PARAMS"]["random_seed"] = seed

    rng = RNG(seed)

    twap_taker = TWAPSingleTaker(
        rng=rng,
        config=CONFIG,
        initial_cash=100_000,
        initial_inventory=0,
        id="TWAP_Taker_1",
    )

    twap_taker.schedule_twap(
        schedule_time=1800.0,
        current_price=CONFIG["SIM_PARAMS"]["initial_price"],
        total_volume=600,
        side=OrderSide.BUY,
    )

    single_taker = SingleTaker(
        rng=rng,
        config=CONFIG,
        initial_cash=100_000,
        initial_inventory=0,
        id="Single_Taker_1",
    )

    single_taker.schedule_order(
        schedule_time=1800.0,
        current_price=CONFIG["SIM_PARAMS"]["initial_price"],
        volume=600,
        side=OrderSide.BUY,
    )

    simulator = Simulator(CONFIG, rng, agents=[single_taker])
    simulator.populate_initial_book(n_orders=1000)

    simulator.run()

    # metrics = simulator.metrics.get_dataframe()

    # order_book_snapshot = simulator.order_book.get_dataframe()

    # simulator.save_order_book()

    # simulator.save_metrics()

    print("\nSingle Taker results")

    print(f"Taker PnL: {single_taker.total_pnl(simulator.order_book.mid_price())}")
    print(f"Taker Avg Slippage: {single_taker.compute_average_slippage():.2f} $/share")
    print(f"Taker Total Slippage: {single_taker.compute_total_slippage():.2f} $\n")

    simulator.reset(agents=[twap_taker])
    simulator.populate_initial_book(n_orders=1000)

    simulator.run()

    print("\nTWAP Taker results")

    print(f"Taker PnL: {twap_taker.total_pnl(simulator.order_book.mid_price())}")
    print(f"Taker Avg Slippage: {twap_taker.compute_average_slippage():.2f} $/share")
    print(f"Taker Total Slippage: {twap_taker.compute_total_slippage():.2f} $")

    # plotting.plot_all(metrics, order_book_snapshot)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        seed = int(sys.argv[1])
        main(seed)
    else:
        main()
