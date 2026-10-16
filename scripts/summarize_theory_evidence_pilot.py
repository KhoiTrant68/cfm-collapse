"""Independently recompute saved pilot energy distances and summarize by problem seed."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def distance(a, b):
    return np.sqrt(np.maximum(((a[:, None] - b[None])**2).sum(-1), 0))


def energy(a, b):
    return 2*distance(a, b).mean() - distance(a, a).mean() - distance(b, b).mean()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path('results/theory_evidence_20261016'))
    args = ap.parse_args(); root = args.root
    main_dir = root/'six_checkpoint_pilot'
    manifest = json.loads((main_dir/'manifest.json').read_text())
    assert manifest['status'] == 'completed' and len(manifest['runs']) == 6
    data, summary, checked = [], [], 0
    for entry in manifest['runs']:
        path = main_dir/entry['file']; rec = json.loads(path.read_text()); data.append(rec)
        raw = np.load(path.with_suffix('.npz'))
        from src.problems.linear_gaussian import LinearGaussianProblem
        cfg = rec['config']; dc = cfg['data']; ps = rec['problem_seed']
        problem = LinearGaussianProblem.create(dc['d'], dc['k'], dc['sigma_obs'], seed=ps,
            prior_std=dc.get('prior_std', 1.), A_kind=dc.get('A_kind', 'random'))
        norm = np.sqrt(problem.posterior_trace())
        assert raw['samples_400'].shape == (28, 256, dc['d'])
        from scripts.heff_family_test import GRID, atomic_reference, knn_weights, weights
        D = np.linalg.norm(raw['queries'][:20, None]-raw['Y'][None], axis=-1)
        for family, fit in rec['families'].items():
            grid = np.arange(1, len(raw['X'])+1) if family == 'knn' else GRID
            refs = []
            for s in grid:
                W = knn_weights(D, int(s)) if family == 'knn' else weights(family, D, float(s))
                refs.append(.999**2 * atomic_reference(W, raw['X'])[0]+dc['d']*.001**2)
            observed = raw['samples_400'][:20].var(1, ddof=1).sum(-1)
            loss = ((np.log(np.maximum(refs, 1e-30))-np.log(observed))**2).mean(1)
            assert np.isclose(grid[int(loss.argmin())], fit['scale'])
            for row in fit['rows']:
                j = row['condition']
                got = energy(raw['samples_400'][20+j], raw[f'{family}_reference_{j}'])/norm
                assert abs(got-row['energy']) < 1e-10, (path, family, j, got)
                control = energy(raw[f'{family}_same_moment_{j}'], raw[f'{family}_reference_{j}'])/norm
                assert abs(control-row['same_moment_control_energy']) < 1e-10
                checked += 1
        rows = rec['families']['gauss']['rows']
        summary.append({'run': rec['run'], 'h': cfg['train']['y_noise_h'], 'seed': ps,
            'effective_bandwidth': rec['families']['gauss']['scale'],
            'mean_energy': float(np.mean([r['energy'] for r in rows])),
            'mean_null': float(np.mean([r['null_mean'] for r in rows])),
            'mean_excess_energy': float(np.mean([r['excess_energy'] for r in rows])),
            'above_null_q95': sum(r['energy'] > r['null_q95'] for r in rows),
            'solver_screen_pass': sum(r['solver_screen_pass'] for r in rows),
            'displacement_200_400': rec['solver_displacement_200_400']})
    eps_dir = root/'eps_0001'; terminal = []
    if (eps_dir/'manifest.json').exists():
        em = json.loads((eps_dir/'manifest.json').read_text()); assert em['status'] == 'completed'
        for rec in data:
            name = f'{rec["run"]}_200000'
            a = np.load(main_dir/f'{name}.npz'); b = np.load(eps_dir/f'{name}.npz')
            assert np.array_equal(a['x0'], b['x0']) and np.array_equal(a['queries'], b['queries'])
            er = json.loads((eps_dir/f'{name}.json').read_text())
            terminal.append({'run': rec['run'], 'mean_displacement': float(
                np.linalg.norm(a['samples_400']-b['samples_400'], axis=-1).mean()),
                'mean_nearest_atom_distance_eps_001': float(np.mean([r['nearest_atom_mean'] for r in rec['families']['gauss']['rows']])),
                'mean_nearest_atom_distance_eps_0001': float(np.mean([r['nearest_atom_mean'] for r in er['families']['gauss']['rows']])),
                'solver_screen_pass_eps_0001': sum(r['solver_screen_pass'] for r in er['families']['gauss']['rows'])})
    earlier = root/'earlier_hard_checkpoints'; risk_records = [r for r in data if 'hard_label_risk' in r]
    if (earlier/'manifest.json').exists():
        early_manifest = json.loads((earlier/'manifest.json').read_text())
        assert early_manifest['status'] == 'completed' and len(early_manifest['runs']) == 6
        risk_records += [json.loads((earlier/e['file']).read_text()) for e in early_manifest['runs']]
    risk = [{'run': r['run'], 'iteration': r['iteration'], 'profile': r['hard_label_risk']} for r in risk_records]
    result = {'independent_energy_recomputations': checked, 'main': summary, 'terminal': terminal,
              'risk': risk, 'warning': 'Exploratory, three reused problem seeds; 16 null pairs per condition. No formal familywise test or equivalence certificate.'}
    (root/'summary.json').write_text(json.dumps(result, indent=2))
    lines = ['# Synthetic server pilot — 2026-10-16', '',
        'Feasibility pilot on existing checkpoints; no training. Results are grouped by problem seed.', '',
        '| training h | seed | fitted h_eff | mean energy | mean reference null | above diagnostic q95 | solver pass |',
        '|---|---|---|---|---|---|---|']
    for r in sorted(summary, key=lambda x: (x['h'], x['seed'])):
        lines.append(f"| {r['h']} | {r['seed']} | {r['effective_bandwidth']:.5f} | {r['mean_energy']:.5f} | {r['mean_null']:.5f} | {r['above_null_q95']}/8 | {r['solver_screen_pass']}/8 |")
    lines += ['', f'Independent NumPy checks: {checked} energy distances and {checked} same-moment control distances matched saved records; all 24 family scale fits reproduced.', '',
        'Energy is normalized by the square root of analytic posterior trace. Reference mixtures use the same finite terminal time. Bandwidth fits use only 20 training queries; eight new queries evaluate the law. Gaussian moment matching is a descriptive fit, not a proof of distributional equality.', '',
        'The q95 envelope uses only 16 independent reference pairs per condition and is diagnostic, not a calibrated multiple-testing decision. Eight conditions are nested within each of three reused problem seeds; checkpoints are not independent replicates. Two queries from seed 0 also appeared in the smoke, with no subsequent selection or tuning.', '',
        'The solver screen compares paired displacement with a mean-based Monte Carlo proxy and one tenth of energy discrepancy. It is a practical screen, not a numerical-error certificate for every statistic.']
    if terminal:
        lines += ['', '## Terminal-time sensitivity', '',
                  '| run | paired displacement eps .001 to .0001 | nearest atom (.001) | nearest atom (.0001) | solver pass (.0001) |',
                  '|---|---|---|---|---|']
        for r in terminal:
            lines.append(f"| {r['run']} | {r['mean_displacement']:.6g} | {r['mean_nearest_atom_distance_eps_001']:.6g} | {r['mean_nearest_atom_distance_eps_0001']:.6g} | {r['solver_screen_pass_eps_0001']}/8 |")
    lines += ['', '## Teacher versus learned-path error', '',
              'Hard-label diagnostics evaluate the exact field (a-x)/(1-t) at the same seven times, on teacher and learned paths, averaged over 20 training queries. They do not estimate uniform-time global training loss or establish a global density/risk-transfer bound.', '',
              '| checkpoint | seed | teacher error t=.999 | learned-path error t=.999 | ratio |',
              '|---|---|---|---|---|']
    for r in sorted(risk_records, key=lambda r: (r['iteration'], r['problem_seed'])):
        p = r['hard_label_risk'][-1]
        lines.append(f"| {r['iteration']} | {r['problem_seed']} | {p['teacher_error_r']:.5g} | {p['rollout_error_m']:.5g} | {p['ratio']:.5g} |")
    (root/'SUMMARY.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)
    ordered = sorted(summary, key=lambda x: (x['h'], x['seed'])); xx = np.arange(len(ordered))
    axes[0].bar(xx-.17, [r['mean_energy'] for r in ordered], width=.34, label='Model vs reference')
    axes[0].bar(xx+.17, [r['mean_null'] for r in ordered], width=.34, label='Reference vs reference')
    axes[0].set_xticks(xx, [f"h={r['h']}\ns={r['seed']}" for r in ordered], fontsize=8)
    axes[0].set_ylabel('Normalized energy distance'); axes[0].legend(fontsize=8)
    for it in sorted(set(r['iteration'] for r in risk_records)):
        group = [r['hard_label_risk'] for r in risk_records if r['iteration']==it]
        eps = np.array([1-p['t'] for p in group[0]])
        rat = np.array([[p['ratio'] for p in g] for g in group])
        axes[1].plot(eps, np.median(rat, axis=0), label=f'{it//1000}k')
        axes[1].fill_between(eps, rat.min(0), rat.max(0), alpha=.12)
    axes[1].set_xscale('log'); axes[1].set_yscale('log'); axes[1].invert_xaxis()
    axes[1].set_xlabel('1 - t'); axes[1].set_ylabel('Learned-path / teacher error')
    axes[1].legend(title='Checkpoint', fontsize=8)
    axes[2].bar(xx, [r['displacement_200_400'] for r in ordered])
    axes[2].set_xticks(xx, [f"h={r['h']}\ns={r['seed']}" for r in ordered], fontsize=8)
    axes[2].set_yscale('log'); axes[2].set_ylabel('Paired displacement: 200 to 400 steps')
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    fig.savefig(root/'pilot_summary.png', dpi=180)
    fig.savefig(root/'pilot_summary.pdf')
    plt.close(fig)
    print(json.dumps({'verified_distances': checked*2, 'main_runs': len(summary),
                      'risk_profiles': len(risk_records), 'terminal_runs': len(terminal)}))


if __name__ == '__main__':
    main()
