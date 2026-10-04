"""Full F2 trace audit and independent CPU verification of every local query."""
import shutil
import numpy as np
import torch
import intact_published_control_v3 as a
from intact_recovery_forks_audit_v2 import native_hits, CONDITIONS
from experience_transfer_control_audit import ROOT, WB, read, save, sha

METHODS = ['WAYPOINT-FEEDBACK','WAYPOINT-OPEN']


@torch.inference_mode()
def main():
    a.setup()
    full_forks = read(WB/'results/E18_20261005_intact_recovery_fork_results.json')
    assert full_forks['completed'] and full_forks['new_continuations']==864
    groups, counts, vectors = [],[],{}
    for task in ['tworoom','pusht']:
        net,processor,source = a.source(task,'cpu')
        before = a.state_hash(net.state_dict())
        out = ROOT/f'20261005-E18-intact-waypoints-{task}'
        assert read(out/'complete.json')==dict(completed=True,n=288,model_unchanged=True) and not (out/'failure.json').exists()
        cfg,pre,rows = read(out/'config.json'),read(out/'preflight.json'),read(out/'rows.json')
        assert cfg['source']==source and cfg['script_sha256']==sha(WB/'scripts/intact_waypoint_recovery.py')==sha(out/'used.py')
        assert cfg['helper_sha256']==sha(a.__file__) and cfg['fork_helper_sha256']==sha(WB/'scripts/intact_recovery_forks_v2.py')
        assert pre['passed'] and pre['n']==144 and pre['model_unchanged']
        assert all(v['passed'] and v['physical_query_manual_exact'] and v['goal_query_native_exact'] and v['clamped_std_exact'] for v in pre['cpu_cuda'])
        assert [v['device'] for v in pre['cpu_cuda']]==['cpu','cuda']
        base = ROOT/f'20261005-E18-intact-forks-v2-{task}'
        assert sha(base/'config.json')==cfg['base_config_sha256']
        bank = a.bank(task)
        ledger = read(bank/'ledger.json')
        assert sha(bank/'ledger.json')==cfg['bank_ledger_sha256']
        assert (cfg['methods'],cfg['conditions'],cfg['budget'],cfg['fork_step'],cfg['response_end_step'])==(METHODS,CONDITIONS,100,10,25)
        assert [(r['anchor'],r['condition'],r['method']) for r in rows]==[(j,c,m) for j in range(48) for c in CONDITIONS for m in METHODS]
        lookup = {(r['anchor'],r['condition'],r['method']):r for r in rows}
        baseline = read(base/'rows.json')
        for method in ['HOLD','REFRESH15','REFRESH5']:
            for condition in CONDITIONS:
                original = [r for r in baseline if r['condition']==condition and r['method']==method]
                assert [r['anchor'] for r in original]==list(range(48))
                vectors[task,condition,method] = np.asarray([float(r['success']) for r in original])
        checked_queries = 0
        for entry in ledger:
            j,goal = entry['anchor'],np.asarray(entry['goal_state'])
            reference_path = out/f'reference_{j:03d}.npz'
            with np.load(reference_path) as reference:
                ref,plan = reference['reference'],reference['standardized_plan']
            assert ref.shape[:2]==(1,6) and plan.shape==(25,2) and np.isfinite(ref).all() and np.isfinite(plan).all()
            for condition in CONDITIONS:
                prefix_path = base/f'prefix_{j:03d}_{condition}.npz'
                with np.load(prefix_path) as prefix:
                    prefix_state,prefix_command,prefix_applied = prefix['states'],prefix['commands'],prefix['applied']
                n = len(prefix_command)
                guard = next(g for g in pre['controls'] if (g['anchor'],g['condition'])==(j,condition))
                assert guard['all_state_pixels_exact'] and guard['reference_first3_exact']
                assert guard['prefix_sha256']==sha(prefix_path) and guard['reference_sha256']==sha(reference_path)
                if n==10 and not native_hits(task,prefix_state,goal).any():
                    with np.load(base/f'features_{j:03d}_{condition}.npz') as feature:
                        assert np.array_equal(ref[:,:3],feature['expected_embeddings']) and np.array_equal(plan,feature['initial_plan'].reshape(25,2))
                for method in METHODS:
                    row = lookup[j,condition,method]
                    path = out/f'trace_{j:03d}_{condition}_{method}.npz'
                    qpath = out/f'queries_{j:03d}_{condition}_{method}.npz'
                    assert row['trace_sha256']==sha(path) and row['queries_sha256']==sha(qpath) and row['prefix_sha256']==sha(prefix_path)
                    assert (row['episode'],row['goal_span'])==(entry['episode'],entry['goal_span'])
                    with np.load(path) as trace:
                        state,commands,applied = trace['states'],trace['commands'],trace['applied_commands']
                    total = row['env_steps']
                    assert total<=100 and state.shape==(total+1,2 if task=='tworoom' else 25) and commands.shape==applied.shape==(total,2)
                    assert np.isfinite(state).all() and np.isfinite(commands).all() and np.isfinite(applied).all()
                    assert np.array_equal(state[:n+1],prefix_state) and np.array_equal(commands[:n],prefix_command) and np.array_equal(applied[:n],prefix_applied)
                    desired = commands.astype(np.float32).copy()
                    if condition=='gain0.7':
                        desired[5:] *= .7
                    if condition=='physics' and task=='tworoom':
                        desired[5:] += np.asarray([.15,0],dtype=np.float32)
                    assert np.array_equal(desired,applied)
                    hit = native_hits(task,state,goal)
                    assert bool(hit.any())==row['success'] and bool(hit[0])==row['initial_success']
                    assert bool(native_hits(task,prefix_state,goal).any())==row['absorbed_in_common_prefix']
                    if total:
                        assert not hit[:-1].any()
                    if not row['success']:
                        assert total==100
                    if row['absorbed_in_common_prefix']:
                        assert total==n and row['decisions']==[]
                    queries = np.load(qpath)
                    cursor,offset,past = 0,n,list(entry['warm_actions'])+list(commands[:n])
                    for d in row['decisions']:
                        assert d['start_step']==offset and np.isfinite(d['solver_seconds']) and d['solver_seconds']>0
                        previous = np.asarray(past[-5:],dtype=np.float32)
                        assert np.array_equal(previous,np.asarray(d['previous_issued_commands'],dtype=np.float32))
                        proposal = np.asarray(d['standardized_proposal'],dtype=np.float32)
                        if offset<25:
                            assert offset in [10,15,20] and d['kind']=='waypoint' and proposal.shape==(5,2)
                            assert int(queries['step'][cursor])==offset
                            target,current,previous_emb = [torch.from_numpy(queries[key][cursor]) for key in ['target','current','previous']]
                            assert torch.equal(target,torch.from_numpy(ref[:,offset//5+1]))
                            if method=='WAYPOINT-OPEN':
                                assert torch.equal(current,torch.from_numpy(ref[:,offset//5]))
                            causal = torch.as_tensor(processor.transform(previous.reshape(1,1,10))).float()
                            recomputed_previous = net.action_encoder(causal)[:,-1]
                            np.testing.assert_allclose(previous_emb.numpy(),recomputed_previous.numpy(),atol=2e-4,rtol=1e-5)
                            delta = target-current
                            grammar = torch.cat([current,delta,torch.zeros_like(current),current*delta,previous_emb],-1)
                            assert torch.equal(grammar,net.inverse_actor.actor_features(current,target,previous_emb))
                            mean,log_std = net.inverse_actor.net(grammar).chunk(2,-1)
                            log_std = log_std.clamp(net.inverse_actor.min_log_std,net.inverse_actor.max_log_std)
                            np.testing.assert_allclose(mean.numpy(),queries['mean'][cursor],atol=2e-4,rtol=1e-5)
                            np.testing.assert_allclose(log_std.numpy(),queries['log_std'][cursor],atol=2e-4,rtol=1e-5)
                            assert np.array_equal(proposal,queries['mean'][cursor].reshape(5,2))
                            width = 5
                            cursor += 1
                            checked_queries += 1
                        else:
                            assert d['kind']=='common-suffix' and proposal.shape==(25,2)
                            width = min(25,100-offset)
                        used = d['executed_steps']
                        assert d['planned_execution_steps']==width and 0<used<=width
                        assert used==width or row['success']
                        assert np.array_equal(processor.scaler.inverse_transform(proposal)[:used],commands[offset:offset+used])
                        past += list(commands[offset:offset+used])
                        offset += used
                    assert offset==total and cursor==len(queries['step'])
                    queries.close()
        assert before==a.state_hash(net.state_dict())
        for condition in CONDITIONS:
            for method in METHODS:
                subset = [lookup[j,condition,method] for j in range(48)]
                vectors[task,condition,method] = np.asarray([float(r['success']) for r in subset])
                counts.append(dict(task=task,condition=condition,method=method,n=48,
                    successes=sum(r['success'] for r in subset),near_successes=sum(r['success'] for r in subset[:24]),far_successes=sum(r['success'] for r in subset[24:]),
                    initial_successes=sum(r['initial_success'] for r in subset),absorbed_common_prefix=sum(r['absorbed_in_common_prefix'] for r in subset),
                    env_steps=sum(r['env_steps'] for r in subset),response_inverse_calls=sum(d['kind']=='waypoint' for r in subset for d in r['decisions']),
                    suffix_full_plan_calls=sum(d['kind']=='common-suffix' for r in subset for d in r['decisions']),solver_seconds=sum(d['solver_seconds'] for r in subset for d in r['decisions'])))
        groups.append(dict(config=cfg,rows_sha256=sha(out/'rows.json'),preflight_sha256=sha(out/'preflight.json'),independent_cpu_queries=checked_queries,artifact_directory=str(out)))
        print('Complete waypoint source/native/causal/typed-query audit',task,'288 PASS',flush=True)
    rng = np.random.default_rng(120101)
    effects = []
    for task in ['tworoom','pusht']:
        for condition in CONDITIONS:
            for method,baseline in [(m,b) for m in METHODS for b in ['HOLD','REFRESH5']] + [('WAYPOINT-FEEDBACK','WAYPOINT-OPEN')]:
                delta = vectors[task,condition,method]-vectors[task,condition,baseline]
                for tier,ids in [('all',np.arange(48)),('near',np.arange(24)),('far',np.arange(24,48))]:
                    draws = rng.choice(ids,(10000,len(ids)),replace=True)
                    effects.append(dict(task=task,condition=condition,method=method,reference=baseline,tier=tier,n=len(ids),
                        mean_delta=float(delta[ids].mean()),helped=int((delta[ids]>0).sum()),harmed=int((delta[ids]<0).sum()),
                        paired_anchor_bootstrap_95=np.quantile(delta[draws].mean(1),[.025,.975]).tolist(),train_sources=1))
    result = dict(completed=True,new_continuations=576,matched_fork_reference_sha256=sha(WB/'results/E18_20261005_intact_recovery_fork_results.json'),
        groups=groups,counts=counts,effects=effects,script_sha256=sha(__file__),
        scope='One frozen joint source0, all48 development goals/3conditions per task; imagined5step waypoints, original local inverse head with real-current vs predicted-current. Every issued/native/shift trace and typed query audited; CPU readout independently rerun on saved input embeddings. Real-current encoder is guarded in producer/preflight, not independently re-encoded every response. References and future suffix protocol identical to auditedF1; one seed, no novelty/confirmation or optimized speed claim.')
    dest = ROOT/'20261005-E18-intact-waypoint-audit'
    assert not dest.exists()
    dest.mkdir()
    shutil.copy2(__file__,dest/'used.py')
    save(dest/'result.json',result)
    result['full_audit_artifact'] = str(dest/'result.json')
    save(WB/'results/E18_20261005_intact_waypoint_recovery_results.json',result)


if __name__=='__main__':
    main()
