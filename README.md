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
    -   **Risk** exposure.
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

```

## Metrics

The simulator automatically records useful metrics for each strategy and for the whole market.

> Visualizations with `plotting.py`

-   PnL
-   Inventory (long/short exposure)
-   Slippage
    -   Average per share (execution quality)
    -   Total cost (absolute PnL impact)
-   Best bids, asks, and mid prices
-   Spread
-   Bid and ask size and depth
-   Trade volume
-   Number of trades
-   Annualized volatility and returns
-   Sharpe Ratio
-   Max Drawdown

## Installation

```bash
git clone https://github.com/luca-dupont2/Market-Microstructure-Model.git
cd Market-Microstructure-Model
pip install -r requirements.txt
```

## Roadmap

-   Extend trading agents (noise taker, reinforcement-learning)
-   Extend market making strategy (Avellaneda-Stoikov model)
-   Extend execution algos (IS, POV, VWAP)
-   Extend metrics
-   Real market data replay support
-   Implement Streamlit dashboard for real-time monitoring and parameter tuning

## License

MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you’d like to add a feature or improve the simulator.
