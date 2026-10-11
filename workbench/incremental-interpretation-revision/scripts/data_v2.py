"""E52 published materials, immutable source gold and explicit semantic missingness."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

from data import CACHE, SOURCES, sha, verified_root, write_jsonl
from sap import load_sap


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def table(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def make_row(**kwargs):
    row = dict(control_type=None, question_target='other', disamb_word_index=None,
               amb_span=None, step5_status='unannotated', genuine=None,
               question_format='yn', options=['Yes', 'No'], gold=None,
               source_gold=None, source_revision=None, source_sha256=None)
    row.update(kwargs)
    row['sentence_sha256'] = digest(row['sentence'])
    row['input_sha256'] = digest(json.dumps(row, sort_keys=True, ensure_ascii=False))
    return row


def build(cache=CACHE):
    root = verified_root(cache, 'amouyal')
    rows = []
    constructions = {'extended_gardenpath_experiments': 'NPZ',
                     'nps_human_base_data': 'NPS', 'npvp_human_base_data': 'NPVP',
                     'reduced_relative_human_base_data': 'MVRR',
                     'depth_charge_human_base_data': 'DEPTH',
                     'double_center_human_base_data': 'DOUBLE', 'gordon_exp_new': 'INTERFERENCE'}
    for name, construction in constructions.items():
        path = root/'data'/f'{name}.csv'
        for i, r in enumerate(table(path)):
            is_gp = not r['sent_type'].lower().startswith('nongp') and 'non' not in r['sent_type'].lower()
            # No assumption that each file's hard condition is named *gp*.
            if construction in ('DEPTH', 'DOUBLE', 'INTERFERENCE'):
                is_gp = {'DEPTH': r['sent_type'] == 'depth_charge',
                         'DOUBLE': r['sent_type'] == 'double_center_embedded',
                         'INTERFERENCE': r['sent_type'] == 'interference'}[construction]
            sid = r['set_id'] if construction == 'NPZ' else r['set_id'].rsplit('_', 1)[0]
            qt = r['quest_type'].lower()
            target = 'initial' if qt == 'gp_question' else ('final' if qt == 'simple_question' else 'other')
            options = ['Yes', 'No'] if r['correct_answer'] in ('Yes', 'No') else [r['correct_answer'], r['incorrect_answer']]
            row = make_row(item_id=f'amouyal:{name}:{i}', source='amouyal',
                construction=construction, pair_id=f'amouyal:{construction}:{sid}',
                cluster_id=f'amouyal:{construction}:{sid}', condition='gp' if is_gp else 'control',
                control_type='clause_reorder' if construction == 'NPZ' else
                    {'NPS': 'that', 'MVRR': 'unreduced', 'NPVP': 'morphology'}.get(construction, 'author_control'),
                sentence=r['sentence'], question=r['question'], question_target=target,
                question_format='yn' if options == ['Yes', 'No'] else '2opt', options=options,
                gold=options.index(r['correct_answer']), source_gold=r['correct_answer'],
                source_row=i, source_set_id=r['set_id'], source_sent_type=r['sent_type'],
                source_question_type=r['quest_type'], source_revision=SOURCES['amouyal'][1],
                source_sha256=sha(path), source_gp_noun=r.get('gp_noun'),
                source_gp_verb=r.get('gp_verb'), source_reduced_verb=r.get('reduced_verb'),
                subtype=r['sent_type'].split('_', 1)[1] if construction == 'NPZ' else None,
                needs_revision=construction in ('NPZ', 'NPS', 'NPVP', 'MVRR'))
            rows.append(row)
    for r in load_sap(cache):
        rows.append(make_row(item_id=r['item_id'], source='sap', construction=r['construction'],
            pair_id=f'sap:{r["construction"]}:{r["source_row_id"]}', cluster_id=r['pair_id'],
            condition='gp' if r['condition'] == 'gp' else 'control', control_type=r['cue_type'],
            sentence=r['sentence'], question=r['question'], question_format='yn' if r['source_yes_no'] else '2opt',
            options=[r['option0'], r['option1']], gold=r['source_answer'], source_gold=r['gold_answer_text'],
            question_target='initial' if r['source_target_xlsx'] else 'other',
            disamb_word_index=r['disambiguator_index'], source_row=r['source_row_id'],
            source_revision=SOURCES['sap'][1], source_sha256=sha(cache/'upstream/sap-discovery/Items for all subsets.xlsx'),
            source_target_csv=r['source_target_csv'], source_target_xlsx=r['source_target_xlsx'], needs_revision=True))
    root = cache/'upstream/cehakova2025'
    audit = json.loads((root/'audit.json').read_text())
    path = root/'stimuli/exp_items.csv'
    expected = next(f['sha256'] for f in audit['files'] if f['name'] == 'exp_items.csv')
    assert sha(path) == expected
    for i, r in enumerate(table(path)):
        construction, condition, question_type = r['condition'].split('-')
        rows.append(make_row(item_id=f'cehakova2025:{i}', source='cehakova2025',
            construction=construction, pair_id=f'cehakova2025:{r["item"]}',
            cluster_id=f'cehakova2025:{r["item"]}', condition='gp' if condition == 'gp' else 'control',
            control_type='comma' if construction == 'NPZ' else 'unreduced',
            sentence=r['sentence'], question=r['question'], gold=int(r['correct']),
            source_gold=['Yes', 'No'][int(r['correct'])], source_row=i, source_set_id=r['item'],
            question_target='initial' if question_type == 'ambmis' else 'final',
            source_question_type=question_type, source_revision='16358492:v1', source_sha256=expected,
            needs_revision=True))
    return rows


def validate(rows):
    assert len({r['item_id'] for r in rows}) == len(rows)
    paired = collections.defaultdict(list)
    for r in rows:
        assert r['gold'] in range(len(r['options']))
        assert r['options'][r['gold']] == r['source_gold']
        assert r['sentence_sha256'] == digest(r['sentence'])
        paired[r['pair_id']].append(r)
    for pid, group in paired.items():
        assert {r['condition'] for r in group} == {'gp', 'control'}, pid
        for r in group:
            counterpart = [q for q in group if q['condition'] != r['condition'] and q['question'] == r['question']]
            # Interference changes the entity in the query alongside its sentence.
            r['matched_question_exact'] = bool(counterpart)
            r['pairing_warning'] = None if counterpart else 'Author control changes question wording; exclude from exact same-question contrasts.'
    return dict(rows=len(rows), pairs=len(paired), clusters=len({r['cluster_id'] for r in rows}),
                sources=dict(collections.Counter(r['source'] for r in rows)),
                constructions=dict(collections.Counter(r['construction'] for r in rows)),
                gp_pairs=len({r['pair_id'] for r in rows if r['needs_revision']}),
                annotation_scope='New T1/T2/T3 required only for controlled GP materials; general natural corpora are not re-audited.')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--cache', type=Path, default=CACHE)
    ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    rows = build(args.cache); report = validate(rows); write_jsonl(args.out, rows)
    report['data_sha256'] = sha(args.out)
    args.out.with_suffix('.manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
