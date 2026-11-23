"""Exact endpoint basin maps on the triangle of Section 6 (data for Figure fig:unrolled of paper_theory).

    PYTHONPATH=.:scripts python scripts/theory_basin_map.py [--workers 48] [--n-grid 500]

Configuration: the triangle of Section sec:intervention-tests (scripts/learned_composition_2d.py,
scripts/spectral_criterion_check.py): three atoms a_k on the unit circle around z = 0, conditional
priors p_k(j) proportional to exp(B 1{j = k}) with B = 2 (the label weights of the exact field at the
query y = B e_k for one-hot labels and h = 1) and the uniform unconditional prior. Every field below
is sum_k c_k v_{p_k} with coefficients summing to one. In tau = -log(1-t) it reads

    dx/dtau = M(x, t) - x,    M = sum_k c_k m_{p_k},

where m_p is the posterior mean of the atoms under the prior p, with weights proportional to
p_j exp(beta <x, a_j>), beta = t/(1-t)^2 (the term -t^2 |a_j|^2 / 2(1-t)^2 is the same for every
atom because |a_j| = 1), computed by log-sum-exp in float64. The fields are

    one    v_{p_0}                               the exact field at one noised label (one field)
    cfg    (1+w) v_{p_0} - w v_unc               guidance (two fields)
    conj   (1+w)/3 sum_k v_{p_k} - w v_unc       guidance on the average of the three conditional
                                                 fields, i.e. the conjunction (four fields)

with w = r w_c and w_c = (1-m^2)/m^2, m = (e^B - 1)/(e^B + 2), the threshold of Corollary
cor:spectral-threshold for the centre (w_c = 1.1596 at B = 2).

Integration, as in scripts/learned_composition_2d.py (exact_classes): RK4 in x and tau up to
t = 1/2 (1000 steps), then the exact blown-up system for xi = beta x in the fast time u, du = beta
dtau,

    dxi/du = M(xi) + xi/(t beta),   dtau/du = 1/beta,

with scipy's RK45 (rtol 1e-9, atol 1e-10) from u = 0 to U_END = 1e4, where 1-t = 7.0e-3. The
system is exact (a change of variables, no off-tie term is dropped) and not stiff in u. Endpoint
classes at the checkpoints U_CHECK:

    3        the centre 0, if the profile is bounded, |xi| < 5;
    4 + k    the midpoint of the edge opposite a_k, if |x - z| < 0.2 there and the edge profile
             <xi, (a_i - a_j)/2> is bounded by 5;
    k        the atom a_k, if |x - a_k| < 0.2 and every posterior puts weight > 1 - 1e-6 on a_k;
    7        unresolved otherwise.

The edge midpoints are candidates of Section sec:intervention-atomicity: at the edge (a_i, a_j)
the conditional priors restricted to the tie have log-odds 2B(p) = B, -B, 0 and the unconditional
0, so the profile function is F(s) = (1+w)/3 [tanh(s + B/2) + tanh(s - B/2)] + ((1+w)/3 - w) tanh s,
with F'(0) = 1 - 2 (1+w)/3 tanh^2(B/2) (Proposition prop:twoatom): the edge midpoints attract for
w > (3/(2 tanh^2(B/2)) - 1), i.e. w/w_c > 1.368 at B = 2, while the centre attracts for w > w_c.
The script reports both, and the class of every source at every checkpoint.

Outputs, under results/theory_basin_map_20261121/:
  maps.npz      the endpoint class of every initial point of an n x n grid on [-L, L]^2 for each
                panel field (and the atoms);
  summary.json  per field: Monte Carlo endpoint fractions from N_MC fresh N(0, I_2) sources
                (seed 20261121) with binomial standard errors, the grid estimate (pi_0-weighted
                fraction of grid points, truncated to the square), the number of unresolved
                sources and of sources whose class changes between u = 1e3 and U_END; and the
                check against results/learned_composition_2d_20261021/exact: the same 4096
                shared sources (torch generator, seed 20261021) and the same atoms (as recorded
                in results/learned_composition_2d_20261021/cfm_v_seed0/summary.json),
                classified here at r in {0, 0.5, 0.9, 1.1, 2, 5, 10}, against exact_classes.npz.

Two further modes add keys to the same summary.json and leave the others unchanged:

  --faces          the configurations of Table tab:spectral (triangle and nine-vertex simplex with
                   one prior per vertex, rectangle and 256-vertex box with product priors), with the
                   sources and the integration of scripts/spectral_criterion_check.py (seed 11, RK4 to
                   t = 1/2, RK45 at rtol 1e-8 to u = 1e4). Every endpoint is classified by the face
                   whose centroid it converges to (face_classes below): its size k is 1 for an atom,
                   N for the centre z = 0, and 1 < k < N for a blend at another non-atom candidate.
                   Key "faces".
  --learned-edges  the stored endpoints of results/learned_composition_2d_20261021/{cfm_v, cfm_x_s,
                   distill_x_s}_seed0-4 (arm L3, every stored gap 1 - t and strength): the number of
                   sources within 0.05 of an edge midpoint of the triangle, and the fraction farther
                   than 0.1 from every atom and from the centre. Key "learned_edge_counts".
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

OUT = Path("results/theory_basin_map_20261121")
B = 2.0
U_END = 1e4
U_CHECK = (1e2, 1e3, 3e3, 1e4)
N_RK4 = 1000                     # RK4 steps in x from t = 0 to t = 1/2
R_PROFILE = 5.0                  # bounded profile
R_NEAR = 0.2                     # distance to a candidate at the checkpoint
CHUNK = 1024
N_MC = 32768
MC_SEED = 20261121
EXACT_2D = Path("results/learned_composition_2d_20261021/exact")


def m_of(Bv: float = B) -> float:
    return (math.exp(Bv) - 1) / (math.exp(Bv) + 2)


def w_c(Bv: float = B) -> float:
    m = m_of(Bv)
    return (1 - m * m) / (m * m)


def edge_threshold(Bv: float = B) -> float:
    """w above which the edge midpoints attract: F'(0) = 1 - 2(1+w)/3 tanh^2(B/2) < 0."""
    return 3.0 / (2.0 * math.tanh(Bv / 2) ** 2) - 1.0


