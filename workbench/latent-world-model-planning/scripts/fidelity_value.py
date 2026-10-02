"""E13 A2: broader native goal ranges, FULL scoring vs a strong cheap search."""
import argparse
import json
from pathlib import Path
import h5py
import hdf5plugin
import numpy as np
import torch
from first_wave import native_info,restore,write_json,sha256,sync_time
from closed_loop import wilson
from timing_audit import SelectiveCost


class Cost:
    def __init__(self,model,mode,features):self.model,self.mode,self.features=model,mode,features
    def get_cost(self,info,actions):
        out,_=SelectiveCost(self.model,30,self.mode,None,None,64,self.features).evaluate(info,actions)
        return torch.tensor(out['estimated_cost'][None],device=actions.device)


def run(args):
    import gymnasium as gym
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    torch.set_num_threads(4);torch.manual_seed(args.seed)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    write_json(out/'config.json',{'sources':args.sources,'seed':args.seed,'episodes_per_stratum':64,
        'goal_offsets':[25,75],'methods':['FULL-300','CHEAP-900'],'harness_sha256':sha256(__file__),
        'hardware':torch.cuda.get_device_name(),'sampling_unit':'whole episode; excluded prior anchors',
        'prepared':args.prepared,
        'prepared_manifest':json.loads((Path(args.prepared)/'manifest.json').read_text()) if args.prepared else None,
        'limitation':'one released checkpoint per task; fresh per-decision native CEM distributions'})
    (out/'fidelity_value_used.py').write_text(Path(__file__).read_text())
    rows=[];rng=np.random.default_rng(args.seed)
    for source in args.sources:
        source=Path(source);cfg=json.loads((source/'config.json').read_text());task=cfg['task']
        model=torch.load(cfg['checkpoint'],map_location='cpu',weights_only=False).cuda().eval().requires_grad_(False)
        norm=np.load(source/'action_normalization.npz')
        forbidden=set(np.load(source/'anchors.npz')['episodes'].tolist())
        env=gym.make('swm/TwoRoom-v1' if task=='tworoom' else 'swm/PushT-v1',render_mode='rgb_array').unwrapped
        plan=swm.PlanConfig(horizon=1,receding_horizon=1,action_block=25,warm_start=True)
        for goal_offset in [25,75]:
            if args.prepared:
                data=np.load(Path(args.prepared)/f'{task}_g{goal_offset}.npz')
                anchors=[{k:data[k][i] for k in data.files} for i in range(len(data['episode']))]
            else:
                with h5py.File(cfg['dataset']) as f:
                    lengths,offsets=f['ep_len'][:],f['ep_offset'][:]
                    valid=np.setdiff1d(np.flatnonzero(lengths>goal_offset+1),list(forbidden))
                    episodes=rng.choice(valid,64,replace=False);forbidden.update(episodes.tolist())
                    anchors=[];key='state' if 'state' in f else 'proprio'
                    for ep in episodes:
                        start=int(rng.integers(0,int(lengths[ep])-goal_offset));row=int(offsets[ep])+start
                        anchors.append({'episode':int(ep),'start':start,'state':f[key][row],
                            'goal_state':f[key][row+goal_offset],'goal_pixels':f['pixels'][row+goal_offset]})
            np.savez_compressed(out/f'{task}_anchors_g{goal_offset}.npz',**{k:np.stack([a[k] for a in anchors]) for k in anchors[0]})
            for j,anchor in enumerate(anchors):
                for method in rng.permutation(['FULL-300','CHEAP-900']):
                    restore(env,anchor,args.seed+j);start=sync_time();success=False;steps=0;times=[]
                    info=native_info(env.render(),anchor['goal_pixels'])
                    with torch.inference_mode():goal=model.encode({'pixels':info['goal'].cuda()})['emb']
                    goal_time=sync_time()-start
                    for decision in range(2*goal_offset//25):
                        begin=sync_time();info=native_info(env.render(),anchor['goal_pixels'])
                        with torch.inference_mode():initial=model.encode({'pixels':info['pixels'].cuda()})['emb']
                        full=bool(method=='FULL-300');cost=Cost(model,'FULL-REFINE' if full else 'CHEAP-ALL',(initial,goal))
                        solver=swm.solver.CEMSolver(cost,batch_size=1,num_samples=300 if full else 900,
                            topk=30,n_steps=30,device='cuda',seed=args.seed+j*100+decision)
                        solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,config=plan)
                        solved=solver.solve(info);times.append(sync_time()-begin+(goal_time if decision==0 else 0))
                        controls=solved['actions'][0].numpy().reshape(25,2)*norm['std']+norm['mean']
                        for a in controls:
                            _,_,done,truncated,_=env.step(a);steps+=1
                            if done or truncated:success=bool(done);break
                        if done or truncated:break
                    row={'task':task,'goal_offset':goal_offset,'anchor':j,'source_episode':anchor['episode'],
                         'method':method,'success':success,'steps':steps,'planning_seconds':times,'episode_seconds':sync_time()-start}
                    rows.append(row);write_json(out/'rows.json',rows)
                    print(task,goal_offset,j,method,success,steps,flush=True)
        env.close();del model;torch.cuda.empty_cache()
    summary=[]
    for task in sorted({r['task'] for r in rows}):
        for offset in [25,75]:
            subset=[r for r in rows if r['task']==task and r['goal_offset']==offset]
            full={r['anchor']:r for r in subset if r['method']=='FULL-300'}
            for method in ['FULL-300','CHEAP-900']:
                data=[r for r in subset if r['method']==method];n=len(data);s=sum(r['success'] for r in data)
                delta=np.array([float(r['success'])-float(full[r['anchor']]['success']) for r in data])
                boot=np.random.default_rng(args.seed+9000).integers(0,n,(2000,n))
                summary.append({'task':task,'goal_offset':offset,'method':method,'n':n,'successes':s,
                    'success_wilson_ci95':wilson(s,n),'paired_success_delta_vs_full':float(delta.mean()),
                    'paired_delta_ci95':np.quantile(delta[boot].mean(1),[.025,.975]).tolist(),
                    'planning_seconds_mean':float(np.mean([t for r in data for t in r['planning_seconds']]))})
    write_json(out/'summary.json',summary);write_json(out/'complete.json',{'completed':True})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sources',nargs='+',required=True);p.add_argument('--output',required=True)
    p.add_argument('--seed',type=int,default=61000);p.add_argument('--prepared');args=p.parse_args()
    try:run(args)
    except Exception as e:
        out=Path(args.output)
        if out.exists():write_json(out/'failure.json',{'error':type(e).__name__,'message':str(e)})
        raise
