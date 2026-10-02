"""E36/E37: bounded instruction recovery, both source orders, question-paired CIs."""
import argparse,hashlib,json
from pathlib import Path
from collections import defaultdict
from transformers import AutoTokenizer
from aggregate import estimate
from circa_pair_data import prepare,prompt,render,CATEGORIES
from run_circa_instruction import STRICT,strict_render
from iqap_data import common_model


def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def describe(ds):
    return {k:estimate([r[k] for r in ds]) for k in sorted(ds[0])}
def stats(idx,pairs,interfaces,conditions):
    values={};groups=defaultdict(list);ordering=defaultdict(list)
    for interface in interfaces:
        for condition in conditions:
            for p in pairs:
                for order in [0,1]:
                    x=idx[p['left_id'],interface,condition,order];y=idx[p['right_id'],interface,condition,order]
                    strong,weak=p['left_label'],p['right_label'];px=x['choice_probs'];py=y['choice_probs']
                    assert x['question_group']==y['question_group']==p['question_group']
                    d={'strong_correct':float(max(px,key=px.get)==strong),'weak_correct':float(max(py,key=py.get)==weak),
                       'weak_as_strong_error':float(max(py,key=py.get)==strong),
                       'strong_gold_probability':px[strong],'weak_gold_probability':py[weak],
                       'paired_relative_weak_probability_delta':py[weak]/(py[weak]+py[strong])-px[weak]/(px[weak]+px[strong]),
                       'strong_two_class_mass':px[strong]+px[weak],'weak_two_class_mass':py[strong]+py[weak],
                       'strong_global_candidate_mass':x['support_mass'],'weak_global_candidate_mass':y['support_mass']}
                    key=(interface,condition,order,p['contrast'],p['question_group']);assert key not in values
                    values[key]=d;groups['/'.join(map(str,key[:4]))].append(d)
                for role,item in [('strong',p['left_id']),('weak',p['right_id'])]:
                    x=idx[item,interface,condition,0]['choice_probs'];y=idx[item,interface,condition,1]['choice_probs']
                    ordering[interface+'/'+condition+'/'+p['contrast']+'/'+role].append({
                        'semantic_argmax_agreement':float(max(x,key=x.get)==max(y,key=y.get)),
                        'max_class_probability_gap':max(abs(x[k]-y[k]) for k in x)})
    changes=defaultdict(list)
    for k,d in values.items():
        interface,condition,order,contrast,question=k
        if condition!='original':continue
        z=values[interface,'strict',order,contrast,question]
        changes[f'{interface}/{order}/{contrast}'].append({m:z[m]-v for m,v in d.items()})
    return {'descriptions':{g:describe(ds) for g,ds in groups.items()},
            'ordering':{g:describe(ds) for g,ds in ordering.items()},
            'paired_strict_minus_original':{g:describe(ds) for g,ds in changes.items()}}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--experiment',choices=['E36','E37'],required=True);a=ap.parse_args();assert not a.output.exists()
    rows,pairs,audit=prepare(a.root);audit=json.loads(json.dumps(audit));source={r['id']:r for r in rows};models={}
    if a.experiment=='E36':
        cps=['Qwen2.5-3B','Qwen2.5-3B-Instruct','OLMoE-1B-7B-0125','OLMoE-1B-7B-0125-SFT','OLMoE-1B-7B-0125-DPO','Qwen3-4B','Qwen3-8B','Qwen3-14B']
        for cp in cps:
            idx={};configs={};tok=AutoTokenizer.from_pretrained(common_model(a.root,cp),local_files_only=True)
            for condition,prefix in [('original','E34-circa-pairs-'),('strict','E36-circa-instruction-')]:
                path=a.root/'runs'/(prefix+cp);c=json.loads((path/'config.json').read_text())
                assert c['complete'] and c['numerical_gate_pass'] and c['source_audit']==audit
                configs[condition]={'config':c,'sha256':digest((path/'config.json').read_text()),'run':path.name}
                raw=[json.loads(l) for l in (path/'predictions.jsonl').read_text().splitlines()];assert len(raw)==4*len(rows)
                local={}
                for z in raw:
                    s=source[z['id']];assert all(z[k]==v for k,v in s.items())
                    key=z['id'],z['interface'],condition,z['order'];assert key not in idx
                    text=(strict_render if condition=='strict' else render)(tok,s,z['order'],z['interface'])
                    assert z['readout_prompt_sha256']==digest(text)
                    assert set(z['choice_probs'])==set(CATEGORIES)
                    assert abs(sum(z['choice_probs'].values())-1)<1e-5
                    idx[key]=z;local[z['id'],z['interface'],z['order']]=z
                for interface in ['bare','common-chat']:
                    for order in [0,1]:
                        encoded=[tok.encode((strict_render if condition=='strict' else render)(tok,r,order,interface),add_special_tokens=False) for r in rows]
                        assert digest(json.dumps(encoded))==c['input_token_hashes'][f'{interface}/{order}']
                if condition=='strict':assert c['strict_instruction']==STRICT
            assert configs['original']['config']['revision']==configs['strict']['config']['revision']
            assert len(idx)==8*len(rows)
            models[cp]={'configs':configs,**stats(idx,pairs,['bare','common-chat'],['original','strict'])}
    else:
        idx={};configs=[];seen=set();tok=AutoTokenizer.from_pretrained(a.root/'models/flan-t5-xl',local_files_only=True,use_fast=False)
        for shard in range(4):
            path=a.root/'runs'/f'E37-flan-circa-shard{shard}of4';c=json.loads((path/'config.json').read_text())
            assert c['complete'] and c['numerical_gate_pass'] and c['source_audit']==audit and c['shard']==shard
            chosen=[r for r in rows if int(r['question_group'],16)%4==shard]
            assert c['item_ids']==[r['id'] for r in chosen] and not seen.intersection(c['item_ids']);seen.update(c['item_ids'])
            raw=[json.loads(l) for l in (path/'predictions.jsonl').read_text().splitlines()];assert len(raw)==4*len(chosen)==c['n']
            for z in raw:
                s=source[z['id']];assert all(z[k]==v for k,v in s.items())
                key=z['id'],z['interface'],z['condition'],z['order'];assert key not in idx
                text=(STRICT if z['condition']=='strict' else '')+prompt(s,z['order'])
                assert z['readout_prompt_sha256']==digest(text) and set(z['choice_probs'])==set(CATEGORIES)
                assert abs(sum(z['choice_probs'].values())-1)<1e-5
                idx[key]=z
            for condition in ['original','strict']:
                for order in [0,1]:
                    ids=[tok.encode((STRICT if condition=='strict' else '')+prompt(r,order),add_special_tokens=True) for r in chosen]
                    assert digest(json.dumps(ids))==c['input_token_hashes'][f'{condition}/{order}']
            configs.append({'config':c,'sha256':digest((path/'config.json').read_text()),'run':path.name})
        assert len(seen)==len(source) and len(idx)==4*len(rows)
        models['flan-t5-xl']={'configs':configs,**stats(idx,pairs,['native-encoder'],['original','strict'])}
    out={'experiment':a.experiment,'complete':True,'source_audit':audit,'models':models,
         'limits':['Question-paired item bootstrap within each contrast; do not pool overlapping contrasts as independent.',
                   'All source judgments and meaning classes preserved; selected unanimous subset only.',
                   'Strong and weak errors, both orders, and absolute candidate support reported together.',
                   'Single-instruction recovery does not establish latent ability or a common criterion.',
                   'Native Flan is an instrument/family boundary, not a controlled training-stage comparison.']}
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    for cp,v in models.items():
        print(cp)
        for g,d in v['descriptions'].items():
            if ('common-chat' in g or 'native-encoder' in g) and g.endswith('negative-strength'):
                print(g,{k:round(d[k]['mean'],4) for k in ['strong_correct','weak_correct','weak_as_strong_error']})
        for g,d in v['paired_strict_minus_original'].items():
            if ('common-chat' in g or 'native-encoder' in g) and g.endswith('negative-strength'):
                print('change',g,{k:d[k] for k in ['strong_correct','weak_correct','weak_as_strong_error']})
if __name__=='__main__':main()
