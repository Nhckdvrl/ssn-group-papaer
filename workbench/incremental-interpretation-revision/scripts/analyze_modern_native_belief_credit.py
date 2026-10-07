"""E96 whole native cohort, complete blind audit, unknown bounds and both targets."""
import collections
import json
from pathlib import Path

from data import sha
from data_v2 import digest
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate
from forward_semantic_credit import rank


def semantic_metrics(assignment, annotations):
    labels = []
    completed = assignment['stopped'] and not assignment['unfinished_thinking']
    for q in assignment['questions']:
        uid = assignment['atom_packets'].get(q['question_id'])
        record = annotations.get(uid)
        label = 'UNKNOWN'
        if completed and record and record['step5_status'] in ['agreed', 'adjudicated']:
            label = record['step5_annotation']['label']
        labels.append(dict(q, label=label))
    unknown = sum(q['label'] == 'UNKNOWN' for q in labels)
    correct = sum(q['label'] != 'UNKNOWN' and ((q['label'] == 'ENTAILED') == (q['source_gold'] == 'Yes')) for q in labels)
    n = len(labels)
    out = dict(pattern_lower=correct/n, pattern_upper=(correct+unknown)/n,
               pattern_accuracy=correct/n if not unknown else None, unknown_atoms=unknown,
               atoms=n, completed=completed, capped=assignment['capped'], atom_labels=labels)
    for gold, field in [('Yes', 'positive_retention'), ('No', 'unsupported_assertion')]:
        qs = [q for q in labels if q['source_gold'] == gold]
        if qs:
            ent = sum(q['label'] == 'ENTAILED' for q in qs)
            unk = sum(q['label'] == 'UNKNOWN' for q in qs)
            out[field+'_lower'] = ent/len(qs)
            out[field+'_upper'] = (ent+unk)/len(qs)
            out[field] = ent/len(qs) if not unk else None
        else:
            for suffix in ['', '_lower', '_upper']:
                out[field+suffix] = None
    p, u = out['positive_retention'], out['unsupported_assertion']
    out['semantic_fidelity'] = None if p is None or u is None else p-u
    for bound, opposite in [('lower', 'upper'), ('upper', 'lower')]:
        p, u = out['positive_retention_'+bound], out['unsupported_assertion_'+opposite]
        out['fidelity_'+bound] = None if p is None or u is None else p-u
    return out


