"""E56b: does the E56 query-only module (trained on race/gender interaction, toxic/safe) transfer, without retraining,
to (1) the flipped rule, (2) E46 real annotators (main effect, toxic/safe), (3) GoEmotions raters (neutral/emotional)?
usage: e56b_transfer.py --model Qwen/Qwen3-8B --weights results/e56/Qwen3-8B_query_saved.pt --mode query|resid --out JSON
For each set: separation D (A vs B) for default-mixed, adapter-mixed, and the single-source upper bound (adapter off),
plus attention share from the answer position to same-source anchors (layers >= L1) with and without the adapter."""
import argparse, copy, json, sys
from pathlib import Path
import numpy as np, torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def sets(n):
    import e56_query_adapter as e56
    out = {}
    P = e56.pools(); rng = np.random.default_rng(3)
    flip = []
    for c in e56.contexts(P["test"], n, rng):
        demos = [(t, role, 1 - y) for t, role, y in c["demos"]]          # flipped rule: A gender toxic, B race toxic
        flip.append({"demos": [(t, role, ("toxic", "safe")[1 - y]) for t, role, y in demos], "names": c["names"],
                     "q": [t for t, _ in c["q"]], "kind": [k for _, k in c["q"]], "words": (("toxic", "safe"), ("toxic", "safe")), "type": "interaction_flipped"})
    out["flip"] = flip
    from e46_perspective import build as b46
    pairs, qs = b46(120)
    out["e46"] = [{"demos": [(t, 0, ("toxic", "safe")[1 - y]) for t, y in p["A"]] + [(t, 1, ("toxic", "safe")[1 - y]) for t, y in p["B"]],
                   "names": p["names"], "q": qs[:12], "words": (("toxic", "safe"), ("toxic", "safe")), "order": p["order"], "type": "main"} for p in pairs[:n]]
    import e49_goemotions as e49
    pairs, qs = e49.build(120)
    out["e49"] = [{"demos": [(t, 0, ("neutral", "emotional")[1 - y]) for t, y in p["A"]] + [(t, 1, ("neutral", "emotional")[1 - y]) for t, y in p["B"]],
                   "names": p["names"], "q": qs[:12], "words": (("neutral", "emotional"), ("neutral", "emotional")), "order": p["order"], "type": "main"} for p in pairs[:n]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--weights"); ap.add_argument("--mode"); ap.add_argument("--out"); ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--rank", type=int, default=8)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    S = sets(a.n)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="eager").eval()
    cfg = model.config; L = cfg.num_hidden_layers; D = cfg.hidden_size; L1 = L // 2 - 2
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    state = {"on": False}
    W = torch.load(a.weights)
    if a.mode == "query":
        QD = model.model.layers[0].self_attn.q_proj.out_features
        mods = {l: (W[2 * i].cuda(), W[2 * i + 1].cuda()) for i, l in enumerate(range(L1, L))}
        def qhook(l):
            def f(mod, inp, out):
                if not state["on"]:
                    return out
                x = inp[0][:, -1].float(); out = out.clone(); d_, u_ = mods[l]
                out[:, -1] = out[:, -1] + ((x @ d_.T) @ u_.T).to(out.dtype)
                return out
            return f
        for l in range(L1, L):
            model.model.layers[l].self_attn.q_proj.register_forward_hook(qhook(l))
    else:
        d_, u_ = W[0].cuda(), W[1].cuda()
        def rhook(m_, inp, out):
            if not state["on"]:
                return out
            h = out[0] if isinstance(out, tuple) else out
            h = h.clone(); h[:, -1] = h[:, -1] + ((h[:, -1].float() @ d_.T) @ u_.T).to(h.dtype)
            return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
        model.model.layers[L1].register_forward_hook(rhook)
    HEAD = "Below are comments and the labels that individual annotators gave them.\n\n"

    @torch.no_grad()
    def score(ctx, role_filter, on):
        demos = [d for d in ctx["demos"] if role_filter is None or d[1] == role_filter]
        if role_filter is None and "order" in ctx:
            demos = [ctx["demos"][j] for j in ctx["order"]]
        elif role_filter is None:
            demos = list(ctx["demos"])
        ids, anchors = enc(HEAD), []
        for t, role, w in demos:
            ids += enc(f"Comment: {t}\nAnnotator: {ctx['names'][role]}\nLabel:"); anchors.append((len(ids), role)); ids += enc(" " + w) + enc("\n\n")
        res = {}
        for role in ((0, 1) if role_filter is None else (role_filter,)):
            w0, w1 = ctx["words"][role]; p0, p1 = enc(" " + w0)[0], enc(" " + w1)[0]
            lds, same_share = [], []
            for qt in ctx["q"]:
                full = ids + enc(f"Comment: {qt}\nAnnotator: {ctx['names'][role]}\nLabel:")
                state["on"] = on
                o = model(input_ids=torch.tensor([full]).cuda(), output_attentions=True)
                state["on"] = False
                l = o.logits[0, -1].float(); lds.append(float(l[p0] - l[p1]))
                own = [p for p, r in anchors if r == role]; oth = [p for p, r in anchors if r != role]
                if oth:
                    att = torch.stack([o.attentions[k][0, :, -1] for k in range(L1, L)]).float()      # [layers, H, T]
                    so, sx = att[..., own].sum(-1), att[..., oth].sum(-1)
                    same_share.append(float((so / (so + sx + 1e-9)).mean()))
            res[role] = (np.array(lds), float(np.mean(same_share)) if same_share else None)
        return res

    out = {"mode": a.mode, "weights": a.weights}
    for name, ctxs in S.items():
        rows = {"default": [], "adapter": [], "single": [], "share_default": [], "share_adapter": []}
        for ctx in ctxs:
            kinds = np.array([k == "race" for k in ctx.get("kind", ["race"] * len(ctx["q"]))])
            def sep(r):
                if ctx["type"].startswith("interaction"):
                    I = lambda v: v[kinds].mean() - v[~kinds].mean()
                    return I(r[0][0]) - I(r[1][0])
                return r[0][0].mean() - r[1][0].mean()
            d0 = score(ctx, None, False); d1 = score(ctx, None, True)
            s0 = {**score(ctx, 0, False), **score(ctx, 1, False)}
            rows["default"].append(sep(d0)); rows["adapter"].append(sep(d1)); rows["single"].append(sep(s0))
            rows["share_default"].append(np.mean([d0[r][1] for r in (0, 1)])); rows["share_adapter"].append(np.mean([d1[r][1] for r in (0, 1)]))
        r = {k: float(np.mean(v)) for k, v in rows.items()}
        if name == "flip":                      # under the flipped rule the A-B interaction sign is reversed
            r = {k: (-v if k in ("default", "adapter", "single") else v) for k, v in r.items()}
        r["retention_default"] = r["default"] / r["single"]; r["retention_adapter"] = r["adapter"] / r["single"]
        out[name] = r
        print(name, {k: round(v, 3) for k, v in r.items()}, flush=True)
    Path(a.out).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
