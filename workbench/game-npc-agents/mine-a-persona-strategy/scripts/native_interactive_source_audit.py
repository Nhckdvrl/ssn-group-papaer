#!/usr/bin/env python3
"""CPU SOURCE AUDIT/POST-HOC: original playable opportunities, no world edits.

env PYTHONPATH=/home/xiang/.cache/game-npc-research/deps \
 /home/xiang/miniconda3/envs/fgvd/bin/python \
 workbench/game-npc-agents/scripts/native_interactive_source_audit.py

Enumerates and parses original native menus; executes no game action or model.
Lexical dialogue markers are not semantic labels, goals, promises or utility gold.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import tarfile

from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import actor_for, ViewerHost
from native_owned_container_qualification import event_id

CACHE = Path('/home/xiang/.cache/game-npc-research')
RUNS = CACHE / 'runs'
WB = Path(__file__).resolve().parents[1]
SOURCE = CACHE / 'sources/LIGHT'
SEEDS = [7501, 7502, 7503]
MARKERS = {
    'question_mark': re.compile(r'\?'),
    'if_or_unless_word': re.compile(r'\b(?:if|unless)\b', re.I),
    'before_or_first_word': re.compile(r'\b(?:before|first)\b', re.I),
    'trade_exchange_return_word': re.compile(r'\b(?:trade|exchange)\b|\bin return\b', re.I),
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def menu(g, actor, cls, mods):
    """Keep only candidate commands that parse back to exactly the same IDs."""
    records, rebound = {}, 0
    for e in cls.get_valid_actions(g, actor):
        cmd = e.to_canonical_form()
        identity = event_id(e, mods)
        parsed = event_id(parse_event(g, actor, cmd, *mods[1:]), mods)
        if parsed != identity:
            rebound += 1
            continue
        records[cmd] = {'command': cmd, 'event_type': identity[0], 'target_node_ids': list(identity[1])}
    return sorted(records.values(), key=lambda x: x['command']), rebound


def inventory(node):
    return [{'item_id': x.node_id, 'name': x.name, 'equipped': x.get_prop('equipped'),
             'food': bool(x.get_prop('food')), 'drink': bool(x.get_prop('drink'))}
            for x in sorted(node.get_contents(), key=lambda x: x.node_id) if x.object]


def annotate_conversations(rows, source_hashes):
    all_c = defaultdict(list)
    for model in ['gemma', '32b']:
        for shard in ['s0', 's1']:
            path = RUNS / f'e75_{model}_{shard}' / 'episodes.jsonl'
            source_hashes[str(path)] = sha(path)
            for line, r in enumerate(map(json.loads, path.open()), 1):
                if r['condition'] != 'retrieval_baseline':
                    continue
                text = (r['conversation'] or {}).get('reply', '')
                flags = {name: bool(rx.search(text)) for name, rx in MARKERS.items()}
                all_c[r['case_id']].append({'model': model, 'persona': r['persona'], 'seed': r['seed'],
                    'stance_field': (r['conversation'] or {}).get('stance'), 'lexical_markers': flags,
                    'reply': text, 'source_path': str(path), 'line_1based': line})
    assert sum(map(len, all_c.values())) == 1224
    assert set(all_c) == {r['case']['case_id'] for r in rows}
    for cid, cs in all_c.items():
        assert len(cs) == 12
        assert {(c['model'], c['persona'], c['seed']) for c in cs} == {
            (m, p, s) for m in ['gemma', '32b'] for p in ['firm', 'agreeable'] for s in SEEDS}
    return all_c


def conversation_counts(cs):
    counts = Counter(utterances=len(cs))
    for c in cs:
        counts['stance_' + str(c['stance_field'])] += 1
        counts.update({k: int(v) for k, v in c['lexical_markers'].items()})
    return dict(counts)


def audit_case(c, mods):
    g = mods[0].from_json(c['quest']['graph'])
    original = g.to_json()
    a, p = g.get_node(c['actor_id']), g.get_node(c['requester_id'])
    item = g.get_node(c['item_id']); iid = item.node_id
    goal_identity = event_id(parse_event(g, a, c['goal_command'], *mods[1:]), mods)
    assert a.get_room() == p.get_room() and not a.get_prop('dead') and not p.get_prop('dead')
    tables = {}; rejected = Counter()
    classes = ['GetObjectEvent', 'GiveObjectEvent', 'RemoveObjectEvent', 'StealObjectEvent',
               'DropObjectEvent', 'PutObjectInEvent', 'BlockEvent', 'FollowEvent',
               'HugEvent', 'HelpEvent', 'WearEvent', 'WieldEvent', 'EatEvent', 'DrinkEvent']
    for role, node in [('npc', a), ('requester', p)]:
        tables[role] = {}
        for name in classes:
            records, failures = menu(g, node, getattr(mods[1], name), mods)
            tables[role][name] = records
            rejected[role + '/' + name] += failures
    requester_gives = [e for e in tables['requester']['GiveObjectEvent'] if e['target_node_ids'][1] == a.node_id]
    requester_get_source = [e for e in tables['requester']['GetObjectEvent'] if e['target_node_ids'][0] == iid]
    requester_get_other = [e for e in tables['requester']['GetObjectEvent'] if e['target_node_ids'][0] != iid]
    npc_give_other = [e for e in tables['npc']['GiveObjectEvent']
                      if e['target_node_ids'][0] != iid and e['target_node_ids'][1] == p.node_id]
    requester_steal_source = [e for e in tables['requester']['StealObjectEvent']
                            if e['target_node_ids'] == [iid, a.node_id]]
    examines, failures = menu(g, a, mods[1].ExamineEvent, mods)
    examiner = [e for e in examines if e['target_node_ids'] == [p.node_id]]
    rejected['npc/ExamineEvent'] += failures
    # Exact native inventory wording available on legal Examine. This is a
    # read-only view call, never an executed observation or private reveal.
    inv_text = ViewerHost(g).view.get_inventory_text_for(p.node_id, give_empty=True)
    summary = {
        'requester_has_direct_inventory': bool(inventory(p)),
        'requester_has_equipped_item': any(x['equipped'] for x in inventory(p)),
        'requester_has_immediate_give_to_npc': bool(requester_gives),
        'requester_has_native_remove_candidate': bool(tables['requester']['RemoveObjectEvent']),
        'requester_can_directly_get_source_item': bool(requester_get_source),
        'requester_has_other_native_get_candidate': bool(requester_get_other),
        'requester_has_native_steal_source_candidate': bool(requester_steal_source),
        'npc_has_immediate_alternative_asset_give': bool(npc_give_other),
        'npc_can_legally_examine_requester': bool(examiner),
        'source_item_directly_held_by_npc': item.get_container().node_id == a.node_id,
        'source_item_directly_in_room': item.get_container() == a.get_room(),
    }
    assert g.to_json() == original, 'Source world mutated by read-only enumeration/view'
    return {'case_id': c['case_id'], 'source_graph_sha256': c['graph_sha256'],
        'source_quest_file': c.get('quest_file'), 'goal_kind': c['goal_kind'],
        'actor_id': a.node_id, 'requester_id': p.node_id, 'source_item_id': iid,
        'goal_command': c['goal_command'], 'request_command': c['request_command'],
        'original_native_goal_identity': [goal_identity[0], list(goal_identity[1])] if goal_identity else None,
        'source_item_name': item.name, 'source_item_parent_id': item.get_container().node_id,
        'source_item_equipped': item.get_prop('equipped'),
        'source_npc_authored_context': {k: c['quest'].get(k) for k in
            ['character', 'persona', 'goal', 'short_motivation', 'mid_motivation', 'long_motivation']},
        'requester_native_persona': p.get_prop('persona'),
        'npc_original_direct_inventory': inventory(a), 'requester_original_direct_inventory': inventory(p),
        'requester_inventory_native_examine_text': inv_text,
        'npc_examine_requester_commands': examiner,
        'requester_immediate_give_to_npc': requester_gives,
        'requester_native_get_source': requester_get_source,
        'requester_native_get_other_items': requester_get_other,
        'requester_native_steal_source': requester_steal_source,
        'requester_native_remove_candidates': tables['requester']['RemoveObjectEvent'],
        'npc_immediate_alternative_give_to_requester': npc_give_other,
        'native_action_candidate_counts': {role: {cls: len(es) for cls, es in vals.items()} for role, vals in tables.items()},
        'enumerated_commands_rejected_or_rebound_by_parser': dict(rejected),
        'source_facts': summary}


def main():
    data75 = RUNS / 'e75_native_retrieval_qualification/snapshots.jsonl'
    rows75 = list(map(json.loads, data75.open())); assert len(rows75) == 102
    manifest55 = RUNS / 'e55_gemma_confirm/manifest.json'
    m55 = json.loads(manifest55.read_text()); data200 = Path(m55['arguments']['dataset'])
    assert sha(data200) == m55['dataset_sha256']
    cases200 = list(map(json.loads, data200.open())); assert len(cases200) == 200
    pack63 = RUNS / 'e63_native_dependency_qualification/snapshots.jsonl'
    source63 = list(map(json.loads, pack63.open())); cases63 = [r['case'] for r in source63]
    assert {c['graph_sha256']: c['quest']['graph'] for c in cases200} == {c['graph_sha256']: c['quest']['graph'] for c in cases63}
    hashes = {str(p): sha(p) for p in [data75, data200, manifest55, pack63]}
    cohorts = {'E75_original_floor_102': [r['case'] for r in rows75], 'E55_E63_original_held_200': cases63}
    mods = load_event_modules(SOURCE)
    all_c = annotate_conversations(rows75, hashes)
    by_hash = {c['graph_sha256']: c for cases in cohorts.values() for c in cases}
    annotation = defaultdict(list)
    archive = CACHE / 'quest_stems.tar.gz'; hashes[str(archive)] = sha(archive)
    with tarfile.open(archive, 'r|gz') as handle:
        for member in handle:
            if not member.name.endswith('.json'):
                continue
            q = json.load(handle.extractfile(member))['data']
            graph_hash = hashlib.sha256(q['graph'].encode()).hexdigest()
            if graph_hash not in by_hash:
                continue
            g = mods[0].from_json(q['graph'])
            try:
                aid = actor_for(g, q['character']).node_id
            except AssertionError:
                aid = None
            annotation[graph_hash].append({'quest_file': member.name, 'actor_id': aid,
                'character': q['character'], 'goal': q['goal'], 'short_motivation': q.get('short_motivation')})
    result = {}
    for name, cases in cohorts.items():
        case_facts = []; totals = Counter(worlds=len(cases)); by_kind = {}
        for c in cases:
            facts = audit_case(c, mods)
            alternatives = [q for q in annotation[c['graph_sha256']] if q['actor_id'] == c['requester_id']]
            facts['requester_alternative_authored_quest_annotations'] = alternatives
            facts['same_graph_archived_quest_annotation_count'] = len(annotation[c['graph_sha256']])
            facts['source_facts']['requester_has_archived_authored_goal_annotation'] = bool(alternatives)
            if c['case_id'] in all_c:
                facts['E75_dialogue_surface_counts'] = conversation_counts(all_c[c['case_id']])
            totals.update({k: int(v) for k, v in facts['source_facts'].items()})
            totals['archived_quest_records_on_source_graphs'] += len(annotation[c['graph_sha256']])
            by_kind.setdefault(c['goal_kind'], Counter(worlds=0)); by_kind[c['goal_kind']]['worlds'] += 1
            by_kind[c['goal_kind']].update({k: int(v) for k, v in facts['source_facts'].items()})
            if name == 'E55_E63_original_held_200':
                assert facts['original_native_goal_identity'] is not None
                assert facts['original_native_goal_identity'][1][0] == c['item_id']
            # The existing snapshots hold complete worlds/motivations. This
            # compact source index does not duplicate those snapshots.
            keep = ['case_id', 'source_graph_sha256', 'source_quest_file', 'goal_kind', 'actor_id',
                'requester_id', 'source_item_id', 'source_item_name', 'source_item_parent_id',
                'source_item_equipped', 'goal_command', 'request_command', 'original_native_goal_identity',
                'requester_original_direct_inventory', 'requester_immediate_give_to_npc',
                'requester_native_get_source', 'requester_native_steal_source',
                'npc_immediate_alternative_give_to_requester', 'source_facts',
                'same_graph_archived_quest_annotation_count', 'E75_dialogue_surface_counts']
            compact = {k: facts[k] for k in keep if k in facts}
            compact['requester_other_get_candidate_count'] = len(facts['requester_native_get_other_items'])
            compact['npc_native_action_class_counts'] = facts['native_action_candidate_counts']['npc']
            compact['requester_native_action_class_counts'] = facts['native_action_candidate_counts']['requester']
            compact['requester_authored_alternative_goal_texts'] = [q['goal'] for q in alternatives]
            case_facts.append(compact)
        result[name] = {'counts': dict(totals), 'by_original_goal_kind': {k: dict(v) for k, v in by_kind.items()}, 'cases': case_facts}
    # Fixed evenly spaced original indices, never selected by success, stance or
    # narrative. First seed is fixed for four exact role/model replies per graph.
    example_indices = [(i*(len(rows75)-1))//9 for i in range(10)]
    examples = []
    for idx in example_indices:
        cid = rows75[idx]['case']['case_id']
        examples.append({'source_order_index_0based': idx, 'case_id': cid,
                         'replies': [c for c in all_c[cid] if c['seed'] == SEEDS[0]]})
    global_c = {'all': conversation_counts([c for cs in all_c.values() for c in cs])}
    for model in ['gemma', '32b']:
        for persona in ['firm', 'agreeable']:
            global_c[model + '/' + persona] = conversation_counts([c for cs in all_c.values() for c in cs
                                                                  if c['model'] == model and c['persona'] == persona])
    output = {'status': 'COMPLETE_CPU_SOURCE_AUDIT_POST_HOC', 'model_calls': 0, 'gpu_hours': 0,
        'native_actions_executed': 0, 'worlds_modified': 0,
        'source_world_union': len(by_hash), 'source_world_overlap': len(set(c['graph_sha256'] for c in cohorts['E75_original_floor_102'])
                                                                      & set(c['graph_sha256'] for c in cases200)),
        'primary_reusable_source': {'path': str(pack63), 'sha256': sha(pack63),
            'rows': 200, 'schema': {'npc_world': 'row.case.quest.graph',
                'npc_authored_persona_and_motivations': 'row.case.quest.{persona,short_motivation,mid_motivation,long_motivation}',
                'actor_id': 'row.case.actor_id', 'requester_id': 'row.case.requester_id',
                'source_item_id': 'row.case.item_id', 'native_goal_command': 'row.case.goal_command',
                'source_request_command': 'row.requests.goal_item.command',
                'source_request_text': 'row.requests.goal_item.request_text'},
            'selected_source_request_scope': 'Existing E63 goal_item request; no other_item sampling or new resources/utility goals.',
            'source_order_retained': True},
        'cohorts': result, 'E75_dialogue_surface_counts': global_c,
        'equidistant_original_dialogue_examples': examples,
        'definitions': {'native_candidate': 'Original native candidate reparses to the same exact event type and target IDs; no action executed.',
            'observable_inventory': 'Requester inventory is displayed by original WorldViewer when the NPC legally examines that requester; not guaranteed in the original immediate look.',
            'alternative_asset': 'Object distinct from the selected source item; no semantic/utility relevance asserted.',
            'lexical_dialogue_markers': {k: rx.pattern for k, rx in MARKERS.items()},
            'stance': 'Original structured model field, not independently verified acceptance, promise, rejection or bargaining gold.',
            'authored_requester_quests': 'Alternative archived author annotations on the same graph, not automatically simultaneously active private goals.',
            'E63_relation': 'E63 packs preserve exactly the same 200 original graph strings as E55 sources; no added resource/quest.'},
        'scope': ['Source audit for the E80 interactive baseline, not an executed model experiment or quality filter. E78/E79 future mentions do not denote completed experiments.',
            'Keep all source worlds; no manufactured objects, inventory transfers, utility gold or semantic API labels.',
            'Native Get/Steal by requester is distinct from NPC voluntary Give; self-acquisition cannot count as NPC social compliance.',
            'Inventory and native transfer availability establish physical opportunity, not mutually beneficial exchange or author-intended bargain.',
            'Existing E75 generic requests were chosen by native eligibility; requester archived goals/persona may motivate different natural interactions.',
            'Equidistant snippets are a finite original-text review aid, not a quantitative semantic claim.',
            'No new model run, driver change, prompt tuning, research status change or git commit.'],
        'source_sha256': hashes, 'script_sha256': sha(Path(__file__))}
    path = WB / 'results/E80_source_audit.json'
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': output['status'], 'union': len(by_hash),
                      'cohort_counts': {k: v['counts'] for k, v in result.items()},
                      'dialogue_counts': global_c['all'], 'out': str(path)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
