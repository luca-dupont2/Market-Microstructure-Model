import logging
import sys
from datetime import datetime


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
        self.logger.debug(
            f"NEW ORDER: {order.side} {order.type} {order.size} @ {getattr(order, 'price', None)}"
        )

    def log_cancel(self, cancel_event):
        self.logger.debug(f"CANCEL: order_id={cancel_event.order_id}")

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
