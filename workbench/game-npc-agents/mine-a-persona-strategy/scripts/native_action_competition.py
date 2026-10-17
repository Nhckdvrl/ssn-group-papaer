#!/usr/bin/env python3
"""E66: raw logits and fixed native-command trie probabilities, no activation edits.

The trie defines a canonical tokenization of the original command menu. Its
probabilities are a constrained readout, not the original JSON sampler's exact
probabilities (JSON admits alternative whitespace/tokenizations).
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import time

import native_dependency_roles as policy
from native_constraint_scope import USE_PERMISSION


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(dataset, source_dirs):
    cases = {r['case']['case_id']: r['case'] for r in
             map(json.loads, dataset.read_text().splitlines())
             if r['case']['goal_kind'] in ['wear', 'wield']}
    assert len(cases) == 79
    selected = {}
    for directory in source_dirs:
        for line in (directory / 'model_calls.jsonl').open():
            r = json.loads(line)
            if (r['case_id'] not in cases or r['stage'] != 'exec' or r['step'] != 0
                    or r['request_mode'] != 'goal_item'):
                continue
            if r['seed'] != 6301 + int(r['case_id'][:7], 16)*10 + 10:
                continue
            key = (r['case_id'], r['persona'], r['rule'])
            assert key not in selected
            selected[key] = r
    assert len(selected) == 79*2*3
    jobs = []
    for (cid, persona, source_rule), row in sorted(selected.items()):
        changes = [('natural', source_rule)]
        if source_rule == 'asset_protection':
            changes += [('fixed_asset_context', x) for x in
                        ['none', 'generic_priority', 'asset_with_use']]
        for context, rule in changes:
            messages = copy.deepcopy(row['messages'])
            if context == 'fixed_asset_context':
                old = '\nDecision rule: ' + policy.RULES['asset_protection']
                assert messages[0]['content'].count(old) == 1
                text = (policy.RULES['asset_protection'] + ' ' + USE_PERMISSION
                        if rule == 'asset_with_use' else policy.RULES[rule])
                messages[0]['content'] = messages[0]['content'].replace(
                    old, '\nDecision rule: ' + text if text else '')
            jobs.append({'case_id': cid, 'persona': persona, 'context': context,
                'source_rule': source_rule, 'rule': rule, 'messages': messages,
                'schema': row['schema'], 'original_messages': row['messages'],
                'source_prompt_sha256': row['prompt_sha256'],
                'source_response': row['response'], 'goal_kind': cases[cid]['goal_kind'],
                'goal_command': cases[cid]['goal_command'],
                'source_action': (row['parsed'] or {}).get('action')})
    assert len(jobs) == 948
    return jobs


def rendered(tokenizer, messages, schema):
    messages = copy.deepcopy(messages)
    messages[0]['content'] += '\nReturn only JSON matching this schema: ' + json.dumps(schema)
    return tokenizer.apply_chat_template(messages, tokenize=False,
                                        add_generation_prompt=True, enable_thinking=False)


def command_tree(tokenizer, commands):
    # The opening quote is already in the shared prefix. Otherwise Qwen merges
    # quote+some verbs, making the first branch mostly a formatting competition.
    paths = [tokenizer.encode(json.dumps(c, ensure_ascii=False)[1:], add_special_tokens=False)
             for c in commands]
    common = []
    for xs in zip(*paths):
        if len(set(xs)) != 1:
            break
        common.append(xs[0])
    tree = {}
    for command, path in zip(commands, paths):
        node = tree
        for token in path[len(common):]:
            node = node.setdefault(token, {})
        node[None] = command
    assert None not in tree and len(tree) > 1
    return common, paths, tree


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--sources', nargs='+', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--batch-size', type=int, default=4)
    args = ap.parse_args()
    jobs = prepare(args.dataset, args.sources)
    args.out.mkdir(parents=True, exist_ok=False)
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForImageTextToText
    torch.set_num_threads(1)
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    tokenizer.padding_side = 'left'
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    prepared = []
    for job in jobs:
        original = rendered(tokenizer, job['original_messages'], job['schema'])
        assert hashlib.sha256(original.encode()).hexdigest() == job['source_prompt_sha256']
        prompt = rendered(tokenizer, job['messages'], job['schema'])
        commands = list(dict.fromkeys(job['schema']['properties']['action']['enum']))
        common, paths, tree = command_tree(tokenizer, commands)
        prefix = tokenizer.encode(prompt + '{"action": "', add_special_tokens=False) + common
        assert job['goal_command'] in commands, job['goal_command']
        target_examine = 'examine ' + job['goal_command'].split(' ', 1)[1]
        targets = {'goal': job['goal_command'], 'frown': 'emote frown',
                   'examine_goal_item': target_examine, 'observed_action': job['source_action']}
        target_paths = {k: paths[commands.index(v)][len(common):]
                        if v in commands else None for k, v in targets.items()}
        prepared.append({**job, 'commands': commands, 'common_tokens': common,
            'prefix_ids': prefix, 'tree': tree, 'target_commands': targets,
            'target_paths': target_paths,
            'readout_prefix_sha256': hashlib.sha256(json.dumps(prefix).encode()).hexdigest()})
    (args.out / 'manifest.json').write_text(json.dumps({
        'experiment': 'E66', 'model': str(args.model), 'contexts': len(prepared),
        'worlds': 79, 'seed': 6301, 'batch_size': args.batch_size,
        'dataset_sha256': digest(args.dataset), 'driver_sha256': digest(__file__),
        'sources': {str(p): digest(p/'model_calls.jsonl') for p in args.sources},
        'temperature': .7, 'action_prefix': '{"action": "',
        'canonical_tokenization': True, 'original_sampler_exact_probability': False,
        'raw_vocab_and_legal_branch_entropy_separate': True,
        'native_actions_regenerated': 0, 'cloud_calls': 0,
        'scope': 'All wear/wield first decisions; previously observed explanatory cohort.',
    }, indent=2) + '\n')
    with (args.out / 'contexts.jsonl').open('w') as f:
        for r in prepared:
            f.write(json.dumps({k: v for k, v in r.items() if k not in
                               ['tree', 'original_messages']}, ensure_ascii=False) + '\n')
    config = json.loads((args.model/'config.json').read_text())
    loader = AutoModelForImageTextToText if config['model_type'] == 'gemma3' else AutoModelForCausalLM
    started = time.monotonic()
    model = loader.from_pretrained(args.model, dtype=torch.bfloat16,
        device_map={'': 'cuda:0'}, local_files_only=True, attn_implementation='sdpa').eval()
    load_seconds = time.monotonic()-started
    started = time.monotonic()
    rows_done = 0
    forward_calls = 0
    max_sham_difference = 0.
    cache_vs_teacher_forcing = None
    with torch.inference_mode(), (args.out/'readouts.jsonl').open('a') as out:
        for offset in range(0, len(prepared), args.batch_size):
            group = prepared[offset:offset+args.batch_size]
            length = max(len(r['prefix_ids']) for r in group)
            tokens = torch.tensor([[tokenizer.pad_token_id]*(length-len(r['prefix_ids']))+
                                   r['prefix_ids'] for r in group], device='cuda')
            mask = torch.tensor([[0]*(length-len(r['prefix_ids']))+[1]*len(r['prefix_ids'])
                                 for r in group], device='cuda')
            position_ids = mask.cumsum(-1)-1
            position_ids.masked_fill_(mask == 0, 0)
            result = model(input_ids=tokens, attention_mask=mask, position_ids=position_ids,
                           use_cache=True, logits_to_keep=1)
            forward_calls += 1
            roots = result.logits[:, -1].float()
            cache = result.past_key_values
            root_values = []
            for i, r in enumerate(group):
                logp = roots[i].log_softmax(-1)
                ids = list(r['tree'])
                branch = torch.softmax(roots[i, ids]/.7, -1)
                top = roots[i].topk(10)
                raw_entropy = -(logp.exp()*logp).sum()
                legal_entropy = -(branch*branch.clamp_min(1e-30).log()).sum()
                branch_rows = [{'token_id': t, 'token': tokenizer.decode([t]),
                    'raw_logit': float(roots[i, t]), 'raw_probability': float(logp[t].exp()),
                    'legal_start_probability': float(branch[j])} for j,t in enumerate(ids)]
                root_values.append({'raw_vocabulary_entropy_nats': float(raw_entropy),
                    'legal_start_entropy_nats': float(legal_entropy),
                    'legal_start_entropy_normalized': float(legal_entropy/math.log(len(ids))),
                    'legal_start_branch_count': len(ids),
                    'legal_start_raw_probability_mass': float(logp[ids].exp().sum()),
                    'top10': [{'token_id': int(t), 'token': tokenizer.decode([int(t)]),
                        'raw_logit': float(v), 'raw_probability': float(logp[t].exp())}
                        for t,v in zip(top.indices, top.values)],
                    'legal_start_branches': branch_rows})
            target_scores = [{} for _ in group]
            for target in ['goal', 'frown', 'examine_goal_item', 'observed_action']:
                logits = roots
                branch_cache = copy.deepcopy(cache)
                branch_mask = mask.clone()
                nodes = [r['tree'] for r in group]
                totals = [0. for _ in group]
                completed = [r['target_paths'][target] is None for r in group]
                for depth in range(max(len(r['target_paths'][target] or []) for r in group)):
                    next_tokens = []
                    for i, r in enumerate(group):
                        if completed[i]:
                            next_tokens.append(tokenizer.pad_token_id)
                            continue
                        path = r['target_paths'][target]
                        allowed = [k for k in nodes[i] if k is not None]
                        token = path[depth]
                        assert token in allowed
                        totals[i] += float(torch.log_softmax(logits[i, allowed]/.7, -1)[allowed.index(token)])
                        nodes[i] = nodes[i][token]
                        next_tokens.append(token)
                        completed[i] = None in nodes[i]
                    if all(completed):
                        break
                    branch_mask = torch.cat([branch_mask, torch.ones((len(group), 1),
                                            device='cuda', dtype=branch_mask.dtype)], dim=1)
                    positions = branch_mask.sum(-1, keepdim=True)-1
                    forward = model(input_ids=torch.tensor(next_tokens, device='cuda')[:,None],
                        attention_mask=branch_mask, position_ids=positions,
                        past_key_values=branch_cache, use_cache=True, logits_to_keep=1)
                    logits = forward.logits[:, -1].float()
                    branch_cache = forward.past_key_values
                    forward_calls += 1
                for i, r in enumerate(group):
                    target_scores[i][target] = (None if r['target_paths'][target] is None else
                        {'command': r['target_commands'][target], 'trie_log_probability': totals[i],
                         'trie_probability': math.exp(totals[i])})
                del branch_cache
            if offset == 0:
                check = model(input_ids=tokens, attention_mask=mask, position_ids=position_ids,
                              use_cache=False, logits_to_keep=1).logits[:, -1].float()
                forward_calls += 1
                max_sham_difference = float((check-roots).abs().max())
                # Independently score one full goal sequence without a KV branch.
                # This verifies indexing/branch-cache handling, not a new condition.
                r = group[0]
                path = r['target_paths']['goal']
                check_ids = torch.tensor([r['prefix_ids']+path[:-1]], device='cuda')
                check_logits = model(input_ids=check_ids, attention_mask=torch.ones_like(check_ids),
                    use_cache=False, logits_to_keep=len(path)).logits[0].float()
                forward_calls += 1
                node = r['tree']
                total = 0.
                for depth, token in enumerate(path):
                    allowed = [k for k in node if k is not None]
                    total += float(torch.log_softmax(check_logits[depth, allowed]/.7, -1)[allowed.index(token)])
                    node = node[token]
                cache_vs_teacher_forcing = {
                    'case_id': r['case_id'], 'cached_log_probability': target_scores[0]['goal']['trie_log_probability'],
                    'teacher_forced_log_probability': total,
                    'probability_difference': math.exp(total)-target_scores[0]['goal']['trie_probability'],
                    'note': 'Single unpadded full forward versus batched cached decode; bf16 differences retained.'}
            for r, root, scores in zip(group, root_values, target_scores):
                entry = {k:r[k] for k in ['case_id', 'persona', 'context', 'source_rule', 'rule',
                    'goal_kind', 'source_action', 'source_prompt_sha256', 'readout_prefix_sha256']}
                entry.update(root)
                entry['command_probabilities'] = scores
                out.write(json.dumps(entry, ensure_ascii=False)+'\n')
                rows_done += 1
            out.flush()
            del result, cache, roots, logits
            if rows_done % 40 == 0 or rows_done == len(prepared):
                print(json.dumps({'contexts': rows_done, 'seconds': time.monotonic()-started}), flush=True)
    runtime = {'contexts': rows_done, 'forward_calls': forward_calls,
        'model_load_seconds': load_seconds, 'wall_seconds': time.monotonic()-started,
        'sham_max_abs_logit_difference': max_sham_difference,
        'cache_vs_teacher_forcing': cache_vs_teacher_forcing,
        'native_actions_regenerated': 0, 'cloud_calls': 0}
    (args.out/'runtime.json').write_text(json.dumps(runtime, indent=2)+'\n')
    print(json.dumps(runtime), flush=True)


if __name__ == '__main__':
    main()
