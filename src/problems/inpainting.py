"""EXP-3 image inpainting problem (MNIST).

A small subset of MNIST is padded to 32x32 and scaled to [-1, 1]. The forward
"observation" masks the bottom half of the image; the conditioning ``y`` is the
visible top half (plus a binary mask channel). The generative task is to sample
the full image consistent with the visible part — a Bayesian inverse problem
whose posterior is multimodal (many plausible bottom halves for a given top).

Under overtraining we expect the same collapse: for a fixed observed top half,
all generated completions become identical to the single memorized training
image with that top half (spec Section 5).
"""
from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class InpaintingProblem:
    X: torch.Tensor          # (N, 1, 32, 32) in [-1, 1]
    mask_obs: torch.Tensor   # (1, 32, 32) 1 = observed (top half), 0 = to inpaint
    labels: torch.Tensor     # (N,) digit labels (for reference only)

    @property
    def N(self) -> int:
        return self.X.shape[0]

    @classmethod
    def create(cls, N: int, seed: int = 0, data_root: str = "data",
               mask_kind: str = "bottom_half") -> "InpaintingProblem":
        from torchvision import datasets  # local import: heavy dependency

        ds = datasets.MNIST(root=data_root, train=True, download=True)
        imgs = ds.data.to(torch.float32) / 255.0          # (60000, 28, 28) in [0,1]
        labels_all = ds.targets

        g = torch.Generator().manual_seed(seed)
        idx = torch.randperm(imgs.shape[0], generator=g)[:N]
        x = imgs[idx]                                     # (N, 28, 28)
        labels = labels_all[idx]

        # pad 28 -> 32 (2 px each side), scale to [-1, 1]
        x = torch.nn.functional.pad(x, (2, 2, 2, 2), value=0.0)   # (N,32,32)
        x = x * 2.0 - 1.0
        x = x.unsqueeze(1)                                # (N,1,32,32)

        mask = torch.zeros(1, 32, 32)
        if mask_kind == "bottom_half":
            mask[:, :16, :] = 1.0                         # observe top half
        elif mask_kind == "top_half":
            mask[:, 16:, :] = 1.0
        else:
            raise ValueError(mask_kind)
        return cls(X=x, mask_obs=mask, labels=labels)

    # ------------------------------------------------------------------ #
    def observation(self, x: torch.Tensor) -> torch.Tensor:
        """y_obs = image with the inpainted region zeroed (kept top half)."""
        return x * self.mask_obs

    def condition(self, x: torch.Tensor) -> torch.Tensor:
        """Conditioning tensor fed to the U-Net: [observed image, mask]."""
        obs = self.observation(x)
        mask = self.mask_obs.expand(x.shape[0], -1, -1, -1)
        return torch.cat([obs, mask], dim=1)             # (B, 2, 32, 32)
