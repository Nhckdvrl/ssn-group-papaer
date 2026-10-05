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
                            readout_kind='asserted_proposition', sentence=sentence,
                            condition='isolated', cue_type='isolated_main_clause',
                            ambiguity_start=None, disambiguator_index=None,
                            source_derivation='NP/Z + optional Extension + Verb + Rest'))
    assert len(out)==168 and len({r['item_id'] for r in out})==len(out)
    assert all(r['gold'] is None for r in out)
    return out


if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--cache',type=Path,default=CACHE)
    p.add_argument('--out',type=Path,required=True); a=p.parse_args()
    assert not a.out.exists(), 'Use an immutable candidate version'
    rows=build(a.cache); write_jsonl(a.out,rows)
    print(json.dumps(dict(rows=len(rows),sha256=sha(a.out),gold_labels=0,
                         upstream_lexical_sets=['NPZ:1','NPZ:2','NPZ:3'])))
