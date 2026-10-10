"""Output namespace and inherited source-rule effects; see E91 preregistration.

A's raw examples and answer vocabulary stay. Only B's label coding changes.
Whole-query A-only reading removes B's direct output positions from all paths.
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
    rows = [json.loads(s) for s in (dest / "behavior.jsonl").read_text().splitlines()]
    run = json.loads((dest / "run.json").read_text())
    assert len(rows) == run["args"]["n"]
    assert [r["context"] for r in rows] == list(range(len(rows)))
    assert run["numeric_max_error"] <= .001
    gold = np.array([r["gold"] for r in rows])
    conditions = list(rows[0]["conditions"])
    z = {k: np.array([r["conditions"][k]["z"] for r in rows]) for k in conditions}
    modes = sorted({k.removeprefix("conflict_") for k in conditions if k.startswith("conflict_")})
    out = {"metrics": {}, "rule_dependence": {}, "contrasts": {},
           "numeric_max_error": run["numeric_max_error"],
           "context_rule_effects": {}}
    for k in conditions:
        out["metrics"][k] = {
            "accuracy": interval(((z[k] > 0) == (gold > 0)).mean(1)),
            "signed_margin": interval((z[k]*gold).mean(1)),
            "argmax_label_rate": interval([np.mean(r["conditions"][k]["argmax_is_label"]) for r in rows]),
            "argmax_accuracy": interval([np.mean(r["conditions"][k]["argmax_correct"]) for r in rows]),
        }
    d = {}
    for k in modes:
        c, a = z[f"conflict_{k}"], z[f"aligned_{k}"]
        d[k] = ((a-c)*gold).mean(1)
        out["context_rule_effects"][k] = d[k].tolist()
        out["rule_dependence"][k] = {
            "signed": interval(d[k]), "absolute": interval(np.abs(d[k])),
            "answer_flip_rate": interval(((a > 0) != (c > 0)).mean(1)),
            "contexts_positive": int((d[k] > .01).sum()), "contexts_negative": int((d[k] < -.01).sum()),
        }
    for left, right in [("shared_native", "far_native"), ("shared_gate", "far_gate"),
                        ("shared_gate", "key_patch"), ("shared_gate", "value_patch"),
                        ("key_patch", "far_gate"), ("value_patch", "far_gate")]:
        out["contrasts"][f"absolute_rule_effect_{left}_minus_{right}"] = interval(np.abs(d[left])-np.abs(d[right]))
        out["contrasts"][f"rule_effect_abs_error_{left}_versus_{right}"] = interval(np.abs(d[left]-d[right]))
        out["contrasts"][f"conflict_margin_{left}_minus_{right}"] = interval(
            ((z[f"conflict_{left}"]-z[f"conflict_{right}"])*gold).mean(1))
        out["contrasts"][f"conflict_accuracy_{left}_minus_{right}"] = interval(
            ((z[f"conflict_{left}"] > 0) == (gold > 0)).mean(1)
            - ((z[f"conflict_{right}"] > 0) == (gold > 0)).mean(1))
    (dest / "analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    for k, v in out["rule_dependence"].items():
        print(k, "rule magnitude", v["absolute"], "accuracy", out["metrics"][f"conflict_{k}"]["accuracy"], flush=True)
    for k, v in out["contrasts"].items():
        if k.startswith("absolute_rule_effect"):
            print(k, v, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/tmp/ices_models/Qwen3-8B")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--seed", type=int, default=91001)
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
        ids = enc(head); roles = [-1]*len(ids); anchors = []
        for (text, role, y), name in zip(ctx["demos"], ctx["shown"]):
            if aligned and role == 1:
                y = 1-y
            block = enc(f"Comment: {text}\nAnnotator: {name}\nLabel:")
            anchors.append(len(ids)+len(block))
            block += enc(" "+WORDS[ns if role == 1 else "shared"][y])+enc("\n\n")
            ids += block; roles += [role]*len(block)
        return ids, roles, anchors

    encoded = []
    for ctx in cs:
        e = {(ns, world): prefix(ctx, ns, aligned=(world == "aligned"))
             for ns in WORDS for world in ["conflict", "aligned"]}
        ref, roles, anchors = e["shared", "conflict"]
        b_anchor = {i for i, d in zip(anchors, ctx["demos"]) if d[1] == 1}
        for ids, r, a in e.values():
            assert len(ids) == len(ref) and r == roles and a == anchors
            assert {i for i,(x,y) in enumerate(zip(ids,ref)) if x != y} <= b_anchor
        assert len(b_anchor) == 8
        encoded.append(e)
    preflight = {"args": vars(args), "word_ids": word_ids,
                 "prefix_lengths": [len(e["shared", "conflict"][0]) for e in encoded],
                 "current_source_changed_tokens": 0, "foreign_source_label_counts": [4,4],
                 "reversed_contexts": sum(c["reverse"] for c in cs),
                 "patch_scope": "All and only target-source A cache positions, at every layer; whole query respects Source mask.",
                 "modes": ["shared_native", "far_native", "shared_gate", "far_gate", "key_patch", "value_patch", "kv_patch", "instruction"]}
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

    def prefill(ids):
        return model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values

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

    def patch(base, donor, roles, kind):
        cp = copy.deepcopy(base)
        idx = [i for i,r in enumerate(roles) if r==0]
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
                si, roles, _ = encoded[ci]["shared",world]
                fi, _, _ = encoded[ci]["far",world]
                sc, fc = prefill(si), prefill(fi)
                for ns, cache in [("shared",sc),("far",fc)]:
                    for gate in [False,True]:
                        mode = f"{ns}_{'gate' if gate else 'native'}"
                        conditions[f"{world}_{mode}"] = query(cache,roles,qs,gate)
                for kind, mode in [("k","key_patch"),("v","value_patch"),("kv","kv_patch")]:
                    conditions[f"{world}_{mode}"] = query(patch(sc,fc,roles,kind),roles,qs,True)
                ii, ir, _ = prefix(ctx,"shared",aligned=(world=="aligned"),instruction=True)
                conditions[f"{world}_instruction"] = query(prefill(ii),ir,qs)
                error = max(abs(x-y) for x,y in zip(conditions[f"{world}_kv_patch"]["z"],conditions[f"{world}_far_gate"]["z"]))
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
           "training":False,"patch_layers":"all","query_source_gate_scope":"all query positions"}
    (dest/"run.json").write_text(json.dumps(run,indent=2)+"\n")
    analyze(dest)


if __name__=="__main__":
    main()
