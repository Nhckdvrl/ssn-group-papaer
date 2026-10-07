"""E98 complete-family, exact-packet T4-v2 reuse and blinded annotation pipeline."""
import argparse
import json
from pathlib import Path
import sys
import time

import audit_paraphrases_role_v2  # original protocol, including role clarification
import audit_paraphrases as role
import step_gp_audit as step
from data import sha, write_jsonl
from data_v2 import digest
from current_open_baseline import MODELS
from query_guidance_fidelity import MODES


def load(path):
    return list(map(json.loads, path.read_text().splitlines()))


def main(root, previous):
    rows = {r['item_id']: r for r in load(root/'data-v1.jsonl')}
    runs = json.loads((root/'runner-pids-v1.json').read_text())
    labels, previous_provenance = {}, []
    for parent in previous:
        path = parent/'step5/annotated.jsonl'
        assert (parent/'step5/summary.json').exists()
        previous_provenance.append(dict(path=str(parent), sha256=sha(path)))
        for z in load(path):
            if z.get('step5_status') not in ['agreed', 'adjudicated']:
                continue
            if z['item_id'] in labels:
                assert labels[z['item_id']]['step5_annotation'] == z['step5_annotation']
            labels[z['item_id']] = z
    step.PROMPT, step.validate = role.PROMPT, role.validate_t4
    phases, packets, assignments, provenance = [], {}, [], []
    pending = list(MODELS)
    while pending:
        ready = [m for m in pending if all((Path(r['out'])/'config.json').exists() and
            'predictions_sha256' in json.loads((Path(r['out'])/'config.json').read_text())
            for r in runs if r['model'] == m)]
        if not ready:
            time.sleep(20)
            continue
        model, phase_packets, phase_assignments = ready[0], {}, []
        seen = set()
        for run in [r for r in runs if r['model'] == model]:
            out = Path(run['out'])
            cfg = json.loads((out/'config.json').read_text())
            assert cfg['data_sha256'] == sha(root/'data-v1.jsonl')
            assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
            predictions = load(out/'predictions.jsonl')
            assert len(predictions) == cfg['tasks'] == cfg['rows']*6
            provenance.append(dict(model=model, shard=run['shard'], config_sha256=sha(out/'config.json'),
                predictions_sha256=cfg['predictions_sha256'], gpu_hours=cfg['gpu_hours']))
            for p in predictions:
                key = p['item_id'], p['mode'], p['readout']
                assert key not in seen
                seen.add(key)
                source = rows[p['item_id']]
                assert p['sentence_sha256'] == source['sentence_sha256']
                assert p['text_sha256'] == digest(p['text'])
                if p['readout'] != 'PARAPHRASE':
                    continue
                final = p['text'].rsplit('</think>', 1)[-1]
                unfinished = '<think>' in p['text'] and '</think>' not in p['text']
                packet = 'SOURCE:\n'+source['sentence']+'\n\nPARAPHRASE:\n'+final
                uid = 'E53-T4:'+digest(packet)
                if not unfinished:
                    phase_packets[uid] = dict(item_id=uid, sentence=packet, sentence_sha256=digest(packet),
                        question='Judge only the source/paraphrase role relation.', question_format='2opt',
                        options=['CORRECT_ROLES', 'GP_MISREADING'], needs_revision=True)
                phase_assignments.append(dict(model=model, item_id=p['item_id'], mode=p['mode'],
                    audit_id=uid, stopped=p['stopped'], capped=p['capped'], unfinished_thinking=unfinished,
                    text_sha256=p['text_sha256']))
        assert seen == {(uid, mode, readout) for uid in rows for mode in MODES for readout in ['QA', 'PARAPHRASE']}
        assert len(phase_assignments) == 300
        phase = root/'phase-audits-v1'/model
        phase.mkdir(parents=True, exist_ok=True)
        new = {k:v for k,v in phase_packets.items() if k not in labels}
        for uid in phase_packets.keys() & labels.keys():
            assert phase_packets[uid]['sentence_sha256'] == labels[uid]['sentence_sha256']
        assert not (phase/'paraphrases.jsonl').exists()
        write_jsonl(phase/'paraphrases.jsonl', [new[k] for k in sorted(new)])
        write_jsonl(phase/'assignments-v1.jsonl', phase_assignments)
        print('E98 complete-family blind T4', model, len(new), 'new packets', flush=True)
        sys.argv = [sys.argv[0], '--data', str(phase/'paraphrases.jsonl'), '--out', str(phase/'step5'),
                    '--workers', '4', '--batch-size', '5']
        step.main()
        for z in load(phase/'step5/annotated.jsonl'):
            assert z['item_id'] not in labels
            labels[z['item_id']] = z
        phases.append(dict(model=model, packets_sha256=sha(phase/'paraphrases.jsonl'),
            summary_sha256=sha(phase/'step5/summary.json'), annotations_sha256=sha(phase/'step5/annotated.jsonl'),
            reused_packets=len(phase_packets)-len(new)))
        packets.update(phase_packets)
        assignments.extend(phase_assignments)
        pending.remove(model)
    assert len(assignments) == 900
    write_jsonl(root/'packets-v1.jsonl', [packets[k] for k in sorted(packets)])
    write_jsonl(root/'assignments-v1.jsonl', assignments)
    merged = root/'step5'
    merged.mkdir(exist_ok=True)
    write_jsonl(merged/'annotated.jsonl', [labels[k] for k in sorted(packets)])
    summary = dict(model=step.MODEL, endpoint=step.MESSAGES, max_batch=5, workers=4,
        prompt_sha256=digest(step.PROMPT), annotations_sha256=sha(merged/'annotated.jsonl'),
        packets_sha256=sha(root/'packets-v1.jsonl'), assignments_sha256=sha(root/'assignments-v1.jsonl'),
        unresolved=sum(labels[k]['step5_status'] not in ['agreed', 'adjudicated'] for k in packets),
        previous_audits=previous_provenance, phases=phases, runs=provenance,
        teacher_blind_to_goal_QA_Gold_model=True, source_reaudit_calls=0)
    (merged/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    from analyze_query_guidance_fidelity import analyze
    analyze(root)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--previous-audits', type=Path, nargs='+', required=True)
    a = p.parse_args()
    main(a.root, a.previous_audits)
