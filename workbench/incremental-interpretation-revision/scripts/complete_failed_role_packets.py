"""Complete transport/schema failures only; never overwrite the original sealed audit."""
import argparse
import json
from pathlib import Path
import time

import audit_paraphrases_role_v2  # registers the original role clarification
import audit_paraphrases
import step_gp_audit as step
from data import sha, write_jsonl


def load(p):
    return [json.loads(s) for s in p.read_text().splitlines()]


def main(a):
    parent = a.root / 'T4-full-v2'
    original = a.original_audit or parent / 'step5'
    packets = a.packets or parent / 'paraphrases.jsonl'
    out = a.out or a.root / 'T4-failure-completion-v1'
    out.mkdir(exist_ok=True)
    if a.protocol == 'critical-dependency':
        import critical_dependency_audit as dependency
        step.PROMPT, step.validate, step.EFFORT = dependency.PROMPT, dependency.validate, 'high'
    else:
        step.PROMPT = audit_paraphrases.PROMPT
        step.validate = audit_paraphrases.validate_t4
    while a.wait and not (original / 'summary.json').exists():
        time.sleep(20)
    rows = load(packets)
    passes = []
    initial = []
    for n in [1, 2]:
        existing = {r['item_id']: r for r in load(original / f'pass{n}.jsonl')}
        missing = [r for r in rows if r['item_id'] not in existing]
        initial.append(dict(pass_number=n, missing_ids=[r['item_id'] for r in missing],
                            original_pass_sha256=sha(original / f'pass{n}.jsonl')))
        additions = step.run_pass(missing, n, out, workers=1, batch_size=1)
        write_jsonl(out / f'failed-pass{n}-completion.jsonl', additions)
        assert not set(existing) & {r['item_id'] for r in additions}
        existing.update({r['item_id']: r for r in additions})
        passes.append(existing)
    (out / 'input-provenance.json').write_text(json.dumps(dict(
        selection='Missing annotation IDs only, never semantic labels or model effects.',
        original_packets_sha256=sha(packets), passes=initial,
        prompt_sha256=__import__('hashlib').sha256(step.PROMPT.encode()).hexdigest(),
        workers=1, batch_size=1, endpoint=step.MESSAGES, model=step.MODEL), indent=2)+'\n')
    while not (original / 'summary.json').exists():
        time.sleep(20)
    original_annotations = load(original / 'annotated.jsonl')
    third = {r['item_id']: r for r in load(original / 'pass3.jsonl')}
    both = passes[0].keys() & passes[1].keys()
    def semantic(r):
        return r['label'], tuple(r['option_labels'])
    disagree = {uid for uid in both if semantic(passes[0][uid]) != semantic(passes[1][uid])}
    failed_third = [r for r in rows if r['item_id'] in disagree and r['item_id'] not in third]
    third.update({r['item_id']: r for r in step.run_pass(failed_third, 3, out, workers=1, batch_size=1)})
    labels = []
    for r in rows:
        uid = r['item_id']
        z = dict(r, step5_status='incomplete')
        if uid in both:
            p1, p2 = passes[0][uid], passes[1][uid]
            z.update(step5_passes=[p1, p2], step5_grammar_agreed=p1['grammar'] == p2['grammar'],
                     step5_position_agreed=(p1['disamb_word_index'], p1['amb_span']) == (p2['disamb_word_index'], p2['amb_span']))
            if uid in disagree and uid not in third:
                z['step5_status'] = 'unresolved'
            else:
                z.update(step5_annotation=third.get(uid, p1),
                         step5_status='adjudicated' if uid in third else 'agreed')
        labels.append(z)
    old = {r['item_id']: r for r in original_annotations}
    for r in labels:
        previous = old[r['item_id']]
        if previous.get('step5_status') in ['agreed', 'adjudicated']:
            assert r['step5_annotation'] == previous['step5_annotation']
    audit = out / 'step5'
    audit.mkdir(exist_ok=True)
    write_jsonl(audit / 'annotated.jsonl', labels)
    summary = dict(items=len(rows), complete_both=len(both), disagreements=len(disagree),
                   adjudications=len(third), unresolved=sum(r['step5_status'] in ['incomplete', 'unresolved'] for r in labels),
                   agreement=(len(both)-len(disagree))/len(both),
                   annotated_sha256=sha(audit / 'annotated.jsonl'), endpoint=step.MESSAGES,
                   model=step.MODEL, max_batch=1, workers=1, proxy_used=False,
                   original_summary_sha256=sha(original / 'summary.json'),
                   original_annotation_sha256=sha(original / 'annotated.jsonl'),
                   failure_completion_only=True, existing_valid_annotations_unchanged=True,
                   effort=step.EFFORT, protocol=a.protocol)
    (audit / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print('Failure-only completion sealed', summary, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--original-audit', type=Path)
    p.add_argument('--packets', type=Path)
    p.add_argument('--out', type=Path)
    p.add_argument('--protocol', choices=['role-v2', 'critical-dependency'], default='role-v2')
    p.add_argument('--wait', action='store_true')
    main(p.parse_args())
