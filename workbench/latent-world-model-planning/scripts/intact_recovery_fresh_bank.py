"""E18 F3: seal new episode selection before any model outcome."""
import argparse
import shutil
import h5py
import hdf5plugin
import numpy as np
import intact_published_control_v3 as a
from experience_transfer_control_audit import ROOT, read, save, sha


def main(task):
    a.setup()
    out=ROOT/f'20261005-E18-intact-fresh-bank48-{task}'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__,out/'used.py')
    seed=121000 if task=='tworoom' else 122000
    excluded=set()
    sources=[]
    try:
        files=[ROOT/f'20261002-E17-query-proposal-RTX-s0/{task}_train.json']
        if task=='tworoom':files.append(ROOT/'20261002-E16-data-compute-RTX-s0/BASE1000/data_manifest.json')
        for file in files:
            record=read(file)
            for key in ['base_episodes','evaluation_episodes','excluded_previous_episodes','excluded_episodes']:
                excluded.update(record.get(key,[]))
            sources.append(dict(path=str(file),sha256=sha(file)))
        prior=read(a.bank(task)/'ledger.json')
        excluded.update(v['episode'] for v in prior)
        sources.append(dict(path=str(a.bank(task)/'ledger.json'),sha256=sha(a.bank(task)/'ledger.json')))
        effect=ROOT/'20261004-E20-legal-effect-bank44/ledger.json'
        excluded.update(v['episode'] for v in read(effect) if v['task']==task)
        sources.append(dict(path=str(effect),sha256=sha(effect)))
        if task=='pusht':
            cached='/tmp/latent-wm-data/E14-goalpolicy-pusht-860-frozen-features/episode_ids.npy'
            excluded.update(np.load(cached).tolist())
            sources.append(dict(path=cached,sha256=sha(cached)))
        dataset='/tmp/latent-wm-data/'+('tworoom.h5' if task=='tworoom' else 'pusht_expert_train.h5')
        episode_rng,start_rng=np.random.default_rng(seed),np.random.default_rng(seed+1)
        ledger=[]
        with h5py.File(dataset) as data:
            lengths,offsets=data['ep_len'][:],data['ep_offset'][:]
            eligible=np.setdiff1d(np.flatnonzero(lengths>=86),sorted(excluded))
            assert len(eligible)>=48
            chosen=episode_rng.choice(eligible,48,replace=False)
            for j,episode in enumerate(chosen):
                span=25 if j<24 else 75
                initial=int(start_rng.integers(0,int(lengths[episode])-10-span))
                offset=int(offsets[episode])+initial
                raw=data['action'][offset:offset+10+span]
                assert raw.shape==(10+span,2) and np.isfinite(raw).all()
                commands=np.clip(raw,-1,1).astype(np.float32)
                state_key='proprio' if task=='tworoom' else 'state'
                entry=dict(anchor=j,episode=int(episode),source_initial_step=initial,goal_span=span,
                    reset_seed=seed+100+j,initial_state=data[state_key][offset].tolist(),
                    goal_state=data[state_key][offset+10+span].tolist(),warm_actions=commands[:10].tolist(),
                    clipped_source_components=int((raw!=np.clip(raw,-1,1)).sum()))
                np.save(out/f'factual_{j:03d}.npy',commands[10:])
                entry['factual_sha256']=sha(out/f'factual_{j:03d}.npy')
                ledger.append(entry)
        save(out/'selection_ledger.json',ledger)
        save(out/'config.json',dict(task=task,n=48,dataset=dataset,dataset_rehashed=False,selection_seed=seed,start_seed=seed+1,
             excluded_episodes=sorted(excluded),exclusion_sources=sources,script_sha256=sha(__file__),helper_sha256=sha(a.__file__),
             scope='New actual-reset episodes/continuation goals, independent of known local training/cache and previous fresh/effect banks. Published pretraining overlap unknown; not restoration of original dataset full hidden memory.'))
        controls=[]
        for entry in ledger:
            j=entry['anchor']
            env,history=a.restore(task,entry)
            states=[a.diagnostic(task,env)]
            for command in np.load(out/f'factual_{j:03d}.npy'):
                env.step(command)
                states.append(a.diagnostic(task,env))
            goal=np.asarray(env.agent_position.numpy() if task=='tworoom' else env._get_obs()).copy()
            goal_image=env.render().copy()
            env.close()
            entry['goal_state']=goal.tolist()
            np.save(out/f'history_{j:03d}.npy',history)
            np.save(out/f'goal_{j:03d}.npy',goal_image)
            np.save(out/f'factual_states_{j:03d}.npy',np.asarray(states))
            repeat,repeated_history=a.restore(task,entry)
            assert np.array_equal(history,repeated_history)
            repeated_states=[a.diagnostic(task,repeat)]
            for command in np.load(out/f'factual_{j:03d}.npy'):
                _,_,done,truncated,_=repeat.step(command)
                assert not truncated
                state=a.diagnostic(task,repeat)
                assert bool(done)==a.success(task,state,goal)
                repeated_states.append(state)
            assert np.array_equal(np.asarray(states),np.asarray(repeated_states))
            assert np.array_equal(goal_image,repeat.render()) and a.success(task,repeated_states[-1],goal)
            repeat.close()
            controls.append(dict(anchor=j,episode=entry['episode'],all_warm_pixels_exact=True,all_factual_states_exact=True,
                goal_pixels_exact=True,factual_native_success=True,initial_success=a.success(task,states[0],goal),
                history_sha256=sha(out/f'history_{j:03d}.npy'),goal_sha256=sha(out/f'goal_{j:03d}.npy'),
                states_sha256=sha(out/f'factual_states_{j:03d}.npy')))
            save(out/'controls.json',controls)
            print('New independent recovery bank',task,j,'factual/replay PASS',flush=True)
        save(out/'ledger.json',ledger)
        save(out/'complete.json',dict(completed=True,n=48,all_factual_replay_exact=True,
             preparation_env_steps=2*sum(10+v['goal_span'] for v in ledger)))
    except Exception as error:
        save(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--task',choices=['tworoom','pusht'],required=True)
    main(p.parse_args().task)
