"""E37: per-anchor value projections.  For every head and every demo label position t:
  vproj[l, h, t] = (W_O[l, h] v_{l,h}(t)) . dd     (what head (l,h) would write toward label1 - label0 if it attended only to t)
  att[l, h, t]   = attention from the answer position to t
so the head's anchor-read contribution is sum_t att * vproj.  dd = (W_U[c1]-W_U[c0]) scaled by the final RMSNorm of
the actual run divided out (dd uses only the norm weight; rms saved separately so that vproj/rms is the logit contribution).  usage: mech_values.py --model M --data D --out NPZ [--n_bases 150] [--limit N]"""
import argparse, json, re
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--data"); ap.add_argument("--out"); ap.add_argument("--n_bases", type=int, default=150)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    root = __file__.rsplit("/", 2)[0]
    rows = [json.loads(l) for l in open(f"{root}/data/{a.data}/rows.jsonl")]
    keep = {}
    for r in rows:
        t = r["cond"].split(":")[0]; keep.setdefault(t, [])
        if r["base_id"] not in keep[t] and len(keep[t]) < a.n_bases:
            keep[t].append(r["base_id"])
    sel = {b for v in keep.values() for b in v}
    rows = [r for r in rows if r["base_id"] in sel][: a.limit or None]
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="eager").eval()
    cfg = model.config; L = cfg.num_hidden_layers; H = cfg.num_attention_heads; KV = cfg.num_key_value_heads
    dh = getattr(cfg, "head_dim", cfg.hidden_size // H); rep = H // KV
    W_U = model.lm_head.weight; norm = model.model.norm
    cap = {}

    def v_hook(l):
        def f(mod, args, out):
            cap[("v", l)] = out[0].detach()                                  # [T, KV*dh]
        return f

    def att_hook(l):
        def f(mod, args, out):
            if out[1] is not None:
                cap[("att", l)] = out[1][0, :, -1, :].detach().float()
        return f

    def pre_norm(mod, args):
        cap["resid"] = args[0][0, -1].detach().float()

    for l, layer in enumerate(model.model.layers):
        layer.self_attn.v_proj.register_forward_hook(v_hook(l)); layer.self_attn.register_forward_hook(att_hook(l))
    norm.register_forward_pre_hook(pre_norm)
    Wo = [layer.self_attn.o_proj.weight.float().view(-1, H, dh) for layer in model.model.layers]   # [D, H, dh]
    out = {"uid": [], "vproj": [], "att": [], "logit_diff": [], "rms": []}
    for i, r in enumerate(rows):
        c0 = tok(r["cands"][0], add_special_tokens=False).input_ids; c1 = tok(r["cands"][1], add_special_tokens=False).input_ids
        assert len(c0) == 1 and len(c1) == 1
        enc = tok(r["prompt"], return_offsets_mapping=True, return_tensors="pt"); offs = enc.pop("offset_mapping")[0].tolist()
        starts = [m.start(1) for m in re.finditer(r"Label: (\S+)\n", r["prompt"])]
        pos = [next(j for j, (s_, e_) in enumerate(offs) if s_ <= st - 1 < e_ or s_ == st) for st in starts]
        lo = model(**{k: v.cuda() for k, v in enc.items()}, output_attentions=True).logits[0, -1].float()
        resid = cap["resid"]; scale = norm.weight.float() / torch.sqrt(resid.pow(2).mean() + norm.variance_epsilon)
        dd = (W_U[c1[0]] - W_U[c0[0]]).float() * norm.weight.float()      # run-independent direction (no 1/rms) for anchor comparisons
        rms = float(torch.sqrt(resid.pow(2).mean() + norm.variance_epsilon))
        vp = np.zeros((L, H, len(pos)), np.float16); at = np.zeros((L, H, len(pos)), np.float16)
        for l in range(L):
            v = cap[("v", l)][pos].float().view(len(pos), KV, dh)                # [P, KV, dh]
            v = v.repeat_interleave(rep, dim=1)                                  # [P, H, dh]
            wd = torch.einsum("dhk,d->hk", Wo[l], dd)                            # [H, dh]  (W_O^T dd per head)
            vp[l] = torch.einsum("phk,hk->hp", v, wd).cpu().numpy()
            at[l] = cap[("att", l)][:, pos].cpu().numpy()
        out["uid"].append(r["uid"]); out["vproj"].append(vp); out["att"].append(at); out["logit_diff"].append(float(lo[c1[0]] - lo[c0[0]])); out["rms"].append(rms)
        if i % 500 == 0:
            print(i, len(rows), flush=True)
    np.savez_compressed(a.out, uid=np.array(out["uid"]), vproj=np.stack(out["vproj"]), att=np.stack(out["att"]), logit_diff=np.array(out["logit_diff"]), rms=np.array(out["rms"]))
    print("done", len(rows))


if __name__ == "__main__":
    main()
