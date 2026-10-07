"""E103 complete-family blind T4 audit and frozen selection-policy readouts."""
import argparse
import collections
import json
from pathlib import Path
import sys
import time

import audit_paraphrases_role_v2
import audit_paraphrases as role
import step_gp_audit as step
from data import sha, write_jsonl
from data_v2 import digest
from current_open_baseline import MODELS
from analyze_paraphrases import PATTERNS
from analyze_correct_answer_carry import estimate


def load(path):
    return list(map(json.loads, path.read_text().splitlines()))


def analyze(root, models, labels, assignments, output):
    rows = {r['item_id']: r for r in load(root/'data-v1.jsonl')}
    runs = json.loads((root/'runner-pids-v1.json').read_text())
    records, panels, provenance, counts = [], [], [], []
    lookup = {(a['model'], a['item_id'], a['candidate']): a for a in assignments}
    for model in models:
        pools = collections.defaultdict(dict)
        for run in [r for r in runs if r['model'] == model]:
            out = Path(run['out']); cfg = json.loads((out/'config.json').read_text())
            assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
            assert cfg['data_sha256'] == sha(root/'data-v1.jsonl')
            provenance.append(dict(model=model, config_sha256=sha(out/'config.json'),
                predictions_sha256=cfg['predictions_sha256'], gpu_hours=cfg['gpu_hours']))
            ps = load(out/'predictions.jsonl'); assert len(ps) == cfg['tasks'] == cfg['pairs']*8
            for p in ps:
                assert p['candidate'] not in pools[p['item_id']]
                pools[p['item_id']][p['candidate']] = p
        assert set(pools) == set(rows)
        for uid, pool in sorted(pools.items()):
            assert set(pool) == set(range(8))
            row = rows[uid]; vals, categories = {}, {}
            for j, p in pool.items():
                a = lookup[model, uid, j]; z = labels.get(a['audit_id'])
                assert a['text_sha256'] == p['text_sha256'] == digest(p['text'])
                category = PATTERNS[tuple(z['step5_annotation']['option_labels'])] if z and z['step5_status'] in ['agreed', 'adjudicated'] else None
                known = p['stopped'] and bool(p['text'].strip()) and not a['unfinished_thinking'] and category is not None
                v = dict(unknown=float(not known), capped=float(p['capped']))
                for cat in ['CORRECT_ROLES', 'GP_MISREADING', 'OTHER']:
                    v[cat+'_lower'] = float(known and category == cat)
                    v[cat+'_upper'] = float(not known or category == cat)
                vals[j], categories[j] = v, category
            selected = dict(GREEDY=0,
                WHOLE=max(range(8), key=lambda j: (pool[j]['scores']['whole'], -j)),
                REVISION_EVIDENCE=max(range(8), key=lambda j: (pool[j]['scores']['suffix'], -j)))
            values = {policy: vals[j] for policy, j in selected.items()}
            values['UNIFORM_POOL'] = {k: sum(vals[j][k] for j in range(8))/8 for k in vals[0]}
            metrics = {policy+'/'+k: v for policy, vs in values.items() for k, v in vs.items()}
            for after, before in [('REVISION_EVIDENCE', 'WHOLE'), ('REVISION_EVIDENCE', 'GREEDY'),
                                  ('WHOLE', 'GREEDY'), ('REVISION_EVIDENCE', 'UNIFORM_POOL'), ('WHOLE', 'UNIFORM_POOL')]:
                for k in vals[0]:
                    other = k[:-6]+'_upper' if k.endswith('_lower') else k[:-6]+'_lower' if k.endswith('_upper') else k
                    metrics[after+'-minus-'+before+'/'+k] = values[after][k]-values[before][other]
            for bound in ['lower', 'upper']:
                metrics['POOL_ORACLE/CORRECT_ROLES_'+bound] = max(vals[j]['CORRECT_ROLES_'+bound] for j in range(8))
            metrics['WHOLE-versus-REVISION/selection_changed'] = float(selected['WHOLE'] != selected['REVISION_EVIDENCE'])
            records.append(dict(model=model, item_id=uid, cluster_id=row['cluster_id'],
                sentence_sha256=row['sources']['gp']['sentence_sha256'], construction=row['construction'],
                selected=selected, candidate_roles=categories, candidate_metrics=vals, metrics=metrics))
        for ct in ['ALL', 'MVRR', 'NPZ', 'NPS']:
            rs = [r for r in records if r['model'] == model and (ct == 'ALL' or r['construction'] == ct)]
            counts.append(dict(model=model, construction=ct, sources=len(rs), candidates=8*len(rs)))
            for metric in sorted(rs[0]['metrics']):
                panels.append(dict(model=model, construction=ct, metric=metric,
                    **estimate(rs, [r['metrics'][metric] for r in rs], seed=103)))
    path = root/output; assert not path.exists()
    path.write_text(json.dumps(dict(models=models, data_sha256=sha(root/'data-v1.jsonl'),
        records=records, panels=panels, counts=counts, runs=provenance,
        statistics='All original sources; source then original cluster bootstrap10000 seed103; bounds retain all unfinished/capped candidates.',
        limits='Native same-source proposal selection; suffix has original teacher T2 position oracle. No automatic boundary discovery or learned policy training.'), indent=2)+'\n')
    manifest = dict(map_sha256=sha(path), panels=len(panels), models=models,
        gpu_hours=sum(r['gpu_hours'] for r in provenance))
    (root/(output+'.manifest.json')).write_text(json.dumps(manifest, indent=2)+'\n')
    print('E103 map sealed', manifest, flush=True)


