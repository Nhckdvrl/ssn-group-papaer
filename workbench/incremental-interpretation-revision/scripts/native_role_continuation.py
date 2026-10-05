"""E42 native assistant continuation NLL, with preserved E40 target sentences."""
import argparse
import collections
import json
from pathlib import Path
import re
import subprocess
import time
import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from data import CACHE, sha, write_jsonl
from event_identity import digest
from aspect_reference import read_run
from analyze_source_ablation import stat, diff

BASE = 'Continue the narrative with one sentence.'
SCOPE = 'For each activity, keep its stated participant description scoped to that activity.'


def prepare(data, model, mode, audit):
    report = json.loads(data.with_suffix('.audit.json').read_text())
    assert sha(data) == report['audited_sha256']
    ir = json.loads(audit.read_text())
    assert ir['model'] == 'gpt-6-luna' and ir['base']['faithful'] and ir['scope']['faithful']
    assert not any(ir['scope'][k] for k in ('chooses_new_patient','forces_equal_probability','denies_old_event'))
    assert ir['source_sha256'] == sha(audit.parent/'instruction-packets.json')
    tok = AutoTokenizer.from_pretrained(model, local_files_only=True, padding_side='left')
    tok.pad_token_id = tok.eos_token_id
    rows = list(map(json.loads, data.read_text().splitlines()))
    assert len(rows) == 1920
    groups, causal = {}, {}
    for r in rows:
        assert digest(r['sentence']) == r['sentence_sha256']
        words = list(re.finditer(r'\S+', r['sentence']))
        pos = words[r['authored_followup_start_word']].start()
        assert pos <= r['target_start_char'] < r['target_stop_char']
        prompt = tok.apply_chat_template([dict(role='system',content=BASE+(' '+SCOPE if mode=='scope' else '')),
                                         dict(role='user',content=r['sentence'][:pos].rstrip())],
                                        tokenize=False,add_generation_prompt=True,enable_thinking=False)
        text = prompt + r['sentence'][pos:]
        start = len(prompt)+r['target_start_char']-pos
        stop = len(prompt)+r['target_stop_char']-pos
        phrase = r['sentence'][r['target_start_char']:r['target_stop_char']]
        assert text[start:stop] == phrase and digest(phrase)==r['target_phrase_sha256']
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
        indices = [i for i,(a,b) in enumerate(enc['offset_mapping']) if a<stop and b>start and text[a:b].strip()]
        assert indices and min(indices)>0
        key = (r['pair_id'],r['fact_realization'],r['readout_actor_mode'],r.get('boundary_marker','old'),r['role_evidence'],r['readout_frame'])
        prefix_ids = enc['input_ids'][:min(indices)]
        if key in causal:
            assert causal[key] == prefix_ids
        causal[key] = prefix_ids
        groups[r['item_id']] = dict(ids=enc['input_ids'],indices=indices,native_prompt_sha256=digest(prompt),
                                   native_input_sha256=digest(text),native_pretarget_tokens_sha256=digest(json.dumps(prefix_ids)))
    assert len(causal)*2==len(rows)
    return tok, rows, groups


def run(args):
    assert not args.out.exists()
    tok,rows,groups=prepare(args.data,args.model,args.mode,args.audit)
    torch.manual_seed(0);torch.set_num_threads(8)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    args.out.mkdir(parents=True);start=time.time()
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='sdpa').to('cuda').eval()
    for p in model.parameters():p.requires_grad_(False)
    cfg=dict(experiment='E42',mode=args.mode,task_count=1920,model_manifest=json.loads((args.model/'manifest.json').read_text()),
             dtype='float32',tf32=False,attention='sdpa',seed=0,frozen=True,batch_size=4,thinking=False,
             data_sha256=sha(args.data),instruction_audit_sha256=sha(args.audit),code_sha256=sha(Path(__file__)),
             git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),torch=torch.__version__,transformers=transformers.__version__,
             gpu=torch.cuda.get_device_name(),system_instruction=BASE+(' '+SCOPE if args.mode=='scope' else ''),
             scoring='Teacher-forced original assistant continuation, target NP token NLL only; not free-generation accuracy.',target_causal_identity_verified=True)
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    keys=sorted(groups,key=lambda k:(len(groups[k]['ids']),k));scores={}
    with torch.inference_mode():
        for off in range(0,len(keys),4):
            kk=keys[off:off+4]
            inp=tok.pad([dict(input_ids=groups[k]['ids'],attention_mask=[1]*len(groups[k]['ids'])) for k in kk],return_tensors='pt').to('cuda')
            logits=model(**inp).logits[:,:-1,:].float();targets=inp['input_ids'][:,1:]
            bits=((logits.logsumexp(-1)-logits.gather(-1,targets.unsqueeze(-1)).squeeze(-1))/np.log(2))
            labels=torch.full_like(inp['input_ids'],-100)
            for i,k in enumerate(kk):
                pad=inp['input_ids'].shape[1]-len(groups[k]['ids']);indices=[pad+t for t in groups[k]['indices']]
                scores[k]=float(bits[i,[t-1 for t in indices]].sum().cpu())
                labels[i,indices]=inp['input_ids'][i,indices]
            if off==0:
                manual=sum(scores[k] for k in kk)/sum(len(groups[k]['indices']) for k in kk)*np.log(2)
                hf=float(model(**inp,labels=labels).loss.cpu());assert abs(manual-hf)<1e-4
                cfg['first_batch_target_loss_check']=dict(manual=manual,hf=hf)
            if off%128==0:print(f'{off+len(kk)}/1920 elapsed={time.time()-start:.1f}s',flush=True)
    out=[]
    for r in rows:
        g=groups[r['item_id']]
        nr={k:v for k,v in r.items() if k!='sentence'}
        nr.update(item_id='E42:'+args.mode+':'+r['item_id'],native_mode=args.mode,target_total_bits=scores[r['item_id']],
                  **{k:g[k] for k in ('native_prompt_sha256','native_input_sha256','native_pretarget_tokens_sha256')})
        out.append(nr)
    write_jsonl(args.out/'scores.jsonl',out);elapsed=time.time()-start
    cfg.update(scores_sha256=sha(args.out/'scores.jsonl'),wall_seconds=elapsed,gpu_hours=elapsed/3600,peak_gpu_bytes=torch.cuda.max_memory_allocated())
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')


