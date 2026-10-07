"""E64 fixed source trajectories: target versus remaining-context consumption."""
import argparse
import fcntl
import inspect
import json
import math
import os
from pathlib import Path
import time
from contextlib import contextmanager
from data import CACHE, sha
from data_v2 import digest
from natural_cue_patching import blocks, unpack, score
from shared_source_cross_use import prepare, greedy
from paraphrase_map import sentence_parts

OPS = ('NATIVE_BASE', 'BASE_BANK', 'FULL_BANK', 'TARGET_BANK', 'CONTEXT_BANK')


@contextmanager
def bank_hooks(decoder, banks, uid, positions, target, op, verified=None):
    import torch
    handles = []
    if op == 'NATIVE_BASE':
        yield
        return
    target = set(target)
    for layer, block in enumerate(decoder):
        device = next(block.parameters()).device
        refs = []
        for position in positions:
            paired = op == 'FULL_BANK' or op == 'TARGET_BANK' and position in target or op == 'CONTEXT_BANK' and position not in target
            refs.append(banks['PAIR' if paired else 'BASE'][uid][layer][position])
        values = torch.stack(refs).to(device)
        def hook(module, inputs, output, layer=layer, values=values):
            hidden = unpack(output).clone()
            assert hidden.shape[0] == 1
            hidden[0, positions] = values
            if verified is not None:
                assert bool((hidden[0, positions] == values).all())
                untouched = [i for i in range(hidden.shape[1]) if i not in set(positions)]
                assert bool((hidden[0, untouched] == unpack(output)[0, untouched]).all())
                verified.append(layer)
            return (hidden, *output[1:]) if isinstance(output, tuple) else hidden
        handles.append(block.register_forward_hook(hook))
    try:
        yield
    finally:
        for handle in handles:
            handle.remove()


def trajectory(model, decoder, prefix, positions, patch_layer=None, receivers=(), donor=None):
    import torch
    result = {}; handles = []
    for layer, block in enumerate(decoder):
        def hook(module, inputs, output, layer=layer):
            hidden = unpack(output)
            if layer == patch_layer:
                hidden = hidden.clone()
                for position, ref in zip(receivers, donor):
                    hidden[0, position] = ref.to(hidden.device)
            result[layer] = {position: hidden[0, position].detach().cpu().clone() for position in positions}
            return (hidden, *output[1:]) if isinstance(output, tuple) else hidden
        handles.append(block.register_forward_hook(hook))
    try:
        ids = torch.tensor([prefix], device=model.device)
        with torch.inference_mode():
            model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False, **last_logits(model))
    finally:
        for handle in handles:
            handle.remove()
    assert len(result) == len(decoder)
    return result


def last_logits(model):
    return {'logits_to_keep': 1} if 'logits_to_keep' in inspect.signature(model.forward).parameters else {}


def qa_score(model, decoder, banks, tokens, t, op, verified=None):
    import torch
    sequences, length = t['encoded']; uid = t['original_row']['source_unit']
    ids = torch.tensor([sequences[0][:length]], device=model.device)
    with bank_hooks(decoder, banks, uid, tokens[uid], t.get('target_tokens', []), op, verified):
        with torch.inference_mode():
            lp = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False, **last_logits(model)).logits[0, -1].float().log_softmax(-1)
    return [float(lp[s[length]]) for s in sequences]


def generate(model, decoder, banks, tokens, g, op, cap):
    with bank_hooks(decoder, banks, g['row']['source_unit'], tokens[g['row']['source_unit']], g['patch_tokens'], op):
        return greedy(model, decoder, {}, g, None, 'BASE', cap)


