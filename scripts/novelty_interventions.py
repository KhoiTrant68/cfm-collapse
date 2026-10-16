"""Frozen protocol: exact intervention stress, tie diagnosis, and learned averaging.

Finite-time numerical evidence does not prove atomicity, null exceptional basins,
or literature priority. Every output directory is new; existing runs are read-only.
"""
from pathlib import Path
import argparse, hashlib, json, platform, time
import numpy as np
import torch


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@torch.no_grad()
def oracle(x, s, atoms, lp, w):
    eps=np.exp(-s); t=-np.expm1(-s)
    spatial=-.5*((x[...,None,:]-t*atoms)**2).sum(-1)/eps**2
    conditional=(torch.softmax(spatial[:,None]+lp[:,:,None,:],-1)@atoms).mean(1)
    unconditional=torch.softmax(spatial,-1)@atoms
    return (1+w[:,None,None])*conditional-w[:,None,None]*unconditional-x


@torch.no_grad()
def rk4(f, x, steps, ends):
    """Record at prescribed end times; same steps per segment for paired refinement."""
    x=x.clone(); saved=[]; start=0.
    for end in ends:
        ds=(end-start)/steps
        for i in range(steps):
            s=start+i*ds
            a=f(x,s); b=f(x+ds*a/2,s+ds/2)
            c=f(x+ds*b/2,s+ds/2); d=f(x+ds*c,s+ds)
            x=x+ds*(a+2*b+2*c+d)/6
        if not torch.isfinite(x).all(): raise FloatingPointError('nonfinite trajectory')
        saved.append(x.clone()); start=end
    return torch.stack(saved)


def summarize(a,b,atoms):
    distance=torch.cdist(b,atoms); nearest=distance.min(-1).values
    displacement=(a-b).norm(dim=-1)
    separation=torch.pdist(atoms).min().item()
    return {'mean_nearest':nearest.mean().item(),'q95_nearest':torch.quantile(nearest,.95).item(),
        'max_nearest':nearest.max().item(),'mean_solver_displacement':displacement.mean().item(),
        'max_solver_displacement':displacement.max().item(),
        'solver_assignment_disagreement':(torch.cdist(a,atoms).argmin(-1)!=distance.argmin(-1)).double().mean().item(),
        'fraction_outside_1pct_minseparation':(nearest>.01*separation).double().mean().item(),
        'min_atom_separation':separation,'trace':b.var(0,unbiased=True).sum().item()}


def controls(device):
    dtype=torch.float64
    a=torch.tensor([[.3,-.7]],device=device,dtype=dtype)
    x=torch.arange(12,device=device,dtype=dtype).reshape(1,6,2)/12
    lp=torch.zeros(1,3,1,device=device,dtype=dtype); w=torch.tensor([12.],device=device,dtype=dtype)
    f=lambda x,s:oracle(x,s,a,lp,w)
    got=rk4(f,x,64,[np.log(100.)])[-1]
    assert (got-(.99*a+.01*x)).abs().max()<1e-7
    # Zero averaging radius gives exactly the original field.
    atoms=torch.tensor([[-1.,0.],[1.,0.]],device=device,dtype=dtype)
    p=torch.tensor([[[0.,-2.]]],device=device,dtype=dtype)
    assert torch.allclose(oracle(x,.5,atoms,p,w),oracle(x,.5,atoms,p.expand(-1,5,-1),w))
    return {'single_atom_affine_max_error':(got-(.99*a+.01*x)).abs().max().item(),
        'zero_radius_field_identity':True}


