"""All registered E38 native episodes; separate semantics, events and returns."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runs',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    import numpy as np
    all_rows=[];manifests=[]
    for shard in range(8):
        data=json.loads((args.runs/f'e38_policy_eval_shard{shard}/summary.json').read_text())
        all_rows.extend(data['episodes']);manifests.append(data['manifest'])
    assert len(all_rows)==360
    keys=[(r['kind'],r['train_seed'],r['mode'],r['focal'],r['world_seed']) for r in all_rows]
    assert len(set(keys))==360
    ids=json.loads((args.runs/'e38_embedding_qualification/texts.json').read_text())
    # Read candidate order directly from the exact input cache, not from IDs
    # inferred by a report's independent ordering.
    import torch
    cache=torch.load(args.runs/'e38_embedding_qualification/persona_emb_correct_pool.pt',map_location='cpu',weights_only=False)
    candidates=cache['ids'];index={p:i for i,p in enumerate(candidates)}
    rows=[]
    for r in all_rows:
        q=np.load(Path(r['raw'])/'native.npz')
        p=q['state_fixed_all_persona_probabilities'].mean(0)
        f=r['focal_slot'];count=np.asarray(r['action_counts'][f]);total=r['steps']
        row={k:r[k] for k in ['kind','train_seed','mode','world_seed','focal','steps']}
        row.update(focal_return=r['return_per_agent'][f],team_return=r['team_return'],
              focal_return_per1000=r['return_per_agent'][f]*1000/total,
              team_return_per1000=r['team_return']*1000/total,
              focal_fire_rate=float(count[7]/total),focal_forward_rate=float(count[1]/total),
              focal_rotation_rate=float(count[5:7].sum()/total),focal_noop_rate=float(count[0]/total),
              focal_zap_hits=r['zap_hits'][f],focal_zap_hits_per1000=r['zap_hits'][f]*1000/total,
              focal_apples=r['apples_consumed'][f],mean_available_apples=r['mean_available_apples'],
              final_available_apples=r['final_apples_before_action'],
              semantic_aggression_contrast=float(p[index['aggressive_zapper'],7]-p[index['cooperative_sustainer'],7]),
              semantic_fast_forward_contrast=float(p[index['fast_mover'],1]-np.delete(p[:,1],index['fast_mover']).mean()),
              semantic_spinner_rotation_contrast=float(p[index['spinner'],5:7].sum()-np.delete(p[:,5:7].sum(-1),index['spinner']).mean()),
              semantic_cautious_noop_contrast=float(p[index['cautious_observer'],0]-p[index['explorer'],0]))
        predicted=r['internal_retrieval_top1']
        correct=[predicted[j]==pid for j,pid in enumerate(r['persona_ids']) if pid in r['internal_retrieval_train_ids']]
        row['internal_train_retrieval_accuracy']=float(np.mean(correct))
        rows.append(row)
    metrics=[k for k in rows[0] if k not in ['kind','train_seed','mode','world_seed','focal']]
    rng=np.random.default_rng(38091);boot=rng.integers(0,5,size=(20000,5))
    def estimate(x):
        x=np.asarray(x,dtype=float)
        return {'mean':float(x.mean()),'per_train_seed':dict(zip(map(str,range(1,6)),x.tolist())),
                'train_seed_bootstrap95':np.quantile(x[boot].mean(1),[.025,.975]).tolist()}
    groups={}
    for kind in ['correct','strong']:
        for mode in ['full','no_consist']:
            for focal in ['all']+['cooperative_sustainer','selfish_harvester','cautious_observer','aggressive_zapper','fast_mover','spinner']:
                selected=[r for r in rows if r['kind']==kind and r['mode']==mode and (focal=='all' or r['focal']==focal)]
                expected=90 if focal=='all' else 15;assert len(selected)==expected
                values={k:estimate([np.mean([r[k] for r in selected if r['train_seed']==seed]) for seed in range(1,6)]) for k in metrics}
                groups[f'{kind}_{mode}_{focal}']={'episodes':len(selected),'metrics':values}
    differences={}
    for kind in ['correct','strong']:
        for focal in ['all']+['cooperative_sustainer','selfish_harvester','cautious_observer','aggressive_zapper','fast_mover','spinner']:
            full=groups[f'{kind}_full_{focal}']['metrics'];no=groups[f'{kind}_no_consist_{focal}']['metrics']
            differences[f'{kind}_full_minus_no_{focal}']={k:estimate([full[k]['per_train_seed'][str(s)]-no[k]['per_train_seed'][str(s)] for s in range(1,6)]) for k in metrics}
    result={'episodes':360,'groups':groups,'full_minus_no':differences,
            'all_raw_reward_equals_apple_events':all(r['raw_return_equals_apple_events'] for r in all_rows),
            'all_engine_terminated':all(r['engine_terminated'] for r in all_rows),
            'interpretation':'Descriptive native episodes and causal state-fixed action response to authored input. Semantic movement anchors are explicit source claims; they are not unique utility optima or psychometric constructs.',
            'uncertainty':'5 train-seed cluster bootstrap after averaging all registered world repeats; native worlds are not byte-paired. Within-episode snapshot variation is not an independent sample.',
            'selection':'All 360 registered episodes, all five train seeds and both code assets retained; no scientific cutoff.',
            'persona_order':candidates,'source_manifests':manifests,'cloud_calls':0,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.out/'episode_metrics.json').write_text(json.dumps(rows,indent=2)+'\n')
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    for kind in ['correct','strong']:
        print(kind,{k:result['full_minus_no'][f'{kind}_full_minus_no_all'][k] for k in ['team_return','focal_return','semantic_aggression_contrast','semantic_fast_forward_contrast','internal_train_retrieval_accuracy']},flush=True)


if __name__=='__main__':main()
