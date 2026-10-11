"""E18: matched full-prefix replays for hold, feedback and extra search."""
import argparse
import copy
import json
from pathlib import Path
import numpy as np
import torch
from first_wave import native_info, restore, sha256, write_json, sync_time, simulator_state, image_tensor
from closed_loop import wilson


class MacroCost:
    def __init__(self,model,initial,goal):self.model,self.initial,self.goal=model,initial,goal;self.scores=None;self.calls=0

    def terminal(self,actions):
        b,s,h,d=actions.shape
        x=self.initial[:,None].expand(b,s,1,192).reshape(b*s,1,192)
        a=actions.reshape(b*s,h,5,10)
        for t in range(h):
            act=self.model.action_encoder(a[:,t],latent=x,return_last_only=True)
            x=self.model.predict(x,act)[:,-1:]
        return x.reshape(b,s,192)

    def get_cost(self,info,actions):
        scores=(self.terminal(actions)-self.goal[:,-1:, :]).square().sum(-1)
        self.scores=scores[0].cpu().numpy();self.calls+=1
        return scores


def controls(model,info,initial,goal):
    rows=[]
    for horizon in [1,2,3]:
        a=torch.randn(1,17,horizon,50,device='cuda',generator=torch.Generator(device='cuda').manual_seed(79000+horizon))
        # Direct native scoring needs an explicit candidate axis, normally added
        # by CEMSolver; encoder-only inputs intentionally lack that axis.
        native={k:v.unsqueeze(1).clone() for k,v in info.items()};native['consistency_loss_weight']=0.
        expected=model.get_cost(native,a);actual=MacroCost(model,initial,goal).get_cost({},a)
        error=float((expected-actual).abs().max())
        if not torch.allclose(expected,actual,atol=1e-5,rtol=1e-5):raise ValueError(f'Native H{horizon} mismatch {error}')
        rows.append({'horizon_macro':horizon,'forecast_primitive_steps':25*horizon,'max_cost_abs_error':error})
    return rows


def solve(model,initial,goal,env,horizon,n,seed):
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    cost=MacroCost(model,initial,goal)
    solver=swm.solver.CEMSolver(cost,batch_size=1,num_samples=n,topk=30,n_steps=30,device='cuda',seed=seed)
    solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,
        config=swm.PlanConfig(horizon=horizon,receding_horizon=horizon,action_block=25,warm_start=True))
    dummy={'pixels':torch.zeros(1,1,1,3,1,1,device='cuda'),'goal':torch.zeros(1,1,1,3,1,1,device='cuda'),
           'action':torch.zeros(1,1,2,device='cuda')}
    begin=sync_time();result=solver.solve(dummy);seconds=sync_time()-begin
    actions=result['actions'].to(device='cuda').reshape(1,1,horizon,50)
    if actions.numel()!=horizon*50:raise ValueError('Incorrect CEM action horizon')
    score=np.sort(cost.scores)
    return actions,{'seconds':seconds,'calls':cost.calls,'candidate_evaluations':n*cost.calls,
                   'elite_cutoff_margin':float(score[30]-score[29])}


def task_distance(env,task):
    if task=='tworoom':return float(np.linalg.norm(env._get_info()['proprio']-env._get_info()['goal_state']))
    return float(env.eval_state(env.goal_state,env._get_obs())[1])


def execute(env,task,actions,gain,start_step,capture=False):
    success=False;return_sum=0.;steps=0
    images=[env.render()] if capture else []
    for i,a in enumerate(actions):
        scale=gain if start_step+i>=10 else 1.
        _,reward,done,truncated,_=env.step(a*scale);steps+=1;return_sum+=float(reward)
        if capture and steps%5==0:images.append(env.render())
        if done or truncated:success=bool(done);break
    result={'success':success,'steps':steps,'native_return':return_sum,'native_task_distance':task_distance(env,task)}
    if capture:result['prefix_images']=np.asarray(images)
    return result


