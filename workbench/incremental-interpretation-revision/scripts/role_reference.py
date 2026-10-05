"""E11: diagnose NP reference in extended-subject questions, without agent gold.

Only the first three upstream NPZ lexical sets are used. Candidate questions
are independently annotated before frozen inference; no model result selects
questions or variants. Source sentences remain byte-identical to E01.
"""
import argparse
import copy
import json
from pathlib import Path
from data import CACHE, sha, write_jsonl
from stimuli import join, terminal


def build(cache):
    components = {r['pair_id']: r for r in map(json.loads, (cache/'normalized/jurayj-components.jsonl').read_text().splitlines())}
    source = list(map(json.loads, (cache/'normalized/jurayj.jsonl').read_text().splitlines()))
    out = []
    for r in source:
        if r['pair_id'] not in ('NPZ:1', 'NPZ:2', 'NPZ:3'):
            continue
        original = dict(r, item_id='E11:'+r['item_id'], gold=None,
                        gold_status='pending_external_review', diagnostic_only=True,
                        parent_item_id=r['item_id'], readout_version='np_reference_v1')
        out.append(original)
        if r['question_type'] != 'intended':
            continue
        comp = components[r['pair_id']]['components']
        subject = join([comp['NP/Z']] + ([comp['Extension']] if r['extended'] else []))
        vp = join([comp['Verb'], comp['Rest']])
        candidates = {
            'full_subject': f'In this sentence, is "{subject}" the grammatical subject of the verb phrase "{vp}"?',
            'subject_head': f'In this sentence, is "{comp["NP/Z"].split()[-1]}" the head noun of the grammatical subject of the verb phrase "{vp}"?',
        }
        for kind, question in candidates.items():
            out.append(dict(original, item_id=original['item_id']+':'+kind,
                            question_type=kind, question=question, readout_kind='syntactic_role'))
        # A direct, source-component clause removes the earlier competing verb.
        # This is a constructed control: its validity is externally reviewed too.
        if r['condition'] == 'gp':
            sentence = terminal(join([subject, vp]))
            for template in [original] + [x for x in out[-2:]]:
                control = copy.deepcopy(template)
                control.update(item_id=template['item_id']+':isolated', sentence=sentence,
                               condition='isolated', cue_type='isolated_main_clause',
                               ambiguity_start=None, disambiguator_index=None,
                               source_derivation='NP/Z + optional Extension + Verb + Rest')
                out.append(control)
            semantic = next(x for x in source if x['pair_id']==r['pair_id'] and x['condition']=='gp'
                            and x['extended']==r['extended'] and x['question_type']=='intended_semantic')
            out.append(dict(original, item_id='E11:'+semantic['item_id']+':isolated',
                            question=semantic['question'], question_type='intended_semantic',
                            parent_item_id=semantic['item_id'],
                            readout_kind='asserted_proposition', sentence=sentence,
                            condition='isolated', cue_type='isolated_main_clause',
                            ambiguity_start=None, disambiguator_index=None,
                            source_derivation='NP/Z + optional Extension + Verb + Rest'))
    assert len(out)==168 and len({r['item_id'] for r in out})==len(out)
    assert all(r['gold'] is None for r in out)
    return out


def analyze_reference(rows):
    from analyze import estimate
    from revision_map import analyze_revision
    result=analyze_revision(rows)
    contrasts={}
    for stratum in ('eligible','acceptable'):
        subset=[r for r in rows if stratum=='eligible' or r['clean_stratum']]
        index={(r['pair_id'],r['prompt_id'],r['condition'],r['extended'],r['question_type']):r for r in subset}
        assert len(index)==len(subset)
        def measure(values):
            if len(values)<2:
                return dict(n_sets=len(values),estimate=next(iter(values.values()),None),ci95=None,pair_ids=sorted(values))
            return dict(estimate([values[s] for s in sorted(values)]),pair_ids=sorted(values))
        def values(pid,c,e,q):
            return {sid:index[(sid,pid,c,e,q)]['p_yes'] for sid in sorted({r['pair_id'] for r in subset})
                    if (sid,pid,c,e,q) in index}
        def diff(a,b):return {s:a[s]-b[s] for s in a.keys()&b.keys()}
        for pid in sorted({r['prompt_id'] for r in subset}):
            for c in sorted({r['condition'] for r in subset}):
                for q in ('full_subject','subject_head','intended_semantic'):
                    for e in (False,True):
                        contrasts[f'{stratum}/{pid}/{c}/{int(e)}/{q}_minus_original_role']=measure(diff(values(pid,c,e,q),values(pid,c,e,'intended')))
                    long=diff(values(pid,c,True,q),values(pid,c,True,'intended'))
                    short=diff(values(pid,c,False,q),values(pid,c,False,'intended'))
                    contrasts[f'{stratum}/{pid}/{c}/extension_by_readout/{q}']=measure(diff(long,short))
    matched=[]
    by_prompt={}
    for r in rows:by_prompt.setdefault(r['prompt_sha256'],[]).append(r)
    for group in by_prompt.values():
        if len(group)>1:
            matched.append(max(r['p_yes'] for r in group)-min(r['p_yes'] for r in group))
    result.update(reference_contrasts=contrasts,
                  same_prompt_repeat=dict(groups=len(matched),max_probability_delta=max(matched,default=None)),
                  audit_scope='Independent advisory probability diagnostics; all gold/correct labels null; at most three lexical sets.')
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--cache',type=Path,default=CACHE)
    p.add_argument('--out',type=Path,required=True); a=p.parse_args()
    assert not a.out.exists(), 'Use an immutable candidate version'
    rows=build(a.cache); write_jsonl(a.out,rows)
    print(json.dumps(dict(rows=len(rows),sha256=sha(a.out),gold_labels=0,
                         upstream_lexical_sets=['NPZ:1','NPZ:2','NPZ:3'])))
