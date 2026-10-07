"""E87 complete-only actual answer map, preserving format/cap missingness."""
import argparse
import collections
import json
import re
from pathlib import Path
import time
from data import sha
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate


def semantic_label(text,mapping):
    text=text.strip()
    m=re.fullmatch(r'([AB])(?:\.\s*(Yes|No))?',text,re.IGNORECASE)
    if m:
        shown=['Yes','No'] if mapping==0 else ['No','Yes']
        label=shown['AB'.index(m.group(1).upper())]
        if m.group(2) and m.group(2).capitalize()!=label:return None,'conflicting_option_and_word'
        return label,'explicit_option'
    m=re.match(r'^(Yes|No)(?=$|[\s.,!?;:])',text,re.IGNORECASE)
    return (m.group(1).capitalize(),'explicit_word') if m else (None,'unresolved')


def analyze(root,semantic=False):
    mothers=list(map(json.loads,(root.parent/'E86/data-v1.jsonl').read_text().splitlines()))
    meta={r['item_id']:dict(r,cluster_id=r['analysis_cluster_id']) for r in mothers}
    runs=json.loads((root/'runner-pids-v1.json').read_text())
    panels=[];joint_panels=[];counts=[];provenance=[];noise=[]
    metrics=['lower_correct','upper_correct','valid','stopped','cap','strict_exact','forced_correct',
             'actual_minus_forced_lower','actual_minus_forced_upper','mismatch_lower','mismatch_upper']
    for model in MODELS:
        index={}; selected=[r for r in runs if r['model']==model];n=selected[0]['shards']
        assert {r['shard'] for r in selected}==set(range(n))
        for run in selected:
            out=Path(run['out']);cfg=json.loads((out/'config.json').read_text())
            assert sha(out/'predictions.jsonl')==cfg['predictions_sha256']
            assert cfg['data_sha256']==sha(root.parent/'E86/data-v1.jsonl')
            assert cfg['model_manifest_sha256']==sha(root.parent/'models'/model/'manifest.json')
            ps=list(map(json.loads,(out/'predictions.jsonl').read_text().splitlines()));assert len(ps)==cfg['tasks']
            for p in ps:
                r=meta[p['item_id']];key=p['item_id'],p['operation'],p['mapping']
                assert key not in index and int(r['sentence_sha256'][:16],16)%n==run['shard']
                assert p['grounded_gold']==r['grounded_gold']
                if semantic:
                    p['label'],p['semantic_parse_status']=semantic_label(p['output_text'],p['mapping'])
                    p['known_correct']=None if p['label'] is None else p['label']==p['grounded_gold']
                    p['lower_correct']=bool(p['stopped'] and p['known_correct'])
                    p['upper_correct']=bool(p['label'] is None or not p['stopped'] or p['known_correct'])
                    p['differs_from_forced']=None if p['label'] is None else p['label']!=p['forced_label']
                p['valid']=p['label'] is not None
                p['forced_correct']=p['forced_label']==p['grounded_gold']
                p['actual_minus_forced_lower']=float(p['lower_correct'])-float(p['forced_correct'])
                p['actual_minus_forced_upper']=float(p['upper_correct'])-float(p['forced_correct'])
                p['mismatch_lower']=bool(p['differs_from_forced'])
                p['mismatch_upper']=p['differs_from_forced'] is None or p['differs_from_forced']
                index[key]=p
            provenance.append(dict(model=model,shard=run['shard'],config_sha256=sha(out/'config.json'),
                predictions_sha256=cfg['predictions_sha256'],gpu_hours=cfg['gpu_hours'],
                code_sha256=cfg['code_sha256'],model_manifest_sha256=cfg['model_manifest_sha256']))
        assert len(index)==6064
        for ct in ['MVRR','NPZ','NPS','NPVP']:
            for cond in ['gp','control']:
                qa=[r for r in mothers if r['task_kind']=='QA_PLAIN' and r['construction']==ct and r['condition']==cond]
                grammar=[r for r in mothers if r['task_kind']=='GRAM_ACCEPT' and r['construction']==ct and r['condition']==cond]
                for op in ['QA_STRICT','QA_RECOVER','QA_PLAIN','GRAM_ACCEPT']:
                    rr=grammar if op=='GRAM_ACCEPT' else qa
                    rr=[meta[r['item_id']] for r in rr]
                    targets=['source'] if op=='GRAM_ACCEPT' else ['initial','final','all']
                    for target in targets:
                        sub=[r for r in rr if target in ['source','all'] or r['analysis_question_target']==target]
                        for metric in metrics:
                            vals=[sum(float(index[r['item_id'],op,mp][metric]) for mp in [0,1])/2 for r in sub]
                            panels.append(dict(model=model,construction=ct,condition=cond,operation=op,target=target,
                                metric=metric,**estimate(sub,vals,seed=87)))
                        raw=[index[r['item_id'],op,mp] for r in sub for mp in [0,1]]
                        counts.append(dict(model=model,construction=ct,condition=cond,operation=op,target=target,
                            raw_tasks=len(raw),valid=sum(p['valid'] for p in raw),known_correct=sum(p['known_correct'] is True for p in raw),
                            known_mismatches=sum(p['differs_from_forced'] is True for p in raw),caps=sum(p['cap'] for p in raw),
                            label_counts=dict(collections.Counter(p['label'] or 'UNKNOWN' for p in raw)),
                            mean_forced_choice_mass=sum(p['forced_choice_mass'] for p in raw)/len(raw) if raw else None))
                    noise.append(dict(model=model,construction=ct,condition=cond,operation=op,
                        mapping_mismatch=sum(index[r['item_id'],op,0]['label']!=index[r['item_id'],op,1]['label'] for r in rr)/len(rr)))
                    if op=='GRAM_ACCEPT':continue
                    groups=collections.defaultdict(list)
                    for r in rr:groups[r['source_unit']].append(r)
                    reps=[g[0] for _,g in sorted(groups.items())]
                    for metric in ['lower_correct','upper_correct','forced_correct']:
                        vals=[sum(all(index[r['item_id'],op,mp][metric] for r in groups[rep['source_unit']]) for mp in [0,1])/2 for rep in reps]
                        joint_panels.append(dict(model=model,construction=ct,condition=cond,operation=op,
                            metric=metric,target='joint_all_registered_QA',**estimate(reps,vals,seed=87)))
    version='v2-posthoc-option-semantics' if semantic else 'v1'
    out=root/f'actual-answer-map-{version}.json';assert not out.exists()
    out.write_text(json.dumps(dict(panels=panels,joint_panels=joint_panels,descriptive_counts=counts,
        mapping_noise=noise,runs=provenance,data_sha256=sha(root.parent/'E86/data-v1.jsonl'),
        analysis_registration='POST-HOC semantic parse of explicit A/B and A/B. Yes/No; preserves v1 literal-format readout' if semantic else 'Preregistered literal Yes/No readout',
        statistics='Mappings/QA average within Source; average Source within lexical cluster; 10000 paired bootstrap seed87. Counts are descriptive raw tasks.',
        limits='UNKNOWN or nonterminal output remains unresolved, bounded by lower/upper; forced score and cached greedy generation have different numerical/choice layouts. No latent parse claim.'),indent=2)+'\n')
    (root/f'complete-map-{version}.json').write_text(json.dumps(dict(map_sha256=sha(out),gpu_hours=sum(r['gpu_hours'] for r in provenance),
        new_outputs=18192,new_api_calls=0,panels=len(panels),joint_panels=len(joint_panels)),indent=2)+'\n')
    print('E87 COMPLETE',sha(out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--wait',action='store_true');p.add_argument('--semantic-options',action='store_true');a=p.parse_args()
    if a.wait:
        while True:
            runs=json.loads((a.root/'runner-pids-v1.json').read_text())
            if all((Path(r['out'])/'config.json').exists() and 'predictions_sha256' in json.loads((Path(r['out'])/'config.json').read_text()) for r in runs):break
            time.sleep(20)
    analyze(a.root,a.semantic_options)
