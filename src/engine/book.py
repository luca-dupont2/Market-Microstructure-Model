from .order import OrderSide, OrderType, Order
import heapq
import warnings
import pandas as pd
from .events import (
    EventQueue,
    create_new_order_event,
    create_trade_event,
    create_cancel_order_event,
    Event,
)
from datetime import datetime


class LimitOrderBook:
    """
    Limit order book for managing bid and ask orders, matching trades,
    processing order events, and providing order book snapshots.

    Attributes
    ----------
    bid_orders : list
        Heap of bid (buy) orders.
    ask_orders : list
        Heap of ask (sell) orders.
    events : EventQueue
        Queue for publishing and consuming order book events.
    """

    def __init__(self, config: dict) -> None:
        self.bid_orders = []
        self.ask_orders = []
        self.tick_size = config["SIM_PARAMS"]["tick_size"]

        self.events = EventQueue()

    def _add_order(self, order: Order) -> Event | None:
        """
        Add a limit order to the order book and publish a new order event.

        Parameters
        ----------
        order : Order
            The order to be added.

        Returns
        -------
        Event or None
            The new order event if added, else None.
        """
        if not order.get_price() and order.type == OrderType.LIMIT:
            warnings.warn("Invalid order. LIMIT order must have a price")
            return

        if order.type != OrderType.LIMIT:
            warnings.warn(
                "Incorrect order type. Limit orders only. Order not added to book."
            )
            return

        if order.side == OrderSide.BUY:
            heapq.heappush(self.bid_orders, order)
        elif order.side == OrderSide.SELL:
            heapq.heappush(self.ask_orders, order)

        new_order_event = create_new_order_event(order, order.timestamp)
        self.events.publish(new_order_event)

        return new_order_event

    def best_bid(self) -> Order:
        """
        Get the best bid order in the book.

        Returns
        -------
        Order
            The highest price bid order, or a dummy order (id = -1) if none exist.
        """
        if not self.bid_orders:
            return Order(
                price=0, size=0, side=OrderSide.BUY, type=OrderType.LIMIT, id=-1
            )
        return self.bid_orders[0]

    def best_ask(self) -> Order:
        """
        Get the best ask order in the book.

        Returns
        -------
        Order
            The lowest price ask order, or a dummy order (id = -1) if none exist.
        """
        if not self.ask_orders:
            return Order(
                price=0, size=0, side=OrderSide.SELL, type=OrderType.LIMIT, id=-1
            )
        return self.ask_orders[0]

    def mid_price(self) -> float:
        """
        Calculate the mid price between best bid and best ask.

        Returns
        -------
        float
            The mid price, or 0.0 if no bids/asks exist.
        """
        best_bid = self.best_bid().get_price()
        best_ask = self.best_ask().get_price()

        if best_bid == 0 and best_ask == 0:
            return 0.0
        elif best_bid == 0:
            return best_ask
        elif best_ask == 0:
            return best_bid
        else:
            return (best_bid + best_ask) / 2

    def get_spread(self) -> float:
        """
        Calculate the spread between best ask and best bid.

        Returns
        -------
        float
            The spread, or 0.0 if no bids/asks exist.
        """
        best_bid = self.best_bid().get_price()
        best_ask = self.best_ask().get_price()

        if best_bid == 0 and best_ask == 0:
            return 0.0
        elif best_bid == 0 or best_ask == 0:
            return float("inf")  # Infinite spread if one side is missing
        else:
            return best_ask - best_bid

    def get_bid_size(self, levels=None) -> int:
        """
        Get the total size of all bid orders in the book.

        Returns
        -------
        int
            Total size of bid orders.
        """
        if levels is None:
            levels = len(self.bid_orders)

        if levels < 1 or levels > len(self.bid_orders):
            return 0

        return sum(order.size for order in self.bid_orders[:levels])

    def get_ask_size(self, levels=None) -> int:
        """
        Get the total size of all ask orders in the book.

        Returns
        -------
        int
            Total size of ask orders.
        """
        if levels is None:
            levels = len(self.ask_orders)
            
        if levels < 1 or levels > len(self.ask_orders):
            return 0

        return sum(order.size for order in self.ask_orders[:levels])

    def get_ask_depth(self) -> int:
        """
        Get the number of ask orders in the book.

        Returns
        -------
        int
            Number of ask orders.
        """
        return len(self.ask_orders)

    def get_bid_depth(self) -> int:
        """
        Get the number of bid orders in the book.

        Returns
        -------
        int
            Number of bid orders.
        """
        return len(self.bid_orders)

    def _match_market_order(self, order: Order) -> list[Event]:
        """
        Match a market order against the book and generate trade events.
        Unfilled quantity is discarded.

        Parameters
        ----------
        order : Order
            The market order to match.

        Returns
        -------
        list[Event]
            List of trade events generated by matching.
        """
        if order.type == OrderType.CANCEL:
            warnings.warn("Un-matchable order type : CANCEL")
            return []

        trade_events = []

        if order.side == OrderSide.BUY:  # Buy order
            while self.ask_orders and order.size > 0:
                best = self.best_ask()

                trade = min(best.size, order.size)

                trade_event = create_trade_event(
                    best.get_price(),
                    trade,
                    order,
                    best,
                    order.timestamp,
                    order.parent_id,
                )

                trade_events.append(trade_event)
                self.events.publish(trade_event)

                best.size -= trade
                order.size -= trade

                if best.size == 0:
                    heapq.heappop(self.ask_orders)

        elif order.side == OrderSide.SELL:
            while self.bid_orders and order.size > 0:
                best = self.best_bid()

                trade = min(best.size, order.size)

                trade_event = create_trade_event(
                    best.get_price(),
                    trade,
                    best,
                    order,
                    order.timestamp,
                    order.parent_id,
                )

                trade_events.append(trade_event)
                self.events.publish(trade_event)

                best.size -= trade
                order.size -= trade

                if best.size == 0:
                    heapq.heappop(self.bid_orders)

        return trade_events

    def _match_limit_order(self, order: Order) -> list[Event]:
        """
        Match a limit order against the book and generate trade events.
        Unfilled quantity is added to the book.

        Parameters
        ----------
        order : Order
            The limit order to match.

        Returns
        -------
        list[Event]
            List of trade events generated by matching.
        """
        if not order.get_price():
            warnings.warn("Invalid order. LIMIT order must have a price")
            return []

        if order.type == OrderType.CANCEL:
            warnings.warn("Un-matchable order type. CANCEL")
            return []

        trade_events = []

        order.price = round(order.price / self.tick_size) * self.tick_size

        if order.side == OrderSide.BUY:  # Buy order
            while self.ask_orders and order.size > 0:
                best = self.best_ask()

                if best.get_price() > order.get_price():
                    break

                trade = min(best.size, order.size)

                trade_event = create_trade_event(
                    best.get_price(),
                    trade,
                    best,
                    order,
                    order.timestamp,
                    order.parent_id,
                )

                trade_events.append(trade_event)
                self.events.publish(trade_event)

                best.size -= trade
                order.size -= trade

                if best.size == 0:
                    heapq.heappop(self.ask_orders)

        elif order.side == OrderSide.SELL:
            while self.bid_orders and order.size > 0:
                best = self.best_bid()

                if best.get_price() < order.get_price():
                    break

                trade = min(best.size, order.size)

                trade_event = create_trade_event(
                    best.get_price(),
                    trade,
                    best,
                    order,
                    order.timestamp,
                    order.parent_id,
                )

                trade_events.append(trade_event)
                self.events.publish(trade_event)

                best.size -= trade
                order.size -= trade

                if best.size == 0:
                    heapq.heappop(self.bid_orders)

        if order.size > 0:
            self._add_order(order)

        return trade_events

    def _cancel_order(self, order_id: int | str) -> Event | None:
        """
        Cancel an order by its ID and publish a cancel event.

        Parameters
        ----------
        order_id : int
            The ID of the order to cancel.

        Returns
        -------
        Event or None
            The cancel event if order found, else None.
        """
        for i, order in enumerate(self.ask_orders):
            if order.id == order_id:
                self.ask_orders.pop(i)

                heapq.heapify(self.ask_orders)

                cancel_event = create_cancel_order_event(order, datetime.now())
                self.events.publish(cancel_event)
                return cancel_event

        for i, order in enumerate(self.bid_orders):
            if order.id == order_id:
                self.bid_orders.pop(i)

                heapq.heapify(self.bid_orders)

                cancel_event = create_cancel_order_event(order, datetime.now())
                self.events.publish(cancel_event)

                return cancel_event

        return None

    def process_order(self, order: Order) -> Event | list[Event] | None:
        """
        Process an incoming order: cancel, market, or limit.

        Parameters
        ----------
        order : Order
            The order to process.

        Returns
        -------
        Event or list[Event] or None
            The resulting event(s) from processing the order.
        """
        if order.type == OrderType.CANCEL:
            cancel_event = self._cancel_order(order.id)
            return cancel_event

        if order.type == OrderType.MARKET:
            trade_events = self._match_market_order(order)
            return trade_events

        if order.type == OrderType.LIMIT:
            trade_events = self._match_limit_order(order)
            return trade_events

    def get_all_order_ids(self) -> list[int | str]:
        """
        Get all order IDs currently in the book.

        Returns
        -------
        list[int | str]
            List of all order IDs.
        """
        return [order.id for order in self.ask_orders + self.bid_orders]

    def depth_snapshot(self, snapshot_depth: int) -> pd.DataFrame | None:
        """
        Get a snapshot of the top N levels of the order book.

        Parameters
        ----------
        snapshot_depth : int
            Number of levels to include in the snapshot.

        Returns
        -------
        pd.DataFrame or None
            DataFrame of the snapshot, or None if invalid depth.
        """
        if snapshot_depth < 0:
            warnings.warn("Invalid depth. Depth cannot be negative.")
            return

        bids = self.bid_orders.copy()
        asks = self.ask_orders.copy()

        bid_levels = []
        ask_levels = []

        for _ in range(snapshot_depth):
            if bids:
                bid = heapq.heappop(bids)
                bid_levels.append(
                    {"side": bid.side, "price": bid.get_price(), "size": bid.size}
                )
            if asks:
                ask = heapq.heappop(asks)
                ask_levels.append(
                    {"side": ask.side, "price": ask.get_price(), "size": ask.size}
                )
            if not bids and not asks:
                break

        return pd.DataFrame(ask_levels + bid_levels)

    def get_dataframe(self) -> pd.DataFrame | None:
        """
        Get a DataFrame representation of the full order book depth.

        Returns
        -------
        pd.DataFrame or None
            DataFrame of the full order book, or None if empty.
        """
        ob_snapshot = self.depth_snapshot(
            snapshot_depth=len(self.bid_orders + self.ask_orders)
        )  # Save full depth

        if ob_snapshot is None:
            return

        return ob_snapshot

    def flush_event_queue(self) -> list[Event]:
        """
        Consume and return all events from the event queue.

        Returns
        -------
        list of Event
            List of all events in the queue.
        """
        return list(self.events.consume())

    def __repr__(self):
        """
        Return a string representation of the order book.

        Returns
        -------
        str
            String showing bids and asks in the book.
        """
        return f"Bids: {[ (order.get_price(), order.size) for order in self.bid_orders ]}\nAsks: {[ (order.get_price(), order.size) for order in self.ask_orders ]}"
