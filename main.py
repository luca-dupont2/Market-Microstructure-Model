from src.engine import Simulator, OrderSide
from src.config import CONFIG
from src.utils import plotting, RNG
from src.strategies import TWAPSingleTaker

seed = CONFIG["SIM_PARAMS"]["random_seed"]

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

simulator = Simulator(CONFIG, rng, agents=[twap_taker])
simulator.populate_initial_book(n_orders=1000)

simulator.run()

metrics = simulator.metrics.get_dataframe()
order_book_snapshot = simulator.order_book.get_dataframe()

# simulator.save_order_book("example-orderbook.csv")
# simulator.save_metrics("example-metrics.csv")

print("\nTWAP Taker results")

print(f"Taker PnL: {twap_taker.total_pnl(simulator.order_book.mid_price())}")
print(f"Taker Avg Slippage: {twap_taker.compute_average_slippage():.2f} $/share")
print(f"Taker Total Slippage: {twap_taker.compute_total_slippage():.2f} $")

plotting.plot_all(metrics, order_book_snapshot)
