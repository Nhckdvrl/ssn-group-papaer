#!/usr/bin/env python3
"""E19 standard conditional-policy likelihood, same cached focal actions/IDs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--policy-seed',type=int,default=42)
    args=ap.parse_args();sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    import torch
    from src.env.v3_constants import OBS_DIM_V3_LARGE,N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic
    torch.set_num_threads(1)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    args.out.mkdir(parents=True,exist_ok=False)
    dump=lambda f,v:Path(f).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    records=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    candidate_ids=np.asarray([int(r['id']) for r in records])
    raw=np.load(args.source/'results/embeddings/persona_embeddings_500.npy').astype(np.float32)
    embeddings=torch.from_numpy(raw[candidate_ids-1]).to(device)
    results={};start=time.monotonic()
    for mode in ['full','no_consist']:
        policy_file=args.source/f'research/results/pcsp_v3_large/{mode}_seed{args.policy_seed}/{mode}/policy.pt'
        policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
        policy.load_state_dict(torch.load(policy_file,map_location='cpu',weights_only=True),strict=True)
        policy.to(device).eval().requires_grad_(False)
        with np.load(args.data/f'{mode}_test.npz') as source:
            observations,actions,labels=source['obs'],source['actions'],source['ids']
            rows=[]
            for index,(obs,chosen,label) in enumerate(zip(observations,actions,labels)):
                obs=torch.from_numpy(obs).to(device);act=torch.from_numpy(chosen).to(device)
                n=len(obs);scores=[]
                with torch.inference_mode():
                    # Fixed candidate chunk: no budget/ordering chosen from scores.
                    for offset in range(0,len(candidate_ids),10):
                        chunk=embeddings[offset:offset+10];size=len(chunk)
                        states=obs.unsqueeze(0).expand(size,-1,-1).reshape(size*n,-1)
                        codes=chunk.unsqueeze(1).expand(-1,n,-1).reshape(size*n,-1)
                        logp=policy.action_logits(states,codes).log_softmax(-1).reshape(size,n,-1)
                        picked=logp.gather(-1,act[None,:,None].expand(size,-1,-1)).squeeze(-1)
                        scores.extend(picked.sum(-1).cpu().tolist())
                scores=np.asarray(scores);ranking=np.argsort(-scores)
                true_index=int(np.flatnonzero(candidate_ids==int(label))[0])
                alternate=float(np.max(np.delete(scores,true_index)))
                rows.append({'persona_id':int(label),'top1_id':int(candidate_ids[ranking[0]]),
                    'top3_ids':candidate_ids[ranking[:3]].tolist(),'top1_correct':int(ranking[0]==true_index),
                    'top3_correct':int(true_index in ranking[:3]),'true_loglikelihood':float(scores[true_index]),
                    'true_minus_best_alternate':float(scores[true_index])-alternate,'all_loglikelihoods':scores.tolist()})
                if (index+1)%50==0:print(json.dumps({'mode':mode,'trajectories':index+1,'total':len(labels)}),flush=True)
        dump(args.out/f'{mode}_scores.json',rows)
        bypersona=np.asarray([np.mean([r['top1_correct'] for r in rows if r['persona_id']==pid]) for pid in candidate_ids])
        rng=np.random.default_rng(191919);boot=[np.mean(rng.choice(bypersona,len(bypersona),replace=True)) for _ in range(2000)]
        results[mode]={'top1':float(np.mean([r['top1_correct'] for r in rows])),
            'top3':float(np.mean([r['top3_correct'] for r in rows])),
            'persona_bootstrap95':np.quantile(boot,[.025,.975]).tolist(),
            'median_true_margin':float(np.median([r['true_minus_best_alternate'] for r in rows])),
            'policy_sha256':hashlib.sha256(policy_file.read_bytes()).hexdigest(),
            'scope':'input-code inference, not independent personality semantics',
            'trajectories':len(rows),'candidate_count':len(candidate_ids)}
        dump(args.out/'summary.json',results)
        print(json.dumps({mode:results[mode]}),flush=True)
    dump(args.out/'runtime.json',{'wall_seconds':time.monotonic()-start,'device':str(device),'cloud_calls':0,'scientific_increment':0})


if __name__=='__main__':main()
