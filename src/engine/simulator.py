from .book import LimitOrderBook, Order, OrderSide, OrderType
from .events import Event
from ..utils import SimLogger
from ..orderflow.generator import Generator
from .book_metrics import Metrics
from datetime import datetime
from pandas import DataFrame


class Simulator:
    def __init__(self, config, rng, agents=[]):
        self.order_book = LimitOrderBook(config)
        self.config = config
        self.agents = agents

        self.simlogger = SimLogger(
            level=config["SIM_PARAMS"]["log_level"],
            console_level=config["SIM_PARAMS"]["console_log_level"],
            log_file=config["SIM_PARAMS"]["log_file"],
            filename=config["SIM_PARAMS"]["log_filename"],
        )
        self.rng = rng

        self.current_time = 0.0
        self.next_record_time = 0.0
        self.record_interval = config["SIM_PARAMS"]["record_interval"]

        self.metrics = Metrics()

        self.generator = Generator(config, rng)

    def populate_initial_book_from_df(self, df: DataFrame):
        for _, row in df.iterrows():
            order = Order(
                side=OrderSide.BUY if row["side"].item() == "buy" else OrderSide.SELL,
                price=row["price"],
                size=row["size"],
                type=OrderType.LIMIT,
            )

            order_event = self.order_book._add_order(order)

        self.simlogger.info(
            f"Populated initial book with {len(df)} limit orders from dataframe."
        )

    def populate_initial_book_rand(self, n_levels=16, orders_per_level=3):
        initial_price = self.config["SIM_PARAMS"]["initial_price"]

        for level in range(1, n_levels + 1):
            price_deviation = level * self.config["SIM_PARAMS"]["tick_size"]

            for _ in range(orders_per_level):
                size1 = self.generator.gen_size()
                size2 = self.generator.gen_size()

                order = Order(
                    side=OrderSide.BUY,
                    price=initial_price - price_deviation,
                    size=size1,
                    type=OrderType.LIMIT,
                )

                order_event = self.order_book._add_order(order)

                order = Order(
                    side=OrderSide.SELL,
                    price=initial_price + price_deviation,
                    size=size2,
                    type=OrderType.LIMIT,
                )

                order_event = self.order_book._add_order(order)

        self.simlogger.info(
            f"Populated initial book with {n_levels} levels of random limit orders."
        )

    def order_flow_step(self) -> list[Event]:
        best_ask = self.order_book.best_ask().get_price()
        best_bid = self.order_book.best_bid().get_price()

        order = self.generator.gen_order(best_ask, best_bid)

        # Specific handling for CANCEL orders (assign id to cancel)
        if order.type == OrderType.CANCEL:
            all_ids = self.order_book.get_all_order_ids()

            if not all_ids:
                return []

            cancelled = self.rng.choice(all_ids)

            order.id = cancelled

            cancel_event = self.order_book.process_order(order)

            if cancel_event:
                self.simlogger.log_events(cancel_event)
                return cancel_event

            else:
                self.simlogger.warning(f"Failed to cancel order {cancelled}")
                return []

        events = self.order_book.process_order(order)
        self.simlogger.log_events(events)

        return events

    def strategy_step(self, orderflow_events=[]):
        next_record = False
        for agent in self.agents:
            cancels, orders = agent.step(
                self.current_time, self.order_book, self.metrics.data
            )

            for cancel in cancels:
                cancel_events = self.order_book.process_order(cancel)
                self.simlogger.log_events(cancel_events)

            for order in orders:
                events = self.order_book.process_order(order)
                self.simlogger.log_events(events)

                agent.update(self.current_time, events + orderflow_events)

    def step(self):
        orderflow_events = self.order_flow_step()
        self.strategy_step(orderflow_events)

        if self.current_time >= self.next_record_time:
            events = self.order_book.flush_event_queue()
            self.record_metrics(events)

            for agent in self.agents:
                agent.record_metrics(self.current_time, self.order_book)

            self.next_record_time += self.record_interval

    def record_metrics(self, events):
        t = self.current_time
        self.metrics.record(t, self.order_book, events)

    def save_metrics(self, filename=None):
        df = self.metrics.get_dataframe()
        if df is None:
            print("No metrics to save.")
            return

        if not filename:
            now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            filename = f"data/{now}-metrics.csv"
        else:
            filename = f"data/{filename}.csv"

        df.to_csv(filename, index=False)
        print(f"Metrics saved in {filename}")

    def save_order_book(self, filename=None):
        df = self.order_book.get_dataframe()
        if df is None:
            print("No order book data to save.")
            return

        if not filename:
            now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            filename = f"data/{now}-orderbook.csv"
        else:
            filename = f"data/{filename}.csv"

        df.to_csv(filename, index=False)
        print(f"Order book snapshot saved in {filename}")

    def run(self):
        T_sim = self.config["SIM_PARAMS"]["horizon"]
        dt = self.config["SIM_PARAMS"]["dt"]

        self.simlogger.logger.info("Starting simulation...")

        while self.current_time < T_sim:
            self.step()
            
            print(f"t={self.current_time:.2f}s", end="\r")
            self.current_time += dt

        self.simlogger.logger.info("Simulation completed.")

    def reset(self, agents):
        self.order_book = LimitOrderBook(self.config)
        self.current_time = 0.0
        self.next_record_time = 0.0
        self.metrics = Metrics()

        self.agents = agents
