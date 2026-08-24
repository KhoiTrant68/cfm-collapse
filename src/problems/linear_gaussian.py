"""Linear-Gaussian Bayesian inverse problem with a closed-form posterior.

Model (spec Section 3.2):

    x ~ N(mu_x, Sigma_x)                       # prior
    y = A x + eps,   eps ~ N(0, sigma_obs^2 I) # linear forward operator

The Gaussian posterior is available in closed form:

    Sigma_post = (Sigma_x^{-1} + A^T A / sigma_obs^2)^{-1}
    mu_post(y) = Sigma_post (Sigma_x^{-1} mu_x + A^T y / sigma_obs^2)

Note that ``Sigma_post`` does *not* depend on ``y`` for a linear-Gaussian model,
so ``trace(Sigma_post)`` is a single scalar ground-truth target for P1.
"""
from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class LinearGaussianProblem:
    """Holds the (fixed) problem geometry and exposes posterior formulas.

    All tensors are float64 on CPU internally for numerically clean posterior
    algebra; sampling helpers cast to the requested dtype/device.
    """

    d: int
    k: int
    A: torch.Tensor          # (k, d)
    sigma_obs: float
    mu_x: torch.Tensor       # (d,)
    Sigma_x: torch.Tensor    # (d, d)

    # cached posterior quantities
    Sigma_post: torch.Tensor          # (d, d)
    _Sigma_x_inv: torch.Tensor        # (d, d)

    @classmethod
    def create(
        cls,
        d: int,
        k: int,
        sigma_obs: float,
        seed: int = 0,
        prior_std: float = 1.0,
        A_kind: str = "random",
    ) -> "LinearGaussianProblem":
        g = torch.Generator().manual_seed(seed)
        mu_x = torch.zeros(d, dtype=torch.float64)
        Sigma_x = (prior_std ** 2) * torch.eye(d, dtype=torch.float64)

        if A_kind == "random":
            # Fixed random Gaussian operator (seeded -> reproducible).
            A = torch.randn(k, d, generator=g, dtype=torch.float64)
        elif A_kind == "projection":
            # Project onto the first k coordinates (information-losing when k<d).
            A = torch.zeros(k, d, dtype=torch.float64)
            for i in range(min(k, d)):
                A[i, i] = 1.0
        else:
            raise ValueError(f"Unknown A_kind={A_kind}")

        Sigma_x_inv = torch.linalg.inv(Sigma_x)
        precision = Sigma_x_inv + (A.T @ A) / (sigma_obs ** 2)
        Sigma_post = torch.linalg.inv(precision)

        return cls(
            d=d, k=k, A=A, sigma_obs=sigma_obs, mu_x=mu_x, Sigma_x=Sigma_x,
            Sigma_post=Sigma_post, _Sigma_x_inv=Sigma_x_inv,
        )

    # ------------------------------------------------------------------ #
    # Sampling
    # ------------------------------------------------------------------ #
    def sample_prior(self, n: int, generator: torch.Generator | None = None) -> torch.Tensor:
        L = torch.linalg.cholesky(self.Sigma_x)
        z = torch.randn(n, self.d, generator=generator, dtype=torch.float64)
        return self.mu_x + z @ L.T

    def forward(self, x: torch.Tensor, generator: torch.Generator | None = None) -> torch.Tensor:
        """y = A x + eps."""
        x = x.to(torch.float64)
        mean = x @ self.A.T
        eps = self.sigma_obs * torch.randn(
            x.shape[0], self.k, generator=generator, dtype=torch.float64
        )
        return mean + eps

    def sample_dataset(self, n: int, seed: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Draw a training set {(x^i, y^i)}. Returns (X, Y) as float64."""
        g = torch.Generator().manual_seed(seed)
        X = self.sample_prior(n, generator=g)
        Y = self.forward(X, generator=g)
        return X, Y

    # ------------------------------------------------------------------ #
    # Analytic posterior
    # ------------------------------------------------------------------ #
    def posterior_mean(self, y: torch.Tensor) -> torch.Tensor:
        """mu_post(y). Accepts (k,) or (n, k); returns (d,) or (n, d)."""
        y = y.to(torch.float64)
        single = y.dim() == 1
        if single:
            y = y[None, :]
        rhs = (self._Sigma_x_inv @ self.mu_x)[None, :] + (y @ self.A) / (self.sigma_obs ** 2)
        mu = rhs @ self.Sigma_post.T
        return mu[0] if single else mu

    def posterior_trace(self) -> float:
        """trace(Sigma_post) — the P1 ground-truth (y-independent)."""
        return float(torch.trace(self.Sigma_post))

    def to_dict(self) -> dict:
        return {
            "d": self.d,
            "k": self.k,
            "sigma_obs": self.sigma_obs,
            "A": self.A.tolist(),
            "mu_x": self.mu_x.tolist(),
            "Sigma_x": self.Sigma_x.tolist(),
            "Sigma_post": self.Sigma_post.tolist(),
            "trace_Sigma_post": self.posterior_trace(),
        }
