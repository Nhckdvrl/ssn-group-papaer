#!/usr/bin/env python3
"""Single-GPU LoRA SFT with complete-example accounting and resumable checkpoints."""
import argparse
from collections import Counter
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import time
import numpy as np
from training_targets import target_positions


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def training_order(entries, mode, seed, token_budget):
    rng = random.Random(seed)
    buckets = {}
    for i, r in enumerate(entries):
        if r['partition'] == 'train':
            buckets.setdefault(r['task'], []).append(i)
    if mode == 'update':
        result = []
        for _ in range(2):
            group = list(buckets['character_state_update'])
            rng.shuffle(group)
            result.extend(group)
        return result
    names = sorted(buckets)
    if len(names) != 3:
        raise ValueError('Expected all three native tasks')
    buffers = {k: [] for k in names}
    result, total = [], 0
    while total < token_budget:
        task = names[len(result) % len(names)]
        if not buffers[task]:
            buffers[task] = list(buckets[task])
            rng.shuffle(buffers[task])
        i = buffers[task].pop()
        result.append(i)
        total += entries[i]['length']
    return result


def selected_ce(model, input_ids, prompt_length, spans=None):
    """Exactly masked causal CE; compute logits only at target predecessor positions."""
    import torch.nn.functional as F
    if spans is not None:
        import torch
        positions=torch.tensor(target_positions(input_ids.shape[1],prompt_length,spans),device=input_ids.device)
        logits=model(input_ids=input_ids,use_cache=False,logits_to_keep=positions-1).logits[0]
        return F.cross_entropy(logits.float(),input_ids[0,positions])
    n = input_ids.shape[1] - prompt_length
    logits = model(input_ids=input_ids, use_cache=False, logits_to_keep=n+1).logits[0, :-1]
    return F.cross_entropy(logits.float(), input_ids[0, prompt_length:])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', required=True)
    p.add_argument('--checkpoint', required=True)
    p.add_argument('--mode', choices=['update', 'multitask'], required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--max-hours', type=float, default=24)
    p.add_argument('--resume')
    a = p.parse_args()
    root, out = Path(a.data), Path(a.out)
    if out.exists() and not a.resume:
        raise FileExistsError(out)
    out.mkdir(parents=True, exist_ok=bool(a.resume))
    manifest = json.loads((root / 'manifest.json').read_text())
    for name, info in manifest['files'].items():
        if sha(root / name) != info['sha256']:
            raise ValueError('Training cache hash mismatch: ' + name)
    entries = [json.loads(line) for line in (root / 'entries.jsonl').read_text().splitlines()]
    tokens = np.memmap(root / 'tokens.bin', mode='r', dtype='<i4')
    order = training_order(entries, a.mode, a.seed, manifest['native_update_two_epoch_tokens'])
    groups = [order[i:i+64] for i in range(0, len(order), 64)]
    vals = [i for i, r in enumerate(entries) if r['partition'] == 'validation']
    meta = dict(experiment=manifest.get('experiment','D-E10'), started_utc=now(), args=vars(a), complete=False,
        source_manifest_sha256=sha(root/'manifest.json'), script_sha256=sha(__file__),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=Path(__file__).resolve().parents[4],text=True).strip(),
        planned_examples=len(order), planned_forward_tokens=sum(entries[i]['length'] for i in order),
        planned_target_tokens=sum(entries[i]['target_length'] for i in order),
        planned_steps=len(groups), planned_tasks=dict(Counter(entries[i]['task'] for i in order)),
        unique_source_rows=len(set(order)), planned_order_sha256=hashlib.sha256(np.array(order,dtype='<i4').tobytes()).hexdigest())
    (out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
    for helper in ['training_targets.py','cache_local_weights.py']:
        (out/helper).write_bytes(Path(__file__).with_name(helper).read_bytes())
    (out/'training_order.json').write_text(json.dumps([entries[i]['row_id'] for i in order])+'\n')
    def save_meta():
        (out/'metadata.json').write_text(json.dumps(meta, indent=2)+'\n')
    save_meta()
    start = time.monotonic()
    import torch, transformers, peft
    from transformers import AutoModelForCausalLM, set_seed
    from peft import LoraConfig, get_peft_model
    set_seed(a.seed)
    torch.set_num_threads(8)
    from cache_local_weights import resolve_local_checkpoint
    resolved,mirror=resolve_local_checkpoint(a.checkpoint)
    meta.update(resolved_checkpoint=resolved,local_weight_mirror=mirror)
    model = AutoModelForCausalLM.from_pretrained(resolved, local_files_only=True,
        dtype=torch.bfloat16, attn_implementation='sdpa', device_map={'': 0})
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(r=64, lora_alpha=128, lora_dropout=.05,
        target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],
        task_type='CAUSAL_LM', bias='none'))
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    model.enable_input_require_grads()
    params = [v for v in model.parameters() if v.requires_grad]
    optimizer = torch.optim.AdamW(params, lr=2e-5, weight_decay=.01)
    n_warm = max(1, math.ceil(len(groups)*.1))
    def schedule(step):
        if step < n_warm:
            return (step+1)/n_warm
        return .5*(1+math.cos(math.pi*(step-n_warm)/max(1,len(groups)-n_warm)))
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, schedule)
    meta.update(torch=torch.__version__, transformers=transformers.__version__, peft=peft.__version__,
        gpu=torch.cuda.get_device_name(0), trainable_parameters=sum(p.numel() for p in params),
        trainable_dtypes=sorted({str(p.dtype) for p in params}), base_dtype='bfloat16',
        optimizer='AdamW', lr=2e-5, weight_decay=.01, warmup_steps=n_warm,
        gradient_accumulation=64, loss='Mean of per-example assistant-only causal CE', dropout=.05)
    save_meta()
    def tensor(i):
        r=entries[i]
        return torch.tensor(np.array(tokens[r['offset']:r['offset']+r['length']],copy=True),device='cuda',dtype=torch.long)[None]
    completed=0; seen_tokens=0; seen_examples=0; processed_tasks=Counter()
    if a.resume:
        state=torch.load(Path(a.resume)/'training_state.pt',map_location='cpu',weights_only=False)
        from peft import set_peft_model_state_dict
        from safetensors.torch import load_file
        set_peft_model_state_dict(model,load_file(str(Path(a.resume)/'adapter_model.safetensors')))
        optimizer.load_state_dict(state['optimizer']);scheduler.load_state_dict(state['scheduler'])
        completed=state['step'];seen_tokens=state['tokens'];seen_examples=state['examples'];processed_tasks.update(state['tasks'])
        torch.set_rng_state(state['torch_rng']);torch.cuda.set_rng_state_all(state['cuda_rng'])
        meta['resumed_from']=a.resume
    def checkpoint(name):
        dest=out/name
        if dest.exists():raise FileExistsError(dest)
        model.save_pretrained(dest)
        torch.save(dict(optimizer=optimizer.state_dict(),scheduler=scheduler.state_dict(),step=completed,
            tokens=seen_tokens,examples=seen_examples,tasks=dict(processed_tasks),
            torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),dest/'training_state.pt')
        (dest/'checkpoint.json').write_text(json.dumps(dict(step=completed,examples=seen_examples,
            forward_tokens=seen_tokens,files={f.name:sha(f) for f in dest.iterdir() if f.is_file()}),indent=2)+'\n')
        return str(dest)
    def evaluate(label):
        model.eval();s=0.;nt=0;rows=[];bytask={}
        with torch.inference_mode():
            for i in vals:
                r=entries[i];loss=selected_ce(model,tensor(i),r['prompt_length'],r.get('target_spans')).item()
                s+=loss*r['target_length'];nt+=r['target_length']
                group=bytask.setdefault(r['task'],dict(loss_sum=0.,target_tokens=0,examples=0))
                group['loss_sum']+=loss*r['target_length'];group['target_tokens']+=r['target_length'];group['examples']+=1
                rows.append(dict(row_id=r['row_id'],book=r['book'],task=r['task'],nll=loss,target_tokens=r['target_length']))
        for group in bytask.values():group['mean_token_nll']=group.pop('loss_sum')/group['target_tokens']
        with (out/'validation.jsonl').open('a') as f:
            f.write(json.dumps(dict(label=label,step=completed,mean_token_nll=s/nt,by_task=bytask,rows=rows))+'\n')
        model.train()
        print('VALIDATION',label,s/nt,flush=True)
    try:
        if not a.resume:
            # Mechanical equivalence on one real source sample, not an extra training step.
            model.eval();checks=[order[0]]
            multiple=next((i for i in order if len(entries[i].get('target_spans',[]))>1),None)
            if multiple is not None:checks.append(multiple)
            alignment=[]
            for i in checks:
                x=tensor(i);r=entries[i]
                with torch.inference_mode():
                    ce=selected_ce(model,x,r['prompt_length'],r.get('target_spans')).item()
                    labels=torch.full_like(x,-100);positions=target_positions(x.shape[1],r['prompt_length'],r.get('target_spans'))
                    labels[0,positions]=x[0,positions]
                    full=model(input_ids=x,labels=labels,use_cache=False).loss.item()
                if abs(ce-full)>1e-3:raise ValueError(('Masked CE misalignment',ce,full))
                alignment.append(dict(row_id=r['row_id'],selected_ce=ce,full_masked_ce=full,assistant_spans=len(r.get('target_spans',[])) or 1))
            meta['alignment_check']=dict(cases=alignment,extra_forwards=2*len(checks))
            save_meta();evaluate('initial')
        model.train()
        for step in range(completed,len(groups)):
            if time.monotonic()-start>a.max_hours*3600:
                meta['stop_reason']='registered_compute_budget';meta['last_checkpoint']=checkpoint('budget-stop')
                break
            begin=time.monotonic();group=groups[step];optimizer.zero_grad(set_to_none=True);loss_sum=0.
            for i in group:
                r=entries[i];loss=selected_ce(model,tensor(i),r['prompt_length'],r.get('target_spans'))
                if not torch.isfinite(loss):raise FloatingPointError('Nonfinite training loss')
                (loss/len(group)).backward();loss_sum+=loss.detach().item()
                seen_tokens+=r['length'];seen_examples+=1;processed_tasks[r['task']]+=1
            grad=torch.nn.utils.clip_grad_norm_(params,1.0)
            if not torch.isfinite(grad):raise FloatingPointError('Nonfinite gradient')
            optimizer.step();scheduler.step();completed=step+1;torch.cuda.synchronize()
            record=dict(step=completed,loss=loss_sum/len(group),grad_norm=float(grad),lr=scheduler.get_last_lr()[0],
                examples=seen_examples,forward_tokens=seen_tokens,step_s=time.monotonic()-begin,
                wall_s=time.monotonic()-start,peak_allocated=torch.cuda.max_memory_allocated())
            with (out/'train_log.jsonl').open('a') as f:f.write(json.dumps(record)+'\n');f.flush();os.fsync(f.fileno())
            print(json.dumps(record),flush=True)
            meta.update(completed_steps=completed,seen_examples=seen_examples,seen_forward_tokens=seen_tokens,
                        processed_tasks=dict(processed_tasks));save_meta()
            if completed%100==0 and completed<len(groups):meta['last_checkpoint']=checkpoint(f'step-{completed:04d}')
            if completed==len(groups)//2:evaluate('halfway')
        if completed==len(groups):
            evaluate('final');meta['final_checkpoint']=checkpoint('final');meta['complete']=True
    except BaseException as error:
        meta['error']=repr(error)
        raise
    finally:
        meta.update(finished_utc=now(),wall_s=time.monotonic()-start,completed_steps=completed,
                    seen_examples=seen_examples,seen_forward_tokens=seen_tokens,processed_tasks=dict(processed_tasks))
        save_meta()


if __name__=='__main__':
    try:
        main()
    except BaseException as error:
        # Loading/adapter construction failures happen before the training loop.
        # Preserve their metadata as well, without manufacturing optimizer steps.
        import sys
        if '--out' in sys.argv:
            path=Path(sys.argv[sys.argv.index('--out')+1])/'metadata.json'
            if path.exists():
                record=json.loads(path.read_text())
                record.update(complete=False,error=repr(error),finished_utc=now())
                path.write_text(json.dumps(record,indent=2)+'\n')
        raise
