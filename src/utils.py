"""Shared utilities: seeding, config loading, device, IO.

Reproducibility is a first-class concern for this project (Section 7.1 of the
spec): every run fixes all RNG seeds and dumps the fully-resolved config next
to its outputs so figures can be regenerated without retraining.
"""
from __future__ import annotations

import copy
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml


# --------------------------------------------------------------------------- #
# Reproducibility
# --------------------------------------------------------------------------- #
def set_seed(seed: int) -> None:
    """Seed every RNG we touch. See spec Section 7.1."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_device(prefer: str = "auto") -> torch.device:
    if prefer == "cpu":
        return torch.device("cpu")
    if prefer == "cuda" or (prefer == "auto" and torch.cuda.is_available()):
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device("cpu")


# --------------------------------------------------------------------------- #
# Config: YAML load + dotted-key CLI overrides
# --------------------------------------------------------------------------- #
def load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _coerce(value: str) -> Any:
    """Turn a CLI string into an int/float/bool/None/list where sensible."""
    lowered = value.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    if lowered in ("null", "none"):
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    # bracketed or comma-separated -> list of coerced items
    stripped = value.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        inner = stripped[1:-1].strip()
        if not inner:
            return []
        return [_coerce(v.strip()) for v in inner.split(",")]
    if "," in value:
        return [_coerce(v.strip()) for v in value.split(",")]
    return value


def set_dotted(cfg: dict, dotted_key: str, value: Any) -> None:
    keys = dotted_key.split(".")
    node = cfg
    for k in keys[:-1]:
        node = node.setdefault(k, {})
    node[keys[-1]] = value


def apply_overrides(cfg: dict, overrides: list[str]) -> dict:
    """Apply a list of ``a.b.c=value`` override strings (mutates a copy)."""
    cfg = copy.deepcopy(cfg)
    for ov in overrides or []:
        if "=" not in ov:
            raise ValueError(f"Override '{ov}' must be of the form key.path=value")
        key, raw = ov.split("=", 1)
        set_dotted(cfg, key.strip(), _coerce(raw.strip()))
    return cfg


def dump_config(cfg: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)


# --------------------------------------------------------------------------- #
# Checkpoint schedule
# --------------------------------------------------------------------------- #
def default_checkpoints(max_iters: int) -> list[int]:
    """Log-spaced checkpoints (spec Section 3.4). Always includes max_iters."""
    base = [100, 300, 1000, 3000, 10000, 30000, 100000, 200000]
    ckpts = sorted({c for c in base if c <= max_iters} | {max_iters})
    return ckpts


# --------------------------------------------------------------------------- #
# Small JSON/CSV helpers
# --------------------------------------------------------------------------- #
def save_json(obj: Any, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=_json_default)


def _json_default(o: Any):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, torch.Tensor):
        return o.detach().cpu().tolist()
    raise TypeError(f"Not JSON serializable: {type(o)}")


@dataclass
class RunPaths:
    root: Path
    figures: Path
    raw: Path
    checkpoints: Path

    @classmethod
    def make(cls, root: str | Path) -> "RunPaths":
        root = Path(root)
        figures = root / "figures"
        raw = root / "raw"
        checkpoints = root / "checkpoints"
        for p in (figures, raw, checkpoints):
            p.mkdir(parents=True, exist_ok=True)
        return cls(root, figures, raw, checkpoints)