def stress(args, write):
    raw={}; rows=[]; dtype=torch.float64
    for seed in args.seeds:
        for dim in (2,8):
            rng=np.random.default_rng(seed+100*dim)
            base=rng.normal(size=(12,dim))/np.sqrt(dim)
            labels=rng.normal(size=12); sources=rng.normal(size=(args.M,dim))
            for geometry in ('random','near_duplicate'):
                atoms=base.copy()
                if geometry=='near_duplicate':
                    direction=base[1]-base[0]; direction/=np.linalg.norm(direction)
                    atoms[1]=atoms[0]+.02*direction
                configs=[]; priors=[]; strengths=[]
                for h in (.3,1.):
                    q=labels[0]+h*np.array([-2.,-1.,0.,1.,2.])
                    logp=-.5*((q[:,None]-labels[None])/h)**2
                    for w in (0.,3.,12.):
                        configs.append({'h':h,'arm':'cfg','w':w})
                        priors.append(np.repeat(logp[2:3],5,axis=0)); strengths.append(w)
                    configs.append({'h':h,'arm':'average_fields','w':0.})
                    priors.append(logp); strengths.append(0.)
                    probs=np.exp(logp-logp.max(1,keepdims=True)); probs/=probs.sum(1,keepdims=True)
                    configs.append({'h':h,'arm':'average_priors','w':0.})
                    priors.append(np.repeat(np.log(probs.mean(0))[None],5,axis=0)); strengths.append(0.)
                A=torch.tensor(atoms,device=args.device,dtype=dtype)
                lp=torch.tensor(np.array(priors),device=args.device,dtype=dtype)
                w=torch.tensor(strengths,device=args.device,dtype=dtype)
                x=torch.tensor(sources,device=args.device,dtype=dtype)[None].expand(len(configs),-1,-1)
                f=lambda x,s:oracle(x,s,A,lp,w)
                ends=np.log(1/np.array([1e-2,1e-4,1e-6]))
                coarse=rk4(f,x,args.steps,ends); fine=rk4(f,x,2*args.steps,ends)
                stem=f'seed{seed}_d{dim}_{geometry}'
                raw[stem+'_atoms']=atoms; raw[stem+'_labels']=labels; raw[stem+'_source']=sources
                raw[stem+'_coarse']=coarse.cpu().numpy(); raw[stem+'_fine']=fine.cpu().numpy()
                for j,eps in enumerate((1e-2,1e-4,1e-6)):
                    for c,cfg in enumerate(configs):
                        rows.append({'seed':seed,'d':dim,'geometry':geometry,'eps':eps,**cfg,
                            **summarize(coarse[j,c],fine[j,c],A)})
                np.savez_compressed(args.out/f'{stem}.npz',**{k:v for k,v in raw.items() if k.startswith(stem)})
                raw={}; write(rows=rows)
                print(f'{stem}: {len(rows)} rows saved',flush=True)
                if time.monotonic()-args.start>args.max_seconds: raise TimeoutError('wall budget')
    return rows


def ties(args, write):
    from scipy.integrate import solve_ivp
    initials=np.array([-1e-2,-1e-4,-1e-8,-1e-12,0,1e-12,1e-8,1e-4,1e-2])
    ends=np.log(1/np.array([1e-2,1e-4,1e-6,1e-8])); rows=[]; raw={}; adaptive=[]
    x=torch.tensor(initials,device=args.device,dtype=torch.float64)
    for h in (.05,.2,1.):
        for arm in ('average_fields','average_priors','hard_field_average'):
            def f(x,s):
                if arm=='hard_field_average': return -x
                eps=np.exp(-s); t=-np.expm1(-s); a=t*x/eps**2
                mean=.5*(torch.tanh(a+1/h**2)+torch.tanh(a-1/h**2)) if arm=='average_fields' else torch.tanh(a)
                return mean-x
            a=rk4(f,x,args.steps,ends); b=rk4(f,x,2*args.steps,ends)
            assert torch.equal(b[:,4],torch.zeros_like(b[:,4]))
            if arm=='hard_field_average': assert np.max(np.abs(b.cpu().numpy()-np.exp(-ends[:,None])*initials))<1e-8
            raw[f'{h}_{arm}_coarse']=a.cpu().numpy(); raw[f'{h}_{arm}_fine']=b.cpu().numpy()
            for j,eps in enumerate((1e-2,1e-4,1e-6,1e-8)):
                for i,x0 in enumerate(initials):
                    rows.append({'h':h,'arm':arm,'eps':eps,'x0':x0,'endpoint':b[j,i].item(),
                        'nearest_atom_distance':abs(abs(b[j,i].item())-1),
                        'solver_displacement':abs(a[j,i].item()-b[j,i].item())})
            if arm=='average_fields' and h in (.2,1.):
                for x0 in (0.,1e-4,1e-8):
                    def scalar(s,z):
                        eps=np.exp(-s); t=-np.expm1(-s); v=t*z/eps**2
                        return .5*(np.tanh(v+1/h**2)+np.tanh(v-1/h**2))-z
                    sol=solve_ivp(scalar,(0,ends[-1]),[x0],method='DOP853',rtol=1e-10,atol=1e-13,t_eval=ends)
                    assert sol.success
                    adaptive.append({'h':h,'x0':x0,'endpoint':sol.y[0].tolist(),'nfev':sol.nfev})
    np.savez_compressed(args.out/'raw.npz',initials=initials,**raw)
    write(rows=rows,adaptive=adaptive)
    return rows


def energy(a,b):
    return (2*torch.cdist(a,b).mean()-torch.cdist(a,a).mean()-torch.cdist(b,b).mean()).item()


