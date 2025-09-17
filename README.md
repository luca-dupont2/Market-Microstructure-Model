# Market Microstructure Simulator

A **market microstructure simulation framework** for modeling limit order books, order flow, and agent-based trading strategies.  
This project is designed for experimenting with **execution quality**, **PnL dynamics**, and **liquidity provision/taking** in realistic trading environments.

---

## Features

-   **Limit Order Book (LOB)**

    -   Supports limit, market, and cancel events.
    -   Tracks order queue dynamics at each price level.

-   **Order Flow Generators**

    -   Configurable noise traders with customizable arrival and size distributions.
    -   Bernoulli discrete arrivals, lognormal size, and discrete Zipf/geometric price distributions.

-   **Agent-Based Strategies**

    -   **Market Makers** (quote provision, spread control).
    -   **Liquidity Takers**.
    -   Easily extendable via a `BaseStrategy` interface.

-   **Execution Algorithms**

    -   **TWAP** (Time-Weighted Average Price).
    -   Custom scheduling logic supported.

-   **Performance Tracking**

    -   Realized and unrealized **PnL**.
    -   **Inventory risk** exposure.
    -   **Slippage**: average per share and total cost.

-   **Extensible & Modular**
    -   Add new order flow models, trading strategies, or execution algorithms with minimal boilerplate.

---

## Project Structure

```
market-microstructure/
│── data/                    # Metrics and snapshots
│── logs/                    # Simulation logs
│── src/                     # Core implementation
│   ├── config.py            # Simulation parameters
│   ├── orderflow/           # Random/noise order generators & distributions
│   ├── strategies/          # Agent-based strategies (makers, takers, execution algos)
│       ├── market_maker.py  # Market-making strategies
│       ├── taker.py         # Liquidity-taking strategies
│   ├── engine/              # Core simulation engine & limit order book
│   ├── utils/               # Helpers, logging, config
│       ├── plotting.py      # Plotting
│── main.py                  # Example simulation runner
│── requirements.txt         # Project requirements
```

---

## Example Usage

```python
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

manual_taker.schedule_order(7200, 300, OrderSide.BUY)

simulator = Simulator(CONFIG, rng, agents=[manual_taker])
simulator.populate_initial_book_rand(n_levels=25, orders_per_level=5)

simulator.run()

metrics = simulator.metrics.get_dataframe()
order_book_snapshot = simulator.order_book.get_dataframe()

simulator.save_order_book()
simulator.save_metrics()

manual_taker.print_summary(simulator.order_book)
simulator.metrics.print_summary()

plotting.plot_all(metrics, order_book_snapshot)

```

## Metrics

The simulator automatically records useful metrics for each strategy and the whole market.

### Strategy metrics

-   PnL
-   Inventory (long/short exposure)
-   Slippage
    -   Average per share (execution quality)
    -   Total cost (absolute PnL impact)

### Market metrics

> Visualizations with `plotting.py`

-   Best bids, asks, and mid prices
-   Spread
-   Bid and ask size
-   Bid and ask depth
-   Trade volume
-   Number of trades

## Installation

```bash
git clone https://github.com/yourusername/market-microstructure.git
cd market-microstructure
pip install -r requirements.txt
```

## Roadmap

-   Extend trading agents (momentum, noise taker, reinforcement-learning)
-   Extend execution algos (IS, POV, VWAP)
-   Extend strategy metrics
-   Real market data replay support

## License

MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you’d like to add a feature or improve the simulator.
