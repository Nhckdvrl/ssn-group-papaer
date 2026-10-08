"""audit_all_sizes: training-start audit of every DataDecide run used in the paper, at every size . For each (size, recipe, seed): a fixed set of weight tensors (att_proj of up to four blocks and
ff_proj of block 0) is read by HTTP range request from the earliest training checkpoint (smallest step > 0) and from
the checkpoint the paper uses, and correlated with the step-0 tensors of every seed (reference recipe = the one whose
step-0 hash is the most common for that seed at that size).

  audit_all_sizes.py            # all sizes -> results/audit_all_sizes/<size>.json
  audit_all_sizes.py 4M 6M      # some sizes
"""
import collections
import concurrent.futures as cf
import json
import struct
import sys

import requests
import torch
from huggingface_hub import hf_hub_url
from huggingface_hub.utils import build_hf_headers

import common as mc
DD = mc.CACHE / "datadecide"
SURVEY = json.loads((DD / "survey_all_sizes.json").read_text())
PLAN = json.loads((DD / "datadecide_plan.json").read_text())
OUT = mc.RESULTS / "audit_all_sizes"
DT = {"F32": torch.float32, "BF16": torch.bfloat16, "F16": torch.float16}
HDR = build_hf_headers()


def get(url, a=None, b=None):
    h = dict(HDR)
    if a is not None:
        h["Range"] = f"bytes={a}-{b}"
    for _ in range(5):
        try:
            r = requests.get(url, headers=h, timeout=300, allow_redirects=True)
            r.raise_for_status()
            return r
        except requests.RequestException:
            continue
    r.raise_for_status()


_HEAD = {}


def header(repo, rev):
    """{tensor name: (file url, absolute byte range, dtype)} for one checkpoint (single file or sharded)."""
    if (repo, rev) in _HEAD:
        return _HEAD[(repo, rev)]
    try:
        idx = get(hf_hub_url(repo, "model.safetensors.index.json", revision=rev)).json()["weight_map"]
        files = sorted(set(idx.values()))
    except requests.HTTPError:
        files = ["model.safetensors"]
    out = {}
    for fn in files:
        url = hf_hub_url(repo, fn, revision=rev)
        n = struct.unpack("<Q", get(url, 0, 7).content)[0]
        meta = json.loads(get(url, 8, 8 + n - 1).content)
        for k, v in meta.items():
            if k != "__metadata__":
                out[k] = (url, 8 + n + v["data_offsets"][0], 8 + n + v["data_offsets"][1], v["dtype"])
    _HEAD[(repo, rev)] = out
    return out


def keys(h):
    blocks = sorted({int(k.split(".blocks.")[1].split(".")[0]) for k in h if ".blocks." in k})
    return [f"model.transformer.blocks.{b}.att_proj.weight" for b in blocks[:4]] + ["model.transformer.blocks.0.ff_proj.weight"]


def vec(repo, rev):
    h = header(repo, rev)
    parts = []
    for k in keys(h):
        url, a, b, dt = h[k]
        raw = get(url, a, b - 1).content
        parts.append(torch.frombuffer(bytearray(raw), dtype=DT[dt]).float())
    return torch.cat(parts)


def corr(a, b):
    return round(float(torch.corrcoef(torch.stack([a, b]))[0, 1]), 4)


def repo_of(size, recipe):
    return f"allenai/DataDecide-{recipe}-{'1B' if size.startswith('1B') else size}"


def used_runs(size):
    if size == "1B":
        return sorted({tuple(f.stem.split("-1B__")) for f in (mc.RESULTS / "crossing_1b").glob("*-1B__*.json") if "step" not in f.stem})
    return sorted({tuple(f.stem.split("__")[1:]) for f in (mc.RESULTS / "crossing_sizes").glob(f"{size}__*.json")})


def audit(size):
    runs = used_runs(size)
    seeds = sorted({s for _, s in runs})
    step_used = {"1B": 69369, "1B@7500": 7500}.get(size) or PLAN[size]["step"]
    # reference step 0 per seed: the recipe with the most common step-0 hash among the used runs (1B: c4)
    ref = {}
    for s in seeds:
        if size.startswith("1B"):
            ref[s] = "c4"
            continue
        sha = collections.Counter(SURVEY[repo_of(size, r)][s]["sha0"] for r, ss in runs if ss == s)
        top = sha.most_common(1)[0][0]
        ref[s] = next(r for r, ss in runs if ss == s and SURVEY[repo_of(size, r)][s]["sha0"] == top)
    S0 = {s: vec(repo_of(size, ref[s]), f"step0-seed-{s}") for s in seeds}

    def one(run):
        r, s = run
        steps = SURVEY.get(repo_of(size, r), {}).get(s, {}).get("steps") or []
        early = min(x for x in steps if x > 0) if steps else None
        rec = {"recipe": r, "seed": s, "earliest_step": early, "used_step": step_used,
               "n_steps_listed": len(steps), "final_listed": max(steps) if steps else None,
               "sha0": SURVEY.get(repo_of(size, r), {}).get(s, {}).get("sha0")}
        try:
            if early is not None:
                e = vec(repo_of(size, r), f"step{early}-seed-{s}")
                rec["earliest_vs_step0"] = {s0: corr(e, S0[s0]) for s0 in seeds}
            u = vec(repo_of(size, r), f"step{step_used}-seed-{s}")
            rec["used_vs_step0"] = {s0: corr(u, S0[s0]) for s0 in seeds}
        except Exception as ex:  # report, do not stop the audit
            rec["error"] = repr(ex)[:200]
        return rec

    with cf.ThreadPoolExecutor(8) as ex:
        recs = list(ex.map(one, runs))
    for rec in recs:
        e = rec.get("earliest_vs_step0") or rec.get("used_vs_step0") or {}
        if e:
            own, other = e[rec["seed"]], max(v for k, v in e.items() if k != rec["seed"])
            rec["starts_from_label"] = bool(own > 0.02 and own > 5 * max(other, 0.004))
    res = {"size": size, "seeds": seeds, "reference_recipe": ref, "used_step": step_used,
           "step0_cross_seed": {f"{a}|{b}": corr(S0[a], S0[b]) for a in seeds for b in seeds if a < b},
           "runs": recs}
    OUT.mkdir(exist_ok=True)
    (OUT / f"{size}.json").write_text(json.dumps(res, indent=1))
    bad = [(x["recipe"], x["seed"]) for x in recs if not x.get("starts_from_label")]
    print(size, "runs", len(recs), "not from label:", bad, flush=True)


def main():
    sizes = sys.argv[1:] or [s for s in PLAN if s != "1B"] + ["1B@7500", "1B"]
    for s in sizes:
        audit(s)


if __name__ == "__main__":
    main()
