"""POST-HOC paired shared-source contrasts; no new model execution or readouts."""
import hashlib
import json
from pathlib import Path
import numpy as np
import e157_analyze as core

ROOT=core.ROOT


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    manifest=json.loads((ROOT/'manifest.json').read_text()); ledger=json.loads((ROOT/'budget.json').read_text())
    assert manifest['status']=='complete' and all(a['status']=='complete' for a in ledger['attempts'])
    path=Path(manifest['raw']['path']); assert sha(path)==manifest['raw']['sha256']
    with np.load(path,allow_pickle=False) as f:a={k:f[k].copy() for k in f.files}
    metrics=core.metrics(a['candidate_loglikelihood'],a['gold'],a['answer_tokens'],a['answer_chars'],a['first_answer_token_KL_vs_P'])
    result={'experiment':'E157','status':'complete','label':'POST-HOC paired contrast implementation after viewing all source cells; original readouts and raw unchanged',
            'raw_sha256':manifest['raw']['sha256'],'analysis_source_sha256':sha(__file__),'direction':'same partial-R model with foreign S minus recipient S_P', 'scopes':{}}
    for scope,sel in [('all_questions',np.ones(128,bool)),('common_native_success',a['common_success'])]:
        views={}
        for view in ('Bio','Math','on_domain','off_domain'):
            v={k:(x[core.GROUPS.index(view)] if view in core.GROUPS else core.compose(x,a['subject'],view=='on_domain')) for k,x in metrics.items()}
            views[view]={r+s+'_minus_'+r+'P':{k:core.stats(x[i,j]-x[i,0],a['subject'],sel) for k,x in v.items()}
                         for i,r in enumerate(core.DONORS) for j,s in [(1,'A'),(2,'B')]}
        result['scopes'][scope]=views
    target=ROOT/'shared_source_effects_posthoc.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for key,stats in result['scopes']['all_questions']['on_domain'].items():
        r=stats['true_answer_token_NLL'];print(key,r['point'],r['question_ci95'])


if __name__=='__main__':main()
