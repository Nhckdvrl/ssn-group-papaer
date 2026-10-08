"""H2A independent replay, manual visual queries and non-oracle proposal audit."""
import shutil
import numpy as np
import torch
import intact_published_control_v3 as a
import controller_consequence_audit as independent
from experience_transfer_control_audit import ROOT, WB, read, save, sha


@torch.inference_mode()
def run():
    a.setup()
    for task in ['tworoom', 'pusht']:
        assert read(ROOT/f'20261005-E14-fixed-controller-experience-{task}/complete.json')['n'] == 1632
    out = ROOT/'20261005-E14-fixed-controller-experience-audit'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__, out/'used.py')
    try:
        groups, summary = [], []
        for task in ['tworoom', 'pusht']:
            folder = ROOT/f'20261005-E14-fixed-controller-experience-{task}'
            cfg, pre, proposals, rows = [read(folder/name) for name in ['config.json', 'preflight.json', 'candidates.json', 'rows.json']]
            assert not (folder/'failure.json').exists() and pre['passed']
            assert cfg['script_sha256'] == sha(folder/'used.py') == sha(WB/'scripts/fixed_controller_experience.py')
            assert cfg['actor_helper_sha256'] == sha(a.__file__) and cfg['collector_ignores_done']
            assert cfg['candidates_sha256'] == sha(folder/'candidates.json') and cfg['memory_images_sha256'] == sha(folder/'memory_images.npy') and cfg['memory_latents_sha256'] == sha(folder/'memory_latents.npy')
            bank = ROOT/f'20261005-E18-intact-fresh-bank48-{task}'
            ledger = read(bank/'ledger.json')
            assert cfg['source_ledger_sha256'] == sha(bank/'ledger.json') and cfg['source_bank'] == str(bank)
            images, latent, memory = np.load(folder/'memory_images.npy'), np.load(folder/'memory_latents.npy'), read(folder/'memory.json')
            assert all(m['train_source_anchor'] < 32 for m in memory)
            assert [(r['anchor'],r['candidate'],r['method']) for r in rows] == [(j,c,m) for j in range(48) for c in range(17) for m in ['OPEN25','GOAL5']]
            net, processor, source = a.source(task, 'cuda')
            assert source == cfg['source']
            prior_bank = ROOT/f'20261005-E14-controller-consequence-{task}'
            prior_result = read(WB/'results/E14_20261005_controller_consequence_results.json')
            group = next(g for g in prior_result['groups'] if g['config']['task'] == task)
            assert group['rows_sha256'] == sha(prior_bank/'rows.json')
            prior_rows = {(r['anchor'],r['goal_branch'],r['method']):r for r in read(prior_bank/'rows.json')}
            import hashlib
            for k,m in enumerate(memory):
                assert m['id'] == k and m['pixel_sha256'] == hashlib.sha256(images[k].tobytes()).hexdigest()
                old_trace = prior_bank/f"trace_{m['train_source_anchor']:03d}_g{m['source_branch']:02d}_OPEN25.npz"
                assert sha(old_trace) == prior_rows[m['train_source_anchor'],m['source_branch'],'OPEN25']['trace_sha256']
                with np.load(old_trace) as raw:
                    assert np.array_equal(images[k],raw['goal_image'])
                encoded = net.encode(dict(pixels=a.pixels(images[k:k+1,None], 'cuda')))['emb'][0,0].cpu().numpy()
                assert np.array_equal(encoded,latent[k])
            weight_sha = a.state_hash(net.state_dict())
            visual_queries = 0
            vector = {m:dict(anytime=np.zeros((48,17),bool), macro=np.zeros((48,17),bool), terminal=np.zeros((48,17),bool)) for m in ['OPEN25','GOAL5']}
            for j, entry in enumerate(ledger):
                proposal = proposals[j]
                assert proposal['anchor'] == j and proposal['episode'] == entry['episode'] and proposal['task_goal_state'] == entry['goal_state']
                final_goal = np.load(bank/f'goal_{j:03d}.npy')
                assert proposal['final_goal_sha256'] == sha(bank/f'goal_{j:03d}.npy')
                zgoal = net.encode(dict(pixels=a.pixels(final_goal[None,None], 'cuda')))['emb'][0,0].cpu().numpy()
                eligible = np.asarray([k for k,m in enumerate(memory) if m['pixel_sha256'] != hashlib.sha256(final_goal.tobytes()).hexdigest()])
                distances = ((latent-zgoal)**2).mean(-1)
                nearest = eligible[np.argsort(distances[eligible],kind='stable')[:8]]
                remaining = np.setdiff1d(eligible,nearest)
                uniform = np.random.default_rng(cfg['proposal_seed']+j).choice(remaining,8,replace=False)
                assert proposal['memory_ids'] == [-1]+nearest.tolist()+uniform.tolist()
                common_state, common_pixels = None, None
                paired = {}
                for candidate, mid in enumerate(proposal['memory_ids']):
                    query_goal = final_goal if mid == -1 else images[mid]
                    for method in ['OPEN25','GOAL5']:
                        row = rows[(j*17+candidate)*2+(method=='GOAL5')]
                        assert row['memory_id'] == mid and row['env_steps'] == 25
                        path = folder/f'trace_{j:03d}_c{candidate:02d}_{method}.npz'
                        assert row['trace_sha256'] == sha(path)
                        with np.load(path) as raw:
                            states, commands, obs, native = [raw[k].copy() for k in ['states','commands','observations','native_final_goal_hits']]
                        assert states.shape == (26,10 if task=='tworoom' else 25) and commands.shape == (25,2) and obs.shape == (6,224,224,3)
                        assert np.isfinite(states).all() and np.isfinite(commands).all()
                        evaluated = independent.native_hits(task,states,np.asarray(entry['goal_state']))
                        assert np.array_equal(evaluated,native) and row['native_success_anytime'] == bool(native.any()) and row['initial_success'] == bool(native[0])
                        vector[method]['anytime'][j,candidate] = native.any()
                        vector[method]['macro'][j,candidate] = native[::5].any()
                        vector[method]['terminal'][j,candidate] = native[-1]
                        env, warm = a.restore(task,entry)
                        assert np.array_equal(warm,np.load(bank/f'history_{j:03d}.npy'))
                        if common_state is None:
                            common_state, common_pixels = states[0], obs[0]
                        assert np.array_equal(common_state,states[0]) and np.array_equal(common_pixels,obs[0])
                        assert np.array_equal(independent.diagnostic(task,env),states[0]) and np.array_equal(env.render(),obs[0])
                        if task=='pusht':
                            assert np.array_equal(env.goal_state,np.asarray(entry['goal_state']))
                        else:
                            assert np.array_equal(states[:,2:4],np.repeat(np.asarray(entry['goal_state'])[None],26,0))
                        for k,command in enumerate(commands):
                            _,_,done,truncated,_ = env.step(command.astype(np.float32))
                            assert not truncated and bool(done) == bool(native[k+1])
                            assert np.array_equal(independent.diagnostic(task,env),states[k+1])
                            if (k+1)%5==0:
                                assert np.array_equal(env.render(),obs[(k+1)//5])
                        env.close()
                        previous = list(entry['warm_actions'])
                        for decision in row['decisions']:
                            offset = decision['step']
                            assert np.array_equal(np.asarray(decision['previous_issued_commands'],dtype=np.float32),np.asarray(previous[-5:],dtype=np.float32))
                            inputs = a.info(obs[offset//5],query_goal,previous,processor,'cuda')
                            z = net.encode(dict(pixels=inputs['pixels']))['emb']
                            goal = net.encode(dict(pixels=inputs['goal']))['emb'][:,-1]
                            actions = inputs['action'].clone()
                            expected = []
                            for _ in range(5 if method=='OPEN25' else 1):
                                mu,_ = independent.mean(net,z[:,-1],goal,net.action_encoder(actions[:,-1:])[:,-1])
                                expected.append(mu)
                                z,actions = independent.append(net,z,actions,mu)
                            plan = torch.stack(expected,1).cpu().numpy().reshape(-1,2)
                            assert np.array_equal(plan,np.asarray(decision['standardized_proposal'],dtype=np.float32))
                            assert np.array_equal(processor.scaler.inverse_transform(plan),commands[offset:offset+len(plan)])
                            previous += list(commands[offset:offset+len(plan)])
                            visual_queries += 1
                        if method=='OPEN25':
                            paired[candidate] = commands[:5]
                        else:
                            assert np.array_equal(paired[candidate],commands[:5])
                if j%8==7:
                    print('H2 full physical/visual/candidate audit',task,j+1,'/48',flush=True)
            assert weight_sha == a.state_hash(net.state_dict())
            for method in vector:
                for tier, ids in [('ALL',np.arange(48)),('NEAR',np.arange(24)),('FAR',np.arange(24,48))]:
                    summary.append(dict(task=task,method=method,tier=tier,unique_anchors=len(ids),final_only_anytime=int(vector[method]['anytime'][ids,0].sum()),memory_oracle_anytime=int(vector[method]['anytime'][ids,1:].any(1).sum()),all_oracle_anytime=int(vector[method]['anytime'][ids].any(1).sum()),all_oracle_macro_prefix=int(vector[method]['macro'][ids].any(1).sum()),all_oracle_terminal=int(vector[method]['terminal'][ids].any(1).sum()),scope='Offline support over sealed TRAIN-memory/known-final queries, fixed25. Retains initial successes; no deployable oracle.'))
            groups.append(dict(config=cfg,visual_queries=visual_queries,rows_sha256=sha(folder/'rows.json'),passed=True))
        result = dict(completed=True,physical_trajectories=3264,forced_env_steps=81600,groups=groups,support=summary,script_sha256=sha(__file__),raw_artifact=str(out),scope='Every primitive full state/pixel replay and visual/manual actor query; all candidates rederived without new outcomes. Forced25 collection is distinct from native-absorbing evaluation. One source0/development48 per task; no trained method claim.')
        save(out/'result.json',result)
        save(WB/'results/E14_20261005_fixed_controller_experience_audit.json',result)
    except Exception as error:
        save(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
        raise


if __name__=='__main__':
    run()
