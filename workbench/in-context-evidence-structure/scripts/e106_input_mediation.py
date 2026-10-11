"""E106: functional path through own input encoding into own label evidence.
Uses E91 namespace task and CTA-style causal path isolation.
"""
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np

from e56_query_adapter import HEAD, contexts, pools

WORDS = {"shared": ["safe", "toxic"], "far": ["pass", "flag"]}


def interval(values):
    v = np.asarray(values, dtype=float)
    draws = np.random.default_rng(910).integers(len(v), size=(10000, len(v)))
    return {"mean": float(v.mean()), "ci95": np.quantile(v[draws].mean(1), [.025, .975]).tolist(),
            "n_contexts": len(v)}


def analyze(dest):
    rows=[json.loads(s) for s in (dest/'behavior.jsonl').read_text().splitlines()]
    run=json.loads((dest/'run.json').read_text());assert len(rows)==run['args']['n']
    gold=np.array([r['gold'] for r in rows]);out={'n_contexts':len(rows),'metrics':{},'rule_dependence':{},'contrasts':{}}
    z={k:np.array([r['conditions'][k]['z'] for r in rows]) for k in rows[0]['conditions']}
    modes=[k.removeprefix('conflict_') for k in z if k.startswith('conflict_')];ds={}
    for k in z:
        out['metrics'][k]={'accuracy':interval(((z[k]>0)==(gold>0)).mean(1)),
             'argmax_label_rate':interval([np.mean(r['conditions'][k]['argmax_is_label']) for r in rows]),
             'argmax_accuracy':interval([np.mean(r['conditions'][k]['argmax_correct']) for r in rows])}
    for k in modes:
        ds[k]=((z['aligned_'+k]-z['conflict_'+k])*gold).mean(1)
        out['rule_dependence'][k]={'signed':interval(ds[k]),'absolute':interval(abs(ds[k])),
            'per_context':ds[k].tolist(),'flip_rate':interval(((z['aligned_'+k]>0)!=(z['conflict_'+k]>0)).mean(1))}
    for l,r in [('shared_gate','far_gate'),('shared_gate','far_label'),('shared_gate','input_mediated_label'),
                ('held_shared_input_far_label','far_label'),('input_mediated_label','far_label'),
                ('shared_gate','full_A')]:
        out['contrasts'][l+'_minus_'+r]={'absolute_rule_effect':interval(abs(ds[l])-abs(ds[r])),
                                         'signed_rule_effect':interval(ds[l]-ds[r])}
    (dest/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
    for k in modes:print(k,out['rule_dependence'][k]['absolute'],flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/tmp/ices_models/Qwen3-8B")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--seed", type=int, default=106001)
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--analyze-only", action="store_true")
    args = ap.parse_args()
    dest = Path(args.out)
    if args.analyze_only:
        analyze(dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    assert not (dest / "behavior.jsonl").exists()
    rng = np.random.default_rng(args.seed)
    cs = contexts(pools()["test"], args.n, rng, nq=4)
    for ctx in cs:
        ctx["reverse"] = bool(rng.integers(2))
        if ctx["reverse"]:
            ctx["demos"] = [(t, role, 1-y) for t, role, y in ctx["demos"]]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda t: tok.encode(t, add_special_tokens=False)
    word_ids = {k: [enc(" "+w) for w in v] for k, v in WORDS.items()}
    assert all(len(i) == 1 for pair in word_ids.values() for i in pair)
    label_ids = [x[0] for x in word_ids["shared"]]

    def prefix(ctx, ns, aligned=False, instruction=False):
        head = HEAD
        if instruction:
            head += "Use only the examples of the requested annotator to infer and apply that annotator's labeling rule.\n\n"
        ids = enc(head); roles = [-1]*len(ids); anchors = []; input_idx=[]
        for (text, role, y), name in zip(ctx["demos"], ctx["shown"]):
            if aligned and role == 1:
                y = 1-y
            block_text=f"Comment: {text}\nAnnotator: {name}\nLabel:"
            block=enc(block_text)
            annotated=tok(block_text,add_special_tokens=False,return_offsets_mapping=True)
            assert annotated['input_ids']==block
            if role==0:
                left=len('Comment: ');right=left+len(text)
                input_idx += [len(ids)+i for i,(a,b) in enumerate(annotated['offset_mapping']) if a<right and b>left]
            anchors.append(len(ids)+len(block))
            block += enc(" "+WORDS[ns if role == 1 else "shared"][y])+enc("\n\n")
            ids += block; roles += [role]*len(block)
        return ids, roles, anchors, input_idx

    encoded = []
    for ctx in cs:
        e = {(ns, world): prefix(ctx, ns, aligned=(world == "aligned"))
             for ns in WORDS for world in ["conflict", "aligned"]}
        ref, roles, anchors, inputs = e["shared", "conflict"]
        b_anchor = {i for i, d in zip(anchors, ctx["demos"]) if d[1] == 1}
        for ids, r, a, ii in e.values():
            assert len(ids) == len(ref) and r == roles and a == anchors and ii == inputs
            assert {i for i,(x,y) in enumerate(zip(ids,ref)) if x != y} <= b_anchor
        assert len(b_anchor) == 8
        encoded.append(e)
    preflight = {"args": vars(args), "word_ids": word_ids,
                 "prefix_lengths": [len(e["shared", "conflict"][0]) for e in encoded],
                 "current_source_changed_tokens": 0, "foreign_source_label_counts": [4,4],
                 "reversed_contexts": sum(c["reverse"] for c in cs),
                 "patch_scope": "A comment-content layer-input trajectories mediate recomputed A label KV; nonlabel query sources remain pristine shared.",
                 "modes": ["shared_native", "far_native", "shared_gate", "far_gate", "full_A", "far_label", "input_mediated_label", "held_shared_input_far_label", "instruction"]}
    (dest / "preflight.json").write_text(json.dumps(preflight, indent=2)+"\n")
    (dest / "contexts.jsonl").write_text("".join(json.dumps(c)+"\n" for c in cs))
    if args.preflight_only:
        print("All namespace/rule pairs aligned; A tokens invariant.", flush=True)
        return
    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    torch.manual_seed(0)
    started = time.time()
    print("Loading model", flush=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
        dtype=torch.float32, device_map="cuda", attn_implementation="eager").eval()
    model.requires_grad_(False)
    print("Model loaded", flush=True)

    active={'capture':None,'replace':None,'idx':None};covered={i:0 for i in range(len(model.model.layers))}
    def hook(module,args,kwargs,i):
        if active['capture'] is None and active['replace'] is None:return args,kwargs
        h=kwargs.get('hidden_states',args[0] if args else None);assert h is not None and h.shape[0]==1
        if active['capture'] is not None:active['capture'][i]=h[:,active['idx']].detach().clone()
        if active['replace'] is not None:
            h=h.clone();h[:,active['idx']]=active['replace'][i];covered[i]+=1
            if args:args=(h,)+args[1:]
            else:kwargs=dict(kwargs,hidden_states=h)
        return args,kwargs
    handles=[layer.register_forward_pre_hook(lambda m,a,k,_i=i:hook(m,a,k,_i),with_kwargs=True)
             for i,layer in enumerate(model.model.layers)]
    def prefill(ids,capture=None,replace=None,idx=None):
        active.update(capture=capture,replace=replace,idx=idx)
        try:return model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
        finally:active.update(capture=None,replace=None,idx=None)

    def query(cache, roles, queries, gate=False):
        plen, n, qlen = len(roles), len(queries), max(map(len,queries))
        ids = torch.zeros((n,qlen), dtype=torch.long, device="cuda")
        pos = torch.zeros_like(ids); live = torch.zeros_like(ids, dtype=torch.bool)
        for i, q in enumerate(queries):
            ids[i,-len(q):] = torch.tensor(q,device="cuda")
            pos[i,-len(q):] = torch.arange(plen,plen+len(q),device="cuda")
            live[i,-len(q):] = True
        keep = torch.ones(plen,dtype=torch.bool,device="cuda")
        if gate:
            keep = torch.tensor(roles,device="cuda") != 1
        allowed = torch.cat([keep[None,None].expand(n,qlen,-1),
                             live[:,None].expand(-1,qlen,-1) & torch.ones((qlen,qlen),dtype=torch.bool,device="cuda").tril()[None]],dim=-1)
        mask = torch.zeros(allowed.shape,dtype=torch.float32,device="cuda")
        mask.masked_fill_(~allowed,float("-inf"))
        cp = copy.deepcopy(cache); cp.batch_repeat_interleave(n)
        lo = model(input_ids=ids,position_ids=pos,attention_mask=mask[:,None],
                   past_key_values=cp,use_cache=True,logits_to_keep=1).logits[:,-1].float()
        top = lo.argmax(-1)
        return {"z":(lo[:,label_ids[1]]-lo[:,label_ids[0]]).cpu().tolist(),
                "argmax_token":top.cpu().tolist(),
                "argmax_is_label":((top==label_ids[0])|(top==label_ids[1])).cpu().tolist()}

    def patch(base, donor, roles, kind, scope=None):
        cp = copy.deepcopy(base)
        idx = [i for i,r in enumerate(roles) if r==0] if scope is None else scope
        assert base.get_seq_length() == donor.get_seq_length()
        for dst, src in zip(cp.layers,donor.layers):
            if "k" in kind:
                dst.keys[...,idx,:] = src.keys[...,idx,:]
            if "v" in kind:
                dst.values[...,idx,:] = src.values[...,idx,:]
        return cp

    errors = []
    with torch.inference_mode(), (dest/"behavior.jsonl").open("w") as stream:
        for ci, ctx in enumerate(cs):
            qs = [enc(f"Comment: {t}\nAnnotator: {ctx['names'][0]}\nLabel:") for t,_ in ctx["q"]]
            gold = [(-1 if ctx["reverse"] else 1)*(1 if k=="race" else -1) for _,k in ctx["q"]]
            conditions = {}
            for world in ["conflict","aligned"]:
                si, roles, anchors, inputs = encoded[ci]["shared",world]
                fi, _, _, _ = encoded[ci]["far",world]
                labels=[i for i,d in zip(anchors,ctx['demos']) if d[1]==0]
                sh,fh={},{}
                sc,fc=prefill(si,capture=sh,idx=inputs),prefill(fi,capture=fh,idx=inputs)
                assert set(sh)==set(fh)==set(covered)
                sm=prefill(si,replace=fh,idx=inputs)
                fm=prefill(fi,replace=sh,idx=inputs)
                if ci==0:
                    self_cache=prefill(si,replace=sh,idx=inputs)
                    assert all(torch.equal(a.keys,b.keys) and torch.equal(a.values,b.values) for a,b in zip(sc.layers,self_cache.layers))
                # Immutable source cache guard; hash selected tensor bytes rather than retaining clones.
                def finger(cache):
                    hh=hashlib.sha256()
                    for layer in cache.layers:
                        for v in (layer.keys,layer.values):hh.update(v.cpu().numpy().tobytes())
                    return hh.hexdigest()
                sc_hash,fc_hash=finger(sc),finger(fc)
                for ns, cache in [("shared",sc),("far",fc)]:
                    for gate in [False,True]:
                        mode = f"{ns}_{'gate' if gate else 'native'}"
                        conditions[f"{world}_{mode}"] = query(cache,roles,qs,gate)
                for mode, donor, scope in [('full_A',fc,None),('far_label',fc,labels),
                    ('input_mediated_label',sm,labels),('held_shared_input_far_label',fm,labels)]:
                    conditions[f"{world}_{mode}"] = query(patch(sc,donor,roles,'kv',scope),roles,qs,True)
                assert finger(sc)==sc_hash and finger(fc)==fc_hash
                assert all(torch.equal(a.keys[...,inputs,:],b.keys[...,inputs,:]) and torch.equal(a.values[...,inputs,:],b.values[...,inputs,:])
                    for a,b in zip(patch(sc,sm,roles,'kv',labels).layers,sc.layers))
                ii, ir, _, _ = prefix(ctx,"shared",aligned=(world=="aligned"),instruction=True)
                conditions[f"{world}_instruction"] = query(prefill(ii),ir,qs)
                error = max(abs(x-y) for x,y in zip(conditions[f"{world}_full_A"]["z"],conditions[f"{world}_far_gate"]["z"]))
                errors.append(error)
                if ci==0 and world=="conflict":
                    full = si+qs[0]
                    direct = model(input_ids=torch.tensor([full],device="cuda"),use_cache=False,logits_to_keep=1).logits[0,-1]
                    dz = float(direct[label_ids[1]]-direct[label_ids[0]])
                    errors.append(abs(dz-conditions["conflict_shared_native"]["z"][0]))
                assert max(errors)<=.001, errors
            for v in conditions.values():
                v["argmax_correct"] = [t==label_ids[int(g>0)] for t,g in zip(v["argmax_token"],gold)]
            stream.write(json.dumps({"context":ci,"gold":gold,"conditions":conditions})+"\n"); stream.flush()
            print(ci+1,"/",args.n,"numeric",max(errors),flush=True)
    elapsed = time.time()-started
    run = {"args":vars(args),"numeric_max_error":max(errors),"elapsed_seconds":elapsed,"gpu_hours":elapsed/3600,
           "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "contexts_sha256":hashlib.sha256((dest/"contexts.jsonl").read_bytes()).hexdigest(),
           "python":platform.python_version(),"torch":torch.__version__,"transformers":transformers.__version__,
           "git_head":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
           "model_revision":"b968826d9c46dd6066d109eabc6255188de91218","dtype":"float32","attention":"eager",
           "training":False,"patch_layers":"all","input_trajectory_calls":covered,"self_trajectory_cache_exact":True,"pristine_source_cache_exact":True,"query_source_gate_scope":"all query positions"}
    (dest/"run.json").write_text(json.dumps(run,indent=2)+"\n")
    analyze(dest)


if __name__=="__main__":
    main()
