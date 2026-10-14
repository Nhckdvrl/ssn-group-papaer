"""Recover exact engine state by strict cassette replay, then finish native ticks.

Never resumes from the source's deliberately partial memory-first checkpoint.
Any unrecorded model request stops execution; it cannot trigger scripted fallback.
"""
import argparse
import copy
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/agent-sandbox'))
    ap.add_argument('--recording', type=Path, required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--model', type=Path, help='Only genuinely new requests after the exact original prefix use this local model')
    ap.add_argument('--cassette', type=Path, help='Optional combined cassette for a zero-model verification')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    ga = args.source / 'godot-generative-agents'
    sys.path[:0] = [str(args.source), str(ga), str(ga / 'backend/penn')]
    import serve_penn
    from backend.run_store import RunStore
    from native_actioncastle import core_state
    from text_adventure_games.recording import ReplayClient, RecordingClient
    from text_adventure_games import llm_client
    class UnrecordedRequest(BaseException):
        pass
    def no_cloud(*a, **kw):
        raise UnrecordedRequest('Unexpected hosted client construction')
    original = llm_client.create_llm_client
    for module in list(sys.modules.values()):
        if getattr(module, 'create_llm_client', None) is original:
            setattr(module, 'create_llm_client', no_cloud)
    hits = []; misses = []; frames = []
    original_lookup = ReplayClient._lookup
    def lookup(self, key, messages):
        if not self._responses.get(key):
            misses.append({'key': key, 'messages': messages})
            raise UnrecordedRequest('Cassette exhausted or divergent request')
        value = original_lookup(self, key, messages); hits.append(key)
        return value
    ReplayClient._lookup = lookup
    store = RunStore(args.recording / 'native_store')
    manifest = store.get_run(args.run_id)['manifest']
    stored = store.read_frames(args.run_id)
    cassette = args.cassette or store.root / args.run_id / 'cassette.jsonl'
    base = None; recorder = None; load_start = time.monotonic()
    if args.model:
        os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
        from strong_native_baseline import ModelClient
        from local_component_client import LocalComponentClient
        base = ModelClient(args.model, manifest['seed'], args.out/'new_model_calls.jsonl')
        base.calls = [json.loads(line) for line in (args.recording/'model_calls.jsonl').read_text().splitlines()]
        recorder = RecordingClient(LocalComponentClient(base, 0, 'continued_native_request'),
                                   path=str(args.out/'new_cassette.jsonl'))
        def fallback_method(name, original_method):
            def invoke(self, *a, **kw):
                try:
                    return original_method(self, *a, **kw)
                except UnrecordedRequest:
                    if len(frames) < len(stored): raise
                    return getattr(recorder, name)(*a, **kw)
            return invoke
        for name in ['chat', 'call_tool', 'call_tools']:
            setattr(ReplayClient, name, fallback_method(name, getattr(ReplayClient, name)))
    model_ready = time.monotonic()
    scenario = serve_penn.SCENARIOS[manifest.get('scenario', 'penn')]
    error = None; stepper = None; start = time.monotonic()
    try:
        stepper = serve_penn.PennStepper(
            num_steps=manifest['num_steps'], world=scenario['world'](), llm=None,
            run_store=None, seed=manifest['seed'], decide_workers=0,
            replay_cassette=str(cassette),
            cognition_tools=manifest.get('cognition_tools', False), react=manifest.get('react', False),
            plan_mode=manifest.get('plan_mode', 'schedule'),
            sim_config=serve_penn._sim_config_from_manifest(manifest), vision_r=scenario['vision_r'])
        for i in range(manifest['num_steps']):
            frame = stepper.tick()
            if frame is None: break
            if i < len(stored):
                if serve_penn._canonical_frame(frame) != serve_penn._canonical_frame(stored[i]):
                    raise UnrecordedRequest(f'Frame diverged at {i}')
            frames.append(copy.deepcopy(frame))
    except UnrecordedRequest as exc:
        error = str(exc)
    if recorder is not None:
        recorder.close()
        (args.out/'combined_cassette.jsonl').write_bytes(cassette.read_bytes() + (args.out/'new_cassette.jsonl').read_bytes())
    def dump(name, value):
        (args.out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    dump('frames.json', frames); dump('unrecorded_requests.json', misses)
    if stepper is not None:
        dump('final_world_state.json', core_state(stepper.game))
        dump('final_plans.json', {n: dataclasses.asdict(c.agent.plan) for n, c in stepper.chars.items()})
        dump('final_memories.json', {n: [r.to_primitive() for r in c.agent.memory.records] for n, c in stepper.chars.items()})
        dump('events.json', [dataclasses.asdict(e) if dataclasses.is_dataclass(e) else vars(e)
                             for e in stepper.game.events])
    result = {'original_frames': len(stored), 'replayed_frames': min(len(frames), len(stored)),
        'total_frames': len(frames), 'native_episode_budget': manifest['num_steps'],
        'original_prefix_frames_byte_equal': len(frames) >= len(stored),
        'cassette_hits': len(hits), 'unrecorded_requests': len(misses), 'error': error,
        'new_model_calls': len(base.calls)-len(hits) if base else 0, 'cloud_calls': 0,
        'model_load_seconds': model_ready-load_start, 'wall_seconds': time.monotonic()-start,
        'cassette_sha256': hashlib.sha256(cassette.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    dump('summary.json', result); print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