def analyze(root):
    data = root/'data-v1.jsonl'
    rows = list(map(json.loads, data.read_text().splitlines()))
    scope = json.loads((root/'scope-v1.json').read_text())
    assert scope['data_sha256'] == sha(data)
    assert scope['packet_sha256'] == sha(root/'packets-v1.jsonl')
    assert scope['assignment_sha256'] == sha(root/'assignments-v1.jsonl')
    summary = json.loads((root/'step5/summary.json').read_text())
    assert summary['data_sha256'] == sha(root/'packets-v1.jsonl')
    assert summary['annotated_sha256'] == sha(root/'step5/annotated.jsonl')
    annotations = {r['item_id']: r for r in map(json.loads, (root/'step5/annotated.jsonl').read_text().splitlines())}
    assignments = {(r['model'], r['item_id'], r['source_condition']): r for r in map(json.loads, (root/'assignments-v1.jsonl').read_text().splitlines())}
    index, provenance = {}, []
    meta = {r['item_id']: r for r in rows}
    for run in json.loads((root/'runner-pids-v1.json').read_text()):
        out = Path(run['out'])
        cfg = json.loads((out/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl') and cfg['data_sha256'] == sha(data)
        assert cfg['model_manifest_sha256'] == sha(root.parent/'models'/run['model']/'manifest.json')
        ps = list(map(json.loads, (out/'predictions.jsonl').read_text().splitlines()))
        assert len(ps) == cfg['tasks'] == cfg['pairs']*6
        for p in ps:
            r = meta[p['item_id']]
            assert int(digest(r['cluster_id'])[:16], 16) % run['shards'] == run['shard']
            if p['operation'] == 'GENERATION':
                key = run['model'], p['item_id'], 'GENERATION', p['source_condition'], ''
                assert p['text_sha256'] == digest(p['text'])
            else:
                key = run['model'], p['item_id'], 'RECONSTRUCTION', p['interpretation_condition'], p['target_condition']
                assert abs(sum(p['token_logprobs'])-p['reward_sum']) < 1e-8
                assert p['target_sentence_sha256'] == r['sources'][p['target_condition']]['sentence_sha256']
            assert key not in index
            index[key] = p
        provenance.append(dict(model=run['model'], shard=run['shard'], config_sha256=sha(out/'config.json'),
                               predictions_sha256=cfg['predictions_sha256'], gpu_hours=cfg['gpu_hours'], instrument=cfg['instrument']))
    expected = {(m, r['item_id'], 'GENERATION', s, '') for m in MODELS for r in rows for s in ['gp', 'control']}
    expected |= {(m, r['item_id'], 'RECONSTRUCTION', s, t) for m in MODELS for r in rows for s in ['gp', 'control'] for t in ['gp', 'control']}
    assert set(index) == expected and len(assignments) == 300
    records, quality = [], []
    for model in MODELS:
        for r in rows:
            sm = {s: semantic_metrics(assignments[model, r['item_id'], s], annotations) for s in ['gp', 'control']}
            for side in ['gp', 'control']:
                p = index[model, r['item_id'], 'GENERATION', side, '']
                a = assignments[model, r['item_id'], side]
                assert p['text_sha256'] == a['text_sha256']
                quality.append(dict(model=model, item_id=r['item_id'], cluster_id=r['cluster_id'],
                    construction=r['construction'], condition=side,
                    sentence_sha256=r['sources'][side]['sentence_sha256'], **sm[side]))
            for target in ['gp', 'control']:
                b, t = [index[model, r['item_id'], 'RECONSTRUCTION', s, target] for s in ['gp', 'control']]
                assert b['observation_tokens'] == t['observation_tokens']
                for side, p in [('gp', b), ('control', t)]:
                    gen = index[model, r['item_id'], 'GENERATION', side, '']
                    assert p['interpretation_sha256'] == digest(gen['text'].rsplit('</think>', 1)[-1])
                z = dict(model=model, item_id=r['item_id'], cluster_id=r['cluster_id'],
                         construction=r['construction'], condition=target,
                         sentence_sha256=r['sources'][target]['sentence_sha256'],
                         delta_reward_sum=t['reward_sum']-b['reward_sum'],
                         delta_reward_mean=t['reward_mean']-b['reward_mean'],
                         reward_rank=rank(b['reward_sum'], t['reward_sum']),
                         identical_interpretations=b['interpretation_sha256'] == t['interpretation_sha256'],
                         metrics={}, semantics=sm)
                for reference, value, lo, hi in [('fidelity', 'semantic_fidelity', 'fidelity_lower', 'fidelity_upper'),
                                                ('pattern', 'pattern_accuracy', 'pattern_lower', 'pattern_upper')]:
                    bm, tm = sm['gp'], sm['control']
                    if bm[lo] is None or tm[lo] is None:
                        continue  # structural NA; missing a polarity, never fabricated
                    dlo, dhi = tm[lo]-bm[hi], tm[hi]-bm[lo]
                    gold = rank(bm[value], tm[value])
                    possible = ([1] if dlo > 1e-12 else [-1] if dhi < -1e-12 else
                                ([0] if abs(dlo) <= 1e-12 and abs(dhi) <= 1e-12 else [-1, 0, 1]))
                    rr = z['reward_rank']
                    z['metrics'][reference] = dict(delta_lower=dlo, delta_upper=dhi,
                        delta_point=None if gold is None else tm[value]-bm[value],
                        rank=gold, possible_ranks=possible,
                        alignment_lower=min(rr*g for g in possible), alignment_upper=max(rr*g for g in possible),
                        raw_correct_lower=float(all(rr == g for g in possible)), raw_correct_upper=float(rr in possible),
                        raw_opposes_lower=float(all(rr*g < 0 for g in possible)), raw_opposes_upper=float(any(rr*g < 0 for g in possible)))
                records.append(z)
    panels, counts = [], []
    for model in MODELS:
        for ct in ['ALL', 'MVRR', 'NPZ', 'NPS']:
            for condition in ['gp', 'control']:
                rs = [r for r in records if r['model'] == model and r['condition'] == condition and (ct == 'ALL' or r['construction'] == ct)]
                qs = [r for r in quality if r['model'] == model and r['condition'] == condition and (ct == 'ALL' or r['construction'] == ct)]
                if not rs:
                    continue
                for metric in ['pattern_lower', 'pattern_upper', 'positive_retention_lower', 'positive_retention_upper',
                               'unsupported_assertion_lower', 'unsupported_assertion_upper', 'fidelity_lower', 'fidelity_upper', 'capped']:
                    sub = [r for r in qs if r[metric] is not None]
                    panels.append(dict(model=model, construction=ct, condition=condition, subset='all',
                        reference='native_quality', metric=metric, **estimate(sub, [r[metric] for r in sub], seed=96)))
                counts.append(dict(model=model, construction=ct, condition=condition, pairs=len(rs),
                    identical_interpretations=sum(r['identical_interpretations'] for r in rs),
                    raw_rank_counts=dict(collections.Counter(str(r['reward_rank']) for r in rs)),
                    unknown_atoms=sum(r['unknown_atoms'] for r in qs), capped=sum(r['capped'] for r in qs),
                    fidelity_structural_NA=sum('fidelity' not in r['metrics'] for r in rs)))
                for reference in ['fidelity', 'pattern']:
                    eligible = [r for r in rs if reference in r['metrics']]
                    for subset, sub in [('all_eligible', eligible), ('changed_DIAGNOSTIC', [r for r in eligible if r['metrics'][reference]['rank'] in [-1, 1]]),
                                        ('ties_DIAGNOSTIC', [r for r in eligible if r['metrics'][reference]['rank'] == 0])]:
                        if not sub:
                            continue
                        for metric in ['delta_lower', 'delta_upper', 'delta_point', 'alignment_lower', 'alignment_upper',
                                       'raw_correct_lower', 'raw_correct_upper', 'raw_opposes_lower', 'raw_opposes_upper']:
                            used = [r for r in sub if r['metrics'][reference][metric] is not None]
                            panels.append(dict(model=model, construction=ct, condition=condition, reference=reference,
                                subset=subset, metric=metric, **estimate(used, [r['metrics'][reference][metric] for r in used], seed=96)))
            for reference in ['fidelity', 'pattern']:
                by_pair = collections.defaultdict(dict)
                for r in records:
                    if r['model'] == model and (ct == 'ALL' or r['construction'] == ct) and reference in r['metrics']:
                        by_pair[r['item_id']][r['condition']] = r
                rs, lower, upper = [], [], []
                for p in by_pair.values():
                    assert set(p) == {'gp', 'control'}
                    g, c = p['gp']['metrics'][reference], p['control']['metrics'][reference]
                    rs.append(p['gp'])
                    lower.append(c['alignment_lower']-g['alignment_upper'])
                    upper.append(c['alignment_upper']-g['alignment_lower'])
                for bound, values in [('lower', lower), ('upper', upper)]:
                    panels.append(dict(model=model, construction=ct, condition='CUE-target-minus-GP-target',
                        reference=reference, subset='all_eligible', metric='alignment_'+bound,
                        **estimate(rs, values, seed=96)))
    out = root/'modern-native-belief-credit-map-v1.json'
    assert not out.exists()
    out.write_text(json.dumps(dict(data_sha256=sha(data), panels=panels, counts=counts, records=records,
        native_quality_records=quality, runs=provenance, audit_summary=summary,
        statistics='Complete current natural writers/selfgraders; Source then original published-pair cluster10000 seed96. All unknown bounded and structural NA reported; changed/tie diagnostic subsets.',
        limits='Only frozen registered common-Q semantics, not full-sentence equivalence certification. Untrained content-reconstruction analogue, not ABBEL reproduction. No hidden Source-bank transplant and no reward-selected generation.'), indent=2)+'\n')
    result = dict(map_sha256=sha(out), actual_outputs=300, reconstruction_scores=600,
        gpu_hours=sum(r['gpu_hours'] for r in provenance), panels=len(panels),
        audited_distinct_packets=summary['items'], audit_unresolved=summary['unresolved'],
        new_source_annotation_calls=0, annotation='Only Step Plan step-5-preview; double blind and disagreement adjudication.')
    (root/'complete-map-v1.json').write_text(json.dumps(result, indent=2)+'\n')
    print('E96 COMPLETE', result, flush=True)
