#!/usr/bin/env python3
"""Consolidate E74–E76 costs and source units without pooling dependent outcomes."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--runs-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();costs={};hashes={}
    for exp in ['E74','E75','E76']:
        p=a.results/(exp+'_cost_accounting.json');costs[exp]=json.loads(p.read_text())
        assert costs[exp]['status']=='COMPLETE' and costs[exp]['new_cloud_calls']==0
        hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    totals={k:sum(c['totals'].get(k,0) for c in costs.values()) for k in
            ['calls','parse_errors','prompt_tokens','completion_tokens','stage_conv','stage_effects','stage_exec']}
    totals['observed_slot_gpu_hours']=sum(c['totals']['observed_slot_hours'] for c in costs.values())
    totals['model_load_and_inference_gpu_hours']=sum(c['totals'].get('load_and_inference_gpu_hours',
        c['totals'].get('model_load_and_inference_gpu_hours',0)) for c in costs.values())
    sources={}
    for exp,folder in [('E74','e70_native_request_qualification'),('E75','e75_native_retrieval_qualification')]:
        p=a.runs_root/folder/'snapshots.jsonl';rs=list(map(json.loads,p.open()))
        sources[exp]={r['case']['graph_sha256']:hashlib.sha256(json.dumps(json.loads(r['case']['quest']['graph']),
            sort_keys=True,separators=(',',':')).encode()).hexdigest() for r in rs}
        hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    raw=set(sources['E74'])|set(sources['E75']);canonical=set(sources['E74'].values())|set(sources['E75'].values())
    result={'status':'COMPLETE','experiments':['E74','E75','E76'],'totals':totals,
            'unique_source_graphs_by_raw_json':len(raw),'unique_source_graphs_by_canonical_json':len(canonical),
            'E74_E75_source_overlap':len(set(sources['E74'])&set(sources['E75'])),
            'source_units':{'E74':len(sources['E74']),'E75':len(sources['E75']),'E76':len(sources['E75'])},
            'forecast_contexts':2808,'native_execution_branches':8928,'peak_gpus':4,'new_cloud_calls':0,
            'source_sha256':hashes,
            'scope':['Source graphs, branches, forecasts and actual calls are distinct units.',
                     'E76 reuses the E75 source set; no pooled independent replication claim.',
                     'Costs include profiles once and model startup/teardown; exact reused output is not an extra actual call.',
                     'No inference about latent ability or complete private utility follows from a source-task flag alone.']}
    a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
