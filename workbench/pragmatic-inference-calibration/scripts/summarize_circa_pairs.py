"""E34 source semantic classes, paired natural answers and ordering diagnostic."""
import argparse,json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from aggregate import estimate
from circa_pair_data import prepare

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
ap.add_argument('--allow-incomplete',action='store_true');a=ap.parse_args();assert not a.output.exists()
source,pairs,audit=prepare(a.root);audit=json.loads(json.dumps(audit));n=len(source);models={};pending=[];values={}
def describe(records):
    keys=set.intersection(*(set(r) for r in records))
    return {k:estimate([r[k] for r in records]) for k in sorted(keys)}
for cp in ['Qwen2.5-3B','Qwen2.5-3B-Instruct','OLMoE-1B-7B-0125','OLMoE-1B-7B-0125-SFT','OLMoE-1B-7B-0125-DPO','Qwen3-4B','Qwen3-8B','Qwen3-14B']:
    path=a.root/'runs'/('E34-circa-pairs-'+cp)
    if not (path/'config.json').exists() or not json.loads((path/'config.json').read_text()).get('complete'):
        pending.append(cp);continue
    c=json.loads((path/'config.json').read_text());assert c['numerical_gate_pass'] and c['source_audit']==audit
    rows=[json.loads(l) for l in (path/'predictions.jsonl').read_text().splitlines()];assert len(rows)==4*n
    idx={(r['id'],r['interface'],r['order']):r for r in rows};assert len(idx)==len(rows)
    groups=defaultdict(list);records={}
    for interface in ['bare','common-chat']:
        for order in [0,1]:
            for p in pairs:
                x=idx[p['left_id'],interface,order];y=idx[p['right_id'],interface,order]
                assert x['question_group']==y['question_group']==p['question_group']
                strong,weak=p['left_label'],p['right_label']
                px=x['choice_probs'];py=y['choice_probs']
                rx=px[weak]/(px[weak]+px[strong]);ry=py[weak]/(py[weak]+py[strong])
                d={'strong_gold_probability':px[strong],'weak_gold_probability':py[weak],
                   'strong_correct':float(max(px,key=px.get)==strong),'weak_correct':float(max(py,key=py.get)==weak),
                   'weak_as_strong_error':float(max(py,key=py.get)==strong),
                   'relative_weak_probability_strong_answer':rx,'relative_weak_probability_weak_answer':ry,
                   'paired_relative_weak_probability_delta':ry-rx,
                   'paired_strong_probability_delta':py[strong]-px[strong],
                   'strong_two_class_probability_mass':px[weak]+px[strong],
                   'weak_two_class_probability_mass':py[weak]+py[strong],
                   'strong_global_candidate_mass':x['support_mass'],'weak_global_candidate_mass':y['support_mass']}
                records[interface,order,p['contrast'],p['question_group']]=d
                groups[interface+'/'+str(order)+'/'+p['contrast']].append(d)
    ordering=defaultdict(list)
    for p in pairs:
        for interface in ['bare','common-chat']:
            for role,k in [('strong',p['left_id']),('weak',p['right_id'])]:
                x=idx[k,interface,0]['choice_probs'];y=idx[k,interface,1]['choice_probs']
                ordering[interface+'/'+p['contrast']+'/'+role].append({'max_class_probability_gap':max(abs(x[t]-y[t]) for t in x),
                    'semantic_argmax_agreement':float(max(x,key=x.get)==max(y,key=y.get))})
    models[cp]={'run':path.name,'source_audit':audit,'input_token_hashes':c['input_token_hashes'],
        'config_sha256':hashlib.sha256((path/'config.json').read_bytes()).hexdigest(),
        'descriptions':{g:describe(rs) for g,rs in groups.items()},'ordering':{g:describe(rs) for g,rs in ordering.items()}}
    values[cp]=(records,c,idx)
paired={}
for left,right in [('Qwen2.5-3B','Qwen2.5-3B-Instruct'),('OLMoE-1B-7B-0125','OLMoE-1B-7B-0125-SFT'),
                   ('OLMoE-1B-7B-0125-SFT','OLMoE-1B-7B-0125-DPO'),('Qwen3-4B','Qwen3-8B'),('Qwen3-8B','Qwen3-14B')]:
    if left not in values or right not in values:continue
    ls,lc,li=values[left];rs,rc,ri=values[right]
    assert lc['input_token_hashes']==rc['input_token_hashes'] and ls.keys()==rs.keys()
    assert all(r['readout_prompt_sha256']==ri[k]['readout_prompt_sha256'] for k,r in li.items())
    groups=defaultdict(list)
    for k,d in ls.items():groups['/'.join(map(str,k[:3]))].append({m:rs[k][m]-v for m,v in d.items()})
    paired[left+' -> '+right]={g:describe(rs) for g,rs in groups.items()}
assert a.allow_incomplete or not pending,pending
out={'models':models,'paired_stage_size_changes':paired,'pending':pending,
     'source_audit':audit,'limits':['Different original replies to the same original question are not a one-variable causal manipulation.',
                                  'CI is by question within each contrast; four shared questions link contrasts, not pooled as independent.',
                                  'Unanimous selected subset does not estimate full Circa population performance.',
                                  'No warranted/unwarranted inference binary labels or SDT.',
                                  'Mean probability differences do not prove latent knowledge or a shared inference criterion.']}
a.output.write_text(json.dumps(out,indent=2)+'\n')
for cp,v in models.items():
    print(cp,{g:{m:round(z[m]['mean'],3) for m in ['strong_correct','weak_correct','weak_as_strong_error','paired_relative_weak_probability_delta']} for g,z in v['descriptions'].items() if g.startswith('common-chat/0/')})
print('pending',pending)
