"""E32 frozen-state diagnostic: useful semantic invariance vs weak role control."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.source/'research'))
    import numpy as np
    import torch
    from src.training.pcsp_trainer import PCSPActorCritic
    from src.env.v3_constants import OBS_DIM_V3_LARGE, N_ACTIONS_V3
    torch.set_num_threads(1)
    start = time.monotonic()
    roles = json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    lookup = {int(r['id']): r for r in roles}
    with np.load(args.runs/'e25_30_evaluation/no_mixed.npz') as z:
        assert z['obs'].shape == (300, 200, OBS_DIM_V3_LARGE)
        ids = z['ids'].copy(); obs = z['obs'][:, [0,20,100,199]].copy()
        world_seeds = z['world_seeds'].copy()
    assert set(map(int, ids)) == set(lookup)
    donors = {pid: [int(r['id']) for r in roles if r['occupation'] == lookup[pid]['occupation']
                   and r['big_five'] != lookup[pid]['big_five']] for pid in lookup}
    assert all(len(v) == 4 for v in donors.values())
    variants = ['canonical', 'canonical_repeat', 'reverse_clauses']
    tables = {v: np.load(args.runs/f'e26_semantic_codes/{v}.npy').astype(np.float32) for v in variants}
    input_vectors = {v: torch.from_numpy(t[ids-1]) for v,t in tables.items()}
    donor_vectors = [torch.from_numpy(tables['canonical'][[donors[int(pid)][i]-1 for pid in ids]]) for i in range(4)]
    observations = torch.from_numpy(obs.reshape(-1, OBS_DIM_V3_LARGE))
    expand = lambda e: e[:,None,:].expand(-1,4,-1).reshape(len(observations),-1)
    def js(p,q):
        m=(p+q)/2
        return (.5*((p*(p.clamp_min(1e-12).log()-m.clamp_min(1e-12).log())).sum(-1)
                    +(q*(q.clamp_min(1e-12).log()-m.clamp_min(1e-12).log())).sum(-1)))
    def cosine(a,b):
        return torch.nn.functional.cosine_similarity(a,b,dim=-1)
    raw = {}; summary = {}; hashes = {}
    for route in ['no','full']:
        folder=args.runs/f'e25_30_{route}'
        policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
        state=torch.load(folder/'policy.pt',map_location='cpu',weights_only=True)
        policy.load_state_dict(state,strict=True); policy.eval().requires_grad_(False)
        if route == 'no':
            reader_state=torch.load(args.runs/'e25_30_readout/policy.pt',map_location='cpu',weights_only=True)
            assert all(torch.equal(state[k],reader_state[k]) for k in state)
        hashes[route]=hashlib.sha256((folder/'policy.pt').read_bytes()).hexdigest()
        values={}; projected={}
        with torch.inference_mode():
            canonical_logits=policy.action_logits(observations,expand(input_vectors['canonical']))
            assert torch.equal(canonical_logits,policy.action_logits(observations,expand(input_vectors['canonical'])))
            p=canonical_logits.softmax(-1)
            for name,e in list(input_vectors.items()) + [(f'other_{i}',e) for i,e in enumerate(donor_vectors)]:
                q=policy.action_logits(observations,expand(e)).softmax(-1)
                values[name]=js(p,q).reshape(300,4).numpy()
                values[name+'_argmax']=(p.argmax(-1)!=q.argmax(-1)).reshape(300,4).numpy()
                projected[name]=cosine(policy.persona_proj(input_vectors['canonical']),policy.persona_proj(e)).numpy()
        other=np.mean([values[f'other_{i}'] for i in range(4)],axis=0)
        selectivity=np.log((values['reverse_clauses']+1e-8)/(other+1e-8))
        raw[route]={'repeat_js':values['canonical_repeat'],'reverse_js':values['reverse_clauses'],
                    'other_js':other,'log_selectivity':selectivity}
        summary[route]={
            'repeat_js':float(values['canonical_repeat'].mean()),
            'reverse_js':float(values['reverse_clauses'].mean()),
            'other_role_js':float(other.mean()),'log_selectivity':float(selectivity.mean()),
            'reverse_argmax_changed':float(values['reverse_clauses_argmax'].mean()),
            'other_argmax_changed':float(np.mean([values[f'other_{i}_argmax'].mean() for i in range(4)])),
            'projection_cosine':{k:float(v.mean()) for k,v in projected.items()}}
    unique_ids=np.asarray(sorted(lookup)); rng=np.random.default_rng(32658)
    boot=rng.integers(0,len(unique_ids),size=(20000,len(unique_ids)))
    d=raw['full']['log_selectivity']-raw['no']['log_selectivity']
    persona_means=np.asarray([d[ids==pid].mean() for pid in unique_ids])
    ci=np.quantile(persona_means[boot].mean(1),[.025,.975])
    result={'policies':summary,'full_minus_no_log_selectivity':float(d.mean()),
            'persona_cluster95':ci.tolist(),
            'other_role_js_retained_ratio':summary['full']['other_role_js']/max(summary['no']['other_role_js'],1e-12),
            'cycle_differences':{str(c):float(d[:,i].mean()) for i,c in enumerate([0,20,100,199])},
            'raw_cosine':{k:float(cosine(input_vectors['canonical'],e).mean())
                          for k,e in list(input_vectors.items())+[(f'other_{i}',e) for i,e in enumerate(donor_vectors)]},
            'samples':{'roles':100,'world_seeds':sorted(set(world_seeds.tolist())),'cycles':[0,20,100,199],'states':1200},
            'policy_sha256':hashes,'donor_ids':donors,'bootstrap_seed':32658,'bootstrap_replicates':20000,
            'world_or_reward_changed':False,'new_rollouts':0,'training_seeds':[42],
            'scope':'Frozen-state action sensitivity only. No semantic correctness, native utility, cross-training-seed or novelty claim.',
            'wall_seconds':time.monotonic()-start,'cloud_calls':0,'gpu_hours':0}
    result['input_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
        [args.runs/'e25_30_evaluation/no_mixed.npz']+[args.runs/f'e26_semantic_codes/{v}.npy' for v in variants]}
    np.savez_compressed(args.out/'per_state.npz',ids=ids,world_seeds=world_seeds,
                        **{f'{r}_{k}':v for r,x in raw.items() for k,v in x.items()})
    (args.out/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['donor_ids','input_sha256']},ensure_ascii=False),flush=True)


if __name__=='__main__': main()
