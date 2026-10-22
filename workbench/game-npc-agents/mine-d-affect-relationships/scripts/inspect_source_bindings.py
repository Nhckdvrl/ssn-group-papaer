#!/usr/bin/env python3
"""Qualify native training IDs against separately released scene assets, read-only."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from experience_store import ExperienceStore
from index_update_provenance import section


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(args.root)
    dataset = root / 'data/EvolvingWorld'
    source = ExperienceStore(dataset / 'experience_index.sqlite')
    rows = []
    try:
        for line in (root / 'data/closed_D-E06/trajectories.jsonl').open():
            trajectory = json.loads(line)
            for update in trajectory['updates']:
                detail = update['details']
                rows.append(dict(cohort='D-E06-frozen-updates', book=detail['book_name'],
                                 role=detail['character'], scene=detail['scene_index'],
                                 scenario=section(update['messages'][1]['content'], 'Scene Scenario', 'Scene Interactions')))
        for row_id in [95104, 74355, 15044]:
            task = source.get(row_id)
            detail = task['details']
            rows.append(dict(cohort='POST-HOC-Mansfield-source-review', source_row_id=row_id,
                             book=detail['book_name'], role=detail['character'],
                             scene=detail['scene_index'],
                             scenario=section(task['conversations'][1]['value'], 'Scene Scenario', 'Scene Interactions')))
        files, scenarios = {}, {}
        for book in sorted({r['book'] for r in rows}):
            path = dataset / 'extracted_data/scenes' / (book + '.json')
            raw = path.read_bytes()
            scenes = json.loads(raw)['scenes']
            files[book] = dict(path=str(path.relative_to(dataset)), n_scenes=len(scenes),
                               sha256=hashlib.sha256(raw).hexdigest())
            scenarios[book] = [r['scenario'].strip() for r in scenes]
        detail_rows, counts = [], defaultdict(Counter)
        for row in rows:
            expected = row.pop('scenario').strip()
            available = scenarios[row['book']]
            matches = [i for i, value in enumerate(available) if value == expected]
            same = row['scene'] < len(available) and available[row['scene']] == expected
            status = 'same_index_exact' if same else 'exact_at_other_index' if matches else 'no_exact_scenario_match'
            row.update(scenario_sha256=digest(expected), exact_scene_indices=matches,
                       index_in_released_range=row['scene'] < len(available), status=status)
            counts[row['cohort']][status] += 1
            detail_rows.append(row)
        result = dict(source_revision=source.metadata['source_revision'],
                      training_file_sha256=source.metadata['source_sha256'],
                      extracted_scene_files=files, counts={k:dict(v) for k,v in counts.items()},
                      unique_native_scenarios=len({(r['book'],r['scene'],r['scenario_sha256']) for r in detail_rows}),
                      details=detail_rows,
                      interpretation='Exact source namespace qualification, not a chronology score or model experiment. '
                      'D-E06 itself binds update and interaction tasks within the same frozen training file; '
                      'no current scene asset was substituted into its inputs. No source files or original outputs rewritten.')
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps(result['counts'], ensure_ascii=False, indent=2))
    finally:
        source.close()


if __name__ == '__main__':
    main()
