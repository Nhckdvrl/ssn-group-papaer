"""E07 summary: choice effect without sampling, per problem set, by base solve rate, with swap-content audit.
Reads /tmp/xiang_lmhead/e07/gen/{t_<cond>_<set>.jsonl, a_<model>_<set>.jsonl}; writes results/e07/summary_<pair>.json.
Usage (ices env, on a node with the tokenizer): python e07_summary.py qwen-base__post [--sets math500,math_l5,olymp]"""
import argparse
import json
import random
import re
from pathlib import Path

import models

ROOT = Path(__file__).resolve().parents[1]
GEN = Path("/tmp/xiang_lmhead/e07/gen")
CONDS = ["t_base_basemode", "t_base_postmode", "t_base_postlow", "t_base_basemode_postlow"]   # B1, B2, B3, B4


def load_grid(tag):
    f = GEN / f"{tag}.jsonl"
    if not f.exists():
        return None
    rows = {}
    for l in open(f):
        r = json.loads(l)
        rows[r["index"]] = r
    return rows


def load_anchor(tag):
    f = GEN / f"{tag}.jsonl"
    if not f.exists():
        return None
    out = {}
    for l in open(f):
        r = json.loads(l)
        c = r["completions"]
        out[r["index"]] = {"p": sum(x["reward"] for x in c) / len(c), "trunc": sum(x["finish"] == "length" for x in c) / len(c),
                           "parse_fail": sum(x["pred"] is None for x in c) / len(c), "len": sum(len(x["token_ids"]) for x in c) / len(c)}
    return out


def boot(vals, n=4000, seed=0):
    rng = random.Random(seed)
    m = sum(vals) / len(vals)
    bs = sorted(sum(vals[rng.randrange(len(vals))] for _ in vals) / len(vals) for _ in range(n))
    return [round(m, 4), round(bs[int(0.025 * n)], 4), round(bs[int(0.975 * n)], 4)]


