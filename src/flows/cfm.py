"""Conditional / unconditional flow-matching loss.

Loss (spec Section 2.1):

    L(v) = E_{t, x0~pi_0, (x1, y)~rho_hat}  || (x1 - x0) - v(x_t, t, y) ||^2

Crucially, ``x0`` is resampled independently every step (the "resample x0"
mechanism from 2510.18118). The central hypothesis of this project is that
conditioning on ``y`` re-introduces the injectivity that resampling was
supposed to break, so we make the sampling of x0 explicit and independent here.
"""
from __future__ import annotations

import torch

from .interpolants import LinearInterpolant


class CFMTrainer:
    """Draws a training batch and computes the flow-matching loss.

    Parameters
    ----------
    X, Y : full training tensors (N, d) and (N, k). ``Y`` may be ``None`` for
        the unconditional baseline.
    interpolant : LinearInterpolant
    conditional : whether to feed y to the model.
    y_noise_h : bandwidth h of Gaussian smoothing added to the *condition*
        (spec P7 remedy). Fresh noise each step. 0 disables it.
    """

    def __init__(
        self,
        X: torch.Tensor,
        Y: torch.Tensor | None,
        interpolant: LinearInterpolant,
        conditional: bool,
        source_std: float = 1.0,
        y_noise_h: float = 0.0,
        device: torch.device | None = None,
    ):
        self.device = device or torch.device("cpu")
        self.X = X.to(self.device, torch.float32)
        self.Y = None if Y is None else Y.to(self.device, torch.float32)
        self.interpolant = interpolant
        self.conditional = conditional
        self.source_std = float(source_std)
        self.y_noise_h = float(y_noise_h)
        self.N = X.shape[0]
        self.d = X.shape[1]

    def sample_source(self, n: int, generator: torch.Generator | None = None) -> torch.Tensor:
        """x0 ~ pi_0 = N(0, source_std^2 I). Resampled every call by design."""
        z = torch.randn(n, self.d, generator=generator, device=self.device)
        return self.source_std * z

    def loss_with_model(self, model, batch_size: int,
                        generator: torch.Generator | None = None) -> torch.Tensor:
        idx = torch.randint(0, self.N, (batch_size,), generator=generator, device=self.device)
        x1 = self.X[idx]
        y = None
        if self.conditional:
            y = self.Y[idx]
            if self.y_noise_h > 0.0:
                y = y + self.y_noise_h * torch.randn(
                    y.shape, generator=generator, device=self.device
                )

        x0 = self.sample_source(batch_size, generator=generator)
        t = torch.rand(batch_size, generator=generator, device=self.device)
        ib = self.interpolant.sample(x0, x1, t, generator=generator)

        pred = model(ib.x_t, ib.t, y)
        return ((ib.target - pred) ** 2).sum(dim=-1).mean()
