#!/usr/bin/env python3
"""Exact E62 decoder branch probabilities; no policy/physics regeneration."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from native_recipient_patch import prepare
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    manifest = json.loads((args.run / 'manifest.json').read_text())
    assert (args.run / 'runtime.json').exists(), 'Freeze complete generation before probability audit'
    assert hashlib.sha256(args.dataset.read_bytes()).hexdigest() == manifest['dataset_sha256']
    cases = {c['case_id']: c for c in map(json.loads, args.dataset.read_text().splitlines())}
    prompts = list(map(json.loads, (args.run / 'prompts.jsonl').read_text().splitlines()))
    assert len(prompts) == manifest['graphs'] * 3 * 2
    modules = load_event_modules(CACHE / 'sources/LIGHT')
    data = {cid: prepare(cases[cid], modules) for cid in manifest['case_ids']}
    assert all(len(v['commands']) == 2 for v in data.values()), 'Exact two-branch cohort, not a generic approximation'
    args.out.mkdir(parents=True, exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForImageTextToText
    torch.set_num_threads(1)
    vectors = torch.load(args.run / 'residuals.pt', weights_only=True, map_location='cpu')
    model_path = Path(manifest['model'])
    config = json.loads((model_path / 'config.json').read_text())
    loader = AutoModelForImageTextToText if config['model_type'] in ['qwen3_5','gemma3'] else AutoModelForCausalLM
    start = time.monotonic()
    model = loader.from_pretrained(str(model_path), dtype=torch.bfloat16, device_map={'':'cuda:0'},
                                  attn_implementation='sdpa', local_files_only=True).eval()
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
    if config['model_type'] == 'qwen3_5': decoder = model.model.language_model
    elif config['model_type'] == 'gemma3': decoder = model.model.language_model
    else: decoder = model.model
    assert len(decoder.layers) == manifest['layer_count']
    layer = decoder.layers[manifest['layer_index']]
    load_seconds = time.monotonic()-start
    (args.out / 'manifest.json').write_text(json.dumps({'source':str(args.run), 'source_manifest':manifest,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'prompts_sha256':hashlib.sha256((args.run / 'prompts.jsonl').read_bytes()).hexdigest(),
        'purpose':'exact constrained first-branch probability; complete command determined thereafter',
        'native_actions_regenerated':0,'cloud_calls':0},indent=2)+'\n')
    started = time.monotonic();count = 0
    for prompt_row in prompts:
        cid = prompt_row['case_id']; context = prompt_row['context']; persona = prompt_row['persona']
        case_data = data[cid]
        text = tokenizer.apply_chat_template(prompt_row['messages'], tokenize=False,
                    add_generation_prompt=True, enable_thinking=False) + '{"action":'
        assert hashlib.sha256(text.encode()).hexdigest() == prompt_row['prompt_sha256']
        common = prompt_row['forced_command_tokens']
        ids = tokenizer(text, add_special_tokens=False).input_ids + common
        assert len(ids) == prompt_row['prefix_length']
        own_ids = tokenizer(json.dumps(case_data['own_command'],ensure_ascii=False),add_special_tokens=False).input_ids
        req_ids = tokenizer(json.dumps(case_data['request_command'],ensure_ascii=False),add_special_tokens=False).input_ids
        assert own_ids[:len(common)] == req_ids[:len(common)] == common
        own_token, req_token = own_ids[len(common)], req_ids[len(common)]
        assert own_token != req_token
        # With exactly two commands and a maximal common prefix, each branch has one leaf.
        # Only the first branch is random; all remaining native command tokens are forced.
        inputs = {'input_ids':torch.tensor([ids],device='cuda'),
                  'attention_mask':torch.ones((1,len(ids)),device='cuda',dtype=torch.long)}
        target = vectors[cid,context,persona].to('cuda',dtype=torch.bfloat16)
        donor_persona = 'agreeable' if persona == 'firm' else 'firm'
        source = vectors[cid,context,donor_persona].to('cuda',dtype=torch.bfloat16)
        generator = torch.Generator(device='cuda').manual_seed(625100031+int(cid[:7],16))
        noise = torch.randn(target.shape,generator=generator,device='cuda',dtype=torch.float32)
        delta = noise/noise.norm()*(source.float()-target.float()).norm()
        position = len(ids)-1
        for condition in manifest['conditions']:
            handle = None
            if condition != 'baseline':
                def patch(module, inputs0, output):
                    h = output[0] if isinstance(output,tuple) else output
                    if h.shape[1] <= position: return output
                    h = h.clone()
                    if condition == 'sham': h[0,position] = target
                    elif condition == 'donor': h[0,position] = source
                    else: h[0,position] = (h[0,position].float()+delta).to(h.dtype)
                    return (h,*output[1:]) if isinstance(output,tuple) else h
                handle = layer.register_forward_hook(patch)
            torch.manual_seed(6251+int(cid[:7],16)*10)
            with torch.inference_mode():
                generated = model.generate(**inputs,do_sample=True,temperature=.7,top_p=1.,top_k=0,
                    max_new_tokens=1,use_cache=True,output_scores=True,return_dict_in_generate=True,
                    prefix_allowed_tokens_fn=lambda batch_index,sequence:[own_token,req_token],
                    eos_token_id=tokenizer.eos_token_id,pad_token_id=tokenizer.eos_token_id)
                logits = generated.scores[0][0].float()
                probs = torch.softmax(logits,-1)
            if handle: handle.remove()
            row = {'case_id':cid,'persona':persona,'context':context,'condition':condition,
                'request_probability':float(probs[req_token]),'own_probability':float(probs[own_token]),
                'processed_branch_log_odds':float(logits[req_token]-logits[own_token]),
                'first_own_token':own_token,'first_request_token':req_token,
                'language_candidate_scores':prompt_row['candidate_log_likelihood']}
            assert abs(row['request_probability']+row['own_probability']-1.) < 1e-5
            with (args.out / 'probabilities.jsonl').open('a') as f:
                f.write(json.dumps(row,ensure_ascii=False)+'\n')
            count += 1
        if count % 120 == 0:
            print(json.dumps({'probability_readouts':count,'seconds':time.monotonic()-started}),flush=True)
    assert count == manifest['graphs']*3*2*4
    runtime = {'graphs':manifest['graphs'],'probability_readouts':count,
        'native_actions_regenerated':0,'model_load_seconds':load_seconds,
        'wall_seconds':time.monotonic()-started,'cloud_calls':0}
    (args.out / 'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n')
    print(json.dumps(runtime),flush=True)


if __name__ == '__main__': main()
