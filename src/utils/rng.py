import numpy as np


class RNG:
    def __init__(self, seed=None):
        self.seed = seed
        self._np_rng = np.random.default_rng(seed)

    def randint(self, low, high):
        """Random integer in [low, high)."""
        return self._np_rng.integers(low, high)

    def bernoulli(self, p):
        """Bernoulli trial."""
        return self._np_rng.binomial(1, p)

    def uniform(self, low=0.0, high=1.0):
        """Uniform float in [low, high)."""
        return self._np_rng.uniform(low, high)

    def lognormal(self, mean=0.0, sigma=1.0):
        """Log-normal distribution draw."""
        return self._np_rng.lognormal(mean, sigma)

    def normal(self, mean=0.0, std=1.0):
        """Normal distribution draw."""
        return self._np_rng.normal(mean, std)

    def geometric(self, p):
        """Geometric distribution draw."""
        return self._np_rng.geometric(p)

    def discrete_zipf_prob(self, alpha, max_value):
        """Get probabilities for discrete Zipf distribution."""
        ranks = np.arange(1, max_value + 1)
        weights = 1 / (ranks**alpha)
        probabilities = weights / weights.sum()
        return probabilities

    def discrete_zipf(self, probabilities, ranks):
        """Discrete Zipf distribution draw."""
        return self._np_rng.choice(ranks, p=probabilities)

    def choice(self, seq, p=None):
        """Pick a random element from a list/array."""
        return self._np_rng.choice(seq, p=p)

    def seed_rng(self, seed):
        """Reset seed for reproducibility."""
        self.seed = seed
        self._np_rng = np.random.default_rng(seed)
