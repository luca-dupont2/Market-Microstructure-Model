import numpy as np


class RNG:
    def __init__(self, seed: int | None = None):
        """Random Number Generator for various distributions.

        Args:
            seed (int | None, optional): Seed for the random number generator. Defaults to None.
        """
        self.seed = seed
        self._np_rng = np.random.default_rng(seed)

    def randint(self, low: int, high: int) -> int:
        """Random integer in [low, high).

        Args:
            low (int): Lower bound (inclusive).
            high (int): Upper bound (exclusive).

        Returns:
            int: A random integer between low (inclusive) and high (exclusive).
        """
        return self._np_rng.integers(low, high)

    def bernoulli(self, p: float) -> int:
        """Draw from a Bernoulli distribution.

        Args:
            p (float): Probability of success (must be in [0, 1]).

        Returns:
            int: 1 with probability p, 0 otherwise.
        """
        return self._np_rng.binomial(1, p)

    def uniform(self, low: float = 0.0, high: float = 1.0) -> float:
        """Draw from a uniform distribution.

        Args:
            low (float, optional): Lower bound (inclusive). Defaults to 0.0.
            high (float, optional): Upper bound (exclusive). Defaults to 1.0.

        Returns:
            float: A random float between low (inclusive) and high (exclusive).
        """
        return self._np_rng.uniform(low, high)

    def lognormal(self, mean: float = 0.0, sigma: float = 1.0) -> float:
        """Draw from a log-normal distribution.

        Args:
            mean (float, optional): Mean of the distribution. Defaults to 0.0.
            sigma (float, optional): Standard deviation of the distribution. Defaults to 1.0.

        Returns:
            float: A random float from a log-normal distribution.
        """
        return self._np_rng.lognormal(mean, sigma)

    def normal(self, mean: float = 0.0, std: float = 1.0) -> float:
        """Draw from a normal distribution.

        Args:
            mean (float, optional): Mean of the distribution. Defaults to 0.0.
            std (float, optional): Standard deviation of the distribution. Defaults to 1.0.

        Returns:
            float: A random float from a normal distribution.
        """
        return self._np_rng.normal(mean, std)

    def geometric(self, p: float) -> int:
        """Draw from a geometric distribution.

        Args:
            p (float): Probability of success (must be in (0, 1]).

        Returns:
            int: A random integer from a geometric distribution.
        """
        return self._np_rng.geometric(p)

    def discrete_zipf_prob(self, alpha: float, max_value: int) -> np.ndarray:
        """Get probabilities for discrete Zipf distribution.

        Args:
            alpha (float): The parameter of the distribution (must be > 0).
            max_value (int): The maximum rank to consider.

        Returns:
            np.ndarray: An array of probabilities for each rank.
        """
        ranks = np.arange(1, max_value + 1)
        weights = 1 / (ranks**alpha)
        probabilities = weights / weights.sum()
        return probabilities

    def discrete_zipf(self, probabilities: np.ndarray, ranks: np.ndarray) -> int:
        """Draw from a discrete Zipf distribution.

        Args:
            probabilities (np.ndarray): The probabilities for each rank.
            ranks (np.ndarray): The ranks to sample from.

        Returns:
            int: A random rank sampled from the distribution.
        """
        return self._np_rng.choice(ranks, p=probabilities)

    def choice(self, seq: np.ndarray, p: np.ndarray | None = None) -> int:
        """Pick a random element from a list/array.

        Args:
            seq (np.ndarray): The sequence to sample from.
            p (np.ndarray | None, optional): The probabilities for each element. Defaults to None.

        Returns:
            int: The index of the selected element.
        """
        return self._np_rng.choice(seq, p=p)

    def seed_rng(self, seed: int | None = None):
        """Reset seed for reproducibility.

        Args:
            seed (int | None, optional): The seed value. Defaults to None.
        """
        self.seed = seed
        self._np_rng = np.random.default_rng(seed)
