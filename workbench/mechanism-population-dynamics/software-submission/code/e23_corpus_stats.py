"""E23: corpus repetition statistics per DataDecide recipe (CPU + network).

Recipe -> list of tokenized shards (OLMo DataDecide branch, olmo/data/named_data_mixes.py, cached in
$MECHPOP_CACHE/datadecide). Shards are grouped by directory; each directory is sampled once
(HTTP Range 20 MB prefix of its first shard, first ~3M tokens of whole documents, raw uint16 memmap, documents separated by EOS=50279); a recipe's statistic is
the size-weighted mean over its directories.
Usage: e23_corpus_stats.py stats   -> results/e23/dir_stats.json, recipe_stats.json ;  e23_corpus_stats.py analyze
"""
import os
_CACHE = os.environ.get("MECHPOP_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache"))  # see README
import collections
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import mp_common as mc

sys.path.insert(0, _CACHE + "/datadecide")
import named_data_mixes as ndm  # noqa: E402

OUT = mc.RESULTS / "e23"
SAMPLES = Path(_CACHE + "/datadecide/samples")
URL = "https://huggingface.co/datasets/allenai/DataDecide-data-recipes/resolve/main/"
EOS, PREFIX_BYTES, TOKEN_CAP = 50279, 20_000_000, 3_000_000
RECIPES = {  # HF model name (DataDecide-<x>-1B) -> named_data_mixes key
    "dolma1_7": "dolma17", "dolma1_7-no-code": "no_code", "dolma1_7-no-math-code": "no_math_no_code",
    "dolma1_7-no-reddit": "no_reddit", "dolma1_7-no-flan": "no_flan", "dolma1_6plus": "dolma-v1-6-and-sources-baseline",
    "c4": "c4", "falcon": "falcon", "falcon-and-cc": "falcon_and_cc",
    "falcon-and-cc-qc-10p": "falcon_and_cc_eli5_oh_top10p", "falcon-and-cc-qc-20p": "falcon_and_cc_eli5_oh_top20p",
    "falcon-and-cc-qc-orig-10p": "falcon_and_cc_og_eli5_oh_top10p", "falcon-and-cc-qc-tulu-10p": "falcon_and_cc_tulu_qc_top10",
    "fineweb-edu": "fineweb_edu_dedup", "fineweb-pro": "prox_fineweb_pro", "dclm-baseline": "DCLM-baseline",
    "dclm-baseline-25p-dolma1.7-75p": "dolma17-75p-DCLM-baseline-25p",
    "dclm-baseline-50p-dolma1.7-50p": "dolma17-50p-DCLM-baseline-50p",
    "dclm-baseline-75p-dolma1.7-25p": "dolma17-25p-DCLM-baseline-75p",
    "dclm-baseline-qc-7p-fw2": "dclm_ft7percentile_fw2", "dclm-baseline-qc-7p-fw3": "dclm_ft7percentile_fw3",
    "dclm-baseline-qc-fw-10p": "dclm_fw_top10", "dclm-baseline-qc-fw-3p": "dclm_fw_top3",
    "dclm-baseline-qc-10p": "pos_eli5_oh_neg_dclm_refinedweb_steps_2000_lr3e4_top10p",
    "dclm-baseline-qc-20p": "pos_eli5_oh_neg_dclm_refinedweb_steps_2000_lr3e4_top20p",
}


def sizes():
    from huggingface_hub import HfApi
    f = OUT / "hf_file_sizes.json"
    if not f.exists():
        info = HfApi().dataset_info("allenai/DataDecide-data-recipes", files_metadata=True)
        f.write_text(json.dumps({s.rfilename: s.size for s in info.siblings}))
    return json.loads(f.read_text())


def fetch_prefix(path):
    dst = SAMPLES / (path.replace("/", "__") + ".prefix")
    if not dst.exists() or dst.stat().st_size < PREFIX_BYTES * 0.9:
        tok = (Path.home() / ".cache/huggingface/token").read_text().strip()
        req = urllib.request.Request(URL + path, headers={"Authorization": f"Bearer {tok}",
                                                          "Range": f"bytes=0-{PREFIX_BYTES - 1}"})
        dst.write_bytes(urllib.request.urlopen(req, timeout=600).read())
    return np.fromfile(dst, dtype=np.uint16)


