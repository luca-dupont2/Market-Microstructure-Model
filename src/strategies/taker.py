from .base_strategy import BaseStrategy
from .signal import MomentumSignal, ImbalanceSignal


class ManualTaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy,
        id=None,
        initial_cash=10000,
        initial_inventory=0,
    ):
        super().__init__(
            execution_strategy=execution_strategy,
            id=id,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
        )


class MomentumTaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy,
        sensitivity: float = 0.5,
        cash_buffer: float = 0.25,
        alpha: float = 200.0,
        look_back: int = 10,
        id=None,
        initial_cash=10000,
        initial_inventory=0,
    ):
        super().__init__(
            execution_strategy=execution_strategy,
            signal=MomentumSignal(look_back=look_back, alpha=alpha),
            sensitivity=sensitivity,
            cash_buffer=cash_buffer,
            id=id,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
        )


class ImbalanceTaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy,
        sensitivity: float = 0.40,
        cash_buffer: float = 0.25,
        levels: int = 10,
        id=None,
        initial_cash=10000,
        initial_inventory=0,
    ):
        super().__init__(
            execution_strategy=execution_strategy,
            signal=ImbalanceSignal(levels=levels),
            sensitivity=sensitivity,
            cash_buffer=cash_buffer,
            id=id,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
        )
