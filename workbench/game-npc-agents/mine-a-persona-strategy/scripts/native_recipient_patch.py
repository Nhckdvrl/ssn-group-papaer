#!/usr/bin/env python3
"""E62: native Give recipient choices, matched-role residual interventions."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import time

import commitment_decisions_v2 as base
from common_history_direct import direct_spec
from commitment_snapshots import outcome
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, execute, legal_commands


def prepare(case, modules):
    graph = modules[0].from_json(case['quest']['graph'])
    actor = graph.get_node(case['actor_id'])
    goal = parse_event(graph, actor, case['goal_command'], *modules[1:])
    request = parse_event(graph, actor, case['request_command'], *modules[1:])
    assert type(goal).__name__ == type(request).__name__ == 'GiveObjectEvent'
    assert goal.target_nodes[0].node_id == request.target_nodes[0].node_id == case['item_id']
    assert goal.target_nodes[1].node_id != request.target_nodes[1].node_id
    commands = []
    for command in legal_commands(graph, actor):
        event = parse_event(graph, actor, command, *modules[1:])
        if type(event).__name__ == 'GiveObjectEvent' and event.target_nodes[0].node_id == case['item_id']:
            commands.append(command)
    assert len(commands) >= 2
    canonical = {parse_event(graph, actor, c, *modules[1:]).to_canonical_form(): c for c in commands}
    assert goal.to_canonical_form() in canonical and request.to_canonical_form() in canonical
    return {'case_id': case['case_id'], 'commands': commands,
            'own_command': canonical[goal.to_canonical_form()],
            'request_command': canonical[request.to_canonical_form()],
            'own_recipient': goal.target_nodes[1].name,
            'requester': request.target_nodes[1].name,
            'item': goal.target_nodes[0].name}


def make_spec(case, persona, context, prepared, modules):
    graph = modules[0].from_json(case['quest']['graph'])
    speech = 'I will hand ' + prepared['item'] + ' to ' + prepared['requester'] + ' next.'
    if context == 'no_history':
        messages, _ = base.exec_spec(case, persona, {}, '00', graph, [], modules)
    else:
        messages, _ = direct_spec(case, persona, speech, graph, [], modules)
    if context == 'future_binding':
        messages[-1]['content'] += ('\nBinding facts: your original authored recipient is '
            + prepared['own_recipient'] + '; the requester is ' + prepared['requester']
            + '. These are distinct characters. Neither physical transfer has occurred.')
    messages[-1]['content'] += ('\nFor this diagnostic, choose the recipient for a give action involving '
        + prepared['item'] + '. Select one of the legal give commands below.\n'
        + '\n'.join(prepared['commands']))
    structure = base.schema({'action': {'type': 'string', 'enum': prepared['commands']}})
    messages[0]['content'] += '\nReturn only JSON matching this schema: ' + json.dumps(structure)
    return messages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--cpu-only', action='store_true')
    ap.add_argument('--limit', type=int, default=102)
    args = ap.parse_args()
    assert args.limit in [1, 102], 'Registered first-scene cost or complete cohort only'
    cases = list(map(json.loads, args.dataset.read_text().splitlines()))
    assert len(cases) == len({c['graph_sha256'] for c in cases}) == 200
    cases = [c for c in cases if c['goal_kind'] == 'give']
    assert len(cases) == 102
    cases = cases[:args.limit]
    modules = load_event_modules(CACHE / 'sources/LIGHT')
    prepared = {c['case_id']: prepare(c, modules) for c in cases}
    args.out.mkdir(parents=True, exist_ok=False)
    qualification = []
    for case in cases:
        for command in prepared[case['case_id']]['commands']:
            graph = modules[0].from_json(case['quest']['graph'])
            event = execute(ViewerHost(graph), graph.get_node(case['actor_id']), command, *modules[1:])
            flags = outcome(graph, case, [event])
            qualification.append({'case_id': case['case_id'], 'command': command,
                                  'legal': event['legal'], 'executed': event.get('executed'), 'flags': flags})
            if command == prepared[case['case_id']]['own_command']:
                assert flags['own_task']
            if command == prepared[case['case_id']]['request_command']:
                assert flags['request']
    (args.out / 'cpu_qualification.json').write_text(json.dumps(qualification, ensure_ascii=False, indent=2) + '\n')
    cpu = {'graphs': len(cases), 'commands': len(qualification),
           'not_executed': sum(not bool(r['executed']) for r in qualification),
           'world_modified': False, 'model_calls': 0}
    if args.cpu_only:
        (args.out / 'runtime.json').write_text(json.dumps(cpu, indent=2) + '\n')
        print(json.dumps(cpu))
        return
    assert args.model is not None
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForImageTextToText
    torch.set_num_threads(1)
    config = json.loads((args.model / 'config.json').read_text())
    loader = AutoModelForImageTextToText if config['model_type'] in ['qwen3_5', 'gemma3'] else AutoModelForCausalLM
    started = time.monotonic()
    model = loader.from_pretrained(str(args.model), dtype=torch.bfloat16, device_map={'': 'cuda:0'},
                                  attn_implementation='sdpa', local_files_only=True).eval()
    tokenizer = AutoTokenizer.from_pretrained(str(args.model), local_files_only=True)
    if config['model_type'] == 'qwen3_5':
        decoder = model.model.language_model
    elif config['model_type'] == 'gemma3':
        decoder = model.model.language_model
    else:
        decoder = model.model
    layer_index = (len(decoder.layers) - 1) // 2
    layer = decoder.layers[layer_index]
    load_seconds = time.monotonic() - started
    manifest = {'model': str(args.model), 'graphs': len(cases), 'source_cohort_graphs': 200,
        'case_ids': [c['case_id'] for c in cases], 'dataset_sha256': hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helpers_sha256': {n: hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
                          for n in ['common_history_direct.py', 'commitment_decisions_v2.py', 'commitment_snapshots.py']},
        'personas': base.PERSONAS, 'contexts': ['no_history', 'future', 'future_binding'],
        'conditions': ['baseline', 'sham', 'donor', 'random'], 'draw_seeds': [6251, 6252],
        'layer_index': layer_index, 'layer_count': len(decoder.layers),
        'prefix_intervention': 'longest shared token prefix of all native Give commands for the target object',
        'world_modified': False, 'cloud_calls': 0, 'load_seconds': load_seconds,
        'scope': 'conditional recipient diagnostic, not full policy; current roles consistent, activation swap is explicitly local'}
    (args.out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    captures = {}
    records = []
    score_count = capture_count = 0
    started = time.monotonic()
    for case in cases:
        data = prepared[case['case_id']]
        token_commands = {c: tokenizer(json.dumps(c, ensure_ascii=False), add_special_tokens=False).input_ids
                          for c in data['commands']}
        common = list(next(iter(token_commands.values())))
        for ids in token_commands.values():
            size = 0
            while size < min(len(common), len(ids)) and common[size] == ids[size]:
                size += 1
            common = common[:size]
        assert common and all(len(ids) > len(common) for ids in token_commands.values())
        trie = {}
        for command, ids in token_commands.items():
            node = trie
            for token in ids[len(common):]:
                node = node.setdefault(token, {})
            node[None] = command
        for context in manifest['contexts']:
            inputs, texts, vectors, scores = {}, {}, {}, {}
            for persona in base.PERSONAS:
                messages = make_spec(case, persona, context, data, modules)
                prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                                       enable_thinking=False) + '{"action":'
                ids = tokenizer(prompt, add_special_tokens=False).input_ids + common
                inputs[persona] = {'input_ids': torch.tensor([ids], device='cuda'),
                                   'attention_mask': torch.ones((1, len(ids)), dtype=torch.long, device='cuda')}
                texts[persona] = {'messages': messages, 'forced_command_tokens': common,
                    'prefix_length': len(ids), 'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest()}
                captured = {}
                def capture(module, args0, output):
                    h = output[0] if isinstance(output, tuple) else output
                    captured['vector'] = h[0, -1].detach().clone()
                handle = layer.register_forward_hook(capture)
                with torch.inference_mode():
                    model(**inputs[persona], use_cache=True, logits_to_keep=1)
                handle.remove()
                vectors[persona] = captured['vector']
                captures[case['case_id'], context, persona] = vectors[persona].float().cpu()
                capture_count += 1
                scores[persona] = {}
                # Full action suffixes, not the isolated first verb/recipient token.
                for name in ['own_command', 'request_command']:
                    suffix = token_commands[data[name]][len(common):]
                    whole = torch.tensor([ids + suffix], device='cuda')
                    with torch.inference_mode():
                        logits = model(input_ids=whole, attention_mask=torch.ones_like(whole), use_cache=False,
                                       logits_to_keep=len(suffix)+1).logits[0, :-1].float()
                        target = torch.tensor(suffix, device='cuda')
                        score = torch.log_softmax(logits, -1).gather(1, target[:, None]).sum().item()
                    scores[persona][name] = score
                    score_count += 1
                texts[persona]['candidate_log_likelihood'] = scores[persona]
                with (args.out / 'prompts.jsonl').open('a') as f:
                    f.write(json.dumps({'case_id': case['case_id'], 'persona': persona, 'context': context,
                        'commands': data['commands'], **texts[persona]}, ensure_ascii=False) + '\n')
            for persona in base.PERSONAS:
                target_vector = vectors[persona]
                donor_persona = 'agreeable' if persona == 'firm' else 'firm'
                source_vector = vectors[donor_persona]
                generator = torch.Generator(device='cuda').manual_seed(625100031 + int(case['case_id'][:7], 16))
                noise = torch.randn(target_vector.shape, generator=generator, device='cuda', dtype=torch.float32)
                delta = noise / noise.norm() * (source_vector.float() - target_vector.float()).norm()
                prefix_length = inputs[persona]['input_ids'].shape[1]
                position = prefix_length - 1
                def allowed(batch_index, ids):
                    node = trie
                    for token in ids[prefix_length:].tolist():
                        node = node[token]
                    return [tokenizer.eos_token_id] if None in node else list(node)
                for condition in manifest['conditions']:
                    handle = None
                    if condition != 'baseline':
                        def patch(module, args0, output):
                            h = output[0] if isinstance(output, tuple) else output
                            if h.shape[1] <= position:
                                return output
                            h = h.clone()
                            if condition == 'sham':
                                h[0, position] = target_vector
                            elif condition == 'donor':
                                h[0, position] = source_vector
                            else:
                                h[0, position] = (h[0, position].float() + delta).to(h.dtype)
                            return (h, *output[1:]) if isinstance(output, tuple) else h
                        handle = layer.register_forward_hook(patch)
                    for draw_seed in manifest['draw_seeds']:
                        seed = draw_seed + int(case['case_id'][:7], 16) * 10
                        torch.manual_seed(seed)
                        t = time.monotonic()
                        with torch.inference_mode():
                            output = model.generate(**inputs[persona], do_sample=True, temperature=.7,
                                top_p=1., top_k=0, max_new_tokens=128, use_cache=True,
                                prefix_allowed_tokens_fn=allowed, eos_token_id=tokenizer.eos_token_id,
                                pad_token_id=tokenizer.eos_token_id)
                        value = tokenizer.decode(common + output[0, prefix_length:].tolist(), skip_special_tokens=True)
                        try:
                            command = json.loads(value)
                            assert command in data['commands']
                            graph = modules[0].from_json(case['quest']['graph'])
                            random.seed(seed)
                            native = execute(ViewerHost(graph), graph.get_node(case['actor_id']), command, *modules[1:])
                            flags = outcome(graph, case, [native])
                            error = None
                        except Exception as exc:
                            command, native, flags, error = None, None, None, str(exc)
                        row = {'case_id': case['case_id'], 'graph_sha256': case['graph_sha256'],
                            'persona': persona, 'context': context, 'condition': condition,
                            'draw_seed': draw_seed, 'sampling_seed': seed, 'command': command,
                            'response': value, 'native': native, 'flags': flags, 'protocol_error': error,
                            'seconds': time.monotonic()-t}
                        records.append(row)
                        with (args.out / 'records.jsonl').open('a') as f:
                            f.write(json.dumps(row, ensure_ascii=False) + '\n')
                    if handle:
                        handle.remove()
        print(json.dumps({'graphs': len({r['case_id'] for r in records}), 'generation_calls': len(records),
                          'wall_seconds': time.monotonic()-started}), flush=True)
    torch.save(captures, args.out / 'residuals.pt')
    assert len(records) == len(cases) * 3 * 2 * 4 * 2
    runtime = {'graphs': len(cases), 'generation_calls': len(records), 'capture_calls': capture_count,
        'candidate_score_calls': score_count, 'model_load_seconds': load_seconds,
        'wall_seconds': time.monotonic()-started, 'protocol_errors': sum(bool(r['protocol_error']) for r in records),
        'cloud_calls': 0}
    (args.out / 'runtime.json').write_text(json.dumps(runtime, indent=2) + '\n')
    print(json.dumps(runtime), flush=True)


if __name__ == '__main__':
    main()
