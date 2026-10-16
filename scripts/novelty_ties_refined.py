"""Posthoc cutoff diagnosis; preserve the original tie experiment unchanged.

Use sinh(2a)/(cosh(2a)+cosh(2b)) in log space instead of cancelling saturated
tanh values. Tight absolute tolerance matters for tiny positive trajectories.
"""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
import numpy as np
import torch
from scipy.integrate import solve_ivp


def mean(x,s,h):
    eps=np.exp(-s); a=(-np.expm1(-s))*x/eps**2; b=1/h**2
    aa=2*a.abs()
    logsinh=aa+torch.log(-torch.expm1(-2*aa))-np.log(2.)
    logcosh=aa+torch.log1p(torch.exp(-2*aa))-np.log(2.)
    bb=2*b; other=bb+np.log1p(np.exp(-2*bb))-np.log(2.)
    return a.sign()*torch.exp(logsinh-torch.logaddexp(logcosh,torch.full_like(a,other)))


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    parent=Path(__file__).with_name('novelty_interventions.py')
    spec=importlib.util.spec_from_file_location('locked_oracle',parent)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    torch.set_num_threads(4)
    z=torch.tensor([-1.,-.1,0.,.1,1.],dtype=torch.float64)
    assert torch.equal(mean(z,1.,.2),-mean(-z,1.,.2))
    assert torch.isfinite(mean(z,40.,.05)).all()
    gaps=np.array([1e-2,1e-4,1e-6,1e-8,1e-10,1e-14,1e-18]);ends=np.log(1/gaps)
    initials=np.array([0.,1e-12,1e-8,1e-4]);x=torch.tensor(initials,dtype=torch.float64)
    rows=[];raw={};adaptive=[]
    for h in (.05,.2,1.):
        f=lambda x,s:mean(x,s,h)-x
        a=mod.rk4(f,x,512,ends); b=mod.rk4(f,x,1024,ends)
        assert torch.equal(b[:,0],torch.zeros_like(b[:,0]))
        raw[f'{h}_coarse']=a.numpy();raw[f'{h}_fine']=b.numpy()
        for j,eps in enumerate(gaps):
            for i,x0 in enumerate(initials):
                rows.append({'h':h,'x0':x0,'eps':float(eps),'endpoint':b[j,i].item(),
                    'solver_displacement':abs(a[j,i].item()-b[j,i].item())})
        for x0 in (1e-12,1e-8):
            def f_adaptive(s,z):
                return (mean(torch.tensor(z,dtype=torch.float64),s,h)-torch.tensor(z)).numpy()
            sol=solve_ivp(f_adaptive,(0,ends[-1]),[x0],method='DOP853',rtol=1e-11,atol=1e-30,t_eval=ends)
            adaptive.append({'h':h,'x0':x0,'success':bool(sol.success),'message':sol.message,
                'saved_times':sol.t.tolist(),'endpoint':np.asarray(sol.y)[0].tolist(),'nfev':sol.nfev})
            print(f'adaptive h={h}, x0={x0}: success={sol.success}, {sol.message}',flush=True)
        print(f'h={h}: final endpoints={b[-1].tolist()}',flush=True)
    np.savez_compressed(args.out/'raw.npz',initials=initials,gaps=gaps,**raw)
    (args.out/'results.json').write_text(json.dumps({'status':'completed_with_solver_limits' if any(not r['success'] for r in adaptive) else 'completed','rows':rows,'adaptive':adaptive,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),
        'steps_per_segment':[512,1024],'rtol':1e-11,'atol':1e-30,
        'elapsed_seconds':time.monotonic()-start,
        'scope':'Posthoc diagnostic; original primary tie experiment retained.'},indent=2))


if __name__=='__main__':main()
