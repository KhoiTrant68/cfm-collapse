"""Bounded checkpoint evaluation: calibration nulls, solver, held-out law, path risk.

Run as python -m scripts.theory_evidence_pilot --help. No training or old output edits.
Energy distance uses the biased V statistic; reference nulls use the same sample size.
This is a feasibility pilot, not an equivalence test or a global transfer certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import time
from pathlib import Path

import numpy as np
import torch

from src.flows.ode_solver import integrate
import src.metrics.calibration as calibration

# An adjacent snapshot permits the authorized two-file deployment without
# replacing the server's shared metric module or copying the full repository.
_snapshot = Path(__file__).with_name('calibration.py')
if _snapshot.exists():
    _spec = importlib.util.spec_from_file_location('pilot_calibration', _snapshot)
    calibration = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(calibration)
central_coverage, joint_pit, marginal_pit = (
    calibration.central_coverage, calibration.joint_pit, calibration.marginal_pit)
reference_central, reference_upper, upper_coverage = (
    calibration.reference_central, calibration.reference_upper, calibration.upper_coverage)
from src.models.mlp_velocity import build_model
from src.problems.linear_gaussian import LinearGaussianProblem
from src.utils import load_yaml
from scripts.heff_family_test import GRID, atomic_reference, knn_weights, weights


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ed(a, b):
    a, b = torch.as_tensor(a, dtype=torch.float64), torch.as_tensor(b, dtype=torch.float64)
    return float(2 * torch.cdist(a, b).mean() - torch.cdist(a, a).mean()
                 - torch.cdist(b, b).mean())


def controls():
    rng = np.random.default_rng(20261016)
    M, n = 64, 20000
    curves = {}
    for name in ('point_mass', 'quantized_gaussian', 'gaussian', 'collapsed', 'overdispersed'):
        if name == 'point_mass':
            s, truth = np.zeros((M, n)), np.zeros(n)
        else:
            truth = rng.normal(size=n)
            s = rng.normal(size=(M, n))
            if name == 'quantized_gaussian':
                s, truth = s.round(), truth.round()
            elif name == 'collapsed':
                s[:] = 0
            elif name == 'overdispersed':
                s *= 2
        curve = central_coverage(marginal_pit(s, truth, rng=rng))
        curves[name] = curve.tolist()
        if name in ('point_mass', 'quantized_gaussian', 'gaussian'):
            assert np.max(np.abs(curve - reference_central(M))) < .02, name
    assert curves['collapsed'][8] < .01
    assert curves['overdispersed'][4] > reference_central(M)[4] + .1
    # Every joint score is tied for a calibrated point mass.
    uj = np.array([joint_pit(np.zeros((M, 2)), np.zeros(2), rng=rng) for _ in range(1200)])
    assert np.max(np.abs(upper_coverage(uj) - reference_upper(M))) < .06
    # Permuting candidate points must permute their LOO scores.
    loo_mahalanobis = calibration.loo_mahalanobis
    z = rng.normal(size=(17, 3)); perm = rng.permutation(len(z))
    assert np.allclose(loo_mahalanobis(z)[perm], loo_mahalanobis(z[perm]))
    a = rng.normal(size=(256, 2)); assert abs(ed(a, a)) < 1e-12
    assert ed(a, a + 4) > 1
    # Hard-conditioned exact oracle has an affine trajectory at every finite T.
    source = torch.tensor(a, dtype=torch.float32)
    atom = torch.tensor([.3, -.7])
    def oracle(x, t, y):
        return (atom - x) / (1-t[:, None])
    errors = {}
    for steps in (100, 200, 400):
        endpoint = integrate(oracle, source, None, n_steps=steps, eps=.001)
        error = float((endpoint - (.999*atom+.001*source)).abs().max())
        assert error < 2e-5, (steps, error)
        errors[steps] = error
    return {'passed': True, 'marginal_curves': curves,
            'hard_oracle_max_coordinate_errors': errors,
            'joint_pointmass_curve': upper_coverage(uj).tolist(),
            'reference_central': reference_central(M).tolist()}


def family_weights(family, distances, scale):
    return knn_weights(distances, int(scale)) if family == 'knn' else weights(family, distances, scale)


def targeted_solver(args):
    """Frozen outlier sources: float32/64 RK4 and independent adaptive DOP853.

    The architecture explicitly casts its time embedding to float32; retain that
    operation. Float64 here refers to state and MLP arithmetic, not a new model.
    """
    from scipy.integrate import solve_ivp
    raw = np.load(args.targeted_raw)
    run = Path('results/exp1')/args.runs[0]; cfg=load_yaml(run/'config.yaml')
    dc=cfg['data']; ck=run/'checkpoints'/'ckpt_200000.pt'
    state=torch.load(ck,map_location='cpu',weights_only=False)['model_state']
    j=20+args.target_condition
    source=torch.tensor(raw['x0'][j],device=args.device)
    y=torch.tensor(raw['queries'][j],device=args.device,dtype=torch.float32)
    args.out.mkdir(parents=True,exist_ok=False); torch.set_num_threads(4)
    model=build_model(cfg,dc['d'],dc['k']).to(args.device).eval(); model.load_state_dict(state)
    endpoints={}; results=[]; start=time.monotonic()
    for dtype_name,dtype in [('float32',torch.float32),('float64',torch.float64)]:
        model.to(dtype=dtype)
        for steps in (400,800,1600,3200):
            out=integrate(model,source.to(dtype),y.to(dtype),n_steps=steps,eps=.001).cpu().numpy().astype(np.float64)
            assert np.isfinite(out).all()
            endpoints[f'{dtype_name}_{steps}']=out
            results.append({'dtype':dtype_name,'steps':steps,'trace':float(out.var(0,ddof=1).sum()),
                'max_norm':float(np.linalg.norm(out,axis=-1).max())})
    reference=endpoints['float64_3200']; lens=np.linalg.norm(reference,axis=-1)
    selected=list(dict.fromkeys([int(lens.argmax()),int(np.argsort(lens)[-2]),int(np.argsort(lens)[len(lens)//2])]))
    model=model.cpu().double(); yy=torch.tensor(raw['queries'][j],dtype=torch.float64)[None]
    def vf(t,z):
        with torch.no_grad():
            x=torch.tensor(z,dtype=torch.float64)[None]
            return model(x,torch.tensor([t],dtype=torch.float64),yy)[0].numpy()
    adaptive=[]
    for i in selected:
        for tol in (1e-7,1e-9):
            sol=solve_ivp(vf,(0.,.999),raw['x0'][j,i].astype(np.float64),method='DOP853',rtol=tol,atol=tol*.01)
            assert sol.success and np.isfinite(sol.y).all()
            end=sol.y[:,-1]; denom=max(1.,float(np.linalg.norm(end)))
            adaptive.append({'source_index':i,'rtol':tol,'nfev':sol.nfev,'endpoint':end.tolist(),
                'relative_error_rk4_3200':float(np.linalg.norm(end-reference[i])/denom)})
    for row in results:
        a=endpoints[f'{row["dtype"]}_{row["steps"]}']
        row['mean_paired_displacement_to_float64_3200']=float(np.linalg.norm(a-reference,axis=-1).mean())
    np.savez_compressed(args.out/'raw.npz',**endpoints,source=raw['x0'][j],query=raw['queries'][j])
    (args.out/'results.json').write_text(json.dumps({'status':'completed','condition':args.target_condition,
        'run':args.runs[0],'checkpoint_sha256':sha(ck),'script_sha256':sha(__file__),
        'eps':.001,'selected_sources':selected,'fixed_step':results,'adaptive':adaptive,
        'time_embedding':'float32 as defined by the original architecture',
        'elapsed_seconds':time.monotonic()-start},indent=2,allow_nan=False))
    print(json.dumps({'fixed_step':results,'adaptive':adaptive}),flush=True)


@torch.no_grad()
def sample(model, x0, queries, steps, eps, device):
    c, m, d = x0.shape
    y = torch.tensor(queries, dtype=torch.float32, device=device).repeat_interleave(m, 0)
    out = integrate(model, x0.reshape(-1, d).to(device), y, n_steps=steps, eps=eps)
    out = out.reshape(c, m, d).cpu().numpy().astype(np.float64)
    assert np.isfinite(out).all(), 'nonfinite trajectory'
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--runs', nargs='+', default=['heff_p7y_h0_seed0'])
    ap.add_argument('--checkpoints', nargs='+', type=int, default=[200000])
    ap.add_argument('--M', type=int, default=256)
    ap.add_argument('--heldout', type=int, default=8)
    ap.add_argument('--device', default='cuda:0')
    ap.add_argument('--eps', type=float, default=.001)
    ap.add_argument('--max-seconds', type=int, default=1800)
    ap.add_argument('--controls-only', action='store_true')
    ap.add_argument('--targeted-raw', type=Path)
    ap.add_argument('--target-condition', type=int, default=50)
    args = ap.parse_args()
    if args.targeted_raw:
        targeted_solver(args); return
    assert 0 < args.eps < 1 and args.M >= 4 and args.heldout >= 1
    T = 1 - args.eps
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    manifest = {'args': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                'host': platform.node(), 'torch': torch.__version__, 'numpy': np.__version__,
                'seed': 20261016, 'eps': args.eps, 'steps': [100, 200, 400],
                'script_sha256': sha(__file__), 'status': 'running',
                'primary': 'held-out energy distance / sqrt(analytic posterior trace)',
                'solver_rule': '200-to-400 displacement < 0.1 * network-reference energy distance AND MC displacement scale',
                'inference': 'exploratory pilot; conditions nested in problem seeds; no equivalence claim',
                'calibration_sha256': sha(calibration.__file__),
                'source_hashes': {p: sha(p) for p in ['src/flows/ode_solver.py',
                    'src/models/mlp_velocity.py', 'src/problems/linear_gaussian.py',
                    'src/metrics/calibration.py', 'scripts/heff_family_test.py']}, 'runs': []}
    def write():
        (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    write()
    (args.out / 'controls.json').write_text(json.dumps(controls(), indent=2))
    print('measurement controls passed', flush=True)
    if args.controls_only:
        manifest['status'] = 'controls_passed'; write(); return
    for run_name in args.runs:
        run = Path('results/exp1') / run_name
        cfg = load_yaml(run / 'config.yaml'); dc, ev = cfg['data'], cfg['eval']
        ps = int(dc.get('problem_seed', cfg['seed']))
        assert dc.get('source_std', 1.) == 1. and cfg['train'].get('interpolant_sigma', 0.) == 0.
        problem = LinearGaussianProblem.create(dc['d'], dc['k'], dc['sigma_obs'], seed=ps,
            prior_std=dc.get('prior_std', 1.), A_kind=dc.get('A_kind', 'random'))
        Xt, Yt = problem.sample_dataset(dc['N'], seed=ps + 1)
        X, Y = Xt.numpy(), Yt.numpy()
        idx = sorted(set(torch.linspace(0, len(X)-1, ev['n_eval_train']).round().long().tolist()))
        # New independent query conditions, frozen before loading checkpoint outputs.
        _, new_y = problem.sample_dataset(args.heldout, seed=20261016 + ps)
        queries = np.concatenate([Y[idx], new_y.numpy()]); nfit = len(idx)
        assert not np.any(np.all(new_y.numpy()[:, None] == Y[None], axis=-1))
        rng = np.random.default_rng(20261016 + ps)
        x0 = torch.tensor(rng.normal(size=(len(queries), args.M, dc['d'])), dtype=torch.float32)
        model = build_model(cfg, problem.d, problem.k).to(args.device).eval()
        for iteration in args.checkpoints:
            if time.monotonic() - start > args.max_seconds:
                manifest['status'] = 'time_limit'; write(); return
            ck = run / 'checkpoints' / f'ckpt_{iteration}.pt'
            record = {'run': run_name, 'iteration': iteration, 'problem_seed': ps,
                      'checkpoint_sha256': sha(ck), 'config_sha256': sha(run/'config.yaml'),
                      'config': cfg, 'n_fit': nfit, 'n_heldout': args.heldout}
            model.load_state_dict(torch.load(ck, map_location=args.device, weights_only=False)['model_state'])
            tick = time.monotonic()
            outputs = {s: sample(model, x0, queries, s, args.eps, args.device) for s in (100, 200, 400)}
            S = outputs[400]; tr = S[:nfit].var(1, ddof=1).sum(-1)
            D = np.linalg.norm(queries[:, None] - Y[None], axis=-1)
            scale_norm = np.sqrt(problem.posterior_trace())
            families, raw = {}, {'X': X, 'Y': Y, 'queries': queries, 'x0': x0.numpy(),
                                 **{f'samples_{s}': a for s, a in outputs.items()}}
            for family in ('gauss', 'laplace', 'cauchy', 'knn'):
                grid = np.arange(1, len(X)+1) if family == 'knn' else GRID
                # Fit finite-time variance on training queries ONLY.
                fit_tr = np.stack([atomic_reference(family_weights(family, D[:nfit], s), X)[0]
                                   * T**2 + dc['d'] * args.eps**2 for s in grid])
                fit = ((np.log(np.maximum(fit_tr, 1e-30)) - np.log(tr)[None])**2).mean(1)
                gi = int(fit.argmin()); scale = float(grid[gi])
                W = family_weights(family, D, scale)
                rows = []
                # Reset reference randomness to make checkpoint comparisons reproducible.
                ref_rng = np.random.default_rng(20261017 + ps)
                for j in range(nfit, len(queries)):
                    def draw():
                        return T * X[ref_rng.choice(len(X), args.M, p=W[j])] + args.eps * ref_rng.normal(size=(args.M, dc['d']))
                    ref = draw(); nulls = []
                    for _ in range(16):
                        nulls.append(ed(draw(), draw()) / scale_norm)
                    mu = T * W[j] @ X
                    centered = X - W[j] @ X
                    cov = T**2 * (centered.T * W[j]) @ centered + args.eps**2 * np.eye(dc['d'])
                    same_moments = ref_rng.multivariate_normal(mu, cov, size=args.M)
                    E = ed(S[j], ref) / scale_norm
                    a, b = S[j, :args.M//2], S[j, args.M//2:]
                    mc = np.linalg.norm(a.mean(0)-b.mean(0)) / scale_norm
                    disp = np.linalg.norm(outputs[400][j]-outputs[200][j], axis=-1).mean()/scale_norm
                    rows.append({'condition': j-nfit, 'energy': E,
                        'null_mean': float(np.mean(nulls)), 'null_q95': float(np.quantile(nulls, .95)),
                        'excess_energy': E-float(np.mean(nulls)),
                        'same_moment_control_energy': ed(same_moments, ref)/scale_norm,
                        'paired_displacement_200_400': float(disp), 'mc_mean_scale': float(mc),
                        'solver_screen_pass': bool(disp < mc and disp < .1*E),
                        'nearest_atom_mean': float(torch.cdist(torch.tensor(S[j]), Xt).min(1).values.mean()),
                        'trace': float(S[j].var(0, ddof=1).sum())})
                    raw[f'{family}_reference_{j-nfit}'] = ref
                    raw[f'{family}_same_moment_{j-nfit}'] = same_moments
                families[family] = {'scale': scale, 'fit_grid_edge': gi in (0, len(grid)-1), 'rows': rows}
            record['families'] = families
            record['solver_displacement_100_200'] = float(np.linalg.norm(outputs[100]-outputs[200], axis=-1).mean())
            record['solver_displacement_200_400'] = float(np.linalg.norm(outputs[200]-outputs[400], axis=-1).mean())
            # Hard-label risk: compare exact teacher field on teacher vs learned paths.
            if float(cfg['train'].get('y_noise_h', 0.)) == 0.:
                risk = []
                tx0 = x0[:nfit].reshape(-1, problem.d).to(args.device)
                ta = torch.tensor(X[idx], dtype=torch.float32, device=args.device).repeat_interleave(args.M, 0)
                ty = torch.tensor(Y[idx], dtype=torch.float32, device=args.device).repeat_interleave(args.M, 0)
                for t in (.25, .5, .75, .9, .95, .99, .999):
                    eps = 1-t; tt = torch.full((len(tx0),), t, device=args.device)
                    with torch.no_grad():
                        teacher = t*ta + eps*tx0
                        learned = integrate(model, tx0, ty, n_steps=400, eps=eps)
                        r = float(((model(teacher, tt, ty) - (ta-teacher)/eps)**2).sum(-1).mean())
                        m = float(((model(learned, tt, ty) - (ta-learned)/eps)**2).sum(-1).mean())
                    risk.append({'t': t, 'teacher_error_r': r, 'rollout_error_m': m, 'ratio': m/max(r, 1e-30)})
                record['hard_label_risk'] = risk
            assert all(np.isfinite(a).all() for a in raw.values())
            stem = f'{run_name}_{iteration}'
            np.savez_compressed(args.out / f'{stem}.npz', **raw)
            record['elapsed_seconds'] = time.monotonic()-tick
            (args.out / f'{stem}.json').write_text(json.dumps(record, indent=2, allow_nan=False))
            manifest['runs'].append({'run': run_name, 'iteration': iteration, 'file': f'{stem}.json'})
            write(); print(f'{stem}: {record["elapsed_seconds"]:.1f}s; solver displacement {record["solver_displacement_200_400"]:.3g}', flush=True)
    manifest['status'] = 'completed'; manifest['elapsed_seconds'] = time.monotonic()-start; write()


if __name__ == '__main__':
    main()
