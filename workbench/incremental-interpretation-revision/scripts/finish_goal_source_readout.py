"""E68 whole-panel runner, then complete goal and route contrasts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from data import sha


def main(a):
    script=Path(__file__).parent;root=a.root;root.mkdir(parents=True,exist_ok=True);cache=root.parent
    names=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'];procs=[];logs=[]
    def launch(phase):
        result=[]
        for gpu,name in enumerate(names):
            out=root/('instruments-v1' if phase=='instrument' else 'runs-v1')/name
            log=(root/f'{phase}-{name}.log').open('w');logs.append(log);env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
            cmd=[a.python,str(script/'goal_source_readout.py'),'--data',str(cache/'E65/data-v1.jsonl'),'--model',str(cache/'models'/name),'--reference',str(cache/'E65/runs-v1'/name),'--out',str(out),'--gpu',str(gpu)]
            if phase=='instrument':cmd+=['--instrument-only']
            result.append(subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True))
        return result
    for phase in ['instrument','science']:
        procs=launch(phase);(root/f'{phase}-pids.json').write_text(json.dumps([p.pid for p in procs])+'\n')
        while any(p.poll() is None for p in procs):time.sleep(10)
        assert all(p.returncode==0 for p in procs),f'{phase} failure; no next stage'
        print('E68 all three',phase,'complete',flush=True)
    out=root/'goal-by-question-read-only-v1.json'
    cmd=[a.python,str(script/'analyze_goal_conditioned_reading.py'),'--data',str(cache/'E65/data-v1.jsonl'),'--runs',*[str(root/'runs-v1'/n) for n in names],'--out',str(out),'--seed','68']
    subprocess.run(cmd,check=True)
    import collections
    from analyze_reading_map import estimate
    native=cache/'E65/goal-by-question-map-v1.cluster-effects.jsonl';routed=out.with_suffix('.cluster-effects.jsonl')
    def effects(path):
        x=collections.defaultdict(dict)
        for line in path.read_text().splitlines():
            r=json.loads(line);assert r['cluster_id'] not in x[r['report']];x[r['report']][r['cluster_id']]=r['value']
        return x
    n=effects(native);r=effects(routed);assert set(n)==set(r);reports={}
    for key,values in r.items():
        assert set(values)==set(n[key]);reports[key]=estimate({c:v-n[key][c] for c,v in values.items()},seed=68)
    target=root/'read-only-minus-native-v1.json';target.write_text(json.dumps(dict(reports=reports,native_path=str(native),native_sha256=sha(native),read_only_path=str(routed),read_only_sha256=sha(routed),interpretation='Paired READ_ONLY-minus-native for each original report, including difference of goal effects. Empty reports remain in complete goal maps.'),indent=2)+'\n')
    s_path=cache/'E66/goal-by-question-source-only-v1.cluster-effects.jsonl';source=effects(s_path);assert set(source)==set(r)
    cross={}
    for key,values in r.items():
        assert set(values)==set(source[key]);cross[key]=estimate({c:v-source[key][c] for c,v in values.items()},seed=68)
    cross_path=root/'read-only-minus-source-only-v1.json';cross_path.write_text(json.dumps(dict(reports=cross,read_only_sha256=sha(routed),source_only_path=str(s_path),source_only_sha256=sha(s_path)),indent=2)+'\n')
    subprocess.run([a.python,str(script/'analyze_goal_truth_strata.py'),'--data',str(cache/'E65/data-v1.jsonl'),'--runs',*[str(root/'runs-v1'/n) for n in names],'--out',str(root/'goal-truth-strata-posthoc-v1.json')],check=True)
    (root/'complete-map-v1.json').write_text(json.dumps(dict(goal_map=str(out),goal_map_sha256=sha(out),route_contrasts=str(target),route_contrasts_sha256=sha(target),cross_path=str(cross_path),cross_sha256=sha(cross_path)),indent=2)+'\n');print('E68 complete maps ready',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--python',required=True);main(p.parse_args())
