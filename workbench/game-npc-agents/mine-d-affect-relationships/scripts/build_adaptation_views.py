#!/usr/bin/env python3
"""Build source-pointer views for character adaptation, without model calls.

Inputs, targets and later readout IDs have separate APIs. A same-scene role turn
is part of the completed experience, never a future test of its end-state.
Published successor order is retained, not certified as canonical chronology.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from experience_store import ExperienceStore, file_sha
from prepare_closed_loop import tracker


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def partitions(books, policy):
    books = set(books)
    observed = set(policy['observed_books'])
    if not observed <= books:
        raise ValueError('Policy contains an unknown observed book')
    ranked = sorted(books - observed, key=lambda b: hashlib.sha256(
        (policy['partition_salt'] + '|' + b).encode()).hexdigest())
    nt, nv = policy['new_test_books'], policy['new_validation_books']
    if type(nt) is not int or type(nv) is not int or min(nt, nv) < 1 or nt + nv >= len(ranked):
        raise ValueError('Invalid complete-book partition quotas')
    result = {book: 'observed_development' for book in observed}
    result.update({book: 'test' if i < nt else 'validation' if i < nt + nv else 'train'
                   for i, book in enumerate(ranked)})
    return result


def update_messages(row):
    """Inference input only. Never insert assistant labels or successor tasks."""
    if row['details']['task'] != 'character_state_update':
        raise ValueError('Expected a native end-of-scene update task')
    turns = row['conversations']
    if [t['from'] for t in turns] != ['system', 'human', 'assistant']:
        raise ValueError('Unexpected native update conversation layout')
    if not all(isinstance(t['value'], str) and t['value'].strip() for t in turns[:2]):
        raise ValueError('Empty or non-text update input')
    return [{'role': role, 'content': turn['value']}
            for role, turn in zip(['system', 'user'], turns[:2])]


def update_target(row):
    """Training/evaluation supervision only; not part of update_messages()."""
    update_messages(row)
    raw = row['conversations'][2]['value']
    value = json.loads(raw)
    if not isinstance(value, dict) or type(value.get('profile_updated')) is not bool:
        raise ValueError('Missing native boolean change label')
    for key in ['hidden_tracker', 'updated_profile', 'short_description']:
        if key not in value:
            raise ValueError(f'Missing target field: {key}')
    if value['profile_updated'] and not isinstance(value['updated_profile'], str):
        raise ValueError('Changed profile must contain text')
    return raw, value


def prior_state(row):
    text = update_messages(row)[1]['content']
    labels = ['Current Profile (State At Scene Start)',
              'Hidden Tracker (State At Scene Start)', 'Current Motivation (State At Scene Start)']
    markers = ['\n\n## ' + label + '\n' for label in labels]
    if any(text.count(marker) != 1 for marker in markers):
        raise ValueError('Ambiguous native prior-state boundaries')
    positions = [text.index(m) for m in markers]
    if positions != sorted(positions):
        raise ValueError('Reordered native prior-state fields')
    return dict(profile=text[positions[0] + len(markers[0]):positions[1]],
                hidden_tracker=text[positions[1] + len(markers[1]):positions[2]])


def after_state(row):
    _, target = update_target(row)
    before = prior_state(row)
    return dict(profile=target['updated_profile'] if target['profile_updated'] else before['profile'],
                hidden_tracker=target['hidden_tracker'])


def continuity(previous, following):
    a, b = after_state(previous), prior_state(following)
    return dict(profile_exact=a['profile'] == b['profile'],
                tracker_normalized_exact=tracker(a['hidden_tracker']) == tracker(b['hidden_tracker']))


def future_readout_ids(store, update_id):
    """Only successor IDs, never same-appearance turns already in the evidence."""
    appearance = store.appearance(update_id)
    next_id = appearance['next_update_id']
    if next_id is None:
        return None
    nxt = store.appearance(next_id)
    if (nxt['book'], nxt['role']) != (appearance['book'], appearance['role']):
        raise ValueError('A source link crosses the target character or book')
    return dict(next_update_id=next_id, scene=nxt['scene'],
                motivation_ids=nxt['same_appearance_tasks'].get('character_motivation_update', []),
                interaction_ids=nxt['same_appearance_tasks'].get('interaction_generation', []),
                order_qualification='published_record_order_only')


def build(store, policy, destination, policy_sha):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    final = destination / 'episodes.jsonl'
    partial = destination / 'episodes.jsonl.partial'
    inventory = destination / 'inventory.json'
    if final.exists() or partial.exists() or inventory.exists():
        raise FileExistsError('Preserve prior views; use a fresh output directory')
    if (store.metadata['source_revision'] != policy['source_revision'] or
            store.metadata['source_sha256'] != policy['source_sha256'] or
            file_sha(store.source) != policy['source_sha256']):
        raise ValueError('Source differs from the frozen policy')
    stat = store.source.stat()
    books = [r[0] for r in store.db.execute('SELECT DISTINCT book FROM updates')]
    split = partitions(books, policy)
    book_counts, part_counts, changes, links = Counter(), Counter(), defaultdict(Counter), Counter()
    roles = defaultdict(set)
    with partial.open('x') as output:
        for meta in store.db.execute('SELECT * FROM updates ORDER BY book,role,scene'):
            uid = meta['row_id']
            row = store.get(uid)
            inp = update_messages(row)
            raw_target, target = update_target(row)
            prior_state(row)  # All examples must be parseable, including terminal appearances.
            nxt = future_readout_ids(store, uid)
            if nxt is not None:
                match = continuity(row, store.get(nxt['next_update_id']))
                nxt['source_state_continuity'] = match
                links['successors'] += 1
                links['both_state_fields_match'] += all(match.values())
                links['with_next_motivation'] += bool(nxt['motivation_ids'])
                links['with_next_interaction'] += bool(nxt['interaction_ids'])
                links['matched_with_next_interaction'] += all(match.values()) and bool(nxt['interaction_ids'])
            source_record = store.db.execute('SELECT sha256 FROM records WHERE row_id=?', (uid,)).fetchone()
            book, role = meta['book'], meta['role']
            part = split[book]
            entry = dict(episode_id=f'ew/update/{uid}', source_row_id=uid,
                         source_record_sha256=source_record['sha256'], book=book, role=role,
                         scene=meta['scene'], research_partition=part, source_release_split='train',
                         input_sha256=digest(inp), target_sha256=digest(raw_target),
                         input_chars=sum(len(m['content']) for m in inp), target_chars=len(raw_target),
                         native_profile_updated=target['profile_updated'], next_readout=nxt)
            output.write(json.dumps(entry, ensure_ascii=False) + '\n')
            book_counts[book] += 1
            part_counts[part] += 1
            changes[part][str(target['profile_updated']).lower()] += 1
            roles[part].add((book, role))
    if store.source.stat().st_mtime_ns != stat.st_mtime_ns or store.source.stat().st_size != stat.st_size:
        raise ValueError('Source changed while constructing views')
    expected = store.db.execute('SELECT COUNT(*) FROM updates').fetchone()[0]
    if sum(part_counts.values()) != expected:
        raise ValueError('Incomplete update coverage')
    partial.rename(final)
    result = dict(schema_version=1, source_revision=policy['source_revision'],
                  source_sha256=policy['source_sha256'], policy_sha256=policy_sha,
                  builder_sha256=file_sha(__file__), n_updates=expected, n_books=len(books),
                  n_roles=sum(len(v) for v in roles.values()),
                  by_partition={p: dict(n_books=sum(v == p for v in split.values()),
                                       n_updates=part_counts[p], n_roles=len(roles[p]),
                                       native_change_flags=dict(changes[p])) for p in sorted(part_counts)},
                  books={b: dict(partition=split[b], n_updates=book_counts[b]) for b in sorted(books)},
                  links=dict(links), episodes_path=str(final.resolve()), episodes_bytes=final.stat().st_size,
                  episodes_sha256=file_sha(final), model_calls=0,
                  qualifications=[
                      'Research partitions apply to prospective new training only; all rows originate in the publisher training split.',
                      'Observed-development books already have inspected model results; no fresh-test claim for them.',
                      'No change-flag or model-outcome selection. Source narrator-like entries remain visible.',
                      'Successor links and state continuity do not certify original-book chronology or causal evidence sufficiency.',
                      'Native references and initial profiles may be retrospectively constructed; they are not unique psychological truth.',
                      'Only pointers are stored. Writer input excludes target and all successor tasks.',
                      'No source text or new model outputs are redistributed in the Git inventory.',
                  ])
    inventory.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result


def export_sft(store, views, partition, output):
    """Explicit training export; assistant target stays outside the input messages."""
    output = Path(output)
    if output.exists() or output.with_suffix(output.suffix + '.partial').exists():
        raise FileExistsError('Do not overwrite an existing SFT export')
    inv = json.loads((Path(views).parent / 'inventory.json').read_text())
    if (file_sha(views) != inv['episodes_sha256'] or
            store.metadata['source_sha256'] != inv['source_sha256']):
        raise ValueError('Views or source index do not match the build inventory')
    temporary = output.with_suffix(output.suffix + '.partial')
    n = 0
    with temporary.open('x') as dest, Path(views).open() as source:
        for line in source:
            item = json.loads(line)
            if item['research_partition'] != partition:
                continue
            row = store.get(item['source_row_id'])
            messages, target = update_messages(row), update_target(row)[0]
            if digest(messages) != item['input_sha256'] or digest(target) != item['target_sha256']:
                raise ValueError('Native input/target no longer match the view')
            dest.write(json.dumps(dict(episode_id=item['episode_id'], messages=messages,
                                       completion=target), ensure_ascii=False) + '\n')
            n += 1
    if n != inv['by_partition'][partition]['n_updates']:
        raise ValueError('Export coverage differs from inventory')
    temporary.rename(output)
    return dict(partition=partition, n_rows=n, path=str(output.resolve()),
                bytes=output.stat().st_size, sha256=file_sha(output), model_calls=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', required=True)
    parser.add_argument('--source')
    sub = parser.add_subparsers(dest='operation', required=True)
    create = sub.add_parser('build')
    create.add_argument('--policy', required=True)
    create.add_argument('--out-dir', required=True)
    create.add_argument('--inventory-copy')
    export = sub.add_parser('export-sft')
    export.add_argument('--views', required=True)
    export.add_argument('--partition', required=True, choices=['train', 'validation', 'test', 'observed_development'])
    export.add_argument('--out', required=True)
    args = parser.parse_args()
    store = ExperienceStore(args.index, args.source)
    try:
        if args.operation == 'build':
            result = build(store, json.loads(Path(args.policy).read_text()), args.out_dir, file_sha(args.policy))
            if args.inventory_copy:
                path = Path(args.inventory_copy)
                with path.open('x') as out:
                    out.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        else:
            result = export_sft(store, args.views, args.partition, args.out)
        print(json.dumps({k: v for k, v in result.items() if k not in ['books', 'qualifications']}, indent=2))
    finally:
        store.close()


if __name__ == '__main__':
    main()
