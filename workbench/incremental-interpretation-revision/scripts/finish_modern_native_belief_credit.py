"""E96 all eight complete runs -> blinded new-P atoms -> complete-only map."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
import time

from data import sha, write_jsonl
from data_v2 import digest
from atomic_repair_footprints import audit
from current_open_baseline import MODELS


def main(root):
    runs = json.loads((root/'runner-pids-v1.json').read_text())
    rows = {r['item_id']: r for r in map(json.loads, (root/'data-v1.jsonl').read_text().splitlines())}
    packets, assignments, provenance = {}, [], []
    annotations, phases = {}, []
    pending = list(MODELS)
    while pending:
        ready = [m for m in pending if all((Path(r['out'])/'config.json').exists() and
                 'predictions_sha256' in json.loads((Path(r['out'])/'config.json').read_text())
                 for r in runs if r['model'] == m)]
        if not ready:
            time.sleep(20)
            continue
        model = ready[0]
        phase_packets = {}
        phase_assignments = []
        for run in [r for r in runs if r['model'] == model]:
            read_run(root, run, rows, phase_packets, phase_assignments, provenance)
        assert len(phase_assignments) == 100
        phase = root / 'phase-audits-v1' / model
        phase.mkdir(parents=True, exist_ok=True)
        new = {k: v for k, v in phase_packets.items() if k not in annotations or annotations[k]['step5_status'] not in ['agreed', 'adjudicated']}
        assert not (phase/'packets-v1.jsonl').exists()
        write_jsonl(phase/'packets-v1.jsonl', [new[k] for k in sorted(new)])
        write_jsonl(phase/'assignments-v1.jsonl', phase_assignments)
        print('E96 complete-family new-P audit', model, len(new), 'new packets', flush=True)
        audit(SimpleNamespace(root=phase, workers=4))
        summary = json.loads((phase/'step5/summary.json').read_text())
        assert summary['data_sha256'] == sha(phase/'packets-v1.jsonl')
        assert summary['annotated_sha256'] == sha(phase/'step5/annotated.jsonl')
        for z in map(json.loads, (phase/'step5/annotated.jsonl').read_text().splitlines()):
            assert z['item_id'] not in annotations or annotations[z['item_id']]['step5_status'] not in ['agreed', 'adjudicated']
            annotations[z['item_id']] = z
        phases.append(dict(model=model, packets_sha256=sha(phase/'packets-v1.jsonl'),
                           summary_sha256=sha(phase/'step5/summary.json'),
                           annotations_sha256=sha(phase/'step5/annotated.jsonl'),
                           assignment_sha256=sha(phase/'assignments-v1.jsonl'),
                           exact_packet_reuse=len(phase_packets)-len(new)))
        packets.update(phase_packets)
        assignments.extend(phase_assignments)
        pending.remove(model)
    assert len(assignments) == 300 and len({(r['model'], r['item_id'], r['source_condition']) for r in assignments}) == 300
    assert not (root/'packets-v1.jsonl').exists()
    write_jsonl(root/'packets-v1.jsonl', [packets[k] for k in sorted(packets)])
    write_jsonl(root/'assignments-v1.jsonl', assignments)
    scope = dict(data_sha256=sha(root/'data-v1.jsonl'), packet_sha256=sha(root/'packets-v1.jsonl'),
                 assignment_sha256=sha(root/'assignments-v1.jsonl'), runs=provenance, phases=phases,
                 interpretations=300, atom_assignments=sum(len(a['questions']) for a in assignments),
                 distinct_packets=len(packets), unfinished=sum(a['unfinished_thinking'] for a in assignments),
                 selection='All preregistered current native outputs; no reward/label selection. Pipeline complete families as available; never sample unfinished families.',
                 teacher_blind_to_source_and_gold_and_model=True, source_reaudit_calls=0)
    (root/'scope-v1.json').write_text(json.dumps(scope, indent=2)+'\n')
    assert set(annotations) == set(packets)
    merged = root/'step5'
    merged.mkdir(exist_ok=True)
    write_jsonl(merged/'annotated.jsonl', [annotations[k] for k in sorted(annotations)])
    both = [z for z in annotations.values() if len(z.get('step5_passes', [])) == 2]
    disagreements = sum(z['step5_passes'][0]['label'] != z['step5_passes'][1]['label'] for z in both)
    summary = dict(model='step-5-preview', endpoint='https://api.stepfun.com/step_plan/v1/messages',
        proxy_used=False, max_batch=5, workers=4, data_sha256=sha(root/'packets-v1.jsonl'),
        annotated_sha256=sha(merged/'annotated.jsonl'), items=len(annotations), complete_both=len(both),
        disagreements=disagreements, adjudications=sum(z['step5_status'] == 'adjudicated' for z in annotations.values()),
        unresolved=sum(z['step5_status'] in ['incomplete', 'unresolved'] for z in annotations.values()),
        agreement=(len(both)-disagreements)/len(both) if both else None,
        merged_complete_family_phases=phases, existing_valid_packet_labels_immutable=True)
    (merged/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    from analyze_modern_native_belief_credit import analyze
    analyze(root)


def read_run(root, run, rows, packets, assignments, provenance):
        out = Path(run['out'])
        cfg = json.loads((out/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
        assert cfg['data_sha256'] == sha(root/'data-v1.jsonl')
        ps = list(map(json.loads, (out/'predictions.jsonl').read_text().splitlines()))
        assert len(ps) == cfg['tasks'] == cfg['pairs']*6
        provenance.append(dict(model=run['model'], shard=run['shard'], config_sha256=sha(out/'config.json'), predictions_sha256=cfg['predictions_sha256']))
        for p in ps:
            if p['operation'] != 'GENERATION':
                continue
            r = rows[p['item_id']]
            assert p['text_sha256'] == digest(p['text'])
            assert p['sentence_sha256'] == r['sources'][p['source_condition']]['sentence_sha256']
            text = p['text'].rsplit('</think>', 1)[-1]
            unfinished = '<think>' in p['text'] and '</think>' not in p['text']
            atom_ids = {}
            if not unfinished:
                for q in r['questions']:
                    uid = 'E96-atom:' + digest(json.dumps([text, q['question_id'], q['question']], ensure_ascii=False))
                    packets[uid] = dict(item_id=uid, sentence=text, sentence_sha256=digest(text),
                        question=q['question'], question_id=q['question_id'], question_format='yn',
                        options=['Yes', 'No'], needs_revision=True)
                    atom_ids[q['question_id']] = uid
            assignments.append(dict(model=run['model'], item_id=p['item_id'], source_condition=p['source_condition'],
                text_sha256=p['text_sha256'], atom_packets=atom_ids, stopped=p['stopped'], capped=p['capped'],
                unfinished_thinking=unfinished, questions=r['questions']))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    main(p.parse_args().root)
