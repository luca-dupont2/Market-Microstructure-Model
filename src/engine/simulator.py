from .book import LimitOrderBook, Order, OrderSide, OrderType
from ..utils import SimLogger
from ..orderflow.generator import Generator
from .metrics import Metrics
from datetime import datetime
from .events import EventType


class Simulator:
    def __init__(self, config, rng, agents=[]):
        self.order_book = LimitOrderBook()
        self.config = config
        self.agents = agents

        self.simlogger = SimLogger(
            level=config["SIM_PARAMS"]["log_level"],
            console_level=config["SIM_PARAMS"]["console_log_level"],
            log_file=config["SIM_PARAMS"]["log_file"],
        )
        self.rng = rng

        self.current_time = 0.0
        self.next_record_time = 0.0
        self.record_interval = config["SIM_PARAMS"]["record_interval"]

        self.metrics = Metrics()

        self.generator = Generator(config)

    def populate_initial_book(self, n_orders=100):
        for i in range(n_orders):
            side = OrderSide.BUY if i % 2 == 0 else OrderSide.SELL

            price = self.generator.gen_initial_price(side)

            size = self.generator.gen_size()

            order = Order(
                side=side,
                price=price,
                size=size,
                type=OrderType.LIMIT,
            )

            order_event = self.order_book._add_order(order)

            self.simlogger.log_order(order_event)

    def log_events(self, events):
        for event in events:
            if event.type == EventType.TRADE:
                self.simlogger.log_trade(event)

    def order_flow_step(self):
        best_ask = self.order_book.best_ask().get_price()
        best_bid = self.order_book.best_bid().get_price()

        order = self.generator.gen_order(best_ask, best_bid)

        # Specific handling for CANCEL orders (assign id to cancel)
        if order.type == OrderType.CANCEL:
            all_ids = self.order_book.get_all_order_ids()

            if not all_ids:
                return

            cancelled = self.rng.choice(all_ids)

            order.id = cancelled

            cancel_event = self.order_book.process_order(order)

            if cancel_event:
                self.simlogger.log_cancel(cancel_event)
            else:
                self.simlogger.warning(f"Failed to cancel order {cancelled}")

            return

        events = self.order_book.process_order(order)

        self.simlogger.log_order(order)

        if type(events) == list and events:
            for event in events:
                if event.type == EventType.TRADE:
                    self.simlogger.log_trade(event)

    def strategy_step(self):
        for agent in self.agents:
            order = agent.step(self.current_time)

            if order:
                events = self.order_book.process_order(order)

                self.simlogger.log_order(order)

                if type(events) == list and events:
                    self.log_events(events)

                    agent.update([e for e in events if e.type == EventType.TRADE])

    def step(self):
        self.order_flow_step()
        self.strategy_step()

    def record_metrics(self, events):
        t = self.current_time
        self.metrics.record(t, self.order_book, events)

    def save_metrics(self):
        df = self.metrics.get_dataframe()
        now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        filename = f"data/{now}-metrics.csv"

        df.to_csv(filename, index=False)
        print(f"Metrics saved in {filename}")

    def save_order_book(self):
        df = self.order_book.get_dataframe()
        if df is None:
            print("No order book data to save.")
            return

        now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        filename = f"data/{now}-orderbook.csv"

        df.to_csv(filename, index=False)
        print(f"Order book snapshot saved in {filename}")

    def run(self):
        T_sim = self.config["SIM_PARAMS"]["horizon"]
        dt = self.config["SIM_PARAMS"]["dt"]

        self.simlogger.logger.info("Starting simulation...")

        while self.current_time < T_sim:
            start_time = None

            self.step()

            if self.current_time >= self.next_record_time:
                events = self.order_book.flush_event_queue()
                print(f"t={self.current_time:.2f}s", end="\r")

                self.record_metrics(events)

                self.next_record_time += self.record_interval

            self.current_time += dt

        self.simlogger.logger.info("Simulation completed.")

    def reset(self, agents):
        self.order_book = LimitOrderBook()
        self.current_time = 0.0
        self.next_record_time = 0.0
        self.metrics = Metrics()

        self.agents = agents
