import logging
import sys
from datetime import datetime
from ..engine.order import Order, OrderType
from ..engine.events import (
    NewOrderEvent,
    TradeEvent,
    CancelOrderEvent,
    Event,
)


class SimLogger:
    def __init__(
        self,
        name: str = "market_sim",
        log_file: bool = False,
        filename: str | None = None,
        console_level: int = logging.INFO,
        level: int = logging.DEBUG,
    ):
        """Initialize the simulator logger.

        Args:
            name (str, optional): Name of the logger. Defaults to "market_sim".
            log_file (bool, optional): Whether to log to a file. Defaults to False.
            filename (str | None, optional): Filename for the log file. Defaults to None.
            console_level (int, optional): Logging level for the console. Defaults to logging.INFO.
            level (int, optional): Logging level for the logger. Defaults to logging.DEBUG.
        """
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

    def log_trade(self, trade_event: TradeEvent):
        """Log a trade event.

        Args:
            trade_event (TradeEvent): The trade event to log.
        """
        self.logger.debug(
            f"TRADE: {trade_event.size} @ {trade_event.price:.2f} "
            f"(buy={trade_event.buy_order_id}, sell={trade_event.sell_order_id})"
        )

    def log_order(self, order: Order | NewOrderEvent):
        """Log a new order or new order event.

        Args:
            order (Order | NewOrderEvent): The order or new order event to log.
        """
        if isinstance(order, Order):
            self.logger.debug(
                f"NEW ORDER: {order.id} {order.side} {order.type} {order.size} @ {order.price}"
            )
        elif isinstance(order, NewOrderEvent):
            self.logger.debug(
                f"NEW ORDER EVENT: {order.side} {OrderType.MARKET if order.price == None else OrderType.LIMIT} {order.size} @ {order.price}"
            )

    def log_cancel(self, cancel_event: CancelOrderEvent):
        """Log a cancel order event.

        Args:
            cancel_event (CancelOrderEvent): The cancel order event to log.
        """
        self.logger.debug(f"CANCEL: order_id={cancel_event.order_id}")

    def log_events(self, events: list[Event]):
        """Log a list of events.

        Args:
            events (list[Event]): The list of events to log.
        """
        if not events:
            return
        for event in events:
            if isinstance(event, TradeEvent):
                self.log_trade(event)
            elif isinstance(event, CancelOrderEvent):
                self.log_cancel(event)
            elif isinstance(event, NewOrderEvent):
                self.log_order(event)

    def info(self, msg: str):
        """Log an informational message.

        Args:
            msg (str): The informational message to log.
        """
        self.logger.info(msg)

    def warning(self, msg: str):
        """Log a warning message.

        Args:
            msg (str): The warning message to log.
        """
        self.logger.warning(msg)

    def error(self, msg: str):
        """Log an error message.

        Args:
            msg (str): The error message to log.
        """
        self.logger.error(msg)