def adapt(model,images,commands,norm,mode):
    # All labels are observations before the fork. No shift parameter is given.
    with torch.inference_mode(False),torch.enable_grad():
        updated=copy.deepcopy(model).eval().requires_grad_(False)
        parts=[updated.action_encoder]+([updated.predictor] if mode=='SHORT-DYNAMICS' else [])
        for part in parts:part.requires_grad_(True)
        parameters=[p for p in updated.parameters() if p.requires_grad]
        feat=model.encode({'pixels':image_tensor(images).unsqueeze(0).cuda()})['emb']
        if feat.ndim!=3 or feat.shape[:2]!=(1,6):raise ValueError(f'Expected 6 pre-fork images, got {feat.shape}')
        initial,target=feat[0,2:5,None].clone(),feat[0,3:6,None].clone()
        action=torch.tensor((commands[10:25]-norm['mean'])/norm['std'],device='cuda').float().reshape(3,1,10)
        optimizer=torch.optim.AdamW(parameters,lr=5e-5,weight_decay=1e-3);losses=[];begin=sync_time()
        for step in range(16):
            optimizer.zero_grad(set_to_none=True)
            emb=updated.action_encoder(action,latent=initial,return_last_only=True)
            prediction=updated.predict(initial,emb)[:,-1:];loss=(prediction-target).square().mean()
            if not torch.isfinite(loss):raise ValueError('Nonfinite short adaptation loss')
            loss.backward();torch.nn.utils.clip_grad_norm_(parameters,1.);optimizer.step();losses.append(float(loss))
        updated.eval().requires_grad_(False)
    return updated,{'gradient_steps':16,'updated_parameters':sum(p.numel() for p in parameters),
                    'seconds':sync_time()-begin,'losses':losses,'data':'last3 pre-fork 5-step transitions only'}


