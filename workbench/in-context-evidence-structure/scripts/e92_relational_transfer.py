"""Relational criterion inference with ambiguous target-source examples; E92."""
import argparse
import copy
import hashlib
import itertools
import json
import platform
import random
import subprocess
import time
from pathlib import Path

WORDS = {'shared': ['negative', 'positive'], 'far': ['flag', 'pass']}
PHRASES = {
 'discovery': {
  'demo': [['The pizza was delicious','The noodles tasted excellent','The burger was perfectly cooked','The dessert was delightful'],
           ['The pizza was awful','The noodles tasted bad','The burger was badly burnt','The dessert tasted terrible'],
           ['The waiter was polite','The staff were attentive','The servers helped us promptly','The service was courteous'],
           ['The waiter was rude','The staff were careless','The servers ignored us','The service was discourteous']],
  'query': [['Our dinner tasted wonderful','The soup was tasty','The entree was superb','The meal was outstanding'],
            ['Our dinner tasted horrible','The soup was disgusting','The entree was awful','The meal was dreadful'],
            ['Our requests were handled kindly','The waitress treated us politely','The employees were considerate','The team served us attentively'],
            ['Our requests were handled rudely','The waitress treated us impolitely','The employees were inconsiderate','The team served us carelessly']]},
 'confirmation': {
  'demo': [['The curry was flavorful','The salad tasted fresh','The fish was deliciously prepared','The bread tasted lovely'],
           ['The curry was revolting','The salad tasted rotten','The fish was disgustingly prepared','The bread tasted foul'],
           ['The host greeted us warmly','The cashier was respectful','The waitress assisted us patiently','The team was welcoming'],
           ['The host greeted us nastily','The cashier was disrespectful','The waitress dismissed us impatiently','The team was hostile']],
  'query': [['I enjoyed the pasta','The stew tasted fantastic','The sandwich was delectable','The roast was excellent'],
            ['I disliked the pasta','The stew tasted nauseating','The sandwich was vile','The roast was terrible'],
            ['We received friendly assistance','The staff took excellent care of us','The waiter was thoughtful','The server was exceptionally helpful'],
            ['We received unfriendly treatment','The staff neglected us badly','The waiter was insulting','The server was exceptionally unhelpful']]}}


def contexts(n, seed, stage):
    rng = random.Random(seed); ps = PHRASES[stage]; out = []
    for i in range(n):
        food_first = bool(rng.randrange(2)); names = rng.sample(['Alice','Bob'],2)
        def text(f,s,pp):
            parts = [pp[0 if f>0 else 1],pp[2 if s>0 else 3]]
            if not food_first: parts.reverse()
            return '. '.join(parts)+'.'
        demos=[]
        for f,s in itertools.product((-1,1),repeat=2):
            fp=ps['demo'][0 if f>0 else 1]; sp=ps['demo'][2 if s>0 else 3]
            pairs=rng.sample(list(itertools.product(fp,sp)),6 if f==s else 2)
            for j,(ff,ss) in enumerate(pairs):
                role=0 if f==s and j<4 else 1
                pp=[ff,ff,ss,ss]
                demos.append({'role':role,'food':f,'service':s,'text':text(f,s,pp)})
        rng.shuffle(demos)
        samples=[rng.sample(p,2) for p in ps['query']]; queries=[]
        for t in (0,1):
            pp=[v[t] for v in samples]
            for f,s in itertools.product((-1,1),repeat=2):
                queries.append({'food':f,'service':s,'text':text(f,s,pp),'template':t})
        out.append({'context':i,'names':names,'base_b_criterion':rng.randrange(2),'demos':demos,'queries':queries})
    return out


