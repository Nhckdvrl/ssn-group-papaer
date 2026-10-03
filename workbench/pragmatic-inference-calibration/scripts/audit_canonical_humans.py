#!/usr/bin/env python3
"""Reconstruct released human filtering; compare actual seen texts, never infer gold."""
import argparse
import ast
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def content(text, item=''):
    # Only presentation headers, not speaker labels or semantic material.
    s = norm(text)
    while re.match(r"^(?:Utterance|Dialogue|Scenario|Excerpt|Passage|Context):\s*", s):
        s = re.sub(r"^(?:Utterance|Dialogue|Scenario|Excerpt|Passage|Context):\s*", "", s)
    if item.startswith('some_all_'):
        s = re.sub(r'^A:\s*', '', s)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    up = args.root / 'upstream/ImplicatureX'
    def read(p):
        return pd.read_csv(up / p, comment='#').fillna('')
    canonical = read('data/datasets/implicatureX.csv').set_index('id')
    stimuli = read('data/crowdsourcing_annotation/experiment/stimuli.csv').set_index('id')
    prompts = read('data/prompts/prompts_implicatureX.csv')
    trials = read('data/crowdsourcing_annotation/raw/prolific_trials.csv')
    attention = read('data/crowdsourcing_annotation/raw/prolific_attention_checks.csv')
    published = read('data/crowdsourcing_annotation/prolific_responses.csv')
    good = attention.groupby('workerid').passed.mean()
    good = set(good[good >= .8].index)
    kept = trials[trials.workerid.isin(good)].copy()
    kept['seen'] = kept.datapoint.map(ast.literal_eval)
    kept['identifier'] = kept.seen.map(lambda x: x['identifier'])
    kept = kept[~kept.identifier.str.contains('instruction')].copy()
    kept['contains_cancellation'] = kept.identifier.str.contains('w_cancellation')
    kept['item_id'] = [i.removesuffix('_w_cancellation' if c else '_wo_cancellation')
                       for i, c in zip(kept.identifier, kept.contains_cancellation)]
    kept = kept[kept.item_id != 'some_all_8'].copy()
    cols = ['item_id', 'contains_cancellation', 'workerid', 'likelihood']
    def multiset(df):
        return Counter(tuple(r) for r in df[cols].itertuples(index=False, name=None))
    assert multiset(kept) == multiset(published), 'Published filtering not reproduced'
    assert not kept.duplicated(cols[:3]).any()
    assert kept.likelihood.between(1, 7).all()
    assert set(kept.item_id) == set(canonical.index) == set(prompts.id)
    assert len(canonical) == 271
    assert set(stimuli.index) - set(canonical.index) == {'some_all_8'}
    kept['z'] = kept.groupby('workerid').likelihood.transform(lambda s: (s-s.mean())/s.std())
    same_worker_both = kept.groupby(['item_id','workerid']).contains_cancellation.nunique()
    fields = ['context', 'utterance', 'implicature', 'cancellation']
    rows = []
    for item, r in canonical.iterrows():
        sr = stimuli.loc[item]
        identical = all(r[f] == sr[f] for f in fields)
        human = kept[kept.item_id == item]
        pr = prompts[prompts.id == item]
        assert pr.implicature.nunique() == 1 and pr.implicature.iloc[0] == r.implicature
        row = dict(item_id=item, phenomenon=r.implicature_type,
                   context=r.context, utterance=r.utterance, q=r.implicature,
                   cancellation=r.cancellation, stimulus_fields_exact=identical,
                   target_layer='UNADJUDICATED', cancellation_layer='UNADJUDICATED',
                   three_state_gold='UNADJUDICATED', conditions={})
        for c in [False, True]:
            h = human[human.contains_cancellation == c]
            model = pr[pr.contains_cancellation == c]
            assert len(h) and model.scenario.nunique() == 1
            seen = {(x['scenario'], x['implicature'], x['speaker-name']) for x in h.seen}
            assert len(seen) == 1, 'Participant seen texts differ within cell'
            scenario, q, speaker = next(iter(seen))
            mc = model.scenario.iloc[0]
            qs = norm(q) == norm(r.implicature)
            cs = content(scenario,item) == content(mc,item)
            row['conditions']['cancel' if c else 'baseline'] = dict(
                n=len(h), raw_mean=float(h.likelihood.mean()), raw_counts=h.likelihood.value_counts().sort_index().to_dict(),
                participant_z_mean=float(h.z.mean()), human_scenario=scenario,
                human_q=q, speaker=speaker, model_scenario=mc,
                q_exact=q == r.implicature, q_presentation_match=qs,
                scenario_presentation_match=cs)
        row['raw_cancel_delta'] = row['conditions']['cancel']['raw_mean']-row['conditions']['baseline']['raw_mean']
        row['z_cancel_delta'] = row['conditions']['cancel']['participant_z_mean']-row['conditions']['baseline']['participant_z_mean']
        row['text_match_both'] = all(v['q_presentation_match'] and v['scenario_presentation_match'] for v in row['conditions'].values())
        rows.append(row)
    local = args.root/'data/E66-canonical-human-audit'
    local.mkdir(parents=True, exist_ok=True)
    target = local/'items.jsonl'
    assert not target.exists(), 'Refuse raw audit overwrite'
    target.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    mismatch = {r['item_id']: {k: {x: v[x] for x in ['q_presentation_match','scenario_presentation_match']}
                             for k,v in r['conditions'].items()} for r in rows if not r['text_match_both']}
    groups = {}
    for ph in sorted({r['phenomenon'] for r in rows}):
        rs = [r for r in rows if r['phenomenon']==ph]
        delta = np.array([r['raw_cancel_delta'] for r in rs])
        draws = np.random.default_rng(0).choice(delta,(2000,len(delta)),replace=True).mean(1)
        groups[ph] = dict(n_items=len(rs), text_match=sum(r['text_match_both'] for r in rs),
                         mean_raw_likert_change=float(delta.mean()), item_bootstrap_ci95=np.quantile(draws,[.025,.975]).tolist(),
                         n_raw_decreases=int((delta<0).sum()), n_raw_increases=int((delta>0).sum()))
    paths = ['data/datasets/implicatureX.csv','data/prompts/prompts_implicatureX.csv',
             'data/crowdsourcing_annotation/prolific_responses.csv',
             'data/crowdsourcing_annotation/raw/prolific_trials.csv',
             'data/crowdsourcing_annotation/raw/prolific_attention_checks.csv',
             'data/crowdsourcing_annotation/experiment/stimuli.csv',
             'data/crowdsourcing_annotation/experiment/instructions.js',
             'data/crowdsourcing_annotation/experiment/experiment.html',
             'data/crowdsourcing_annotation/filter.ipynb', 'src/exps/generate_prompts.py']
    summary = dict(experiment='E66', upstream_commit='15d1c58d1d3cb8c198c07ae5c1e63531a672b10d',
                   hashes={p:sha(up/p) for p in paths}, raw_trials=len(trials),
                   raw_attention_workers=attention.workerid.nunique(), retained_workers=kept.workerid.nunique(),
                   released_response_rows=len(kept), released_filter_multiset_exact=True,
                   no_duplicate_item_condition_worker=True, same_worker_both_conditions=int((same_worker_both>1).sum()),
                   items=len(rows), canonical_stimulus_field_matches=sum(r['stimulus_fields_exact'] for r in rows),
                   fully_text_matched=sum(r['text_match_both'] for r in rows), mismatch=mismatch,
                   rating_counts=kept.likelihood.value_counts().sort_index().to_dict(),
                   ratings_per_cell_counts=kept.groupby(['item_id','contains_cancellation']).size().value_counts().sort_index().to_dict(),
                   by_phenomenon=groups, item_audit_path=str(target), item_audit_sha256=sha(target),
                   derived_controls={'baseline':'human ratings exist', 'cancel':'human ratings exist',
                                     'prior':'NO human norm; different question', 'irrelevant':'NO human norm',
                                     'negation':'NO human norm', 'strengthen':'NO human norm'},
                   limitations=['Likert not probability; no binary inference license inferred',
                                'Canonical/stimuli text corrections are recorded as differences, not hidden or assumed gold',
                                'Target/cancellation layers remain unadjudicated, not machine-assigned gold',
                                'Item-bootstrap intervals ignore shared participant dependence; descriptive only',
                                'Human reasonableness vs model True/False wording remains different'])
    args.output.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:summary[k] for k in ['items','released_response_rows','retained_workers','fully_text_matched','by_phenomenon']},ensure_ascii=False))


if __name__ == '__main__':
    main()
