"""E35: official PennStepper, original three NPCs, strictly local cognition."""
import argparse
import copy
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/agent-sandbox'))
    ap.add_argument('--backend', choices=['mock', 'preflight', 'local'], required=True)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=3501)
    ap.add_argument('--steps', type=int, default=1200)
    ap.add_argument('--max-calls', type=int, default=0, help='0 completes the finite native episode without an extra call cap')
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false', LLM_PROVIDER='mock')
    source_sha = subprocess.check_output(['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip()
    assert source_sha == 'd7b872e396df2ef05ff8391de53e0563ca698cf3'
    ga = args.source / 'godot-generative-agents'
    sys.path[:0] = [str(args.source), str(ga), str(ga / 'backend/penn')]
    import numpy as np
    import serve_penn
    from backend.run_store import RunStore
    from penn_world import build_penn_world, WORLD_DATA
    from native_actioncastle import core_state, state_diff
    from local_component_client import LocalComponentClient
    from text_adventure_games import llm_client as upstream_client
    random.seed(args.seed); np.random.seed(args.seed)
    def dump(name, value):
        (args.out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    def primitive(value):
        if value is None: return None
        if hasattr(value, 'to_primitive'): return value.to_primitive()
        if dataclasses.is_dataclass(value): return dataclasses.asdict(value)
        return repr(value)
    def forbid_cloud(*a, **kw):
        raise RuntimeError('Hosted client construction forbidden in E35')
    original_factory = upstream_client.create_llm_client
    for module in list(sys.modules.values()):
        if getattr(module, 'create_llm_client', None) is original_factory:
            setattr(module, 'create_llm_client', forbid_cloud)
    base = None; start = time.monotonic()
    if args.backend == 'local':
        assert args.model is not None
        from strong_native_baseline import ModelClient
        base = ModelClient(args.model, args.seed, args.out / 'model_calls.jsonl')
    elif args.backend == 'preflight':
        base = SimpleNamespace(calls=[])
    model_ready = time.monotonic()
    preflight_tools = []
    class PreflightClient:
        """Exercise native client wiring without a model or behavioral claims."""
        def __init__(self, role): self.context = {'role': role}
        def call_tool(self, messages, tool, *args, **kwargs):
            preflight_tools.append(tool['name']); return None
        def call_tools(self, *a, **kw): return None
        def chat(self, *a, **kw): return ''
    class LocalStepper(serve_penn.PennStepper):
        def _decide_client(self):
            if args.backend == 'preflight': return PreflightClient('decide')
            return LocalComponentClient(base, args.max_calls, 'decide')
        def _role_client(self, role):
            if args.backend == 'preflight': return PreflightClient(role)
            return LocalComponentClient(base, args.max_calls, role)
    world = build_penn_world()
    assert [p['name'] for p in world.personas] == ['Diego Torres', 'Professor Tanaka', 'Sofia Ramirez']
    original_build = world.build_world_fn
    parser_records = []; depth = 0
    def build_capture(world_map):
        nonlocal depth
        game, chars = original_build(world_map)
        original = game.parser.parse_command
        def parse(command, actor=None, *a, **kw):
            nonlocal depth
            level = depth; depth += 1
            before = core_state(game); before_calls = len(base.calls) if base else 0
            try:
                success = bool(original(command, actor, *a, **kw))
            finally:
                depth -= 1
            after = core_state(game)
            row = {'command': command, 'actor': getattr(actor, 'name', None), 'depth': level,
                   'success': success, 'model_calls_before': before_calls,
                   'model_calls_after': len(base.calls) if base else 0,
                   'failure': None if success else getattr(game.parser, 'last_fail_message', None),
                   'material_delta': state_diff(before, after), 'before': before, 'after': after}
            parser_records.append(row)
            with (args.out / 'parser_calls.jsonl').open('a') as f:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
            return success
        game.parser.parse_command = parse
        return game, chars
    world.build_world_fn = build_capture
    dump('manifest.json', {'source_sha': source_sha, 'world_file': WORLD_DATA,
         'world_sha256': hashlib.sha256(Path(WORLD_DATA).read_bytes()).hexdigest(),
         'harness_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'backend': args.backend, 'model': str(args.model), 'seed': args.seed, 'steps': args.steps,
         'max_calls': args.max_calls, 'official_runner': 'PennStepper', 'decide_workers': 0,
         'events': world.events, 'personas': world.personas, 'cloud_factory': 'raises',
         'cloud_calls': 0, 'world_or_rules_changed': False,
         'llm_descriptor_note': 'Non-None descriptor enables native LLM path; overridden factories construct only local vLLM adapters.'})
    store = RunStore(args.out / 'native_store')
    stepper_class = LocalStepper if base else serve_penn.PennStepper
    descriptor = {'provider': 'local-vllm', 'model': str(args.model), 'max_cost_usd': None} if base else None
    frames = []; stop_reason = 'episode_complete'; error = None; stepper = None
    try:
        stepper = stepper_class(num_steps=args.steps, world=world, llm=descriptor,
                 run_store=store, decide_workers=0, plan_mode='llm' if base else 'schedule', seed=args.seed)
        if base:
            assert not stepper.injector._meetings
        initial_plans = {name: primitive(char.agent.plan) for name, char in stepper.chars.items()}
        dump('initial_plans.json', initial_plans)
        dump('initial_memories.json', {name: [r.to_primitive() for r in char.agent.memory.records]
                                      for name, char in stepper.chars.items()})
        if args.backend == 'preflight': stop_reason = 'adapter_preflight_only'
        for _ in range(0 if args.backend == 'preflight' else args.steps):
            if base and args.max_calls and len(base.calls) >= args.max_calls:
                stop_reason = 'model_call_cap'; break
            frame = stepper.tick()
            if frame is None: break
            frames.append(copy.deepcopy(frame))
            if len(frames) % 100 == 0:
                print(json.dumps({'ticks': len(frames), 'model_calls': len(base.calls) if base else 0}), flush=True)
    except Exception as exc:
        error = f'{type(exc).__name__}: {exc}'; stop_reason = 'exception'
        (args.out / 'exception.txt').write_text(traceback.format_exc())
    if stepper is not None:
        stepper._finish_run()
        dump('final_plans.json', {name: primitive(char.agent.plan) for name, char in stepper.chars.items()})
        dump('final_memories.json', {name: [r.to_primitive() for r in char.agent.memory.records]
                                    for name, char in stepper.chars.items()})
        dump('final_world_state.json', core_state(stepper.game))
    dump('frames.json', frames)
    root = [r for r in parser_records if r['depth'] == 0]
    summary = {'backend': args.backend, 'seed': args.seed, 'frames': len(frames),
         'stop_reason': stop_reason, 'error': error, 'root_parser_calls': len(root),
         'root_legal': sum(r['success'] for r in root),
         'model_calls': len(base.calls) if base else 0,
         'calls_by_tool': {t: sum(r.get('tool', {}).get('name') == t for r in base.calls)
                           for t in sorted({r.get('tool', {}).get('name') for r in base.calls if r.get('tool')})} if base else {},
         'planner_sources': stepper._planner_sources if stepper is not None else {},
         'conversations': stepper._conversations_total if stepper is not None else 0,
         'prompt_tokens': sum(r['prompt_tokens'] for r in base.calls) if base else 0,
         'completion_tokens': sum(r['completion_tokens'] for r in base.calls) if base else 0,
         'model_load_seconds': model_ready - start, 'run_seconds': time.monotonic() - model_ready,
         'wall_seconds': time.monotonic() - start, 'cloud_calls': 0,
         'scientific_increment': 0, 'raw': str(args.out)}
    summary['preflight_tools'] = preflight_tools
    dump('summary.json', summary); print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
