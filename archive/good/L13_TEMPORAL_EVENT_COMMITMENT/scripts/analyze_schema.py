#!/usr/bin/env python
"""L13 E06 analysis.

E06a (free): parse the model's own three-state event table and read off the
status it assigned to the target event.
E06b (forced slot): bootstrap the status distribution from `schema_slot.jsonl`,
side by side with the direct probe P1 from `strict.jsonl`, so that
"asked directly" and "asked inside the structure" are on the same scale.
"""
import argparse
import collections
import json
import os
import re
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

CONDS = ["after", "before_neutral", "before_confirm", "before_cancel", "nontemporal_neutral"]
STATUSES = ["REALIZED", "UNRESOLVED", "NOT_REALIZED"]
STOP = set("the a an of to and or in on at for with his her their its by that this it".split())
N_BOOT = 10000


def content(s):
    return {w for w in re.findall(r"[a-z']+", s.lower()) if w not in STOP}


def norm_status(s):
    s = s.strip().lower()
    if s.startswith("not-real") or s.startswith("not real") or s.startswith("unreal"):
        return "NOT_REALIZED"
    if s.startswith("unres"):
        return "UNRESOLVED"
    if s.startswith("real"):
        return "REALIZED"
    return None


def parse_free(path, stim):
    counts = collections.defaultdict(collections.Counter)
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r["task_order"] != "schema_timeline_first":
            continue
        it = stim[r["item_id"]]
        tgt = content(it["target"])
        found = None
        for ln in r["text"].splitlines():
            if "::" not in ln:
                continue
            left, right = ln.rsplit("::", 1)
            if len(tgt & content(left)) / max(1, len(tgt)) >= 0.7:
                found = norm_status(right)
                break
        counts[it["condition"]][found or "ABSENT_OR_UNPARSED"] += 1
    return {
        cond: {k: round(v / sum(c.values()), 3) for k, v in sorted(c.items())}
        for cond, c in counts.items()
    }


def boot_mean(vals_by_base, bases, rng):
    arr = np.array([vals_by_base[b] for b in bases], dtype=float)
    idx = rng.integers(0, len(bases), size=(N_BOOT, len(bases)))
    s = arr[idx].mean(axis=1)
    return [round(float(arr.mean()), 4)] + [round(float(x), 4) for x in np.percentile(s, [2.5, 97.5])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(PROJ, "configs", "e06_schema.json"))
    args = ap.parse_args()
    cfg = json.load(open(args.config, encoding="utf-8"))
    stim = {
        j["item_id"]: j
        for j in (json.loads(l) for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8"))
    }
    rng = np.random.default_rng(cfg["seed"])
    report = {}

    for spec in cfg["models"]:
        d = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
        entry = {}

        free_path = os.path.join(d, "context_turns_e06.jsonl")
        if os.path.exists(free_path):
            entry["free_table"] = parse_free(free_path, stim)

        slot_path = os.path.join(d, "schema_slot.jsonl")
        if os.path.exists(slot_path):
            rows = [json.loads(l) for l in open(slot_path, encoding="utf-8")]
            per = collections.defaultdict(lambda: collections.defaultdict(list))
            for r in rows:
                per[r["condition"]][r["base_id"]].append(r["probs"])
            bases = sorted({r["base_id"] for r in rows})
            entry["forced_slot"] = {
                cond: {
                    st: boot_mean(
                        {b: statistics.fmean(p[st] for p in ps) for b, ps in bb.items()},
                        bases,
                        rng,
                    )
                    for st in STATUSES
                }
                for cond, bb in per.items()
            }

        direct = os.path.join(d, "strict.jsonl")
        if os.path.exists(direct):
            per = collections.defaultdict(lambda: collections.defaultdict(list))
            for l in open(direct, encoding="utf-8"):
                r = json.loads(l)
                if r["task_order"] != "fact_first":
                    continue
                per[r["condition"]][r["base_id"]].append(r["probs"])
            bases = sorted({b for bb in per.values() for b in bb})
            entry["direct_probe"] = {
                cond: {
                    lab: boot_mean(
                        {b: statistics.fmean(p[lab] for p in ps) for b, ps in bb.items()},
                        bases,
                        rng,
                    )
                    for lab in ["YES", "NO", "NOT_DETERMINED"]
                }
                for cond, bb in per.items()
            }
        # headline paired contrast: the same model, the same sentence, asked
        # directly vs asked inside the structure it is building.
        if "forced_slot" in entry and os.path.exists(direct):
            slot_rows = [json.loads(l) for l in open(slot_path, encoding="utf-8")]
            slot_by = collections.defaultdict(lambda: collections.defaultdict(list))
            for r in slot_rows:
                slot_by[r["condition"]][r["base_id"]].append(r["probs"]["UNRESOLVED"])
            direct_by = collections.defaultdict(lambda: collections.defaultdict(list))
            for l in open(direct, encoding="utf-8"):
                r = json.loads(l)
                if r["task_order"] != "fact_first":
                    continue
                direct_by[r["condition"]][r["base_id"]].append(r["probs"]["NOT_DETERMINED"])
            entry["open_state_loss"] = {}
            for cond in CONDS:
                bs = sorted(set(slot_by[cond]) & set(direct_by[cond]))
                if not bs:
                    continue
                entry["open_state_loss"][cond] = boot_mean(
                    {
                        b: statistics.fmean(direct_by[cond][b])
                        - statistics.fmean(slot_by[cond][b])
                        for b in bs
                    },
                    bs,
                    rng,
                )
        if entry:
            report[spec["slug"]] = entry

    out = os.path.join(PROJ, "results", cfg["tag"], "schema_analysis.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("condition: before_neutral — is `unresolved` used when a slot exists?\n")
    print(f"{'model':24s} {'direct P(ND)':>16s} {'slot P(UNRESOLVED)':>20s} {'slot P(REALIZED)':>18s} {'free-table unresolved':>22s}")
    for slug, e in report.items():
        d = e.get("direct_probe", {}).get("before_neutral", {}).get("NOT_DETERMINED", [None])[0]
        s = e.get("forced_slot", {}).get("before_neutral", {})
        ft = e.get("free_table", {}).get("before_neutral", {}).get("UNRESOLVED")
        print(
            f"{slug:24s} {str(d):>16s} {str(s.get('UNRESOLVED',[None])[0]):>20s} "
            f"{str(s.get('REALIZED',[None])[0]):>18s} {str(ft):>22s}"
        )
    print("\nopen-state loss = direct P(NOT_DETERMINED) - schema-slot P(UNRESOLVED), paired by base")
    for slug, e in report.items():
        if "open_state_loss" not in e:
            continue
        v = e["open_state_loss"].get("before_neutral")
        w = e["open_state_loss"].get("nontemporal_neutral")
        if v:
            extra = f"   (nontemporal control {w[0]:+.3f})" if w else ""
            print(f"  {slug:24s} {v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]{extra}")

    print(f"\nfull report: {out}")


if __name__ == "__main__":
    main()
