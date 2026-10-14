#!/usr/bin/env python3
"""Graph-paired stage geometry, held-out directions, explicitly noncausal."""
import argparse
import json
from pathlib import Path
import torch


def cosine(a,b):
    return (a*b).sum(-1)/(a.norm(dim=-1)*b.norm(dim=-1)).clamp_min(1e-12)


def report(directory):
    h=torch.load(directory/'residuals.pt',map_location='cpu',weights_only=True)
    m=[json.loads(x) for x in (directory/'prompts.jsonl').read_text().splitlines()]
    index={(r['case_id'],r['stage'],r['persona'],r['location']):i for i,r in enumerate(m)}
    ids=list(dict.fromkeys(r['case_id'] for r in m));stages=['conv','update','exec']
    output={'manifest':json.loads((directory/'manifest.json').read_text()),
            'graphs':len(ids),'train_graphs':len(ids)//2,'test_graphs':len(ids)-len(ids)//2,
            'scope':'paired fixed-context persona representation, not causal action effect','locations':{}}
    for loc in ['input_boundary','generation_prefix']:
        d=torch.stack([torch.stack([h[index[(i,s,'agreeable',loc)]]-h[index[(i,s,'firm',loc)]]
                                   for s in stages]) for i in ids])
        n=len(ids)//2;direction=d[:n].mean(0);test=d[n:]
        baseline=torch.stack([torch.stack([h[index[(i,s,'firm',loc)]] for s in stages]) for i in ids])
        rows=[]
        for l in range(d.shape[2]):
            mean=d[:,:,l].mean(0)
            norm=d[:,:,l].norm(dim=-1).mean(0)
            mat=[[float(cosine(mean[a],mean[b])) for b in range(3)] for a in range(3)]
            transfer=[[float(cosine(test[:,b,l],direction[a,l]).mean()) for b in range(3)] for a in range(3)]
            sign=[[float(((test[:,b,l]*direction[a,l]).sum(-1)>0).float().mean()) for b in range(3)] for a in range(3)]
            rows.append({'layer':l+1,'stages':stages,'mean_delta_norm':norm.tolist(),
                'relative_delta_norm':(norm/baseline[:,:,l].norm(dim=-1).mean(0)).tolist(),
                'coherence':(mean.norm(dim=-1)/norm.clamp_min(1e-12)).tolist(),
                'mean_direction_cosine':mat,'heldout_transfer_cosine':transfer,'heldout_positive_projection':sign})
        output['locations'][loc]=rows
    return output


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    torch.set_num_threads(1)
    out=report(a.directory)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    for loc,rows in out['locations'].items():
        print(loc,'layer64',json.dumps(rows[-1]))
