"""Complete E53 role map with input-defined MVRR correction, preserving original audits."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from data import sha,write_jsonl


def source_text(row):
    return row['sentence'].split('\n\nPARAPHRASE:\n',1)[0].removeprefix('SOURCE:\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args();root=args.root
    script=Path(__file__).parent;old=root/'T4-full-native-v2';start=time.monotonic()
    while not (old/'step5/summary.json').exists():
        if time.monotonic()-start>86400:raise RuntimeError('Original E53 full audit unfinished; inspect request/cache logs.')
        time.sleep(10)
    assert json.loads((old/'step5/summary.json').read_text())['complete']
    data=root/'sentences.jsonl';sources=[json.loads(l) for l in data.read_text().splitlines()]
    mvrr={r['sentence'] for r in sources if r['construction']=='MVRR'}
    labels={};removed=0;failed=0;provenance=[]
    for directory in [old,root/'T4-instrument-v2']:
        path=directory/'step5/annotated.jsonl';provenance.append(dict(path=str(directory),sha256=sha(path)))
        for row in map(json.loads,path.read_text().splitlines()):
            if source_text(row) in mvrr:removed+=1;continue
            if row.get('step5_status') not in ('agreed','adjudicated'):failed+=1;continue
            assert row['item_id'] not in labels;labels[row['item_id']]=row
    # Reuse identical corrected MVRR packets if the E63/E64 corrected panel has finished.
    corrected=root.parent/'E64/T4-full-v2'
    if (corrected/'step5/summary.json').exists():
        path=corrected/'step5/annotated.jsonl';provenance.append(dict(path=str(corrected),sha256=sha(path)))
        for row in map(json.loads,path.read_text().splitlines()):
            if source_text(row) in mvrr and row.get('step5_status') in ('agreed','adjudicated'):
                assert row['item_id'] not in labels;labels[row['item_id']]=row
    legacy=root/'legacy-role-v2-input';(legacy/'step5').mkdir(parents=True,exist_ok=True)
    write_jsonl(legacy/'step5/annotated.jsonl',[labels[k] for k in sorted(labels)])
    (legacy/'step5/summary.json').write_text(json.dumps(dict(complete=True,retained=len(labels),removed_old_MVRR=removed,retry_unresolved=failed))+'\n')
    (legacy/'scope.json').write_text(json.dumps(dict(provenance=provenance,policy='Old completed non-MVRR retained by input construction, corrected MVRR only from completed role-v2; unresolved packets retried. No class/outcome selection.'),indent=2)+'\n')
    runs=[root/'runs/Qwen3-8B-paraphrase',root/'runs-native-v2/gemma-3-12b-it-paraphrase',root/'runs-native-v2/Meta-Llama-3.1-8B-Instruct-paraphrase']
    audit=root/'T4-role-v2-complete'
    subprocess.run([sys.executable,str(script/'audit_paraphrases_role_v2.py'),'--data',str(data),'--runs',*map(str,runs),'--out',str(audit),
        '--workers','4','--previous-audits',str(legacy)],check=True)
    out=root/'paraphrase-map-role-v2.json'
    subprocess.run([sys.executable,str(script/'analyze_paraphrases.py'),'--metadata',str(root.parent/'E52/qualified-v3.jsonl'),'--data',str(data),
        '--runs',*map(str,runs),'--audits',str(audit),str(legacy),'--out',str(out)],check=True)
    (root/'complete-role-map-v2.json').write_text(json.dumps(dict(path=str(out),sha256=sha(out),scope='Fixed complete E53 model/format/reading panel; corrected MVRR role protocol, original labels/output preserved.'),indent=2)+'\n')
    print('E53 complete corrected role map ready',out,flush=True)


if __name__=='__main__':main()
