from ..utils import RNG, distributions
from numpy import clip
from ..engine.order import OrderSide, OrderType, Order


def round_to_tick(price: float, tick_size: float) -> float:
    """Round a price to the nearest tick size.

    Args:
        price (float): The price to round.
        tick_size (float): The tick size to round to.

    Returns:
        float: The rounded price.
    """
    return round(price / tick_size) * tick_size


class Generator:
    def __init__(self, config: dict, rng: RNG):
        """Initialize the order flow generator.

        Args:
            config (dict): Configuration parameters for the generator.
            rng (RNG): Random number generator.
        """
        seed = config["SIM_PARAMS"]["random_seed"]
        self.rng = rng

        self.order_probs = config["ORDERFLOW_PARAMS"]["order_bernoulli"]

        self.side_map = {
            "limit_buy": OrderSide.BUY,
            "limit_sell": OrderSide.SELL,
            "market_buy": OrderSide.BUY,
            "market_sell": OrderSide.SELL,
            "cancel": OrderSide.BUY,  #! Side doesn't matter for cancel
        }
        self.type_map = {
            "limit_buy": OrderType.LIMIT,
            "limit_sell": OrderType.LIMIT,
            "market_buy": OrderType.MARKET,
            "market_sell": OrderType.MARKET,
            "cancel": OrderType.CANCEL,
        }

        # Order size parameters
        self.min_size = config["ORDERFLOW_PARAMS"]["size_distribution"]["min_size"]
        self.max_size = config["ORDERFLOW_PARAMS"]["size_distribution"]["max_size"]

        # Price placement parameters
        self.pointmass = config["ORDERFLOW_PARAMS"]["placement_distribution"][
            "r_pointmass"
        ]
        self.tick_size = config["SIM_PARAMS"]["tick_size"]
        self.max_distance = config["ORDERFLOW_PARAMS"]["placement_distribution"][
            "max_distance"
        ]
        self.initial_price = config["SIM_PARAMS"]["initial_price"]

        self.log_normal = distributions.LogNormalDistribution(
            mean=config["ORDERFLOW_PARAMS"]["size_distribution"]["mu"],
            sigma=config["ORDERFLOW_PARAMS"]["size_distribution"]["sigma"],
            seed=seed,
        )

        self.geometric = distributions.GeometricDistribution(
            p=config["ORDERFLOW_PARAMS"]["placement_distribution"]["p_geom"],
            seed=seed,
        )

        self.discrete_zipf = distributions.DiscreteZipfDistribution(
            alpha=config["ORDERFLOW_PARAMS"]["placement_distribution"]["alpha_zipf"],
            max_value=config["ORDERFLOW_PARAMS"]["placement_distribution"][
                "max_distance"
            ],
            seed=seed,
        )

    def gen_size(self):
        """Generate a random order size.

        Returns:
            int: Rounded order size clipped to min and max size.
        """
        rounded_size = int(self.log_normal.sample())
        return clip(rounded_size, self.min_size, self.max_size)

    def gen_price(self, best_price: float) -> float:
        """Generate a random order price based on the best price.

        Args:
            best_price (float): The best price on the relevant side of the book.

        Returns:
            float: The generated price.
        """
        direction = self.rng.choice([1, -1])
        if self.rng.bernoulli(self.pointmass):
            price_change = self.geometric.sample()
        else:
            price_change = self.discrete_zipf.sample()

        price_change = min(price_change, self.max_distance)

        price = best_price + direction * price_change * self.tick_size

        price = round_to_tick(price, self.tick_size)

        return max(price, 0)

    def gen_order(self, ask_price: float | None, bid_price: float | None) -> Order:
        """Generate a random order based on the current market conditions.

        Args:
            ask_price (float | None): The current ask price.
            bid_price (float | None): The current bid price.

        Returns:
            Order: The generated order.
        """
        event_choice = self.rng.choice(
            list(self.order_probs.keys()), p=list(self.order_probs.values())
        )

        side = self.side_map[event_choice]
        type = self.type_map[event_choice]

        event_choice = self.rng.choice(
            list(self.order_probs.keys()), p=list(self.order_probs.values())
        )

        side = self.side_map[event_choice]
        type = self.type_map[event_choice]

        if type == OrderType.CANCEL:
            return Order(side=side, price=None, size=0, type=type)

        size = self.gen_size()

        if type == OrderType.MARKET:
            return Order(side=side, price=None, size=size, type=type)

        # Price generation for LIMIT orders
        # Relies on the best price on the SAME side of the book if possible, else uses opposite book, else initial price

        if side == OrderSide.BUY:
            if bid_price:
                price = self.gen_price(bid_price)
            elif ask_price:
                price = self.gen_price(ask_price)
            else:
                price = self.gen_price(self.initial_price)
        else:
            if ask_price:
                price = self.gen_price(ask_price)
            elif bid_price:
                price = self.gen_price(bid_price)
            else:
                price = self.gen_price(self.initial_price)

        return Order(side=side, price=price, size=size, type=type)
