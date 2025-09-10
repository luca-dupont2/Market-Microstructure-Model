from ..utils.rng import RNG
import numpy as np


class Distribution:
    def __init__(self, seed=None):
        self.rng = RNG(seed)
        self.params = {}

    def sample(self):
        raise NotImplementedError("Subclasses should implement this!")


class NormalDistribution(Distribution):
    def __init__(self, mean=0.0, std=1.0, seed=None):
        super().__init__(seed)
        self.params = {"mean": mean, "std": std}

    def sample(self):
        return self.rng.normal(self.params["mean"], self.params["std"])


class BernoulliDistribution(Distribution):
    def __init__(self, p=0.5, seed=None):
        super().__init__(seed)
        self.params = {"p": p}

    def sample(self):
        return self.rng.bernoulli(self.params["p"])


class LogNormalDistribution(Distribution):
    def __init__(self, mean=0.0, sigma=1.0, seed=None):
        super().__init__(seed)
        self.params = {"mean": mean, "sigma": sigma}

    def sample(self):
        return self.rng.lognormal(self.params["mean"], self.params["sigma"])


class GeometricDistribution(Distribution):
    def __init__(self, p=0.5, seed=None):
        super().__init__(seed)
        self.params = {"p": p}

    def sample(self):
        return self.rng.geometric(self.params["p"]) - 1


class DiscreteZipfDistribution(Distribution):
    def __init__(self, alpha=1.0, max_value=100, seed=None):
        super().__init__(seed)
        probabilities = self.rng.discrete_zipf_prob(alpha, max_value)
        self.params = {
            "ranks": np.arange(1, max_value + 1),
            "probabilities": probabilities,
        }

    def sample(self):
        return self.rng.discrete_zipf(
            self.params["probabilities"],
            self.params["ranks"],
        )
