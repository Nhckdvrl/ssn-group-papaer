#!/usr/bin/env python3
"""E233 / E234 signal-detection summary. H = share of B (reject / change) on WRONG given answers, F = share of B on CORRECT
given answers (verdict judge + endorsement rule). Wrong and correct sets may or may not share item ids (on-policy: not).
Bootstrap resamples wrong and correct items independently. Optional gate file (clean judged) keeps items answered correctly.
usage: python e23x_sdt.py out.json name=<wrong verdict>,<right verdict>[,<clean judged>] ..."""
import json, sys, random, collections
from e230_rule import final
FR = {"V": "Let me check whether this answer is correct.", "W": "Wait,", "N": ""}


def load(path):
    d = collections.defaultdict(dict)
    for r in map(json.loads, open(path)):
        ds = "onpolicy" if r["ds"].startswith("onpolicy") else r["ds"]
        d[(r["fmt"], ds, r.get("frame", "N"))].setdefault(r["cond"], {})[r["id"]] = final(r, FR) == "B"
    return d


def main():
    out, specs = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
    res = {}
    for name, paths in specs.items():
        ps = paths.split(",")
        Hd, Fd = load(ps[0]), load(ps[1])
        gate = None
        if len(ps) > 2:
            gate = {(r["fmt"], r["ds"], r["id"]) for r in map(json.loads, open(ps[2])) if r["cond"] == "clean" and r["judge"]}
        for key in sorted(set(Hd) & set(Fd)):
            conds = [c for c in "CSOU" if c in Hd[key] and c in Fd[key]]
            ok = lambda i: gate is None or (key[0], key[1], i) in gate
            hid = sorted(i for i in set.intersection(*[set(Hd[key][c]) for c in conds]) if ok(i))
            fid = sorted(i for i in set.intersection(*[set(Fd[key][c]) for c in conds]) if ok(i))
            if not hid or not fid:
                continue
            cell = dict(nH=len(hid), nF=len(fid))
            for c in conds:
                h = sum(Hd[key][c][i] for i in hid) / len(hid); f = sum(Fd[key][c][i] for i in fid) / len(fid)
                cell[c] = dict(H=round(h, 3), F=round(f, 3), HmF=round(h - f, 3))
            rng = random.Random(0)
            bs = collections.defaultdict(list)
            for _ in range(1000):
                sh = [hid[rng.randrange(len(hid))] for _ in hid]; sf = [fid[rng.randrange(len(fid))] for _ in fid]
                hm = {c: sum(Hd[key][c][i] for i in sh) / len(sh) - sum(Fd[key][c][i] for i in sf) / len(sf) for c in conds}
                for c in conds:
                    if c != "C":
                        bs[c + "-C"].append(hm[c] - hm["C"])
                if "U" in conds and "S" in conds:
                    bs["U-S"].append(hm["U"] - hm["S"])
            for k, v in bs.items():
                v.sort(); a, b = k.split("-")
                cell["d" + k] = [round(cell[a]["HmF"] - cell[b]["HmF"], 3), round(v[25], 3), round(v[974], 3)]
            res[f"{name}|{'|'.join(key)}"] = cell
    json.dump(res, open(out, "w"), indent=1)
    for k, c in res.items():
        parts = " ".join(f"{x}:H{c[x]['H']:.2f}/F{c[x]['F']:.2f}" for x in "CSOU" if x in c)
        ds = " ".join(f"{d}={c[d][0]:+.2f}[{c[d][1]:+.2f},{c[d][2]:+.2f}]" for d in c if d.startswith("d"))
        print(f"{k:34s} nH{c['nH']:4d} nF{c['nF']:4d}  {parts}  {ds}")


if __name__ == "__main__":
    main()
