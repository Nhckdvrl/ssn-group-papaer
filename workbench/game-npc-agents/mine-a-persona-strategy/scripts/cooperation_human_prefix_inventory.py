#!/usr/bin/env python3
"""E81 source inventory: all archived human/bot utterances and native actions.

No models, new assets, source repairs, semantic gold or original RNG claims.
Keyword hits are recall indexes only. Full archive prefixes are replayed from
their original quest graphs, including native rejections and stochastic failure.
Run with the existing fgvd environment and cached LIGHT dependency overlay.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import random
import re
import subprocess
import tarfile
import time
from pathlib import Path

from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, actor_for, material_state

WB = Path(__file__).resolve().parents[1]
SOURCE = CACHE / 'sources/LIGHT'
TARGET_VERBS = {'give', 'put', 'eat', 'drink'}
PATTERNS = {
    'conditional': r'\bif\b|\bonce\b|\bas long as\b|\bin return\b|\bfirst\b.*\bthen\b',
    'exchange_or_return': r'\btrad\w*\b|\bexchang\w*\b|\bbargain\w*\b|\brepay\w*\b|\breturn\w*\b|\bborrow\w*\b|\blend\w*\b|\bbuy\b|\bsell\b|\bpay\w*\b',
    'commitment_or_offer': r"\bI (?:will|can|shall|would)\b|\bI['’]ll\b|\bpromis\w*\b|\bagree\w*\b|\bdeal\b|\bhere (?:is|are|you)\b|\blet me\b",
    'request_or_help': r'\bhelp\w*\b|\bplease\b|\b(?:can|could|will|would) you\b|\bgive\b|\btake\b|\boffer\w*\b|\bshare\w*\b',
}
REGEX = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}

# Human reading of ALL 123 author-bound, lexically indexed, clean prefixes.
# These are broad candidates for quick inspection, not certified agreements.
# Partial/unavailable obligations are deliberately retained with their limits.
REVIEW = {
    (158, 7): 'Actual silver payment; earlier agreement to fetch chair and later request for wine. Inspect whether requested destinations/items exist; dialogue changes topic.',
    (280, 4): 'Human asks bot to hold something; bot agrees; actual coal handover. Observable custody, but no explicit return deadline or return promise.',
    (280, 11): 'Continuation of agreed custody; bot says hungry before actual potato handover. Eating is feasible only if native food flag; not a negotiated return.',
    (304, 6): 'Original authored lending goal and explicit borrow discussion; actual Bible handover. Return can be native Give; reading/sermon itself has no completion flag and bot made no explicit return promise.',
    (593, 6): 'Human offers rake for help and bot says I will use this. Inspect native wield/use affordance; searching for water or digging is not assumed to exist.',
    (659, 7): 'Bot agrees to fetch chair/guide king, then human hands over chair. Moving to a balcony needs a real path, not a claim that holding chair completes it.',
    (721, 9): 'Human asks for a plate and bot agrees; human subsequently obtains and puts plate in cupboard. Native availability changes, but dinner/prayer talk is not certified execution.',
    (1245, 11): 'Human asks for cape to be worn; bot instead says set it out for queen, followed by actual cape handover. Distinct proposed uses, not unambiguous agreement.',
    (1329, 9): 'Explicit accepted help moving broken organ; human obtains and hands organ to nun. Churchyard movement/repair requires real destination/tool support.',
    (1490, 8): 'Explicit original Bible loan discussion and actual handover; no explicit return deadline. Native return is a possibility, reading is not an engine event.',
    (1513, 4): 'Human requests new uniform including cape; bot answers yes, my lord; actual cape handover. Native Wear is a concrete downstream consequence; extra fur-washing talk is not an engine effect.',
    (1649, 9): 'Human asks help with organ; bot asks may I hold it; actual Put organ on stage exposes a real retrieval opportunity. Does not by itself implement moving organ outside.',
    (1708, 9): 'Bot agrees to take tapes to office; human instead puts tapes on box. Inspect whether office/path exists; Get/Put alone is not office delivery.',
    (1766, 11): 'Bot promises to fetch pot and put it on counter; actual human action puts cupboard on counter, not the requested pot. Retained as object/obligation mismatch, not fulfillment.',
    (1893, 6): 'Human proposes weapon trade and actually gives sword; bot asks what sword is wanted. No specific return weapon or final accepted terms yet.',
    (1944, 9): 'Human says only take spear from rucksack; bot claims taking blade; actual human Gives herb bag. Verify named spear/blade is present; do not invent asset or conflate bag with spear.',
    (1956, 10): 'Accepted talk of following/leading and food in exchange; actual rake handover. Follow can be native, bread/water/path may be unsupported; preserve this distinction.',
    (2057, 10): 'Initial uniform/cape command is acknowledged, but later coercive consort/lap dialogue includes explicit bot resistance. Actual cape handover is not consent or an unambiguous continuing agreement.',
}
QUOTE_STEPS = {
    (158, 7): [0, 1, 5, 6], (280, 4): [2, 3], (280, 11): [5, 6, 10],
    (304, 6): [0, 2, 3], (593, 6): [2, 4, 5], (659, 7): [0, 1, 3],
    (721, 9): [0, 1], (1245, 11): [6, 7], (1329, 9): [2, 3, 5, 6],
    (1490, 8): [4, 5], (1513, 4): [0, 1], (1649, 9): [5, 6],
    (1708, 9): [4, 5], (1766, 11): [2, 3], (1893, 6): [4, 5],
    (1944, 9): [7, 8], (1956, 10): [2, 3, 4, 5], (2057, 10): [0, 1, 8, 9],
}


def short_quote(event, index):
    text = event['text']
    return {'dialogue_index': index, 'role': event.get('id', event.get('role')),
            'text': text[:180], 'excerpt_only': len(text) > 180}


def compact_versionable_report(report, prefix_file, replay_file):
    """Keep originals/full prefixes in cache, never version them as benchmark."""
    for row in report['complete_author_bound_lexical_clean_index']:
        hits = row.pop('lexical_hits_before_action')
        row['lexical_hit_index'] = [{k: h[k] for k in ['dialogue_index', 'role', 'lexical_tags']} for h in hits]
        row['short_source_quotes'] = [short_quote(h, h['dialogue_index']) for h in hits[-2:]]
        row['qualification'] = 'Complete archived prefix and target native event successful for both replay seeds; lexical recall, not accepted-cooperation gold.'
        row['raw_prefix_cache'] = str(prefix_file)
    for row in report['human_reading_candidates_not_gold']:
        prefix = row.pop('raw_prefix')
        row['short_source_quotes'] = [short_quote(prefix[i], i) for i in QUOTE_STEPS[(row['demo_index'], row['dialogue_index'])]]
        human = row.pop('original_human_quest')
        row['original_human_goal'] = human['goal']
        bot = row.pop('original_bound_bot_quests')
        row['original_bot_goal_bindings'] = [{'quest_file': q['quest_file'], 'goal': q['quest']['goal']} for q in bot]
        row['native_bot_options_after_prefix'] = [x for x in row['native_bot_options_after_prefix'] if x['involves_human_changed_object'] or x['event_type'] == 'FollowEvent']
        row['raw_prefix_cache'] = str(prefix_file)
        row['full_replay_cache'] = str(replay_file)
    return report


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def short_quest(q):
    return {k: q.get(k) for k in ['character', 'persona', 'goal', 'short_motivation',
                                 'mid_motivation', 'long_motivation', 'timeline']}


def load_quests(path, needed):
    found = {}
    with tarfile.open(path, 'r|gz') as archive:
        for member in archive:
            filename = member.name.rsplit('/', 1)[-1]
            if filename in needed and member.isfile():
                found[filename] = json.load(archive.extractfile(member))['data']
    return found


def native_actor(graph, persona):
    node = graph.get_node(persona['id'])
    if node is not None and node.agent:
        return node, 'exact_archived_id'
    return actor_for(graph, persona['name']), 'unique_original_name'


def replay(demo, quest, seed, modules):
    graph = modules[0].from_json(quest['graph'])
    actors, binding = {}, {}
    for role in ['human', 'bot']:
        actors[role], binding[role] = native_actor(graph, demo[role + '_persona'])
    random.seed(seed)
    host = ViewerHost(graph)
    rows, stats = [], Counter()
    clean = True
    for index, raw in enumerate(demo['dialogue']):
        role, kind = raw.get('id'), raw.get('type')
        row = {'dialogue_index': index, 'role': role, 'archive_type': kind,
               'archive_text': raw.get('text'), 'archive_score': raw.get('score')}
        if role not in actors or kind not in ['speech', 'action']:
            row['exception'] = 'unsupported_archive_role_or_kind'
            clean = False
            rows.append(row)
            continue
        actor = actors[role]
        command = 'say ' + raw['text'] if kind == 'speech' else raw['text']
        row.update(actor_id=actor.node_id, command=command)
        before = material_state(graph) if kind == 'action' else None
        before_messages = len(host.messages)
        try:
            event = parse_event(graph, actor, command, *modules[1:])
            row['event_type'] = type(event).__name__
            row['legal'] = not isinstance(event, modules[2])
            if row['legal']:
                row['target_node_ids'] = [n.node_id for n in event.target_nodes]
                row['canonical_command'] = event.to_canonical_form()
                event.execute(host)
                row['executed'] = bool(event.executed)
                row['stochastic_failure'] = bool(getattr(event, 'failed', False))
            else:
                row['native_error'] = event.view_as(actor)
        except Exception as exc:
            # A failed source prefix remains failed. Do not repair or skip assets.
            row['exception'] = f'{type(exc).__name__}: {exc}'
        ok = row.get('legal', False) and row.get('executed', False) and not row.get('stochastic_failure') and not row.get('exception')
        row['successful_native_event'] = bool(ok)
        clean &= bool(ok)
        row['all_prefix_events_successful'] = clean
        row['messages'] = host.messages[before_messages:]
        if kind == 'action':
            after = material_state(graph)
            changed = {nid: {'before': before.get(nid), 'after': after.get(nid)}
                       for nid in before.keys() | after.keys() if before.get(nid) != after.get(nid)}
            row['changed_nodes'] = changed
            row['material_changed'] = bool(changed)
            stats['actions'] += 1
            stats['successful_actions'] += bool(ok)
            stats['rejected_actions'] += row.get('legal') is False
            stats['stochastic_action_failures'] += row.get('stochastic_failure', False)
            stats['action_exceptions'] += bool(row.get('exception'))
            stats['material_changes'] += bool(changed)
        rows.append(row)
        if row.get('exception'):
            # Mutation after an engine exception is not silently treated as a
            # trustworthy continuation. Later prefixes are reported unavailable.
            break
    return {'seed': seed, 'actors': {k: v.node_id for k, v in actors.items()},
            'actor_binding': binding, 'rows': rows, 'stats': dict(stats),
            'full_dialogue_processed': len(rows) == len(demo['dialogue']),
            'all_prefix_events_successful': clean}


def inspect_prefix(demo, quest, end, seed, modules):
    """Exact source prefix, then enumerate unmodified guarded native options."""
    from light.graph.events.all_events_list import ALL_EVENTS_LIST
    graph = modules[0].from_json(quest['graph'])
    actors = {k: native_actor(graph, demo[k + '_persona'])[0] for k in ['human', 'bot']}
    host = ViewerHost(graph)
    random.seed(seed)
    before_branch = None
    final_event = None
    for i, raw in enumerate(demo['dialogue'][:end + 1]):
        if i == end: before_branch = graph.to_json()
        command = 'say ' + raw['text'] if raw['type'] == 'speech' else raw['text']
        event = parse_event(graph, actors[raw['id']], command, *modules[1:])
        assert not isinstance(event, modules[2]), (i, command)
        event.execute(host)
        assert event.executed and not getattr(event, 'failed', False), (i, command)
        final_event = event
    bot = actors['bot']
    source_id = final_event.target_nodes[0].node_id if final_event.target_nodes else None
    options = []
    for cls in ALL_EVENTS_LIST:
        for event in cls.get_valid_actions(graph, bot):
            if cls.__name__ not in {'GiveObjectEvent', 'PutObjectInEvent', 'GetObjectEvent',
                    'DropObjectEvent', 'EatEvent', 'DrinkEvent', 'WearEvent', 'WieldEvent',
                    'FollowEvent', 'GoEvent', 'RemoveObjectEvent'}:
                continue
            guarded = cls.construct_from_args(bot, event.target_nodes, event.text_content)
            if isinstance(guarded, modules[2]): continue
            options.append({'event_type': cls.__name__, 'actor_id': bot.node_id,
                            'target_node_ids': [n.node_id for n in event.target_nodes],
                            'command': event.to_canonical_form(),
                            'involves_human_changed_object': any(n.node_id == source_id for n in event.target_nodes)})
    # Verify concrete object continuations on independent untouched forks. This
    # witnesses a primitive effect, never the truth of the surrounding promise.
    for option in options:
        if not option['involves_human_changed_object']: continue
        fork = modules[0].from_json(graph.to_json())
        cls = getattr(modules[1], option['event_type'])
        actor = fork.get_node(bot.node_id)
        event = cls.construct_from_args(actor, [fork.get_node(i) for i in option['target_node_ids']], None)
        before = material_state(fork)
        event.execute(ViewerHost(fork))
        option['native_continuation_witness'] = {'executed': bool(event.executed),
            'stochastic_failure': bool(getattr(event, 'failed', False)),
            'material_changed': material_state(fork) != before}
    return {'before_final_human_action_graph': before_branch, 'after_prefix_graph': graph.to_json(),
            'actor_ids': {k: v.node_id for k, v in actors.items()},
            'native_bot_options_after_prefix': sorted(options, key=lambda x: (x['event_type'], x['target_node_ids']))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=CACHE / 'runs/e81_human_prefix_inventory')
    ap.add_argument('--report', type=Path, default=WB / 'results/E81_human_prefix_inventory.json')
    ap.add_argument('--seeds', type=int, nargs='+', default=[8101, 8102])
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    demo_path, join_path = CACHE / 'light_quests_human_demos.json', CACHE / 'light_npc_human_join.json'
    demos, joins = json.loads(demo_path.read_text()), json.loads(join_path.read_text())
    join_by_demo = defaultdict(list)
    for row in joins:
        join_by_demo[row['demo_index']].append(row)
    needed = {d['location']['quest_file'] for d in demos}
    needed.update(q['file'] for row in joins for q in row['npc_goals'])
    quests = load_quests(CACHE / 'quest_stems.tar.gz', needed)
    modules = load_event_modules(SOURCE)
    counts, action_counts, replay_counts = Counter(), Counter(), Counter()
    errors, candidates, demo_index = Counter(), [], []
    graph_sets = defaultdict(set)
    event_counts = Counter((e.get('id'), e.get('type')) for d in demos for e in d['dialogue'])
    replay_file, prefix_file = args.out / 'replayed_demos.jsonl', args.out / 'candidate_prefixes.jsonl'
    with replay_file.open('w') as replay_handle, prefix_file.open('w') as prefix_handle:
        for di, demo in enumerate(demos):
            qfile = demo['location']['quest_file']
            quest = quests.get(qfile)
            base = {'demo_index': di, 'quest_file': qfile,
                    'original_human_persona': demo['human_persona'], 'original_bot_persona': demo['bot_persona'],
                    'archived_model_name': demo['model_name'], 'same_graph_author_bindings': join_by_demo[di]}
            if quest is None:
                errors['missing_quest_graph'] += 1
                replay_handle.write(json.dumps({**base, 'exception': 'missing_quest_graph'}) + '\n')
                continue
            gh = hashlib.sha256(quest['graph'].encode()).hexdigest()
            graph_sets['all_archive_worlds'].add(gh)
            if join_by_demo[di]: graph_sets['joined_archive_worlds'].add(gh)
            base.update(graph_sha256=gh, original_human_quest=short_quest(quest))
            bound = []
            for j in join_by_demo[di]:
                for nq in j['npc_goals']:
                    v = quests.get(nq['file'])
                    bound.append({'quest_file': nq['file'], 'exact_graph_match': bool(v and v['graph'] == quest['graph']),
                                  'source_quest': short_quest(v) if v else None})
            base['original_bound_bot_quests'] = bound
            replays = []
            for seed in args.seeds:
                try:
                    r = replay(demo, quest, seed, modules)
                except Exception as exc:
                    r = {'seed': seed, 'exception': f'{type(exc).__name__}: {exc}', 'rows': []}
                    errors[r['exception']] += 1
                replays.append(r)
                replay_counts.update(r.get('stats', {}))
            replay_handle.write(json.dumps({**base, 'replays': replays}, ensure_ascii=False) + '\n')
            index = {'demo_index': di, 'graph_sha256': gh, 'quest_file': qfile,
                     'joined': bool(join_by_demo[di]), 'archive_actions': sum(x['type'] == 'action' for x in demo['dialogue']),
                     'replay_full_processed_per_seed': [r.get('full_dialogue_processed', False) for r in replays],
                     'replay_all_successful_per_seed': [r.get('all_prefix_events_successful', False) for r in replays]}
            demo_index.append(index)
            for r in replays:
                for row in r['rows']:
                    if row.get('native_error'): errors[row['native_error']] += 1
                    if row.get('exception'): errors[row['exception']] += 1
            for ei, raw in enumerate(demo['dialogue']):
                if raw['type'] != 'action': continue
                verb = raw['text'].split(' ', 1)[0].lower()
                action_counts[verb] += 1
                if verb not in TARGET_VERBS: continue
                counts['target_action_attempts'] += 1
                graph_sets['target_action_worlds'].add(gh)
                prefix = demo['dialogue'][:ei + 1]
                hits = []
                for si, speech in enumerate(prefix[:-1]):
                    if speech['type'] != 'speech': continue
                    tags = [k for k, pattern in REGEX.items() if pattern.search(speech['text'])]
                    if tags:
                        hits.append({'dialogue_index': si, 'role': speech['id'], 'text': speech['text'], 'lexical_tags': tags})
                native = []
                for r in replays:
                    row = next((x for x in r['rows'] if x['dialogue_index'] == ei), None)
                    native.append({'seed': r['seed'], 'available': row is not None,
                                   **({k: row.get(k) for k in ['actor_id', 'event_type', 'target_node_ids', 'canonical_command',
                                       'legal', 'executed', 'stochastic_failure', 'successful_native_event', 'material_changed',
                                       'changed_nodes', 'all_prefix_events_successful', 'native_error', 'exception']} if row else {})})
                successful = all(x.get('successful_native_event', False) for x in native)
                clean = all(x.get('all_prefix_events_successful', False) for x in native)
                record = {'prefix_id': f'human-demo-{di}-event-{ei}', 'demo_index': di, 'dialogue_index': ei,
                          'graph_sha256': gh, 'quest_file': qfile, 'joined_author_goal_count': len(bound),
                          'role': raw['id'], 'archive_command': raw['text'], 'archive_score': raw.get('score'),
                          'verb': verb, 'lexical_hits_before_action': hits,
                          'lexical_hits_last_six_events': [x for x in hits if x['dialogue_index'] >= ei - 6],
                          'native_action_per_seed': native, 'target_successful_all_replay_seeds': successful,
                          'all_prefix_events_successful_all_replay_seeds': clean,
                          'semantic_scope': 'Lexical recall candidate only; no certified proposal/agreement/fulfillment relation. Archive action is an attempt text, not original serialized execution outcome.'}
                candidates.append(record)
                prefix_handle.write(json.dumps({**base, **record, 'full_original_dialogue_prefix': prefix}, ensure_ascii=False) + '\n')
                if hits:
                    counts['lexically_indexed_target_prefixes'] += 1
                    graph_sets['lexical_target_worlds'].add(gh)
                    if successful:
                        counts['lexical_target_native_success_both_seeds'] += 1
                        graph_sets['lexical_native_success_worlds'].add(gh)
                    if clean:
                        counts['lexical_clean_prefixes_both_seeds'] += 1
                        graph_sets['lexical_clean_worlds'].add(gh)
                counts['target_native_success_both_seeds'] += successful
                counts['target_clean_prefixes_both_seeds'] += clean
                counts['joined_target_prefixes'] += bool(bound)
                if bound and hits and clean:
                    counts['joined_lexical_clean_prefixes_both_seeds'] += 1
                    graph_sets['joined_lexical_clean_worlds'].add(gh)
            if (di + 1) % 250 == 0:
                print(json.dumps({'processed_demos': di + 1, 'target_prefixes': len(candidates)}), flush=True)
    # Keep large raw traces in the cache. The versionable report contains the
    # complete 123-row inspection index and 18 transparent reading candidates.
    demo_index_path = args.out / 'demo_index.jsonl'
    demo_index_path.write_text(''.join(json.dumps(x) + '\n' for x in demo_index))
    authored_candidates = [x for x in candidates if x['joined_author_goal_count'] and
                           x['all_prefix_events_successful_all_replay_seeds'] and x['lexical_hits_before_action']]
    by_id = {(x['demo_index'], x['dialogue_index']): x for x in candidates}
    inspected = []
    snapshot_path = args.out / 'review_candidate_native_snapshots.jsonl'
    with snapshot_path.open('w') as handle:
        for (di, ei), note in REVIEW.items():
            source = by_id[(di, ei)]
            detail = inspect_prefix(demos[di], quests[source['quest_file']], ei, args.seeds[0], modules)
            handle.write(json.dumps({'prefix_id': source['prefix_id'], **detail}, ensure_ascii=False) + '\n')
            inspected.append({'prefix_id': source['prefix_id'], 'demo_index': di, 'dialogue_index': ei,
                'graph_sha256': source['graph_sha256'], 'quest_file': source['quest_file'],
                'human_action': source['archive_command'], 'human_native_events': [
                    {k: n.get(k) for k in ['seed', 'actor_id', 'event_type', 'target_node_ids', 'canonical_command', 'successful_native_event']}
                    for n in source['native_action_per_seed']],
                'original_human_quest': short_quest(quests[source['quest_file']]),
                'original_bound_bot_quests': [{'quest_file': q['file'], 'quest': short_quest(quests[q['file']])}
                    for j in join_by_demo[di] for q in j['npc_goals']],
                'raw_prefix': demos[di]['dialogue'][:ei + 1], 'reading_note_not_gold': note,
                'native_bot_options_after_prefix': detail['native_bot_options_after_prefix']})
    report = {'scope': 'Full archived human demonstration source inventory and unchanged native replay. Lexical recall only, no semantic cooperation gold or new model experiment.',
              'archive_demo_count': len(demos), 'same_graph_join_rows': len(joins),
              'joined_distinct_demo_count': sum(bool(v) for v in join_by_demo.values()), 'event_kind_counts': {f'{r}:{t}': n for (r, t), n in event_counts.items()},
              'archive_action_verb_counts': dict(action_counts), 'counts': dict(counts),
              'independent_graph_counts': {k: len(v) for k, v in graph_sets.items()},
              'replay_aggregate_across_seeds': dict(replay_counts), 'seeds': args.seeds,
              'demo_full_replay_success_both_seeds': sum(all(x['replay_all_successful_per_seed']) for x in demo_index),
              'demo_all_events_processed_both_seeds': sum(all(x['replay_full_processed_per_seed']) for x in demo_index),
              'native_rejections_and_exceptions_across_seeds': dict(errors.most_common()),
              'original_physical_bot_action_records': event_counts.get(('bot', 'action'), 0),
              'limitations': ['No original serialized native event outcomes or RNG states are present: native replay proves present source reachability, not exact historical execution.',
                             'The archive contains human physical action attempts and both sides speech; no bot physical action is recorded. Verbal giving is not reconstructed as a physical action.',
                             'Both fixed replay seeds are retained. Failed, rejected or exceptional prefixes are not repaired; after an exception no continuation is certified.',
                             'Matching words do not certify natural cooperation, an accepted condition, mutual benefit, or a promise referring to the subsequent action.',
                             'Independently authored same-graph bot goals are alternative annotations, not evidence that the original archival bot used those goals.'],
              'source_sha': subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip(),
              'inputs': {str(p): digest(p) for p in [demo_path, join_path, CACHE / 'quest_stems.tar.gz']},
              'artifacts': {str(p): digest(p) for p in [replay_file, prefix_file, demo_index_path, snapshot_path]},
              'complete_author_bound_lexical_clean_index': [{
                  k: x[k] for k in ['prefix_id', 'demo_index', 'dialogue_index', 'graph_sha256', 'quest_file',
                      'archive_command', 'joined_author_goal_count', 'lexical_hits_before_action']}
                  | {'native_events': [{k: n.get(k) for k in ['seed', 'actor_id', 'event_type', 'target_node_ids', 'canonical_command']}
                                      for n in x['native_action_per_seed']]} for x in authored_candidates],
              'human_reading_candidates_not_gold': inspected,
              'reading_scope': 'Read all 123 author-bound lexical clean source prefixes in full; 18 broad candidates/near-misses retained, including missing physical obligation support. No semantic acceptance threshold, success gold or experimental cohort is assigned.',
              'human_reading_candidate_count': len(inspected),
              'human_reading_candidate_distinct_worlds': len({x['graph_sha256'] for x in inspected}),
              'wall_seconds': time.monotonic() - started, 'inference_api_calls': 0, 'gpu_hours': 0}
    report = compact_versionable_report(report, prefix_file, replay_file)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['complete_author_bound_lexical_clean_index', 'human_reading_candidates_not_gold', 'native_rejections_and_exceptions_across_seeds']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
