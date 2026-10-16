"""Paired Euler-resolution pilot on archived CIFAR DDPM checkpoints; no training.

Calibrated ranks randomize exact ties. Conditions, source draws and evaluation
images are held fixed across resolutions. Raw unclipped outputs are preserved.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path
import numpy as np
import torch
from scripts.calib_image_checkpoints import build_model, test_images
from src.problems.inpainting import InpaintingProblem
from src.utils import load_yaml


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@torch.no_grad()
def euler(model, source, condition, steps, eps):
    x = source.clone(); dt = (1-eps)/steps
    cond = condition.to(x.device).expand(len(x), -1, -1, -1)
    for i in range(steps):
        t = torch.full((len(x),), i*dt, device=x.device)
        x += dt*model(x, t, cond)
    assert torch.isfinite(x).all(), 'nonfinite endpoint'
    return x


def selftest():
    x = torch.arange(8, dtype=torch.float32).reshape(2, 1, 2, 2)/8
    a = torch.ones_like(x)*.3
    def oracle(z, t, cond):
        return (a-z)/(1-t[:, None, None, None])
    for steps in (50, 100, 200, 400):
        got = euler(oracle, x, torch.zeros(1, 1, 2, 2), steps, .001)
        assert (got-(.999*a+.001*x)).abs().max() < 2e-5


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--runs', nargs='+', default=['exp3_cifar_heff_h0_s0'])
    ap.add_argument('--M', type=int, default=16)
    ap.add_argument('--n-test', type=int, default=2)
    ap.add_argument('--steps', nargs='+', type=int, default=[50, 100, 200, 400])
    ap.add_argument('--checkpoint', type=int, default=60000)
    ap.add_argument('--device', default='cuda:0')
    ap.add_argument('--calibration-path', type=Path, default=Path('src/metrics/calibration.py'))
    ap.add_argument('--max-seconds', type=int, default=1800)
    ap.add_argument('--selftest-only', action='store_true')
    args = ap.parse_args(); selftest()
    if args.selftest_only:
        print('Euler oracle checks passed'); return
    assert args.M >= 4 and args.n_test >= 1 and len(set(args.steps)) == len(args.steps)
    args.out.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('calibration_snapshot', args.calibration_path)
    cal = importlib.util.module_from_spec(spec); spec.loader.exec_module(cal)
    assert 'rng' in __import__('inspect').signature(cal.marginal_pit).parameters
    torch.set_num_threads(4); torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    start = time.monotonic(); completed = []
    manifest = {'status': 'running', 'script_sha256': sha(__file__),
        'calibration_sha256': sha(args.calibration_path), 'M': args.M, 'n_test': args.n_test,
        'steps': args.steps, 'eps': .001, 'torch': torch.__version__, 'seed': 20261017,
        'source_hashes': {p: sha(p) for p in ['src/models/unet.py', 'src/problems/inpainting.py',
                            'scripts/calib_image_checkpoints.py']},
        'warning': 'Feasibility pilot; held-out images, not pixels, are statistical units; NN distance is not exact membership.'}
    def write():
        manifest['completed'] = completed
        (args.out/'manifest.json').write_text(json.dumps(manifest, indent=2))
    write()
    cache = {}
    for run_name in args.runs:
        root = Path('results/exp3')/run_name; cfg = load_yaml(root/'config.yaml'); dc = cfg['data']
        assert dc.get('dataset') == 'cifar10' and dc.get('cond_kind', 'inpaint') == 'inpaint'
        assert cfg['model'].get('arch', 'ddpm') == 'ddpm'
        seed = cfg.get('problem_seed', cfg['seed']); tick = time.monotonic()
        key = (seed, dc['N'], dc.get('mask_kind', 'bottom_half'), dc.get('data_root', 'data'))
        if key not in cache:
            problem = InpaintingProblem.create(dc['N'], seed=seed, data_root=key[3],
                mask_kind=key[2], dataset='cifar10')
            test = test_images('cifar10', key[3], args.n_test, seed=20261017)
            hidden = (1-problem.mask_obs).bool().expand(3, -1, -1).flatten().numpy()
            train = problem.X.flatten(1).numpy().astype(np.float64)
            mu, V, explained = cal.pca_basis(train[:, hidden], 32)
            cache[key] = problem, test, hidden, train, mu, V, explained
        problem, test, hidden, train, mu, V, explained = cache[key]
        model = build_model(cfg, 3, args.device).eval()
        ck = root/'checkpoints'/f'ckpt_{args.checkpoint}.pt'
        model.load_state_dict(torch.load(ck, map_location=args.device, weights_only=False)['model_state'])
        nparam = sum(p.numel() for p in model.parameters())
        assert nparam > 30_000_000, 'unexpected substitute architecture'
        raw = {'truth': test.numpy(), 'pca_mean': mu, 'pca_basis': V,
               'pca_explained': explained, 'hidden_mask': hidden, 'training_images': problem.X.numpy()}
        rows = []
        for j in range(args.n_test):
            if time.monotonic()-start > args.max_seconds:
                raise TimeoutError('CIFAR pilot budget exhausted')
            source = dc.get('source_std', 1.)*torch.randn(args.M, 3, 32, 32,
                generator=torch.Generator().manual_seed(20261017+j))
            cond = problem.condition(test[j:j+1]); raw[f'x0_{j}'] = source.numpy()
            raw[f'condition_{j}'] = cond.numpy(); outputs = {}
            for steps in sorted(args.steps):
                s = euler(model, source.to(args.device), cond, steps, .001).cpu().numpy()
                raw[f'samples_{j}_{steps}'] = s; outputs[steps] = s
                sf = s.reshape(args.M, -1).astype(np.float64); sh = sf[:, hidden]
                truth = test[j].flatten().numpy().astype(np.float64); th = truth[hidden]
                # Reset tie RNG by image for pairing across solvers/models.
                rng = np.random.default_rng(20261018+j)
                u = cal.marginal_pit(sh, th, rng=rng)
                zs, zt = (sh-mu)@V.T, (th-mu)@V.T
                upc = cal.marginal_pit(zs, zt, rng=rng)
                joint = {str(k): cal.joint_pit(zs[:, :k], zt[:k], rng=rng) for k in (8, 32)}
                nearest = np.full(args.M, np.inf)
                for chunk in np.array_split(train, 16):
                    dd = ((sf[:, None]-chunk[None])**2).mean(-1)
                    nearest = np.minimum(nearest, dd.min(1))
                rows.append({'image': j, 'steps': steps,
                    'pixel_coverage': cal.central_coverage(u).tolist(),
                    'pc_coverage': cal.central_coverage(upc).tolist(), 'joint_rank': joint,
                    'hidden_trace': float(sh.var(0, ddof=1).sum()),
                    'hidden_mean_mse': float(((sh.mean(0)-th)**2).mean()),
                    'observed_mean_mse': float(((sf.mean(0)[~hidden]-truth[~hidden])**2).mean()),
                    'nearest_train_mse': float(nearest.mean()),
                    'exact_pixel_tie_fraction': float((sh==th).mean())})
            fine = outputs[max(args.steps)]
            for row in rows:
                if row['image'] == j:
                    row['paired_rms_to_finest'] = float(np.sqrt(((outputs[row['steps']]-fine).astype(np.float64)**2).mean()))
            print(f'{run_name}: image {j+1}/{args.n_test}, elapsed {time.monotonic()-tick:.1f}s', flush=True)
        np.savez_compressed(args.out/f'{run_name}.npz', **raw)
        record = {'run': run_name, 'config': cfg, 'config_sha256': sha(root/'config.yaml'),
            'checkpoint_sha256': sha(ck), 'parameter_count': nparam, 'rows': rows,
            'reference_central': cal.reference_central(args.M).tolist(),
            'reference_upper': cal.reference_upper(args.M).tolist(),
            'elapsed_seconds': time.monotonic()-tick}
        (args.out/f'{run_name}.json').write_text(json.dumps(record, indent=2, allow_nan=False))
        completed.append(run_name); write(); del model
    manifest['status'] = 'completed'; manifest['elapsed_seconds'] = time.monotonic()-start; write()


if __name__ == '__main__':
    main()
