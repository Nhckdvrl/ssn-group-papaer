"""Explicit Push fact inputs for the unchanged pinned GC-IDM training component."""
import argparse
import shutil
import subprocess
import sys
import numpy as np
import goal_policy_baseline as g

CACHE=g.ROOT/'20261005-E14-goalpolicy-pusht-RELEASED-features-retry1'


def load(geometry,seed):
    assert geometry=='RELEASED' and seed==0
    assert g.read(CACHE/'complete.json')==dict(completed=True,episodes=86,frames=9374,frozen_model_unchanged=True)
    c=g.read(CACHE/'config.json')
    for key,value in c['array_sha256'].items():assert g.sha(CACHE/f'{key}.npy')==value
    z=np.load(CACHE/'features.npy');a=np.load(CACHE/'actions.npy');ep=np.load(CACHE/'episode_ids.npy')
    assert z.shape==(9374,192) and a.shape==(9374,2) and np.isfinite(z).all()
    end=np.zeros(len(ep),int);covered=np.zeros(len(ep),bool)
    for row in c['layout']:
        start=row['cache_row'];stop=start+row['frames'];assert not covered[start:stop].any()
        assert (ep[start:stop]==row['episode']).all();end[start:stop]=stop;covered[start:stop]=True
    assert covered.all() and set(ep)==set(range(86)) and not set(ep)&set(c['excluded_fresh_eval_episodes'])
    valid=np.flatnonzero((ep[:-1]==ep[1:])&np.isfinite(a[:-1]).all(1))
    perm=np.random.default_rng(115200).permutation(valid);nval=int(len(valid)*.1)
    c=dict(c,source_adapter_sha256=g.sha(__file__),component_trainer_sha256=g.sha(g.__file__))
    return z,a,ep,end,perm[nval:],perm[:nval],c


def main(mode,device,arm):
    g.load=load
    if mode=='preflight':g.preflight('RELEASED',0,device)
    elif mode=='train':g.train('RELEASED',0,arm)
    else:
        out=g.ROOT/'20261005-E14-goalpolicy-pusht-pipeline-s0';assert not out.exists();out.mkdir()
        shutil.copy2(__file__,out/'adapter_used.py');shutil.copy2(g.__file__,out/'component_used.py')
        g.save(out/'config.json',dict(task='pusht',seed=0,adapter_sha256=g.sha(__file__),component_sha256=g.sha(g.__file__)))
        commands=[['preflight','--device',d] for d in ['cpu','cuda']]+[['train','--arm',a] for a in g.ARMS]
        try:
            for command in commands:subprocess.run([sys.executable,'-u',__file__,*command],check=True)
            g.save(out/'complete.json',dict(completed=True,task='pusht',seed=0,training_runs=3))
        except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error),phase=command));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','train','queue']);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--arm',choices=g.ARMS);a=p.parse_args();g.torch.set_num_threads(4);main(a.mode,a.device,a.arm)