def tok_class(t):
    if t in ("<|im_end|>", "<|endoftext|>", "<|im_start|>"):
        return "stop/special"
    s = t.replace("Ġ", " ").replace("Ċ", "\n")
    if s.strip() == "":
        return "whitespace"
    if re.fullmatch(r"\s*[\d.,]+\s*", s):
        return "digit"
    if re.fullmatch(r"\s*[\\$^_{}()\[\]=+\-*/<>|!,.:;'\"`~#&%]+\s*", s):
        return "symbol/punct"
    return "word"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--sets", default="math500,math_l5,olymp")
    args = ap.parse_args()
    p0, p1, _ = models.PAIRS[args.pair]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(p1))
    res = {"pair": args.pair, "sets": {}}
    for s in args.sets.split(","):
        G = {c: load_grid(f"t_{c}_{s}") for c in CONDS}
        A = {"base": load_anchor(f"a_{p0}_{s}"), "post": load_anchor(f"a_{p1}_{s}")}
        R = {"conditions": {}, "paired": {}, "anchors": {}, "by_base_solve_rate": {}}
        have = [c for c in CONDS if G[c]]
        common = sorted(set.intersection(*[set(G[c]) for c in have])) if have else []
        for c in have:
            rows = [G[c][k] for k in common]
            R["conditions"][c] = {"n": len(rows), "acc": boot([r["reward"] for r in rows]),
                                  "parse_fail": round(sum(r["pred"] is None for r in rows) / len(rows), 4),
                                  "truncated": round(sum(r["truncated"] for r in rows) / len(rows), 4),
                                  "mean_len": round(sum(r["n_tokens"] for r in rows) / len(rows), 1),
                                  "mean_dis_hi": round(sum(r.get("n_dis_hi", 0) for r in rows) / len(rows), 2),
                                  "mean_dis_lo": round(sum(r.get("n_dis_lo", 0) for r in rows) / len(rows), 2),
                                  "mean_swaps": round(sum(len(r.get("swaps", [])) for r in rows) / len(rows), 2),
                                  "looped": round(sum(r.get("looped", False) for r in rows) / len(rows), 4)}
        for a, b in [("t_base_postmode", "t_base_basemode"), ("t_base_basemode_postlow", "t_base_basemode")]:
            if G[a] and G[b]:
                R["paired"][f"{a} - {b}"] = boot([G[a][k]["reward"] - G[b][k]["reward"] for k in common])
        for name, an in A.items():
            if an:
                ks = sorted(an)
                R["anchors"][name] = {"n": len(ks), "acc": boot([an[k]["p"] for k in ks]),
                                      "truncated": round(sum(an[k]["trunc"] for k in ks) / len(ks), 4),
                                      "parse_fail": round(sum(an[k]["parse_fail"] for k in ks) / len(ks), 4),
                                      "mean_len": round(sum(an[k]["len"] for k in ks) / len(ks), 1)}
        if A["base"] and A["post"]:
            kc = [k for k in common if k in A["base"] and k in A["post"]]
            R["paired"]["P0 - B0 (anchors, same problems)"] = boot([A["post"][k]["p"] - A["base"][k]["p"] for k in kc])
            for c in ("t_base_basemode", "t_base_postlow"):
                if G[c]:
                    R["paired"][f"{c} - B0"] = boot([G[c][k]["reward"] - A["base"][k]["p"] for k in kc])
            bins = {"p_base=0": lambda p: p == 0, "0<p_base<=3/8": lambda p: 0 < p <= 0.375,
                    "3/8<p_base<1": lambda p: 0.375 < p < 1, "p_base=1": lambda p: p == 1}
            for bn, f in bins.items():
                kk = [k for k in kc if f(A["base"][k]["p"])]
                if len(kk) < 15:
                    continue
                d = {"n": len(kk), "gap_P0_B0": boot([A["post"][k]["p"] - A["base"][k]["p"] for k in kk])}
                if G["t_base_basemode"]:
                    d["derand_B1_B0"] = boot([G["t_base_basemode"][k]["reward"] - A["base"][k]["p"] for k in kk])
                if G["t_base_postmode"] and G["t_base_basemode"]:
                    d["C_hi_B2_B1"] = boot([G["t_base_postmode"][k]["reward"] - G["t_base_basemode"][k]["reward"] for k in kk])
                if G["t_base_postlow"]:
                    d["C_lo_B3_B0"] = boot([G["t_base_postlow"][k]["reward"] - A["base"][k]["p"] for k in kk])
                if G["t_base_basemode_postlow"] and G["t_base_basemode"]:
                    d["C_lo_after_derand_B4_B1"] = boot([G["t_base_basemode_postlow"][k]["reward"] - G["t_base_basemode"][k]["reward"] for k in kk])
                R["by_base_solve_rate"][bn] = d
        # swap-content audit
        for c in ("t_base_postmode", "t_base_postlow", "t_base_basemode_postlow"):
            if not G[c]:
                continue
            cnt, ex = {}, {}
            for k in common:
                for t, b, q, h in G[c][k].get("swaps", []):
                    key = (tok_class(tok.convert_ids_to_tokens(b)), tok_class(tok.convert_ids_to_tokens(q)))
                    cnt[key] = cnt.get(key, 0) + 1
                    pair = (tok.convert_ids_to_tokens(b), tok.convert_ids_to_tokens(q))
                    ex[pair] = ex.get(pair, 0) + 1
            tot = sum(cnt.values()) or 1
            R[f"swap_classes_{c}"] = {f"{a}->{b}": round(v / tot, 4) for (a, b), v in sorted(cnt.items(), key=lambda x: -x[1])[:12]}
            R[f"swap_top_pairs_{c}"] = [[a, b, v] for (a, b), v in sorted(ex.items(), key=lambda x: -x[1])[:30]]
        res["sets"][s] = R
        print("==", s, json.dumps({k: v for k, v in R.items() if not k.startswith("swap_top")}, indent=1))
    out = ROOT / "results" / "e07"; out.mkdir(parents=True, exist_ok=True)
    (out / f"summary_{args.pair}.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
