"""Run all three registered E49 cases with one local model engine."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from penn_cross_role_commitments import main as run_case


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--actor', choices=['Diego Torres','Sofia Ramirez'], required=True)
    ap.add_argument('--style', choices=['original','contrast'], required=True)
    ap.add_argument('--plan-channel', choices=['keep','block'], required=True)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--cpu-prefix', action='store_true')
    args=ap.parse_args()
    args.out.mkdir(exist_ok=False)
    root=Path('/home/xiang/.cache/game-npc-research/runs')
    sources=[(3501,root/'e35_original_cast/partial_local'),
             (3502,root/'e35_natural_repeats/seed3502'),
             (3503,root/'e35_natural_repeats/seed3503')]
    engine_cache={}
    completed=[]
    for seed,recording in sources:
        out=args.out/('seed'+str(seed))
        run_case(SimpleNamespace(source=Path('/home/xiang/.cache/game-npc-research/sources/agent-sandbox'),
            recording=recording, fork_step=None, actor=args.actor, style=args.style,
            plan_channel=args.plan_channel, model=args.model, conditions=['grounded'],
            cpu_replay=False, cpu_prefix=args.cpu_prefix, out=out), engine_cache)
        completed.append(json.loads((out/'summary.json').read_text()))
    (args.out/'worker_summary.json').write_text(json.dumps({'actor':args.actor,'style':args.style,
        'plan_channel':args.plan_channel,'completed_cases':completed,'model_engines':len(engine_cache),
        'cloud_calls':0},indent=2)+'\n')


if __name__=='__main__':
    main()
