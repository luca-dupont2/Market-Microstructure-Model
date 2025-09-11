CONFIG = {
    "SIM_PARAMS": {
        "horizon": 1 * 60 * 60,  # seconds of simulated time
        "dt": 0.1,  # time step for simulation
        "tick_size": 0.01,  # minimum price increment
        "initial_price": 100,
        "record_interval": 30,  # record state interval
        "random_seed": 42,
        "log_file": False,
        "log_filename": None,
        "log_level": "DEBUG",
        "console_log_level": "INFO",
    },
    "ORDERFLOW_PARAMS": {
        "order_bernoulli": {
            "limit_buy": 0.3,
            "limit_sell": 0.3,
            "market_buy": 0.175,
            "market_sell": 0.175,
            "cancel": 0.05,
        },
        "size_distribution": {  # LogNormal
            "mu": 1.0,
            "sigma": 0.50,
            "min_size": 1,
            "max_size": 100,
        },
        "placement_distribution": {  # Geometric + Zipf mixture
            "p_geom": 0.40,
            "max_distance": 200,
            "r_pointmass": 0.90,  # prob of sampling from geometric distribution
            "alpha_zipf": 1.45,  # exponent for zipf distribution
            "drift": 0.55,  # prob of placing orders above mid
        },
    },
    # TODO Implement strategies
    "STRATEGY_PARAMS": {
        "market_maker": {
            "base_spread": 0.05,  # ticks
            "inventory_limit": 100,
            "gamma": 0.1,  # risk aversion
            "quote_size": 10,
        },
        "taker": {
            "twap": {
                "intervals": 6,
                "duration": 20 * 60,  # seconds
            },
        },
    },
}
