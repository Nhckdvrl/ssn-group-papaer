"""E103: inherited criterion/private mapping under native hybrid state swaps.

State-swap follows Afendulev et al. (arXiv:2609.04434). No cache is zeroed.
Only past demonstration labels change; neither parent has seen a future query.
"""
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

from e93_selective_sharing import body, contexts, design_audit
from e94_coordinate_transfer import SYSTEM


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def interval(values):
    rng = random.Random(103001)
    bs = sorted(sum(values[rng.randrange(len(values))] for _ in values)/len(values)
                for _ in range(10000))
    return {'mean': sum(values)/len(values), 'ci95': [bs[250], bs[9749]],
            'per_context': values, 'n_contexts': len(values)}


def analyze(rows):
    ids = sorted({r['context'] for r in rows})
    assert len(rows) == 64*len(ids)
    out = {'n_rows': len(rows), 'unique_memory_query_inputs': len(set(
        (r['context'], tuple(r['kv_world']), tuple(r['rec_world']), r['query']) for r in rows)),
        'native_accuracy': interval([sum(r['argmax_class'] == r['gold']
            for r in rows if r['context'] == ci and r['condition'] == 'native')/16 for ci in ids]),
        'conditions': {}, 'dependency_models': {}}
    for cond in ('native', 'all_donor', 'kv_donor', 'rec_donor'):
        rr = [r for r in rows if r['condition'] == cond]
        item = {'n': len(rr), 'invalid': sum(not r['valid'] for r in rr), 'predictions': {}}
        for typ in ('recipient_function', 'donor_function', 'criterion_only', 'private_only',
                    'actual_native_R', 'actual_native_D'):
            groups = {}
            for r in rr:
                groups.setdefault((r['context'], r['cr'], r['pr']), []).append(r)
            assert all(len(g) == 4 and {r['query'] for r in g} == set(range(4)) for g in groups.values())
            item['predictions'][typ] = {'matches': sum(r['argmax_class'] == r['predictions'][typ] for r in rr),
                'denominator': len(rr), 'rate': interval([
                    sum(r['argmax_class'] == r['predictions'][typ] for r in rr if r['context'] == ci)/16
                    for ci in ids]),
                'complete_profiles': sum(all(r['argmax_class'] == r['predictions'][typ] for r in g)
                                         for g in groups.values()), 'profile_denominator': len(groups)}
        out['conditions'][cond] = item
    mappings = {
        'KV_whole_function': ('donor_function', 'recipient_function'),
        'Rec_whole_function': ('recipient_function', 'donor_function'),
        'KV_criterion_Rec_private': ('criterion_only', 'private_only'),
        'KV_private_Rec_criterion': ('private_only', 'criterion_only')}
    rr = [r for r in rows if r['condition'] in ('kv_donor', 'rec_donor')]
    for name, types in mappings.items():
        out['dependency_models'][name] = {'record_denominator': len(rr),
            'unique_input_denominator': len({(r['context'], tuple(r['kv_world']), tuple(r['rec_world']), r['query'])
                                             for r in rr}),
            'accuracy': interval([sum(r['argmax_class'] == r['predictions'][
                types[0 if r['condition'] == 'kv_donor' else 1]] for r in rr if r['context'] == ci)/32
                for ci in ids])}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='/tmp/ices_models/Qwen3.8-27B')
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=4)
    ap.add_argument('--seed', type=int, default=103001)
    ap.add_argument('--preflight-only', action='store_true')
    a = ap.parse_args(); p = Path(a.out); p.mkdir(parents=True, exist_ok=True)
    assert not (p/'behavior.jsonl').exists()
    cs = contexts(a.n, a.seed); audit = design_audit(cs)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    lids = [tok.encode(' '+s, add_special_tokens=False) for s in ('no', 'yes')]
    assert all(len(v) == 1 for v in lids); lids = [v[0] for v in lids]

    def record(c, cr, pr, qi):
        user = body(c, 'probe', -pr, cr, pr, 0, qi)
        prompt = tok.apply_chat_template([{'role':'system','content':SYSTEM},
            {'role':'user','content':user}], tokenize=False,
            add_generation_prompt=True, enable_thinking=False)+'Answer:'
        field = f'Reviewer: {c["names"][1]}'
        cut = prompt.rfind(field+'\nReview:')+len(field)
        assert cut >= len(field)
        full = tok.encode(prompt, add_special_tokens=False)
        prefix = tok.encode(prompt[:cut], add_special_tokens=False)
        assert full[:len(prefix)] == prefix
        assert c['queries'][qi]['text'] not in prompt[:cut]
        x = c['queries'][qi]['x']
        return {'context': c['context'], 'cr': cr, 'pr': pr, 'query': qi, 'x': x,
                'gold': pr*x[cr], 'prefix_ids': prefix, 'suffix_ids': full[len(prefix):],
                'full_ids': full}

    records = []
    for c in cs:
        dd = {(cr, pr, qi): record(c, cr, pr, qi)
              for cr, pr, qi in itertools.product((0, 1), (1, -1), range(4))}
        assert len({len(r['prefix_ids']) for r in dd.values()}) == 1
        for cr, pr in itertools.product((0, 1), (1, -1)):
            assert len({tuple(dd[cr, pr, qi]['prefix_ids']) for qi in range(4)}) == 1
            patterns = [tuple(sign*q['x'][cc] for q in c['queries'])
                        for sign, cc in [(pr, cr), (-pr, 1-cr), (pr, 1-cr), (-pr, cr)]]
            assert len(set(patterns)) == 4
        # Same future suffix for every parent world, rendered once per full prompt.
        for qi in range(4):
            assert len({tuple(r['suffix_ids']) for (cr, pr, q), r in dd.items() if q == qi}) == 1
        records.append(dd)
    cfg = json.loads((Path(a.model)/'config.json').read_text()); tc = cfg.get('text_config', cfg)
    types = tc['layer_types']; assert types.count('linear_attention') == 48
    assert types.count('full_attention') == 16
    audit.update(expected_records=64*a.n, expected_unique_inputs=32*a.n,
                 future_query_in_parent=False, direct_rule_from_examples=True)
    (p/'design_audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    (p/'preflight.json').write_text(json.dumps({'args':vars(a), 'label_ids':lids,
        'prefix_lengths':[len(next(iter(d.values()))['prefix_ids']) for d in records],
        'layers':types, 'all_token_boundaries_exact':True,
        'future_suffix_byte_identical_across_worlds':True, 'state_swap_reference':'arXiv:2609.04434'}, indent=2)+'\n')
    (p/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    if a.preflight_only:
        print('Preflight passed', 64*a.n, 'records', 32*a.n, 'unique memory-query inputs', flush=True); return

    import torch, transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0); t0=time.time()
    print('Loading float32/eager on two GPUs', flush=True)
    model, loading = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True,
        dtype=torch.float32, device_map='auto', max_memory={0:'64GiB',1:'64GiB'},
        attn_implementation='eager', output_loading_info=True)
    model.eval(); model.requires_grad_(False)
    assert not loading.get('missing_keys'), loading
    assert set(model.hf_device_map.values()) <= {0,1,'cuda:0','cuda:1'}
    assert all(any(k in x for k in ('visual.', 'vision_', 'mtp.'))
               for x in loading.get('unexpected_keys', [])), loading
    (p/'loading_info.json').write_text(json.dumps(loading, indent=2, default=str)+'\n')
    flags={'suffix':False}; carry={i:0 for i,t in enumerate(types) if t=='linear_attention'}
    # Observe restored state consumption without changing any mixing operation.
    for i,t in enumerate(types):
        if t!='linear_attention': continue
        mixer=model.model.layers[i].linear_attn
        for fn_name in ('chunk_gated_delta_rule','recurrent_gated_delta_rule'):
            original=getattr(mixer,fn_name)
            def checked(*args, _fn=original, _idx=i, **kwargs):
                if flags['suffix']:
                    assert kwargs.get('initial_state') is not None, 'restored recurrent state silently ignored'
                    carry[_idx]+=1
                return _fn(*args,**kwargs)
            setattr(mixer,fn_name,checked)
    numeric={'all_donor_max_nats':0., 'self_copy_max_nats':0., 'repeated_input_max_nats':0.,
             'unsplit_split_max_vocab_nats':0., 'unsplit_split_max_label_margin_nats':0.,
             'unsplit_split_argmax_disagreement':0, 'unsplit_split_checked':0,
             'unmodified_channel_exact':True, 'pristine_cache_preserved':True}
    rows=[]; shapes=[]

    def tensor_fields(cache):
        for i,t in enumerate(types):
            layer=cache.layers[i]
            for name in (('keys','values') if t=='full_attention' else ('conv_states','recurrent_states')):
                yield i,name,getattr(layer,name)

    def fingerprint(cache):
        h=hashlib.sha256()
        for i,name,value in tensor_fields(cache):
            assert value is not None
            h.update(str((i,name,tuple(value.shape))).encode())
            h.update(value.detach().cpu().numpy().tobytes())
        return h.hexdigest()

    def combine(receiver, donor, cond):
        out=copy.deepcopy(receiver)
        for i,t in enumerate(types):
            fields=('keys','values') if t=='full_attention' else ('conv_states','recurrent_states')
            change=cond=='all_donor' or (cond=='kv_donor' and t=='full_attention') or (cond=='rec_donor' and t=='linear_attention')
            for name in fields:
                target=getattr(out.layers[i],name); rv=getattr(receiver.layers[i],name); dv=getattr(donor.layers[i],name)
                assert target.data_ptr()!=rv.data_ptr(), 'cache alias'
                assert target.shape==dv.shape and target.device==dv.device
                if change: target.copy_(dv)
                assert torch.equal(target,dv if change else rv), 'unintended channel edit'
        assert out.get_seq_length()==receiver.get_seq_length()==donor.get_seq_length()
        for i,t in enumerate(types):
            if t=='linear_attention': assert out.has_previous_state(i)
        return out

    def predict(r, cache):
        flags['suffix']=True
        start=len(r['prefix_ids']); ids=torch.tensor([r['suffix_ids']],device='cuda:0')
        positions=torch.arange(start,start+ids.shape[1],device='cuda:0')[None]
        try:
            lo=model(input_ids=ids,position_ids=positions,past_key_values=cache,
                     use_cache=True,logits_to_keep=1).logits[0,-1].float().cpu()
        finally: flags['suffix']=False
        return lo

    def scored(r, lo):
        top=int(lo.argmax()); z=float(lo[lids[1]]-lo[lids[0]])
        return {'context':r['context'],'cr':r['cr'],'pr':r['pr'],'query':r['query'],
                'x':r['x'],'gold':r['gold'],'z':z,'argmax_token':top,
                'argmax_class':1 if top==lids[1] else -1 if top==lids[0] else 0,
                'valid':top in lids}

    with torch.inference_mode(), (p/'behavior.jsonl').open('w') as stream:
        for ci, dd in enumerate(records):
            parents={}; original_hash={}; native={}; seen={}
            for cr,pr in itertools.product((0,1),(1,-1)):
                r=dd[cr,pr,0]
                parents[cr,pr]=model(input_ids=torch.tensor([r['prefix_ids']],device='cuda:0'),
                                    use_cache=True,logits_to_keep=1).past_key_values
                original_hash[cr,pr]=fingerprint(parents[cr,pr])
            if ci==0:
                shapes=[{'layer':i,'field':name,'shape':list(v.shape),'device':str(v.device)}
                        for i,name,v in tensor_fields(parents[0,1])]
                (p/'cache_shapes.json').write_text(json.dumps(shapes,indent=2)+'\n')
            for key,r in dd.items():
                cr,pr,qi=key; lo=predict(r,combine(parents[cr,pr],parents[cr,pr],'native'))
                native[key]=lo; seen[((cr,pr),(cr,pr),qi)]=lo
                if ci==0:
                    full=model(input_ids=torch.tensor([r['full_ids']],device='cuda:0'),
                               use_cache=False,logits_to_keep=1).logits[0,-1].float().cpu()
                    numeric['unsplit_split_max_vocab_nats']=max(numeric['unsplit_split_max_vocab_nats'],float((full-lo).abs().max()))
                    err=abs(float((full[lids[1]]-full[lids[0]])-(lo[lids[1]]-lo[lids[0]])))
                    numeric['unsplit_split_max_label_margin_nats']=max(numeric['unsplit_split_max_label_margin_nats'],err)
                    numeric['unsplit_split_argmax_disagreement']+=int(full.argmax()!=lo.argmax())
                    numeric['unsplit_split_checked']+=1
            (p/'numeric_audit.json').write_text(json.dumps(numeric,indent=2)+'\n')
            assert numeric['unsplit_split_argmax_disagreement']==0
            assert numeric['unsplit_split_max_label_margin_nats']<=.01
            for key,r in dd.items():
                cr,pr,qi=key; dc,dp=1-cr,-pr; ref=native[key]; dref=native[dc,dp,qi]
                for cond in ('native','all_donor','kv_donor','rec_donor'):
                    kv=(dc,dp) if cond in ('all_donor','kv_donor') else (cr,pr)
                    rec=(dc,dp) if cond in ('all_donor','rec_donor') else (cr,pr)
                    if cond=='native': lo=ref
                    else: lo=predict(r,combine(parents[cr,pr],parents[dc,dp],cond))
                    if cond=='all_donor': numeric['all_donor_max_nats']=max(numeric['all_donor_max_nats'],float((lo-dref).abs().max()))
                    sk=(kv,rec,qi)
                    if sk in seen: numeric['repeated_input_max_nats']=max(numeric['repeated_input_max_nats'],float((lo-seen[sk]).abs().max()))
                    seen[sk]=lo
                    x=r['x'];d=scored(r,lo);d.update(condition=cond,kv_world=kv,rec_world=rec,
                        donor_world=[dc,dp],predictions={
                            'recipient_function':pr*x[cr], 'donor_function':dp*x[dc],
                            'criterion_only':pr*x[dc], 'private_only':dp*x[cr],
                            'actual_native_R':scored(r,ref)['argmax_class'],
                            'actual_native_D':scored(r,dref)['argmax_class']})
                    rows.append(d);stream.write(json.dumps(d)+'\n');stream.flush()
            rr=dd[0,1,0];cp=combine(parents[0,1],parents[0,1],'all_donor')
            no_op=predict(rr,cp)
            numeric['self_copy_max_nats']=max(numeric['self_copy_max_nats'],float((no_op-native[0,1,0]).abs().max()))
            assert all(fingerprint(cache)==original_hash[key] for key,cache in parents.items())
            assert numeric['all_donor_max_nats']<=.001 and numeric['self_copy_max_nats']<=.001
            assert numeric['repeated_input_max_nats']<=.001
            (p/'numeric_audit.json').write_text(json.dumps(numeric,indent=2)+'\n')
            print('context',ci+1,'/',a.n,'rows',len(rows),flush=True)
    analysis=analyze(rows); analysis['native_gate_passed']=analysis['native_accuracy']['mean']>=.90
    (p/'analysis.json').write_text(json.dumps(analysis,indent=2)+'\n')
    (p/'carry_audit.json').write_text(json.dumps({'layers':carry,'all_48_layers_used_restored_state':all(v>0 for v in carry.values())},indent=2)+'\n')
    run={'args':vars(a),'n_rows':len(rows),'script_sha256':sha(__file__),
         'dependency_sha256':sha('scripts/e93_selective_sharing.py'),
         'model_config_sha256':sha(Path(a.model)/'config.json'),'training':False,
         'numeric':numeric,'dtype':'float32','attention':'eager',
         'elapsed_seconds':time.time()-t0,'gpu_hours':2*(time.time()-t0)/3600,
         'torch':torch.__version__,'transformers':transformers.__version__,
         'python':platform.python_version(),'device_map':model.hf_device_map,
         'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    (p/'run.json').write_text(json.dumps(run,indent=2)+'\n')
    print('Complete',len(rows),'records',analysis['unique_memory_query_inputs'],'unique inputs',flush=True)


if __name__=='__main__':
    main()
