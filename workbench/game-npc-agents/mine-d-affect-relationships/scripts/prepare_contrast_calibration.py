#!/usr/bin/env python3
"""Freeze a source-state/behavior readout calibration from already saved ArcANE runs."""
import argparse
from collections import defaultdict,Counter
import hashlib
import json
from pathlib import Path

DECISION={'benjamin_franklin','deborah_read_franklin','duke_and_duchess','edmond_dantes','louis_trevelyan','mary_barfoot','monica_madden','sanson_carrasco','sir_marmaduke_rowley','william_franklin'}
STRATEGY={'alice_madden','anna_karenina','don_quixote','emily_trevelyan','fernand_mondego','mercedes','rhoda_nunn','sancho_panza'}
RUBRIC='''Compare two roleplay continuations of the SAME scenario/question under two supplied current character states, A and B.
Treat the supplied states as the conditions; do not replace them with remembered canon or infer a missing chapter.
Read observable actions, spoken commitments, or interpersonal response strategies. Unspoken thoughts, a recap of past facts,
psychological labels, response length, and literary fluency alone do not establish a behavioral contrast.
First decide whether there is an observable behavioral contrast. Then decide whether the two responses admit a defensible
one-to-one matching to states A/B. Multiple responses can be appropriate; if both fit both states, both fit only one state,
or the difference is not enough to establish a mapping, say underdetermined. Never invent a difference between identical responses.
Return one JSON object: {"observable_contrast": boolean, "mapping": "A1_B2" or "A2_B1" or "underdetermined",
"quotes": [{"response": 1 or 2, "quote": "exact short quotation from that response"}], "reason": "brief explanation"}.
For a definite mapping, quote behavioral evidence from BOTH responses. For underdetermined, quotes may be empty.
No Markdown. A systematic reverse mapping is not absence of sensitivity; this instrument measures source-state correspondence,
not uniquely correct psychology, episode recall, or the causal effect of a lived experience.'''


def read(p):return [json.loads(x) for x in p.read_text().splitlines()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text_sha(s):return hashlib.sha256(s.encode()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    root=Path(a.asset_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    cohort=root/'data/arcane_D-E07_v2/tasks.jsonl';original=root/'data/arcane_D-E01/tasks.jsonl';reference=root/'data/arcane_D-E01/references.jsonl'
    groups=defaultdict(list)
    for row in read(cohort):groups[row['trial']['probe_id']].append(row['trial'])
    templates={(r['trial']['probe_id'],r['trial']['phase_idx']):r for r in read(original) if r['mode']=='arc'}
    refs={r['trial_id']:r['reference'] for r in read(reference)}
    files={'qwen3_8b_arc':root/'runs/D-E01/qwen3_8b/responses.jsonl',
           'arcane_8b_dpo_arc':root/'runs/D-E01/arcane_8b_dpo/responses.jsonl',
           'qwen3_32b_arc':root/'runs/D-E03/qwen3_32b/responses.jsonl'}
    actors={name:{(r['probe_id'],r['phase_idx']):r for r in read(file) if r.get('mode')=='arc'} for name,file in files.items()}
    tasks=[];bindings=[];excluded=[]
    for probe,trials in sorted(groups.items()):
        pair=[min(trials,key=lambda t:t['phase_idx']),max(trials,key=lambda t:t['phase_idx'])]
        assert pair[0]['phase_idx']!=pair[1]['phase_idx']
        assert pair[0]['scenario']==pair[1]['scenario'] and pair[0]['question']==pair[1]['question']
        states=[];ref_responses=[];pairs={name:[] for name in files};missing_axis=False
        for trial in pair:
            template=templates[probe,trial['phase_idx']]
            context=json.loads(template['messages'][0]['content'].split('<context>\n',1)[1].rsplit('\n</context>',1)[0])
            axes=context.get('intrapersonal_axes',[])+context.get('relational_axes',[])
            axis=next((x for x in axes if x['axis_id']==trial['axis_id']),None)
            if axis is None:
                excluded.append(dict(probe_id=probe,novel=trial['novel'],axis_id=trial['axis_id'],phase_idx=trial['phase_idx'],
                    reason='The actual saved Arc actor input has no matching axis state; cannot serve as an explicit-state positive control'))
                missing_axis=True;break
            phase=axis['trajectory'][trial['phase_idx']]
            assert phase['phase']==trial['phase_label']
            states.append(phase['position_description'])
            ref=refs[probe+'__p'+str(trial['phase_idx'])]
            ref_responses.append('Action: '+ref['gt_action']+'\nSpeech: '+str(ref.get('gt_speech') or '(None)'))
            for name,index in actors.items():
                row=index[probe,trial['phase_idx']]
                assert not row.get('error') and row['finish_reason']=='stop' and row['response'].strip()
                assert row['prompt_system']==template['messages'][0]['content'] and row['prompt_user']==template['messages'][1]['content']
                pairs[name].append(row['response'])
        if missing_axis:continue
        slug=pair[0]['character_slug'];stratum='decision' if slug in DECISION else 'strategy' if slug in STRATEGY else 'overlap_or_expression'
        pairs['reference']=ref_responses
        duplicate=int(text_sha('D-E13-null|'+probe),16)%2
        pairs['identical_reference']=[ref_responses[duplicate]]*2
        state_order=[0,1] if int(text_sha('D-E13-state-order|'+probe),16)%2==0 else [1,0]
        for material,responses in pairs.items():
            for orientation in [0,1]:
                response_order=[0,1] if orientation==0 else [1,0]
                body=dict(character=pair[0]['character'],scenario=pair[0]['scenario'],question=pair[0]['question'],
                    state_A=states[state_order[0]],state_B=states[state_order[1]],
                    response_1=responses[response_order[0]],response_2=responses[response_order[1]])
                expected=None if material=='identical_reference' else 'A1_B2' if state_order[0]==response_order[0] else 'A2_B1'
                tasks.append(dict(task_id=probe+'/'+material+'/'+str(orientation),probe_id=probe,novel=pair[0]['novel'],
                    character_slug=slug,material=material,orientation=orientation,stratum=stratum,expected_mapping=expected,
                    messages=[dict(role='system',content=RUBRIC),dict(role='user',content=json.dumps(body,ensure_ascii=False))]))
        bindings.append(dict(probe_id=probe,novel=pair[0]['novel'],character=pair[0]['character'],stratum=stratum,
            phase_indices=[t['phase_idx'] for t in pair],state_hashes=list(map(text_sha,states)),
            candidate_hashes={k:list(map(text_sha,v)) for k,v in pairs.items()}))
    assert len(bindings)+len(excluded)==25 and len(tasks)==len(bindings)*10
    tasks.sort(key=lambda t:text_sha('D-E13-call-order|'+t['task_id']))
    (out/'tasks.jsonl').write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in tasks))
    manifest=dict(experiment='D-E13',n_candidate_probes=25,n_probes=len(bindings),n_books=len({x['novel'] for x in bindings}),n_requests=len(tasks),
        source_exclusions=excluded,
        n_primary_behavior_probes=sum(x['stratum']!='overlap_or_expression' for x in bindings),
        strata=dict(Counter(x['stratum'] for x in bindings)),task_sha256=sha(out/'tasks.jsonl'),rubric_sha256=text_sha(RUBRIC),
        source_files={str(p.relative_to(root)):sha(p) for p in [cohort,original,reference,*files.values()]},
        actor_records_complete_and_input_matched=True,actor_model_calls=0,bindings=bindings,
        scope='Calibration on already observed explicit phase-state controls. No lived experience was intervened on; not a causal adaptation result.')
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ['bindings','source_files']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
