"""Replace scoped T1 judgments deterministically; preserve original T2/T3."""
import argparse
import collections
import json
from pathlib import Path

from analyze_reading_map import assemble, load
from data import sha, write_jsonl


def merge(published, qualified, original, validation, destination, out):
    scope = json.loads((validation/'scope.json').read_text())
    assert scope['source_data_sha256'] == sha(qualified)
    assert (validation/'step5/summary.json').exists(), 'Full validation required'
    checks = {r['item_id']:r for r in load(validation/'step5/annotated.jsonl')}
    assert len(checks) == scope['rows']
    records = load(original/'annotated.jsonl')
    changes = collections.Counter()
    statuses = collections.Counter()
    for record in records:
        uid = record['item_id']
        prior = record.get('step5_annotation')
        if prior and (prior['label'] == 'CONTRADICTED' or 'CONTRADICTED' in prior['option_labels']):
            assert uid in checks, 'Every potential final contradiction requires validation'
        if uid not in checks:
            continue
        checked = checks[uid]
        assert checked['sentence_sha256'] == record['sentence_sha256']
        record['step5_v4_annotation'] = prior
        record['step5_semantic_validation_status'] = checked['step5_status']
        record['step5_semantic_validation_passes'] = checked.get('step5_passes', [])
        statuses[checked['step5_status']] += 1
        if checked['step5_status'] not in ('agreed', 'adjudicated'):
            record['step5_status'] = 'unresolved_semantic_validation'
            continue
        chosen = checked['step5_annotation']
        changes[(prior['label'], tuple(prior['option_labels']), chosen['label'], tuple(chosen['option_labels']))] += 1
        # Compatibility placeholders never replace independently assessed grammar
        # or positions. Only the adjudicated T1 fields change.
        record['step5_annotation'] = dict(prior)
        for key in ('label', 'option_labels', 'confidence', 'note', 'semantic_checks'):
            record['step5_annotation'][key] = chosen[key]
        record['step5_status'] = chosen_status = checked['step5_status']
        assert chosen_status in ('agreed', 'adjudicated')
    destination.mkdir(parents=True, exist_ok=True)
    annotation = destination/'annotated.jsonl'
    write_jsonl(annotation, records)
    for n in (1,2):
        source = original/f'pass{n}.jsonl'
        (destination/source.name).write_bytes(source.read_bytes())
    report = dict(published_data_sha256=sha(published), original_annotation_sha256=sha(original/'annotated.jsonl'),
                  validation_annotation_sha256=sha(validation/'step5/annotated.jsonl'),
                  merged_annotation_sha256=sha(annotation), validation_scope=scope,
                  validation_summary=json.loads((validation/'step5/summary.json').read_text()),
                  validation_status_counts=dict(statuses),
                  label_changes=[dict(before=[a,list(b)], after=[c,list(d)], rows=n)
                                 for (a,b,c,d),n in sorted(changes.items())],
                  interpretation='Scoped T1 countermodel revalidation; original two-pass grammar/landmarks retained. Failed revalidation is unknown, never a pass. No model outcomes were used.')
    (destination/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    assemble(published, annotation, out)
    # A failed T1-only request does not invalidate independently agreed original
    # T2/T3. Restore the globally checked v4 landmarks, including its exclusions.
    previous = {r['item_id']:r for r in load(qualified)}
    assembled = load(out)
    position_fields = ('disamb_word_index','amb_span','position_origin','ambiguity_span_origin')
    for row in assembled:
        old = previous[row['item_id']]
        assert old['sentence_sha256'] == row['sentence_sha256']
        for field in position_fields:
            if field in old:
                row[field] = old[field]
            else:
                row.pop(field, None)
    write_jsonl(out, assembled)
    manifest_path = out.with_suffix('.manifest.json')
    manifest = json.loads(manifest_path.read_text())
    old_manifest = json.loads(qualified.with_suffix('.manifest.json').read_text())
    for field in ('position_available','position_inconsistent_sentences','ambiguity_span_inconsistent_sentences'):
        manifest[field] = old_manifest[field]
    manifest.update(assembled_sha256=sha(out),
                    landmark_policy='Original independently agreed T2, with original cross-question conflicts retained; T1-only validation never supplies positions.')
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('published','qualified','original','validation','destination','out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    merge(args.published,args.qualified,args.original,args.validation,args.destination,args.out)
