"""E18 F2: use existing physical intent readout to track imagined references."""
import argparse
import shutil
import time
import numpy as np
import torch
import intact_published_control_v3 as a
import intact_recovery_forks_v2 as f
from experience_transfer_control_audit import ROOT, read, save, sha

METHODS = ['WAYPOINT-FEEDBACK', 'WAYPOINT-OPEN']


def query(net, current, target, previous):
    stats = net.inverse_action_parameters(current, target, previous)
    delta = target-current
    grammar = torch.cat([current,delta,torch.zeros_like(current),current*delta,previous],-1)
    assert torch.equal(grammar,net.inverse_actor.actor_features(current,target,previous))
    mean,raw_log_std = net.inverse_actor.net(grammar).chunk(2,-1)
    assert torch.equal(mean,stats['map_mean'])
    assert torch.equal(raw_log_std.clamp(net.inverse_actor.min_log_std,net.inverse_actor.max_log_std),stats['log_std'])
    return stats


def reference(net, info, plan):
    emb = net.encode(dict(pixels=info['pixels']))['emb']
    past = info['action'].clone()
    states = [emb[:,-1].clone()]
    for k in range(5):
        emb,past = net.rollout_one_step(emb,plan[:,k],past,history_size=net.predictor.pos_embedding.size(1))
        states.append(emb[:,-1].clone())
    return torch.stack(states,1)