def design_audit(cs):
    totals={'relation_aware':0,'follow_b':0,'invert_b_when_different':0}; count=0
    for c in cs:
        assert len(c['demos'])==16 and len(c['queries'])==8
        assert not {d['text'] for d in c['demos']} & {q['text'] for q in c['queries']}
        a=[d for d in c['demos'] if d['role']==0]; b=[d for d in c['demos'] if d['role']==1]
        assert len(a)==len(b)==8 and all(d['food']==d['service'] for d in a)
        assert sum(d['food']>0 for d in a)==4
        assert [k for k in (0,1) if all((d['food'],d['service'])[k]==d['food'] for d in a)]==[0,1]
        for cb in (0,1):
            # Allow either output polarity in B: concordant examples identify it.
            possible=[(k,p) for k in (0,1) for p in (-1,1)
                      if all(p*(d['food'],d['service'])[k]==(d['food'],d['service'])[cb] for d in b)]
            assert possible==[(cb,1)]
            assert sum((d['food'],d['service'])[cb]>0 for d in b)==4
            for rel in (0,1):
                ca=cb^rel
                possible_a=[k for k in (0,1) if all((d['food'],d['service'])[k]==d['food'] for d in a) and k==(cb^rel)]
                assert possible_a==[ca]
                for q in c['queries']:
                    f,s=q['food'],q['service']; target=(f,s)[ca]; bp=(f,s)[cb]
                    preds={'relation_aware':target,'follow_b':bp,'invert_b_when_different':bp*(-1 if rel else 1)}
                    for k,p in preds.items():totals[k]+=int(p==target)
                    count+=1
    return {'n_contexts':len(cs),'a_alone_criteria_per_context':2,'b_criterion_and_polarity_jointly_identifiable':True,
            'a_criterion_with_b_and_relationship_unique':True,'no_demo_query_overlap':True,
            'static_predictors_accuracy':{k:v/count for k,v in totals.items()},
            'note':'Design enumeration, not LLM evidence. Relation-aware retrieval remains compatible with perfect behavior.'}


def interval(v):
    import numpy as np
    v=np.asarray(v,dtype=float); ix=np.random.default_rng(920).integers(len(v),size=(10000,len(v)))
    return {'mean':float(v.mean()),'ci95':np.quantile(v[ix].mean(1),[.025,.975]).tolist(),'n_contexts':len(v)}


