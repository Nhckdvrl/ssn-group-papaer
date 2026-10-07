"""E94 deterministic timing map of author reward on released observation traces."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import re

import numpy as np

from data import sha, write_jsonl
from data_v2 import digest
from analyze_correct_answer_carry import estimate


def oracle_state(gt):
    # Retain author's observed object/state dictionaries, not a simulator oracle.
    objects = dict(gt['object_locations'])
    raw_inv = gt['current_inventory']
    inv = None
    if raw_inv:
        m = re.match(r'^([\w ]+?\d+)\b', raw_inv)
        assert m, 'Inventory must name an observed numbered instance'
        inv = m.group(1).strip()
        objects[inv] = 'in_hand'
    result = dict(state=dict(objects=objects, states=dict(gt['object_states']),
                             visited=sorted(gt['visited']),
                             unvisited_candidates=sorted(gt['unvisited_candidates'])),
                  task={}, prediction='')
    return result, dict(raw_inventory=raw_inv, inventory_instance=inv,
                        inventory_normalized=raw_inv is not None and raw_inv != inv,
                        compound_object_keys=[k for k in gt['object_locations'] if ' from ' in k or ' with ' in k],
                        compound_state_keys=[k for k in gt['object_states'] if ' from ' in k or ' with ' in k])


def action_type(action):
    first = action.split()[0].lower()
    if first in {'take', 'put', 'heat', 'cool', 'clean', 'open', 'close'}:
        return 'STATE_CHANGING'
    if first in {'go', 'look', 'examine'}:
        return 'INFORMATION_ONLY'
    return 'OTHER'


def run(root, code_root):
    raw = code_root / 'data/alfworld_rebel/rebel_coldstart.json'
    tracker_path = code_root / 'agent_system/environments/env_package/alfworld/belief_tracker.py'
    assert sha(raw) == '0a61235269b17140e22a76d260efd0aec109faeffcb90e4a4d8faf25696d89ae'
    assert sha(tracker_path) == 'f8890ad3f2f0b94992948f5b0346e826a9b126847eed57f39e2f314d481d44bc'
    spec = importlib.util.spec_from_file_location('author_alfworld_beliefs', tracker_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reward = module.RebelRewardCalculator()
    episodes = json.loads(raw.read_text())
    root.mkdir(parents=True, exist_ok=True)
    records = []
    terminal = []
    trajectory_shas = []
    for i, episode in enumerate(episodes):
        steps = episode['data']
        assert [x['step'] for x in steps] == list(range(1, len(steps) + 1))
        actions = []
        for x in steps:
            matches = re.findall(r'<action>\s*(.*?)\s*</action>', x['response'], re.S | re.I)
            assert len(matches) == 1
            actions.append(matches[0].strip())
        traj_sha = digest(json.dumps([(x['obs'], a) for x, a in zip(steps, actions)]))
        trajectory_shas.append(traj_sha)
        tracker = module.GroundTruthTracker()
        tracker.update_from_observation(steps[0]['obs'])
        for j, (x, action) in enumerate(zip(steps, actions)):
            before = copy.deepcopy(tracker.get_ground_truth_state())
            if j + 1 == len(steps):
                terminal.append(dict(episode_index=i, step=x['step'], action=action, reason='No published next observation'))
                continue
            next_obs = steps[j + 1]['obs']
            tracker.update_from_observation(next_obs, action)
            after = copy.deepcopy(tracker.get_ground_truth_state())
            b_before, before_meta = oracle_state(before)
            b_after, after_meta = oracle_state(after)
            for b in [b_before, b_after]:
                parsed = module.BeliefStateParser.parse_belief('<belief>' + json.dumps(b) + '</belief>')
                assert parsed and parsed['state'] == b['state']
            step = x['step']
            def grade(b, g):
                a = reward.calculate_state_reward(b, g, step)
                assert reward.calculate_state_reward(b, g, step) == a
                return a
            bb, ba = grade(b_before, before), grade(b_before, after)
            ab, aa = grade(b_after, before), grade(b_after, after)
            if b_before['state'] == b_after['state']:
                assert bb == ab and ba == aa
            uid = f'E94:episode:{i}:step:{step}'
            changed = [k for k in b_before['state'] if b_before['state'][k] != b_after['state'][k]]
            records.append(dict(item_id=uid, sentence_sha256=digest(uid), cluster_id=traj_sha,
                                episode_index=i, task=episode['task'], author_success=episode['done'],
                                step=step, action=action, action_type=action_type(action),
                                current_observation=x['obs'], next_observation=next_obs,
                                before_belief=b_before, after_belief=b_after,
                                before_gt=before, after_gt=after,
                                before_parser_metadata=before_meta, after_parser_metadata=after_meta,
                                changed_fields=changed, changed_state=bool(changed),
                                nothing_happens='nothing happens' in next_obs.lower(),
                                lenient_step=step < 2, scores=dict(BEFORE_BEFORE=bb, BEFORE_AFTER=ba,
                                                                AFTER_BEFORE=ab, AFTER_AFTER=aa),
                                anticipation_preference=aa-ba, truthful_before_reward_shift=ba-bb,
                                anticipation_prefers=float(aa > ba + 1e-12),
                                anticipation_ties=float(abs(aa-ba) <= 1e-12)))
    assert len(records) == 4983 and len(terminal) == 426
    out = root / 'transition-map-v1.jsonl'
    assert not out.exists()
    write_jsonl(out, records)
    write_jsonl(root / 'terminal-without-next-v1.jsonl', terminal)
    panels = []
    for typ in ['ALL', 'STATE_CHANGING', 'INFORMATION_ONLY', 'OTHER']:
        for changed in ['ALL', 'CHANGED', 'SAME']:
            for timing in ['ALL', 'LENIENT_FIRST', 'REGULAR']:
                rs = [r for r in records if (typ == 'ALL' or r['action_type'] == typ)
                      and (changed == 'ALL' or r['changed_state'] == (changed == 'CHANGED'))
                      and (timing == 'ALL' or r['lenient_step'] == (timing == 'LENIENT_FIRST'))]
                panels.append(dict(action_type=typ, state_change=changed, step_regime=timing, transitions=len(rs),
                                   metrics={k: estimate(rs, [r[k] for r in rs], seed=94)
                                            for k in ['anticipation_preference', 'truthful_before_reward_shift',
                                                      'anticipation_prefers', 'anticipation_ties']},
                                   row_means={k: float(np.mean([r[k] for r in rs])) if rs else None
                                              for k in ['anticipation_preference', 'truthful_before_reward_shift']}))
    summary = dict(panels=panels, raw_sha256=sha(raw), author_tracker_sha256=sha(tracker_path),
                   author_revision=json.loads((code_root / 'provenance.json').read_text())['revision'],
                   code_sha256=sha(Path(__file__)), map_sha256=sha(out), episodes=len(episodes),
                   unique_trace_clusters=len(set(trajectory_shas)), transitions=len(records),
                   terminal_without_next=len(terminal), new_model_outputs=0, new_api_calls=0, gpu_hours=0,
                   limits='Released successful SFT traces; author cumulative-observation parser reference, not complete simulator truth. Original generated beliefs not used as gold. Inventory first numbered-instance normalization declared before scoring; raw GT and parser anomalies retained.',
                   statistics='Transition Source means then duplicate-trace clusters; 10000 bootstrap seed94. Does not establish independent environments or a general cross-model law.')
    p = root / 'observable-credit-timing-map-v1.json'
    p.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(path=str(p), sha256=sha(p), transitions=len(records), panels=len(panels))))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--code-root', type=Path, required=True)
    a = p.parse_args()
    run(a.root, a.code_root)
