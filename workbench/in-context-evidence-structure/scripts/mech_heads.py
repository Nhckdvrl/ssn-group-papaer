"""E36: per-head direct logit attribution (DLA) at the answer position + answer->demo-label attention.

usage: mech_heads.py --model M --data ctxeffect --out NPZ [--n_bases 150] [--limit N]
For every prompt: dla_head [L, H] and dla_mlp [L] on direction W_U[label1] - W_U[label0] (after the final RMSNorm
scale of the actual final residual), total logit diff, and attention from the last position to each demo label
token [L, H, n_demos].  Labels must be single tokens (Qwen family)."""
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
    rows = [r for r in rows if r["base_id"] in sel]
    if a.limit:
        rows = rows[:a.limit]
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="eager").eval()
    cfg = model.config; L = cfg.num_hidden_layers; H = cfg.num_attention_heads; dh = getattr(cfg, "head_dim", cfg.hidden_size // H)
    W_U = model.lm_head.weight; norm = model.model.norm
    cap = {}

    def pre_o(l):
        def f(mod, args):
            cap[("z", l)] = args[0][0, -1].detach().float()            # [H*dh]
        return f

    def post_attn(l):
        def f(mod, args, out):
            w = out[1]
            if w is not None:
                cap[("att", l)] = w[0, :, -1, :].detach().float()     # [H, T]
        return f

    def post_mlp(l):
        def f(mod, args, out):
            cap[("mlp", l)] = out[0, -1].detach().float()
        return f

    def pre_norm(mod, args):
        cap["resid"] = args[0][0, -1].detach().float()

    hs = []
    for l, layer in enumerate(model.model.layers):
        hs.append(layer.self_attn.o_proj.register_forward_pre_hook(pre_o(l)))
        hs.append(layer.self_attn.register_forward_hook(post_attn(l)))
        hs.append(layer.mlp.register_forward_hook(post_mlp(l)))
    hs.append(norm.register_forward_pre_hook(pre_norm))
    Wo = [layer.self_attn.o_proj.weight.float() for layer in model.model.layers]   # [D, H*dh]
    out = {"uid": [], "dla_head": [], "dla_mlp": [], "logit_diff": [], "att_lab": [], "lab_pos_ok": []}
    for i, r in enumerate(rows):
        c0 = tok(r["cands"][0], add_special_tokens=False).input_ids; c1 = tok(r["cands"][1], add_special_tokens=False).input_ids
        assert len(c0) == 1 and len(c1) == 1, r["cands"]
        d = (W_U[c1[0]] - W_U[c0[0]]).float()
        enc = tok(r["prompt"], return_offsets_mapping=True, return_tensors="pt")
        offs = enc.pop("offset_mapping")[0].tolist()
        # demo label token positions: the token that starts at the space before each demo label word
        starts = [m.start(1) for m in re.finditer(r"Label: (\S+)\n", r["prompt"])]
        pos = []
        for st in starts:
            k = next((j for j, (s_, e_) in enumerate(offs) if s_ <= st - 1 < e_ or s_ == st), None); pos.append(k)
        ok = all(p is not None for p in pos)
        with torch.no_grad():
            lo = model(**{k: v.cuda() for k, v in enc.items()}, output_attentions=True).logits[0, -1].float()
        resid = cap["resid"]; scale = norm.weight.float() / torch.sqrt(resid.pow(2).mean() + norm.variance_epsilon)
        dd = d * scale
        dla_h = np.zeros((L, H), np.float32); dla_m = np.zeros(L, np.float32); att = np.zeros((L, H, len(pos)), np.float32)
        for l in range(L):
            z = cap[("z", l)].view(H, dh)
            ho = torch.einsum("dhk,hk->hd", Wo[l].view(-1, H, dh), z)          # [H, D]
            dla_h[l] = (ho @ dd).cpu().numpy()
            dla_m[l] = float(cap[("mlp", l)] @ dd)
            if ok and ("att", l) in cap:
                att[l] = cap[("att", l)][:, pos].cpu().numpy()
        out["uid"].append(r["uid"]); out["dla_head"].append(dla_h); out["dla_mlp"].append(dla_m)
        out["logit_diff"].append(float(lo[c1[0]] - lo[c0[0]])); out["att_lab"].append(att); out["lab_pos_ok"].append(ok)
        if i % 200 == 0:
            print(i, len(rows), f"recon {dla_h.sum() + dla_m.sum():+.2f} vs {out['logit_diff'][-1]:+.2f}", flush=True)
    np.savez_compressed(a.out, uid=np.array(out["uid"]), dla_head=np.stack(out["dla_head"]), dla_mlp=np.stack(out["dla_mlp"]),
                        logit_diff=np.array(out["logit_diff"]), att_lab=np.stack(out["att_lab"]), lab_pos_ok=np.array(out["lab_pos_ok"]))
    print("done", len(rows))


if __name__ == "__main__":
    main()
