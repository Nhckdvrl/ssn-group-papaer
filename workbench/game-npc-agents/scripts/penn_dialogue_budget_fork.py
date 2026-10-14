"""E47: registered focal dialogue budget control with original game state.

No world, task, persona, or execution rule changes. A complete recorded branch
can be replayed without a model because the outer cassette records the original
engine requests; the model trace separately records the added factual sentence.
"""
import argparse
import copy
import dataclasses
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def dialogue_facts(messages, condition, stamp, dialogue_style="original"):
    from native_tool_loop import template_messages
    actual = copy.deepcopy(messages)
    view = template_messages(actual)
    is_dialogue = ("Persona: I am Professor Tanaka," in view[0]["content"]
                   and view[-1]["content"].startswith("You are talking with "))
    if is_dialogue and dialogue_style == "reserved":
        assert actual[0]["content"].count("precise and warm with students") == 1
        actual[0]["content"] = actual[0]["content"].replace("precise and warm with students", "precise and reserved with students")
    sentence = None
    if is_dialogue and condition != "native":
        sentence = "The current game time is "+stamp
        if condition == "clock_and_duty":
            sentence += "; your authored schedule has you hosting the 10:00 gravitational-waves lecture at Irvine Auditorium"
        sentence += "."
        actual[-1]["content"] += "\n"+sentence
    return actual, sentence


def dialogue_budget(messages, budget):
    from native_tool_loop import template_messages
    view = template_messages(messages)
    target = ('Persona: I am Professor Tanaka,' in view[0]['content']
              and view[-1]['content'].startswith('You are talking with '))
    return 512 if target else budget


def progress_messages(messages, condition, stamp, dialogue_style, progress_text):
    actual, sentence = dialogue_facts(messages, condition, stamp, dialogue_style)
    if sentence:
        actual[-1]['content'] += '\n'+progress_text
    return actual, sentence