def main(root, previous):
    rows = {r['item_id']: r for r in load(root/'data-v1.jsonl')}
    runs = json.loads((root/'runner-pids-v1.json').read_text())
    labels, prior = {}, []
    for parent in previous:
        path = parent/'step5/annotated.jsonl'
        assert (parent/'step5/summary.json').exists()
        prior.append(dict(path=str(parent), annotations_sha256=sha(path)))
        for z in load(path):
            if z['step5_status'] not in ['agreed', 'adjudicated']:
                continue
            if z['item_id'] in labels:
                assert labels[z['item_id']]['step5_annotation'] == z['step5_annotation']
            labels[z['item_id']] = z
    step.PROMPT, step.validate = role.PROMPT, role.validate_t4
    pending, phases, packets, assignments = list(MODELS), [], {}, []
    while pending:
        ready = [m for m in pending if all((Path(r['out'])/'config.json').exists() and
            'predictions_sha256' in json.loads((Path(r['out'])/'config.json').read_text())
            for r in runs if r['model'] == m)]
        if not ready:
            time.sleep(20); continue
        model, phase_packets, phase_assignments = ready[0], {}, []
        seen = set()
        for run in [r for r in runs if r['model'] == model]:
            out = Path(run['out']); cfg = json.loads((out/'config.json').read_text())
            assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
            for p in load(out/'predictions.jsonl'):
                key = p['item_id'], p['candidate']; assert key not in seen; seen.add(key)
                source = rows[p['item_id']]['sources']['gp']
                assert source['sentence_sha256'] == p['sentence_sha256']
                assert digest(p['text']) == p['text_sha256']
                final = p['text'].rsplit('</think>', 1)[-1]
                unfinished = '<think>' in p['text'] and '</think>' not in p['text']
                packet = 'SOURCE:\n'+source['sentence']+'\n\nPARAPHRASE:\n'+final
                uid = 'E53-T4:'+digest(packet)
                if not unfinished:
                    phase_packets[uid] = dict(item_id=uid, sentence=packet, sentence_sha256=digest(packet),
                        question='Judge only the source/paraphrase role relation.', question_format='2opt',
                        options=['CORRECT_ROLES', 'GP_MISREADING'], needs_revision=True)
                phase_assignments.append(dict(model=model, item_id=p['item_id'], candidate=p['candidate'],
                    audit_id=uid, text_sha256=p['text_sha256'], unfinished_thinking=unfinished))
        assert seen == {(uid, j) for uid in rows for j in range(8)}
        phase = root/'phase-audits-v1'/model; phase.mkdir(parents=True, exist_ok=True)
        new = {k:v for k,v in phase_packets.items() if k not in labels}
        for uid in phase_packets.keys() & labels.keys():
            assert phase_packets[uid]['sentence_sha256'] == labels[uid]['sentence_sha256']
        assert not (phase/'paraphrases.jsonl').exists()
        write_jsonl(phase/'paraphrases.jsonl', [new[k] for k in sorted(new)])
        write_jsonl(phase/'assignments-v1.jsonl', phase_assignments)
        print('E103 complete-family blind T4', model, len(new), 'new packets', flush=True)
        sys.argv = [sys.argv[0], '--data', str(phase/'paraphrases.jsonl'), '--out', str(phase/'step5'),
                    '--workers', '4', '--batch-size', '5']
        step.main()
        for z in load(phase/'step5/annotated.jsonl'):
            assert z['item_id'] not in labels; labels[z['item_id']] = z
        phases.append(dict(model=model, annotations_sha256=sha(phase/'step5/annotated.jsonl'),
            summary_sha256=sha(phase/'step5/summary.json'), reused_packets=len(phase_packets)-len(new)))
        packets.update(phase_packets); assignments.extend(phase_assignments); pending.remove(model)
        analyze(root, [model], labels, phase_assignments, 'interim-complete-'+model+'-v1.json')
    assert len(assignments) == 1200
    write_jsonl(root/'packets-v1.jsonl', [packets[k] for k in sorted(packets)])
    write_jsonl(root/'assignments-v1.jsonl', assignments)
    merged = root/'step5'; merged.mkdir(exist_ok=True)
    write_jsonl(merged/'annotated.jsonl', [labels[k] for k in sorted(packets)])
    (merged/'summary.json').write_text(json.dumps(dict(model=step.MODEL, endpoint=step.MESSAGES,
        max_batch=5, workers=4, prompt_sha256=digest(step.PROMPT),
        annotations_sha256=sha(merged/'annotated.jsonl'), phases=phases, previous=prior,
        unresolved=sum(labels[k]['step5_status'] not in ['agreed', 'adjudicated'] for k in packets),
        teacher_blind_to_model_seed_reward_Gold=True, source_reaudit_calls=0), indent=2)+'\n')
    analyze(root, MODELS, labels, assignments, 'native-pool-revision-credit-map-v1.json')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--previous-audits', type=Path, nargs='+', required=True)
    a = p.parse_args(); main(a.root, a.previous_audits)
