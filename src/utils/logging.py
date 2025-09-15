import logging
import sys
from datetime import datetime
from ..engine.order import Order, OrderType
from ..engine.events import EventType, NewOrderEvent


class SimLogger:
    def __init__(
        self,
        name="market_sim",
        log_file: bool = False,
        filename=None,
        console_level=logging.INFO,
        level=logging.DEBUG,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Clear existing handlers (important if re-instantiating)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        handler.setLevel(console_level)
        # File handler
        if log_file:
            if not filename:
                now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                filename = f"logs/{now}-run.log"
            else:
                filename = f"logs/{filename}.log"
            file_handler = logging.FileHandler(filename)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            self.logger.addHandler(file_handler)

    def log_trade(self, trade_event):
        self.logger.debug(
            f"TRADE: {trade_event.size} @ {trade_event.price:.2f} "
            f"(buy={trade_event.buy_order_id}, sell={trade_event.sell_order_id})"
        )

    def log_order(self, order):
        if isinstance(order, Order):
            self.logger.debug(
                f"NEW ORDER: {order.id} {order.side} {order.type} {order.size} @ {order.price}"
            )
        elif isinstance(order, NewOrderEvent):
            self.logger.debug(
                f"NEW ORDER EVENT: {order.side} {OrderType.MARKET if order.price == None else OrderType.LIMIT} {order.size} @ {order.price}"
            )

    def log_cancel(self, cancel_event):
        self.logger.debug(f"CANCEL: order_id={cancel_event.order_id}")

    def log_events(self, events):
        for event in events:
            if event.type == EventType.TRADE:
                self.log_trade(event)
            elif event.type == EventType.CANCEL_ORDER:
                self.log_cancel(event)
            elif event.type == EventType.NEW_ORDER:
                self.log_order(event)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
