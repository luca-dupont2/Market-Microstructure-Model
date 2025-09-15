from ..engine import OrderSide
from uuid import uuid4


class ExecutionStrategy:
    def __init__(self, rng) -> None:
        self.rng = rng

    def schedule_order(self, *args, **kwargs):
        raise NotImplementedError("Execution strategy must implement schedule method")


class TWAPExecution(ExecutionStrategy):
    def __init__(self, rng, intervals, duration) -> None:
        self.intervals = intervals
        self.duration = duration
        super().__init__(rng=rng)

    def schedule_order(
        self,
        schedule_time,
        total_volume,
        side: OrderSide,
        parent_id=None,
    ):

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
    def __init__(self, rng) -> None:
        super().__init__(rng=rng)

    def schedule_order(
        self,
        schedule_time,
        total_volume,
        side: OrderSide,
        parent_id=None,
    ):

        if total_volume <= 0:
            raise ValueError("Total volume must be positive")

        if schedule_time <= 0:
            raise ValueError("Schedule time must be positive")

        schedule = [(schedule_time, total_volume, side, parent_id)]

        return schedule
