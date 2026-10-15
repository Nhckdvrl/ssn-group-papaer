#!/usr/bin/env python3
"""Resume E68 by exact message/schema/seed replay; publish only after full validation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import native_rule_execution as execution


def digest(job):
    return hashlib.sha256(json.dumps({k:job[k] for k in ['messages','schema','seed']},
        sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def identity(job):
    return tuple(job.get(k) for k in ['case_id','persona','stage','seed','upstream_rule','exec_rule','request_mode','step'])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resume-source',type=Path,required=True)
    ap.add_argument('--prior-reserved-seconds',type=float,required=True)
    options,remaining=ap.parse_known_args()
    oi=remaining.index('--out')+1;target=Path(remaining[oi]);working=target.with_name(target.name+'.working')
    assert not target.exists() and not working.exists()
    remaining[oi]=str(working)
    prior=[];partial_tail=None;lines=(options.resume_source/'model_calls.jsonl').read_text().splitlines()
    for i,line in enumerate(lines):
        try:prior.append(json.loads(line))
        except json.JSONDecodeError:
            assert i==len(lines)-1
            partial_tail={'bytes':len(line.encode()),'sha256':hashlib.sha256(line.encode()).hexdigest()}
    by_identity={identity(r):digest(r) for r in prior};by_hash={digest(r):r for r in prior}
    assert len(by_hash)==len(prior)
    clients=[];Original=execution.SharedPrefixClient
    class Resumed(Original):
        def __init__(self,model,out,seed):
            super().__init__(model,out,seed)
            self.cache.update({k:r['parsed'] for k,r in by_hash.items()});self.prior_seen=set()
            self.inner.trace.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in prior))
            self.inner.calls=len(prior)
            self.inner.load_seconds+=options.prior_reserved_seconds
            clients.append(self)
        def batch(self,jobs):
            for j in jobs:
                k=digest(j);old=by_identity.get(identity(j))
                if old is not None:assert k==old, ('Prior prompt changed',identity(j))
                if k in by_hash:self.prior_seen.add(k)
            return super().batch(jobs)
    execution.SharedPrefixClient=Resumed
    import native_reserve_rule_execution as driver
    sys.argv=[str(Path(driver.__file__)),*remaining];driver.main()
    assert len(clients)==1 and clients[0].prior_seen==set(by_hash)
    old_episodes=[]
    if (options.resume_source/'episodes.jsonl').exists():
        old_episodes=list(map(json.loads,(options.resume_source/'episodes.jsonl').read_text().splitlines()))
    def episode_key(r):return tuple(r[k] for k in ['case_id','seed','persona','mode','upstream_rule','exec_rule','feedback'])
    new={episode_key(r):r for r in map(json.loads,(working/'episodes.jsonl').read_text().splitlines())}
    assert all(new[episode_key(r)]==r for r in old_episodes)
    validation={'all_prior_recorded_calls_replayed':len(prior),'prior_complete_episodes_identical':len(old_episodes),
        'partial_write_tail_preserved_in_original':partial_tail,'source':str(options.resume_source),
        'source_calls_sha256':hashlib.sha256((options.resume_source/'model_calls.jsonl').read_bytes()).hexdigest(),
        'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'prior_reserved_seconds_included_in_model_load_seconds':options.prior_reserved_seconds,
        'sampling_or_world_changed':False,'source_cost_basis':'Conservative full process reservation, including startup and I/O.'}
    (working/'resume_validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    working.rename(target);print(json.dumps(validation),flush=True)


if __name__=='__main__':main()
