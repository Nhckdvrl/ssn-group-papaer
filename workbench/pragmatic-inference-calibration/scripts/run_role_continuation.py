import argparse,hashlib,json,time,math
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from role_continuation_data import prepare,fingerprint,tokenizer_path

ap=argparse.ArgumentParser()
for k in ['root','model','output']:ap.add_argument('--'+k,type=Path,required=True)
for k in ['model-id','revision']:ap.add_argument('--'+k,required=True)
a=ap.parse_args();assert not a.output.exists();a.output.mkdir(parents=True)
tok=AutoTokenizer.from_pretrained(tokenizer_path(a.root,a.model.name),local_files_only=True)
rows,audit=prepare(a.root,tok)
pre=json.loads((Path(__file__).resolve().parents[1]/'results/E50-source-preflight.json').read_text())
sha=lambda name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
assert pre['gate_pass'] and pre['source_audit']==audit and pre['models'][a.model.name]['input_token_sha256']==fingerprint(rows)
assert pre['helper_sha256']==sha('role_continuation_data.py') and pre['original_dependency_sha256']==sha('speaker_listener_data.py')
torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').eval().to('cuda')
start=time.monotonic()
@torch.inference_mode()
def score(p,which,batch):
    sequences=p[which+'_ids'];begin=len(p['prefix_ids']);result=[]
    for offset in range(0,len(sequences),batch):
        seqs=sequences[offset:offset+batch];width=max(len(s) for s in seqs)
        x=torch.full((len(seqs),width),tok.pad_token_id or tok.eos_token_id,device='cuda',dtype=torch.long)
        mask=torch.zeros_like(x)
        for i,s in enumerate(seqs):x[i,:len(s)]=torch.tensor(s,device='cuda');mask[i,:len(s)]=1
        h=model.model(input_ids=x,attention_mask=mask,use_cache=False).last_hidden_state
        for i,s in enumerate(seqs):
            logits=model.lm_head(h[i,begin-1:len(s)-1]).float().log_softmax(-1)
            targets=torch.tensor(s[begin:],device='cuda')
            result.append(float(logits.gather(-1,targets[:,None]).sum()))
    return result

def read(p,batch=4):
    out={}
    for which in ['full','content']:
        lp=score(p,which,batch);pvec=torch.tensor(lp,dtype=torch.float64).softmax(0).tolist()
        out[which]={'logprobs':lp,'conditional_probs':pvec,'candidate_mass':sum(math.exp(x) for x in lp),'argmax':max(range(len(lp)),key=lambda j:lp[j])}
    return out

@torch.inference_mode()
def independent(p):
    out={};begin=len(p['prefix_ids'])
    for which in ['full','content']:
        lp=[]
        for seq in p[which+'_ids']:
            logits=model(input_ids=torch.tensor([seq[:-1]],device='cuda'),
                attention_mask=torch.ones((1,len(seq)-1),device='cuda',dtype=torch.long),use_cache=False).logits[0].float()
            target=torch.tensor(seq[begin:],device='cuda')
            values=logits[begin-1:].log_softmax(-1).gather(-1,target[:,None])
            lp.append(float(values.sum()))
        out[which]={'logprobs':lp,'conditional_probs':torch.tensor(lp,dtype=torch.float64).softmax(0).tolist(),
            'argmax':max(range(len(lp)),key=lambda j:lp[j])}
    return out

control_indices=[]
for interface in ['bare','common-chat']:
    for task in ['listener','speaker']:
        group=[i for i,r in enumerate(rows) if r['interface']==interface and r['row']['task']==task]
        control_indices.extend([group[0],group[-1]])
controls=[]
for i in control_indices:
    p=rows[i]['plan'];x,y,z=read(p),read(p),independent(p)
    repeat=max(abs(u-v) for w in x for u,v in zip(x[w]['logprobs'],y[w]['logprobs']))
    delta=max(abs(u-v) for w in x for u,v in zip(x[w]['logprobs'],z[w]['logprobs']))
    prob=max(abs(u-v) for w in x for u,v in zip(x[w]['conditional_probs'],z[w]['conditional_probs']))
    same=all(x[w]['argmax']==z[w]['argmax'] for w in x)
    controls.append({'index':i,'id':rows[i]['row']['id'],'interface':rows[i]['interface'],
        'repeat_delta':repeat,'independent_single_full_lp_delta':delta,'probability_delta':prob,'argmax_agrees':same,
        'pass':repeat<1e-6 and delta<.001 and prob<.001 and same})
(a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2));assert all(z['pass'] for z in controls)
config={'model':a.model_id,'revision':a.revision,'dtype':'float32','n':len(rows),'candidate_batch_size':4,'source_audit':audit,
    'input_token_sha256':fingerprint(rows),'numerical_gate_pass':True,'primary':'full period-completed continuation content, no EOS',
    'script_sha256':sha('run_role_continuation.py'),'helper_sha256':sha('role_continuation_data.py'),
    'original_dependency_sha256':sha('speaker_listener_data.py')}
(a.output/'config.json').write_text(json.dumps(config,indent=2))
with (a.output/'predictions.jsonl').open('w') as f:
    for i,r in enumerate(rows):
        out={k:v for k,v in r['row'].items() if k not in ['prompt','human_norm']}
        out.update(read(r['plan']),interface=r['interface'],plan=r['plan'])
        f.write(json.dumps(out,ensure_ascii=False)+'\n');f.flush()
        if i%40==0:print(json.dumps({'done':i+1,'total':len(rows)}),flush=True)
config.update(complete=True,wall_seconds=time.monotonic()-start);(a.output/'config.json').write_text(json.dumps(config,indent=2))
print(json.dumps({'complete':True,'n':len(rows)}),flush=True)
