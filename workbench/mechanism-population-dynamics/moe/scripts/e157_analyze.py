"""CPU-only E157 paired analysis, including frozen E156 references."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'results'/'e157'
SEED=157001
GROUPS=('Bio','Math'); DONORS=('A','B'); SHARED=('P','A','B'); SOURCES=('P','A','B')


def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def logsoftmax(x):
    x=np.asarray(x,dtype=np.float64); z=x-x.max(-1,keepdims=True)
    return z-np.log(np.exp(z).sum(-1,keepdims=True))


def metrics(ll,gold,tokens,chars,kl):
    q=np.arange(len(gold)); ll=np.asarray(ll,dtype=float)
    return {'raw_accuracy':(ll.argmax(-1)==gold).astype(float),
            'per_char_accuracy':((ll/chars).argmax(-1)==gold).astype(float),
            'choice_CE':-logsoftmax(ll)[...,q,gold],
            'true_answer_token_NLL':-ll[...,q,gold]/tokens[q,gold],
            'first_answer_token_KL_vs_P':np.asarray(kl,dtype=float)}


def stats(x,subject,selection):
    x=np.asarray(x,dtype=float)
    if x.shape!=(128,) or subject.shape!=(128,) or selection.shape!=(128,): raise ValueError('Expected 128 paired values')
    rng=np.random.default_rng(SEED); draws=[]; means=[]; details={}
    for i,name in enumerate(('high_school_biology','high_school_mathematics')):
        v=x[selection & (subject==i)]
        if len(v)==0: raise ValueError('Each subject must be present')
        b=v[rng.integers(0,len(v),(1000,len(v)))].mean(1)
        means.append(v.mean()); draws.append(b)
        details[name]={'point':float(v.mean()),'question_ci95':np.quantile(b,[.025,.975]).tolist(),'questions':len(v)}
    return {'point':float(np.mean(means)),'question_ci95':np.quantile(np.mean(draws,axis=0),[.025,.975]).tolist(),
            'per_subject':details,'question_count':int(selection.sum()),'bootstrap_seed':SEED,
            'unit':'paired questions within fixed subjects, equal macro; not model or subject population'}


def compose(x,subject,on=True):
    """Select group index per question, regardless of held performance."""
    if x.shape[0]!=2 or x.shape[-1]!=len(subject): raise ValueError('Expected group axis and question axis')
    idx=subject if on else 1-subject
    return np.take_along_axis(x,idx.reshape((1,)+(1,)*(x.ndim-2)+(len(subject),)),axis=0)[0]


def contrast(x,accuracy=False):
    # donor axis A/B; shared axis P/A/B. Off-source minus same-source loss.
    v=(x[0,2]+x[1,1]-x[0,1]-x[1,2])/2
    return -v if accuracy else v


def check_raw(new,old):
    shapes={'candidate_loglikelihood':(2,2,3,128,4),'first_answer_token_KL_vs_P':(2,2,3,128),
            'native_candidate_loglikelihood':(3,128,4),'native_first_answer_token_KL_vs_P':(3,128),
            'gold':(128,),'subject':(128,),'answer_tokens':(128,4),'answer_chars':(128,4),
            'common_success':(128,),'group_names':(2,),'donor_names':(2,),'shared_names':(3,)}
    for k,shape in shapes.items():
        if k not in new or new[k].shape!=shape: raise ValueError(f'Unexpected or missing E157 field {k}')
    oldshapes={'candidate_loglikelihood':(3,3,2,128,4),'first_answer_token_KL_vs_P':(3,3,2,128),
               'native_candidate_loglikelihood':(3,2,128,4),'native_first_answer_token_KL_vs_P':(3,2,128),
               'source_names':(3,),'policies':(2,)}
    for k,shape in oldshapes.items():
        if k not in old or old[k].shape!=shape: raise ValueError(f'Unexpected or missing E156 field {k}')
    if tuple(new['group_names'])!=GROUPS or tuple(new['donor_names'])!=DONORS or tuple(new['shared_names'])!=SHARED: raise ValueError('E157 source order mismatch')
    if tuple(old['source_names'])!=SOURCES or tuple(old['policies'])!=('full','receiverP32'): raise ValueError('E156 source order mismatch')
    for k in ('gold','subject','answer_tokens','answer_chars','common_success'):
        if k not in old or not np.array_equal(new[k],old[k]): raise ValueError(f'Inputs differ: {k}')
    for k in ('gold','subject','answer_tokens','answer_chars'):
        if new[k].dtype.kind not in 'iu': raise ValueError(f'Expected integer {k}')
    if new['common_success'].dtype.kind!='b' or np.bincount(new['subject'],minlength=2).tolist()!=[64,64]: raise ValueError('Unexpected mask or subjects')
    if [int((new['common_success']&(new['subject']==i)).sum()) for i in (0,1)]!=[36,8]: raise ValueError('Common-success counts differ')
    if np.any((new['gold']<0)|(new['gold']>3)) or np.any(new['answer_tokens']<=0) or np.any(new['answer_chars']<=0): raise ValueError('Invalid labels/lengths')
    for arrays,keys in [(new,('candidate_loglikelihood','first_answer_token_KL_vs_P','native_candidate_loglikelihood','native_first_answer_token_KL_vs_P')),
                        (old,('candidate_loglikelihood','first_answer_token_KL_vs_P','native_candidate_loglikelihood','native_first_answer_token_KL_vs_P'))]:
        for k in keys:
            if not np.isfinite(arrays[k]).all(): raise ValueError(f'Nonfinite {k}')
    if not np.array_equal(new['native_candidate_loglikelihood'],old['native_candidate_loglikelihood'][:,0]): raise ValueError('E157 native full replay differs from E156')


def analyze():
    plan=json.loads((ROOT/'plan.json').read_text()); manifest=json.loads((ROOT/'manifest.json').read_text()); budget=json.loads((ROOT/'budget.json').read_text())
    if manifest.get('status')!='complete' or not budget.get('attempts') or any(x.get('status')!='complete' for x in budget['attempts']): raise ValueError('Complete manifest and budget required')
    if manifest.get('plan_sha256')!=sha(ROOT/'plan.json'): raise ValueError('Plan hash differs')
    if manifest.get('source_sha256',{}).get(Path(__file__).name)!=sha(__file__): raise ValueError('Frozen analysis source differs')
    npth=Path(manifest['raw']['path']); opth=Path(plan['previous_raw']['path'])
    if sha(npth)!=manifest['raw']['sha256'] or sha(opth)!=plan['previous_raw']['sha256']: raise ValueError('Raw hash mismatch')
    with np.load(npth,allow_pickle=False) as f: new={k:f[k].copy() for k in f.files}
    with np.load(opth,allow_pickle=False) as f: old={k:f[k].copy() for k in f.files}
    check_raw(new,old); gold=new['gold']; tokens=new['answer_tokens']; chars=new['answer_chars']; sub=new['subject']
    part=metrics(new['candidate_loglikelihood'],gold,tokens,chars,new['first_answer_token_KL_vs_P'])
    full=metrics(old['candidate_loglikelihood'][:,:,0],gold,tokens,chars,old['first_answer_token_KL_vs_P'][:,:,0])
    masked=metrics(old['candidate_loglikelihood'][:,:,1],gold,tokens,chars,old['first_answer_token_KL_vs_P'][:,:,1])
    native=metrics(new['native_candidate_loglikelihood'],gold,tokens,chars,new['native_first_answer_token_KL_vs_P'])
    result={'experiment':'E157','status':'complete','raw_sha256':manifest['raw']['sha256'],
            'previous_raw_sha256':plan['previous_raw']['sha256'],'plan_sha256':sha(ROOT/'plan.json'),
            'analysis_source_sha256':sha(__file__),'group_order':list(GROUPS),'donor_order':list(DONORS),'shared_order':list(SHARED),
            'definitions':{'cell_comparison':'partial minus reference','contrast':'A/B off-source minus same-source for losses, reverse for accuracy; PP excluded',
                'contrast_delta':'partial pairing contrast minus E156 whole-bank pairing contrast',
                'inherited_on_domain_masked':'E156 donor/S receiverP32; inherited, not new E157 measurement',
                'off_domain_masked':'not measured; omitted','on_off':'group fixed by question subject or opposite, never by outcomes'},'scopes':{}}
    for scope,sel in [('all_questions',np.ones(128,bool)),('common_native_success',new['common_success'])]:
        stat=lambda x:stats(x,sub,sel)
        row={'native_full':{s:{k:stat(v[i]) for k,v in native.items()} for i,s in enumerate(SOURCES)},'views':{}}
        for view in ('Bio','Math','on_domain','off_domain'):
            values={k:(v[GROUPS.index(view)] if view in GROUPS else compose(v,sub,view=='on_domain')) for k,v in part.items()}
            cells={}
            for i,donor in enumerate(DONORS):
                for j,s in enumerate(SHARED):
                    cells[donor+s]={'absolute':{},'minus_PP_full':{},'minus_same_S_P_R_full':{},'minus_whole_bank_full':{}}
                    for k,v in values.items():
                        x=v[i,j]; cells[donor+s]['absolute'][k]=stat(x)
                        cells[donor+s]['minus_PP_full'][k]=stat(x-full[k][0,0])
                        cells[donor+s]['minus_same_S_P_R_full'][k]=stat(x-full[k][0,j])
                        cells[donor+s]['minus_whole_bank_full'][k]=stat(x-full[k][i+1,j])
                    if view=='on_domain': cells[donor+s]['inherited_E156_receiverP32']={k:stat(v[i+1,j]) for k,v in masked.items()}
            pairing={}; pairing_delta={}; whole_pairing={}
            for k,v in values.items():
                acc=k in ('raw_accuracy','per_char_accuracy'); p=contrast(v,acc); w=contrast(full[k][1:3],acc)
                pairing[k]=stat(p); whole_pairing[k]=stat(w); pairing_delta[k]=stat(p-w)
            row['views'][view]={'cells':cells,'AB_pairing_contrast':pairing,'E156_whole_bank_AB_pairing_contrast':whole_pairing,'partial_minus_whole_bank_pairing_contrast':pairing_delta}
        result['scopes'][scope]=row
    (ROOT/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    return ROOT/'summary.json'


def self_test():
    subject=np.array([0]*64+[1]*64); x=np.stack([np.zeros(128),np.ones(128)])
    assert np.array_equal(compose(x,subject),subject) and np.array_equal(compose(x,subject,False),1-subject)
    grid=np.arange(2*2*3*128).reshape(2,2,3,128)
    expected=np.stack([grid[subject[q],:,:,q] for q in range(128)],axis=-1)
    assert np.array_equal(compose(grid,subject),expected)
    a=np.zeros((2,3,128)); a[0,2]=4; a[1,1]=2; a[0,1]=1; a[1,2]=3
    assert np.all(contrast(a)==1) and np.all(contrast(a,True)==-1)
    g=np.zeros(128,dtype=int); lengths=np.ones((128,4),dtype=int); ll=np.tile([3.,0,0,0],(128,1))
    m=metrics(ll,g,lengths,lengths,np.zeros(128)); assert np.all(m['raw_accuracy']==1) and np.allclose(m['choice_CE'],np.log1p(3*np.exp(-3))) and np.all(m['true_answer_token_NLL']==-3)
    z=stats(np.r_[np.zeros(64),np.ones(64)],subject,np.ones(128,bool)); assert z['point']==.5 and z['question_ci95']==[.5,.5]
    return {'status':'passed','checks':['on_off_subject_axes','AB_pairing_sign','candidate_metrics','stratified_bootstrap']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('self-test','analyze'));args=p.parse_args()
    if args.mode=='self-test': print(json.dumps(self_test()))
    else: print(analyze())