def doc_stats(a, max_docs=20000):
    cut = np.where(a == EOS)[0]
    docs = np.split(a, cut + 1)[1:-1][:max_docs]  # drop partial first/last
    s1n = s1d = s2n = s3 = ntok = 0
    per_doc = []
    for d in docs:
        d = d[d != EOS]
        n = len(d)
        if n < 16:
            continue
        seen, hit = {}, 0
        for j in range(2, n):
            k = (int(d[j - 2]), int(d[j - 1]))
            if k in seen and seen[k] == d[j]:
                hit += 1
            seen[k] = d[j]
        rep8 = np.zeros(n, bool)
        s8 = {}
        for j in range(n - 7):
            k = d[j:j + 8].tobytes()
            if k in s8:
                rep8[j:j + 8] = True
            else:
                s8[k] = j
        per_doc.append((hit / (n - 2), rep8.mean(), n))
        s1n += hit; s1d += n - 2; s2n += rep8.sum(); ntok += n
        if ntok >= TOKEN_CAP:
            break
    return {"n_docs": len(per_doc), "n_tokens": int(ntok), "S1": s1n / s1d, "S2": float(s2n / ntok),
            "S1_doc_mean": float(np.mean([p[0] for p in per_doc])), "S2_doc_mean": float(np.mean([p[1] for p in per_doc]))}


def qa_density(a, tok):
    text = tok.decode(a[:2_000_000].tolist())
    lines = text.split("\n")
    n = sum(l.lstrip().startswith(("Question:", "Answer:", "Q:", "A:")) for l in lines)
    return 1000 * n / 2_000_000


def stats():
    OUT.mkdir(exist_ok=True)
    SAMPLES.mkdir(exist_ok=True)
    sz = sizes()
    from transformers import PreTrainedTokenizerFast
    import glob
    tok = PreTrainedTokenizerFast(tokenizer_file=glob.glob(
        _CACHE + "/hf/models--allenai--DataDecide-dolma1_7-1B/snapshots/*/tokenizer.json")[0])
    groups = {}
    for name, key in RECIPES.items():
        g = collections.defaultdict(int)
        for p in ndm.DATA_PATHS[key]:
            g[p.rsplit("/", 1)[0]] += sz.get(p, 0) or 0
        groups[name] = dict(g)
    dirs = sorted({d for g in groups.values() for d in g})
    f = OUT / "dir_stats.json"
    ds = json.loads(f.read_text()) if f.exists() else {}
    for d in dirs:
        if d in ds:
            continue
        first = sorted(p for p in sz if p.startswith(d + "/") and p.endswith(".npy"))
        if not first:
            ds[d] = None
            print("missing on HF:", d, flush=True)
            continue
        a = fetch_prefix(first[0])
        ds[d] = {**doc_stats(a), "QA_per_1k": qa_density(a, tok), "sample": first[0]}
        f.write_text(json.dumps(ds, indent=1))
        print(d, {k: round(v, 4) if isinstance(v, float) else v for k, v in ds[d].items() if k != "sample"}, flush=True)
    rs = {}
    for name, g in groups.items():
        w = {d: s for d, s in g.items() if ds.get(d)}
        tot = sum(w.values())
        rs[name] = {"coverage": tot / max(1, sum(g.values())),
                    **{k: sum(ds[d][k] * s for d, s in w.items()) / tot for k in ("S1", "S2", "QA_per_1k")}}
    (OUT / "recipe_stats.json").write_text(json.dumps(rs, indent=1))
    for k, v in sorted(rs.items(), key=lambda x: x[1]["S1"]):
        print(f"{k:35s} S1 {v['S1']:.4f} S2 {v['S2']:.4f} QA {v['QA_per_1k']:.3f} cov {v['coverage']:.2f}")


def analyze():
    import dd_common as dd
    rs = json.loads((OUT / "recipe_stats.json").read_text())
    E = {}
    for name in rs:
        vals = [json.loads((mc.RESULTS / "e20" / f"{name}-1B__{s}.json").read_text())["conditions"] for s in dd.SEEDS
                if (mc.RESULTS / "e20" / f"{name}-1B__{s}.json").exists()]
        if len(vals) < 3:
            continue
        sub = np.mean([np.mean([c[k]["margin"] for k in c if k.endswith("Substitution Conflict")]) for c in vals])
        cohwc = np.mean([np.mean([c[k]["margin"] for k in c if k.endswith("Coherent Conflict")]) for c in vals])  # all 6 (amendment)
        kn = np.mean([np.mean([c[k]["clean_margin"] for k in c]) for c in vals])
        E[name] = (sub, cohwc, kn)
    names = sorted(E)
    x = {k: np.array([rs[n][k] for n in names]) for k in ("S1", "S2", "QA_per_1k")}
    sub, cohwc, kn = (np.array([E[n][i] for n in names]) for i in range(3))
    rng = np.random.default_rng(0)

    def perm_p(a, b):
        r = spearmanr(a, b)[0]
        return float(np.mean([abs(spearmanr(rng.permutation(a), b)[0]) >= abs(r) for _ in range(10000)]))
    from e21_e22_corpus import partial_spearman
    out = {"n_recipes": len(names)}
    for k, v in x.items():
        out[k] = {"rho_sub": float(spearmanr(v, sub)[0]), "p_sub": perm_p(v, sub),
                  "rho_coh_all6": float(spearmanr(v, cohwc)[0]),
                  "partial_rho_sub_given_K": partial_spearman(v, sub, [kn])}
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"stats": stats, "analyze": analyze}[sys.argv[1]]()
