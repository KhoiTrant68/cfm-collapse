"""A standard DDPM-style U-Net, for running EXP-3 at a realistic capacity.

``unet_small.SmallUNet`` (0.5M parameters, three resolutions, one residual block
each, no attention) is deliberately minimal: it is enough to show the collapse
qualitatively but it is the architecture a reviewer points at when asking whether
the effect is an artefact of a toy network. This module is the usual CIFAR-10
denoiser instead -- base width 128, channel multipliers (1,2,2,2), two residual
blocks per resolution and self-attention at 16x16, giving ~35M parameters -- so
that the same experiment can be run at a capacity people actually deploy.

Interface matches SmallUNet: ``forward(x, t, cond)`` with ``t`` in [0,1] and
``cond`` concatenated on the channel axis, so ``train_exp3`` can switch between
them from the config with no other change.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


def timestep_embedding(t: torch.Tensor, dim: int) -> torch.Tensor:
    """Sinusoidal embedding of continuous t in [0,1]; (B,) -> (B, dim)."""
    half = dim // 2
    freqs = torch.exp(
        -math.log(10000.0) * torch.arange(half, device=t.device, dtype=torch.float32) / half
    )
    args = t.float()[:, None] * freqs[None, :] * 1000.0
    emb = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)
    if dim % 2:
        emb = F.pad(emb, (0, 1))
    return emb


def _norm(c: int) -> nn.GroupNorm:
    return nn.GroupNorm(min(32, c), c)


class ResBlock(nn.Module):
    def __init__(self, cin: int, cout: int, temb_dim: int, dropout: float = 0.0):
        super().__init__()
        self.norm1 = _norm(cin)
        self.conv1 = nn.Conv2d(cin, cout, 3, padding=1)
        self.temb = nn.Linear(temb_dim, cout)
        self.norm2 = _norm(cout)
        self.dropout = nn.Dropout(dropout)
        self.conv2 = nn.Conv2d(cout, cout, 3, padding=1)
        self.skip = nn.Conv2d(cin, cout, 1) if cin != cout else nn.Identity()
        nn.init.zeros_(self.conv2.weight)
        nn.init.zeros_(self.conv2.bias)

    def forward(self, x: torch.Tensor, temb: torch.Tensor) -> torch.Tensor:
        h = self.conv1(F.silu(self.norm1(x)))
        h = h + self.temb(F.silu(temb))[:, :, None, None]
        h = self.conv2(self.dropout(F.silu(self.norm2(h))))
        return h + self.skip(x)


class AttnBlock(nn.Module):
    def __init__(self, c: int):
        super().__init__()
        self.norm = _norm(c)
        self.qkv = nn.Conv2d(c, 3 * c, 1)
        self.proj = nn.Conv2d(c, c, 1)
        nn.init.zeros_(self.proj.weight)
        nn.init.zeros_(self.proj.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, C, H, W = x.shape
        q, k, v = self.qkv(self.norm(x)).reshape(B, 3, C, H * W).unbind(1)
        # (B, HW, C) x (B, C, HW) -> attention over spatial positions
        out = F.scaled_dot_product_attention(
            q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)
        )
        return x + self.proj(out.transpose(1, 2).reshape(B, C, H, W))


class Downsample(nn.Module):
    def __init__(self, c: int):
        super().__init__()
        self.op = nn.Conv2d(c, c, 3, stride=2, padding=1)

    def forward(self, x):
        return self.op(x)


class Upsample(nn.Module):
    def __init__(self, c: int):
        super().__init__()
        self.conv = nn.Conv2d(c, c, 3, padding=1)

    def forward(self, x):
        return self.conv(F.interpolate(x, scale_factor=2, mode="nearest"))


class UNet(nn.Module):
    """DDPM-style U-Net. ~35M parameters at the default settings."""

    def __init__(self, in_channels: int = 4, out_channels: int = 3,
                 base: int = 128, ch_mult: tuple[int, ...] = (1, 2, 2, 2),
                 num_res_blocks: int = 2, attn_resolutions: tuple[int, ...] = (16,),
                 temb_dim: int = 512, dropout: float = 0.0, image_size: int = 32):
        super().__init__()
        self.base = base
        self.temb_dim = temb_dim
        self.temb = nn.Sequential(
            nn.Linear(base, temb_dim), nn.SiLU(), nn.Linear(temb_dim, temb_dim)
        )
        self.in_conv = nn.Conv2d(in_channels, base, 3, padding=1)

        # ---- encoder ----
        self.down = nn.ModuleList()
        chans = [base]
        c = base
        res = image_size
        for level, mult in enumerate(ch_mult):
            cout = base * mult
            for _ in range(num_res_blocks):
                block = nn.ModuleList([ResBlock(c, cout, temb_dim, dropout),
                                       AttnBlock(cout) if res in attn_resolutions else nn.Identity()])
                self.down.append(block)
                c = cout
                chans.append(c)
            if level != len(ch_mult) - 1:
                self.down.append(nn.ModuleList([Downsample(c), nn.Identity()]))
                chans.append(c)
                res //= 2

        # ---- middle ----
        self.mid1 = ResBlock(c, c, temb_dim, dropout)
        self.mid_attn = AttnBlock(c)
        self.mid2 = ResBlock(c, c, temb_dim, dropout)

        # ---- decoder ----
        self.up = nn.ModuleList()
        for level, mult in reversed(list(enumerate(ch_mult))):
            cout = base * mult
            for j in range(num_res_blocks + 1):
                block = nn.ModuleList([ResBlock(c + chans.pop(), cout, temb_dim, dropout),
                                       AttnBlock(cout) if res in attn_resolutions else nn.Identity()])
                self.up.append(block)
                c = cout
                if level and j == num_res_blocks:
                    self.up.append(nn.ModuleList([Upsample(c), nn.Identity()]))
                    res *= 2

        self.out_norm = _norm(c)
        self.out_conv = nn.Conv2d(c, out_channels, 3, padding=1)
        nn.init.zeros_(self.out_conv.weight)
        nn.init.zeros_(self.out_conv.bias)

    def forward(self, x: torch.Tensor, t: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        temb = self.temb(timestep_embedding(t, self.base))
        h = self.in_conv(torch.cat([x, cond], dim=1))
        hs = [h]
        for block in self.down:
            first, second = block
            if isinstance(first, Downsample):
                h = first(h)
            else:
                h = second(first(h, temb)) if not isinstance(second, nn.Identity) else first(h, temb)
            hs.append(h)
        h = self.mid2(self.mid_attn(self.mid1(h, temb)), temb)
        for block in self.up:
            first, second = block
            if isinstance(first, Upsample):
                h = first(h)
                continue
            h = first(torch.cat([h, hs.pop()], dim=1), temb)
            if not isinstance(second, nn.Identity):
                h = second(h)
        return self.out_conv(F.silu(self.out_norm(h)))
