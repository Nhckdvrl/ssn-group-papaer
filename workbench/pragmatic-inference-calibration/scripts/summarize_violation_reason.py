"""E63 immutable source/token/numeric audit and all preregistered reason contrasts."""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from aggregate import estimate
from violation_data import prepare,specs,common_path,sha,fingerprint,dependencies,TRAITS

def describe(rows,values):
    grouped=defaultdict(list)
    for r,v in zip(rows,values):grouped[r['scene']].append(v)
    return {k:estimate([np.mean([v[k] for v in vs]) for vs in grouped.values()]) for k in values[0]}

def human_bootstrap(root):
    rows=list(csv.DictReader((root/'data/E62-exp2.csv').open()))
    people=sorted({r['subj'] for r in rows});assert len(people)==93
    index={p:i for i,p in enumerate(people)}
    draws=np.random.default_rng(0).multinomial(len(people),np.full(len(people),1/len(people)),size=2000)
    cells=defaultdict(list)
    for r in rows:
        if int(r['Item'])<=14:cells[str(int(r['Item'])),r['Reason.for.Violation'],r['Informativeness']].append(r)
    result={}
    for cell,rs in cells.items():
        present=np.zeros(len(people));present[[index[r['subj']] for r in rs]]=1
        den=draws@present;assert (den>0).all()
        for trait in TRAITS:
            counts=np.zeros((len(people),7))
            for r in rs:counts[index[r['subj']],int(r[trait])-1]=1
            result[cell+(trait,)]=(draws@counts)/den[:,None]
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    assert not a.output.exists();pre=json.loads((Path(__file__).resolve().parents[1]/'results/E63-source-preflight.json').read_text())
    assert pre['gate_pass'] and pre['models']==specs(a.root)
    prepared={};models={};families=defaultdict(list);allvalues={};allrows={};hb=human_bootstrap(a.root);allbvalues={}
    for m in specs(a.root):
        cp=m['id'].split('/')[-1];run=a.root/'runs'/('E63-violation-reason-'+cp)
        if m['family'] not in prepared:prepared[m['family']]=prepare(a.root,AutoTokenizer.from_pretrained(common_path(a.root,m),local_files_only=True))
        rows,audit,nulls=prepared[m['family']];audit=json.loads(json.dumps(audit));cfg=json.loads((run/'config.json').read_text())
        assert cfg['complete'] and cfg['n']==len(rows)==1380 and cfg['model']==m['id'] and cfg['revision']==m['sha']
        assert cfg['source_audit']==audit==pre['audits'][cp]['source_audit']
        assert cfg['input_sha256']==fingerprint(rows,nulls)==pre['audits'][cp]['input_sha256']
        assert cfg['helper_sha256']==sha(Path(__file__).with_name('violation_data.py'))==pre['helper_sha256']
        assert cfg['dependency_sha256']==dependencies()==pre['dependencies']
        assert cfg['script_sha256']==sha(Path(__file__).with_name('run_violation_reason.py'))
        assert cfg['dtype']=='float32' and cfg['batch_size']==1 and cfg['attention']=='eager' and not cfg['tf32'] and cfg['numerical_gate_pass']
        controls=json.loads((run/'numerical-control.json').read_text());assert len(controls)==32 and all(v['pass'] for v in controls)
        raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()];assert len(raw)==1380
        groups=defaultdict(list);rr=defaultdict(list);copies=defaultdict(list);values={};entries={};cell={};bvalues={};hg=defaultdict(list)
        for r,z in zip(rows,raw):
            assert all(z[k]==v for k,v in r.items())
            for mode in ['full_logprob','content_logprob']:
                q=z[mode];lp=np.array([s[mode] for s in z['choice_scores']]);norm=float(np.logaddexp.reduce(lp))
                assert np.isfinite(lp).all() and np.allclose(q['conditional_probs'],np.exp(lp-norm),rtol=1e-10,atol=1e-12)
                assert q['argmax']==int(lp.argmax()) and 0<=q['candidate_mass']<=1.00001 and abs(q['candidate_mass']-math.exp(norm))<1e-12
                p=np.array(q['conditional_probs']);v={'candidate_mass':q['candidate_mass']}
                if r['kind']=='trait':
                    h=np.array(r['human_counts'])/r['human_n'];pm=float(p@np.arange(1,8));hm=float(h@np.arange(1,8))
                    v.update(model_mean_rating=pm,human_mean_rating=hm,mean_rating_absolute_error=abs(pm-hm),human_distribution_brier=float(np.square(p-h).sum()))
                    cell[r['alias'],r['interface'],mode,r['attribute'],r['scene'],r['context'],r['utterance']]=(pm,hm)
                else:
                    v.update(correct=float(q['argmax']==r['expected_index']),expected_probability=float(p[r['expected_index']]))
                g='/'.join((r['alias'],r['interface'],mode,r['kind']))
                if r['kind'].endswith('copy'):copies[g].append(v)
                else:groups[g].append(v);rr[g].append(r);values[r['id'],mode]=v;entries[r['id'],mode]=r
                if r['kind']=='trait':
                    hdraw=hb[r['scene'],r['context'],r['utterance'],r['attribute']]
                    bv=np.square(p-hdraw).sum(1);hg[g].append(bv);bvalues[r['id'],mode]=bv
        effects={};targets={};scenes=sorted({r['scene'] for r in rows if 'scene' in r},key=int)
        assert len(scenes)==14
        for alias,interface,mode,attribute in sorted({k[:4] for k in cell}):
            per=[]
            for scene in scenes:
                contrast=lambda j,level:cell[alias,interface,mode,attribute,scene,'Ina',level][j]-cell[alias,interface,mode,attribute,scene,'Unw',level][j]
                v={'scene':scene}
                for level in ['High','Low']:
                    v['model_'+level]=contrast(0,level);v['human_'+level]=contrast(1,level);v['model_minus_human_'+level]=contrast(0,level)-contrast(1,level)
                for who in ['model','human','model_minus_human']:v[who+'_mean']=(v[who+'_High']+v[who+'_Low'])/2
                per.append(v)
            name='/'.join((alias,interface,mode,attribute));effects[name]={'scene_values':per,**{k:estimate([v[k] for v in per]) for k in per[0] if k!='scene'}}
            hcontrast=np.mean([((hb[scene,'Ina',level,attribute]-hb[scene,'Unw',level,attribute])@np.arange(1,8)) for scene in scenes for level in ['High','Low']],axis=0)
            effects[name]['human_participant_sampling_ci95']=np.quantile(hcontrast,[.025,.975]).tolist()
            effects[name]['fixed_model_human_sampling_discrepancy_ci95']=np.quantile(effects[name]['model_mean']['mean']-hcontrast,[.025,.975]).tolist()
        for alias,interface,mode in sorted({k[:3] for k in cell}):
            for dimension,positive,negative in [('competence','Competent','Knowledgeable'),('warmth','Likable','Considerate')]:
                x=effects['/'.join((alias,interface,mode,positive))]['scene_values'];y=effects['/'.join((alias,interface,mode,negative))]['scene_values']
                per=[{'scene':u['scene'],**{k:u[k]-v[k] for k in u if k!='scene'}} for u,v in zip(x,y)]
                assert all(u['scene']==v['scene'] for u,v in zip(x,y))
                targets['/'.join((alias,interface,mode,dimension))]={'scene_values':per,**{k:estimate([v[k] for v in per]) for k in per[0] if k!='scene'}}
        models[cp]={'model':m['id'],'revision':m['sha'],'family':m['family'],'stage':m['stage'],'n':len(raw),'wall_seconds':cfg['wall_seconds'],
            'descriptions':{g:describe(rr[g],v) for g,v in groups.items()},'reason_effects':effects,'target_reason_interactions':targets,
            'fixed_model_human_participant_sampling_brier_ci95':{g:np.quantile(np.mean(v,axis=0),[.025,.975]).tolist() for g,v in hg.items()},
            'copy_controls':{g:{k:estimate([v[k] for v in vv]) for k in vv[0]} for g,vv in copies.items()},
            'null_readout':cfg['null_readout'],'config_sha256':sha(run/'config.json'),'raw_sha256':sha(run/'predictions.jsonl'),'numerical_controls':controls}
        allvalues[cp]=values;allrows[cp]=entries;allbvalues[cp]=bvalues;families[m['family']].append(cp)
    paired={}
    for family,names in families.items():
        for left,right in zip(names,names[1:]):
            assert allvalues[left].keys()==allvalues[right].keys();groups=defaultdict(list);rr=defaultdict(list)
            for key,x in allvalues[left].items():
                r=allrows[left][key];g='/'.join((r['alias'],r['interface'],key[1],r['kind']))
                groups[g].append({k:allvalues[right][key][k]-v for k,v in x.items()});rr[g].append(r)
            changes={g:describe(rr[g],v) for g,v in groups.items()}
            ec={}
            for g,x in models[left]['reason_effects'].items():
                y=models[right]['reason_effects'][g];per=[{k:v[k]-u[k] for k in u if k!='scene'} for u,v in zip(x['scene_values'],y['scene_values'])]
                ec[g]={k:estimate([v[k] for v in per]) for k in per[0]}
            hg=defaultdict(list)
            for key,x in allbvalues[left].items():
                r=allrows[left][key];g='/'.join((r['alias'],r['interface'],key[1],r['kind']))
                hg[g].append(allbvalues[right][key]-x)
            paired[left+' -> '+right]={'task_changes':changes,'reason_effect_changes':ec,
              'fixed_models_human_participant_sampling_brier_delta_ci95':{g:np.quantile(np.mean(v,axis=0),[.025,.975]).tolist() for g,v in hg.items()}}
    result={'experiment':'E63','n':sum(m['n'] for m in models.values()),'source_input_numerical_gate_pass':True,'models':models,'paired_stage_changes':paired,
        'script_sha256':sha(Path(__file__)),'limitations':[
          'Fourteen independent scenes, not 11040 situations; scene CI is a pilot. Source scenes15/16 not expanded due pre-output ambiguity.',
          'Public PDF expansion differs from original incremental visual UI; declared rendering and missing source strings are retained.',
          'Quote controls verify literal opening-string reading, not semantic knowledge/motive understanding.',
          'Different trait content is confounded with temporary/durable framing; their interaction does not isolate temporal generalization causally.',
          'Human ratings describe perceived impressions, not true personality; population distributions are not model intrinsic uncertainty.',
          'Nulls diagnose trait frames only; no automatic prior removal or transparent latent belief readout.',
          'All interfaces/instructions/modes/traits retained; many descriptive contrasts, no selected significant finding.',
          'Checkpoint algorithm, data and budget covary; no isolated RLHF or scale causal claim.',
          'Secondary human participant bootstrap preserves the same person across scene responses; scene CI and human sampling CI are separate, not joint/training-seed CI.',
          'Original subject/item mixed-model inference not reproduced; target-interaction human sampling CI not computed.']}
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({cp:{g:{k:round(v['mean'],4) for k,v in z.items() if k in ['correct','candidate_mass','mean_rating_absolute_error']} for g,z in m['descriptions'].items() if 'original/common-chat/full' in g} for cp,m in models.items()},indent=2))

if __name__=='__main__':main()
