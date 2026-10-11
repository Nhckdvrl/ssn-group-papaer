"""E56d: where does the E56 query-only module act?  (a) enable the module only on one layer group at a time;
(b) per head, change in attention share to same-source anchors (adapter on vs off), on E56 test contexts.
usage: e56d_dissect.py --model Qwen/Qwen3-8B --weights results/e56/Qwen3-8B_query_saved.pt --out JSON [--n 30]"""
import argparse, json, sys
from pathlib import Path
import numpy as np, torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--weights"); ap.add_argument("--out"); ap.add_argument("--n", type=int, default=30)
    a = ap.parse_args()
    import e56_query_adapter as e56
    from transformers import AutoModelForCausalLM, AutoTokenizer
    ctxs = e56.contexts(e56.pools()["test"], a.n, np.random.default_rng(2))
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="eager").eval()
    L = model.config.num_hidden_layers; H = model.config.num_attention_heads; L1 = L // 2 - 2
    W = torch.load(a.weights); mods = {l: (W[2 * i].cuda(), W[2 * i + 1].cuda()) for i, l in enumerate(range(L1, L))}
    state = {"layers": set()}
    def qhook(l):
        def f(mod, inp, out):
            if l not in state["layers"]:
                return out
            x = inp[0][:, -1].float(); out = out.clone(); d_, u_ = mods[l]; out[:, -1] = out[:, -1] + ((x @ d_.T) @ u_.T).to(out.dtype)
            return out
        return f
    for l in range(L1, L):
        model.model.layers[l].self_attn.q_proj.register_forward_hook(qhook(l))
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    TOX, SAFE = enc(" toxic")[0], enc(" safe")[0]
    HEAD = "Below are comments and the labels that individual annotators gave them.\n\n"
    groups = {"none": set(), "all": set(range(L1, L))}
    for s in range(L1, L, 4):
        groups[f"{s}-{s + 3}"] = set(range(s, min(s + 4, L)))
    sep = {g: [] for g in groups}; share = {"off": np.zeros((L, H)), "on": np.zeros((L, H))}; cnt = 0
    for ctx in ctxs:
        ids, anchors = enc(HEAD), []
        for (t, role, y), s_ in zip(ctx["demos"], ctx["shown"]):
            ids += enc(f"Comment: {t}\nAnnotator: {s_}\nLabel:"); anchors.append((len(ids), role)); ids += enc(" " + ("toxic" if y else "safe")) + enc("\n\n")
        kinds = np.array([k == "race" for _, k in ctx["q"]])
        for g, layers in groups.items():
            state["layers"] = layers; I_ = []
            for role in (0, 1):
                lds = []
                for qt, _ in ctx["q"]:
                    full = ids + enc(f"Comment: {qt}\nAnnotator: {ctx['names'][role]}\nLabel:")
                    o = model(input_ids=torch.tensor([full]).cuda(), output_attentions=(g in ("none", "all")))
                    lds.append(float(o.logits[0, -1, TOX] - o.logits[0, -1, SAFE]))
                    if g in ("none", "all"):
                        own = [p for p, r in anchors if r == role]; oth = [p for p, r in anchors if r != role]
                        for l in range(L):
                            at = o.attentions[l][0, :, -1].float()
                            so, sx = at[:, own].sum(-1), at[:, oth].sum(-1)
                            share["off" if g == "none" else "on"][l] += (so / (so + sx + 1e-9)).cpu().numpy()
                        if g == "none":
                            cnt += 1
                lds = np.array(lds); I_.append(lds[kinds].mean() - lds[~kinds].mean())
            sep[g].append(I_[0] - I_[1])
        print(len(sep["none"]), {g: round(float(np.mean(v)), 2) for g, v in sep.items()}, flush=True)
    state["layers"] = set()
    d = (share["on"] - share["off"]) / cnt
    top = np.argsort(-d.ravel())[:15]
    out = {"sep_by_group": {g: float(np.mean(v)) for g, v in sep.items()},
           "share_off_mean": float((share["off"] / cnt)[L1:].mean()), "share_on_mean": float((share["on"] / cnt)[L1:].mean()),
           "top15_heads_share_increase": [[f"{k // H}.{k % H}", round(float(d.ravel()[k]), 3), round(float((share['off'] / cnt).ravel()[k]), 3)] for k in top]}
    Path(a.out).write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
