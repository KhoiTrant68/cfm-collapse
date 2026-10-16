"""Independently recompute saved finite-time metrics and report paired seed results."""
from pathlib import Path
import csv,hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/novelty_interventions_20261016'


def distances(x,a): return np.linalg.norm(x[:,None]-a[None],axis=-1)
def energy(x,y):
    return 2*distances(x,y).mean()-distances(x,x).mean()-distances(y,y).mean()
def dumpcsv(p,rows):
    with p.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    data={}; checks=0; hashes={}; family_difference=[]; distance_errors=[]
    for suite in ('exact-field-stress-five-seeds','learned-label-averaging-five-seeds','tie-neighborhood-boundary'):
        folder=OUT/suite
        rec=json.loads((folder/'results.json').read_text()); assert rec['status']=='completed'
        data[suite]=rec
        hashes[str((folder/'results.json').relative_to(OUT))]=hashlib.sha256((folder/'results.json').read_bytes()).hexdigest()
        dumpcsv(OUT/f'{suite}.csv',rec['rows'])
    stress=data['exact-field-stress-five-seeds']['rows']
    assert len(stress)==600
    cached={}
    for row in stress:
        stem=f"seed{row['seed']}_d{row['d']}_{row['geometry']}"
        if stem not in cached: cached[stem]=np.load(OUT/'exact-field-stress-five-seeds'/f'{stem}.npz')
        raw=cached[stem]; j={1e-2:0,1e-4:1,1e-6:2}[row['eps']]
        c={.3:0,1.:5}[row['h']]+({'cfg':int({0.:0,3.:1,12.:2}[row['w']]),'average_fields':3,'average_priors':4}[row['arm']])
        x=raw[stem+'_fine'][j,c]; a=raw[stem+'_coarse'][j,c]; atoms=raw[stem+'_atoms']
        nearest=distances(x,atoms).min(1)
        # CUDA cdist's squared-norm expansion loses precision close to an atom.
        # Direct NumPy norms independently bound that absolute roundoff here.
        distance_errors.append(abs(nearest.mean()-row['mean_nearest']))
        assert np.isclose(nearest.mean(),row['mean_nearest'],rtol=1e-8,atol=2e-9)
        assert np.isclose(np.quantile(nearest,.95),row['q95_nearest'],rtol=1e-8,atol=2e-9)
        sep=distances(atoms,atoms)+np.eye(len(atoms))*1e20
        assert np.isclose((nearest>.01*sep.min()).mean(),row['fraction_outside_1pct_minseparation'])
        assert np.isclose(np.linalg.norm(x-a,axis=-1).mean(),row['mean_solver_displacement'],atol=1e-12)
        assert np.isclose((distances(a,atoms).argmin(1)!=distances(x,atoms).argmin(1)).mean(),row['solver_assignment_disagreement'])
        checks+=1
    for stem,raw in cached.items():
        for c,h in ((3,.3),(8,1.)):
            a=raw[stem+'_atoms']; xf=raw[stem+'_fine'][-1]
            aa=distances(xf[c],a).argmin(1);bb=distances(xf[c+1],a).argmin(1)
            family_difference.append({'instance':stem,'h':h,'paired_assignment_disagreement':float((aa!=bb).mean())})
    learned=data['learned-label-averaging-five-seeds']['rows']; assert len(learned)==60
    cached={}
    for row in learned:
        seed=row['seed']
        if seed not in cached:cached[seed]=np.load(OUT/'learned-label-averaging-five-seeds'/f'seed{seed}.npz')
        raw=cached[seed];c={0.:0,.5:4,1.5:8}[row['radius_in_label_std']]+row['query_index']
        x=raw['learned_fine'][c];y=raw['oracle_fine'][c]
        assert np.isclose(distances(x,raw['atoms']).min(1).mean(),row['mean_nearest'],atol=1e-12)
        assert np.isclose(distances(y,raw['atoms']).min(1).mean(),row['oracle_mean_nearest'],atol=1e-12)
        assert np.isclose(np.linalg.norm(raw['learned_coarse'][c]-x,axis=-1).mean(),row['mean_solver_displacement'],atol=1e-12)
        # Recompute the analytic posterior trace from each frozen problem seed.
        from src.problems.linear_gaussian import LinearGaussianProblem
        p=LinearGaussianProblem.create(2,1,.1,seed=seed)
        assert np.isclose(energy(x,y)/np.sqrt(p.posterior_trace()),row['network_reference_energy_normalized'],rtol=1e-7,atol=1e-10)
        checks+=1
    ties=data['tie-neighborhood-boundary']; assert len(ties['rows'])==324
    raw_ties=np.load(OUT/'tie-neighborhood-boundary/raw.npz')
    for row in ties['rows']:
        j={1e-2:0,1e-4:1,1e-6:2,1e-8:3}[row['eps']]
        i=int(np.where(raw_ties['initials']==row['x0'])[0][0])
        stem=f"{row['h']}_{row['arm']}"
        assert raw_ties[stem+'_fine'][j,i]==row['endpoint']
        assert abs(raw_ties[stem+'_fine'][j,i]-raw_ties[stem+'_coarse'][j,i])==row['solver_displacement']
        assert np.isclose(abs(abs(row['endpoint'])-1),row['nearest_atom_distance'])
        if row['x0']==0.:assert row['endpoint']==0.
        if row['arm']=='hard_field_average':assert np.isclose(row['endpoint'],row['eps']*row['x0'],atol=1e-10)
        checks+=1
    final=[r for r in stress if r['eps']==1e-6]
    aggregates=[]
    for qt in ('training','fresh'):
        for radius in (0.,.5,1.5):
            picked=[r for r in learned if r['query_type']==qt and r['radius_in_label_std']==radius]
            means=[]
            for seed in sorted({r['seed'] for r in picked}):
                rr=[r for r in picked if r['seed']==seed]
                means.append({k:float(np.mean([r[k] for r in rr])) for k in ('network_reference_energy_normalized','mean_nearest','oracle_mean_nearest','mean_solver_displacement','oracle_solver_displacement')})
            aggregates.append({'query_type':qt,'radius':radius,'n_seeds':5,
                **{f'mean_{k}':float(np.mean([r[k] for r in means])) for k in means[0]},
                'seed_energy_min':min(r['network_reference_energy_normalized'] for r in means),
                'seed_energy_max':max(r['network_reference_energy_normalized'] for r in means)})
    result={'status':'verified','raw_metric_rows_checked':checks,'result_hashes':hashes,
        'max_exact_mean_distance_roundoff':max(distance_errors),
        'exact_final_cells':len(final),'exact_final_max_q95_nearest':max(r['q95_nearest'] for r in final),
        'exact_final_max_solver_displacement':max(r['mean_solver_displacement'] for r in final),
        'exact_final_max_assignment_disagreement':max(r['solver_assignment_disagreement'] for r in final),
        'exact_final_max_fraction_outside_threshold':max(r['fraction_outside_1pct_minseparation'] for r in final),
        'field_vs_prior_assignments':family_difference,'learned_aggregates':aggregates,
        'runtime_seconds':{k:v['elapsed_seconds'] for k,v in data.items()},
        'warning':'Diagnostic finite-time evidence. No equivalence, null-basin, or priority proof.'}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    dumpcsv(OUT/'learned_seed_aggregates.csv',aggregates)
    fig,axs=plt.subplots(1,3,figsize=(13,3.6))
    for arm,w,label in [('cfg',0.,'single field'),('cfg',12.,'CFG w=12'),('average_fields',0.,'field average'),('average_priors',0.,'prior average')]:
        xs=[1e-2,1e-4,1e-6]
        ys=[np.mean([r['mean_nearest'] for r in stress if r['d']==2 and r['geometry']=='random' and r['h']==1. and r['eps']==eps and r['arm']==arm and r['w']==w]) for eps in xs]
        axs[0].loglog(xs,ys,'o-',label=label)
    axs[0].set(xlabel='terminal gap',ylabel='mean nearest-atom distance',title='Exact fields: 5 seed means');axs[0].legend(fontsize=7)
    for h in (.05,.2,1.):
        rr=[r for r in ties['rows'] if r['arm']=='average_fields' and r['h']==h and r['x0']==1e-8]
        axs[1].loglog([r['eps'] for r in rr],[max(r['nearest_atom_distance'],1e-15) for r in rr],'o-',label=f'h={h}')
    axs[1].set(xlabel='terminal gap',ylabel='nearest-atom distance',title='Near tie: initial offset 1e-8');axs[1].legend(fontsize=7)
    for seed in range(1001,1006):
        ys=[np.mean([r['network_reference_energy_normalized'] for r in learned if r['seed']==seed and r['query_type']=='fresh' and r['radius_in_label_std']==a]) for a in (0.,.5,1.5)]
        axs[2].plot([0.,.5,1.5],ys,'o-',label=str(seed))
    axs[2].set(xlabel='averaging radius / label std',ylabel='normalized energy statistic',title='Learned vs exact average: fresh labels');axs[2].legend(fontsize=7)
    fig.tight_layout();fig.savefig(OUT/'novelty_experiments.png',dpi=180);fig.savefig(OUT/'novelty_experiments.pdf');plt.close(fig)
    lines=['# Novelty intervention experiments — verified server results','','Finite-time diagnostics; no theorem or novelty certification.','',
        f'Raw metric rows independently checked: {checks}.',
        f'Exact final cells: {len(final)}; max q95 nearest distance {result["exact_final_max_q95_nearest"]:.6g}; max mean solver displacement {result["exact_final_max_solver_displacement"]:.6g}.',
        f'Max paired assignment disagreement: {result["exact_final_max_assignment_disagreement"]:.6g}.',
        f'Max fraction outside 1% minimum-separation threshold: {result["exact_final_max_fraction_outside_threshold"]:.6g}.','',
        '| queries | radius / label std | seed-mean energy | range over seed means | network nearest | oracle nearest | network solver displacement |',
        '|---|---|---|---|---|---|---|']
    for r in aggregates:
        lines.append(f'| {r["query_type"]} | {r["radius"]} | {r["mean_network_reference_energy_normalized"]:.6g} | {r["seed_energy_min"]:.6g}–{r["seed_energy_max"]:.6g} | {r["mean_mean_nearest"]:.6g} | {r["mean_oracle_mean_nearest"]:.6g} | {r["mean_mean_solver_displacement"]:.6g} |')
    lines+=['','Five independent problem seeds; conditions and samples are nested, not independent replications.',
        'Finite-M energy is biased and has no null/equivalence threshold in this study. Small values are not proof of law equality.',
        'Full per-cell metrics are in CSV; raw arrays and checkpoint hashes are retained.']
    (OUT/'SUMMARY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('field_vs_prior_assignments','learned_aggregates','result_hashes')},indent=2))


if __name__=='__main__':main()