def triangle(top: bool = True) -> np.ndarray:
    """Atoms on the unit circle: vertex 0 at the top (display), or the atoms of the earlier runs.

    simplex(3) of scripts/spectral_criterion_check.py takes an SVD basis of a matrix with a repeated
    singular value, which LAPACK builds may return rotated; the earlier triangle runs record their
    atoms in every summary.json, and the check below uses those.
    """
    if top:
        ang = np.pi / 2 + 2 * np.pi * np.arange(3) / 3
        return np.stack([np.cos(ang), np.sin(ang)], 1)
    rec = json.loads((EXACT_2D.parent / "cfm_v_seed0" / "summary.json").read_text(encoding="utf-8"))
    A = np.array(rec["atoms"], dtype=np.float64)
    assert A.shape == (3, 2) and np.allclose(np.linalg.norm(A, axis=1), 1, atol=1e-12)
    return A


def priors(Bv: float = B) -> tuple[np.ndarray, np.ndarray]:
    """Log conditional priors (3, 3), row k favouring vertex k, and the log uniform prior (3,)."""
    logp = np.eye(3) * Bv
    logp -= np.log(np.exp(logp).sum(1, keepdims=True))
    return logp, np.full(3, -math.log(3))


def field_spec(kind: str, r: float = 0.0, Bv: float = B) -> tuple[np.ndarray, np.ndarray]:
    """(coefficients c, log priors) of the signed combination sum_k c_k v_{p_k}."""
    lc, lu = priors(Bv)
    w = r * w_c(Bv)
    if kind == "one":
        return np.array([1.0]), lc[:1]
    if kind == "cfg":
        return np.array([1 + w, -w]), np.vstack([lc[0], lu])
    if kind == "conj":
        return np.array([(1 + w) / 3] * 3 + [-w]), np.vstack([lc, lu])
    raise ValueError(kind)