def instrument(model, decoder, banks, tokens, tasks, gens, layer):
    import torch
    fixed = sorted(gens, key=lambda g: g['row']['source_unit'])[:4]
    fixed_ids = {g['row']['source_unit'] for g in fixed}
    paired = [t for t in tasks if t['operation'] == 'PAIR' and t['original_row']['source_unit'] in fixed_ids]
    target = {g['row']['source_unit']: g['patch_tokens'] for g in gens}
    delta = {'BASE_BANK': [], 'FULL_BANK': []}; greedy_checks = []; source_checks = []
    for t in paired:
        t['target_tokens'] = target[t['original_row']['source_unit']]
        native = qa_score(model, decoder, banks, tokens, t, 'NATIVE_BASE')
        frozen = qa_score(model, decoder, banks, tokens, t, 'BASE_BANK')
        original_pair = score(model, decoder, banks['BASE'], [t], model.config.pad_token_id)[0]
        full = qa_score(model, decoder, banks, tokens, t, 'FULL_BANK')
        delta['BASE_BANK'].append(max(abs(a-b) for a,b in zip(native, frozen)))
        delta['FULL_BANK'].append(max(abs(a-b) for a,b in zip(original_pair, full)))
        assert max(delta['BASE_BANK'][-1], delta['FULL_BANK'][-1]) < .001
        for op in ('TARGET_BANK', 'CONTEXT_BANK'):
            checks = []; qa_score(model, decoder, banks, tokens, t, op, checks)
            assert checks == list(range(len(decoder)))
    for g in fixed:
        uid = g['row']['source_unit']; captured = {}; handles = []
        for l, block in enumerate(decoder):
            def capture(module, inputs, output, l=l):
                captured[l] = unpack(output)[0, tokens[uid]].detach().cpu().clone()
            handles.append(block.register_forward_hook(capture))
        try:
            ids = torch.tensor([g['ids']], device=model.device)
            with torch.inference_mode():model(input_ids=ids, use_cache=False, **last_logits(model))
        finally:
            for h in handles:h.remove()
        for l in range(len(decoder)):
            ref = torch.stack([banks['BASE'][uid][l][p] for p in tokens[uid]])
            difference = captured[l] - ref
            absolute = difference.abs().amax(-1); relative = difference.double().norm(dim=-1)/ref.double().norm(dim=-1).clamp_min(1e-12)
            assert bool(((absolute < .001) | (relative < 1e-5)).all())
            source_checks.append({'uid':uid,'layer':l,'abs':float(absolute.max()),'relative':float(relative.max())})
        native = greedy(model, decoder, {}, g, layer, 'BASE', 16)
        original_pair = greedy(model, decoder, banks['BASE'], g, layer, 'PAIR', 16)
        assert native == generate(model, decoder, banks, tokens, g, 'BASE_BANK', 16)
        assert original_pair == generate(model, decoder, banks, tokens, g, 'FULL_BANK', 16)
        greedy_checks.append(uid)
    return dict(lp_max_deltas={k:max(v) for k,v in delta.items()},greedy_16step_equal=greedy_checks,source_checks=source_checks,
        mixed_banks_exact=True,non_source_outputs_not_overwritten=True)


