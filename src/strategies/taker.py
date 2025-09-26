from .base_strategy import BaseStrategy
from .signal import MomentumSignal, ImbalanceSignal
from .execution import ExecutionStrategy
from ..engine.book import LimitOrderBook


class ManualTaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy: ExecutionStrategy,
        id=None,
        initial_cash=10000,
        initial_inventory=0,
        **kwargs,
    ):
        """Initialize the manual taker strategy.

        Args:
            execution_strategy (ExecutionStrategy): The execution strategy to use.
            id (str | int, optional): Identifier for the strategy. Defaults to None.
            initial_cash (float, optional): Initial cash balance. Defaults to 10000.
            initial_inventory (float, optional): Initial inventory level. Defaults to 0.
        """
        super().__init__(
            execution_strategy=execution_strategy,
            id=id,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
            **kwargs,
        )


class MomentumTaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy: ExecutionStrategy,
        sensitivity: float = 0.5,
        alpha: float = 80.0,
        look_back: int = 10,
        **kwargs,
    ):
        """Momentum-based taker strategy.

        Args:
            execution_strategy (ExecutionStrategy): The execution strategy to use.
            sensitivity (float, optional): Sensitivity parameter for the strategy. Defaults to 0.5.
            alpha (float, optional): Alpha parameter for the strategy. Defaults to 80.0.
            look_back (int, optional): Look-back period for the strategy. Defaults to 10.
        """
        smoothing = 2 / (look_back + 1)
        super().__init__(
            execution_strategy=execution_strategy,
            signal=MomentumSignal(look_back=look_back, alpha=alpha),
            sensitivity=sensitivity,
            smoothing=smoothing,
            **kwargs,
        )


class ImbalanceTaker(BaseStrategy):
    def __init__(
        self,
        execution_strategy: ExecutionStrategy,
        sensitivity: float = 0.40,
        levels: int = 10,
        **kwargs,
    ):
        """Imbalance-based taker strategy.

        Args:
            execution_strategy (ExecutionStrategy): The execution strategy to use.
            sensitivity (float, optional): Sensitivity parameter for the strategy. Defaults to 0.40.
            levels (int, optional): Number of levels for the strategy. Defaults to 10.
        """
        super().__init__(
            execution_strategy=execution_strategy,
            signal=ImbalanceSignal(levels=levels),
            sensitivity=sensitivity,
            **kwargs,
        )
