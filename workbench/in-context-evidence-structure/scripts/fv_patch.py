"""E17: does the in-context task vector itself integrate evidence over time?

For a context C (demos + query), take the residual-stream state at the last prompt token after
layer L: theta(C).  Patch theta into a zero-shot prompt (header + new query only) at the same
position/layer, then score the two candidate answers of the NEW query (B-regime vs A-regime).

Layer selection (calibration, disjoint bases): contexts 'allA' vs 'allB' -> choose L maximising the
patched-prompt contrast  lo_B(theta(allB)) - lo_B(theta(allA)).  Test patterns are never used to
choose L.

usage: fv_patch.py --model M --data DATA_DIR --fmt arith --out OUT.json [--n_cal 40 --n_test 200]
Supported formats: arith (x->x+-3), mag_nat (small/large classification), parity_nat.
"""
import argparse, json, re
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
TEST_PATS = ["allA", "suffix_4", "disp_4", "noise_2__suffix_3", "suffix_3", "block_start4",
             "block_late4_return2", "single_1", "single_16", "suffix_8"]


def zero_shot(r, fmt, rng):
    """Header + a new query (not in the demos) and its two candidate answers (A, B)."""
    p = r["prompt"]
    header = p.split("\n\n")[0] + "\n\n"
    if fmt == "arith":
        used = set(r["base"]["xs"]) | {r["base"]["q"]}
        q = int(rng.choice([x for x in range(20, 80) if x not in used]))
        sgn = r["base"]["sgn"]
        return header + f"Input: {q}\nOutput:", [f" {q + 3 * sgn}", f" {q - 3 * sgn}"]
    used = set(r["base"]["xs"]) | {r["base"]["q"]}
    q = int(rng.choice([x for x in range(20, 80) if x not in used]))
    lw = r["base"]["lw"]; s = r["base"]["s"]
    cls = (q % 2) if fmt.startswith("parity") else int(q >= 50)
    yA = cls ^ s
    return header + f"Number: {q}\nLabel:", [" " + lw[yA], " " + lw[1 - yA]]


def make_allB(r, fmt):
    """Rebuild the context with every demo labelled by the B regime (calibration only)."""
    header = r["prompt"].split("\n\n")[0] + "\n\n"
    b = r["base"]; xs = b["xs"]; q = b["q"]
    if fmt == "arith":
        sgn = b["sgn"]
        body = "".join(f"Input: {x}\nOutput: {x - 3 * sgn}\n\n" for x in xs)
        return header + body + f"Input: {q}\nOutput:"
    lw = b["lw"]; s = b["s"]
    cls = (lambda x: x % 2) if fmt.startswith("parity") else (lambda x: int(x >= 50))
    body = "".join(f"Number: {x}\nLabel: {lw[1 - (cls(x) ^ s)]}\n\n" for x in xs)
    return header + body + f"Number: {q}\nLabel:"


def seq_scores(model, tok, prompt, cands, layer=None, theta=None):
    """log P(cand + '\\n\\n' | prompt) for each cand, optionally patching theta at the prompt's last
    position after `layer`."""
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    out = []
    for c in cands:
        full = tok(prompt + c + "\n\n", add_special_tokens=False)["input_ids"]
        k = 0
        while k < min(len(p_ids), len(full)) and p_ids[k] == full[k]:
            k += 1
        pos = len(p_ids) - 1
        h = None
        if layer is not None:
            def hook(mod, inp, outp):
                hs = outp[0] if isinstance(outp, tuple) else outp
                hs[:, pos, :] = theta.to(hs.dtype)
                return outp
            h = model.model.layers[layer].register_forward_hook(hook)
        with torch.no_grad():
            lg = model(torch.tensor([full]).cuda()).logits[0].float()
        if h is not None:
            h.remove()
        lp = torch.log_softmax(lg, -1)
        tgt = torch.tensor(full[k:]).cuda()
        out.append(float(lp[torch.arange(k - 1, len(full) - 1), tgt].sum()))
    return out


def theta_of(model, tok, prompt, layers):
    ids = tok(prompt, add_special_tokens=False)["input_ids"]
    with torch.no_grad():
        o = model(torch.tensor([ids]).cuda(), output_hidden_states=True)
    return {L: o.hidden_states[L + 1][0, -1].clone() for L in layers}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--data"); ap.add_argument("--fmt"); ap.add_argument("--out")
    ap.add_argument("--n_cal", type=int, default=40); ap.add_argument("--n_test", type=int, default=200)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda").eval()
    nL = model.config.num_hidden_layers
    rows = {}
    for l in open(ROOT / "data" / a.data / "rows.jsonl"):
        r = json.loads(l)
        g, p = r["cond"].split(":", 1)
        if g == a.fmt:
            rows.setdefault(r["base_id"], {})[p] = r
    bases = sorted(rows)
    rng = np.random.default_rng(0)
    cal, test = bases[:a.n_cal], bases[a.n_cal:a.n_cal + a.n_test]
    # calibration: build allB by flipping allA labels via the suffix_16-like pattern if absent
    layers = list(range(4, nL - 2, 2))
    con = {L: [] for L in layers}
    for b in cal:
        rA = rows[b]["allA"]
        zs, cands = zero_shot(rA, a.fmt, rng)
        tA = theta_of(model, tok, rA["prompt"], layers); tB = theta_of(model, tok, make_allB(rA, a.fmt), layers)
        for L in layers:
            sA = seq_scores(model, tok, zs, cands, L, tA[L]); sB = seq_scores(model, tok, zs, cands, L, tB[L])
            con[L].append((sB[1] - sB[0]) - (sA[1] - sA[0]))
    cm = {L: float(np.mean(v)) for L, v in con.items()}
    Lbest = max(cm, key=cm.get)
    print("calibration contrast by layer:", {L: round(v, 2) for L, v in cm.items()}, "-> L*", Lbest, flush=True)
    res = {"layer": Lbest, "cal": cm, "test": {}}
    for i, b in enumerate(test):
        zs, cands = zero_shot(rows[b]["allA"], a.fmt, rng)
        base0 = seq_scores(model, tok, zs, cands)
        for p in TEST_PATS:
            if p not in rows[b]:
                continue
            th = theta_of(model, tok, rows[b][p]["prompt"], [Lbest])[Lbest]
            s = seq_scores(model, tok, zs, cands, Lbest, th)
            res["test"].setdefault(p, []).append(s[1] - s[0])
        res["test"].setdefault("_zeroshot", []).append(base0[1] - base0[0])
        if i % 20 == 0:
            print(i, flush=True)
    json.dump(res, open(a.out, "w"))
    T = res["test"]
    d = lambda x, y: np.mean(np.array(T[x]) - np.array(T[y]))
    print({p: round(float(np.mean(v)), 2) for p, v in T.items()})
    print("suffix4-disp4", d("suffix_4", "disp_4"), "noise2", d("noise_2__suffix_3", "suffix_3"),
          "late-start block", d("block_late4_return2", "block_start4"), "last-first", d("single_16", "single_1"))


if __name__ == "__main__":
    main()
