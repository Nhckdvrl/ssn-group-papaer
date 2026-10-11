"""POST-HOC 2x2 interaction; not an independently validated new claim."""
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval

for d in [Path('results/e70/qwen3_discovery'),Path('results/e70/qwen3_confirmation')]:
    rows=[json.loads(l) for l in (d/'behavior.jsonl').read_text().splitlines()]
    g=np.array([r['signs'] for r in rows]);half=g.shape[1]//2
    raw={k:np.array([r['scores'][k] for r in rows]) for k in ['isolated','common','centered','both']}
    margin={k:(v*g).mean(1) for k,v in raw.items()};acc={k:(v*g>0).mean(1) for k,v in raw.items()}
    rank={k:((v[:,:half]-v[:,half:])*g[:,:half]>0).mean(1) for k,v in raw.items()}
    out={'post_hoc':True,'independent_validation_required':True,'definition':'both - common - centered + isolated',
         'interaction':{name:interval(v['both']-v['common']-v['centered']+v['isolated']) for name,v in [('margin',margin),('accuracy',acc),('paired_source_ranking',rank)]}}
    (d/'interaction_posthoc.json').write_text(json.dumps(out,indent=2));print(d.name,out['interaction'])
