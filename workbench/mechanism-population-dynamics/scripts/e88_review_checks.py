"""E88: analyses requested by the 2026-10-11 review, computed from stored maps (no new model runs).

Usage: e88_review_checks.py -> results/e88/analysis.json + printed summary
  A  carriers ranked by single-head ablation: top-k overlap and additive transfer for k = 1, 3, 5, 10, by relation (E81 maps)
  B  midtraining -> SFT step of the OLMo-2-1B lineage (E81 maps)
  C  inheritance of individual role heads between DataDecide-1B models (E35 maps): is the source's top-k head of a role
     (whole model) the same head index among the target's top-k?  siblings vs unrelated
  D  uncertainty: corpus-cluster bootstrap CIs for sibling vs unrelated correspondences; permutation test for the
     corpus-distance correlation (Mantel-type, permuting corpus labels)
"""
import glob
import itertools
import json

import numpy as np
from scipy.stats import spearmanr

import mp_common as mc
from e81_analyze import SB, load, within

OUT = mc.RESULTS / "e88"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(0)


def topk(m, k):
    H = m.shape[1]
    return [(int(t // H), int(t % H)) for t in np.argsort(m.ravel())[::-1][:k]]


def carrier_stats(dx, dy, k):
    ax, ay = dx["abl"].mean(0), dy["abl"].mean(0)
    tx, ty = topk(ax, k), topk(ay, k)
    own = sum(ay[h] for h in ty)
    return {"overlap": len(set(tx) & set(ty)) / k, "transfer": float(sum(ay[h] for h in tx) / own) if own > 0 else np.nan}


def corrected_abl(dx, dy):
    r = within(dx["abl"].mean(0), dy["abl"].mean(0))
    return r / np.sqrt(max(SB(within(*dx["abl"])), 1e-3) * max(SB(within(*dy["abl"])), 1e-3))


def part_a(D):
    dd = {k: v for k, v in D.items() if k.startswith("dd__")}
    rel = {"lineage": [], "closely related": [], "siblings": [], "unrelated": []}
    for a, b in itertools.combinations(sorted(dd), 2):
        ca, sa = a.split("__")[1], a.split("seed-")[1]
        cb, sb = b.split("__")[1], b.split("seed-")[1]
        if sa != sb:
            rel["unrelated"].append((a, b))
        elif {ca, cb} == {"DataDecide-dolma1_7-1B", "DataDecide-dolma1_7-no-flan-1B"}:
            rel["closely related"].append((a, b))
        else:
            rel["siblings"].append((a, b))
    rel["closely related"].append(("pythia__pythia-410m__143000", "pythia__pythia-410m-deduped__143000"))
    O = "hf__OLMo-2-0425-1B__"
    rel["lineage"] = [("pythia__pythia-410m__66000", "pythia__pythia-410m__143000")]
    rel["lineage"] += [(O + "stage1-step1907359-tokens4001B", O + f"stage2-ingredient{i}-step23852-tokens51B") for i in (1, 2, 3)]
    rel["lineage"] += [(O + f"stage2-ingredient{i}-step23852-tokens51B", "hf__OLMo-2-0425-1B-SFT__main") for i in (1, 2, 3)]
    rel["lineage"] += [("hf__OLMo-2-0425-1B-SFT__main", "hf__OLMo-2-0425-1B-DPO__main"),
                       ("hf__OLMo-2-0425-1B-DPO__main", "hf__OLMo-2-0425-1B-Instruct__main")]
    out = {}
    for name, pairs in rel.items():
        pairs = [p for p in pairs if p[0] in D and p[1] in D]
        out[name] = {"n_pairs": len(pairs)}
        for k in (1, 3, 5, 10):
            s = [carrier_stats(D[a], D[b], k) for a, b in pairs]
            out[name][f"k{k}"] = {m: float(np.nanmean([x[m] for x in s])) for m in ("overlap", "transfer")}
    return out


def part_b(D):
    O = "hf__OLMo-2-0425-1B__"
    sft = D["hf__OLMo-2-0425-1B-SFT__main"]
    rows = {}
    for i in (1, 2, 3):
        s = D[O + f"stage2-ingredient{i}-step23852-tokens51B"]
        rows[f"ingredient{i}"] = {"abl_corrected": float(corrected_abl(s, sft)),
                                  "att_io": within(s["att_io"].mean(0), sft["att_io"].mean(0)),
                                  "top3_dla_overlap": len(set(topk(s["dla"].mean(0), 3)) & set(topk(sft["dla"].mean(0), 3))),
                                  "main_same": topk(s["dla"].mean(0), 1) == topk(sft["dla"].mean(0), 1),
                                  "transfer3": carrier_stats(s, sft, 3)["transfer"],
                                  "main_src": "%d.%d" % topk(s["dla"].mean(0), 1)[0], "main_sft": "%d.%d" % topk(sft["dla"].mean(0), 1)[0]}
    return rows


def dd_maps():
    bad = set(json.loads((mc.RESULTS / "e35_verified.json").read_text())["excluded"])
    seeds = ("default", "large-aux-2", "large-aux-3")
    recs = sorted({f.split("/")[-1].split("-1B__")[0] for f in glob.glob(str(mc.RESULTS / "e35" / "*-1B__*.json")) if "step" not in f})
    keys = [(r, sd) for sd in seeds for r in recs if f"{r}|{sd}" not in bad and (mc.RESULTS / "e35" / f"{r}-1B__{sd}.json").exists()]
    return {k: {m: np.array(v) for m, v in json.loads((mc.RESULTS / "e35" / f"{k[0]}-1B__{k[1]}.json").read_text())["maps"].items()}
            for k in keys}


def part_c(maps):
    keys = list(maps)
    out = {}
    for role in ("M1", "M2", "M3", "M4"):
        for k in (1, 5):
            hits = {"siblings": [], "unrelated": []}
            for a, b in itertools.permutations(keys, 2):
                rel = "siblings" if a[1] == b[1] else "unrelated"
                ta, tb = set(topk(maps[a][role], k)), set(topk(maps[b][role], k))
                hits[rel].append(len(ta & tb) / k)
            out[f"{role}_top{k}"] = {r: float(np.mean(v)) for r, v in hits.items()}
            L, H = maps[keys[0]][role].shape
            out[f"{role}_top{k}"]["chance_any_head"] = k / (L * H)
    return out


def part_d(maps):
    keys = list(maps)
    corp = sorted({k[0] for k in keys})
    roles = ("M1", "M2", "M3", "M4")
    C = {}
    for a, b in itertools.combinations(keys, 2):
        C[(a, b)] = C[(b, a)] = np.mean([within(maps[a][m], maps[b][m]) for m in roles])

    def stat(cs):
        sib, unr = [], []
        idx = [k for c in cs for k in keys if k[0] == c]
        for i, a in enumerate(idx):
            for b in idx[i + 1:]:
                if a == b or a[0] == b[0] and a[1] == b[1]:
                    continue
                (sib if a[1] == b[1] else unr).append(C[(a, b)])
        return np.mean(sib), np.mean(unr)
    point = stat(corp)
    boots = np.array([stat(list(rng.choice(corp, len(corp), replace=True))) for _ in range(1000)])
    res = {"role_sib": point[0], "role_unr": point[1],
           "role_sib_ci": np.percentile(boots[:, 0], [2.5, 97.5]).tolist(),
           "role_unr_ci": np.percentile(boots[:, 1], [2.5, 97.5]).tolist(),
           "role_diff_ci": np.percentile(boots[:, 0] - boots[:, 1], [2.5, 97.5]).tolist()}
    return res


def part_d_carriers(D):
    dd = {k: v for k, v in D.items() if k.startswith("dd__")}
    corp = sorted({k.split("__")[1] for k in dd})
    P = {}
    for a, b in itertools.combinations(sorted(dd), 2):
        P[(a, b)] = (within(dd[a]["att_io"].mean(0), dd[b]["att_io"].mean(0)), corrected_abl(dd[a], dd[b]))

    def stat(cs):
        sib, unr = [], []
        for (a, b), v in P.items():
            ca, cb = a.split("__")[1], b.split("__")[1]
            na, nb = cs.count(ca), cs.count(cb)
            if na == 0 or nb == 0:
                continue
            w = na * nb
            (sib if a.split("seed-")[1] == b.split("seed-")[1] else unr).extend([v] * w)
        sib, unr = np.array(sib), np.array(unr)
        return sib[:, 0].mean(), sib[:, 1].mean(), unr[:, 0].mean(), unr[:, 1].mean()
    point = stat(corp)
    boots = np.array([stat(list(rng.choice(corp, len(corp), replace=True))) for _ in range(2000)])
    names = ("sib_att", "sib_abl", "unr_att", "unr_abl")
    out = {n: float(p) for n, p in zip(names, point)}
    out.update({n + "_ci": np.nanpercentile(boots[:, i], [2.5, 97.5]).tolist() for i, n in enumerate(names)})
    out["sib_att_minus_abl_ci"] = np.nanpercentile(boots[:, 0] - boots[:, 1], [2.5, 97.5]).tolist()
    return out


def main():
    D = load()
    maps = dd_maps()
    res = {"A_ablation_ranked_carriers": part_a(D), "B_midtrain_to_sft": part_b(D), "C_role_head_inheritance": part_c(maps),
           "D_role_bootstrap": part_d(maps), "D_carrier_bootstrap": part_d_carriers(D)}
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=lambda x: round(float(x), 3)))


if __name__ == "__main__":
    main()
