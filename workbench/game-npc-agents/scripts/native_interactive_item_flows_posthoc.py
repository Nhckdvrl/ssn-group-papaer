#!/usr/bin/env python3
"""E80 POST-HOC physical flows; no language labels, models, or new episodes."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, required=True)
    args = parser.parse_args()
    output = {'status': 'COMPLETE_POST_HOC', 'scope':
              'Physical item-flow description only; simultaneous two-way transfers do not establish a negotiated contract. No new model calls.',
              'models': {}, 'source_reports_sha256': {}}
    for model in ['gemma', '32b']:
        report_path = args.results / f'E80_{model}_complete.json'
        report = json.loads(report_path.read_text())
        assert report['status'] == 'COMPLETE' and report['episodes'] == 2400
        output['source_reports_sha256'][str(report_path)] = hashlib.sha256(report_path.read_bytes()).hexdigest()
        episodes = {}
        for filename in report['primary_episode_sources_ordered']:
            for row in map(json.loads, Path(filename).open()):
                key = tuple(row[k] for k in ['case_id', 'seed', 'persona', 'backend'])
                episodes.setdefault(key, row)
        assert len(episodes) == 2400
        counts, worlds, examples = defaultdict(Counter), defaultdict(set), defaultdict(list)
        for key, row in episodes.items():
            actor, player, source = row['actor_id'], row['requester_id'], row['goal_item_id']
            successful = [h for h in row['turns'] if h.get('legal') and h.get('executed')
                          and not h.get('stochastic_failure')]
            gives = [h for h in successful if h['event_type'] == 'GiveObjectEvent'
                     and len(h['target_node_ids']) >= 2]
            player_gives = [h for h in gives if h['actor'] == player and h['target_node_ids'][1] == actor]
            npc_gives = [h for h in gives if h['actor'] == actor and h['target_node_ids'][1] == player]
            flags = {
                'bidirectional_any_Give': bool(player_gives and npc_gives),
                'NPC_sourceGive_and_player_other_assetGive': bool(row['npc_give_request_ever']
                    and any(h['target_node_ids'][0] != source for h in player_gives)),
                'NPC_sourceGive_and_player_source_return': bool(row['npc_give_request_ever']
                    and any(h['target_node_ids'][0] == source for h in player_gives)),
                'NPC_sourceGive_and_player_source_consumption': bool(row['npc_give_request_ever']
                    and any(h['role'] == 'player' and h['event_type'] in ['EatEvent', 'DrinkEvent', 'IngestEvent']
                            and h['target_node_ids'] and h['target_node_ids'][0] == source for h in successful)),
            }
            for label, present in flags.items():
                if present:
                    counts[row['persona'] + '/' + row['backend']][label] += 1
                    worlds[label].add(row['case_id'])
                    examples[label].append(key)
        output['models'][model] = {
            'counts_per_600_episode_cell': {k: dict(v) for k, v in counts.items()},
            'source_worlds': {k: len(v) for k, v in worlds.items()},
            'hash_median_example_keys': {k: list(sorted(v)[len(v) // 2]) for k, v in examples.items()},
        }
    output['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    destination = args.results / 'E80_item_flows_POST_HOC.json'
    destination.write_text(json.dumps(output, indent=2) + '\n')
    print(destination)


if __name__ == '__main__':
    main()
