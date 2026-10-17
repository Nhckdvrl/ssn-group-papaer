#!/usr/bin/env python3
"""E66 within-world action probability contrasts, retaining raw token diagnostics."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    runtime = json.loads((a.run/'runtime.json').read_text())
    manifest = json.loads((a.run/'manifest.json').read_text())
    rows = list(map(json.loads, (a.run/'readouts.jsonl').read_text().splitlines()))
    assert len(rows) == runtime['contexts'] == 948
    contexts = {(r['case_id'],r['persona'],r['context'],r['rule']):r
                for r in map(json.loads,(a.run/'contexts.jsonl').read_text().splitlines())}
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(manifest['model'], local_files_only=True)
    lookup = {(r['case_id'],r['persona'],r['context'],r['rule']):r for r in rows}
    assert len(lookup) == len(rows) and set(lookup) == set(contexts)
    ids = sorted({r['case_id'] for r in rows})
    assert len(ids) == 79
    all_verbs = sorted({command.split(' ')[0] for r in contexts.values() for command in r['commands']})
    values = {}
    for key,row in lookup.items():
        scores = row['command_probabilities']
        branches = {r['token_id']:r for r in row['legal_start_branches']}
        assert abs(sum(r['legal_start_probability'] for r in branches.values())-1) < 1e-5
        root = contexts[key]
        branch_verbs = {}
        for command in root['commands']:
            path = tokenizer.encode(json.dumps(command, ensure_ascii=False)[1:], add_special_tokens=False)
            first = path[len(root['common_tokens'])]
            branch_verbs.setdefault(first, set()).add(command.split(' ')[0])
        assert set(branch_verbs) == set(branches)
        data = {f:row[f] for f in ['raw_vocabulary_entropy_nats', 'legal_start_entropy_nats',
                                  'legal_start_entropy_normalized','legal_start_raw_probability_mass']}
        # Assign mass only when every command beneath the branch has this verb.
        # Mixed-token branches are reported, not arbitrarily assigned to actions.
        for verb in ['emote','examine']:
            ambiguous = any(verb in vs and vs != {verb} for vs in branch_verbs.values())
            data[verb+'_family_start_probability'] = (np.nan if ambiguous else sum(
                branches[t]['legal_start_probability'] for t,vs in branch_verbs.items() if vs == {verb}))
        for verb in all_verbs:
            ambiguous = any(verb in vs and vs != {verb} for vs in branch_verbs.values())
            data['family_'+verb+'_start_probability'] = (np.nan if ambiguous else sum(
                branches[t]['legal_start_probability'] for t,vs in branch_verbs.items() if vs == {verb}))
        data['mixed_verb_start_probability'] = sum(branches[t]['legal_start_probability']
                                                  for t,vs in branch_verbs.items() if len(vs)>1)
        for name in ['goal','frown','examine_goal_item']:
            data[name+'_probability'] = scores[name]['trie_probability'] if scores[name] else np.nan
            path = root['target_paths'][name]
            data[name+'_start_branch_probability'] = branches[path[0]]['legal_start_probability'] if path else np.nan
        data['goal_frown_log_odds'] = scores['goal']['trie_log_probability'] - scores['frown']['trie_log_probability']
        data['goal_minus_frown_probability'] = data['goal_probability']-data['frown_probability']
        data['source_chose_goal'] = float(row['source_action'] == root['goal_command'])
        values[key] = data
    conditions = [('natural',r) for r in ['none','generic_priority','asset_protection']]
    conditions += [('fixed_asset_context',r) for r in ['none','generic_priority','asset_with_use']]
    contrasts = [(("natural","asset_protection"),("natural",r)) for r in ['none','generic_priority']]
    contrasts += [(('fixed_asset_context',r),('natural','asset_protection'))
                  for r in ['none','generic_priority','asset_with_use']]
    cells, differences = {}, {}
    missing = {}
    for persona in ['firm','agreeable','pooled']:
        ps = ['firm','agreeable'] if persona == 'pooled' else [persona]
        def aggregate(left, right=None):
            result = {}
            for field in next(iter(values.values())):
                points = []
                for cid in ids:
                    vals = [values[(cid,p,*left)][field] - (values[(cid,p,*right)][field] if right else 0)
                            for p in ps]
                    if all(np.isfinite(v) for v in vals):points.append(np.mean(vals))
                result[field] = estimate(points)
                if len(points) != 79:
                    missing[f'{persona}/{left}/{right}/{field}'] = 79-len(points)
            return result
        for context,rule in conditions:
            cells[f'{persona}/{context}/{rule}'] = aggregate((context,rule))
        for left,right in contrasts:
            differences[f'{persona}/{left[0]}/{left[1]}-minus-{right[0]}/{right[1]}'] = aggregate(left,right)
    examples = [r for r in rows if r['case_id'] in ids[:2]]
    report = {'status':'COMPLETE','worlds':79,'contexts':948,'manifest':manifest,'runtime':runtime,
        'gpu_hours':(runtime['wall_seconds']+runtime['model_load_seconds'])/3600,
        'cells':cells,'planned_contrasts':differences,'missing_targets':missing,
        'top10_examples_selection':'First two sorted source case IDs, all conditions and personas.',
        'top10_examples':examples,
        'readouts_sha256':hashlib.sha256((a.run/'readouts.jsonl').read_bytes()).hexdigest(),
        'scope':[
            'One prespecified seed; 79 previously observed worlds; two personas averaged within world when pooled.',
            'Natural pathways differ in plans/conversations; fixed-asset contexts hold those constant.',
            'First-token entropy is not full action entropy; raw vocabulary entropy is a separate quantity.',
            'Canonical native-menu trie probabilities are not exact probabilities of the original JSON sampler.',
            'Output probabilities localize a decision preference, not a neural circuit or training cause.',
            'Raw logits are not comparable in scale between model families.',
        ]}
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','worlds','contexts','gpu_hours','missing_targets']}),flush=True)


if __name__=='__main__':main()
