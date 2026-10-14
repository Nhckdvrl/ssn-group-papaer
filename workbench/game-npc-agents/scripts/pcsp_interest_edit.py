"""E33: source-defined single-attribute utility, fixed body, native execution."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import time


BASE_IDS = [401, 421, 441, 461, 481]
PEER_IDS = [402, 409, 416, 422, 429, 436, 442, 449, 456, 462, 469, 476, 482, 489, 496]
WORLD_SEEDS = [33011, 33012, 33013]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['gate', 'encode', 'run'], required=True)
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--model', type=Path)
    ap.add_argument('--codes', type=Path, default=Path('/tmp/npc_e33_codes'))
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--condition', choices=['plain', 'clarified'], default='plain')
    ap.add_argument('--policy-prefix', type=Path)
    ap.add_argument('--training-seed', type=int, default=42)
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.source / 'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv, N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE, N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic
    torch.set_num_threads(1)
    start = time.monotonic()
    dump = lambda name, obj: (args.out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    rows = json.loads((args.source / 'research/data/personas/test_100_v3.json').read_text())
    lookup = {int(r['id']): r for r in rows}
    syntax = ast.parse((args.source / 'research/scripts/generate_personas_500.py').read_text())
    descriptions = next(ast.literal_eval(n.value) for n in syntax.body if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == '_BF_DESC' for t in n.targets))
    def text(row):
        return f"{row['age']}세 {row['occupation']}. " + ', '.join(descriptions[f'{k}_{v}'] for k, v in row['big_five'].items()) + '.'
    assert all(text(lookup[i]) == lookup[i]['text'] for i in BASE_IDS)
    def changed(pid, level):
        row = copy.deepcopy(lookup[pid])
        row['big_five']['C'] = level
        row['text'] = text(row)
        assert all(row[k] == lookup[pid][k] for k in ['decay_modifiers', 'preferred_actions', 'age', 'occupation'])
        assert all(row['big_five'][k] == lookup[pid]['big_five'][k] for k in ['E', 'N', 'A', 'O'])
        return row
    def environments(pid, seed, cycles):
        envs = [MiniInzoiV3LargeEnv(personas=[PersonaConfig.from_dict(changed(pid, level))]
                 + [PersonaConfig.from_dict(lookup[i]) for i in PEER_IDS], max_steps=cycles)
                for level in ['high', 'low']]
        for env in envs:
            env.reset(seed=seed)
        return envs
    def parity(envs):
        a, b = envs
        for key in ['positions', 'needs', 'last_actions', 'repeat_counts', 'novelty_steps']:
            assert np.array_equal(getattr(a, key), getattr(b, key)), key
        assert a.agent_selection == b.agent_selection and a.step_count == b.step_count
        assert np.array_equal(a.observe(a.possible_agents[0]), b.observe(b.possible_agents[0]))
    def contrast(envs):
        a, b = envs
        result = np.asarray([a._style_reward(0, action) - b._style_reward(0, action)
                             for action in range(N_ACTIONS_V3)], dtype=np.float64)
        for action in [6, 7, 14]:
            result[action] += a._social_bonus(0) - b._social_bonus(0)
        return result
    dump('manifest.json', {'source_sha': '5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
         'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'base_ids': BASE_IDS, 'peer_ids': PEER_IDS, 'world_seeds': WORLD_SEEDS,
         'body_fixed': True, 'reward_function_changed': False, 'cloud_calls': 0,
         'mode': args.mode, 'condition': args.condition, 'limit': args.limit,
         'policy_prefix': str(args.policy_prefix), 'training_seed': args.training_seed})
    if args.mode == 'gate':
        output = []
        for pid in BASE_IDS:
            envs = environments(pid, WORLD_SEEDS[0], 20)
            tape = np.random.default_rng(33000 + pid).integers(N_ACTIONS_V3, size=(20, N_AGENTS))
            max_error = 0.; total = np.zeros(2); spans = []
            for cycle in range(20):
                parity(envs)
                delta = contrast(envs); spans.append(float(np.ptp(delta)))
                for index, action in enumerate(tape[cycle]):
                    rewards = []
                    for env in envs:
                        agent = env.agent_selection; env.step(int(action)); rewards.append(env.rewards[agent])
                    if index == 0:
                        max_error = max(max_error, abs(rewards[0] - rewards[1] - delta[action]))
                        total += rewards
                parity(envs)
            assert max_error < 1e-6 and min(spans) > 1e-4
            output.append({'id': pid, 'source_reward_contrast_max_error': max_error,
                           'physical_byte_parity': True, 'oracle_contrast_span_min': min(spans),
                           'fixed_tape_returns': total.tolist()})
        dump('summary.json', {'controls': output, 'passed': True, 'wall_seconds': time.monotonic() - start})
        print(json.dumps(output), flush=True)
        return
    if args.mode == 'encode':
        assert args.model is not None
        from transformers import AutoModel, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
        names = []; texts = []; metadata = []
        for pid in BASE_IDS:
            names.append(f'canonical_{pid}'); texts.append(lookup[pid]['text']); metadata.append(lookup[pid])
            for level in ['high', 'low']:
                row = changed(pid, level)
                for condition in ['plain', 'clarified']:
                    names.append(f'{condition}_{pid}_{level}')
                    suffix = f" In this game, the character's Conscientiousness (C) is {level}." if condition == 'clarified' else ''
                    texts.append(row['text'] + suffix); metadata.append(row)
        lengths = [len(tok(t)['input_ids']) for t in texts]
        assert max(lengths) <= 256
        dump('texts.json', {'names': names, 'texts': texts, 'personas': metadata, 'token_lengths': lengths})
        model = AutoModel.from_pretrained(args.model, local_files_only=True, dtype=torch.float16).to('cuda').eval().requires_grad_(False)
        tokens = tok(texts, padding=True, truncation=False, return_tensors='pt').to('cuda')
        with torch.inference_mode():
            hidden = model(**tokens).last_hidden_state
            indices = tokens['attention_mask'].sum(-1) - 1
            assert tok.padding_side == 'right'
            e = torch.nn.functional.normalize(hidden[torch.arange(len(texts), device='cuda'), indices], dim=-1).float().cpu().numpy()
        np.save(args.out / 'vectors.npy', e)
        old = np.load(args.runs / 'e26_semantic_codes/canonical.npy')
        comparisons = {pid: float(np.dot(e[names.index(f'canonical_{pid}')], old[pid - 1]) /
                                  (np.linalg.norm(e[names.index(f'canonical_{pid}')]) * np.linalg.norm(old[pid - 1])))
                       for pid in BASE_IDS}
        assert min(comparisons.values()) >= .9999
        dump('summary.json', {'canonical_cosines': comparisons, 'passed': True, 'model_revision': args.model.name,
                              'pooling': 'last real attention-mask token', 'dtype': 'float16',
                              'wall_seconds': time.monotonic() - start, 'cloud_calls': 0})
        print(json.dumps(comparisons), flush=True)
        return
    assert json.loads((args.codes / 'summary.json').read_text())['passed']
    names = json.loads((args.codes / 'texts.json').read_text())['names']
    encoded = np.load(args.codes / 'vectors.npy')
    canonical = np.load(args.runs / 'e26_semantic_codes/canonical.npy').astype(np.float32)
    summaries = []; policy_hashes = {}
    for route in ['no', 'full']:
        policy = PCSPActorCritic(OBS_DIM_V3_LARGE, N_ACTIONS_V3)
        folder = Path(str(args.policy_prefix) + route) if args.policy_prefix is not None else args.runs / f'e25_30_{route}'
        state = torch.load(folder / 'policy.pt', map_location='cpu', weights_only=True)
        policy_hashes[route] = hashlib.sha256((folder / 'policy.pt').read_bytes()).hexdigest()
        policy.load_state_dict(state, strict=True); policy.eval().requires_grad_(False)
        for pid in BASE_IDS:
            vectors = {level: encoded[names.index(f'{args.condition}_{pid}_{level}')] for level in ['high', 'low']}
            with torch.inference_mode():
                phis = {k: policy.persona_proj(torch.from_numpy(v).unsqueeze(0)) for k, v in vectors.items()}
                phi_cos = float(torch.nn.functional.cosine_similarity(phis['high'], phis['low']))
            for seed in WORLD_SEEDS:
                for level in ['high', 'low']:
                    envs = environments(pid, seed, 200)
                    inputs = torch.from_numpy(np.stack([vectors[level]] + [canonical[i - 1] for i in PEER_IDS]))
                    uniforms = np.random.default_rng(seed + 1000003).random((200, N_AGENTS))
                    rewards = np.zeros((2, 200)); actions = np.empty((200, N_AGENTS), dtype=np.int16)
                    obs_trace = []; need_trace = []; position_trace = []; local_orientation = []
                    episode_start = time.monotonic()
                    for cycle in range(200):
                        parity(envs)
                        delta = contrast(envs)
                        for index, agent in enumerate(envs[0].possible_agents):
                            assert envs[0].agent_selection == agent
                            obs = torch.from_numpy(envs[0].observe(agent)).unsqueeze(0)
                            with torch.inference_mode():
                                logits = policy.action_logits(obs, inputs[index].unsqueeze(0))
                                if cycle == 0 and index == 0:
                                    assert torch.equal(logits, policy.action_logits(obs, inputs[index].unsqueeze(0)))
                                probs = logits.softmax(-1).numpy()[0]
                                if index == 0:
                                    q = [policy.action_logits(obs, torch.from_numpy(vectors[k]).unsqueeze(0)).softmax(-1).numpy()[0]
                                         for k in ['high', 'low']]
                                    local_orientation.append(float(np.dot(q[0] - q[1], delta)))
                            action = min(int(np.searchsorted(np.cumsum(probs), uniforms[cycle, index], side='right')), N_ACTIONS_V3 - 1)
                            actions[cycle, index] = action
                            if index == 0:
                                obs_trace.append(obs.numpy()[0].copy())
                            immediate = []
                            for env in envs:
                                env.step(action); immediate.append(float(env.rewards[agent]))
                            if index == 0:
                                rewards[:, cycle] = immediate
                                assert abs(immediate[0] - immediate[1] - delta[action]) < 1e-6
                        parity(envs)
                        need_trace.append(envs[0].needs.copy()); position_trace.append(envs[0].positions.copy())
                    path = args.out / f'{route}_{pid}_{level}_s{seed}.npz'
                    np.savez_compressed(path, rewards=rewards, actions=actions, obs=np.asarray(obs_trace),
                                        needs=np.asarray(need_trace), positions=np.asarray(position_trace),
                                        local_orientation=np.asarray(local_orientation))
                    summaries.append({'route': route, 'id': pid, 'seed': seed, 'input_C': level,
                         'J_high': float(rewards[0].sum()), 'J_low': float(rewards[1].sum()),
                         'local_orientation': float(np.mean(local_orientation)), 'phi_cosine_high_low': phi_cos,
                         'raw_cosine_high_low': float(np.dot(vectors['high'], vectors['low']) /
                                                     (np.linalg.norm(vectors['high']) * np.linalg.norm(vectors['low']))),
                         'physical_parity': True, 'wall_seconds': time.monotonic() - episode_start})
                    dump('episodes.json', summaries)
                    if len(summaries) == 1:
                        print(json.dumps({'cost_gate': summaries[0]}), flush=True)
                        assert summaries[0]['wall_seconds'] <= 120
                    if args.limit is not None and len(summaries) >= args.limit:
                        dump('summary.json', {'limited_cost_gate': True, 'episodes': summaries, 'wall_seconds': time.monotonic() - start})
                        return
        print(json.dumps({'route': route, 'episodes': len(summaries), 'wall_seconds': time.monotonic() - start}), flush=True)
    outcomes = []
    for route in ['no', 'full']:
        for pid in BASE_IDS:
            effects = []
            for seed in WORLD_SEEDS:
                high = next(x for x in summaries if (x['route'], x['id'], x['seed'], x['input_C']) == (route, pid, seed, 'high'))
                low = next(x for x in summaries if (x['route'], x['id'], x['seed'], x['input_C']) == (route, pid, seed, 'low'))
                effects.append((high['J_high'] - low['J_high']) - (high['J_low'] - low['J_low']))
            outcomes.append({'route': route, 'id': pid, 'world_effects': effects, 'mean_effect': float(np.mean(effects))})
    result = {'condition': args.condition, 'per_base': outcomes,
              'routes': {route: {'mean_effect': float(np.mean([x['mean_effect'] for x in outcomes if x['route'] == route])),
                                'positive_base_count': sum(x['mean_effect'] > 0 for x in outcomes if x['route'] == route)}
                         for route in ['no', 'full']},
              'wall_seconds': time.monotonic() - start, 'training_seeds': 1, 'episodes': len(summaries),
              'training_seed': args.training_seed, 'policy_hashes': policy_hashes,
              'reward_function_changed': False, 'cloud_calls': 0, 'raw': str(args.out)}
    result['clarification_required_by_card'] = any(x['mean_effect'] <= 0 or x['positive_base_count'] < 4 for x in result['routes'].values())
    dump('summary.json', result); print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
