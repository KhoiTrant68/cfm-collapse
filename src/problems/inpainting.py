"""EXP-3 image inpainting problem (MNIST, or CIFAR-10 as a harder analogue).

A small subset of the dataset is scaled to [-1, 1] on a common 32x32 canvas
(MNIST is zero-padded 28->32; CIFAR-10 is natively 32x32). The forward
"observation" masks the bottom half of the image; the conditioning ``y`` is the
visible top half (plus a binary mask channel). The generative task is to sample
the full image consistent with the visible part — a Bayesian inverse problem
whose posterior is multimodal (many plausible bottom halves for a given top).

Under overtraining we expect the same collapse: for a fixed observed top half,
all generated completions become identical to the single memorized training
image with that top half (spec Section 5). ``channels`` is 1 for MNIST
(grayscale) and 3 for CIFAR-10 (RGB); the U-Net and training loop are
channel-agnostic and read it off ``InpaintingProblem.channels``.
"""
from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class InpaintingProblem:
    X: torch.Tensor          # (N, C, 32, 32) in [-1, 1]
    mask_obs: torch.Tensor   # (1, 32, 32) 1 = observed (top half), 0 = to inpaint
    labels: torch.Tensor     # (N,) class/digit labels
    cond_kind: str = "inpaint"   # "inpaint": y = visible half; "class": y = one-hot
    n_classes: int = 10

    @property
    def N(self) -> int:
        return self.X.shape[0]

    @property
    def channels(self) -> int:
        return self.X.shape[1]

    @classmethod
    def create(cls, N: int, seed: int = 0, data_root: str = "data",
               mask_kind: str = "bottom_half",
               dataset: str = "mnist",
               cond_kind: str = "inpaint") -> "InpaintingProblem":
        from torchvision import datasets  # local import: heavy dependency

        if dataset == "mnist":
            ds = datasets.MNIST(root=data_root, train=True, download=True)
            imgs = ds.data.to(torch.float32) / 255.0      # (60000, 28, 28) in [0,1]
            labels_all = ds.targets
            g = torch.Generator().manual_seed(seed)
            idx = torch.randperm(imgs.shape[0], generator=g)[:N]
            x = imgs[idx]                                 # (N, 28, 28)
            labels = labels_all[idx]
            # pad 28 -> 32 (2 px each side), scale to [-1, 1]
            x = torch.nn.functional.pad(x, (2, 2, 2, 2), value=0.0)   # (N,32,32)
            x = x * 2.0 - 1.0
            x = x.unsqueeze(1)                            # (N,1,32,32)
        elif dataset == "cifar10":
            ds = datasets.CIFAR10(root=data_root, train=True, download=True)
            imgs = torch.from_numpy(ds.data).to(torch.float32) / 255.0  # (50000,32,32,3) in [0,1]
            labels_all = torch.tensor(ds.targets)
            g = torch.Generator().manual_seed(seed)
            idx = torch.randperm(imgs.shape[0], generator=g)[:N]
            x = imgs[idx].permute(0, 3, 1, 2).contiguous()  # (N,3,32,32)
            labels = labels_all[idx]
            x = x * 2.0 - 1.0                             # already 32x32, no padding
        else:
            raise ValueError(f"Unknown dataset={dataset!r} (expected mnist|cifar10)")

        mask = torch.zeros(1, 32, 32)
        if mask_kind == "bottom_half":
            mask[:, :16, :] = 1.0                         # observe top half
        elif mask_kind == "top_half":
            mask[:, 16:, :] = 1.0
        else:
            raise ValueError(mask_kind)
        if cond_kind not in ("inpaint", "class"):
            raise ValueError(f"Unknown cond_kind={cond_kind!r} (expected inpaint|class)")
        return cls(X=x, mask_obs=mask, labels=labels, cond_kind=cond_kind,
                   n_classes=int(labels.max().item()) + 1)

    # ------------------------------------------------------------------ #
    def observation(self, x: torch.Tensor) -> torch.Tensor:
        """y_obs = image with the inpainted region zeroed (kept top half)."""
        return x * self.mask_obs

    def condition(self, x: torch.Tensor, rows=None) -> torch.Tensor:
        """Conditioning tensor fed to the U-Net.

        For ``cond_kind="inpaint"`` this is [observed image ; mask], and it is a
        function of ``x`` alone. For ``cond_kind="class"`` it is the one-hot class
        broadcast over the spatial grid -- which keeps the U-Net's
        ``forward(x, t, cond)`` signature unchanged for the price of a few constant
        channels -- and it is *not* a function of ``x``, so ``rows`` must say which
        rows of ``self.labels`` the batch corresponds to. It defaults to all of them,
        which is right when ``x`` is the whole of ``self.X``; callers passing a slice
        must pass the matching slice here.
        """
        if self.cond_kind == "class":
            lab = self.labels if rows is None else self.labels[rows]
            if lab.shape[0] != x.shape[0]:
                raise ValueError(
                    f"condition(): {x.shape[0]} rows of x but {lab.shape[0]} labels; "
                    "pass rows= matching the slice of X")
            oh = torch.zeros(x.shape[0], self.n_classes, dtype=x.dtype,
                             device=x.device)
            oh[torch.arange(x.shape[0]), lab.to(x.device)] = 1.0
            return oh[:, :, None, None].expand(-1, -1, x.shape[2], x.shape[3])
        obs = self.observation(x)
        mask = self.mask_obs.expand(x.shape[0], -1, -1, -1)
        return torch.cat([obs, mask], dim=1)             # (B, 2, 32, 32)

    @property
    def cond_channels(self) -> int:
        return self.n_classes if self.cond_kind == "class" else self.channels + 1
