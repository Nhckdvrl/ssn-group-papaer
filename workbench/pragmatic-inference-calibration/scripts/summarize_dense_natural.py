"""E51/E52 complete source-matched stage contrasts, preserving probability mass."""
import argparse
import importlib
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from aggregate import estimate


def iqap_metrics(source, q):
    p=np.array(q['conditional_probs']);h=np.array([int(source[k]) for k in ['definite-yes','probable-yes','definite-no','probable-no']])/30
    assert abs(h.sum()-1)<1e-12
    m={'candidate_mass':q['candidate_mass'],'polarity_mae':float(abs(p[:2].sum()-h[:2].sum())),
       'four_way_brier':float(np.square(p-h).sum()),'definite_probability':float(p[[0,2]].sum()),
       'human_definite_probability':float(h[[0,2]].sum()),'definite_minus_human':float(p[[0,2]].sum()-h[[0,2]].sum())}
    if h[:2].sum()!=.5:m['polarity_correct']=float((p[:2].sum()>.5)==(h[:2].sum()>.5))
    return m


def summarize(values):
    return {k:estimate([v[k] for v in values if k in v]) for k in sorted(set().union(*(set(v) for v in values)))}


def iqap_describe(entries, values):
    out=summarize(values)
    for key, stat in out.items():
        clusters=defaultdict(list)
        for r,v in zip(entries,values):
            if key in v:clusters[r['source']['Classification']+'/'+r['source']['Source']].append(v[key])
        sums=np.array([sum(v) for v in clusters.values()]);counts=np.array([len(v) for v in clusters.values()])
        idx=np.random.default_rng(0).integers(len(sums),size=(2000,len(sums)))
        stat['source_cluster_ci95_sensitivity']=np.quantile(sums[idx].sum(1)/counts[idx].sum(1),[.025,.975]).tolist()
        stat['n_source_clusters']=len(clusters)
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--experiment',choices=['E51','E52'],required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists()
    helper=importlib.import_module('dense_stage_data' if a.experiment=='E51' else 'dense_anchor_data')
    script='run_dense_stage.py' if a.experiment=='E51' else 'run_dense_anchor.py'
    helper_name='dense_stage_data.py' if a.experiment=='E51' else 'dense_anchor_data.py'
    pre=json.loads((Path(__file__).resolve().parents[1]/('results/'+a.experiment+'-source-preflight.json')).read_text())
    assert pre['gate_pass'] and pre['models']==helper.specs(a.root)
    tok=AutoTokenizer.from_pretrained(helper.common_path(a.root),local_files_only=True)
    source_data={task:helper.prepare(a.root,tok,task) for task in ['iqap','circa']}
    iqap_index={r['id']:r for r in source_data['iqap'][0]}
    models={};paired_values={};total=0
    for m in helper.specs(a.root):
        cp=m['id'].split('/')[-1];tasks={};stage_values={}
        for task in ['iqap','circa']:
            run=a.root/'runs'/(a.experiment+'-'+task+'-'+cp);cfg=json.loads((run/'config.json').read_text())
            rows,audit,nulls=source_data[task]
            assert cfg['complete'] and cfg['model']==m['id'] and cfg['revision']==m['sha'] and cfg['stage']==m['stage']
            assert cfg['dtype']=='float32' and cfg['batch_size']==1 and cfg['attention']=='eager' and not cfg['tf32']
            assert cfg['source_audit']==audit==pre['tasks'][task]['source_audit'] and cfg['n']==len(rows)
            assert cfg['input_sha256']==helper.fingerprint(rows,nulls)==pre['tasks'][task]['input_sha256']
            assert cfg['script_sha256']==helper.sha(Path(__file__).with_name(script))
            assert cfg['helper_sha256']==helper.sha(Path(__file__).with_name(helper_name))==pre['helper_sha256']
            assert cfg['dependency_sha256']==helper.dependency_shas()==pre['dependency_sha256'] and cfg['numerical_gate_pass']
            controls=json.loads((run/'numerical-control.json').read_text())
            assert len(controls)==(4 if task=='iqap' else 8)
            assert all(c['pass'] and c['repeat_lp_delta']<1e-6 and c['independent_full_lp_delta']<.001 and c['probability_delta']<.001 and c['argmax_agrees'] for c in controls)
            raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()];assert len(raw)==len(rows)
            index={}
            for r,z in zip(rows,raw):
                assert all(z[k]==v for k,v in r.items());assert z['id'] not in index
                for key in ['full_logprob','content_logprob']:
                    lp=np.array([s[key] for s in z['choice_scores']]);assert np.isfinite(lp).all()
                    q=z[key];norm=float(np.logaddexp.reduce(lp))
                    assert np.allclose(q['conditional_probs'],np.exp(lp-norm),rtol=1e-10,atol=1e-12)
                    assert q['argmax']==int(lp.argmax()) and 0<=q['candidate_mass']<=1.00001
                    assert abs(q['candidate_mass']-math.exp(norm))<1e-12
                index[z['id']]=z
            total+=len(raw)
            groups=defaultdict(list);entries=defaultdict(list);values={}
            if task=='iqap':
                for z in raw:
                    for key in ['full_logprob','content_logprob']:
                        v=iqap_metrics(z['source'],z[key]);values[z['id'],key]=v
                        for cls in ['all',z['source']['Classification']]:
                            group=z['interface']+'/'+key+'/'+cls;groups[group].append(v);entries[group].append(z)
                descriptions={g:iqap_describe(entries[g],vs) for g,vs in groups.items()}
                null=cfg['null_readout']
                assert set(null)==set(nulls)
                extra={'null_readout':null,'human_polarity_tie_n':sum(sum(int(r['source'][k]) for k in ['definite-yes','probable-yes'])==15 for r in rows)//2}
            else:
                ordering=defaultdict(list)
                for interface in ['bare','common-chat']:
                    for order in [0,1]:
                        for pair in audit['pairs']:
                            x=index[pair['left_id']+'/'+interface+'/'+str(order)];y=index[pair['right_id']+'/'+interface+'/'+str(order)]
                            assert x['source']['question_group']==y['source']['question_group']==pair['question_group']
                            px=dict(zip(x['options'],x['full_logprob']['conditional_probs']));py=dict(zip(y['options'],y['full_logprob']['conditional_probs']))
                            strong,weak=pair['left_label'],pair['right_label'];sx=px[strong]+px[weak];sy=py[strong]+py[weak]
                            assert sx>0 and sy>0
                            v={'strong_gold_probability':px[strong],'weak_gold_probability':py[weak],
                               'strong_correct':float(max(px,key=px.get)==strong),'weak_correct':float(max(py,key=py.get)==weak),
                               'weak_as_strong_error':float(max(py,key=py.get)==strong),
                               'paired_relative_weak_probability_delta':py[weak]/sy-px[weak]/sx,
                               'paired_strong_probability_delta':py[strong]-px[strong],
                               'strong_two_class_probability_mass':sx,'weak_two_class_probability_mass':sy,
                               'strong_global_candidate_mass':x['full_logprob']['candidate_mass'],'weak_global_candidate_mass':y['full_logprob']['candidate_mass']}
                            group=interface+'/'+str(order)+'/'+pair['contrast'];groups[group].append(v)
                            values[interface,order,pair['contrast'],pair['question_group']]=v
                    for r in rows:
                        if r['interface']!=interface or r['order']!=0:continue
                        x=index[r['id']];y=index[r['source']['id']+'/'+interface+'/1']
                        px=dict(zip(x['options'],x['full_logprob']['conditional_probs']));py=dict(zip(y['options'],y['full_logprob']['conditional_probs']))
                        ordering[interface].append({'max_semantic_probability_gap':max(abs(px[k]-py[k]) for k in px),
                            'semantic_argmax_agreement':float(max(px,key=px.get)==max(py,key=py.get))})
                descriptions={g:summarize(vs) for g,vs in groups.items()};extra={'ordering':{g:summarize(vs) for g,vs in ordering.items()}}
            stage_values[task]=values
            tasks[task]={'n':len(raw),'descriptions':descriptions,**extra,
                'source_audit':audit,'input_sha256':cfg['input_sha256'],'numerical_controls':controls,
                'config_sha256':helper.sha(run/'config.json'),'raw_sha256':helper.sha(run/'predictions.jsonl'),'wall_seconds':cfg['wall_seconds']}
        models[cp]={'stage':m['stage'],'model':m['id'],'revision':m['sha'],'tasks':tasks};paired_values[cp]=stage_values
    paired={};names=list(models)
    for left,right in zip(names,names[1:]):
        changes={}
        for task in ['iqap','circa']:
            ls,rs=paired_values[left][task],paired_values[right][task];assert ls.keys()==rs.keys()
            groups=defaultdict(list);entries=defaultdict(list)
            for key,x in ls.items():
                v={k:rs[key][k]-n for k,n in x.items()}
                if task=='iqap':
                    item,key_metric=key;interface=item.rsplit('/',1)[-1];group=interface+'/'+key_metric
                    # Preserve transcript clusters in paired differences as well.
                    original=iqap_index[item]
                    entries[group].append(original)
                else:group='/'.join(map(str,key[:3]))
                groups[group].append(v)
            changes[task]={g:(iqap_describe(entries[g],vs) if task=='iqap' else summarize(vs)) for g,vs in groups.items()}
        paired[left+' -> '+right]=changes
    result={'experiment':a.experiment,'n':total,'models':models,'paired_stage_changes':paired,
        'full_source_input_score_gate_pass':True,'script_sha256':helper.sha(Path(__file__)),
        'limits':['Matched common tokenizer/terminal is a controlled interface, not native Base generation.',
            'Stage algorithms, datasets and budgets co-vary; no isolated DPO/RLHF causal claim.',
            'Human response distributions are judgments about intent, not model intrinsic uncertainty or speaker certainty.',
            'Circa replies share original questions but differ in content/difficulty; not a one-variable causal manipulation.',
            'All source pairs, orders and interfaces retained. Unanimous source selection does not estimate full Circa performance.',
            'Item/question CI is not training-seed CI. No multiplicity-adjusted confirmatory discovery, inference-licensing gold or SDT claim.']}
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({cp:{i:{k:m['tasks']['iqap']['descriptions'][i+'/full_logprob/all'][k]['mean'] for k in ['polarity_correct','four_way_brier','candidate_mass']} for i in ['bare','common-chat']} for cp,m in models.items()},indent=2))


if __name__=='__main__':main()
