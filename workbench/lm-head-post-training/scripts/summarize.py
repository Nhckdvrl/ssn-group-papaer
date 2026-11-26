"""Print compact markdown tables from results/e01/*.json and results/e02/*.json (for cards / logs)."""
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def f(x, n=3):
    return "—" if x is None else (f"{x:.{n}g}" if isinstance(x, float) else str(x))


def e01():
    rows = []
    for p in sorted(glob.glob(str(ROOT / "results/e01/weights_*.json"))):
        r = json.load(open(p))
        if r.get("same_control"):
            continue
        g, h, e = r["groups"], r["lm_head"], r["embed_tokens"]
        body = [k for k in g if k not in ("lm_head", "embed_tokens", "final_norm") and "norm" not in k]
        body_sq_d = sum(g[k]["norm_d"] ** 2 for k in body)
        body_rel = (body_sq_d / sum((g[k]["norm_d"] / max(g[k]["rel_change"], 1e-30)) ** 2 for k in body if g[k]["rel_change"] > 0)) ** 0.5
        fn = ROOT / f"results/e01/function_{r['pair']}.json"
        fs = json.load(open(fn))["summary_all"] if fn.exists() else {}
        get = lambda k: fs.get(k, {}).get("mean")
        rows.append([r["pair"], r["stage"], f(h["rel_change"]), f(e["rel_change"]), f(body_rel),
                     f(g["lm_head"]["frac_bitwise_equal"]), f(h["rounding_null"]["frac_sv_above"]),
                     f(h["common_shift_energy_frac"]), f(h["w0_proportional_alpha"]), f(h["energy_top_rows"]["top1%"]),
                     f(h["colspace"]["min_cos"]), f(get("kl_total")), f(get("kl_head_h0")), f(get("kl_bb_W0")),
                     f(get("flip_head_h0")), f(get("flip_bb_W0"))])
    hdr = ["pair", "stage", "head Δrel", "emb Δrel", "body Δrel", "head bit-eq", "head sv>floor", "common-shift E",
           "α(W0)", "top1% rows E", "min cos col", "KL tot", "KL head|h0", "KL bb|W0", "flip head", "flip bb"]
    print("| " + " | ".join(hdr) + " |\n|" + "---|" * len(hdr))
    for r_ in rows:
        print("| " + " | ".join(r_) + " |")


if __name__ == "__main__":
    e01()
