"""E53 all-row lossless representation types, preserving original raw hashes."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from lossless_role_format import normalize, checks
from speaker_listener_data import specs


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists();checks()
    models={}
    for cp,_,_ in specs(a.root):
        p=a.root/'runs'/('E49-speaker-listener-'+cp)/'predictions.jsonl'
        rows=[json.loads(l) for l in p.read_text().splitlines()];assert len(rows)==1080
        counts=Counter()
        for r in rows:
            if not r['terminated_by_eos']:key='not_eos'
            elif normalize(r['raw_text'],r['task']) is None:key='invalid_after_lossless_audit'
            else:
                text=r['raw_text'];fenced=re.fullmatch(r'\s*```(?:json)?[ \t]*\r?\n(.*?)\r?\n```\s*',text,re.DOTALL|re.IGNORECASE)
                value=json.loads(fenced.group(1) if fenced else text)
                kinds=sorted({type(v).__name__ for v in value})
                key=('fenced/' if fenced else 'json/')+'+'.join(kinds)
            counts[key]+=1
        assert sum(counts.values())==1080
        models[cp]={'n':1080,'representation_counts':dict(counts),'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    out={'experiment':'E53','post_hoc':True,'n':8640,'models':models,
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'normalizer_sha256':hashlib.sha256(Path(__file__).with_name('lossless_role_format.py').read_bytes()).hexdigest()}
    a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(models,indent=2))


if __name__=='__main__':main()
