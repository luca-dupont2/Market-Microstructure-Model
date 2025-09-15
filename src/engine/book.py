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
    def __init__(self) -> None:
        self.bid_orders = []
        self.ask_orders = []

        self.events = EventQueue()

    def _add_order(self, order: Order):
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

    def best_bid(self):
        if not self.bid_orders:
            return Order(
                price=0, size=0, side=OrderSide.BUY, type=OrderType.LIMIT, id=-1
            )
        return self.bid_orders[0]

    def best_ask(self):
        if not self.ask_orders:
            return Order(
                price=0, size=0, side=OrderSide.SELL, type=OrderType.LIMIT, id=-1
            )
        return self.ask_orders[0]

    def mid_price(self):
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

    def _match_market_order(self, order):
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

    def _match_limit_order(self, order):
        if not order.get_price():
            warnings.warn("Invalid order. LIMIT order must have a price")
            return []

        if order.type == OrderType.CANCEL:
            warnings.warn("Un-matchable order type. CANCEL")
            return []

        trade_events = []

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

    def _cancel_order(self, order_id):
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

    def process_order(self, order):
        if order.type == OrderType.CANCEL:
            cancel_event = self._cancel_order(order.id)
            return cancel_event

        if order.type == OrderType.MARKET:
            trade_events = self._match_market_order(order)
            return trade_events

        if order.type == OrderType.LIMIT:
            trade_events = self._match_limit_order(order)
            return trade_events

    def get_all_order_ids(self):
        return [order.id for order in self.ask_orders + self.bid_orders]

    def depth_snapshot(self, snapshot_depth) -> pd.DataFrame | None:
        if snapshot_depth <= 0:
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
        ob_snapshot = self.depth_snapshot(
            snapshot_depth=len(self.bid_orders + self.ask_orders)
        )  # Save full depth

        if ob_snapshot is None:
            return

        return ob_snapshot

    def flush_event_queue(self) -> list[Event]:
        return list(self.events.consume())

    def __repr__(self):
        return f"Bids: {[ (order.get_price(), order.size) for order in self.bid_orders ]}\nAsks: {[ (order.get_price(), order.size) for order in self.ask_orders ]}"
