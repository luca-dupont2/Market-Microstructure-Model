from ..utils.rng import RNG
import numpy as np


class Distribution:
    def __init__(self, seed: int | None = None):
        """Base class for all distributions.

        Args:
            seed (int | None, optional): Random seed for reproducibility. Defaults to None.
        """
        self.rng = RNG(seed)
        self.params = {}

    def sample(self):
        """Sample from the distribution.

        Raises:
            NotImplementedError: Subclasses should implement this!
        """
        raise NotImplementedError("Subclasses should implement this!")


class NormalDistribution(Distribution):
    def __init__(self, mean: float = 0.0, std: float = 1.0, seed: int | None = None):
        """Normal distribution.

        Args:
            mean (float, optional): Mean of the distribution. Defaults to 0.0.
            std (float, optional): Standard deviation of the distribution. Defaults to 1.0.
            seed (int | None, optional): Random seed for reproducibility. Defaults to None.
        """
        super().__init__(seed)
        self.params = {"mean": mean, "std": std}

    def sample(self) -> float:
        """Sample from the normal distribution.

        Returns:
            float: A sample from the normal distribution.
        """
        return self.rng.normal(self.params["mean"], self.params["std"])


class BernoulliDistribution(Distribution):
    def __init__(self, p: float = 0.5, seed: int | None = None):
        """Bernoulli distribution.

        Args:
            p (float, optional): Probability of success. Defaults to 0.5.
            seed (int | None, optional): Random seed for reproducibility. Defaults to None.
        """
        super().__init__(seed)
        self.params = {"p": p}

    def sample(self) -> int:
        """Sample from the Bernoulli distribution.

        Returns:
            int: 1 for success, 0 for failure.
        """
        return self.rng.bernoulli(self.params["p"])


class LogNormalDistribution(Distribution):
    def __init__(self, mean: float = 0.0, sigma: float = 1.0, seed: int | None = None):
        """Log-normal distribution.

        Args:
            mean (float, optional): Mean of the underlying normal distribution. Defaults to 0.0.
            sigma (float, optional): Standard deviation of the underlying normal distribution. Defaults to 1.0.
            seed (int | None, optional): Random seed for reproducibility. Defaults to None.
        """
        super().__init__(seed)
        self.params = {"mean": mean, "sigma": sigma}

    def sample(self) -> float:
        """Sample from the log-normal distribution.

        Returns:
            float: A sample from the log-normal distribution.
        """
        return self.rng.lognormal(self.params["mean"], self.params["sigma"])


class GeometricDistribution(Distribution):
    def __init__(self, p: float = 0.5, seed: int | None = None):
        """Geometric distribution.

        Args:
            p (float, optional): Probability of success. Defaults to 0.5.
            seed (int | None, optional): Random seed for reproducibility. Defaults to None.
        """
        super().__init__(seed)
        self.params = {"p": p}

    def sample(self) -> int:
        """Sample from the geometric distribution.

        Returns:
            int: A sample from the geometric distribution.
        """
        return self.rng.geometric(self.params["p"]) - 1


class DiscreteZipfDistribution(Distribution):
    def __init__(
        self, alpha: float = 1.0, max_value: int = 100, seed: int | None = None
    ):
        """Discrete Zipf distribution.

        Args:
            alpha (float, optional): Parameter of the distribution. Defaults to 1.0.
            max_value (int, optional): Maximum value of the distribution. Defaults to 100.
            seed (int | None, optional): Random seed for reproducibility. Defaults to None.
        """
        super().__init__(seed)
        probabilities = self.rng.discrete_zipf_prob(alpha, max_value)
        self.params = {
            "ranks": np.arange(1, max_value + 1),
            "probabilities": probabilities,
        }

    def sample(self) -> int:
        """Sample from the discrete Zipf distribution.

        Returns:
            int: A sample from the discrete Zipf distribution.
        """
        return self.rng.discrete_zipf(
            self.params["probabilities"],
            self.params["ranks"],
        )