def M(xi: np.ndarray, A: np.ndarray, c: np.ndarray, logp: np.ndarray) -> np.ndarray:
    """sum_k c_k (posterior mean under prior k) at the blown-up position xi = beta x; (n, 2)."""
    lg = logp[:, None, :] + (xi @ A.T)[None]
    lg = lg - lg.max(-1, keepdims=True)
    q = np.exp(lg)
    q /= q.sum(-1, keepdims=True)
    return np.tensordot(c, q @ A, axes=1)


def beta_of(tau: float) -> float:
    return -math.expm1(-tau) * math.exp(2 * tau)


def classify(xi: np.ndarray, tau: float, A: np.ndarray, logp: np.ndarray) -> np.ndarray:
    beta = beta_of(tau)
    x = xi / beta
    cls = np.full(len(xi), 7, np.int8)
    # atoms: close, and every posterior (all priors used) concentrated on the atom
    lg = logp[:, None, :] + (xi @ A.T)[None]
    lg = lg - lg.max(-1, keepdims=True)
    q = np.exp(lg)
    q /= q.sum(-1, keepdims=True)
    for k in range(3):
        ok = (np.linalg.norm(x - A[k], axis=1) < R_NEAR) & (q[:, :, k].min(0) > 1 - 1e-6)
        cls[ok] = k
    for k in range(3):                               # the edge opposite a_k
        i, j = [m for m in range(3) if m != k]
        z = (A[i] + A[j]) / 2
        sig = xi @ ((A[i] - A[j]) / 2)
        ok = (np.linalg.norm(x - z, axis=1) < R_NEAR) & (np.abs(sig) < R_PROFILE)
        cls[ok] = 4 + k
    cls[np.linalg.norm(xi, axis=1) < R_PROFILE] = 3
    return cls


def endpoints(x0: np.ndarray, A: np.ndarray, c: np.ndarray, logp: np.ndarray) -> np.ndarray:
    """Classes (len(U_CHECK), n) of the exact flow from x0 (n, 2)."""
    n = len(x0)
    tau0 = math.log(2.0)
    h = tau0 / N_RK4

    def f1(x, tau):
        return M(beta_of(tau) * x, A, c, logp) - x
    x, tau = x0.astype(np.float64).copy(), 0.0
    for _ in range(N_RK4):
        k1 = f1(x, tau); k2 = f1(x + h / 2 * k1, tau + h / 2)
        k3 = f1(x + h / 2 * k2, tau + h / 2); k4 = f1(x + h * k3, tau + h)
        x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); tau += h

    def f2(u, y):
        xi, ta = y[:-1].reshape(n, 2), y[-1]
        t = -math.expm1(-ta); be = beta_of(ta)
        return np.concatenate([(M(xi, A, c, logp) + xi / (t * be)).ravel(), [1.0 / be]])

    y0 = np.concatenate([(beta_of(tau0) * x).ravel(), [tau0]])
    sol = solve_ivp(f2, (0.0, U_END), y0, method="RK45", rtol=1e-9, atol=1e-10, t_eval=U_CHECK)
    assert sol.success, sol.message
    return np.stack([classify(sol.y[:-1, i].reshape(n, 2), sol.y[-1, i], A, logp)
                     for i in range(len(U_CHECK))])


def _job(args):
    x0, A, c, logp = args
    return endpoints(x0, A, c, logp)


def run_points(pool, x0, A, c, logp) -> np.ndarray:
    chunks = [x0[i:i + CHUNK] for i in range(0, len(x0), CHUNK)]
    res = list(pool.map(_job, [(ch, A, c, logp) for ch in chunks]))
    return np.concatenate(res, axis=1)


