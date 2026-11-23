"""Shared helpers of the uncertainty analyses (numpy only).

Shared by the uncertainty scripts: Student-t and normal quantiles without scipy, the
paper-style number formatting, the exact seed bootstrap of a five-seed mean, and the EXP-1
per-seed readers. Nothing here writes a file.
"""
from __future__ import annotations

import csv
import glob
import itertools
import math
import re
from pathlib import Path

import numpy as np

SEED = 20261121
B_SLOPE = 20000
B_AUC = 10000
ALPHA = 0.05


# ============================================================================ distributions (numpy only)
def _t_cdf_pos(t: float, df: int) -> float:
    """P(T <= t) for t >= 0: Simpson integration of the Student-t density on [0, t]."""
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    xs = np.linspace(0.0, t, 40001)
    f = c * (1.0 + xs ** 2 / df) ** (-(df + 1) / 2)
    h = xs[1] - xs[0]
    return 0.5 + h / 3 * (f[0] + f[-1] + 4 * f[1:-1:2].sum() + 2 * f[2:-1:2].sum())


def t_ppf(p: float, df: int) -> float:
    lo, hi = 0.0, 100.0
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if _t_cdf_pos(mid, df) < p else (lo, mid)
    return 0.5 * (lo + hi)


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if norm_cdf(mid) < p else (lo, mid)
    return 0.5 * (lo + hi)


KNOWN_T975 = {1: 12.706204736174698, 2: 4.302652729749464, 4: 2.7764451051977987}
_TQ: dict[int, float] = {}


def tq(df: int) -> float:
    if df not in _TQ:
        _TQ[df] = t_ppf(0.975, df)
    return _TQ[df]


Z975 = norm_ppf(0.975)



# ============================================================================ small helpers
def rel(p) -> str:
    return Path(p).as_posix()


def fnum(x: float, d: int) -> str:
    s = f"{x:.{d}f}"
    return s[1:] if s.startswith("-") and float(s) == 0 else s


def cell(m: float, lo: float, hi: float, d: int) -> str:
    """Paper style of tab:cifarddpm: $m$\\,[$lo$, $hi$]."""
    return f"${fnum(m, d)}$\\,[${fnum(lo, d)}$, ${fnum(hi, d)}$]"


def parse_pm(s: str):
    """'0.396+-0.127' -> (0.396, 0.127, 3, 3); '0.583' -> (0.583, None, 3, None)."""
    if "+-" in s:
        a, b = s.split("+-")
        return float(a), float(b), len(a.split(".")[1]) if "." in a else 0, len(b.split(".")[1]) if "." in b else 0
    return float(s), None, len(s.split(".")[1]) if "." in s else 0, None


def matches(value: float, paper: float, d: int) -> bool:
    return abs(round(value, d) - paper) < 0.5 * 10 ** (-d) + 1e-12


def seed_summary(v) -> dict:
    """Mean, population SD (as printed), sample SD, t-interval (df=n-1), exact seed-bootstrap interval."""
    v = np.asarray(v, float)
    n = v.size
    m, sdp, sd = float(v.mean()), float(v.std(ddof=0)), float(v.std(ddof=1))
    se = sd / math.sqrt(n)
    tc = tq(n - 1)
    idx = np.array(list(itertools.product(range(n), repeat=n)))      # all n^n equally likely resamples
    bm = v[idx].mean(1)
    blo, bhi = (float(q) for q in np.percentile(bm, [2.5, 97.5]))
    return {"n": int(n), "values": [float(x) for x in v], "mean": m, "sd_pop": sdp, "sd_sample": sd,
            "se": se, "t_crit": tc, "t_lo": m - tc * se, "t_hi": m + tc * se, "boot_lo": blo,
            "boot_hi": bhi, "boot_resamples": int(len(bm))}



def check_t_quantiles() -> dict:
    """Fail loudly if the numeric t quantiles drift from their known values."""
    tchk = {df: tq(df) for df in KNOWN_T975}
    for df, v in tchk.items():
        assert abs(v - KNOWN_T975[df]) < 1e-6, (df, v)
    print("t quantiles (0.975):", {df: round(v, 6) for df, v in tchk.items()}, " z:", round(Z975, 6))
    return tchk


# ============================================================================ EXP-1 per-seed readers
EXP1 = Path("results/exp1")
PAT = {"cond": f"{EXP1.as_posix()}/exp1_cond_seed[0-4]/raw/metrics.csv",
       "cos": f"{EXP1.as_posix()}/exp1_ext_sched_seed[0-4]/raw/metrics.csv",
       "uncond": f"{EXP1.as_posix()}/exp1_uncond_seed[0-4]/raw/metrics.csv",
       "cond_mr": f"{EXP1.as_posix()}/exp1_cond_seed[0-4]_mr/raw/metrics.csv",
       "uncond_mr": f"{EXP1.as_posix()}/exp1_uncond_seed[0-4]_mr/raw/metrics.csv"}
P7_CSV = EXP1 / "_theory" / "raw" / "p7_kernel.csv"


def _csv_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def per_seed(key: str, group: str, col: str, it: int):
    files = sorted(glob.glob(PAT[key]))
    assert len(files) == 5, (PAT[key], files)
    vals, seeds = [], []
    for f in files:
        rows = [r for r in _csv_rows(f) if r["group"] == group and int(float(r["iter"])) == it]
        assert len(rows) == 1, (f, group, it, len(rows))
        vals.append(float(rows[0][col]))
        seeds.append(int(re.search(r"seed(\d)", f).group(1)))
    assert seeds == [0, 1, 2, 3, 4], seeds
    return np.array(vals)


def _entry(paper: str, s: dict, source: str) -> dict:
    pm, ppm, d, dpm = parse_pm(paper)
    e = dict(s)
    e.update({"source": source, "paper": paper, "paper_mean": pm, "paper_pm": ppm, "decimals": d,
              "mean_matches_paper": matches(s["mean"], pm, d),
              "sd_pop_matches_paper": None if ppm is None else matches(s["sd_pop"], ppm, dpm)})
    return e



def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o