def analyze(cache, out):
    parent=Path(__file__).resolve().parents[1]/'results/E40-summary.json'
    if not parent.exists():parent=parent.with_name('E40-raw-summary.json')
    pp=json.loads(parent.read_text())['probability']
    configs=[];allrows=[]
    for mode in ('base','scope'):
        c,rr=read_run(cache/'runs'/f'E42-{mode}');configs.append(c);allrows.extend(rr)
    for k in ('model_manifest','dtype','tf32','attention','seed','frozen','torch','transformers','data_sha256'):
        assert configs[0][k]==configs[1][k]
    result=dict(experiment='E42',configs=configs,bootstrap_unit='12 verb families, two sources averaged',bootstrap_draws=10000,
                bootstrap_seed=20261005,parent_summary_sha256=sha(parent),cells={},contrasts={},cohorts={},per_family={})
    conditions=sorted({(r['fact_realization'],r['readout_actor_mode'],r.get('boundary_marker','old') if r['readout_actor_mode']!='original_activity' else 'old') for r in allrows})
    for cohort,keep0 in pp['cohorts'].items():
        chosen=[r for r in allrows if (cohort!='eligible' or r['eligible']) and (cohort!='grammar_common' or r['acceptable'])]
        counts=collections.Counter(r['pair_id'] for r in chosen)
        keep={f:sids for f,sids in keep0.items() if all(counts[s]==160 for s in sids)}
        result['cohorts'][cohort]=keep;v={}
        def record(section,key,vector):result[section][cohort+'/'+key]=stat(vector);v[key]=vector
        for mode in ('base','scope'):
            ix={(r['pair_id'],r['fact_realization'],r['readout_actor_mode'],r.get('boundary_marker','old') if r['readout_actor_mode']!='original_activity' else 'old',r['role_evidence'],r['readout_frame'],r['target_kind']):r for r in chosen if r['native_mode']==mode}
            for form,actor,pred in conditions:
                vv={}
                for frame in ('activity','neutral_entity'):
                    for role in ('source_patient_stated','other_patient_stated'):
                        rv={}
                        for f,sids in keep.items():
                            obs=[]
                            for sid in sids:
                                a=ix[sid,form,actor,pred,role,frame,'source_np'];b=ix[sid,form,actor,pred,role,frame,'other_source_np']
                                assert a['native_pretarget_tokens_sha256']==b['native_pretarget_tokens_sha256']
                                obs.append(b['target_total_bits']-a['target_total_bits'])
                            rv[f]=float(np.mean(obs))
                        vv[role,frame]=rv
                    vv[frame]=diff(vv['source_patient_stated',frame],vv['other_patient_stated',frame])
                    record('cells',f'D/{mode}/{form}/{actor}/{pred}/{frame}',vv[frame])
                jv=diff(vv['activity'],vv['neutral_entity']);record('cells',f'J/{mode}/{form}/{actor}/{pred}',jv)
                raw={f:pp['per_family'][cohort][f][f'J/{form}/{actor}/{pred}'] for f in keep}
                record('contrasts',f'native_minus_raw/{mode}/{form}/{actor}/{pred}',diff(jv,raw))
        for form,actor,pred in conditions:
            record('contrasts',f'scope_minus_base/{form}/{actor}/{pred}',diff(v[f'J/scope/{form}/{actor}/{pred}'],v[f'J/base/{form}/{actor}/{pred}']))
        result['per_family'][cohort]={f:{key:x[f] for key,x in v.items()} for f in keep}
    out.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','run','analyze']);p.add_argument('--cache',type=Path,default=CACHE)
    p.add_argument('--data',type=Path,default=CACHE/'E40-material-preparation-v1/probability-audited-v2.jsonl')
    p.add_argument('--model',type=Path,default=CACHE/'models/Qwen3-8B');p.add_argument('--mode',choices=['base','scope'],default='base')
    p.add_argument('--audit',type=Path,default=CACHE/'E42-material-preparation-v1/instruction-review.json');p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.action=='prepare':
        for m in ('base','scope'):
            t,rr,g=prepare(a.data,a.model,m,a.audit);print(m,len(rr),'verified')
    elif a.action=='run':run(a)
    else:analyze(a.cache,a.out)
