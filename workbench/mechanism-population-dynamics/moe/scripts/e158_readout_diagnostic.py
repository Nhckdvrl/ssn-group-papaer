"""POST-HOC native within-class rank ceiling; original E158 readouts unchanged."""
from pathlib import Path
import hashlib,json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'results/e158/whole_path'


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    manifest=json.loads((ROOT/'manifest.json').read_text());plan=json.loads((ROOT/'plan.json').read_text())
    if manifest['status']!='complete' or sha(manifest['raw']['path'])!=manifest['raw']['sha256'] or sha(plan['data']['path'])!=plan['data']['sha256']:
        raise ValueError('Sealed raw/data required')
    with np.load(plan['data']['path'],allow_pickle=False) as f:d={k:f[k].copy() for k in f.files}
    with np.load(manifest['raw']['path'],allow_pickle=False) as f:a={k:f[k].copy() for k in f.files}
    index={int(t):i for i,t in enumerate(d['token_union'])}
    out={'status':'POST_HOC_complete','raw_sha256':manifest['raw']['sha256'],'analysis_source_sha256':sha(__file__),
      'definition':'Native gold token for the unasked relation: its rank within all canonical first-token answers of that relation before interchange; diagnostic only, original statistics unchanged.', 'models':{}}
    for m,name in enumerate(('P','A','B')):
        rows=[]
        for r in range(2):
            candidates=[index[int(t)] for t in d['range_token_ids'][1-r,:int(d['range_count'][1-r])]]
            correct=[];wins=[]
            for c in range(24):
                target=int(d['target_query_index'][r,c]);source=int(d['source_query_index'][1,r,c])
                token=index[int(d['gold_token'][source])];lp=a['native_lp_selected'][m,target];other=[i for i in candidates if i!=token]
                correct.append(bool(lp[token]>=max(lp[candidates])))
                wins.append(float(((lp[token]>lp[other])+.5*(lp[token]==lp[other])).mean()))
            rows.append({'target_relation':r,'correct_unasked_answer_top_within_its_relation':sum(correct),'questions':24,'mean_win_fraction':float(np.mean(wins))})
        out['models'][name]=rows
    (ROOT/'readout_diagnostic.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out,ensure_ascii=False))


if __name__=='__main__':main()
