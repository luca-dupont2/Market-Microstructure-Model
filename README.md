# 📈 Market Microstructure Simulator  

A **market microstructure simulation framework** for modeling limit order books, order flow, and agent-based trading strategies.  
This project is designed for experimenting with **execution quality**, **PnL dynamics**, and **liquidity provision/taking** in realistic trading environments.  

---

## 🚀 Features  

- 📊 **Limit Order Book (LOB)**  
  - Supports limit, market, and cancel events.  
  - Tracks order queue dynamics at each price level.  

- 🎲 **Order Flow Generators**  
  - Configurable noise traders with customizable arrival and size distributions.  
  - Poisson arrivals, uniform/lognormal size distributions, and more.  

- 🤖 **Agent-Based Strategies**  
  - **Market Makers** (quote provision, spread control).  
  - **Liquidity Takers** (VWAP, TWAP execution, momentum traders, noise takers).  
  - Easily extendable via a `BaseStrategy` interface.  

- ⚡ **Execution Algorithms**  
  - **TWAP** (Time-Weighted Average Price).  
  - **VWAP** (Volume-Weighted Average Price).  
  - Custom scheduling logic supported.  

- 💹 **Performance Tracking**  
  - Realized and unrealized **PnL**.  
  - **Inventory risk** exposure.  
  - **Slippage**: average per share and total cost.  

- 🧩 **Extensible & Modular**  
  - Add new order flow models or trading strategies with minimal boilerplate.  

---

## 📂 Project Structure  
```
market-microstructure/
│── orderflow/           # Random/noise order generators & distributions
│── strategies/          # Agent-based strategies (makers, takers, execution algos)
│   ├── base_strategy.py # Abstract base for all strategies
│   ├── market_maker.py  # Market-making strategies
│   ├── taker.py         # Liquidity-taking strategies
│── engine/              # Core simulation engine & limit order book
│── utils/               # Helpers, logging, config
│── main.py              # Example simulation runner
```

---

## 📊 Example Usage  

```python
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

simulator = Simulator(CONFIG, rng, agents=[single_taker])
simulator.populate_initial_book(n_orders=1000)

simulator.run(real_time=False)

metrics = simulator.metrics.get_dataframe()
order_book_snapshot = simulator.order_book.get_dataframe()

simulator.save_order_book()
simulator.save_metrics()

print("\nTWAP Taker results")

print(f"Taker PnL: {twap_taker.compute_pnl(simulator.order_book.mid_price())}")
print(f"Taker Avg Slippage: {twap_taker.compute_average_slippage():.2f} $/share")
print(f"Taker Total Slippage: {twap_taker.compute_total_slippage():.2f} $")

plotting.plot_all(metrics, order_book_snapshot)
```
