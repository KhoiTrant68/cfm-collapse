"""Oracle interventions and exact matched-teacher-loss illustration; no training.

Integrate in s=-log(1-t); the right side is m(x,t)-x. Saved finite-time
distances illustrate convergence; they do not prove atomicity or null basins.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np


def softmax(a):
    e = np.exp(a-a.max(-1, keepdims=True)); return e/e.sum(-1, keepdims=True)


def field(x, s, atoms, log_priors, hard, guidance):
    eps = np.exp(-s); t = -np.expm1(-s)
    spatial = -.5 * (((x[:, None]-t*atoms[None])/eps)**2).sum(-1)
    uncond = softmax(spatial) @ atoms
    if hard:
        cond = np.broadcast_to(atoms[0], x.shape)
    else:
        # An average of fields, not the field from averaging label priors.
        cond = (softmax(spatial[:, None]+log_priors[None]) @ atoms).mean(1)
    return (1+guidance)*cond-guidance*uncond-x


def solve(x0, atoms, log_priors, hard, guidance, steps):
    assert steps % 3 == 0
    x = x0.copy(); ds = np.log(1e6)/steps; out = []
    for i in range(steps):
        s = i*ds
        f = lambda z, u: field(z, u, atoms, log_priors, hard, guidance)
        a = f(x, s); b = f(x+ds*a/2, s+ds/2)
        c = f(x+ds*b/2, s+ds/2); d = f(x+ds*c, s+ds)
        x += ds*(a+2*b+2*c+d)/6
        if (i+1) % (steps//3) == 0:
            out.append(x.copy())
    assert np.isfinite(out).all()
    return np.array(out)


def matched_loss():
    rows = []
    for delta in (1e-2, 3e-3, 1e-3, 1e-4):
        A = np.log(1/delta)
        loss = delta*(1+1.5*A+7/6*A*A)  # divided by d
        L = 1/(3*loss); assert L >= 1
        # Independent integration of the polynomial teacher-risk profile on
        # each stage, avoiding a uniform t grid that misses the thin layer.
        v = np.linspace(.5, 1., 10001)
        f = (1+2*A*v)**2
        quadrature = delta*np.sum((f[1:]+f[:-1])*np.diff(v)/2)+delta/2
        assert abs(quadrature-loss) < 1e-8
        amplification_endpoint = delta*np.exp((2*A/delta)*(delta/2))
        lipschitz_endpoint = (1/L)*np.exp(-1)
        assert abs(amplification_endpoint-1) < 1e-12
        rows.append({'delta': delta, 'teacher_loss_per_d': loss, 'L': L,
                     'loss_quadrature_per_d': float(quadrature),
                     'counterexample_endpoint_variance_per_d': amplification_endpoint**2,
                     'lipschitz_endpoint_variance_per_d': lipschitz_endpoint**2})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seeds', nargs='+', type=int, default=[101, 102, 103, 104, 105])
    ap.add_argument('--M', type=int, default=128)
    ap.add_argument('--steps', type=int, default=768)
    ap.add_argument('--max-seconds', type=int, default=900)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic(); rows = []; raw = {}
    analytic = matched_loss()
    (args.out/'matched_loss.json').write_text(json.dumps(analytic, indent=2))
    # Source x0=0 remains at the midpoint of symmetric atoms; neighboring
    # sources must depart. This is an exceptional trajectory, not a basin test.
    tie_atoms = np.array([[-1., 0.], [1., 0.]])
    tie = solve(np.array([[0., 0.], [-1e-4, 0.], [1e-4, 0.]]), tie_atoms,
                np.zeros((1, 2)), False, 0, args.steps*2)
    assert np.max(np.abs(tie[:, 0])) < 1e-12
    assert np.max(np.abs(np.abs(tie[-1, 1:, 0])-1)) < 1e-3
    raw['symmetric_tie'] = tie
    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        atoms = rng.normal(size=(5, 2))*1.5; labels = rng.normal(size=(5, 1))
        x0 = rng.normal(size=(args.M, 2)); h = .7
        priors = -.5*((labels-labels[0])**2).sum(1)[None]/h**2
        queries = labels[0]+np.array([[-h], [0.], [h]])
        averaged = -.5*((queries[:, None]-labels[None])**2).sum(-1)/h**2
        raw[f'{seed}_atoms'] = atoms; raw[f'{seed}_labels'] = labels
        raw[f'{seed}_x0'] = x0
        arms = [(f'hard_cfg_w{w}', True, w, priors) for w in (0, 3, 12)]
        arms += [(f'label_smoothed_cfg_w{w}', False, w, priors) for w in (0, 3, 12)]
        arms += [('average_three_label_fields', False, 0, averaged)]
        for name, hard, w, lp in arms:
            if time.monotonic()-start > args.max_seconds:
                raise TimeoutError('oracle pilot budget exhausted')
            a = solve(x0, atoms, lp, hard, w, args.steps)
            b = solve(x0, atoms, lp, hard, w, args.steps*2)
            raw[f'{seed}_{name}_coarse'] = a; raw[f'{seed}_{name}_fine'] = b
            for j, eps in enumerate((1e-2, 1e-4, 1e-6)):
                distances = np.linalg.norm(b[j, :, None]-atoms[None], axis=-1)
                assigned = distances.argmin(1); count = np.bincount(assigned, minlength=len(atoms))
                freq = count/args.M; nz = freq > 0
                rows.append({'seed': seed, 'arm': name, 'eps': eps,
                    'mean_nearest_atom_distance': float(distances.min(1).mean()),
                    'max_nearest_atom_distance': float(distances.min(1).max()),
                    'paired_solver_displacement': float(np.linalg.norm(a[j]-b[j], axis=-1).mean()),
                    'conditioned_atom_fraction': float((assigned==0).mean()),
                    'atom_frequencies': freq.tolist(), 'atom_entropy': float(-(freq[nz]*np.log(freq[nz])).sum()),
                    'trace': float(b[j].var(0, ddof=1).sum())})
            print(f'seed={seed} {name}: nearest={rows[-1]["mean_nearest_atom_distance"]:.3g}, solver={rows[-1]["paired_solver_displacement"]:.3g}', flush=True)
        # Exact finite-time smoothed-endpoint law. Same atom choices/noise
        # across rho values isolate endpoint noise; this is not a guided ODE.
        W = softmax(priors)[0]; indices = rng.choice(len(atoms), args.M, p=W)
        z = rng.normal(size=x0.shape)
        for rho in (0., .15):
            b = []
            for eps in (1e-2, 1e-4, 1e-6):
                t = 1-eps
                samples = t*atoms[indices]+np.sqrt(eps**2+t**2*rho**2)*z; b.append(samples)
                distances = np.linalg.norm(samples[:, None]-atoms[None], axis=-1)
                rows.append({'seed': seed, 'arm': f'exact_target_noise_rho{rho}', 'eps': eps,
                    'mean_nearest_atom_distance': float(distances.min(1).mean()),
                    'trace': float(samples.var(0, ddof=1).sum()), 'exact_law_draw': True})
            raw[f'{seed}_target_noise_rho{rho}'] = np.array(b)
    np.savez_compressed(args.out/'raw.npz', **raw)
    result = {'status': 'completed', 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'M': args.M, 'steps': [args.steps, args.steps*2], 'seeds': args.seeds,
        'geometry': 'five atoms in R^2, scalar labels, Gaussian source', 'label_h': .7,
        'averaging': 'equal average of three fields at y0-h,y0,y0+h; not a continuum approximation claim',
        'elapsed_seconds': time.monotonic()-start, 'rows': rows,
        'warning': 'Numerical illustration only; frequencies do not identify exact guided endpoint weights.'}
    (args.out/'results.json').write_text(json.dumps(result, indent=2, allow_nan=False))
    print(f'completed in {result["elapsed_seconds"]:.1f}s', flush=True)


if __name__ == '__main__':
    main()
