#!/usr/bin/env python3
"""Freeze conservative locally unexposed LIGHT reserve worlds before E68 calls."""
import collections
import hashlib
import json
import os
from pathlib import Path
import re


def digest(s):return hashlib.sha256(s.encode()).hexdigest()


def main():
    root=Path('/home/xiang/.cache/game-npc-research/runs')
    source=root/'e50_native_snapshots_v1/snapshots.jsonl'
    reserve=[r for r in map(json.loads,source.read_text().splitlines()) if r['split']=='reserve']
    assert len(reserve)==120
    by_id={r['case_id']:r for r in reserve}
    by_file={r['quest_file']:r['case_id'] for r in reserve}
    by_graph={digest(json.dumps(json.loads(r['quest']['graph']),sort_keys=True)):r['case_id'] for r in reserve}
    exposed=collections.defaultdict(set);traces=[];run_dirs=set();metadata=[]
    actual_ids=collections.defaultdict(set)
    for path,dirs,files in os.walk(root):
        # Freeze to all existing numbered experiments preceding this new reserve run.
        rel=Path(path).relative_to(root)
        if not rel.parts:continue
        match=re.match(r'e(\d+)',rel.parts[0])
        if not match or int(match[1])>=68:
            dirs[:]=[];continue
        for name in files:
            if name in ['model_calls.jsonl','calls.jsonl','calls.json','model_calls.json']:
                f=Path(path)/name
                if f.stat().st_size:
                    traces.append(f);run_dirs.add(root/rel.parts[0])
            elif name=='prompts.jsonl' and any(n.endswith('.pt') for n in files):
                traces.append(Path(path)/name);run_dirs.add(root/rel.parts[0])
    pattern=re.compile(rb'"case_id"\s*:\s*"([^"\\]+)"')
    scanned=0
    for f in traces:
        with f.open('rb') as stream:
            for line in stream:
                scanned+=len(line)
                for cid in pattern.findall(line):
                    cid=cid.decode()
                    actual_ids[root/f.relative_to(root).parts[0]].add(cid)
                    if cid in by_id:exposed[cid].add(str(f))
    def visit(obj,origin):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in ['graph','graph_json'] and isinstance(v,str):
                    try:cid=by_graph.get(digest(json.dumps(json.loads(v),sort_keys=True)))
                    except (json.JSONDecodeError,TypeError):cid=None
                    if cid:exposed[cid].add(str(origin)+'#canonical_graph')
                if k in ['case_id','graph_sha256'] and isinstance(v,str) and v[:16] in by_id:
                    exposed[v[:16]].add(str(origin)+'#'+k)
                if k in ['quest_file','npc_quest_file','human_quest_file'] and v in by_file:
                    exposed[by_file[v]].add(str(origin)+'#'+k)
                visit(v,origin)
        elif isinstance(obj,list):
            for v in obj:visit(v,origin)
    for d in sorted(run_dirs):
        # Associated input manifests conservatively exclude even unconfirmed prefix rows.
        for name in ['manifest.json','source_cases.json','source_pairs.json','snapshots.json']:
            f=d/name
            if f.exists():
                visit(json.loads(f.read_text()),f);metadata.append(str(f))
        manifest=d/'manifest.json'
        if manifest.exists():
            m=json.loads(manifest.read_text())
            dataset=m.get('dataset',m.get('arguments',{}).get('dataset'))
            if dataset and Path(dataset).is_file():
                f=Path(dataset)
                if f.suffix=='.jsonl':
                    for row in map(json.loads,f.read_text().splitlines()):
                        rid=row.get('case_id',row.get('case',{}).get('case_id'))
                        if rid in actual_ids[d]:visit(row,f)
                    metadata.append(str(f)+'#actual_model_case_ids')
    # E57/E64 use different pair identifiers; their published qualification files
    # are fixed input worlds, all used in completed inference. Resolve graphs too.
    for name in ['e57_native_food_pairs','e64_native_reciprocal_qualification']:
        f=root/name/'snapshots.jsonl'
        for row in map(json.loads,f.read_text().splitlines()):visit(row,f)
        metadata.append(str(f)+'#completed_native_interaction_cohort')
    clean=[r for r in reserve if r['case_id'] not in exposed]
    out=root/'e68_clean_reserve_lock';out.mkdir(exist_ok=False)
    dest=out/'cases.jsonl';dest.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in clean))
    report={'status':'LOCKED_BEFORE_NEW_INFERENCE','reserve_worlds':120,'retained_worlds':len(clean),
        'goal_kinds':dict(collections.Counter(r['goal_kind'] for r in clean)),
        'exclusions':{cid:sorted(paths) for cid,paths in sorted(exposed.items())},
        'retained_case_ids':[r['case_id'] for r in clean],
        'scanned_trace_files':len(traces),'scanned_trace_bytes':scanned,'trace_paths':sorted(map(str,traces)),
        'metadata_paths':metadata,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'locked_dataset_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'model_calls':0,'scope':['No matching evidence in recorded local inference and associated source metadata.',
          'Not a claim about model pretraining or public LIGHT data contamination.',
          'Conservative manifest exclusions can include planned but unexecuted rows.',
          'Same original split/order; no outcome-based selection.']}
    (out/'exposure.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','retained_worlds','goal_kinds','scanned_trace_files','scanned_trace_bytes']}),flush=True)


if __name__=='__main__':main()
