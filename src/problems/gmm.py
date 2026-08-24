"""Gaussian-mixture prior with a linear-Gaussian likelihood (EXP-2).

Prior:      x ~ sum_k pi_k N(mu_k, Sigma_k)         (multimodal)
Likelihood: y = A x + eps,  eps ~ N(0, sigma_obs^2 I)

Because the likelihood is linear-Gaussian, the posterior is *again a Gaussian
mixture in closed form* — no grid/MCMC needed for ground truth:

    posterior component k:
        prec_k   = Sigma_k^{-1} + A^T A / sigma^2
        Sigma_k' = prec_k^{-1}
        mu_k'(y) = Sigma_k' (Sigma_k^{-1} mu_k + A^T y / sigma^2)
        w_k(y)   ∝ pi_k * N(y; A mu_k, A Sigma_k A^T + sigma^2 I)

When ``A`` loses information (e.g. projects R^2 -> R^1), several prior modes
remain consistent with the same ``y`` and the posterior is genuinely
multimodal — the regime where collapse / selective memorization hurts most.
"""
from __future__ import annotations

from dataclasses import dataclass

import math

import torch


def _mvn_logpdf(x: torch.Tensor, mean: torch.Tensor, cov: torch.Tensor) -> torch.Tensor:
    """log N(x; mean, cov) for a batch x:(n,d)."""
    d = mean.shape[-1]
    L = torch.linalg.cholesky(cov)
    diff = (x - mean).unsqueeze(-1)
    sol = torch.cholesky_solve(diff, L).squeeze(-1)
    quad = (diff.squeeze(-1) * sol).sum(-1)
    logdet = 2.0 * torch.log(torch.diagonal(L)).sum()
    return -0.5 * (d * math.log(2 * math.pi) + logdet + quad)


@dataclass
class GMMProblem:
    d: int
    k: int
    A: torch.Tensor              # (k, d)
    sigma_obs: float
    weights: torch.Tensor        # (K,)
    means: torch.Tensor          # (K, d)
    covs: torch.Tensor           # (K, d, d)

    @classmethod
    def create(cls, d: int = 2, k: int = 1, sigma_obs: float = 0.2,
               mode_scale: float = 2.0, mode_std: float = 0.5,
               seed: int = 0, A_kind: str = "project_x0") -> "GMMProblem":
        if d == 2:
            centers = torch.tensor([[+1, +1], [+1, -1], [-1, +1], [-1, -1]],
                                   dtype=torch.float64) * mode_scale
        else:
            g = torch.Generator().manual_seed(seed)
            centers = mode_scale * torch.randn(8, d, generator=g, dtype=torch.float64)
        K = centers.shape[0]
        weights = torch.full((K,), 1.0 / K, dtype=torch.float64)
        covs = (mode_std ** 2) * torch.eye(d, dtype=torch.float64).expand(K, d, d).clone()

        if A_kind == "project_x0":            # keep only first coordinate -> info loss
            A = torch.zeros(k, d, dtype=torch.float64)
            for i in range(min(k, d)):
                A[i, i] = 1.0
        elif A_kind == "random":
            g = torch.Generator().manual_seed(seed + 1)
            A = torch.randn(k, d, generator=g, dtype=torch.float64)
        else:
            raise ValueError(A_kind)

        return cls(d=d, k=k, A=A, sigma_obs=sigma_obs,
                   weights=weights, means=centers, covs=covs)

    # ------------------------------------------------------------------ #
    def sample_prior(self, n: int, generator: torch.Generator | None = None) -> torch.Tensor:
        comp = torch.multinomial(self.weights, n, replacement=True, generator=generator)
        out = torch.empty(n, self.d, dtype=torch.float64)
        for kk in range(self.means.shape[0]):
            mask = comp == kk
            m = int(mask.sum())
            if m == 0:
                continue
            L = torch.linalg.cholesky(self.covs[kk])
            z = torch.randn(m, self.d, generator=generator, dtype=torch.float64)
            out[mask] = self.means[kk] + z @ L.T
        return out

    def forward(self, x: torch.Tensor, generator: torch.Generator | None = None) -> torch.Tensor:
        x = x.to(torch.float64)
        eps = self.sigma_obs * torch.randn(x.shape[0], self.k, generator=generator, dtype=torch.float64)
        return x @ self.A.T + eps

    def sample_dataset(self, n: int, seed: int) -> tuple[torch.Tensor, torch.Tensor]:
        g = torch.Generator().manual_seed(seed)
        X = self.sample_prior(n, generator=g)
        Y = self.forward(X, generator=g)
        return X, Y

    # ------------------------------------------------------------------ #
    # Closed-form posterior (a Gaussian mixture)
    # ------------------------------------------------------------------ #
    def posterior_params(self, y: torch.Tensor):
        """Return (w'(K,), mu'(K,d), Sigma'(K,d,d)) for a single y:(k,)."""
        y = y.to(torch.float64).reshape(self.k)
        K = self.means.shape[0]
        s2 = self.sigma_obs ** 2
        mus, covs, logw = [], [], []
        for kk in range(K):
            Sk = self.covs[kk]
            Sk_inv = torch.linalg.inv(Sk)
            prec = Sk_inv + (self.A.T @ self.A) / s2
            Sig = torch.linalg.inv(prec)
            mu = Sig @ (Sk_inv @ self.means[kk] + self.A.T @ y / s2)
            # marginal likelihood N(y; A mu_k, A Sk A^T + s2 I)
            marg_cov = self.A @ Sk @ self.A.T + s2 * torch.eye(self.k, dtype=torch.float64)
            lw = math.log(float(self.weights[kk])) + float(
                _mvn_logpdf((self.A @ self.means[kk]).unsqueeze(0), y.unsqueeze(0), marg_cov)[0]
            )
            mus.append(mu); covs.append(Sig); logw.append(lw)
        logw = torch.tensor(logw, dtype=torch.float64)
        w = torch.softmax(logw, dim=0)
        return w, torch.stack(mus), torch.stack(covs)

    def sample_posterior(self, y: torch.Tensor, n: int,
                         generator: torch.Generator | None = None) -> torch.Tensor:
        w, mus, covs = self.posterior_params(y)
        comp = torch.multinomial(w, n, replacement=True, generator=generator)
        out = torch.empty(n, self.d, dtype=torch.float64)
        for kk in range(mus.shape[0]):
            mask = comp == kk
            m = int(mask.sum())
            if m == 0:
                continue
            L = torch.linalg.cholesky(covs[kk])
            z = torch.randn(m, self.d, generator=generator, dtype=torch.float64)
            out[mask] = mus[kk] + z @ L.T
        return out

    def to_dict(self) -> dict:
        return {
            "d": self.d, "k": self.k, "sigma_obs": self.sigma_obs,
            "A": self.A.tolist(), "weights": self.weights.tolist(),
            "means": self.means.tolist(),
        }
