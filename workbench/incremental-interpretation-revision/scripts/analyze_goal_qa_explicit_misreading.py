"""E99 POST-HOC same-source success/explicit-error conjunction, no new inference."""
import argparse
import collections
import json
from pathlib import Path

from data import sha
from data_v2 import digest
from analyze_correct_answer_carry import estimate
from analyze_paraphrases import PATTERNS


def load(path):
    return list(map(json.loads, path.read_text().splitlines()))


def analyze(root):
    parent = root.parent
    data = parent/'E67/sources-v1.jsonl'
    rows = load(data)
    meta = {r['item_id']: r for r in rows}
    labels, audits = {}, []
    for p in [parent/'E67/T4-failure-completion-v1', parent/'E64/T4-full-v2', parent/'E64/legacy-non-MVRR-v1']:
        path = p/'step5/annotated.jsonl'
        assert (p/'step5/summary.json').exists()
        audits.append(dict(path=str(p), annotation_sha256=sha(path)))
        for r in load(path):
            assert r['item_id'] not in labels
            labels[r['item_id']] = r
    panels, records, provenance, counts = [], [], [], []
    for model in ['Qwen3-8B', 'gemma-3-12b-it', 'Meta-Llama-3.1-8B-Instruct']:
        pdir = parent/'E67/runs-v2'/model
        cfg = json.loads((pdir/'config.json').read_text())
        assert cfg['data_sha256'] == sha(data) and cfg['predictions_sha256'] == sha(pdir/'predictions.jsonl')
        ps = load(pdir/'predictions.jsonl')
        index = {(r['item_id'], r['reading']): r for r in ps}
        assert len(index) == len(ps) == 3*len(rows)
        assert set(index) == {(r['item_id'], g) for r in rows for g in ['NONE', 'INITIAL', 'FINAL']}
        roles = {}
        for p in ps:
            s = meta[p['item_id']]
            assert p['sentence_sha256'] == s['sentence_sha256'] and digest(p['text']) == p['text_sha256']
            packet = 'SOURCE:\n'+s['sentence']+'\n\nPARAPHRASE:\n'+p['text'].rsplit('</think>', 1)[-1]
            z = labels.get('E53-T4:'+digest(packet))
            unfinished = '<think>' in p['text'] and '</think>' not in p['text']
            if not unfinished:
                assert z and z['sentence_sha256'] == digest(packet)
            category = PATTERNS[tuple(z['step5_annotation']['option_labels'])] if z and z['step5_status'] in ['agreed', 'adjudicated'] else None
            known = category is not None and not p['capped'] and not unfinished and bool(p['text'].strip())
            roles[p['item_id'], p['reading']] = category, known
        qdir = parent/'E65/runs-v1'/model
        qc = json.loads((qdir/'config.json').read_text())
        assert qc['predictions_sha256'] == sha(qdir/'predictions.jsonl')
        assert qc['model_manifest_sha256'] == cfg['model_manifest_sha256']
        qs = load(qdir/'predictions.jsonl')
        assert len(qs) == qc['tasks'] and {q['source_unit'] for q in qs} == set(meta)
        assert len({(q['item_id'], q['operation'], q['readout'], q['mapping']) for q in qs}) == len(qs)
        provenance.append(dict(model=model, P_config_sha256=sha(pdir/'config.json'), QA_config_sha256=sha(qdir/'config.json'),
            P_predictions_sha256=cfg['predictions_sha256'], QA_predictions_sha256=qc['predictions_sha256']))
        for readout in ['words', 'letters']:
            for matched in [False, True]:
                groups = collections.defaultdict(list)
                for q in qs:
                    if q['readout'] == readout and (not matched or q['source_gold_matches_grounding']):
                        groups[q['source_unit'], q['operation'], q['mapping']].append(q)
                values = {}
                for s in rows:
                    for goal in ['NONE', 'INITIAL', 'FINAL']:
                        category, known = roles[s['item_id'], goal]
                        successes = [float(all(q['correct'] for q in groups[s['item_id'], goal, mp]))
                                     for mp in [0, 1] if groups[s['item_id'], goal, mp]]
                        # Source without a question in this reference scope is structural NA.
                        if not successes:
                            continue
                        assert len(successes) == 2
                        success = sum(successes)/2
                        wronglo, wronghi = float(known and category == 'GP_MISREADING'), float(not known or category == 'GP_MISREADING')
                        correctlo, correcthi = float(known and category == 'CORRECT_ROLES'), float(not known or category == 'CORRECT_ROLES')
                        v = dict(QA_all_correct=success, QA_correct_AND_GPwrong_lower=success*wronglo,
                            QA_correct_AND_GPwrong_upper=success*wronghi, QA_correct_AND_roles_correct_lower=success*correctlo,
                            QA_correct_AND_roles_correct_upper=success*correcthi,
                            QA_wrong_AND_GPwrong_lower=(1-success)*wronglo, QA_wrong_AND_GPwrong_upper=(1-success)*wronghi,
                            role_unknown=float(not known), GPwrong_lower=wronglo, GPwrong_upper=wronghi)
                        values[s['item_id'], goal] = v
                        records.append(dict(model=model, item_id=s['item_id'], goal=goal, readout=readout,
                            matched_gold=matched, role=category, metrics=v))
                for ct in ['ALL', 'MVRR', 'NPZ', 'NPS', 'NPVP']:
                    for condition in ['gp', 'control']:
                        eligible = [s for s in rows if (ct == 'ALL' or s['construction'] == ct) and s['condition'] == condition]
                        selected = [s for s in eligible if (s['item_id'], 'NONE') in values]
                        assert all((s['item_id'], g) in values for s in selected for g in ['NONE', 'INITIAL', 'FINAL'])
                        prefix = dict(model=model, construction=ct, condition=condition, readout=readout, matched_gold=matched)
                        counts.append(dict(prefix, sources=len(selected), structural_NA=len(eligible)-len(selected)))
                        for metric in next(iter(values.values())):
                            for goal in ['NONE', 'INITIAL', 'FINAL', 'INITIAL-minus-NONE', 'FINAL-minus-NONE']:
                                if '-minus-' in goal:
                                    after = goal.split('-minus-')[0]
                                    opposite = metric[:-6]+'_upper' if metric.endswith('_lower') else metric[:-6]+'_lower' if metric.endswith('_upper') else metric
                                    xs = [values[s['item_id'], after][metric]-values[s['item_id'], 'NONE'][opposite] for s in selected]
                                else:
                                    xs = [values[s['item_id'], goal][metric] for s in selected]
                                panels.append(dict(prefix, goal=goal, metric=metric, **estimate(selected, xs, seed=99)))
    root.mkdir(exist_ok=True)
    out = root/'same-source-qa-explicit-misreading-map-v1.json'
    assert not out.exists()
    out.write_text(json.dumps(dict(source_sha256=sha(data), audits=audits, runs=provenance,
        panels=panels, records=records, counts=counts, analysis='POST-HOC E65/E67 complete maps; same-source joint metrics on all fixed inputs.',
        limits='QA remains forced-choice two mappings, not actual sampled behavior; no unique latent parse, no causal conditional success selection.'), indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(map_sha256=sha(out), panels=len(panels), GPU_hours=0,
        new_API_calls=0, new_model_outputs=0), indent=2)+'\n')
    print('E99 complete', sha(out), len(panels), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    analyze(p.parse_args().root)
