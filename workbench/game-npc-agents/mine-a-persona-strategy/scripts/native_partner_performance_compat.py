#!/usr/bin/env python3
"""Explicit E85 snapshot-copy compatibility overlay; frozen driver stays intact.

Preserve original serialized source attack/xp/reward_xp values omitted by the
legacy loader, and fall back to a full graph deepcopy only if the original
roundtrip is unequal. Exact cached inputs are reused, including aborted runs.
No role, prompt, tool, world rule, condition or sampling seed is changed.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

import native_partner_performance as driver

FROZEN_DRIVER_SHA = '4767814ed0ecab53ce2cdaa970b4ec2d8b256a06c958f77e301547ca22b3dc9b'
MISSING = '<key absent>'


def differences(before, after, path=()):
    if isinstance(before, dict) and isinstance(after, dict):
        rows = []
        for key in sorted(set(before) | set(after)):
            if key not in before or key not in after:
                rows.append({'path': list(path + (key,)),
                             'original': before.get(key, MISSING),
                             'roundtrip': after.get(key, MISSING)})
            else:
                rows.extend(differences(before[key], after[key], path + (key,)))
        return rows
    if before == after:
        return []
    return [{'path': list(path), 'original': before, 'roundtrip': after}]


def read_cached_calls(folders, manifest):
    cache, provenance = {}, []
    source_history_ids = {h['history_id'] for h in driver.load_lines(manifest['data'])}
    for folder in folders:
        folder = Path(folder)
        old = json.loads((folder / 'manifest.json').read_text())
        for key in ['model', 'data_sha256', 'driver_sha256', 'dependency_sha256',
                    'max_turns', 'primary_conditions', 'controls', 'revision_conditions',
                    'fact_check_sentence', 'uniform_execution_mechanics_sentence']:
            assert old[key] == manifest[key], ('partial compatibility mismatch', folder, key)
        # A model may reuse exact keys from either old shard, while the frozen
        # driver still runs only its assigned sorted source slice.
        assert set(old['history_ids']) <= source_history_ids
        assert set(old['seeds']) <= set(manifest['seeds'])
        calls = driver.load_lines(folder / 'model_calls.jsonl')
        for row in calls:
            key = driver.input_key(row)
            assert key == row['decision_key']
            if key in cache:
                assert cache[key] == row['parsed'], ('conflicting exact cached response', key)
            cache[key] = row['parsed']
        provenance.append({'path': str(folder), 'calls': len(calls),
                           'manifest_sha256': driver.sha(folder / 'manifest.json'),
                           'model_calls_sha256': driver.sha(folder / 'model_calls.jsonl'),
                           'runtime_present': (folder / 'runtime.json').exists(),
                           'completed_episodes': (len(driver.load_lines(folder / 'episodes.jsonl'))
                                                  if (folder / 'episodes.jsonl').exists() else 0)})
    return cache, provenance


def install(event_sink=None, partial_runs=()):
    assert driver.sha(driver.__file__) == FROZEN_DRIVER_SHA
    original_new_game = driver.new_game
    original_fork = driver.fork_game
    original_client = driver.SharedPrefixClient
    events = []

    def emit(row):
        events.append(row)
        if event_sink is not None:
            driver.write_line(event_sink, row)

    def faithful_new_game(history, seed, modules):
        game = original_new_game(history, seed, modules)
        desired = json.loads(history['pre_player_graph_json'])
        actual = json.loads(game['graph'].to_json())
        changes = differences(desired, actual)
        for change in changes:
            path, value, observed = change['path'], change['original'], change['roundtrip']
            assert (len(path) == 3 and path[0] == 'nodes'
                    and path[2] in ['attack', 'xp', 'reward_xp']
                    and isinstance(value, (int, float)) and not isinstance(value, bool)
                    and observed in [None, MISSING]), ('unexpected source loader difference', change)
            game['graph'].get_node(path[1]).set_prop(path[2], value)
        assert json.loads(game['graph'].to_json()) == desired
        # The already-recorded initial frame must describe the operative graph.
        game['states'][0]['graph'] = game['graph'].to_json()
        assert game['initial_state'] == driver.material_state(game['graph'])
        if changes:
            emit({'kind': 'source_scalar_restoration', 'history_id': history['history_id'],
                  'seed': seed, 'differences': changes,
                  'full_source_JSON_exact_after_restoration': True})
        return game

    def faithful_fork(game):
        try:
            return original_fork(game)
        except AssertionError:
            before = json.loads(game['graph'].to_json())
            roundtrip = game['modules'][0].from_json(game['graph'].to_json())
            changes = differences(before, json.loads(roundtrip.to_json()))
            if not changes:
                raise
            excluded = {'graph', 'host', 'modules', 'case', 'history'}
            out = {key: copy.deepcopy(value) for key, value in game.items() if key not in excluded}
            out.update(case=game['case'], history=game['history'], modules=game['modules'])
            out['graph'] = copy.deepcopy(game['graph'])
            out['host'] = driver.ViewerHost(out['graph'])
            assert json.loads(out['graph'].to_json()) == before
            assert out['visible'] == game['visible']
            assert all(out['graph'].get_node(nid) is not node
                       for nid, node in game['graph'].all_nodes.items())
            emit({'kind': 'failed_roundtrip_deepcopy_fallback', 'history_id': game['history_id'],
                  'seed': game['seed'], 'panel': game.get('panel'), 'branch': game.get('branch'),
                  'control': game.get('control'), 'turns_completed': len(game['turns']),
                  'differences': changes, 'deepcopy_full_JSON_and_visible_exact': True})
            return out

    class CompatibleClient(original_client):
        def __init__(self, model, out, seed):
            manifest_path = out / 'manifest.json'
            manifest = json.loads(manifest_path.read_text())
            cached, provenance = read_cached_calls(partial_runs, manifest)
            overlay = {'overlay_path': str(Path(__file__).resolve()),
                       'overlay_sha256': driver.sha(__file__),
                       'frozen_driver_sha256': FROZEN_DRIVER_SHA,
                       'operative_loader': 'source-scalar-restoration + failed-roundtrip-only deepcopy',
                       'partial_runs': provenance, 'unique_partial_input_keys': len(cached),
                       'reuse_rule': 'Only identical messages, schema and sampling seed; no cached input is resampled.'}
            manifest['compatibility_overlay'] = overlay
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
            (out / 'compatibility.json').write_text(json.dumps(overlay, indent=2) + '\n')
            super().__init__(model, out, seed)
            self.cache.update(cached)

    driver.new_game = faithful_new_game
    driver.fork_game = faithful_fork
    driver.SharedPrefixClient = CompatibleClient
    return events


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--partial-runs', nargs='*', type=Path, default=[])
    args, remaining = ap.parse_known_args()
    # --partial-runs must precede another option (or end the command), just as
    # the frozen driver's --prior-runs. Each resumed shard takes its own partial.
    out_index = remaining.index('--out')
    out = Path(remaining[out_index + 1])
    if '--cpu-check' in remaining:
        event_sink = out.with_suffix('.compat_events.jsonl')
    else:
        # The frozen driver creates out exclusively before first new_game.
        event_sink = out / 'compatibility_events.jsonl'
    install(event_sink=event_sink, partial_runs=args.partial_runs)
    sys.argv = [driver.__file__] + remaining
    driver.main()


if __name__ == '__main__':
    main()
