"""E16: identical diagnostic candidate banks, real simulator task utility."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from lewm_pilot import architecture, pixels, NativeCost, native_control, digest, dump

METHODS=['NO-ADD','IID','UNIFORM-COMMON-RESET','COVERAGE','GLOBAL-U','TASK-U','PBB']


def execute(env,state,goal,actions,seed):
    env.reset(seed=seed);env._set_state(state);env._set_goal_state(goal)
    distances=[float(np.linalg.norm(env._get_info()['proprio']-goal))];states=[env._get_info()['proprio']]
    stopped=None;success=False
    for control in actions:
        _,_,done,_,_=env.step(control)
        d=float(np.linalg.norm(env._get_info()['proprio']-goal));distances.append(d);states.append(env._get_info()['proprio'])
        if stopped is None and done:stopped=d;success=True
    return {'terminal_distance':distances[-1],'deployed_distance':stopped if success else distances[-1],
            'success':success,'states':np.asarray(states),'terminal_pixels':env.render()}


def run(args):
    import gymnasium as gym
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    torch.set_num_threads(4);torch.manual_seed(74000)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    source=Path(args.methods);anchors=np.load(Path(args.base_run)/'eval_anchors.npz')
    base_state=torch.load(args.checkpoint,map_location='cpu',weights_only=False)
    manifest=base_state['manifest'];mean,std=np.asarray(manifest['action_mean']),np.asarray(manifest['action_std'])
    locked={m:json.loads((source/m/'train_summary.json').read_text()) for m in METHODS}
    dump(out/'config.json',{'args':vars(args),'harness_sha256':digest(__file__),'helper_sha256':digest(Path(__file__).with_name('lewm_pilot.py')),
        'hardware':torch.cuda.get_device_name(),'base_sha256':digest(args.checkpoint),'methods':locked,
        'candidate_ids':'64 uniform from base CEM iteration15, seed74000+anchor; no outcome inputs',
        'elite_count':7,'scope':'regret within diagnostic 64-bank; native elite mean separately executed'})
    (out/'decision_audit_used.py').write_text(Path(__file__).read_text())
    base=architecture(base_state['config']).cuda().eval().requires_grad_(False)
    base.load_state_dict(base_state['state_dict'],strict=True)
    env=gym.make('swm/TwoRoom-v1',render_mode='rgb_array').unwrapped
    plan=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True)
    selections=[]
    # Commit all candidate IDs before any true outcome is executed.
    with torch.inference_mode():
        for j in range(48):
            history=pixels(anchors['pixels'][j:j+1]);goal=pixels(anchors['goal_pixels'][j:j+1]).unsqueeze(0)
            past=torch.tensor((anchors['past_actions'][j:j+1]-mean)/std,device='cuda').float().reshape(1,2,10)
            cost=NativeCost(base,history,goal,past,capture=True)
            solver=swm.solver.CEMSolver(cost,batch_size=1,num_samples=300,topk=30,n_steps=30,device='cuda',seed=74000+j)
            solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,config=plan)
            solver.solve({'pixels':history,'goal':goal,'action':torch.zeros(1,3,10)})
            ids=np.random.default_rng(74000+j).choice(300,64,replace=False);row=cost.banks[15]
            selections.append({'anchor':j,'ids':ids.tolist()})
            np.savez_compressed(out/f'public_{j:03d}.npz',ids=ids,actions=row['actions'][ids],base_cost=row['cost'][ids])
    dump(out/'candidate_ledger.json',selections);seal=digest(out/'candidate_ledger.json')
    dump(out/'selection_seal.json',{'sha256':seal,'hidden_file_existed':False})
    replay_error=0.;physical_steps=0
    for j in range(48):
        public=np.load(out/f'public_{j:03d}.npz');actions=public['actions'].reshape(64,25,2)*std+mean
        actual=[execute(env,anchors['state'][j],anchors['goal_state'][j],a,j) for a in actions]
        physical_steps+=64*25
        if j<8:
            control=execute(env,anchors['state'][j],anchors['goal_state'][j],actions[0],j);physical_steps+=25
            replay_error=max(replay_error,float(np.abs(control['states']-actual[0]['states']).max()))
        np.savez_compressed(out/f'hidden_{j:03d}.npz',**{k:np.stack([x[k] for x in actual]) for k in actual[0]})
        print('decision_bank',j,flush=True)
    if digest(out/'candidate_ledger.json')!=seal or replay_error!=0:raise ValueError('Seal or reset replay failed')
    del base;torch.cuda.empty_cache();rows=[]
    with torch.inference_mode():
        for method in METHODS:
            checkpoint=locked[method]['checkpoint']
            if digest(checkpoint)!=locked[method]['sha256']:raise ValueError('Trained checkpoint changed')
            state=torch.load(checkpoint,map_location='cpu',weights_only=False)
            model=architecture(state['config']).cuda().eval().requires_grad_(False)
            model.load_state_dict(state['state_dict'],strict=True)
            for j in range(48):
                public=np.load(out/f'public_{j:03d}.npz');hidden=np.load(out/f'hidden_{j:03d}.npz')
                history=pixels(anchors['pixels'][j:j+1]);goal=pixels(anchors['goal_pixels'][j:j+1]).unsqueeze(0)
                past=torch.tensor((anchors['past_actions'][j:j+1]-mean)/std,device='cuda').float().reshape(1,2,10)
                if j==0:dump(out/f'{method}_native_control.json',native_control(model,history,goal,past))
                cost=NativeCost(model,history,goal,past);actions=torch.tensor(public['actions'][None],device='cuda')
                terminal=cost.rollout(actions)[0];scores=cost.get_cost({},actions)[0].cpu().numpy()
                true_features=model.encode({'pixels':pixels(hidden['terminal_pixels']).unsqueeze(1)})['emb'][:,0]
                effect_mse=(terminal-true_features).square().mean(-1).cpu().numpy()
                rank=np.argsort(scores,kind='stable');oracle=np.argsort(hidden['terminal_distance'],kind='stable')
                selected=int(rank[0]);deployed=hidden['deployed_distance'];best=float(deployed.min())
                elite_mean=public['actions'][rank[:7]].mean(0).reshape(25,2)*std+mean
                mean_actual=execute(env,anchors['state'][j],anchors['goal_state'][j],elite_mean,j);physical_steps+=25
                rows.append({'method':method,'anchor':j,'source_episode':int(anchors['episode'][j]),
                    'selected_candidate_id':int(public['ids'][selected]),'selected_candidate_distance_pixels':float(deployed[selected]),
                    'best_diagnostic_candidate_distance_pixels':best,'selected_candidate_regret_pixels':float(deployed[selected])-best,
                    'selected_candidate_success':bool(hidden['success'][selected]),'oracle_bank_success':bool(hidden['success'].any()),
                    'terminal_task_elite_recall':len(set(rank[:7])&set(oracle[:7]))/7,
                    'counterfactual_terminal_latent_mse':float(effect_mse.mean()),
                    'elite_mean_success':bool(mean_actual['success']),
                    'elite_mean_signed_distance_gap_pixels':float(mean_actual['deployed_distance'])-best})
                dump(out/'rows.json',rows)
            del model;torch.cuda.empty_cache();print('decision_audit_method',method,flush=True)
    summary=[];baseline=[r for r in rows if r['method']=='NO-ADD'];bootstrap=np.random.default_rng(84000).integers(0,48,(2000,48))
    for method in METHODS:
        rr=[r for r in rows if r['method']==method];delta=np.asarray([r['selected_candidate_regret_pixels']-b['selected_candidate_regret_pixels'] for r,b in zip(rr,baseline)])
        summary.append({'method':method,'n':48,'selected_candidate_regret_pixels_mean':float(np.mean([r['selected_candidate_regret_pixels'] for r in rr])),
            'paired_regret_delta_vs_no_add_pixels':float(delta.mean()),'paired_delta_ci95':np.quantile(delta[bootstrap].mean(1),[.025,.975]).tolist(),
            'selected_candidate_successes':sum(r['selected_candidate_success'] for r in rr),'elite_mean_successes':sum(r['elite_mean_success'] for r in rr),
            'task_elite_recall_mean':float(np.mean([r['terminal_task_elite_recall'] for r in rr])),
            'terminal_latent_mse_mean':float(np.mean([r['counterfactual_terminal_latent_mse'] for r in rr]))})
    dump(out/'summary.json',summary);dump(out/'complete.json',{'completed':True,'physical_env_steps':physical_steps,'replay_max_abs':replay_error,'ledger_sha256':seal})
    env.close()


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['base-run','checkpoint','methods','output']:p.add_argument('--'+name,required=True)
    args=p.parse_args()
    try:run(args)
    except Exception as e:
        out=Path(args.output)
        if out.exists():dump(out/'failure.json',{'error':type(e).__name__,'message':str(e)})
        raise
