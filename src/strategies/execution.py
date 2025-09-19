from ..engine import OrderSide
from uuid import uuid4
from ..utils import RNG


class ExecutionStrategy:
    """Base class for execution strategies.

    Attributes
    ----------
    rng : RNG
        Random number generator instance.
    """

    def __init__(self, rng: RNG) -> None:
        self.rng = rng

    def schedule_order(self, *args, **kwargs):
        """
        Schedule an order using the execution strategy.

        Raises:
          NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError("Execution strategy must implement schedule method")


class TWAPExecution(ExecutionStrategy):
    """
    Time-Weighted Average Price execution strategy.

    Attributes
    ----------
    rng : RNG
        Random number generator instance.
    intervals : int
        Number of intervals to split the order.
    duration : float
        Total duration over which to execute the order.
    """

    def __init__(self, rng: RNG, intervals: int, duration: float) -> None:
        if intervals <= 0:
            raise ValueError("Intervals must be positive")
        if duration <= 0:
            raise ValueError("Duration must be positive")

        self.intervals = intervals
        self.duration = duration
        super().__init__(rng=rng)

    def schedule_order(
        self,
        schedule_time: float,
        total_volume: int,
        side: OrderSide,
        parent_id: int | str | None = None,
    ) -> list[tuple[float, int, OrderSide, int | str]]:
        """
        Schedule an order using the TWAP strategy.

        Args:
          schedule_time (float): Start time for scheduling.
          total_volume (int): Total volume to execute.
          side (OrderSide): Side of the order (buy/sell).
          parent_id (int | str | None, optional): Parent order ID.

        Returns:
          list: List of scheduled order tuples (time, volume, side, parent_id).

        Raises:
          ValueError: If total_volume or schedule_time is not positive.
        """
        if not parent_id:
            parent_id = uuid4().int

        if total_volume <= 0:
            raise ValueError("Total volume must be positive")

        if schedule_time <= 0:
            raise ValueError("Schedule time must be positive")

        interval_volume = total_volume // self.intervals
        times = [
            schedule_time
            + i * (self.duration / self.intervals)
            + self.rng.uniform(0, self.duration / self.intervals)
            for i in range(self.intervals)
        ]

        schedule = [(t, interval_volume, side, parent_id) for t in times]

        return schedule


class BlockExecution(ExecutionStrategy):
    """
    Block execution strategy that executes the entire order at once.

    Attributes
    ----------
    rng : RNG
        Random number generator instance.
    """

    def __init__(self, rng: RNG) -> None:
        super().__init__(rng=rng)

    def schedule_order(
        self,
        schedule_time: float,
        total_volume: int,
        side: OrderSide,
    ) -> list[tuple[float, int, OrderSide, int]]:
        """
        Schedule an order using the Block execution strategy.

        Args:
          schedule_time (float): Time to execute the order.
          total_volume (int): Total volume to execute.
          side (OrderSide): Side of the order (buy/sell).
          parent_id (int | str | None, optional): Parent order ID.

        Returns:
          list: List containing a single scheduled order tuple (time, volume, side, parent_id).

        Raises:
          ValueError: If total_volume or schedule_time is not positive.
        """
        parent_id = uuid4().int

        schedule = [(schedule_time, total_volume, side, parent_id)]

        return schedule