def learned(args, write):
    from src.models.mlp_velocity import build_model
    from src.problems.linear_gaussian import LinearGaussianProblem
    from src.utils import load_yaml
    rows=[]; hashes={}
    for seed in args.seeds:
        run=Path(f'results/exp1/linear-gaussian-mlp-h0p1-seed{seed}-200k')
        cfg=load_yaml(run/'config.yaml'); dc=cfg['data']; h=float(cfg['train']['y_noise_h'])
        assert h==.1 and dc['d']==2 and dc['k']==1 and dc.get('source_std',1.)==1.
        problem=LinearGaussianProblem.create(dc['d'],dc['k'],dc['sigma_obs'],seed=seed,
            prior_std=dc.get('prior_std',1.),A_kind=dc.get('A_kind','random'))
        X,Y=problem.sample_dataset(dc['N'],seed=seed+1)
        _,fresh=problem.sample_dataset(2,seed=20261019+seed)
        queries=torch.cat([Y[[0,len(Y)-1]],fresh]).double().to(args.device)
        A=X.double().to(args.device); labels=Y.double().to(args.device)
        scale=Y.double().std().item(); radii=np.array([0.,.5,1.5])*scale
        y=torch.cat([queries for _ in radii]); offsets=torch.tensor([-1.,0.,1.],device=args.device,dtype=torch.float64)
        shifted=torch.cat([queries[:,None,:]+r*offsets[None,:,None] for r in radii])
        lp=-.5*((shifted[:,:,None,:]-labels[None,None,:,:])/h).square().sum(-1)
        w=torch.zeros(len(y),device=args.device,dtype=torch.float64)
        rng=np.random.default_rng(20261020+seed)
        source=rng.normal(size=(4,args.M,dc['d']))
        x=torch.tensor(np.tile(source,(3,1,1)),device=args.device,dtype=torch.float64)
        ck=run/'checkpoints/ckpt_200000.pt'; hashes[str(ck)]=sha(ck)
        model=build_model(cfg,dc['d'],dc['k']).to(args.device).eval()
        model.load_state_dict(torch.load(ck,map_location=args.device,weights_only=False)['model_state'])
        @torch.no_grad()
        def vf(z,t):
            c,m,d=z.shape
            zz=z[:,:,None,:].expand(-1,-1,3,-1).reshape(-1,d).float()
            yy=shifted[:,None,:,:].expand(-1,m,-1,-1).reshape(-1,1).float()
            tt=torch.full((len(zz),),t,device=args.device)
            return model(zz,tt,yy).reshape(c,m,3,d).mean(2)
        # Original network arithmetic remains float32, including its time embedding.
        ac=rk4(vf,x.float(),args.steps,[.999])[-1].double()
        bf=rk4(vf,x.float(),args.steps*2,[.999])[-1].double()
        f=lambda z,s:oracle(z,s,A,lp,w)
        oc=rk4(f,x,args.oracle_steps,[np.log(1000.)])[-1]
        of=rk4(f,x,2*args.oracle_steps,[np.log(1000.)])[-1]
        raw={'atoms':X.numpy(),'labels':Y.numpy(),'queries':queries.cpu().numpy(),'shifted':shifted.cpu().numpy(),
            'source':source,'learned_coarse':ac.cpu().numpy(),'learned_fine':bf.cpu().numpy(),
            'oracle_coarse':oc.cpu().numpy(),'oracle_fine':of.cpu().numpy()}
        np.savez_compressed(args.out/f'seed{seed}.npz',**raw)
        norm=np.sqrt(problem.posterior_trace())
        for c in range(12):
            row={'seed':seed,'radius_in_label_std':(0.,.5,1.5)[c//4],
                'query_index':c%4,'query_type':'training' if c%4<2 else 'fresh',
                'network_reference_energy_normalized':energy(bf[c],of[c])/norm,
                'oracle_mean_nearest':torch.cdist(of[c],A).min(1).values.mean().item(),
                'oracle_solver_displacement':(oc[c]-of[c]).norm(dim=-1).mean().item(),
                **summarize(ac[c],bf[c],A)}
            rows.append(row)
        write(rows=rows,checkpoint_hashes=hashes)
        print(f'learned seed={seed}: {len(rows)} rows saved',flush=True)
        if time.monotonic()-args.start>args.max_seconds: raise TimeoutError('wall budget')
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--suite',choices=['stress','ties','learned'],required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--device',default='cuda:0')
    ap.add_argument('--seeds',nargs='+',type=int,default=[201,202,203,204,205])
    ap.add_argument('--M',type=int,default=128)
    ap.add_argument('--steps',type=int,default=256)
    ap.add_argument('--oracle-steps',type=int,default=768)
    ap.add_argument('--max-seconds',type=int,default=1800)
    ap.add_argument('--controls-only',action='store_true')
    args=ap.parse_args(); args.start=time.monotonic(); args.out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4); torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    result={'status':'running','host':platform.node(),'pid':__import__('os').getpid(),
        'script_sha256':sha(__file__),'args':{k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items() if k!='start'},
        'torch':torch.__version__,'statistical_unit':'geometry/problem seed; paired sources are nested',
        'warning':'Finite-time diagnostic, not a proof or equivalence certificate.'}
    def write(**kwargs):
        result.update(kwargs); result['elapsed_seconds']=time.monotonic()-args.start
        (args.out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    write()
    try:
        result['controls']=controls(args.device)
        if not args.controls_only: globals()[args.suite](args,write)
        write(status='completed')
        print(f'completed {args.suite}: {result["elapsed_seconds"]:.1f}s',flush=True)
    except BaseException as e:
        write(status='failed',error=repr(e)); raise


if __name__=='__main__': main()
