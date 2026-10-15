#!/usr/bin/env python3
"""E65 paired physical outcomes plus native plan replay; no semantic judge."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate
from native_dependency_plan_analysis import analyze
from native_constraint_scope import RULES
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE


def metrics(row, source, modules):
    plan, replay = analyze(row, source, modules)
    history = row['history']
    streak = maximum = 0
    unchanged = 0
    for h in history:
        quiet = bool(h['legal'] and h.get('executed') and not h['material_changed'])
        unchanged += quiet
        streak = streak+1 if quiet else 0
        maximum = max(streak, maximum)
    fields = {
        'goal_executed': float(row['goal_executed']),
        'request_given': float(row['request_given']),
        'first_action_goal': float(bool(history) and history[0]['goal_executed_after']),
        'neither_event': float(not row['goal_executed'] and not row['request_given']),
        'no_material_change_fraction': unchanged/max(1, len(history)),
        'max_no_material_change_streak': float(maximum),
        'steps': float(len(history)), 'protocol_error': float(bool(row['protocol_error'])),
        'plan_feasible_no_actual_goal': plan['replay_goal_but_no_actual_goal'],
        'plan_feasible_goal': plan['replay_goal_executed'],
        'plan_lists_goal': plan['planned_original_goal'],
        'emote_fraction': sum(h['command'].startswith('emote ') for h in history)/max(1, len(history)),
        'examine_fraction': sum(h['command'].startswith('examine ') for h in history)/max(1, len(history)),
        'speech_fraction': sum(h['command'].split(' ')[0] in ['say','tell','whisper'] for h in history)/max(1, len(history)),
    }
    return fields, replay


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--reference', type=Path, required=True)
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--raw-out', type=Path, required=True)
    a = ap.parse_args()
    cases = {r['case']['case_id']: r for r in map(json.loads, a.dataset.read_text().splitlines())
             if r['case']['goal_kind'] in ['wear','wield']}
    assert len(cases) == 79
    rows = []
    manifests = []
    runtime = []
    for d in a.runs:
        assert (d/'runtime.json').exists()
        manifests.append(json.loads((d/'manifest.json').read_text()))
        runtime.append(json.loads((d/'runtime.json').read_text()))
        rows.extend(map(json.loads, (d/'episodes.jsonl').read_text().splitlines()))
    assert len(rows) == 2370
    for m in manifests:
        assert m['rules'] == RULES and m['seeds'] == [6301,6302,6303]
        for key in ['model','dataset_sha256','policy_sha256','driver_sha256']:
            assert m[key] == manifests[0][key]
    reference = [r for r in map(json.loads,(a.reference/'episodes.jsonl').read_text().splitlines())
                 if r['case_id'] in cases and r['mode'] == 'goal_item']
    assert len(reference) == 1422
    all_rows = rows + reference
    lookup = {(r['case_id'], r['seed'], r['persona'], r['rule']): r for r in all_rows}
    rules = list(RULES) + ['none','generic_priority','asset_protection']
    expected = {(cid,s,p,r) for cid in cases for s in [6301,6302,6303]
                for p in ['firm','agreeable'] for r in rules}
    assert len(lookup) == len(all_rows) and set(lookup) == expected
    modules = load_event_modules(CACHE/'sources/LIGHT')
    data = {}
    a.raw_out.mkdir(parents=True, exist_ok=False)
    with (a.raw_out/'plan_replays.jsonl').open('w') as f:
        for key, row in lookup.items():
            values, replay = metrics(row,cases[row['case_id']],modules)
            data[key] = values
            f.write(json.dumps({'key':key, 'values':values, 'replay':replay})+'\n')
    cells, contrasts = {}, {}
    planned = [('negative_with_use','negative_only'), ('asset_with_use','asset_protection'),
               ('negative_only','retention_only'), ('temporal_permission','negative_only')]
    for kind in ['all','wear','wield']:
        ids = sorted(cid for cid,r in cases.items() if kind=='all' or r['case']['goal_kind']==kind)
        def aggregate(persona, rule, other=None):
            return {field: estimate([np.mean([
                data[cid,s,persona,rule][field] - (data[cid,s,persona,other][field] if other else 0)
                for s in [6301,6302,6303]]) for cid in ids]) for field in next(iter(data.values()))}
        for persona in ['firm','agreeable']:
            for rule in rules:
                cells[f'{kind}/{persona}/{rule}'] = aggregate(persona,rule)
            for left,right in planned:
                contrasts[f'{kind}/{persona}/{left}-minus-{right}'] = aggregate(persona,left,right)
    calls = Counter()
    for d in a.runs:
        for line in (d/'model_calls.jsonl').open():
            r = json.loads(line)
            calls.update({'count':1,'parse_errors':int(bool(r['parse_error'])),
                          'prompt_tokens':r['prompt_tokens'],'completion_tokens':r['completion_tokens']})
    assert calls['count'] == sum(r['calls'] for r in runtime)
    report = {'status':'COMPLETE','worlds':79,'new_episodes':len(rows),'reference_episodes':len(reference),
        'new_rules':RULES,'cells':cells,'planned_contrasts':contrasts,'calls':dict(calls),
        'runtimes':runtime,'gpu_hours':sum(r['wall_seconds']+r['model_load_seconds'] for r in runtime)/3600,
        'protocol_errors':sum(bool(r['protocol_error']) for r in rows),
        'native_illegal_steps':sum(not h['legal'] for r in rows for h in r['history']),
        'native_stochastic_failures':sum(bool(h.get('stochastic_failure')) for r in rows for h in r['history']),
        'source_sha256':{str(d/'episodes.jsonl'):hashlib.sha256((d/'episodes.jsonl').read_bytes()).hexdigest()
                         for d in [*a.runs,a.reference]},
        'world_order':sorted(cases), 'scope':[
            'Full previously observed wear/wield stratum, not independent confirmatory data.',
            'Three seeds averaged within graph before graph bootstrap.',
            'Nonmaterial actions can be useful communication; no automatic safety/inaction label.',
            'B/C agree about goal use and giving, not every possible environmental action.',
            'Historical reference and new variants may differ in batching/runtime hardware.',
            'Permission interventions change semantic salience; not a pure syntax-length experiment.']}
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','worlds','new_episodes','calls','gpu_hours']}),flush=True)


if __name__=='__main__':main()
