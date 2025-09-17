ORDER_DRIFT = 0.0  # Increase in probability of placing a buy order vs sell order

CONFIG = {
    "SIM_PARAMS": {
        "horizon": 24 * 60 * 60,  # simulated time (s)
        "dt": 0.5,  # time step for simulation (s)
        "tick_size": 0.01,  # minimum price increment ($)
        "initial_price": 100,  # initial mid price ($)
        "record_interval": 30,  # interval for recording order book state (s)
        "random_seed": 42,  # random seed for reproducibility (int or None)
        "log_file": False,  # save logs to file (True/False)
        "log_filename": None,  # filname for logs if log_file is True. Else filename is timestamped
        "log_level": "DEBUG",  # Minimum log level to record to file
        "console_log_level": "INFO",  # Minimum log level to print to console
    },
    "ORDERFLOW_PARAMS": {
        "order_bernoulli": {  # Probability of each order type. Selected event via bernoulli trial. Must sum to 1.
            "limit_buy": 0.3 + ORDER_DRIFT,
            "limit_sell": 0.3 - ORDER_DRIFT,
            "market_buy": 0.175 + ORDER_DRIFT,
            "market_sell": 0.175 - ORDER_DRIFT,
            "cancel": 0.05,
        },
        "size_distribution": {  # Log-normal distribution
            "mu": 1.0,  # Mean of underlying normal distribution
            "sigma": 0.50,  # Std dev of underlying normal distribution
            "min_size": 1,  # Minimum order size
            "max_size": 100,  # Maximum order size
        },
        "placement_distribution": {  # Geometric + Zipf mixture
            "p_geom": 0.45,  # prob of bernoulli trial success when sampling from geometric distribution
            "max_distance": 200,  # max distance from best bid/ask for limit orders (in ticks)
            "r_pointmass": 0.90,  # prob of sampling from geometric distribution
            "alpha_zipf": 1.45,  # exponent for zipf distribution
        },
    },
    "STRATEGY_PARAMS": {
        "market_maker": {
            "base_spread": 0.05,  # ticks
            "inventory_limit": 100,
            "gamma": 0.1,  # risk aversion
            "quote_size": 10,
        },
        "taker": {
            "twap": {  # Time-Weighted Average Price strategy
                "intervals": 6,  # number of child orders
                "duration": 20 * 60,  # duration over which to execute (s)
            },
        },
    },
}