def fractions(cls: np.ndarray) -> dict:
    n = len(cls)
    out = {}
    for name, sel in (("atom0", cls == 0), ("atom1", cls == 1), ("atom2", cls == 2),
                      ("centre", cls == 3), ("edges", (cls >= 4) & (cls <= 6)),
                      ("unresolved", cls == 7)):
        p = float(sel.mean())
        out[name] = {"p": p, "se": math.sqrt(p * (1 - p) / n), "count": int(sel.sum())}
    out["edge_each"] = [int((cls == 4 + k).sum()) for k in range(3)]
    return out


PANELS = (("one", 0.0), ("cfg", 2.0), ("conj", 2.0))
EXTRA = (("conj", 1.1), ("conj", 1.5), ("conj", 5.0), ("conj", 10.0))
CHECK_R = (0.0, 0.5, 0.9, 1.1, 2.0, 5.0, 10.0)

# --- --faces: every candidate of the configurations of Table tab:spectral ---------------------
FACE_GAP = 50.0                  # log-weight gap separating the atoms of a face from the others
SPECTRAL_SEED = 11               # the sources of scripts/spectral_criterion_check.py
SPECTRAL = Path("results/theory_spectral_20261020/summary.json")


def face_classes(xi: np.ndarray, tau: float, A: np.ndarray, logp: np.ndarray) -> np.ndarray:
    """Size k of the face whose centroid each source converges to (1: an atom, len(A): the centre
    z = 0), or 0 if unresolved. Every atom lies on the unit sphere, so the uniform posterior weights
    are proportional to exp(<xi, a_j>); the face is the set of atoms whose weight is within
    e^FACE_GAP of the largest. A face of k >= 2 atoms is accepted when its centroid z has exactly
    these atoms as nearest atoms, the trajectory is within R_NEAR of z and the profile
    beta P_L(x - t z), L = span{a - z : a in the face}, is bounded by R_PROFILE (for the centre this
    is |xi| < 5, the criterion of Table tab:spectral); an atom is accepted as in classify()."""
    beta = beta_of(tau)
    t = -math.expm1(-tau)
    x = xi / beta
    ell = xi @ A.T
    member = ell > ell.max(1, keepdims=True) - FACE_GAP
    lg = logp[:, None, :] + ell[None]
    lg = lg - lg.max(-1, keepdims=True)
    q = np.exp(lg)
    q /= q.sum(-1, keepdims=True)
    out = np.zeros(len(xi), np.int64)
    for i in range(len(xi)):
        F = np.flatnonzero(member[i])
        if len(F) == 1:
            j = F[0]
            if np.linalg.norm(x[i] - A[j]) < R_NEAR and q[:, i, j].min() > 1 - 1e-6:
                out[i] = 1
            continue
        z = A[F].mean(0)
        dist = np.linalg.norm(A - z, axis=1)
        if not np.array_equal(np.flatnonzero(dist < dist.min() + 1e-9), F):
            continue
        _, S, Vt = np.linalg.svd(A[F] - z)
        P = Vt[:len(S)][S > 1e-9 * S.max()]
        if (np.linalg.norm(x[i] - z) < R_NEAR
                and np.linalg.norm(beta * P @ (x[i] - t * z)) < R_PROFILE):
            out[i] = len(F)
    return out


def free_axes(xi: np.ndarray, tau: float, A: np.ndarray, half: np.ndarray) -> list:
    """For product configurations: (long, short) numbers of axes on which the face of each source
    varies, i.e. the axes whose coordinate ends at 0."""
    ell = xi @ A.T
    member = ell > ell.max(1, keepdims=True) - FACE_GAP
    long = half == half.max()
    out = []
    for i in range(len(xi)):
        F = np.flatnonzero(member[i])
        var = np.ptp(A[F], axis=0) > 1e-9
        out.append((int((var & long).sum()), int((var & ~long).sum())))
    return out


