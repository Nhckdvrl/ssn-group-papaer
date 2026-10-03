import argparse,hashlib,json,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from qwen14_readout import prepare,fingerprint

ap=argparse.ArgumentParser()
for k in ['root','model','output']:ap.add_argument('--'+k,type=Path,required=True)
for k in ['model-id','revision']:ap.add_argument('--'+k,required=True)
ap.add_argument('--task',choices=['hu-bare','hu-chat','implicaturex'],required=True)
a=ap.parse_args();assert not a.output.exists()
tok=AutoTokenizer.from_pretrained(a.root/'models/Qwen2.5-14B-Instruct',local_files_only=True)
rows=prepare(a.root,tok,a.task)
preflight=json.loads(Path('workbench/pragmatic-inference-calibration/results/E41-prefix-preflight.json').read_text())
assert fingerprint(rows)==preflight[a.task]['input_token_hash'] and len(rows)==preflight[a.task]['n']
a.output.mkdir(parents=True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
start=time.monotonic()
@torch.inference_mode()
def read(p):
    ids=p['input_ids'];h=model.model(input_ids=torch.tensor([ids],device=model.device),use_cache=False).last_hidden_state[0]
    logits=model.lm_head(h[-1]).float();chosen=logits[p['candidate_ids']]
    shared_lp=0.
    for i in range(p['original_prefix_length'],len(ids)):
        shared_lp+=float(model.lm_head(h[i-1]).float().log_softmax(-1)[ids[i]])
    conditional_mass=float((chosen.logsumexp(-1)-logits.logsumexp(-1)).exp())
    return {'label_probs':chosen.softmax(-1).cpu().tolist(),
        'full_choice_content_logprobs':(chosen.log_softmax(0)+chosen.logsumexp(-1)-logits.logsumexp(-1)+shared_lp).cpu().tolist(),
        'conditional_candidate_mass':conditional_mass,'support_mass':conditional_mass*__import__('math').exp(shared_lp),
        'generated_common_prefix_logprob':shared_lp,'global_argmax_is_candidate':int(logits.argmax()) in p['candidate_ids']}
controls=[]
for i in [0,len(rows)-1]:
    p=rows[i]['plan'];x,y=read(p),read(p);delta=max(abs(u-v) for u,v in zip(x['label_probs'],y['label_probs']))
    # Independent teacher-forced complete candidate scoring checks the exact
    # factorization, including the probability of the generated shared prefix.
    direct=[]
    with torch.inference_mode():
        for full in p['full_choice_ids']:
            h=model.model(input_ids=torch.tensor([full[:-1]],device=model.device),use_cache=False).last_hidden_state[0]
            lp=0.
            for j in range(p['original_prefix_length'],len(full)):
                lp+=float(model.lm_head(h[j-1]).float().log_softmax(-1)[full[j]])
            direct.append(lp)
    lp_delta=max(abs(u-v) for u,v in zip(direct,x['full_choice_content_logprobs']))
    direct_probs=torch.tensor(direct).softmax(0).tolist()
    prob_delta=max(abs(u-v) for u,v in zip(direct_probs,x['label_probs']))
    same_argmax=max(range(len(direct)),key=lambda j:direct[j])==max(range(len(direct_probs)),key=lambda j:x['label_probs'][j])
    controls.append({'index':i,'single_repeat_delta':delta,'direct_full_content_lp_delta':lp_delta,
        'direct_probability_delta':prob_delta,'direct_argmax_agrees':same_argmax,
        'pass':delta<1e-6 and lp_delta<.001 and prob_delta<.001 and same_argmax})
(a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2));assert all(c['pass'] for c in controls)
config={'task':'qwen25_strong_parent_'+a.task,'model':a.model_id,'revision':a.revision,'dtype':'float32','batch_size':1,
    'n':len(rows),'input_token_hash':fingerprint(rows),'numerical_gate_pass':True,
    'common_tokenizer':str(a.root/'models/Qwen2.5-14B-Instruct'),
    'readout':'full numeric option content likelihood; exact shared generated prefix factored out; no EOS',
    'bare_bos':False,'original_isolated_numeric_labels_two_tokens':False,
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'helper_sha256':hashlib.sha256(Path(__file__).with_name('qwen14_readout.py').read_bytes()).hexdigest()}
(a.output/'config.json').write_text(json.dumps(config,indent=2))
with (a.output/'predictions.jsonl').open('w') as f:
    for i,r in enumerate(rows):
        z=read(r['plan']);p=r['plan'];s=r['source'];record={k:v for k,v in r.items() if k not in ['plan','source']}
        record.update({k:v for k,v in s.items() if k not in ['prompt','system_prompt']})
        probs=dict(zip(p['choices'],z['label_probs']));prediction=max(probs,key=probs.get)
        record.update(z,prompt_sha256=p['prompt_sha256'],prediction=prediction,full_choice_ids=p['full_choice_ids'],
            generated_common_prefix_ids=p['generated_common_prefix_ids'],numeric_choice_probs=probs)
        if a.task.startswith('hu'):record.update(correct=prediction==s['gold'],prob_true_answer=probs[s['gold']])
        elif a.task=='circa':record.update(choice_probs=dict(zip(r['options'],z['label_probs'])))
        else:record.update(p_true=probs[s['true_label']])
        f.write(json.dumps(record,ensure_ascii=False)+'\n');f.flush()
        if i%100==0:print(json.dumps({'done':i+1,'total':len(rows)}),flush=True)
config.update(complete=True,wall_seconds=time.monotonic()-start)
(a.output/'config.json').write_text(json.dumps(config,indent=2));print(json.dumps({'complete':True,'n':len(rows)}),flush=True)
