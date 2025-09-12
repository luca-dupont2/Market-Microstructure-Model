from ..engine import OrderSide


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
    ):

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

        schedule = [
            (t, interval_volume, side, True if i == 0 else False)
            for i, t in enumerate(times)
        ]

        return schedule


class BlockExecution(ExecutionStrategy):
    def __init__(self, rng) -> None:
        super().__init__(rng=rng)

    def schedule_order(
        self,
        schedule_time,
        total_volume,
        side: OrderSide,
    ):

        if total_volume <= 0:
            raise ValueError("Total volume must be positive")

        if schedule_time <= 0:
            raise ValueError("Schedule time must be positive")

        schedule = [(schedule_time, total_volume, side, True)]

        return schedule