def _spectral_jobs():
    import spectral_criterion_check as sc
    B = 2.0
    jobs = []
    for name, n_v, n_src in (("tri2", 3, 2048), ("simplex8", 9, 2048)):
        m = (math.exp(B) - 1) / (math.exp(B) + n_v - 1)
        wc = (1 - m * m) / (m * m)
        for ratio in (0.5, 0.9, 1.1, 2.0, 5.0):
            jobs.append(dict(name=name, kind="simplex", n_v=n_v, n_src=n_src, w=ratio * wc,
                             w_over_wc=ratio, w_c=wc))
    for name, half, Bv, n_src in (("rect2", [2.0, 1.0], [2.0, 0.5], 2048),
                                  ("cube8", [2.0] * 4 + [1.0] * 4, [2.0] * 4 + [0.5] * 4, 512)):
        for w in (1.0, 5.0):
            jobs.append(dict(name=name, kind="product", half=half, B_axes=Bv, n_src=n_src, w=w))
    return sc, jobs


def _face_job(job: dict) -> dict:
    sc, _ = _spectral_jobs()
    if job["kind"] == "simplex":
        atoms = sc.simplex(job["n_v"])
        fld = sc.Field(atoms, sc.vertex_priors(job["n_v"], 2.0), job["w"])
        half = None
    else:
        half = np.array(job["half"])
        atoms, logp, _ = sc.product_config(half, np.array(job["B_axes"]))
        fld = sc.Field(atoms, logp, job["w"])
    t0 = time.time()
    res = sc.run(fld, job["n_src"], seed=SPECTRAL_SEED, keep_states=True)
    N = len(atoms)
    cls = [face_classes(xi, tau, atoms, fld.logp) for xi, tau in zip(res["states"], res["taus"])]
    i3 = list(sc.U_CHECK).index(1e3)
    end = cls[-1]
    n = len(end)
    row = {k: v for k, v in job.items() if k != "kind"}
    row.update(N=N, d=atoms.shape[1], seed=SPECTRAL_SEED,
               face_size_counts={int(k): int((end == k).sum()) for k in sorted(set(end.tolist()))},
               atom_fraction=float((end == 1).mean()), centre_fraction=float((end == N).mean()),
               blend_fraction=float(((end > 1) & (end < N)).mean()),
               unresolved=int((end == 0).sum()), changed_after_1e3=int((cls[i3] != end).sum()),
               centre_bounded_profile_fraction=res["checkpoints"][-1]["frac_bounded"],
               nfev=res["nfev"], seconds=time.time() - t0)
    if half is not None:
        fa = free_axes(res["states"][-1], res["taus"][-1], atoms, half)
        hist = {}
        for (nl, ns), k in zip(fa, end):
            if k > 0:
                hist[f"{nl}long_{ns}short"] = hist.get(f"{nl}long_{ns}short", 0) + 1
        row["free_axes_counts"] = dict(sorted(hist.items()))
    try:                                              # the value printed in Table tab:spectral
        table = json.loads(SPECTRAL.read_text(encoding="utf-8"))["configs"]
        for c in table:
            same = c["name"] == job["name"] and (abs(c.get("w_over_wc", -1) - job.get("w_over_wc", -2)) < 1e-12
                                                  or (job["kind"] == "product" and c["w"] == job["w"]))
            if same:
                row["table_fraction_bounded"] = c["result"]["checkpoints"][-1]["frac_bounded"]
    except FileNotFoundError:
        pass
    return row


def run_faces(workers: int) -> dict:
    _, jobs = _spectral_jobs()
    with ProcessPoolExecutor(min(workers, len(jobs))) as pool:
        rows = list(pool.map(_face_job, jobs))
    for r in rows:
        print("faces", r["name"], r.get("w_over_wc", r["w"]), r["face_size_counts"],
              "unresolved", r["unresolved"], "changed", r["changed_after_1e3"],
              "centre", r["centre_fraction"], "table", r.get("table_fraction_bounded"), flush=True)
    return {"note": "face sizes at u = 1e4 (1: atom, N: the centre z = 0, between: another blend); "
                    "sources and integration of scripts/spectral_criterion_check.py",
            "face_gap": FACE_GAP, "r_profile": R_PROFILE, "r_near": R_NEAR, "rows": rows}


