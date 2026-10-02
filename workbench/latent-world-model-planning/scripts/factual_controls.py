"""Whole locked-anchor factual replay controls; no filtering by success."""
import argparse
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
import h5py
import hdf5plugin
import numpy as np
import torch


def dump(p,x):
    Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')


def audit(task,dataset,anchors,offset,seed,label,out,rows):
    import gymnasium as gym
    import stable_worldmodel
    env=gym.make('swm/TwoRoom-v1' if task=='tworoom' else 'swm/PushT-v1',render_mode='rgb_array').unwrapped
    with h5py.File(dataset) as f:
        offsets=f['ep_offset'][:];key='state' if task=='pusht' else 'proprio'
        for j in range(len(anchors['episode'])):
            ep,t=int(anchors['episode'][j]),int(anchors['start'][j]);ix=int(offsets[ep])+t
            actual=f[key][ix:ix+offset+1];actions=f['action'][ix:ix+offset]
            image=f['pixels'][ix]
            env.reset(seed=seed+j);env._set_state(actual[0].copy());env._set_goal_state(actual[-1].copy())
            replay=[np.asarray(env._get_obs()) if task=='pusht' else env._get_info()['proprio']]
            mae=float(np.abs(env.render().astype(float)-image).mean())
            success=False
            for a in actions:
                _,_,done,_,_=env.step(a);success=success or bool(done)
                replay.append(np.asarray(env._get_obs()) if task=='pusht' else env._get_info()['proprio'])
            replay=np.asarray(replay);error=replay-actual
            row={'stratum':label,'task':task,'goal_offset':offset,'anchor':j,'episode':ep,'start':t,
                 'success_during_factual_suffix':success,'initial_pixel_mae_0_255':mae,
                 'state_max_abs_by_coordinate':np.abs(error).max(0).tolist()}
            if task=='pusht':
                angle=np.arctan2(np.sin(error[:,4]),np.cos(error[:,4]))
                row.update({'position_max_abs_pixels':float(np.abs(error[:,:4]).max()),
                    'block_angle_max_abs_radians_wrapped':float(np.abs(angle).max()),
                    'agent_velocity_max_abs_pixels_per_second':float(np.abs(error[:,5:]).max())})
            else:row['position_max_abs_pixels']=float(np.abs(error).max())
            rows.append(row);dump(out/'rows.json',rows)
        print('factual_controls',label,'n',len(anchors['episode']),flush=True)
    env.close()


def run(args):
    torch.set_num_threads(4)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False);rows=[]
    dump(out/'config.json',{'args':vars(args),'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'policy':'all locked anchors; controls do not change main evaluation inclusion',
        'success':'any native success during factual suffix; run complete suffix for error audit',
        'limitation':'public setter consistency, not complete physics-memory restoration'})
    (out/'factual_controls_used.py').write_text(Path(__file__).read_text())
    base=Path(args.e16_base);data=np.load(base/'eval_anchors.npz')
    manifest=json.loads((base/'data_manifest.json').read_text())
    audit('tworoom','/tmp/latent-wm-data/'+manifest['dataset_file'],data,25,0,'E16-seed0-eval48',out,rows)
    prepared=Path(args.prepared)
    for source in args.sources:
        cfg=json.loads((Path(source)/'config.json').read_text());task=cfg['task']
        for offset in [25,75]:
            data=np.load(prepared/f'{task}_g{offset}.npz')
            audit(task,cfg['dataset'],data,offset,61000,f'E13-{task}-g{offset}',out,rows)
    summaries=[]
    for label in sorted({r['stratum'] for r in rows}):
        rr=[r for r in rows if r['stratum']==label]
        summaries.append({'stratum':label,'n':len(rr),'factual_successes':sum(r['success_during_factual_suffix'] for r in rr),
            'max_position_error_pixels':max(r['position_max_abs_pixels'] for r in rr),
            'max_initial_pixel_mae_0_255':max(r['initial_pixel_mae_0_255'] for r in rr),
            'max_wrapped_angle_error_radians':max(r.get('block_angle_max_abs_radians_wrapped',0) for r in rr)})
    dump(out/'summary.json',summaries);dump(out/'complete.json',{'completed':True,'anchors':len(rows)})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--e16-base',required=True);p.add_argument('--prepared',required=True)
    p.add_argument('--sources',nargs='+',required=True);p.add_argument('--output',required=True);args=p.parse_args()
    try:run(args)
    except Exception as e:
        out=Path(args.output)
        if out.exists():dump(out/'failure.json',{'error':type(e).__name__,'message':str(e)})
        raise
