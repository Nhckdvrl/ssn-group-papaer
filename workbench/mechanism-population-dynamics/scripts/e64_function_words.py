"""E64 (ACL angle): which word statistics carry the corpus-distance law — function words or content words?
Recipe unigram distributions (E60 samples) restricted to function-word tokens vs content-word tokens (renormalized),
pairwise JS, then Mantel Spearman with same-seed within-layer inheritance on source-disjoint recipe pairs."""
import json
import sys

import numpy as np

import mp_common as mc
from e60_corpus_distance import dir_dists, inheritance, js, mantel
from e60_disjoint import partial_spearman

FW = set("""a an the this that these those my your his her its our their some any no every each either neither all both
half several many much more most few fewer less least other another such what which whose whatever whichever
i me you he him she it we us they them myself yourself himself herself itself ourselves themselves one ones
who whom whoever someone anyone everyone nobody somebody anybody everybody something anything everything nothing
in on at by for with about against between into through during before after above below to from up down out off
over under again further of upon within without among across along around behind beyond near since until toward
towards via per than as like unlike despite except onto
and or but nor so yet if because although though while whereas unless whether since once when where whenever wherever
be am is are was were been being have has had having do does did doing will would shall should can could may might must
not n't no yes there here then now very too also just only even still already ever never always often
how why whether just quite rather almost""".split())


def main():
    from transformers import PreTrainedTokenizerFast
    import glob
    tok = PreTrainedTokenizerFast(tokenizer_file=glob.glob(str(mc.HF_CACHE / "models--allenai--DataDecide-dolma1_7-1B/snapshots/*/tokenizer.json"))[0])
    V = 50304
    words = [tok.decode([i]) if i < len(tok) else "" for i in range(V)]
    is_fw = np.array([w.strip().lower() in FW and w.strip().isalpha() for w in words])
    is_alpha = np.array([w.strip().isalpha() for w in words])
    is_cw = is_alpha & ~is_fw
    print("function-word tokens", int(is_fw.sum()), "content-word tokens", int(is_cw.sum()), flush=True)
    rec = dir_dists()
    names = sorted(rec)
    D = {"fw": {}, "cw": {}, "fw_mass": {}}
    for a in names:
        D["fw_mass"][a] = float(rec[a]["uni"][is_fw].sum())
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            p, q = rec[a]["uni"], rec[b]["uni"]
            for key, m in (("fw", is_fw), ("cw", is_cw)):
                pp, qq = p[m] / p[m].sum(), q[m] / q[m].sum()
                D[key][(a, b)] = js(pp, qq)
    print("mean JS fw %.4f cw %.4f; FW mass range %.3f-%.3f" % (np.mean(list(D["fw"].values())), np.mean(list(D["cw"].values())),
          min(D["fw_mass"].values()), max(D["fw_mass"].values())), flush=True)
    import collections, sys as _s
    _s.path.insert(0, "/home/xiang/mechpop_cache/datadecide")
    import named_data_mixes as ndm
    from e23_corpus_stats import RECIPES, sizes
    sz = sizes()
    W = {}
    for name, key in RECIPES.items():
        g = collections.defaultdict(float)
        for pth in ndm.DATA_PATHS[key]:
            g[pth.rsplit("/", 1)[0]] += sz.get(pth, 0) or 0
        t = sum(g.values())
        W[name] = {k: v / t for k, v in g.items()}
    ov = lambda a, b: sum(min(W[a].get(k, 0), W[b].get(k, 0)) for k in set(W[a]) | set(W[b]))
    rng = np.random.default_rng(0)
    e35 = sorted((mc.RESULTS / "e35").glob("*-1B__*.json"))
    sets = {"1B": inheritance([f for f in e35 if "step" not in f.name and tuple(f.stem.split("-1B__")) not in mc.UNVERIFIED_1B], lambda f: (f.stem.split("-1B__")[0], f.stem.split("-1B__")[1]))}
    for size in ("90M", "150M", "300M", "530M", "750M", "1B@7500"):
        sets[size] = inheritance(sorted((mc.RESULTS / "e45").glob(f"{size}__*.json")), lambda f: tuple(f.stem.split("__")[1:3]))
    out = {"n_fw_tokens": int(is_fw.sum()), "n_cw_tokens": int(is_cw.sum()), "by_size": {}}
    for size, inh in sets.items():
        out["by_size"][size] = {}
        for m, sim in inh.items():
            pairs = [p for p in sim if p in D["fw"] and ov(*p) < 1e-9]
            if len(pairs) < 10:
                continue
            r = {k: mantel(pairs, {p: D[k][p] for p in pairs}, sim, rng, n=2000) for k in ("fw", "cw")}
            r["partial_fw_given_cw"] = partial_spearman([D["fw"][p] for p in pairs], [sim[p] for p in pairs], [D["cw"][p] for p in pairs])
            r["partial_cw_given_fw"] = partial_spearman([D["cw"][p] for p in pairs], [sim[p] for p in pairs], [D["fw"][p] for p in pairs])
            out["by_size"][size][m] = r
            print(f"{size:8s} {m} n {len(pairs):3d} | rho fw {r['fw'][0]:+.3f} (p {r['fw'][1]:.3f}) cw {r['cw'][0]:+.3f} (p {r['cw'][1]:.3f}) | "
                  f"partial fw|cw {r['partial_fw_given_cw']:+.3f} cw|fw {r['partial_cw_given_fw']:+.3f}", flush=True)
    (mc.RESULTS / "e60" / "function_words.json").write_text(json.dumps(out, indent=1))
    # per-pair values for the paper figure (source-disjoint 1B pairs): JS of each word class and same-seed inheritance
    pairs = {"|".join(p): {"fw": D["fw"][p], "cw": D["cw"][p], "disjoint": ov(*p) < 1e-9,
                           "inherit": {m: float(sets["1B"][m][p]) for m in sets["1B"] if p in sets["1B"][m]}}
             for p in D["fw"]}
    (mc.RESULTS / "e60" / "function_words_pairs.json").write_text(json.dumps(pairs, indent=1))


if __name__ == "__main__":
    main()