def run(args):
    import gymnasium as gym
    import stable_worldmodel
    torch.set_num_threads(4);torch.manual_seed(77000)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False);rows=[];replay_max=0.;pixel_max=0.;physical_steps=0
    methods=['HOLD','PREDICTED-REPLAN','FEEDBACK','EXTRA-REPLAN']
    if args.short_updates:methods+=['SHORT-HEAD','SHORT-DYNAMICS']
    source_configs=[json.loads((Path(s)/'config.json').read_text()) for s in args.sources]
    if args.reference:
        reference=Path(args.reference)
        if not (reference/'complete.json').exists():raise ValueError('Reference must be complete')
        ref_config=json.loads((reference/'config.json').read_text())
        if ref_config['sources']!=source_configs or ref_config['args']['prepared']!=args.prepared:
            raise ValueError('Reference checkpoint/data mismatch')
    write_json(out/'config.json',{'args':vars(args),'sources':source_configs,'methods':methods,'gains':[1.,.7],
        'shift_onset_primitive_step':10,'count_per_task':32,'seed':77000,'harness_sha256':sha256(__file__),
        'hardware':torch.cuda.get_device_name(),'timing_scope':'ambient GPU occupancy must be audited; model-call counts recorded',
        'scope':'one released checkpoint/task; no router trained; feedback and replan are separate from parameter adaptation'})
    (out/'recovery_forks_used.py').write_text(Path(__file__).read_text())
    with torch.inference_mode():
        for source,cfg in zip(args.sources,source_configs):
            task=cfg['task'];model=torch.load(cfg['checkpoint'],map_location='cpu',weights_only=False).cuda().eval().requires_grad_(False)
            norm=np.load(Path(source)/'action_normalization.npz');anchors=np.load(Path(args.prepared)/f'{task}_g75.npz')
            env=gym.make('swm/TwoRoom-v1' if task=='tworoom' else 'swm/PushT-v1',render_mode='rgb_array').unwrapped
            if task=='pusht' and not env.relative:raise ValueError('Action gain requires relative PushT controls')
            for j in range(32):
                anchor={'state':anchors['state'][j],'goal_state':anchors['goal_state'][j]};reset_seed=77000+j
                restore(env,anchor,reset_seed);info=native_info(env.render(),anchors['goal_pixels'][j])
                initial=model.encode({'pixels':info['pixels'].cuda()})['emb'];goal=model.encode({'pixels':info['goal'].cuda()})['emb']
                if j==0:write_json(out/f'{task}_native_control.json',controls(model,info,initial,goal))
                if args.reference:
                    reference=Path(args.reference);nominal=np.load(reference/f'{task}_initial_plan_{j:03d}.npy')
                    prior=json.loads((reference/'rows.json').read_text())
                    initial_search=next(r['initial_search'] for r in prior if r['task']==task and r['anchor']==j)
                    if nominal.shape!=(75,2):raise ValueError('Reference plan length mismatch')
                    planned=torch.tensor((nominal-norm['mean'])/norm['std'],device='cuda').float().reshape(1,1,3,50)
                else:
                    planned,initial_search=solve(model,initial,goal,env,3,300,77000+j*100)
                    nominal=planned[0,0].cpu().numpy().reshape(75,2)*norm['std']+norm['mean']
                np.save(out/f'{task}_initial_plan_{j:03d}.npy',nominal)
                predicted=MacroCost(model,initial,goal).terminal(planned[:,:,:1])
                for gain in [1.,.7]:
                    restore(env,anchor,reset_seed);prefix=execute(env,task,nominal[:25],gain,0,capture=args.short_updates);physical_steps+=prefix['steps']
                    fork_state=simulator_state(env,env._get_info());fork_pixels=env.render();fork_distance=task_distance(env,task)
                    observed=model.encode({'pixels':native_info(fork_pixels,anchors['goal_pixels'][j])['pixels'].cuda()})['emb']
                    features={'prediction_observation_latent_mse':float((predicted-observed).square().mean()),
                        'visible_goal_latent_progress':float((initial-goal).square().sum()-(observed-goal).square().sum()),
                        'initial_elite_cutoff_margin':initial_search['elite_cutoff_margin']} if not prefix['success'] else None
                    # Features are sealed before any method's future outcome exists.
                    write_json(out/f'{task}_features_{j:03d}_gain{gain}.json',features)
                    for method in methods:
                        adaptation=None
                        restore(env,anchor,reset_seed);repeat=execute(env,task,nominal[:25],gain,0);physical_steps+=repeat['steps']
                        error=float(np.abs(simulator_state(env,env._get_info())-fork_state).max())
                        pixel=float(np.abs(env.render().astype(float)-fork_pixels).max());replay_max=max(replay_max,error);pixel_max=max(pixel_max,pixel)
                        if error!=0 or pixel!=0:raise ValueError('Full-prefix fork replay mismatch')
                        if prefix['success']:
                            result={'success':True,'steps':0,'native_return':0.,'native_task_distance':fork_distance};search=None
                        else:
                            if method=='HOLD':remaining=nominal[25:];search=None
                            else:
                                state=predicted if method=='PREDICTED-REPLAN' else observed
                                current=model
                                if method.startswith('SHORT-'):
                                    current,adaptation=adapt(model,prefix['prefix_images'],nominal[:25],norm,method)
                                a,search=solve(current,state,goal,env,2,900 if method=='EXTRA-REPLAN' else 300,77001+j*100)
                                remaining=a[0,0].cpu().numpy().reshape(50,2)*norm['std']+norm['mean']
                                if current is not model:del current
                            result=execute(env,task,remaining,gain,25);physical_steps+=result['steps']
                        rows.append({'task':task,'anchor':j,'source_episode':int(anchors['episode'][j]),'condition_gain':gain,
                            'method':method,'absorbed_before_fork':prefix['success'],'prefix_steps':prefix['steps'],
                            'deployment_features':features,'initial_search':initial_search,'additional_search':search,'adaptation':adaptation,
                            'fork_native_task_distance':fork_distance,**result})
                        write_json(out/'rows.json',rows)
                    print('recovery_fork',task,j,gain,flush=True)
            env.close();del model;torch.cuda.empty_cache()
    summary=[];bootstrap=np.random.default_rng(87000).integers(0,32,(2000,32))
    for task in ['tworoom','pusht']:
        for gain in [1.,.7]:
            subset=[r for r in rows if r['task']==task and r['condition_gain']==gain];hold=[r for r in subset if r['method']=='HOLD']
            for method in methods:
                data=[r for r in subset if r['method']==method]
                success=np.array([int(r['success'])-int(b['success']) for r,b in zip(data,hold)])
                utility=np.array([b['native_task_distance']-r['native_task_distance'] for r,b in zip(data,hold)])
                s=sum(r['success'] for r in data)
                summary.append({'task':task,'gain':gain,'method':method,'n':32,'successes':s,'success_wilson_ci95':wilson(s,32),
                    'helped':int(sum(success>0)),'harmed':int(sum(success<0)),
                    'paired_success_gain_vs_hold':float(success.mean()),'paired_success_ci95':np.quantile(success[bootstrap].mean(1),[.025,.975]).tolist(),
                    'paired_native_distance_utility_gain':float(utility.mean()),'paired_distance_ci95':np.quantile(utility[bootstrap].mean(1),[.025,.975]).tolist(),
                    'additional_candidate_evaluations':sum(r['additional_search']['candidate_evaluations'] for r in data if r['additional_search']),
                    'absorbed_before_fork':sum(r['absorbed_before_fork'] for r in data)})
    write_json(out/'summary.json',summary);write_json(out/'complete.json',{'completed':True,'physical_env_steps':physical_steps,
        'fork_state_replay_max_abs':replay_max,'fork_pixel_replay_max_abs':pixel_max})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sources',nargs='+',required=True);p.add_argument('--prepared',required=True);p.add_argument('--output',required=True)
    p.add_argument('--short-updates',action='store_true');p.add_argument('--reference')
    args=p.parse_args()
    try:run(args)
    except Exception as e:
        out=Path(args.output)
        if out.exists():write_json(out/'failure.json',{'error':type(e).__name__,'message':str(e)})
        raise
