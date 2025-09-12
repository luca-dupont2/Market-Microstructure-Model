from src.engine import Simulator, OrderSide
from src.config import CONFIG
from src.utils import plotting, RNG
from src.strategies import ManualTaker, TWAPExecution

seed = CONFIG["SIM_PARAMS"]["random_seed"]
intervals = CONFIG["STRATEGY_PARAMS"]["taker"]["twap"]["intervals"]
duration = CONFIG["STRATEGY_PARAMS"]["taker"]["twap"]["duration"]

rng = RNG(seed)

execution_strategy = TWAPExecution(rng, intervals=intervals, duration=duration)

manual_taker = ManualTaker(
    initial_cash=100_000,
    initial_inventory=0,
    id="Manual_Taker_1",
    execution_strategy=execution_strategy,
)

manual_taker.schedule_order(1800, 600, OrderSide.BUY)

simulator = Simulator(CONFIG, rng, agents=[manual_taker])
simulator.populate_initial_book(n_orders=500)

simulator.run()

metrics = simulator.metrics.get_dataframe()
order_book_snapshot = simulator.order_book.get_dataframe()

simulator.save_order_book()
simulator.save_metrics()

print("\nManual Taker results with TWAP Execution")

print(f"Taker PnL: {manual_taker.total_pnl(simulator.order_book.mid_price())}")
print(f"Taker Avg Slippage: {manual_taker.compute_average_slippage():.2f} $/share")
print(f"Taker Total Slippage: {manual_taker.compute_total_slippage():.2f} $")

plotting.plot_all(metrics, order_book_snapshot)
