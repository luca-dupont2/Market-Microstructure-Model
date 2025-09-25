from src.engine import Simulator
from src.config import CONFIG
from src.utils import plotting, RNG
from src.strategies import BlockExecution, SymmetricMaker

seed = CONFIG["SIM_PARAMS"]["random_seed"]
intervals = CONFIG["STRATEGY_PARAMS"]["taker"]["twap"]["intervals"]
duration = CONFIG["STRATEGY_PARAMS"]["taker"]["twap"]["duration"]

rng = RNG(seed)

execution_strategy = BlockExecution(rng)

maker = SymmetricMaker(
    execution_strategy=execution_strategy,
    quote_size=10,
    max_inventory=100,
    quote_update_interval=3,
    record_metrics=True,
    id="Symmetric_Maker_1",
    initial_cash=10_000,
    initial_inventory=0,
    config=CONFIG,
)

simulator = Simulator(CONFIG, rng, agents=[maker])
simulator.populate_initial_book_rand(n_levels=20, orders_per_level=50)

simulator.run()

book_metrics = simulator.metrics.get_dataframe()
order_book_snapshot = simulator.order_book.get_dataframe()

simulator.save_order_book()
simulator.save_metrics()
simulator.metrics.print_summary()

if maker.metrics:
    maker.metrics.print_summary()
    maker_metrics = maker.metrics.get_dataframe()

    plotting.plot_all(book_metrics, maker_metrics, maker.id, order_book_snapshot, save=True)
