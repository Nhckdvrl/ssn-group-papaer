#!/usr/bin/env python3
"""Finish only missing DATA labels after frozen high-reasoning truncations."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from step_plan_labels import call, MODEL, PLAN_URL

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True)
    ap.add_argument('--key-file',type=Path,required=True);a=ap.parse_args()
    public=json.loads((a.directory/'public_data.json').read_text())
    completed=json.loads((a.directory/'labels_collected.json').read_text())
    missing=[r for r in public if r['annotation_id'] not in completed];assert 0<len(missing)<=120
    out=a.directory/'recovery_medium64k';out.mkdir(exist_ok=False)
    (out/'manifest.json').write_text(json.dumps({'IDs':[r['annotation_id'] for r in missing],
        'selection':'only missing or schema-invalid IDs; no outcomes or persona/model labels exposed',
        'completed_labels_sha256':hashlib.sha256((a.directory/'labels_collected.json').read_bytes()).hexdigest(),
        'model':MODEL,'endpoint':PLAN_URL,'max_tokens':65536,'reasoning_effort':'medium',
        'cash_endpoint_calls':0,'npc_cloud_calls':0},indent=2)+'\n')
    key=a.key_file.read_text().strip()
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(call,i,missing[k:k+20],key,out,65536,'medium') for i,k in enumerate(range(0,len(missing),20))]
        for f in futures:f.result()

if __name__=='__main__':main()