@torch.inference_mode()
def run(task):
    a.setup()
    out = ROOT/f'20261005-E18-intact-waypoints-{task}'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__,out/'used.py')
    try:
        net,scaler,source = a.source(task,'cuda')
        before = a.state_hash(net.state_dict())
        base = ROOT/f'20261005-E18-intact-forks-v2-{task}'
        pre = read(base/'preflight.json')
        assert pre['passed'] and pre['source']==source and pre['script_sha256']==sha(f.__file__)
        bank = a.bank(task)
        ledger = read(bank/'ledger.json')
        native = read(ROOT/f'20261005-E01-intact-v3-{task}-native-control/rows.json')
        tests = []
        entry = ledger[0]
        image = np.load(bank/'history_000.npy')[-1]
        goal_image = np.load(bank/'goal_000.npy')
        for device in ['cpu','cuda']:
            model,processor,meta = a.source(task,device)
            assert meta==source
            initial = a.state_hash(model.state_dict())
            info = a.info(image,goal_image,entry['warm_actions'],processor,device)
            plan = model.get_action(info,horizon=5)
            ref = reference(model,info,plan)
            goal = model.encode(dict(pixels=info['goal']))['emb'][:,-1]
            previous = model.action_encoder(info['action'])[:,-1]
            global_stats = query(model,ref[:,0],goal,previous)
            local_stats = query(model,ref[:,0],ref[:,1],previous)
            assert torch.equal(global_stats['map_mean'],plan[:,0])
            values = torch.cat([global_stats['map_mean'],global_stats['log_std'],local_stats['map_mean'],local_stats['log_std']],-1).cpu().numpy()
            if device=='cpu':
                cpu_values = values
            else:
                np.testing.assert_allclose(values,cpu_values,atol=2e-4,rtol=1e-5)
            assert initial==a.state_hash(model.state_dict())
            tests.append(dict(device=device,passed=True,goal_query_native_exact=True,physical_query_manual_exact=True,clamped_std_exact=True,model_unchanged=True))
        prepared,guards = [],[]
        for entry in ledger:
            j = entry['anchor']
            goal_image = np.load(bank/f'goal_{j:03d}.npy')
            info = a.info(np.load(bank/f'history_{j:03d}.npy')[-1],goal_image,entry['warm_actions'],scaler,'cuda')
            plan,_ = f.call(net,info)
            raw_plan = plan.cpu().numpy().reshape(25,2)
            if not native[j]['initial_success']:
                assert np.array_equal(raw_plan,np.asarray(native[j]['decisions'][0]['standardized_proposal'],dtype=np.float32))
            ref = reference(net,info,plan)
            arrays = out/f'reference_{j:03d}.npz'
            np.savez_compressed(arrays,reference=ref.cpu().numpy(),standardized_plan=raw_plan)
            for condition in f.CONDITIONS:
                expected = np.load(base/f'prefix_{j:03d}_{condition}.npz')
                env,record = f.prefix(task,entry,scaler.scaler.inverse_transform(raw_plan),condition)
                for key in ['states','commands','applied','observations','current']:
                    assert np.array_equal(record[key],expected[key])
                env.close()
                if not record['reached']:
                    with np.load(base/f'features_{j:03d}_{condition}.npz') as features:
                        assert np.array_equal(ref[:,:3].cpu().numpy(),features['expected_embeddings'])
                        assert np.array_equal(raw_plan,features['initial_plan'].reshape(25,2))
                expected.close()
                guards.append(dict(anchor=j,condition=condition,all_state_pixels_exact=True,reference_first3_exact=True,
                    prefix_sha256=sha(base/f'prefix_{j:03d}_{condition}.npz'),reference_sha256=sha(arrays)))
            prepared.append((raw_plan,ref))
        assert before==a.state_hash(net.state_dict())
        save(out/'preflight.json',dict(passed=True,n=144,cpu_cuda=tests,controls=guards,model_unchanged=True))
        save(out/'config.json',dict(task=task,methods=METHODS,conditions=f.CONDITIONS,budget=100,fork_step=10,response_end_step=25,
            source=source,script_sha256=sha(__file__),helper_sha256=sha(a.__file__),fork_helper_sha256=sha(f.__file__),
            bank_ledger_sha256=sha(bank/'ledger.json'),base_config_sha256=sha(base/'config.json'),hardware=torch.cuda.get_device_name(),
            scope='Frozen full joint source0/local inverse mean; same matched 15step window and EX25 suffix. References are imagined, no privileged or true future input. One trainseed/development goals; not original RWM or new adaptive tracking claim.'))
        rows = []
        for entry,(plan,ref) in zip(ledger,prepared):
            j,goal = entry['anchor'],np.asarray(entry['goal_state'])
            goal_image = np.load(bank/f'goal_{j:03d}.npy')
            for condition in f.CONDITIONS:
                for method in METHODS:
                    env,record = f.prefix(task,entry,scaler.scaler.inverse_transform(plan),condition)
                    expected = np.load(base/f'prefix_{j:03d}_{condition}.npz')
                    for key in ['states','commands','applied','observations','current']:
                        assert np.array_equal(record[key],expected[key])
                    expected.close()
                    states,commands,applied = list(record['states']),list(record['commands']),list(record['applied'])
                    past = list(entry['warm_actions'])+list(commands)
                    reached,decisions = record['reached'],[]
                    query_records = []
                    while not reached and len(commands)<100:
                        step = len(commands)
                        previous_raw = np.asarray(past[-5:],dtype=np.float32)
                        if step < 25:
                            index = step//5
                            assert step in [10,15,20]
                            torch.cuda.synchronize()
                            tick = time.perf_counter()
                            previous = torch.as_tensor(scaler.transform(previous_raw.reshape(1,1,10)),device='cuda').float()
                            previous = net.action_encoder(previous)[:,-1]
                            current = (net.encode(dict(pixels=a.pixels(env.render()[None,None],'cuda')))['emb'][:,-1]
                                       if method=='WAYPOINT-FEEDBACK' else ref[:,index])
                            target = ref[:,index+1]
                            stats = query(net,current,target,previous)
                            proposal = stats['map_mean'].cpu().numpy().reshape(5,2)
                            torch.cuda.synchronize()
                            seconds = time.perf_counter()-tick
                            query_records.append(dict(step=step,current=current.cpu().numpy(),target=target.cpu().numpy(),
                                previous=previous.cpu().numpy(),mean=stats['map_mean'].cpu().numpy(),log_std=stats['log_std'].cpu().numpy()))
                            width,kind = 5,'waypoint'
                        else:
                            inputs = a.info(env.render().copy(),goal_image,past,scaler,'cuda')
                            tensor,seconds = f.call(net,inputs)
                            proposal = tensor.cpu().numpy().reshape(25,2)
                            width,kind = min(25,100-step),'common-suffix'
                        issued = scaler.scaler.inverse_transform(proposal)[:width]
                        used = 0
                        for command in issued:
                            state,actual,done = f.advance(task,env,command,condition,len(commands))
                            reached = a.success(task,state,goal)
                            assert done==reached
                            commands.append(command)
                            applied.append(actual)
                            past.append(command)
                            states.append(state)
                            used += 1
                            if reached:
                                break
                        decisions.append(dict(start_step=step,kind=kind,planned_execution_steps=width,executed_steps=used,
                            previous_issued_commands=previous_raw.tolist(),standardized_proposal=proposal.tolist(),solver_seconds=seconds))
                    env.close()
                    path = out/f'trace_{j:03d}_{condition}_{method}.npz'
                    np.savez_compressed(path,states=np.asarray(states),commands=np.asarray(commands).reshape(-1,2),applied_commands=np.asarray(applied).reshape(-1,2))
                    qpath = out/f'queries_{j:03d}_{condition}_{method}.npz'
                    if query_records:
                        np.savez_compressed(qpath,**{key:np.asarray([r[key] for r in query_records]) for key in query_records[0]})
                    else:
                        np.savez_compressed(qpath,step=np.asarray([],dtype=np.int64))
                    rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],condition=condition,method=method,
                        success=reached,initial_success=record['initial_success'],absorbed_in_common_prefix=record['reached'],
                        env_steps=len(commands),decisions=decisions,trace_sha256=sha(path),queries_sha256=sha(qpath),
                        prefix_sha256=sha(base/f'prefix_{j:03d}_{condition}.npz')))
                    save(out/'rows.json',rows)
                print('INTACT both-waypoint fork',task,j,condition,'COMPLETE',flush=True)
        assert len(rows)==288 and before==a.state_hash(net.state_dict())
        save(out/'complete.json',dict(completed=True,n=288,model_unchanged=True))
    except Exception as error:
        save(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--task',choices=['tworoom','pusht'],required=True)
    run(p.parse_args().task)
