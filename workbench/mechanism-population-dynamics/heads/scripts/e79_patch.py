"""E79b: where does memory enter under a conflicting context? Causal patching real <- nonce.

For each item: conflict prompt with the real subject (R) and the nonce subject (N); identical context answer o' and
candidates. Readout: final-position first-token logit difference LD = logit[o'] - logit[o].
Patch sites (GPTNeoX layer outputs, layer l):
  ctx   - residual at the context-answer tokens (the copied span) of R replaced by N's at the same span
  final - residual at the final position of R replaced by N's
Gap closed = (LD_patched - LD_R) / (LD_N - LD_R), averaged over items whose LD_N - LD_R > 0.5 (memory actually survives).
Usage: e79_patch.py --repo EleutherAI/pythia-410m --rev 143000 --n 400
"""
import argparse
import json

import numpy as np
import torch

import mp_common as mc

OUT = mc.RESULTS / "e79"


def spans(tok, prompt, dist):
    enc = tok(prompt, add_special_tokens=False, return_offsets_mapping=True)
    c0 = prompt.index(dist)
    sp = [j + 1 for j, (a, b) in enumerate(enc["offset_mapping"]) if b > c0 and a < c0 + len(dist)]
    return [tok.eos_token_id] + enc["input_ids"], sp


def run(repo, rev, n, every):
    from transformers import AutoTokenizer
    torch.set_grad_enabled(False)
    model = mc.load_hf_model(repo, int(rev), dtype=torch.float32, check_manifest=False).cuda()
    tok = AutoTokenizer.from_pretrained(repo, cache_dir=str(mc.HF_CACHE))
    layers = model.gpt_neox.layers
    Ls = list(range(0, len(layers), every)) + ([len(layers) - 1] if (len(layers) - 1) % every else [])
    I = json.loads((mc.RESULTS / "e77" / "items.json").read_text())
    rng = np.random.default_rng(1)
    sel = sorted(rng.choice(len(I), min(n, len(I)), replace=False).tolist())
    store, patch = {}, {}

    def mk(l):
        def f(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            if "cap" in store:
                store["cap"][l] = h[0].detach().clone()
            if l in patch:
                src, dst = patch[l]
                h[0, dst] = src
            return out
        return f
    hs = [layer.register_forward_hook(mk(l)) for l, layer in enumerate(layers)]

    def ld(ids, o, o2):
        lg = model(torch.tensor([ids]).cuda()).logits[0, -1]
        return float(lg[o2] - lg[o])
    rows = []
    for i in sel:
        x = I[i]
        o = tok(" " + x["ans"], add_special_tokens=False)["input_ids"][0]
        o2 = tok(" " + x["dist"], add_special_tokens=False)["input_ids"][0]
        if o == o2:
            continue
        idsR, spR = spans(tok, x["prompts"]["c1_decl"], x["dist"])
        idsN, spN = spans(tok, x["prompts"]["nonce_c1_decl"], x["dist"])
        if len(spR) != len(spN):
            continue
        store["cap"] = {}
        ldN = ld(idsN, o, o2)
        capN = store.pop("cap")
        ldR = ld(idsR, o, o2)
        r = {"i": i, "ldR": ldR, "ldN": ldN, "ctx": {}, "final": {}}
        for l in Ls:
            patch.clear()
            patch[l] = (capN[l][spN], spR)
            r["ctx"][l] = ld(idsR, o, o2)
            patch.clear()
            patch[l] = (capN[l][len(idsN) - 1], len(idsR) - 1)
            r["final"][l] = ld(idsR, o, o2)
        patch.clear()
        rows.append(r)
    for h in hs:
        h.remove()
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f"patch__{repo.split('/')[-1]}__{rev}"
    (OUT / f"{tag}.json").write_text(json.dumps({"layers": Ls, "rows": rows}))
    gap = np.array([r["ldN"] - r["ldR"] for r in rows])
    ok = gap > 0.5
    summ = {"n": len(rows), "n_gap": int(ok.sum()), "mean_gap": float(gap[ok].mean())}
    for site in ("ctx", "final"):
        summ[site] = {l: float(np.mean([(r[site][l] - r["ldR"]) / (r["ldN"] - r["ldR"]) for r, k in zip(rows, ok) if k]))
                      for l in Ls}
    (OUT / f"{tag}.summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--every", type=int, default=2)
    a = ap.parse_args()
    run(a.repo, a.rev, a.n, a.every)
