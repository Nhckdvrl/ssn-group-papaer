#!/usr/bin/env python3
"""Resume E64 after a logger-only death failure using recorded policy decisions."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import native_reciprocal_deathsafe as policy


def key(j):
    return tuple(j.get(k) for k in ['case_id', 'episode_seed', 'persona', 'cue', 'stage', 'acting_index', 'turn', 'seed'])


class MissingDecision(Exception): pass


class ReplayClient:
    def __init__(self, source, out, model, seed, cpu):
        self.source, self.out, self.model, self.seed, self.cpu = source, out, model, seed, cpu
        rows = list(map(json.loads, (source/'model_calls.jsonl').read_text().splitlines()))
        self.lookup = {key(r): r for r in rows}; assert len(rows) == len(self.lookup)
        self.client = None; self.replayed = 0

    @property
    def calls(self): return 0 if self.client is None else self.client.calls

    @property
    def load_seconds(self): return 0 if self.client is None else self.client.load_seconds

    def batch(self, jobs):
        answers = [None]*len(jobs); missing = []
        for i, j in enumerate(jobs):
            old = self.lookup.get(key(j))
            if old is None:
                missing.append((i, j)); continue
            assert old['messages'][0] == j['messages'][0], 'identity/rule changed'
            if j['stage'] != 'opening':
                assert set(old['schema']['properties']['action']['enum']) == set(j['schema']['properties']['action']['enum'])
                def observable_tail(msg):
                    return msg.split('\nYour goal resource is currently in your own possession: ',1)[1].split('\nLegal game commands:',1)[0]
                # This replays past decisions, not inference-cache responses.
                # Native inventory enumeration can permute text across processes.
                # Check objective state flags and menus; validate full physical
                # transitions against the previously completed episode tapes below.
                old_flags = observable_tail(old['messages'][-1]['content']).split('\nRecent observable interaction:',1)[0]
                new_flags = observable_tail(j['messages'][-1]['content']).split('\nRecent observable interaction:',1)[0]
                assert old_flags == new_flags, 'objective state replay mismatch'
            answers[i] = old['parsed']; self.replayed += 1
            with (self.out/'replayed_decisions.jsonl').open('a') as f:
                f.write(json.dumps({'key': key(j), 'source_prompt_sha256': old['prompt_sha256'],
                    'source': str(self.source), 'exact_rendered_messages': old['messages'] == j['messages'],
                    'method': 'prior decision tape replay, not inference on a different prompt'}, ensure_ascii=False)+'\n')
        if missing:
            if self.cpu: raise MissingDecision(str(key(missing[0][1])))
            if self.client is None: self.client = policy.BatchClient(self.model, self.out, self.seed)
            new = self.client.batch([j for _, j in missing])
            for (i, _), answer in zip(missing, new): answers[i] = answer
        return answers


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--validate-only',action='store_true');a=ap.parse_args()
    ref=json.loads((a.source/'manifest.json').read_text())
    rows=list(map(json.loads,Path(ref['arguments']['dataset']).read_text().splitlines()))
    old=list(map(json.loads,(a.source/'episodes.jsonl').read_text().splitlines()))
    assert len(rows)==9 and len(old)==12 and len({r['case_id'] for r in old})==1
    complete={r['case_id'] for r in old};seeds=ref['arguments']['seeds']
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={**ref,'arguments':{**ref['arguments'],'out':str(a.out)},
        'source_policy_sha256':ref['script_sha256'],
        'death_adapter_sha256':hashlib.sha256(Path(policy.__file__).read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'resumed_from':str(a.source),'completed_prefix_episodes':len(old),
        'validation_only':a.validate_only,'prior_runtime':json.loads((a.source/'interrupted_runtime.json').read_text())}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    modules=policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    client=ReplayClient(a.source,a.out,Path(ref['arguments']['model']),seeds[0],a.validate_only)
    original_apply=policy.apply
    def monitored_apply(g,*args):
        original_apply(g,*args)
        if g['stop']=='character_death':
            with (a.out/'death_events.jsonl').open('a') as f:
                f.write(json.dumps({'case_id':g['case']['case_id'],'seed':g['seed'],'persona':g['persona'],
                    'cue':g['cue'],'turn':g['turns'][-1]['turn'],'health':g['turns'][-1]['health_after']})+'\n')
    policy.apply=monitored_apply
    groups=[rows[:1]]+[rows[i:i+3] for i in range(1,len(rows),3)]
    if a.validate_only:
        policy.run_group(groups[0],seeds,client,modules,a.out)
        replayed=list(map(json.loads,(a.out/'episodes.jsonl').read_text().splitlines()))
        lookup={(r['case_id'],r['seed'],r['persona'],r['cue']):r for r in old}
        for r in replayed:
            base=lookup[r['case_id'],r['seed'],r['persona'],r['cue']]
            for field in ['initial_state','final_state','strict_goal_done','ever_attained','final_attained','final_health','final_dead']:
                assert r[field]==base[field],field
            assert len(r['turns'])==len(base['turns'])
            for t,b in zip(r['turns'],base['turns']):
                for field in ['command','before','after','legal','event_type','attained_after','health_before','health_after']:
                    assert t[field]==b[field],field
        try: policy.run_group(groups[1],seeds,client,modules,a.out)
        except MissingDecision as exc:
            result={'validated_complete_episodes':len(replayed),'replayed_prior_decisions':client.replayed,
                'first_unrecorded_decision':str(exc),'model_calls':0,'gpu_hours':0}
            assert (a.out/'death_events.jsonl').exists()
            (a.out/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return
        raise AssertionError('expected missing future decisions')
    (a.out/'episodes.jsonl').write_text((a.source/'episodes.jsonl').read_text())
    start=time.monotonic();count=len(old)
    for group in groups:
        if all(r['case_id'] in complete for r in group): continue
        assert all(r['case_id'] not in complete for r in group)
        count+=policy.run_group(group,seeds,client,modules,a.out)
        print(json.dumps({'episodes':count,'new_calls':client.calls,'replayed':client.replayed}),flush=True)
    assert count==108
    (a.out/'runtime.json').write_text(json.dumps({'worlds':9,'episodes':count,'calls':client.calls,
        'replayed_prior_decisions':client.replayed,'wall_seconds':time.monotonic()-start-client.load_seconds,
        'model_load_seconds':client.load_seconds,'prior_run':manifest['prior_runtime'],'cloud_calls':0},indent=2)+'\n')


if __name__=='__main__':main()
