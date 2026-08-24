"""MLP velocity field v_theta(x_t, t, y) with sinusoidal time embedding.

Used for EXP-1 / EXP-2. A single class handles both the *conditional* model
(input = [x_t, time_embed, y]) and the *unconditional* baseline (input =
[x_t, time_embed]) via ``cond_dim=0``. Keeping them the same class guarantees
identical capacity for the P4 comparison (spec Section 3.6).
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn


class SinusoidalTimeEmbedding(nn.Module):
    """Standard transformer-style sinusoidal embedding of a scalar t in [0, 1]."""

    def __init__(self, dim: int, max_period: float = 1000.0):
        super().__init__()
        assert dim % 2 == 0, "time embedding dim must be even"
        self.dim = dim
        self.max_period = max_period

    def forward(self, t: torch.Tensor) -> torch.Tensor:
        # t: (batch,) or (batch, 1) -> (batch, dim)
        t = t.reshape(-1).to(torch.float32)
        half = self.dim // 2
        freqs = torch.exp(
            -math.log(self.max_period)
            * torch.arange(half, device=t.device, dtype=torch.float32)
            / half
        )
        args = t[:, None] * freqs[None, :]
        return torch.cat([torch.cos(args), torch.sin(args)], dim=-1)


_ACTIVATIONS = {
    "silu": nn.SiLU,
    "selu": nn.SELU,
    "gelu": nn.GELU,
    "relu": nn.ReLU,
}


class MLPVelocity(nn.Module):
    """v_theta: (x_t in R^d, t in R, y in R^k) -> R^d."""

    def __init__(
        self,
        data_dim: int,
        cond_dim: int = 0,
        width: int = 128,
        depth: int = 4,
        time_embed_dim: int = 64,
        activation: str = "silu",
    ):
        super().__init__()
        self.data_dim = data_dim
        self.cond_dim = cond_dim
        self.conditional = cond_dim > 0

        self.time_embed = SinusoidalTimeEmbedding(time_embed_dim)
        act = _ACTIVATIONS[activation]

        in_dim = data_dim + time_embed_dim + cond_dim
        layers: list[nn.Module] = [nn.Linear(in_dim, width), act()]
        for _ in range(depth - 1):
            layers += [nn.Linear(width, width), act()]
        layers += [nn.Linear(width, data_dim)]
        self.net = nn.Sequential(*layers)

    def forward(
        self,
        x: torch.Tensor,
        t: torch.Tensor,
        y: torch.Tensor | None = None,
    ) -> torch.Tensor:
        temb = self.time_embed(t)
        parts = [x, temb]
        if self.conditional:
            if y is None:
                raise ValueError("Conditional model called without y")
            parts.append(y)
        elif y is not None:
            # Explicitly ignore y for the unconditional baseline so a caller
            # cannot accidentally leak the condition (spec Section 12 warning).
            pass
        h = torch.cat(parts, dim=-1)
        return self.net(h)


def build_model(cfg: dict, data_dim: int, cond_dim: int) -> MLPVelocity:
    m = cfg.get("model", {})
    return MLPVelocity(
        data_dim=data_dim,
        cond_dim=cond_dim,
        width=m.get("width", 128),
        depth=m.get("depth", 4),
        time_embed_dim=m.get("time_embed_dim", 64),
        activation=m.get("activation", "silu"),
    )