def plan_progress(stepper, actor='Professor Tanaka'):
    agent = stepper.chars[actor].agent
    plan = agent.plan
    cursor = int(agent.schedule.stop_index)
    assert -1 <= cursor <= len(plan.stops)
    rows = []
    for index, stop in enumerate(plan.stops):
        status = 'completed' if index < cursor else 'current' if index == cursor else 'upcoming'
        pin = f' (pinned {stop.start_hour:02d}:00)' if stop.start_hour is not None else ''
        rows.append(f'{index}. {status}: {stop.activity} at {stop.place}{pin}')
    state = stepper.state[actor]
    payload = {'schedule_stop_index': cursor, 'plan_revision': plan.revision,
        'current_engine_activity': state['desc'], 'performing': bool(state['performing']),
        'waiting_for_anchor': bool(state['waiting_for_anchor']), 'labelled_plan': rows,
        'scope': 'Your plan execution boundary; not a physical proof of task achievement.'}
    text = 'Your current plan and its execution position:\n'+'\n'.join(rows)
    text += '\nYour current engine activity: '+str(state['desc'])
    text += '\nPerforming: '+str(bool(state['performing']))+'; waiting for a pinned next stop: '+str(bool(state['waiting_for_anchor']))
    return text, payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/agent-sandbox'))
    ap.add_argument('--recording', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs/e35_natural_repeats/seed3502'))
    ap.add_argument('--fork-step', type=int)
    ap.add_argument('--dialogue-style', choices=['original','reserved'], required=True)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--conditions', nargs='+', choices=['native', 'clock', 'clock_and_duty'], default=['native', 'clock', 'clock_and_duty'])
    ap.add_argument('--cpu-replay', action='store_true')
    ap.add_argument('--cpu-prefix', action='store_true')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false', LLM_PROVIDER='mock')
    assert subprocess.check_output(['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip() == 'd7b872e396df2ef05ff8391de53e0563ca698cf3'
    ga = args.source/'godot-generative-agents'
    sys.path[:0] = [str(args.source), str(ga), str(ga/'backend/penn')]
    import serve_penn
    from text_adventure_games.recording import ReplayClient, RecordingClient, request_key, _dump
    from text_adventure_games import llm_client
    from native_actioncastle import core_state, state_diff
    from local_component_client import LocalComponentClient
    from native_tool_loop import template_messages
    manifest_path = next((args.recording/'native_store').glob('run-*/manifest.json'))
    manifest = json.loads(manifest_path.read_text())
    cassette = manifest_path.parent/'cassette.jsonl'
    expected_frames = json.loads((args.recording/'frames.json').read_text())
    original_calls = [json.loads(x) for x in (args.recording/'model_calls.jsonl').read_text().splitlines()]
    assert manifest['num_steps'] == 1200
    selected = [(i,r) for i,r in enumerate(original_calls)
        if (r.get('tool') or {}).get('name')=='speak'
        and (r.get('context') or {}).get('actor')=='Professor Tanaka'
        and r['context']['turn']>=720]
    prefix_calls, first_call = selected[0]
    if args.fork_step is None:
        args.fork_step = first_call['context']['turn']
    assert args.fork_step == first_call['context']['turn']
    originals = {n: getattr(ReplayClient, n) for n in ['chat', 'call_tool', 'call_tools', 'count_tokens']}
    class CloudForbidden(BaseException):
        pass
    class PrefixComplete(BaseException):
        pass
    def forbid_cloud(*a, **kw):
        raise CloudForbidden('Hosted client construction is forbidden')
    factory = llm_client.create_llm_client
    for module in list(sys.modules.values()):
        if getattr(module, 'create_llm_client', None) is factory:
            setattr(module, 'create_llm_client', forbid_cloud)
    base = None
    load_seconds = 0.
    if not (args.cpu_replay or args.cpu_prefix):
        assert args.model is not None
        from strong_native_baseline import ModelClient
        started = time.monotonic()
        class EagerModelClient(ModelClient):
            def __init__(self, model, seed, trace_file):
                from vllm import LLM
                self.llm = LLM(model=str(model), tensor_parallel_size=1, dtype='bfloat16',
                    gpu_memory_utilization=.82, max_model_len=8192, enforce_eager=True,
                    enable_prefix_caching=True, seed=seed, language_model_only=True,
                    safetensors_load_strategy='eager')
                self.tokenizer = self.llm.get_tokenizer()
                self.seed, self.calls, self.trace_file = seed, [], Path(trace_file)
        base = EagerModelClient(args.model, manifest['seed'], args.out/'unused_model_calls.jsonl')
        load_seconds = time.monotonic()-started
    all_results = {}
    conditions = ['cpu_replay'] if args.cpu_replay else ['cpu_prefix'] if args.cpu_prefix else args.conditions
    for condition in conditions:
        out = args.out/condition
        out.mkdir()
        frames, prefix_rows, additions, parser_rows = [], [], [], []
        first_request = None
        prefix_hits = 0
        depth = 0
        started = time.monotonic()
        def dump(name, value):
            (out/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
        class FactualClient(LocalComponentClient):
            def prepared(self, messages, method):
                stamp = stepper.clock.time_at(len(frames)).strftime('%H:%M:%S')
                text, payload = plan_progress(stepper)
                actual, sentence = progress_messages(messages, condition, stamp, args.dialogue_style, text)
                progress = payload if sentence else None
                if sentence or actual[0]['content'] != messages[0]['content']:
                    additions.append({'step': len(frames), 'sentence': sentence,
                        'method': method, 'actor': 'Professor Tanaka', 'world_fact_changed': False,
                        'persona_clause_changed': actual[0]['content'] != messages[0]['content'],
                        'plan_progress_disclosure': progress})
                self.context.clear()
                self.context.update(role='native_suffix', turn=len(frames), method=method)
                return actual
            def call_tool(self, messages, tool, *a, **kw):
                actual = self.prepared(messages, 'speak_tool') if tool['name']=='speak' else messages
                if tool['name'] == 'speak':
                    if a:
                        a = (dialogue_budget(actual, a[0]),)+a[1:]
                    else:
                        kw['max_tokens'] = dialogue_budget(actual, kw.get('max_tokens',128))
                self.context.clear()
                self.context.update(role='native_'+tool['name'], turn=len(frames), tool_name=tool['name'])
                return super().call_tool(actual, tool, *a, **kw)
            def chat(self, messages, *a, **kw):
                actual = self.prepared(messages, 'free_text_fallback')
                if a:
                    a = (dialogue_budget(actual, a[0]),)+a[1:]
                else:
                    kw['max_tokens'] = dialogue_budget(actual, kw.get('max_tokens',128))
                return super().chat(actual, *a, **kw)
        recorder = None
        if base:
            base.seed = manifest['seed']
            base.calls = copy.deepcopy(original_calls[:prefix_calls])
            base.trace_file = out/'model_calls.jsonl'
            recorder = RecordingClient(FactualClient(base, 0, 'native_suffix'), path=str(out/'suffix_cassette.jsonl'))
        def wrapper(name):
            def invoke(client, *a, **kw):
                nonlocal prefix_hits, first_request
                replaying = args.cpu_replay or len(frames) < args.fork_step
                if replaying:
                    result = originals[name](client, *a, **kw)
                    if name != 'count_tokens':
                        prefix_hits += 1
                        bound = inspect.signature(originals[name]).bind(client, *a, **kw)
                        bound.apply_defaults()
                        values = bound.arguments
                        key = request_key(name, values['messages'], values['max_tokens'], values['temperature'],
                            tools=values.get('tools', values.get('tool')), tool_choice=values.get('tool_choice'))
                        prefix_rows.append({'method': name, 'key': key, 'response': _dump(result)})
                    return result
                if name != 'count_tokens' and first_request is None:
                    first_request = {'method': name, 'messages': copy.deepcopy(a[0]), 'tool': copy.deepcopy(a[1]) if len(a)>1 else None,
                                     'prefix_model_responses': prefix_hits, 'step': len(frames)}
                    assert prefix_hits == prefix_calls
                    assert a[0] == first_call['messages']
                    assert name == 'call_tool' and a[1]['name'] == 'speak'
                if args.cpu_prefix:
                    if name == 'count_tokens':
                        return originals[name](client, *a, **kw)
                    raise PrefixComplete()
                return getattr(recorder, name)(*a, **kw)
            return invoke
        for name in originals:
            setattr(ReplayClient, name, wrapper(name))
        world = serve_penn.SCENARIOS[manifest.get('scenario', 'penn')]['world']()
        build = world.build_world_fn
        def capture(world_map):
            game, chars = build(world_map)
            parse = game.parser.parse_command
            def tracked(command, actor=None, *a, **kw):
                nonlocal depth
                level = depth
                depth += 1
                before = core_state(game)
                try:
                    success = bool(parse(command, actor, *a, **kw))
                finally:
                    depth -= 1
                after = core_state(game)
                parser_rows.append({'step': len(frames), 'depth': level, 'actor': getattr(actor, 'name', None),
                    'command': command, 'success': success, 'material_delta': state_diff(before, after)})
                return success
            game.parser.parse_command = tracked
            return game, chars
        world.build_world_fn = capture
        stepper = serve_penn.PennStepper(num_steps=manifest['num_steps'], world=world, llm=None,
            run_store=None, seed=manifest['seed'], decide_workers=0, replay_cassette=str(cassette),
            cognition_tools=manifest.get('cognition_tools', False), react=manifest.get('react', False),
            plan_mode=manifest.get('plan_mode', 'schedule'), sim_config=serve_penn._sim_config_from_manifest(manifest),
            vision_r=serve_penn.SCENARIOS[manifest.get('scenario', 'penn')]['vision_r'])
        error = None
        try:
            for i in range(manifest['num_steps']):
                frame = stepper.tick()
                assert frame is not None
                if args.cpu_replay or i < args.fork_step:
                    assert serve_penn._canonical_frame(frame) == serve_penn._canonical_frame(expected_frames[i]), f'Prefix diverged at {i}'
                frames.append(copy.deepcopy(frame))
                if len(frames)%100 == 0:
                    print(json.dumps({'condition': condition, 'frames': len(frames), 'new_calls': len(base.calls)-prefix_calls if base else 0}), flush=True)
        except PrefixComplete:
            pass
        except BaseException as exc:
            error = f'{type(exc).__name__}: {exc}'
            raise
        finally:
            if recorder:
                recorder.close()
        if args.cpu_prefix:
            progress_text, progress_payload = plan_progress(stepper)
            dump('first_progress_snapshot.json', {'text': progress_text, 'payload': progress_payload})
        dump('frames.json', frames)
        dump('first_suffix_request.json', first_request)
        dump('factual_additions.json', additions)
        dump('parser_calls.json', parser_rows)
        dump('final_plans.json', {n: dataclasses.asdict(c.agent.plan) for n, c in stepper.chars.items()})
        dump('final_memories.json', {n: [r.to_primitive() for r in c.agent.memory.records] for n, c in stepper.chars.items()})
        dump('final_world_state.json', core_state(stepper.game))
        if recorder:
            counts = [line for line in cassette.read_text().splitlines() if json.loads(line).get('method') == 'count_tokens']
            prefix = '\n'.join(counts+[json.dumps(r, ensure_ascii=False) for r in prefix_rows])+'\n'
            (out/'combined_cassette.jsonl').write_text(prefix+(out/'suffix_cassette.jsonl').read_text())
        result = {'condition': condition, 'seed': manifest['seed'], 'fork_step': args.fork_step,
            'frames': len(frames), 'prefix_byte_equal_frames': min(len(frames), args.fork_step),
            'complete_cpu_replay_byte_equal': args.cpu_replay and len(frames)==1200,
            'first_suffix_request_matches_source': first_request is not None,
            'prefix_model_responses': prefix_hits, 'new_local_calls': len(base.calls)-prefix_calls if base else 0,
            'dialogue_style': args.dialogue_style,
            'factual_additions': sum(r['sentence'] is not None for r in additions),
            'persona_instruction_edits': sum(r['persona_clause_changed'] for r in additions), 'root_parser_calls': sum(r['depth']==0 for r in parser_rows),
            'root_legal': sum(r['depth']==0 and r['success'] for r in parser_rows),
            'wall_seconds': time.monotonic()-started, 'error': error, 'cloud_calls': 0,
            'world_or_rules_changed': False,
            'authored_world_persona_preserved': True,
            'persona_intervention_scope': 'Professor conversation instruction only; original history and planner/decider preserved',
            'weight_load_strategy': 'eager',
            'own_plan_progress_disclosed_in_dialogue': True,
            'professor_dialogue_max_tokens':512, 'other_budgets_preserved':True, 'raw': str(out)}
        dump('summary.json', result)
        all_results[condition] = result
        print(json.dumps(result), flush=True)
    for name, method in originals.items():
        setattr(ReplayClient, name, method)
    (args.out/'summary.json').write_text(json.dumps({'model_load_seconds': load_seconds, 'branches': all_results,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'cloud_calls': 0}, indent=2)+'\n')


if __name__ == '__main__':
    main()