# --- --learned-edges: stored learned endpoints on the triangle ----------------------------------
LEARNED_2D = Path("results/learned_composition_2d_20261021")
LEARNED_VARIANTS = ("cfm_v", "cfm_x_s", "distill_x_s")


def learned_edges() -> dict:
    rows = []
    for v in LEARNED_VARIANTS:
        for seed in range(5):
            d = LEARNED_2D / f"{v}_seed{seed}"
            rec = json.loads((d / "summary.json").read_text(encoding="utf-8"))
            A = np.array(rec["atoms"], dtype=np.float64)
            mids = np.array([(A[i] + A[j]) / 2 for i, j in ((1, 2), (0, 2), (0, 1))])
            fin = np.load(d / "final_states.npz")
            for key in fin.files:
                if not key.startswith("L3_r"):
                    continue
                X = fin[key].astype(np.float64)                    # (gaps, sources, 2)
                for e, eps in enumerate(rec["eps_out"]):
                    x = X[e]
                    de = np.linalg.norm(x[:, None] - mids[None], axis=-1).min(1)
                    da = np.linalg.norm(x[:, None] - A[None], axis=-1).min(1)
                    dc = np.linalg.norm(x, axis=1)
                    rows.append({"variant": v, "seed": seed, "r": float(key[4:]), "eps": eps, "n": len(x),
                                 "edge_count_0.05": int((de < 0.05).sum()),
                                 "edge_count_0.2": int((de < 0.2).sum()),
                                 "off_atoms_and_centre_0.1": float(((da >= 0.1) & (dc >= 0.1)).mean()),
                                 "off_every_candidate_0.1": float(((da >= 0.1) & (dc >= 0.1) & (de >= 0.1)).mean())})
    summ = {}
    for v in LEARNED_VARIANTS:
        last = [r for r in rows if r["variant"] == v and r["eps"] == 1e-5]
        top = max(last, key=lambda r: r["edge_count_0.05"])
        off = {}
        for r_ in sorted({r["r"] for r in last}):
            vals = np.array([r["off_atoms_and_centre_0.1"] for r in last if r["r"] == r_])
            off[f"{r_:g}"] = [float(vals.mean()), float(vals.std())]
        summ[v] = {"max_edge_count_0.05_at_eps_1e-5": top["edge_count_0.05"],
                   "argmax": {"seed": top["seed"], "r": top["r"]},
                   "n_sources": top["n"],
                   "off_atoms_and_centre_0.1_at_eps_1e-5_mean_sd": off}
        print("learned edges", v, summ[v], flush=True)
    return {"note": "arm L3 of results/learned_composition_2d_20261021, every stored gap and strength; "
                    "edge midpoints (a_i + a_j)/2 with the atoms of each summary.json; "
                    "off_atoms_and_centre_0.1 is the 'learned off all atoms' column of its SUMMARY.md",
            "summary": summ, "rows": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--n-grid", type=int, default=500)
    ap.add_argument("--half-width", type=float, default=2.5)
    ap.add_argument("--skip-check", action="store_true")
    ap.add_argument("--only", default="", help="comma list of field tags to run, e.g. conj_r2")
    ap.add_argument("--faces", action="store_true", help="face masses of Table tab:spectral only")
    ap.add_argument("--learned-edges", action="store_true", help="learned edge counts only")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.faces or args.learned_edges:
        path = OUT / "summary.json"
        summary = json.loads(path.read_text(encoding="utf-8"))
        if args.faces:
            summary["faces"] = run_faces(args.workers)
        if args.learned_edges:
            summary["learned_edge_counts"] = learned_edges()
        path.write_text(json.dumps(summary, indent=1), encoding="utf-8")
        print(f"wrote {path}")
        return
    A = triangle(top=True)
    L, n = args.half_width, args.n_grid
    g = np.linspace(-L, L, n)
    X, Y = np.meshgrid(g, g)                         # rows: y, columns: x
    grid = np.stack([X.ravel(), Y.ravel()], 1)
    dens = np.exp(-(grid ** 2).sum(1) / 2)
    mc = np.random.default_rng(MC_SEED).standard_normal((N_MC, 2))
    summary = {"script": "scripts/theory_basin_map.py", "B": B, "w_c": w_c(), "m": m_of(),
               "w_edge": edge_threshold(), "r_edge": edge_threshold() / w_c(), "atoms": A.tolist(),
               "U_END": U_END, "U_CHECK": list(U_CHECK), "n_grid": n, "half_width": L,
               "n_mc": N_MC, "mc_seed": MC_SEED, "fields": {}}
    prev = OUT / "summary.json"
    if prev.exists():
        old = json.loads(prev.read_text(encoding="utf-8"))
        summary["fields"] = old.get("fields", {})
        if "check_exact_2d" in old:
            summary["check_exact_2d"] = old["check_exact_2d"]
    arrays = dict(np.load(OUT / "maps.npz")) if (OUT / "maps.npz").exists() else {}
    arrays.update(atoms=A, grid=g)
    only = {s for s in args.only.split(",") if s}
    with ProcessPoolExecutor(args.workers) as pool:
        for kind, r in PANELS + EXTRA:
            tag = f"{kind}_r{r:g}"
            if only and tag not in only:
                continue
            c, logp = field_spec(kind, r)
            t0 = time.time()
            cm = run_points(pool, mc, A, c, logp)
            cg = run_points(pool, grid, A, c, logp)
            fin = cg[-1]
            arrays[tag] = fin.reshape(n, n)
            gfrac = {k: float((dens * (fin == k)).sum() / dens.sum()) for k in range(8)}
            row = {"kind": kind, "r": r, "w": r * w_c(), "c": c.tolist(),
                   "mc": fractions(cm[-1]),
                   "mc_changed_after_1e3": int((cm[1] != cm[-1]).sum()),
                   "grid_pi0_fraction": gfrac,
                   "grid_unresolved": int((fin == 7).sum()),
                   "grid_changed_after_1e3": int((cg[1] != cg[-1]).sum()),
                   "seconds": time.time() - t0}
            summary["fields"][tag] = row
            print(tag, json.dumps(row["mc"]), "changed", row["mc_changed_after_1e3"],
                  row["grid_changed_after_1e3"], "unresolved", row["grid_unresolved"],
                  f"{row['seconds']:.0f}s", flush=True)
            np.savez_compressed(OUT / "maps.npz", **arrays)
            (OUT / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

        if not args.skip_check:
            # the 4096 shared sources and the atoms of results/learned_composition_2d_20261021/exact
            import torch
            src = torch.randn(16384, 2, generator=torch.Generator().manual_seed(20261021))
            x0 = src[:4096].double().numpy()
            A0 = triangle(top=False)
            ref = np.load(EXACT_2D / "exact_classes.npz")
            ref_json = {row["r"]: row for row in
                        json.loads((EXACT_2D / "exact.json").read_text(encoding="utf-8"))["rows"]}
            check = []
            for r in CHECK_R:
                c, logp = field_spec("conj", r)
                cls = run_points(pool, x0, A0, c, logp)[-1]
                old = ref[f"classes_r{r:g}"]
                edge = (cls >= 4) & (cls <= 6)
                # an edge class is reported by the earlier argmax classifier as one of its two atoms
                edge_ok = all(old[i] in [m for m in range(3) if m != cls[i] - 4]
                              for i in np.where(edge)[0])
                row = {"r": r, "centre_fraction": float((cls == 3).mean()),
                       "reference_midpoint_fraction": ref_json[r]["midpoint_fraction"],
                       "centre_disagreements": int(((cls == 3) != (old == 3)).sum()),
                       "atom_disagreements": int(((cls <= 2) & (cls != old)).sum()),
                       "edge_count": int(edge.sum()), "edge_reported_as_an_edge_atom": bool(edge_ok),
                       "unresolved": int((cls == 7).sum())}
                check.append(row)
                print("check", row, flush=True)
            summary["check_exact_2d"] = check
            (OUT / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
