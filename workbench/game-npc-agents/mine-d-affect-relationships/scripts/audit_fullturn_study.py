#!/usr/bin/env python3
"""Offline D-E12 final-data/adapter/score audit; never starts training or inference."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

DIMENSIONS=['experience_interpretation','justified_change_or_preservation','goals_and_relationships',
            'speech_action_alignment','character_expression']


def load(p):return json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in p.read_text().splitlines()]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def same(a,b):
    if a is None or b is None:assert a is b
    else:assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(a,b)


def readable_original_scores(text):
    """POST-HOC numeric-readability sensitivity; never replaces the registered parser."""
    text=text.strip()
    if text.startswith('```'):text=text.split('\n',1)[-1].rsplit('```',1)[0].strip()
    if any(len(re.findall('"'+re.escape(d)+'"\\s*:',text))!=1 for d in DIMENSIONS):return None
    mode='full_json'
    try:value,_=json.JSONDecoder().raw_decode(text)
    except ValueError:
        at=text.find('"reason"');prefix=text[:at].rstrip() if at>=0 else ''
        if not prefix.endswith(','):return None
        try:value=json.loads(prefix[:-1]+'}')
        except ValueError:return None
        if set(value)!=set(DIMENSIONS):return None
        mode='complete_numeric_prefix_before_malformed_reason'
    if not isinstance(value,dict) or any(type(value.get(d)) not in [int,float] or not 1<=value[d]<=5 for d in DIMENSIONS):return None
    return dict(scores={d:value[d] for d in DIMENSIONS},mode=mode)


def complete_book_values(primary,books,dimension=None):
    groups=defaultdict(list)
    for x in primary:
        scores=x['result']['scores'];groups[x['book_name'],x['episode_id']].append(scores[dimension] if dimension else statistics.mean(scores.values()))
    return [statistics.mean(statistics.mean(v) for (book,_),v in groups.items() if book==b) for b in books]


def numeric_sensitivity(primary,raw_selected,books,baseline):
    import copy
    import numpy as np
    readable=[];recovered=[]
    for row in primary:
        raw=raw_selected[row['task_id']];value=readable_original_scores(raw['response'])
        if row['valid']:assert value and value['scores']==row['result']['scores']
        if value:
            r=copy.deepcopy(row);r.update(valid=True,result=dict(scores=value['scores']));readable.append(r)
            if not row['valid']:recovered.append(dict(task_id=row['task_id'],scores=value['scores'],mode=value['mode'],
                selected_attempt=row['selected_attempt'],response_sha256=hashlib.sha256(raw['response'].encode()).hexdigest()))
    result=dict(post_hoc=True,registered_primary_unchanged=True,no_model_calls=True,no_manual_rescoring=True,
        rule='Each of the five named numeric fields occurs exactly once, is in [1,5], and forms a complete JSON object before a malformed final reason. Ambiguous or absent fields are never invented.',
        strict_primary_valid=sum(x['valid'] for x in primary),readable_primary=len(readable),recovered=recovered)
    if len(readable)==len(primary):
        current=np.array(complete_book_values(readable,books));samples=np.random.default_rng(173).integers(0,len(books),(10000,len(books)))
        result['macro_quality']=float(current.mean());result['paired_vs']={}
        result['by_book_quality']={b:float(v) for b,v in zip(books,current)}
        result['dimensions']={d:statistics.mean(complete_book_values(readable,books,d)) for d in DIMENSIONS}
        same(statistics.mean(result['dimensions'].values()),result['macro_quality'])
        for name,old in baseline['systems'].items():
            delta=current-np.array([statistics.mean(old['by_book'][b].values()) for b in books])
            result['paired_vs'][name]=dict(mean=float(delta.mean()),ci95=np.quantile(delta[samples].mean(1),[.025,.975]).tolist())
    bounds=[]
    for score in [1,5]:
        filled=copy.deepcopy(primary)
        for r in filled:
            if not r['valid']:r['result']=dict(scores={d:score for d in DIMENSIONS})
        bounds.append(statistics.mean(complete_book_values(filled,books)))
    result['unknown_score_range_sensitivity']=dict(macro_interval=bounds,
        delta_vs_base_interval=[v-baseline['systems']['base']['macro_quality'] for v in bounds],
        meaning='All original 87 contexts and their original role/book weights retained. These are deterministic [1,5] missing-score bounds, not confidence intervals or filled primary labels.')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    root=a.asset_root;run=root/'runs/D-E12';train=run/'train_multitask_fullturn';data=root/'data/training_D-E12'
    if not load(run/'finish_status.json').get('complete'):raise ValueError('D-E12 final execution is not complete; no partial audit output')
    tm=load(train/'metadata.json');assert tm['complete'] and tm['completed_steps']==tm['planned_steps']==261
    manifest=load(data/'manifest.json');assert sha(data/'manifest.json')==tm['source_manifest_sha256']
    for name,v in manifest['files'].items():
        assert (data/name).stat().st_size==v['bytes'] and sha(data/name)==v['sha256'],name
    entries={x['row_id']:x for x in rows(data/'entries.jsonl')};order=load(train/'training_order.json')
    old_order=load(root/'runs/D-E10/train_multitask_v2/training_order.json');assert order==old_order[:len(order)]
    assert len(order)==tm['seen_examples']==tm['planned_examples']==16684
    counts=Counter(entries[i]['task'] for i in order);assert dict(counts)==tm['processed_tasks']
    forward=sum(entries[i]['length'] for i in order);targets=sum(entries[i]['target_length'] for i in order)
    assert forward==tm['seen_forward_tokens']==tm['planned_forward_tokens']==85900222
    assert targets==tm['planned_target_tokens']==4726227
    interaction_turns=sum(entries[i]['assistant_turns'] for i in order if entries[i]['task']=='interaction_generation');assert interaction_turns==15195
    recorded_final=tm['final_checkpoint'];final=train/'final'
    assert Path(recorded_final).parts[-3:]==final.parts[-3:]
    adapter_sha={p.name:sha(p) for p in final.iterdir() if p.name in ['adapter_model.safetensors','adapter_config.json']}
    assert len(adapter_sha)==2
    pipe=run/'system_multitask_sft';pm=load(pipe/'metadata.json');assert pm['complete'] and pm['adapter']==recorded_final
    episodes=rows(root/'data/evaluation_D-E10/episodes.jsonl');E={x['episode_id']:x for x in episodes}
    questions={q['question_id']:(e,q) for e in episodes for q in e['queries']};assert len(questions)==87 and len(E)==47
    outputs=rows(pipe/'outputs.jsonl');assert len(outputs)==87 and {r['question_id'] for r in outputs}==set(questions)
    states={r['episode_id']:r for r in rows(pipe/'states.jsonl')};motives={r['episode_id']:r for r in rows(pipe/'motivations.jsonl')}
    assert set(states)==set(motives)==set(E)
    actor_tasks=rows(pipe/'actor_tasks.jsonl');assert len(actor_tasks)==87
    for t in actor_tasks:
        e,q=questions[t['question_id']];assert t['messages'][1:]==q['messages'][1:]
        text=t['messages'][0]['content'].split('## Your Character State\n',1)[1].lstrip()
        body,_=json.JSONDecoder().raw_decode(text);assert list(body)==[e['role']]
        own=body[e['role']];s=states[e['episode_id']]['state']
        assert own['profile']==s['profile'] and own['hidden_tracker']==s['hidden_tracker']
        assert own['motivation']==motives[e['episode_id']]['motivation']
    stage_calls=Counter();usage=Counter();allraw=[]
    for file in sorted(run.rglob('responses.jsonl')):
        records=rows(file);assert len(records)==len({r['task_id'] for r in records})
        meta=load(file.parent/'metadata.json');name=str(file.parent.relative_to(run));stage_calls[name]=len(records)
        if file.is_relative_to(pipe) and records:
            assert meta['args']['adapter']==recorded_final and meta['adapter_files']==adapter_sha
        for r in records:
            assert len(r['generated_token_ids'])==r['usage']['completion_tokens']
            usage.update(r['usage']);allraw.append(r)
    for r in outputs:
        assert any(x['task_id']==r['task_id'] and x['generated_token_ids']==r['generated_token_ids'] and x['response']==r['response'] for x in allraw)
    judge=run/'judge';jt=rows(judge/'tasks.jsonl');old_jt=rows(root/'runs/D-E10/judges/base/tasks.jsonl')
    old={(r['question_id'],r['repeat']):r for r in old_jt};assert len(jt)==99 and {(x['question_id'],x['repeat']) for x in jt}==set(old)
    omit=lambda x:{k:v for k,v in x.items() if k not in ['candidate_motivation','candidate_reply']}
    for t in jt:
        b=old[t['question_id'],t['repeat']];assert t['messages'][0]==b['messages'][0]
        assert omit(json.loads(t['messages'][1]['content']))==omit(json.loads(b['messages'][1]['content']))
    selected=rows(judge/'selected.jsonl');primary=[x for x in selected if not x['repeat']]
    first={x['task_id']:x for x in rows(judge/'first/responses.jsonl')}
    recovery={x['task_id']:x for x in rows(judge/'recovery/responses.jsonl')} if (judge/'recovery/responses.jsonl').exists() else {}
    task_lookup={x['task_id']:x for x in jt}
    for x in selected:
        raw=recovery.get(x['task_id'],first[x['task_id']]);assert raw['messages']==task_lookup[x['task_id']]['messages']
        if x['valid']:
            text=raw['response'].strip()
            if text.startswith('```'):text=text.split('\n',1)[-1].rsplit('```',1)[0].strip()
            value,_=json.JSONDecoder().raw_decode(text)
            assert {d:value[d] for d in DIMENSIONS}==x['result']['scores']
    assert len(primary)==87 and {x['question_id'] for x in primary}==set(questions)
    valid=[x for x in primary if x['valid']];byrole=defaultdict(lambda:defaultdict(list))
    for x in valid:
        for d in DIMENSIONS:byrole[x['book_name'],x['episode_id']][d].append(x['result']['scores'][d])
    result_dir=Path(__file__).resolve().parent.parent/'results';reported=load(result_dir/'D-E12-summary.json')
    baseline=load(result_dir/'D-E10-summary.json');books=sorted({e['book'] for e in episodes})
    bybook={}
    for b in books:
        values=[v for (book,_),v in byrole.items() if book==b]
        bybook[b]={d:statistics.mean(statistics.mean(v[d]) for v in values) if values else None for d in DIMENSIONS}
    assert len(valid)==reported['valid_primary']
    for b in books:
        for d in DIMENSIONS:same(bybook[b][d],reported['by_book'][b][d])
    macro=statistics.mean(statistics.mean(bybook[b].values()) for b in books) if len(valid)==87 else None
    same(macro,reported['macro_quality'])
    if macro is not None:
        import numpy as np
        samples=np.random.default_rng(173).integers(0,6,(10000,6));cur=np.array([statistics.mean(bybook[b].values()) for b in books])
        for name,old_group in baseline['systems'].items():
            delta=cur-np.array([statistics.mean(old_group['by_book'][b].values()) for b in books]);r=reported['paired_vs'][name]
            same(float(delta.mean()),r['mean'])
            for x,y in zip(np.quantile(delta[samples].mean(1),[.025,.975]),r['ci95']):same(float(x),y)
    else:assert not reported['paired_vs']
    likelihood=rows(run/'likelihood/scores.jsonl');assert len(likelihood)==87 and {x['question_id'] for x in likelihood}==set(questions)
    lm=load(run/'likelihood/metadata.json');assert lm['complete'] and not lm['args'].get('adapter')
    old_lm=load(root/'runs/D-E10/likelihood/metadata.json')
    assert all(lm['args'][k]==old_lm['args'][k] for k in ['checkpoint','revision'])
    nll=defaultdict(list)
    for x in likelihood:nll[x['book_name'],x['trajectory_id']].append(x['mean_target_nll'])
    value=statistics.mean(statistics.mean(statistics.mean(v) for (book,_),v in nll.items() if book==b) for b in books);same(value,reported['fixed_consumer_nll'])
    sizes=[len(x['response'].split()) for x in outputs]
    audit=dict(experiment='D-E12',post_hoc=True,model_calls=0,complete=True,
        training=dict(examples=len(order),forward_tokens=forward,target_tokens=targets,tasks=dict(counts),interaction_assistant_turns=interaction_turns,
                      cache_hashes_verified=True,training_order_matches_old_prefix=True,final_adapter_sha256=adapter_sha),
        information_paths=dict(actor_uses_final_selected_state_and_motivation=True,source_dialogue_preserved=True,judge_common_evidence_matches_D_E10=True),
        checks=dict(cohort_exact=True,loaded_adapters_match_final=True,selected_outputs_match_saved_generations=True,book_role_weighting_verified=True,registered_paired_intervals_recomputed=macro is not None,fixed_consumer_nll_recomputed=True),
        generation_attempts=dict(stage_calls),known_usage=dict(usage),n_outputs=len(outputs),valid_primary=len(valid),macro_quality=macro,
        response_words=dict(mean=statistics.mean(sizes),median=statistics.median(sizes),min=min(sizes),max=max(sizes)),
        summary_sha256=sha(result_dir/'D-E12-summary.json'),
        interpretation='Execution-agent offline verification, not independent human review. Same previously observed source cohort; original evidence-path and quality-vs-experience-effect limitations remain. Word counts are descriptive, not quality labels.')
    audit['numeric_readability_sensitivity']=numeric_sensitivity(primary,{x['task_id']:recovery.get(x['task_id'],first[x['task_id']]) for x in primary},books,baseline)
    a.out.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');print(json.dumps(audit,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