def analyze(dest):
    import numpy as np
    rows=[json.loads(x) for x in (dest/'behavior.jsonl').read_text().splitlines()]
    run=json.loads((dest/'run.json').read_text()); assert len(rows)==run['args']['n'] and run['numeric_max_error']<.001
    out={'conditions':{},'criterion_responses':{},'contrasts':{},'numeric_max_error':run['numeric_max_error']}
    ds=np.array([q['food']!=q['service'] for q in rows[0]['queries']]); ss={}
    for rel in ('same','different'):
        for ns in WORDS:
            for mode in ('native','gate','instruction'):
                name=f'{rel}_{ns}_{mode}'
                zz=[]
                for world in ('base','flip'):
                    key=f'{rel}_{ns}_{world}_{mode}'; zs=np.array([r['conditions'][key]['z'] for r in rows])
                    gs=np.array([r['gold'][f'{rel}_{world}'] for r in rows]); zz.append(zs)
                    top=np.array([r['conditions'][key]['argmax_class'] for r in rows]); valid=top!=0
                    out['conditions'][key]={
                        'discordant_accuracy':interval(((zs[:,ds]>0)==(gs[:,ds]>0)).mean(1)),
                        'concordant_accuracy':interval(((zs[:,~ds]>0)==(gs[:,~ds]>0)).mean(1)),
                        'margin':interval((zs*gs).mean(1)),
                        'argmax_valid':interval(valid.mean(1)),
                        'argmax_accuracy':interval((top==gs).mean(1))}
                gb=np.array([r['gold'][f'{rel}_base'] for r in rows]); delta=zz[0]-zz[1]
                ss[name]=(delta[:,ds]*gb[:,ds]).mean(1)/2
                out['criterion_responses'][name]={'signed_response':interval(ss[name]),'context_responses':ss[name].tolist(),
                                                 'concordant_absolute_change':interval(np.abs(delta[:,~ds]).mean(1)),
                                                 'mean_bias_change':interval(delta.mean(1))}
        for mode in ('native','gate','instruction'):
            out['contrasts'][f'{rel}_{mode}_far_minus_shared']=interval(ss[f'{rel}_far_{mode}']-ss[f'{rel}_shared_{mode}'])
        for ns in WORDS:
            for mode in ('gate','instruction'):
                out['contrasts'][f'{rel}_{ns}_{mode}_minus_native']=interval(ss[f'{rel}_{ns}_{mode}']-ss[f'{rel}_{ns}_native'])
    for k in rows[0]['conditions']:
        if not k.startswith(('oracle_','probe_','single_')):continue
        source='B' if k.startswith('probe_') else 'A'
        vals=[]; av=[]
        for r in rows:
            if k.startswith('oracle_'): _,rel,world=k.split('_'); g=r['gold'][f'{rel}_{world}']
            elif k.startswith('probe_'): _,ns,world=k.split('_'); g=r['b_gold'][world]
            else:
                # Two indistinguishable worlds require complementary discordant answers.
                g=r['gold'][k.removeprefix('single_')+'_base']
            z=r['conditions'][k]['z']; top=r['conditions'][k]['argmax_class']
            vals.append(sum((z[i]>0)==(g[i]>0) for i,x in enumerate(ds) if x)/int(ds.sum()))
            av.append(sum(t!=0 for t in top)/len(top))
        out['conditions'][k]={'source':source,'discordant_base_accuracy':interval(vals),'argmax_valid':interval(av)}
    (dest/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
    for k,v in out['criterion_responses'].items():print(k,v['signed_response'],flush=True)
    for k,v in out['conditions'].items():
        if k.startswith(('oracle_','probe_','single_')):print(k,v,flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True)
    ap.add_argument('--model',default='/tmp/ices_models/Qwen3-8B');ap.add_argument('--n',type=int,default=16)
    ap.add_argument('--seed',type=int,default=92001);ap.add_argument('--stage',choices=list(PHRASES),default='discovery')
    ap.add_argument('--design-only',action='store_true');ap.add_argument('--analyze-only',action='store_true')
    args=ap.parse_args();dest=Path(args.out)
    if args.analyze_only:analyze(dest);return
    dest.mkdir(parents=True,exist_ok=True);assert not (dest/'behavior.jsonl').exists()
    cs=contexts(args.n,args.seed,args.stage); audit=design_audit(cs)
    (dest/'design_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    if args.design_only:print(json.dumps(audit,indent=2));return
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True);enc=lambda s:tok.encode(s,add_special_tokens=False)
    shell=tok.apply_chat_template([{'role':'system','content':'Infer the requested reviewer\'s criterion and label. Return exactly the requested label word.'},
                                   {'role':'user','content':'CONTENT_PLACEHOLDER'}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    lead,tail=shell.split('CONTENT_PLACEHOLDER');tail+='Answer:'
    ids_words={ns:[enc(' '+w)[0] for w in ws] for ns,ws in WORDS.items()}
    assert all(len(enc(' '+w))==1 for ws in WORDS.values() for w in ws)

    def prefix(c,rel,ns,world,oracle=False,instruction=False,single=False):
        cb=c['base_b_criterion']^(world=='flip'); ca=cb^(rel=='different'); na,nb=c['names']
        head=("Each reviewer judges only one aspect of a restaurant: food or service. A positive judgment means that aspect was good; a negative judgment means it was bad. "
              "Reviewers may use different label words, whose meanings can be inferred from their examples.\n"
              f"{na} and {nb} judge {'the same aspect' if rel=='same' else 'different aspects'}. Infer their criteria from the examples.\n\n")
        if oracle:head+=f"{na} judges only the {'food' if ca==0 else 'service'}.\n\n"
        if instruction:head+=f"Use {nb}'s examples and the stated relationship to resolve {na}'s otherwise ambiguous criterion.\n\n"
        text=lead+head; ids=enc(text); roles=[-1]*len(ids); anchors=[]
        for d in c['demos']:
            if single and d['role']==1:continue
            role=d['role']; sign=d['food'] if role==0 else (d['food'],d['service'])[cb]
            block=f"Reviewer: {c['names'][role]}\nReview: {d['text']}\nLabel:"
            pp=enc(block); anchors.append(len(ids)+len(pp)); word=WORDS[ns if role else 'shared'][int(sign>0)]
            block+=' '+word+'\n\n';part=enc(block)
            assert part[len(pp)]==ids_words[ns if role else 'shared'][int(sign>0)]
            ids+=part;roles += [role]*len(part);text+=block
        assert enc(text)==ids
        return ids,roles,text,anchors

    preflight={'args':vars(args),'words':ids_words,'native_chat_shell':shell,'a_raw_invariant':True,'world_changes_only_b_discordant_labels':True}
    for c in cs:
        for rel in ('same','different'):
            pairs={(ns,w):prefix(c,rel,ns,w) for ns in WORDS for w in ('base','flip')}
            ref,rr,_,aa=pairs['shared','base']; banchors={idx for idx,d in zip(aa,c['demos']) if d['role']==1}
            for ii,r,_,an in pairs.values():
                assert len(ii)==len(ref) and r==rr and an==aa
                assert {i for i,(x,y) in enumerate(zip(ii,ref)) if x!=y}<=banchors
    (dest/'preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
    import torch,transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6);torch.manual_seed(0);t0=time.time();print('Loading model',flush=True)
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,dtype=torch.float32,device_map='cuda',attn_implementation='eager').eval()
    model.requires_grad_(False);print('Model loaded',flush=True)
    def prefill(ids):return model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
    def query(cache,roles,qs,ns,gate=False):
        plen,n,w=len(roles),len(qs),max(map(len,qs)); ids=torch.zeros((n,w),dtype=torch.long,device='cuda');pos=torch.zeros_like(ids);live=torch.zeros_like(ids,dtype=torch.bool)
        for i,q in enumerate(qs):
            ids[i,-len(q):]=torch.tensor(q,device='cuda');pos[i,-len(q):]=torch.arange(plen,plen+len(q),device='cuda');live[i,-len(q):]=True
        keep=torch.tensor([r!=1 or not gate for r in roles],device='cuda',dtype=torch.bool)
        allowed=torch.cat([keep[None,None].expand(n,w,-1),live[:,None].expand(-1,w,-1)&torch.ones((w,w),dtype=torch.bool,device='cuda').tril()[None]],-1)
        mask=torch.zeros(allowed.shape,device='cuda',dtype=torch.float32).masked_fill_(~allowed,float('-inf'))
        cp=copy.deepcopy(cache);cp.batch_repeat_interleave(n)
        lo=model(input_ids=ids,position_ids=pos,attention_mask=mask[:,None],past_key_values=cp,use_cache=True,logits_to_keep=1).logits[:,-1].float()
        neg,positive=ids_words[ns];top=lo.argmax(-1)
        return {'z':(lo[:,positive]-lo[:,neg]).cpu().tolist(),'argmax_token':top.cpu().tolist(),
                'argmax_class':torch.where(top==positive,1,torch.where(top==neg,-1,0)).cpu().tolist()}
    errors=[]
    with torch.inference_mode(),(dest/'behavior.jsonl').open('w') as stream:
        for c in cs:
            qs=lambda role:[enc(f"Reviewer: {c['names'][role]}\nReview: {q['text']}\nGive this reviewer's label for the review.\n"+tail) for q in c['queries']]
            cond={}; gold={};bgold={}
            for rel in ('same','different'):
                for world in ('base','flip'):
                    cb=c['base_b_criterion']^(world=='flip');ca=cb^(rel=='different')
                    gold[f'{rel}_{world}']=[(q['food'],q['service'])[ca] for q in c['queries']]
                    bgold[world]=[(q['food'],q['service'])[cb] for q in c['queries']]
                    for ns in WORDS:
                        pi,rr,pt,_=prefix(c,rel,ns,world); cache=prefill(pi);qa=qs(0)
                        for mode in ('native','gate'):
                            key=f'{rel}_{ns}_{world}_{mode}';cond[key]=query(cache,rr,qa,'shared',mode=='gate')
                        if rel=='same':cond[f'probe_{ns}_{world}']=query(cache,rr,qs(1),ns)
                        ip,ir,_,_=prefix(c,rel,ns,world,instruction=True)
                        cond[f'{rel}_{ns}_{world}_instruction']=query(prefill(ip),ir,qa,'shared')
                        if c['context']==0 and rel=='same' and world=='base' and ns=='shared':
                            full=pi+qa[0];assert enc(pt+tok.decode(qa[0],skip_special_tokens=False))==full
                            lo=model(input_ids=torch.tensor([full],device='cuda'),use_cache=False,logits_to_keep=1).logits[0,-1]
                            errors.append(abs(float(lo[ids_words['shared'][1]]-lo[ids_words['shared'][0]])-cond[key.removesuffix('gate')+'native']['z'][0]))
                            assert max(errors)<.001
                    op,orr,_,_=prefix(c,rel,'shared',world,oracle=True)
                    cond[f'oracle_{rel}_{world}']=query(prefill(op),orr,qs(0),'shared')
                sp,sr,_,_=prefix(c,rel,'shared','base',single=True)
                cond[f'single_{rel}']=query(prefill(sp),sr,qs(0),'shared')
            stream.write(json.dumps({'context':c['context'],'queries':c['queries'],'gold':gold,'b_gold':bgold,'conditions':cond})+'\n');stream.flush()
            print(c['context']+1,'/',args.n,'numeric',max(errors),flush=True)
    elapsed=time.time()-t0
    run={'args':vars(args),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'contexts_sha256':hashlib.sha256((dest/'contexts.jsonl').read_bytes()).hexdigest(),
         'numeric_max_error':max(errors),'elapsed_seconds':elapsed,'gpu_hours':elapsed/3600,'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,
         'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'dtype':'float32','attention':'eager','query_gate':'all query positions including chat closing/answer prefix','training':False}
    (dest/'run.json').write_text(json.dumps(run,indent=2)+'\n');analyze(dest)


if __name__=='__main__':main()
