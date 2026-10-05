"""E38/E39 paired family bootstrap; declared scopes and full condition reporting."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import CACHE, sha
from aspect_reference import read_run
from analyze_source_ablation import stat, diff


def average(vectors):
    assert vectors and all(v.keys() == vectors[0].keys() for v in vectors)
    return {f: float(np.mean([v[f] for v in vectors])) for f in vectors[0]}


def analyze(experiment, cache, reviews):
    cfg, rows = read_run(cache / 'runs' / (experiment + '-probability'))
    expected = {'E38': 3840, 'E39': 2880, 'E40': 1920, 'E43': 960, 'E45':1920}[experiment]
    assert len(rows) == expected
    parent = Path(__file__).resolve().parents[1] / 'results/E31-summary.json'
    parent_cohorts = json.loads(parent.read_text())['probability']['cohorts']
    e38 = experiment == 'E38'
    fields = ('fact_realization', 'selection_policy', 'candidate_order') if e38 else ('fact_realization', 'readout_actor_mode', 'boundary_marker')
    def condition(r):
        if e38:
            return tuple(r[k] for k in fields)
        return (r['fact_realization'], r['readout_actor_mode'], r.get('boundary_marker', 'old') if r['readout_actor_mode'] != 'original_activity' else 'old')
    conditions = sorted({condition(r) for r in rows})
    roles = ('initial_patient_only', 'reference_only') if e38 else ('source_patient_stated', 'other_patient_stated') if experiment in ('E40','E43','E45') else ('source_patient_only', 'other_patient_only')
    source_families = collections.defaultdict(set)
    for r in rows:
        source_families[r['verb_family']].add(r['pair_id'])
    count_per_source = expected // 24
    out = dict(experiment=experiment, raw_tasks=expected, analysis_code_sha256=sha(Path(__file__)),
               bootstrap_unit='12 verb families, two sources averaged before resampling', bootstrap_draws=10000,
               bootstrap_seed=20261005, units='bits', raw_config=cfg,
               probability=dict(cells={}, contrasts={}, cohorts={}, per_family={}),
               interpretation='Conditional string preference, not an event probability, hidden state, or ability error.')
    parent_path = Path(__file__).resolve().parents[1] / ('results/E40-summary.json' if experiment in ('E43','E45') else 'results/E39-summary.json' if experiment == 'E40' else 'results/E36-summary.json')
    parent_probability = json.loads(parent_path.read_text())['probability']
    out['parent_summary_sha256'] = sha(parent_path)
    for cohort in ('all', 'eligible', 'grammar_common', 'anchor_cross_clear', 'anchor_cross_acceptable', 'prior_and_ablation_faithful'):
        chosen = [r for r in rows if cohort != 'eligible' or r['eligible']]
        if cohort == 'grammar_common':
            chosen = [r for r in chosen if r['acceptable']]
        counts = collections.Counter(r['pair_id'] for r in chosen)
        keep = {f: sorted(sids) for f, sids in source_families.items() if all(counts[s] == count_per_source for s in sids)}
        if cohort in parent_cohorts:
            keep = {f: s for f, s in keep.items() if f in parent_cohorts[cohort]}
        if cohort == 'grammar_common':
            keep = {f: s for f, s in keep.items() if f in parent_probability['cohorts'][cohort]}
        out['probability']['cohorts'][cohort] = keep
        ix = {(r['pair_id'], condition(r), r['role_evidence'], r['readout_frame'], r['target_kind']): r for r in chosen}
        assert len(ix) == len(chosen)
        vectors = {}
        def record(section, key, vector):
            out['probability'][section][cohort + '/' + key] = stat(vector)
            vectors[key] = vector
        for c in conditions:
            name = '/'.join(c)
            v = {}
            for frame in ('activity', 'neutral_entity'):
                for role in roles:
                    vv = {}
                    for f, sids in keep.items():
                        obs = []
                        for sid in sids:
                            a = ix[sid, c, role, frame, 'source_np']
                            b = ix[sid, c, role, frame, 'other_source_np']
                            assert a['target_context_sha256'] == b['target_context_sha256']
                            obs.append(b['target_total_bits'] - a['target_total_bits'])
                        vv[f] = float(np.mean(obs))
                    v[role, frame] = vv
                    record('cells', 'M/' + name + '/' + role + '/' + frame, vv)
                v[frame] = diff(v[roles[0], frame], v[roles[1], frame])
                record('cells', 'D/' + name + '/' + frame, v[frame])
            record('cells', 'J/' + name, diff(v['activity'], v['neutral_entity']))
        forms = sorted({c[0] for c in conditions})
        if e38:
            policies = ('candidate_only', 'procedure_unknown', 'independent_fair', 'selected_source', 'selected_other')
            orders = ('source_first', 'other_first')
            for form in forms:
                for policy in policies:
                    record('cells', f'J/{form}/{policy}/order_average', average([vectors[f'J/{form}/{policy}/{o}'] for o in orders]))
                for order in orders + ('order_average',):
                    record('contrasts', f'fair_minus_unknown/{form}/{order}', diff(vectors[f'J/{form}/independent_fair/{order}'], vectors[f'J/{form}/procedure_unknown/{order}']))
                for order in orders:
                    for frame in ('activity', 'neutral_entity'):
                        selected = {}
                        for policy in ('selected_source', 'selected_other'):
                            selected[policy] = average([vectors[f'M/{form}/{policy}/{order}/{role}/{frame}'] for role in roles])
                        record('contrasts', f'selected_source_minus_other/{form}/{order}/{frame}', diff(selected['selected_source'], selected['selected_other']))
        else:
            for form in forms:
                for actor in ('same_actor', 'other_actor'):
                    for measure in ('J',):
                        record('contrasts', f'different_minus_same/{form}/{actor}/{measure}', diff(vectors[f'{measure}/{form}/{actor}/different_began'], vectors[f'{measure}/{form}/{actor}/same_began']))
        # Frozen parent comparisons: explicit changes of referents/introduction
        # for E39 and removal of exhaustivity for E40, never a pure lexical test.
        pp = parent_probability['per_family'][cohort]
        if isinstance(pp, list):
            pp = {r['verb_family']: r for r in pp}
        for c in conditions:
            form = c[0]
            if e38:
                parent_key = f'J/{form}/other_actor/same_began'
                key = 'J/' + '/'.join(c)
            else:
                if experiment=='E43':
                    for parent_form in ('plain_mention_first','plain_mention_last'):
                        parent_key=f'J/{parent_form}/{c[1]}/{c[2]}'
                        pv={f:pp[f][parent_key] for f in keep}
                        record('contrasts','minus_frozen_parent/'+parent_form+'/'+'/'.join(c),diff(vectors['J/'+'/'.join(c)],pv))
                    continue
                parent_form = form if experiment == 'E45' else form.replace('plain_', 'affirmative_') if experiment == 'E40' else 'contrast_parent' if form == 'contrast_named' else form
                actor = c[1] if experiment in ('E40','E45') or c[1] != 'original_activity' else 'old_activity'
                parent_key = f'J/{parent_form}/{actor}/{c[2]}'
                key = 'J/' + '/'.join(c)
            pv = {f: pp[f][parent_key] for f in keep}
            record('contrasts', 'minus_frozen_parent/' + '/'.join(c), diff(vectors[key], pv))
        out['probability']['per_family'][cohort] = {f: {k: v[f] for k, v in vectors.items()} for f in sorted(keep)}
    if reviews:
        out['native'] = analyze_responses(experiment, cache, reviews, out['probability']['cohorts'])
    if experiment == 'E45':
        out['transport'] = scaffold_transport(out)
    return out


def scaffold_transport(out):
    """Preregistered matched family differences; no outcome-defined subsets."""
    root = Path(__file__).resolve().parents[1] / 'results'
    e40 = json.loads((root / 'E40-summary.json').read_text())['probability']
    e44 = json.loads((root / 'E44-summary.json').read_text())['probability']
    transport = dict(parent_hashes={n:sha(root / (n+'-summary.json')) for n in ('E40','E44')},cells={},cohorts={})
    for cohort, current in out['probability']['per_family'].items():
        for parent_name,parent in [('E40',e40),('E44',e44)]:
            families=sorted(set(current) & set(parent['per_family'][cohort]))
            transport['cohorts'][cohort+'/'+parent_name]=families
            for order in ('first','last'):
                form='plain_mention_'+order
                for actor,preds in [('original_activity',('old',)),('same_actor',('same_began','different_began')),('other_actor',('same_began','different_began'))]:
                    for pred in preds:
                        for measure in ('activity','neutral_entity','J'):
                            key=f'J/{form}/{actor}/{pred}' if measure=='J' else f'D/{form}/{actor}/{pred}/{measure}'
                            if parent_name=='E44':
                                pf='balanced_mention_'+order
                                parent_key=f'J/{pf}/{actor}/{pred}/no_protocol' if measure=='J' else f'D/{pf}/{actor}/{pred}/no_protocol/{measure}'
                            else:
                                parent_key=key
                            vector={f:current[f][key]-parent['per_family'][cohort][f][parent_key] for f in families}
                            transport['cells'][f'{cohort}/minus_{parent_name}/{form}/{actor}/{pred}/{measure}']=stat(vector)
    return transport


def analyze_responses(experiment, cache, reviews, cohorts):
    annotations = {}
    for p in reviews:
        j = json.loads(p.read_text())
        assert j['model'] == 'gpt-6-luna'
        for a in j['reviews']:
            assert a['item_id'] not in annotations
            assert a['correct'] in (True, False, None)
            annotations[a['item_id']] = a
    rows = []
    configs = []
    for query in (('current', 'fair') if experiment == 'E38' else ('current','identity_status') if experiment=='E47' else ('current',)):
        path = cache / 'runs' / f'{experiment}-{query}'
        c = json.loads((path / 'config.json').read_text())
        assert sha(path / 'generations.jsonl') == c['generations_sha256']
        configs.append(c)
        rows.extend(map(json.loads, (path / 'generations.jsonl').read_text().splitlines()))
    assert len(rows) == len(annotations) == {'E38': 1536, 'E39': 288, 'E40': 192, 'E43': 96, 'E45':192, 'E46':1536, 'E47':1920}[experiment]
    for r in rows:
        a = annotations[r['item_id']]
        for k in ('passage_sha256', 'question_sha256', 'answer_sha256'):
            assert a[k] == r[k]
        if a['correct'] is True and a['answer_class'] in ('equal_half', 'unspecified', 'source_candidate', 'other_candidate','asserted_identity','unverified_quote','not_asserted'):
            assert a['answer_class'] == r['gold_answer_class'], 'Semantic class encoding disagrees with correct judgment: ' + r['item_id']
        r['response_audit'] = a
    fields = ('fact_realization', 'selection_policy', 'candidate_order', 'role_evidence', 'mode') if experiment == 'E38' else ('query','fact_realization','role_evidence','mode') if experiment=='E47' else ('fact_realization', 'role_evidence', 'mode')
    out = dict(configs=configs, review_sha256=[sha(p) for p in reviews], answer_classes=dict(collections.Counter(a['answer_class'] for a in annotations.values())),
               certainty=dict(collections.Counter(a['certainty'] for a in annotations.values())), correct=sum(a['correct'] is True for a in annotations.values()),
               cells={}, contrasts={}, per_family={})
    for cohort, keep in cohorts.items():
        vals = {}
        for condition in sorted({tuple(r[k] for k in fields) for r in rows}):
            chosen = [r for r in rows if tuple(r[k] for k in fields) == condition]
            v = {}
            for f, sids in keep.items():
                obs = [r['response_audit']['correct'] for r in chosen if r['pair_id'] in sids]
                assert len(obs) == 2
                if None in obs:
                    continue
                v[f] = 100 * float(np.mean(obs))
            vals[condition] = v
            out['cells'][cohort + '/' + '/'.join(condition) + '/correct'] = stat(v)
        for condition, v in vals.items():
            if condition[-1] == 'priority':
                b = vals[condition[:-1] + ('base',)]
                if b.keys() == v.keys():
                    out['contrasts'][cohort + '/' + '/'.join(condition[:-1]) + '/priority_minus_base'] = stat(diff(v, b))
        out['per_family'][cohort] = {'/'.join(k): v for k, v in vals.items()}
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--experiment', choices=['E38', 'E39', 'E40', 'E43', 'E45'], required=True)
    p.add_argument('--cache', type=Path, default=CACHE)
    p.add_argument('--reviews', type=Path, nargs='*', default=[])
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out.write_text(json.dumps(analyze(a.experiment, a.cache, a.reviews), indent=2) + '\n')