def run(args):
    import torch
    from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM, Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    torch.manual_seed(64);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False
    lock=(CACHE/'E52/gpu-slots'/str(args.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    start=time.monotonic();args.out.mkdir(parents=True,exist_ok=True)
    assert not (args.out/'qa-predictions.jsonl').exists()
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cfg=AutoConfig.from_pretrained(args.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    model.config.pad_token_id=tok.pad_token_id
    decoder=blocks(model);layer=math.floor(.25*(len(decoder)-1))
    rows=[json.loads(l) for l in args.data.read_text().splitlines()]
    tasks,gens,prefixes,tokens,excluded=prepare(rows,tok,layer)
    reference=json.loads((args.reference/'config.json').read_text())
    assert sorted(prefixes)==reference['cohort'] and reference['data_sha256']==sha(args.data) and reference['layer']==layer
    if args.instrument_only:
        ids={u for g in sorted(gens,key=lambda g:g['row']['source_unit'])[:4] for u in (g['row']['source_unit'],g['row']['donor_source_unit'])}
        prefixes={u:p for u,p in prefixes.items() if u in ids}
    banks={'BASE':{},'PAIR':{}}
    for uid,prefix in prefixes.items():banks['BASE'][uid]=trajectory(model,decoder,prefix,tokens[uid])
    gi={g['row']['source_unit']:g for g in gens}
    for uid,prefix in prefixes.items():
        g=gi[uid];donor=[banks['BASE'][g['row']['donor_source_unit']][layer][p] for p in g['donor_tokens']]
        banks['PAIR'][uid]=trajectory(model,decoder,prefix,tokens[uid],layer,g['patch_tokens'],donor)
    report=instrument(model,decoder,banks,tokens,tasks,gens,layer)
    (args.out/'instrument.json').write_text(json.dumps(report,indent=2)+'\n')
    config=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),
        code_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in ('shared_source_cross_use.py','natural_cue_patching.py')},
        layer=layer,dtype='float32',attention='eager',seed=64,gpu_index=args.gpu,cohort=reference['cohort'],operations=OPS[1:],cap=args.cap,
        reference_config_sha256=sha(args.reference/'config.json'),phase='instrument_only' if args.instrument_only else 'science')
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    if args.instrument_only:print('E64 instrument passed',args.model.name,flush=True);return
    torch.save(banks,args.out/'source-banks.pt')
    for name in ('source_bank_routes.py','shared_source_cross_use.py','natural_cue_patching.py'):(args.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    target={g['row']['source_unit']:g['patch_tokens'] for g in gens}
    baseline=[t for t in tasks if t['operation']=='BASE']
    with (args.out/'qa-predictions.jsonl').open('w') as f:
        for i,t in enumerate(baseline):
            r=t['original_row'];t['target_tokens']=target[r['source_unit']]
            for op in OPS[1:]:
                lp=qa_score(model,decoder,banks,tokens,t,op);den=max(lp)+math.log(sum(math.exp(x-max(lp)) for x in lp))
                record={k:r[k] for k in ('item_id','sentence_sha256','question','construction','condition','source_gold_matches_grounding','literal_label','source_unit','donor_source_unit')}
                record.update(operation=op,readout=t['readout'],mapping=t['mapping'],question_target=r['analysis_question_target'],cluster_id=r['analysis_cluster_id'],
                    pair_id=r['analysis_pair_id'],candidate_gold=t['candidate_gold'],candidate_logprobs=lp,correct=max(range(len(lp)),key=lp.__getitem__)==t['candidate_gold'],
                    p_correct=math.exp(lp[t['candidate_gold']]-den),prompt_sha256=digest(t['prompt']))
                f.write(json.dumps(record)+'\n')
            f.flush()
            if (i+1)%100==0:print('E64 QA',i+1,'/',len(baseline),flush=True)
    with (args.out/'predictions.jsonl').open('w') as f:
        for i,g in enumerate(gens):
            for op in OPS[1:]:
                generated=generate(model,decoder,banks,tokens,g,op,args.cap);text=tok.decode(generated,skip_special_tokens=True);r=g['row'];parts=sentence_parts(text)
                record=dict(item_id=r['source_unit'],sentence_sha256=r['sentence_sha256'],construction=r['construction'],condition=r['condition'],cluster_id=r['analysis_cluster_id'],
                    format='TASK_AFTER_SOURCE',reading=op,prompt_sha256=digest(g['prompt']),text=text,text_sha256=digest(text),generated_token_ids=generated,
                    capped=len(generated)==args.cap,finish_reason='length' if len(generated)==args.cap else 'stop',automatic_sentence_parts=parts,automatic_two_sentences=len(parts)==2)
                f.write(json.dumps(record)+'\n');f.flush()
            if (i+1)%10==0:print('E64 roles',i+1,'/',len(gens),flush=True)
    config.update(predictions_sha256=sha(args.out/'predictions.jsonl'),qa_predictions_sha256=sha(args.out/'qa-predictions.jsonl'),source_banks_sha256=sha(args.out/'source-banks.pt'),
        gpu_hours=(time.monotonic()-start)/3600,qa_tasks=len(baseline)*len(OPS[1:]),role_tasks=len(gens)*len(OPS[1:]))
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');print('Completed E64',args.model.name,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path,required=True)
    p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--gpu',type=int,required=True)
    p.add_argument('--cap',type=int,default=256);p.add_argument('--instrument-only',action='store_true');run(p.parse_args())
