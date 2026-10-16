"""Aggregate the frozen ten-run comparison; retain all seeds and unresolved rows."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np


def direct_energy(a, b):
    def dist(x, y):
        return np.sqrt(((x[:, None]-y[None])**2).sum(-1))
    return float(2*dist(a, b).mean()-dist(a, a).mean()-dist(b, b).mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path('results/independent_seeds_20261016'))
    ap.add_argument('--verify-raw', action='store_true')
    args = ap.parse_args(); root = args.root
    from src.problems.linear_gaussian import LinearGaussianProblem
    from scripts.heff_family_test import GRID, atomic_reference, weights
    all_records, seeds, families, failed, histories, provenance = [], [], [], [], [], []
    checks = 0; discrepancies = []; pair_inputs = {}; outlier = None
    dirs = sorted(root.glob('eval_*')); assert len(dirs) == 10
    for folder in dirs:
        manifest = json.loads((folder/'manifest.json').read_text())
        assert manifest['status']=='completed' and len(manifest['runs'])==1
        assert json.loads((folder/'controls.json').read_text())['passed'] is True
        assert manifest['args']['M']==512 and manifest['args']['heldout']==64
        entry = manifest['runs'][0]; path = folder/entry['file']; r = json.loads(path.read_text())
        assert r['iteration']==200000 and r['n_fit']==20 and r['n_heldout']==64
        cfg = r['config']; h = float(cfg['train']['y_noise_h']); seed = r['problem_seed']
        assert seed in range(1001,1006) and h in (0., .1)
        assert cfg['train']['max_iters']==200000 and cfg['train']['batch_size']==256
        assert cfg['train']['lr']==.001 and cfg['model']['width']==128 and cfg['model']['depth']==4
        all_records.append(r)
        provenance.append({'run':r['run'], 'result_file':str(path.relative_to(root)),
            'result_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'checkpoint_sha256':r['checkpoint_sha256'], 'config_sha256':r['config_sha256'],
            'eval_script_sha256':manifest['script_sha256']})
        for family, fit in r['families'].items():
            rr = fit['rows']; assert len(rr)==64 and [x['condition'] for x in rr]==list(range(64))
            assert all(np.isfinite(x['energy']) and np.isfinite(x['null_mean']) for x in rr)
            families.append({'run':r['run'], 'h':h, 'seed':seed, 'family':family,
                'scale':fit['scale'], 'grid_edge':fit['fit_grid_edge'],
                'mean_energy':float(np.mean([x['energy'] for x in rr])),
                'mean_excess_energy':float(np.mean([x['excess_energy'] for x in rr]))})
        rows = r['families']['gauss']['rows']
        for x in rows:
            assert np.isclose(x['energy']-x['null_mean'], x['excess_energy'])
            if not x['solver_screen_pass']:
                failed.append({'run':r['run'], 'h':h, 'seed':seed, **x})
        energies = np.array([x['energy'] for x in rows]); excess = np.array([x['excess_energy'] for x in rows])
        seeds.append({'run':r['run'], 'h':h, 'seed':seed,
            'h_eff':r['families']['gauss']['scale'], 'mean_energy':float(energies.mean()),
            'median_condition_energy':float(np.median(energies)),
            'mean_null':float(np.mean([x['null_mean'] for x in rows])),
            'mean_excess_energy':float(excess.mean()),
            'above_diagnostic_q95':sum(x['energy']>x['null_q95'] for x in rows),
            'solver_pass':sum(x['solver_screen_pass'] for x in rows),
            'median_paired_displacement':float(np.median([x['paired_displacement_200_400'] for x in rows])),
            'max_paired_displacement':float(max(x['paired_displacement_200_400'] for x in rows)),
            'risk_ratio_t999':r.get('hard_label_risk',[{}])[-1].get('ratio')})
        # Same-checkpoint training proxies, kept separate from held-out full-law metrics.
        log = (root/'logs'/f'{r["run"]}.log').read_text()
        for line in log.splitlines():
            if line.lstrip().startswith('iter=') and '[  train]' in line:
                import re
                m = re.search(r'iter=\s*(\d+).*trace_cov=([\deE+.-]+).*loss=([\deE+.-]+)',line)
                if m:
                    histories.append({'run':r['run'],'h':h,'seed':seed,'iteration':int(m[1]),
                                      'train_query_trace':float(m[2]),'loss_ema':float(m[3])})
        if args.verify_raw:
            raw = np.load(path.with_suffix('.npz')); dc=cfg['data']
            assert raw['samples_400'].shape==(84,512,2) and np.isfinite(raw['samples_400']).all()
            inputs = {k: hashlib.sha256(raw[k].tobytes()).hexdigest() for k in ('X','Y','queries','x0')}
            if seed in pair_inputs:
                assert pair_inputs[seed]==inputs
            pair_inputs[seed]=inputs
            problem=LinearGaussianProblem.create(dc['d'],dc['k'],dc['sigma_obs'],seed=seed,
                    prior_std=dc.get('prior_std',1.),A_kind=dc.get('A_kind','random'))
            norm=np.sqrt(problem.posterior_trace())
            D=np.linalg.norm(raw['queries'][:20,None]-raw['Y'][None],axis=-1)
            refs=np.stack([atomic_reference(weights('gauss',D,float(s)),raw['X'])[0]*.999**2+2e-6 for s in GRID])
            observed=raw['samples_400'][:20].var(1,ddof=1).sum(-1)
            fit=((np.log(np.maximum(refs,1e-30))-np.log(observed))**2).mean(1)
            assert np.isclose(GRID[fit.argmin()],r['families']['gauss']['scale'])
            for x in rows:
                j=x['condition']; a=raw['samples_400'][20+j]; b=raw[f'gauss_reference_{j}']
                computed=direct_energy(a,b)/norm
                control=direct_energy(raw[f'gauss_same_moment_{j}'],b)/norm
                discrepancies.append({'run':r['run'],'condition':j,'recorded_energy':x['energy'],
                    'direct_energy':computed,'difference':computed-x['energy']})
                # Large, cancelling terms in exploding trajectories can expose
                # the distance implementation's conditioning; retain that difference.
                assert abs(computed-x['energy']) < 1e-4*max(1.,abs(computed))
                assert abs(control-x['same_moment_control_energy']) < 1e-8
                disp=np.linalg.norm(a-raw['samples_200'][20+j],axis=-1).mean()/norm
                assert np.isclose(disp,x['paired_displacement_200_400'],rtol=1e-10,atol=1e-12)
                checks+=1
                if h==0 and seed==1004 and j==50:
                    lengths=np.linalg.norm(a,axis=-1)
                    y=float(raw['queries'][20+j,0]); yy=raw['Y'][:,0]
                    outlier={'run':r['run'],'condition':j,'query_y':y,
                        'train_y_range':[float(yy.min()),float(yy.max())],
                        'max_endpoint_norm':float(lengths.max()),'median_endpoint_norm':float(np.median(lengths)),
                        'count_endpoint_norm_above_100':int((lengths>100).sum()),
                        'direct_energy':computed,'saved_energy':x['energy'],
                        'mean_excess_without_condition_posthoc':float(np.mean([z['excess_energy'] for z in rows if z['condition']!=j]))}
    assert len({(r['h'],r['seed']) for r in seeds})==10
    aggregates=[]
    for h in (0.,.1):
        ss=[r for r in seeds if r['h']==h]; ex=np.array([r['mean_excess_energy'] for r in ss])
        aggregates.append({'h':h,'mean_seed_excess':float(ex.mean()),'median_seed_excess':float(np.median(ex)),
            'min_seed_excess':float(ex.min()),'max_seed_excess':float(ex.max()),
            'above_diagnostic_q95':sum(r['above_diagnostic_q95'] for r in ss),
            'solver_pass':sum(r['solver_pass'] for r in ss),
            'gaussian_best_excess_count':sum(min([f for f in families if f['h']==h and f['seed']==seed],
                key=lambda f:f['mean_excess_energy'])['family']=='gauss' for seed in range(1001,1006))})
    result={'scope':'ten completed200k runs, five new independent problem seeds,64queries/run,M512',
        'primary':'mean normalized Gaussian-reference energy minus reference-reference mean',
        'aggregates':aggregates,'per_seed':seeds,'families':families,'solver_failed':failed,
        'histories':histories,'raw_primary_conditions_verified':checks,
        'raw_controls_verified':checks,'outlier':outlier,'raw_energy_differences':discrepancies,
        'provenance':provenance,'warning':'Five independent problem seeds; conditions nested within seeds. Null16-pair q95 is descriptive, not a formal test. Failed solver row retained.'}
    (root/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    with (root/'per_seed.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(seeds[0]));w.writeheader();w.writerows(seeds)
    lines=['# Tổng hợp 10 runs trên seeds mới — 16/10/2026','',
        'Cả 10 runs đã hoàn tất 200.000 iterations và đánh giá cuối. Mỗi mức h có 5 problem seeds 1001–1005. Mỗi run dùng 20 training conditions để fit bandwidth, 64 conditions mới để đánh giá, 512 samples/condition. So sánh tại cùng checkpoint 200k; không chọn seed theo kết quả.','',
        '**Kết luận:** h=0.1 làm Gaussian reference gần sampler hơn, nhưng dữ liệu không xác nhận một bandwidth mô tả đúng toàn bộ phân phối. h=0 có một condition cực trị chưa qua solver screen; giữ nguyên trong số liệu chính.','',
        '| training h | seed | h_eff | mean excess energy | conditions trên q95 tham chiếu (diagnostic) | solver pass |',
        '|---|---|---|---|---|---|']
    for r in sorted(seeds,key=lambda r:(r['h'],r['seed'])):
        lines.append(f"| {r['h']} | {r['seed']} | {r['h_eff']:.6g} | {r['mean_excess_energy']:.6g} | {r['above_diagnostic_q95']}/64 | {r['solver_pass']}/64 |")
    lines+=['','Energy được chuẩn hóa bằng sqrt(trace posterior giải tích); excess trừ mean reference-vs-reference cùngM và cùng finite terminal time. Giá trị nhỏ hơn nghĩa là gần reference hơn, không tự động là posterior chất lượng cao hơn.','',
        '| h | mean qua 5 seeds | median qua 5 seeds | khoảng qua 5 seeds | Gaussian tốt nhất trong 4 families |',
        '|---|---|---|---|---|']
    for a in aggregates:
        lines.append(f"| {a['h']} | {a['mean_seed_excess']:.6g} | {a['median_seed_excess']:.6g} | {a['min_seed_excess']:.6g}–{a['max_seed_excess']:.6g} | {a['gaussian_best_excess_count']}/5 |")
    lines+=['','## Giới hạn và outlier','',
        'Phép thử này đánh giá generalization tại labels mới. Ở h=0, empirical conditional law chỉ được xác định tại training labels; sự thất bại ở label mới không bác bỏ định lý atomicity/hard conditioning tại training labels. Kết luận cần thu hẹp là cách diễn giải Gaussian effective-bandwidth như một law tổng quát của trained sampler ngoài tập conditions đã fit.','',
        'q95 chỉ dùng 16 reference pairs/condition, không phải một kiểm định có hiệu chỉnh multiple testing. Có 5 problem seeds độc lập, không phải 320 replicates mô hình. Không dùng khoảng bootstrap qua conditions như uncertainty giữa problem seeds.','',
        'h=0, seed 1004, condition 50 có saved energy 253.092, paired solver displacement chuẩn hóa 118.101 và trace khoảng 1.70e12. Solver chưa được tách khỏi learned-field error ở condition này. Không được gọi tất cả 640 conditions đã hội tụ; 639/640 qua practical screen. Outlier không bị loại khỏi primary mean. Median qua seeds được báo song song, không thay thế primary đã khóa.']
    if outlier:
        lines+=['',f"Raw check: query y={outlier['query_y']:.6g}, training-label range={outlier['train_y_range']}; {outlier['count_endpoint_norm_above_100']}/512 endpoints có norm>100, max norm={outlier['max_endpoint_norm']:.6g}, median norm={outlier['median_endpoint_norm']:.6g}. Đây là quan sát số, chưa là chẩn đoán nguyên nhân.",
            f"Sensitivity posthoc: mean excess của seed 1004 nếu bỏ riêng condition 50 là {outlier['mean_excess_without_condition_posthoc']:.6g}; con số này không thay thế mean chính."]
    lines+=['','## Reference-family comparison','',
        'Gaussian tốt nhất trên cả 5 seeds khi h=0.1; khi h=0, một family khác gần sampler hơn ở cả 5 seeds. Các scales được chọn bằng fit variance trên 20 training conditions, không tối ưu energy trên held-out data. Vì vậy đây là so sánh các reference đã fit theo protocol, không chứng minh family nào tối ưu trên mọi tham số.','',
        '## Teacher error và rollout error','']
    ratios=[r['risk_ratio_t999'] for r in seeds if r['h']==0]
    lines.append(f'Ở t=0.999, h=0, learned-path/teacher-error ratio là {min(ratios):.4g}–{max(ratios):.4g} qua 5 seeds. Đây là fixed-time diagnostic tại training conditions, không phải training loss tích phân theo thời gian hay một risk-transfer bound toàn cục.')
    lines += ['', 'Đồ thị loss EMA chỉ theo dõi quá trình học trong từng run. Hai mức h tối ưu các objective conditioning khác nhau; không xếp hạng chất lượng posterior bằng cách so trực tiếp giá trị loss của hai objective.']
    lines+=['','## Hệ quả cho paper','',
        '- Giữ các định lý oracle/atomicity trong đúng giả thiết và tách khỏi hành vi của network hữu hạn.',
        '- Thu hẹp h_eff thành diagnostic về moment; không trình bày Gaussian-reference fit như đồng nhất toàn bộ phân phối.',
        '- Báo cả outlier và giới hạn solver; không quy mọi sai lệch cho một cơ chế chưa kiểm tra.',
        '- Kết quả lặp lại trên seeds mới, nhưng chưa xác nhận novelty hay đủ điều kiện được ICLR chấp nhận.', '',
        f'Raw checks: {checks} Gaussian model-reference energies, {checks} same-moment-control energies; 10 Gaussian scale fits được tái tính khi --verify-raw được bật. Secondary-family energies trong báo cáo lấy từ JSON của evaluator. Full checkpoints và raw artifacts được giữ trên server.', '',
        'Run IDs, hashes và bảng secondary families: summary.json. Bảng theo seed: per_seed.csv. Không chỉnh bản thảo hoặc thay số cũ trong paper trong bước tổng hợp này.']
    (root/'SUMMARY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(13,3.7),constrained_layout=True)
    for seed in range(1001,1006):
        pair=sorted([r for r in seeds if r['seed']==seed],key=lambda r:r['h'])
        axes[0].plot([0,.1],[r['mean_excess_energy'] for r in pair],'o-',label=str(seed))
    axes[0].set_yscale('log');axes[0].set_xticks([0,.1]);axes[0].set_xlabel('Training label noise h')
    axes[0].set_ylabel('Mean excess energy / seed');axes[0].legend(title='Problem seed',fontsize=7)
    for h,color in ((0,'tab:blue'),(.1,'tab:orange')):
        for seed in range(1001,1006):
            hs=sorted([x for x in histories if x['h']==h and x['seed']==seed],key=lambda x:x['iteration'])
            axes[1].plot([r['iteration'] for r in hs],[r['loss_ema'] for r in hs],color=color,alpha=.6,label=f'h={h}' if seed==1001 else None)
    axes[1].set_xscale('log');axes[1].set_xlabel('Training iteration');axes[1].set_ylabel('Training loss EMA (proxy)');axes[1].legend(fontsize=8)
    for h,color in ((0,'tab:blue'),(.1,'tab:orange')):
        vals=[[r['mean_excess_energy'] for r in families if r['h']==h and r['family']==f] for f in ('gauss','laplace','cauchy','knn')]
        axes[2].plot(range(4),np.median(vals,axis=1),'o-',color=color,label=f'h={h}')
    axes[2].set_xticks(range(4),['Gaussian','Laplace','Cauchy','kNN'],rotation=20)
    axes[2].set_yscale('log');axes[2].set_ylabel('Median seed excess energy');axes[2].legend(fontsize=8)
    fig.savefig(root/'independent_seeds.png',dpi=180);fig.savefig(root/'independent_seeds.pdf');plt.close(fig)
    print(json.dumps({'runs':len(seeds),'primary_conditions':640,'raw_verified':checks,'solver_failed':len(failed),'aggregates':aggregates}))


if __name__=='__main__':
    main()
