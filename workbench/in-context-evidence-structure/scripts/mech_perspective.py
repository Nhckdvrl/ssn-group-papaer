"""E48: in real perspectivist prompts (E46), where does the other annotator's influence enter?
Per head, the direct contribution to the query's (toxic - safe) logit direction is split by source position into:
own-annotator label anchors, other-annotator label anchors, and everything else; attention mass on each group too.
usage: mech_perspective.py --model Qwen/Qwen3-8B --out NPZ [--pairs 40 --queries 20]
Conditions: mixed (shared words) and mixed_far (B: flag/pass); query annotator A and B."""
import argparse, sys
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from e46_perspective import build, HEAD, WORDS  # noqa


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--out"); ap.add_argument("--pairs", type=int, default=40)
    ap.add_argument("--queries", type=int, default=20)
    a = ap.parse_args()
    pairs, qs = build(120)
    pairs = pairs[: a.pairs]; qs = qs[: a.queries]
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="eager").eval()
    cfg = model.config; L = cfg.num_hidden_layers; H = cfg.num_attention_heads; KV = cfg.num_key_value_heads
    dh = getattr(cfg, "head_dim", None) or cfg.hidden_size // H; rep = H // KV
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    cap = {}
    for l, layer in enumerate(model.model.layers):
        layer.self_attn.v_proj.register_forward_hook(lambda m, i, o, l=l: cap.__setitem__(("v", l), o[0].float()))
        layer.self_attn.register_forward_hook(lambda m, i, o, l=l: cap.__setitem__(("a", l), o[1][0, :, -1, :].float()))
    model.model.norm.register_forward_pre_hook(lambda m, i: cap.__setitem__("resid", i[0][0, -1].float()))
    Wo = [layer.self_attn.o_proj.weight.float() for layer in model.model.layers]
    W_U = model.lm_head.weight
    recs = []
    for pi, p in enumerate(pairs):
        nA, nB = p["names"]
        for c, vB in (("mixed", "shared"), ("mixed_far", "far")):
            blocks = [(t, nA, WORDS["shared"][1 - y], 0) for t, y in p["A"]] + [(t, nB, WORDS[vB][1 - y], 1) for t, y in p["B"]]
            blocks = [blocks[j] for j in p["order"]]
            ids = enc(HEAD); anchor = []
            for t, name, w, who in blocks:
                pre = enc(f"Comment: {t}\nAnnotator: {name}\nLabel:"); ids += pre
                anchor.append((len(ids), who)); ids += enc(" " + w) + enc("\n\n")
            for wi in (0, 1):
                name = nA if wi == 0 else nB; words = WORDS["shared"] if wi == 0 else WORDS[vB]
                d = (W_U[enc(" " + words[0])[0]] - W_U[enc(" " + words[1])[0]]).float()
                for qi, qt in enumerate(qs):
                    full = ids + enc(f"Comment: {qt}\nAnnotator: {name}\nLabel:")
                    lo = model(input_ids=torch.tensor([full]).cuda(), output_attentions=True).logits[0, -1].float()
                    r = cap["resid"]; norm = model.model.norm
                    dd = d * norm.weight.float() / torch.sqrt(r.pow(2).mean() + norm.variance_epsilon)
                    own = torch.tensor([pos for pos, who in anchor if who == wi]).cuda()
                    oth = torch.tensor([pos for pos, who in anchor if who != wi]).cuda()
                    contrib = np.zeros((L, H, 3), np.float32); att = np.zeros((L, H, 2), np.float32)
                    for l in range(L):
                        A = cap[("a", l)]                                      # [H, T]
                        V = cap[("v", l)].view(-1, KV, dh)                     # [T, KV, dh]
                        Vh = V.repeat_interleave(rep, dim=1)                   # [T, H, dh]
                        WoH = Wo[l].T.reshape(H, dh, -1)                       # [H, dh, D]
                        vd = torch.einsum("thd,hdm,m->th", Vh, WoH, dd)        # per position, per head contribution weight
                        tot = (A.T * vd)                                       # [T, H]
                        contrib[l, :, 0] = tot[own].sum(0).cpu().numpy(); contrib[l, :, 1] = tot[oth].sum(0).cpu().numpy()
                        contrib[l, :, 2] = (tot.sum(0) - tot[own].sum(0) - tot[oth].sum(0)).cpu().numpy()
                        att[l, :, 0] = A[:, own].sum(-1).cpu().numpy(); att[l, :, 1] = A[:, oth].sum(-1).cpu().numpy()
                    recs.append({"pair": pi, "cond": c, "who": wi, "q": qi, "ld": float(lo[enc(" " + words[0])[0]] - lo[enc(" " + words[1])[0]]),
                                 "contrib": contrib, "att": att})
        print(pi, flush=True)
    np.savez_compressed(a.out, pair=np.array([r["pair"] for r in recs]), cond=np.array([r["cond"] for r in recs]),
                        who=np.array([r["who"] for r in recs]), q=np.array([r["q"] for r in recs]), ld=np.array([r["ld"] for r in recs]),
                        contrib=np.stack([r["contrib"] for r in recs]), att=np.stack([r["att"] for r in recs]))
    print("done")


if __name__ == "__main__":
    main()
