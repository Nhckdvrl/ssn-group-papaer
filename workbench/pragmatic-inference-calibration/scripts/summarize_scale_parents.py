"""E28 completed exact parent contracts; clustered endpoint comparisons."""
import argparse,json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from aggregate import estimate,cluster

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists()
out={'hu':{},'wavelength':{},'implicaturex':{},'limits':['Endpoint size comparisons also change training/data; not pure size causality.',
     'MCQ and original Wavelength likelihood are their parent readouts, not transparent latent knowledge.',
     'Approx has no human norm; no gold FPR, criterion or SDT.',
     'Item/concept-pair intervals are not training-seed or model-family replication intervals.']}
def load(name,file='predictions.jsonl'):
    path=a.root/'runs'/name;c=json.loads((path/'config.json').read_text())
    assert c.get('complete') and c['numerical_gate_pass']
    return [json.loads(l) for l in (path/file).read_text().splitlines()],c
for interface in ['bare','chat']:
    vals=[load(f'E28-hu-{interface}-Qwen3-{size}B') for size in [8,14]]
    assert vals[0][1]['unpadded_input_token_ids_sha256']==vals[1][1]['unpadded_input_token_ids_sha256']
    def collapse(rs):
        g=defaultdict(list)
        for r in rs:g[r['phenomenon'],r['item_id']].append(r)
        return {k:{m:np.mean([r[m] for r in rows]) for m in ['correct','prob_true_answer']} for k,rows in g.items()}
    cs=[collapse(rows) for rows,c in vals];assert cs[0].keys()==cs[1].keys()
    descriptions={};changes={}
    for ph in sorted({k[0] for k in cs[0]}):
        keys=[k for k in cs[0] if k[0]==ph]
        changes[ph]={m:estimate([cs[1][k][m]-cs[0][k][m] for k in keys]) for m in ['correct','prob_true_answer']}
        descriptions[ph]={str(size):{m:estimate([cs[j][k][m] for k in keys]) for m in ['correct','prob_true_answer']} for j,size in enumerate([8,14])}
    out['hu'][interface]={'description':descriptions,'14_minus_8':changes,'input_token_hash_equal':True}
waves={}
for size in [8,14]:
    rows,c=load(f'E28-wavelength-Qwen3-{size}B');assert len(rows)==100
    waves[size]=rows
    unit=lambda r:r['source']['left']+'/'+r['source']['right']
    out['wavelength'][str(size)]={'mae':cluster(rows,lambda r:r['paper_absolute_error'],unit),
        'wasserstein':cluster(rows,lambda r:r['wasserstein'],unit),
        'human_mae':cluster(rows,lambda r:abs(r['human_mean']-float(r['source']['target'])),unit),
        'numerical_controls':c['numerical_controls']}
idx={r['item_id']:r for r in waves[8]}
assert all(r['prompt_sha256']==idx[r['item_id']]['prompt_sha256'] for r in waves[14])
out['wavelength']['14_minus_8_mae']=cluster(waves[14],lambda r:r['paper_absolute_error']-idx[r['item_id']]['paper_absolute_error'],unit)
ivals=[load(f'E28-implicaturex-Qwen3-{size}B','item-results.jsonl') for size in [8,14]]
assert ivals[0][1]['input_token_hashes']==ivals[1][1]['input_token_hashes']
indexes=[{(r['item_id'],r['condition']):r for r in rows} for rows,c in ivals];assert indexes[0].keys()==indexes[1].keys()
metrics=['baseline','recognition','cancel_minus_irrelevant_delta','joint_update','mean_support_mass','max_order_ptrue_difference']
for cond in ['parent','format']:
    changes={};descriptions={}
    for ph in sorted({r['phenomenon'] for r in ivals[0][0]}):
        keys=[k for k,r in indexes[0].items() if r['condition']==cond and r['phenomenon']==ph]
        changes[ph]={m:estimate([indexes[1][k][m]-indexes[0][k][m] for k in keys]) for m in metrics}
        descriptions[ph]={str(size):{m:estimate([indexes[j][k][m] for k in keys]) for m in metrics} for j,size in enumerate([8,14])}
    out['implicaturex'][cond]={'description':descriptions,'14_minus_8':changes,'input_token_hashes_equal':True}
a.output.write_text(json.dumps(out,indent=2)+'\n')
print('Wave',{k:v.get('mae',v) for k,v in out['wavelength'].items()})
print('Impli natural',out['implicaturex']['parent']['14_minus_8']['naturally_occurring_conversational'])
