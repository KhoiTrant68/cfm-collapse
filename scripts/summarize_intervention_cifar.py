"""Recompute pilot metrics from raw outputs and write a seed-level report/figures."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path('results/intervention_cifar_pilot_20261016'))
    ap.add_argument('--oracle-only', action='store_true')
    ap.add_argument('--server-audit', type=Path)
    args = ap.parse_args(); root = args.root
    oracle = json.loads((root/'oracle_five_seeds/results.json').read_text())
    raw = np.load(root/'oracle_five_seeds/raw.npz'); verified_oracle = 0
    for row in oracle['rows']:
        seed, arm, eps = row['seed'], row['arm'], row['eps']
        j = (1e-2, 1e-4, 1e-6).index(eps); atoms = raw[f'{seed}_atoms']
        if 'paired_solver_displacement' in row:
            samples = raw[f'{seed}_{arm}_fine'][j]
            coarse = raw[f'{seed}_{arm}_coarse'][j]
            assert np.isclose(np.linalg.norm(samples-coarse, axis=-1).mean(), row['paired_solver_displacement'], atol=1e-14)
        else:
            rho = float(arm.split('rho')[1]); samples = raw[f'{seed}_target_noise_rho{rho}'][j]
        dist = np.sqrt(((samples[:, None]-atoms[None])**2).sum(-1))
        assert np.isclose(dist.min(1).mean(), row['mean_nearest_atom_distance'], atol=1e-14)
        assert np.isclose(samples.var(0, ddof=1).sum(), row['trace'])
        verified_oracle += 1
    matched = json.loads((root/'oracle_five_seeds/matched_loss.json').read_text())
    for r in matched:
        delta = r['delta']; A = np.log(1/delta)
        loss = delta*(1+1.5*A+7/6*A*A)
        assert np.isclose(loss, r['teacher_loss_per_d'])
        assert np.isclose(1/(3*r['L']), loss)
        assert np.isclose(np.exp(-2)/r['L']**2, r['lipschitz_endpoint_variance_per_d'])
    lines = ['# Oracle interventions and CIFAR pilot', '',
        'Existing checkpoints only; no retraining. Numerical illustrations and feasibility pilots do not establish novelty or venue readiness.', '',
        '## Oracle interventions', '',
        'Five new geometry seeds, five atoms in R^2, scalar labels, 128 shared Gaussian source samples per seed; paired log-time RK4 at 768/1536 steps.', '',
        '| intervention | mean nearest-atom distance at eps=1e-6: range over seeds |',
        '|---|---|']
    arms = list(dict.fromkeys(r['arm'] for r in oracle['rows']))
    for arm in arms:
        vals = [r['mean_nearest_atom_distance'] for r in oracle['rows'] if r['arm']==arm and r['eps']==1e-6]
        lines.append(f'| {arm} | {min(vals):.6g} – {max(vals):.6g} |')
    lines += ['', 'The target-noise controls are exact finite-time law draws, not numerically integrated guided fields. Field averaging is the equal average of three fields, not averaging label priors. The symmetric source at the midpoint remains an exceptional non-atom trajectory; nearby sources move to atoms. Frequencies from 128 sources do not identify exact guided endpoint probabilities.', '',
        '## Exact matched teacher loss', '',
        '| delta | teacher loss / d (both fields) | counterexample endpoint variance / d | Lipschitz-attainer endpoint variance / d |',
        '|---|---|---|---|']
    for r in matched:
        lines.append(f"| {r['delta']} | {r['teacher_loss_per_d']:.7g} | {r['counterexample_endpoint_variance_per_d']:.7g} | {r['lipschitz_endpoint_variance_per_d']:.7g} |")
    lines += ['', 'These are exact constructed fields with the same teacher loss. Their Lipschitz constants are not held equal. This is not evidence that the trained architectures realize the counterexample. Segmentwise quadrature was independently checked against its analytic loss.', '']
    summary = []; verified_cifar = 0; pair_refs = {}
    audit = None
    if args.server_audit:
        audit = json.loads(args.server_audit.read_text())
        assert audit['status'] == 'passed' and audit['rows_checked'] == 192
        assert len(audit['artifacts']) == 6
    if not args.oracle_only:
        for dirname in ('cifar_hard_three_seeds', 'cifar_smoothed_three_seeds'):
            folder = root/dirname; man = json.loads((folder/'manifest.json').read_text())
            assert man['status'] == 'completed' and len(man['completed']) == 3
            assert man['M'] == 32 and man['n_test'] == 8
            for run in man['completed']:
                rec = json.loads((folder/f'{run}.json').read_text())
                seed = rec['config']['seed']; h = rec['config']['train']['y_noise_h']
                assert rec['parameter_count'] == 35750915
                if audit:
                    a = next(a for a in audit['artifacts'] if a['run']==run)
                    assert hashlib.sha256((folder/f'{run}.json').read_bytes()).hexdigest() == a['result_sha256']
                    if seed in pair_refs:
                        assert pair_refs[seed] == a['input_array_hashes']
                    pair_refs[seed] = a['input_array_hashes']
                    verified_cifar += len(rec['rows'])
                else:
                    arr = np.load(folder/f'{run}.npz')
                    hidden = arr['hidden_mask']; truth = arr['truth'].reshape(8, -1)
                    if seed in pair_refs:
                        previous = pair_refs[seed]
                        assert np.array_equal(arr['truth'], previous['truth'])
                        for j in range(8):
                            assert np.array_equal(arr[f'x0_{j}'], previous[f'x0_{j}'])
                            assert np.array_equal(arr[f'condition_{j}'], previous[f'condition_{j}'])
                        assert np.array_equal(arr['training_images'], previous['training_images'])
                    else:
                        pair_refs[seed] = {k: arr[k] for k in ['truth', 'training_images']+
                            [f'x0_{j}' for j in range(8)]+[f'condition_{j}' for j in range(8)]}
                    for row in rec['rows']:
                        j, steps = row['image'], row['steps']
                        samples = arr[f'samples_{j}_{steps}'].reshape(32, -1).astype(np.float64)
                        sh, th = samples[:, hidden], truth[j, hidden]
                        ties = (sh==th).sum(0); below = (sh < th).sum(0)
                        rng = np.random.default_rng(20261018+j)
                        u = (below+rng.integers(0, ties+1)+.5)/33
                        coverage = float((np.abs(u-.5) <= .45+1e-12).mean())
                        assert abs(coverage-row['pixel_coverage'][8]) < 1e-12
                        assert np.isclose(sh.var(0, ddof=1).sum(), row['hidden_trace'])
                        assert np.isclose(((sh.mean(0)-th)**2).mean(), row['hidden_mean_mse'])
                        finest = arr[f'samples_{j}_400'].reshape(32, -1).astype(np.float64)
                        assert np.isclose(np.sqrt(((samples-finest)**2).mean()), row['paired_rms_to_finest'], atol=1e-12)
                        verified_cifar += 1
                for steps in (50, 100, 200, 400):
                    rows = [r for r in rec['rows'] if r['steps']==steps]
                    summary.append({'run': run, 'h': h, 'seed': seed, 'steps': steps,
                        'pixel_cov90': float(np.mean([r['pixel_coverage'][8] for r in rows])),
                        'pc_cov90': float(np.mean([r['pc_coverage'][8] for r in rows])),
                        'joint8_cov90': float(np.mean([r['joint_rank']['8'] <= .9+1e-12 for r in rows])),
                        'joint32_cov90': float(np.mean([r['joint_rank']['32'] <= .9+1e-12 for r in rows])),
                        'hidden_trace': float(np.mean([r['hidden_trace'] for r in rows])),
                        'hidden_mean_mse': float(np.mean([r['hidden_mean_mse'] for r in rows])),
                        'observed_mean_mse': float(np.mean([r['observed_mean_mse'] for r in rows])),
                        'rms_to_400': float(np.mean([r['paired_rms_to_finest'] for r in rows])),
                        'nearest_train_mse': float(np.mean([r['nearest_train_mse'] for r in rows]))})
        lines += ['## CIFAR solver/calibration pilot', '',
            'Six exact DDPM checkpoints (35,750,915 parameters), h=0,4 × seeds 0,1,2 at 60k. Eight identical held-out test images and M=32 identical source draws across models/solvers. Four Euler resolutions, epsilon=.001, no clipping.', '',
            '| h | seed | steps | pixel 90% coverage | joint8 coverage | joint32 coverage | hidden trace | hidden mean MSE | paired RMS to 400 |',
            '|---|---|---|---|---|---|---|---|---|']
        for r in sorted(summary, key=lambda r: (r['h'], r['seed'], r['steps'])):
            lines.append(f"| {r['h']} | {r['seed']} | {r['steps']} | {r['pixel_cov90']:.4f} | {r['joint8_cov90']:.3f} | {r['joint32_cov90']:.3f} | {r['hidden_trace']:.5g} | {r['hidden_mean_mse']:.5g} | {r['rms_to_400']:.5g} |")
        lines += ['', 'Finite-M reference coverage at nominal 90%: '+str(rec['reference_central'][8])+
            ' for central ranks and '+str(rec['reference_upper'][8])+' for upper ranks.', '',
            'Eight images are the evaluation units; pixels and PCA coordinates are not independent replicates. The same images across seeds make this a paired pilot, not 48 independent test images. Joint coverage has resolution 1/8. There is no formal significance claim or full posterior-quality certificate. A 400-step output is a comparison reference, not a proven exact endpoint. Nearest-training-image MSE is not exact membership.', '']
    lines += [f'Independent raw checks: {verified_oracle} oracle rows, four matched-loss constructions, {verified_cifar} CIFAR image/solver rows.']
    if audit:
        lines += ['', 'CIFAR raw recomputation ran on the server. This local summary verifies result-file hashes and cross-h input-array hashes against that audit. Full raw samples remain on the server; local downloads may be incomplete.']
    (root/'SUMMARY.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (root/'summary.json').write_text(json.dumps({'oracle_checks': verified_oracle,
        'cifar_checks': verified_cifar, 'cifar': summary}, indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), constrained_layout=True)
    for arm in ('hard_cfg_w12', 'label_smoothed_cfg_w12', 'average_three_label_fields', 'exact_target_noise_rho0.15'):
        vals = [[r['mean_nearest_atom_distance'] for r in oracle['rows'] if r['arm']==arm and r['eps']==e] for e in (1e-2, 1e-4, 1e-6)]
        med = np.median(vals, axis=1)
        axes[0].loglog([1e-2, 1e-4, 1e-6], med, 'o-', label=arm.replace('_', ' '))
    axes[0].invert_xaxis(); axes[0].set_xlabel('1 - t')
    axes[0].set_ylabel('Mean distance to nearest atom'); axes[0].legend(fontsize=6)
    loss = [r['teacher_loss_per_d'] for r in matched]
    axes[1].loglog(loss, [r['counterexample_endpoint_variance_per_d'] for r in matched], 'o-', label='Amplifying field')
    axes[1].loglog(loss, [r['lipschitz_endpoint_variance_per_d'] for r in matched], 'o-', label='Lipschitz attainer')
    axes[1].set_xlabel('Teacher loss / d (matched)'); axes[1].set_ylabel('Endpoint variance / d')
    axes[1].legend(fontsize=8)
    fig.savefig(root/'oracle_matched_loss.png', dpi=180); fig.savefig(root/'oracle_matched_loss.pdf'); plt.close(fig)
    if summary:
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.5), constrained_layout=True)
        for h, color in ((0, 'tab:blue'), (4, 'tab:orange')):
            for seed in range(3):
                rr = sorted([r for r in summary if r['h']==h and r['seed']==seed], key=lambda r:r['steps'])
                for ax, key in zip(axes, ('pixel_cov90', 'hidden_trace', 'rms_to_400')):
                    ax.plot([r['steps'] for r in rr], [r[key] for r in rr], 'o-', color=color,
                        alpha=.65, label=f'h={h}' if seed==0 else None)
        axes[0].axhline(rec['reference_central'][8], ls='--', color='black', lw=1, label='Calibrated reference')
        axes[0].set_ylabel('Pixel 90% rank coverage'); axes[0].legend(fontsize=8)
        axes[1].set_ylabel('Hidden-region covariance trace')
        axes[2].set_ylabel('Paired RMS distance to 400 steps')
        for ax in axes:
            ax.set_xlabel('Euler steps'); ax.set_xscale('log', base=2)
            ax.set_xticks([50, 100, 200, 400], ['50','100','200','400'])
        fig.savefig(root/'cifar_solver.png', dpi=180); fig.savefig(root/'cifar_solver.pdf'); plt.close(fig)
    print(json.dumps({'oracle_rows': verified_oracle, 'cifar_rows': verified_cifar}))


if __name__ == '__main__':
    main()
