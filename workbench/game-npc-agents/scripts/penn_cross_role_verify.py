"""Independent zero-model replay of every E49 causal branch, including its narrow intervention."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/agent-sandbox'))
    ap.add_argument('--recording', type=Path, required=True)
    ap.add_argument('--branch', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists()
    ga = args.source/'godot-generative-agents'
    sys.path[:0] = [str(args.source), str(ga), str(ga/'backend/penn')]
    import serve_penn
    from backend import cognition
    from text_adventure_games import llm_client

    class CloudForbidden(BaseException):
        pass

    factory = llm_client.create_llm_client

    def forbidden(*a, **kw):
        raise CloudForbidden('Zero-model verifier cannot create hosted clients')

    for module in list(sys.modules.values()):
        if getattr(module, 'create_llm_client', None) is factory:
            setattr(module, 'create_llm_client', forbidden)
    manifest = json.loads(next((args.recording/'native_store').glob('run-*/manifest.json')).read_text())
    expected = json.loads((args.branch/'frames.json').read_text())
    branch_summary = json.loads((args.branch/'summary.json').read_text())
    actor = branch_summary['actor']
    fork_step = branch_summary['fork_step']
    blocked_channel = branch_summary['plan_channel'] == 'block'
    cassette = args.branch/'combined_cassette.jsonl'
    scenario = serve_penn.SCENARIOS[manifest.get('scenario', 'penn')]
    started = time.monotonic()
    frame_index = -1
    blocked = []
    native_revision = cognition.maybe_revise_plan

    def controlled_revision(char, trigger, clock=None):
        if blocked_channel and frame_index >= fork_step and char.name == actor and trigger.reason == cognition.CONVERSATION:
            blocked.append({'frame': frame_index, 'actor': char.name, 'detail': trigger.detail})
            return cognition.PlanRevisionResult()
        return native_revision(char, trigger, clock)

    cognition.maybe_revise_plan = controlled_revision
    try:
        stepper = serve_penn.PennStepper(num_steps=manifest['num_steps'], world=scenario['world'](), llm=None,
            run_store=None, seed=manifest['seed'], decide_workers=0, replay_cassette=str(cassette),
            cognition_tools=manifest.get('cognition_tools', False), react=manifest.get('react', False),
            plan_mode=manifest.get('plan_mode', 'schedule'), sim_config=serve_penn._sim_config_from_manifest(manifest),
            vision_r=scenario['vision_r'])
        assert len(expected) == manifest['num_steps']
        for frame_index, original in enumerate(expected):
            actual = stepper.tick()
            assert serve_penn._canonical_frame(actual) == serve_penn._canonical_frame(original), f'Branch differs at frame {frame_index}'
        assert len(blocked) == branch_summary['suppressed_conversation_revisions']
    finally:
        cognition.maybe_revise_plan = native_revision
    result = {'frames_verified': len(expected), 'all_frames_byte_equal': True, 'new_model_or_API_calls': 0,
        'cassette_sha256': hashlib.sha256(cassette.read_bytes()).hexdigest(), 'branch': str(args.branch),
        'actor': actor, 'plan_channel':branch_summary['plan_channel'], 'fork_step':fork_step,
        'intervention': 'Focal conversation-triggered explicit revision suppressed after fork only when registered block channel',
        'suppressed_revisions_match_branch': True, 'blocked': blocked, 'wall_seconds': time.monotonic()-started}
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
