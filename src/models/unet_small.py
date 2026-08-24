"""A small U-Net velocity field for EXP-3 image inpainting.

Conditioning follows the spec (Section 5.2): the observation ``y`` (the visible
part of the image) and the binary mask are concatenated to ``x_t`` along the
channel dimension. The network regresses the flow-matching velocity for the full
image. Deliberately small — EXP-3 is a qualitative illustration, not a quality
benchmark.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


def timestep_embedding(t: torch.Tensor, dim: int, max_period: float = 1000.0) -> torch.Tensor:
    t = t.reshape(-1).float()
    half = dim // 2
    freqs = torch.exp(-math.log(max_period) * torch.arange(half, device=t.device) / half)
    args = t[:, None] * freqs[None, :]
    emb = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)
    if dim % 2:
        emb = F.pad(emb, (0, 1))
    return emb


class ResBlock(nn.Module):
    def __init__(self, cin: int, cout: int, temb_dim: int):
        super().__init__()
        self.norm1 = nn.GroupNorm(8, cin)
        self.conv1 = nn.Conv2d(cin, cout, 3, padding=1)
        self.temb = nn.Linear(temb_dim, cout)
        self.norm2 = nn.GroupNorm(8, cout)
        self.conv2 = nn.Conv2d(cout, cout, 3, padding=1)
        self.skip = nn.Conv2d(cin, cout, 1) if cin != cout else nn.Identity()

    def forward(self, x, temb):
        h = self.conv1(F.silu(self.norm1(x)))
        h = h + self.temb(temb)[:, :, None, None]
        h = self.conv2(F.silu(self.norm2(h)))
        return h + self.skip(x)


class SmallUNet(nn.Module):
    """3-level U-Net (32 -> 16 -> 8). in = x_t + conditioning channels."""

    def __init__(self, in_channels: int = 3, out_channels: int = 1,
                 base: int = 32, temb_dim: int = 128):
        super().__init__()
        self.temb_dim = temb_dim
        self.temb_mlp = nn.Sequential(nn.Linear(temb_dim, temb_dim), nn.SiLU(),
                                      nn.Linear(temb_dim, temb_dim))
        c1, c2, c3 = base, base * 2, base * 2
        self.in_conv = nn.Conv2d(in_channels, c1, 3, padding=1)
        self.down1 = ResBlock(c1, c1, temb_dim)
        self.down2 = ResBlock(c1, c2, temb_dim)
        self.down3 = ResBlock(c2, c3, temb_dim)
        self.mid = ResBlock(c3, c3, temb_dim)
        self.up3 = ResBlock(c3 + c3, c2, temb_dim)
        self.up2 = ResBlock(c2 + c2, c1, temb_dim)
        self.up1 = ResBlock(c1 + c1, c1, temb_dim)
        self.out_norm = nn.GroupNorm(8, c1)
        self.out_conv = nn.Conv2d(c1, out_channels, 3, padding=1)

    def forward(self, x, t, cond=None):
        if cond is not None:
            x = torch.cat([x, cond], dim=1)
        temb = self.temb_mlp(timestep_embedding(t, self.temb_dim).to(x.dtype))

        h0 = self.in_conv(x)                         # 32x32, c1
        h1 = self.down1(h0, temb)                    # 32x32, c1
        h2 = self.down2(F.avg_pool2d(h1, 2), temb)   # 16x16, c2
        h3 = self.down3(F.avg_pool2d(h2, 2), temb)   # 8x8,   c3
        hm = self.mid(h3, temb)                      # 8x8

        u3 = self.up3(torch.cat([hm, h3], 1), temb)                       # 8x8 -> c2
        u3 = F.interpolate(u3, scale_factor=2, mode="nearest")           # 16x16
        u2 = self.up2(torch.cat([u3, h2], 1), temb)                      # 16x16 -> c1
        u2 = F.interpolate(u2, scale_factor=2, mode="nearest")           # 32x32
        u1 = self.up1(torch.cat([u2, h1], 1), temb)                      # 32x32 -> c1
        return self.out_conv(F.silu(self.out_norm(u1)))
