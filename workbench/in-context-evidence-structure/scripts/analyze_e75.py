"""Native function-family validity, all sampled replies included."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory');a=ap.parse_args();d=Path(a.directory)
    run=json.loads((d/'run.json').read_text());n=run['args']['n']
    rows=[json.loads(l) for l in (d/'generations.jsonl').read_text().splitlines()]
    assert len(rows)==6*n and len({r['uid'] for r in rows})==len(rows)
    out={'run':run,'conditions':{},'limitations':['New seed, same identities and vocabulary; interface pilot, not independent mechanism confirmation.',
        'One sampled reply per query; context-only bootstrap.','Thinking text is not evidence of faithful computation.']}
    for condition in ['full.bijective','held.bijective','held.independent']:
        rs=sorted([r for r in rows if r['condition']==condition],key=lambda r:(r['context'],r['source']));assert len(rs)==2*n
        vals={'accuracy':[r['prediction']==r['gold'] for r in rs],'strict_accuracy':[r['strict_prediction']==r['gold'] for r in rs],
            'valid_format':[r['prediction']>=0 for r in rs],'truncated':[r['truncated'] for r in rs],
            'unknown':[r['prediction']==3 for r in rs],'tokens':[r['tokens'] for r in rs]}
        out['conditions'][condition]={name:interval(np.array(v).reshape(n,2).mean(1),seed=750,nboot=4000) for name,v in vals.items()}
        out['conditions'][condition]['source_accuracy']={str(s):interval(np.array([r['prediction']==r['gold'] for r in rs if r['source']==s]),seed=750,nboot=4000) for s in [0,1]}
    (d/'analysis.json').write_text(json.dumps(out,indent=2));print(out['conditions'])


if __name__=='__main__':main()
