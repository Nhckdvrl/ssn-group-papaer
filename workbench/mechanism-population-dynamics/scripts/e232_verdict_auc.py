#!/usr/bin/env python3
"""E232: graded verdict readout (card: experiments/E232-*.md).
m = log P(" incorrect") - log P(" correct") at a fixed verdict stem after the check phrase, with or without a locked
recomputation text that is identical across C / S / O. AUC over items (wrong vs correct version) separates
discriminability from criterion (mean m).
usage: python e232_verdict_auc.py score <model_dir> <out.jsonl> --data scli5.json gsm8k_sc300.json [--chat]
       python e232_verdict_auc.py summarize <out.json> name=<scored.jsonl> ...
"""
import argparse, json, os, re, sys, time, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e229_blind_spot import items
from e230_check_frame import f1, f2, correct_items

FR = {"V": "Let me check whether this answer is correct.", "Wp": "Wait, let me check whether this answer is correct."}
STEM = " Verdict (correct or incorrect):"


def recompute(it, raw_gsm):
    q, g = it["q"], it["gold"]
    t = it["type"]
    if it["ds"] == "gsm8k_sc":
        s = re.sub(r"<<[^>]*>>", "", raw_gsm[it["id"]]).split("####")[0]
        return " ".join(x.strip() for x in s.strip().splitlines() if x.strip())
    if t in ("get_add_one", "get_sub_one"):
        a = re.search(r"of (\d+) [+-] 1", q).group(1)
        return f"{a} {'+' if t == 'get_add_one' else '-'} 1 = {g}."
    if t in ("get_smaller_number", "get_larger_number"):
        x, y = re.search(r"(\d+) or (\d+)", q).groups()
        other = y if x == g else x
        w = "smaller" if t == "get_smaller_number" else "larger"
        return f"{g} is {w} than {other}, so the {w} one is {g}."
    c = re.search(r"(after|before) (\S+)\?", q).group(2)
    return f"The letter {'after' if t == 'get_next_character' else 'before'} {c} is {g}."


def score(a):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16, device_map="cuda").eval()
    ti, tc = tok(" incorrect", add_special_tokens=False)["input_ids"], tok(" correct", add_special_tokens=False)["input_ids"]
    print("token ids incorrect", ti, "correct", tc, flush=True)
    ti, tc = ti[0], tc[0]
    raw = {r["id"]: r["answer"] for p in a.data if "gsm8k" in p for r in json.load(open(p))}
    wrong = items(a.data)
    right = correct_items(wrong, [r for p in a.data if "gsm8k" in p for r in json.load(open(p))])
    jobs = []
    for ver, its in (("wrong", wrong), ("right", right)):
        for it in its:
            rec = recompute(it, raw)
            for fk, fr in FR.items():
                for ro in ("direct", "locked"):
                    tail = fr + (f" Recomputing: {rec}" if ro == "locked" else "") + STEM
                    for cond in ("C", "S", "O"):
                        meta = dict(ds=it["ds"], id=it["id"], type=it["type"], ver=ver, frame=fk, ro=ro, cond=cond)
                        jobs.append((dict(meta, fmt="F1"), tok(f1(it, cond, tail))["input_ids"]))
                        if a.chat:
                            jobs.append((dict(meta, fmt="F2"), tok(f2(tok, it, cond, tail), add_special_tokens=False)["input_ids"]))
    if a.show:
        for m, ids in jobs[:: max(1, len(jobs) // 6)][:6]:
            print(m, repr(tok.decode(ids)[-300:]))
    order = sorted(range(len(jobs)), key=lambda j: len(jobs[j][1]))
    out = open(a.out, "w")
    t0 = time.time()
    for b in range(0, len(order), a.bs):
        idx = order[b:b + a.bs]
        enc = tok.pad({"input_ids": [jobs[j][1] for j in idx]}, return_tensors="pt").to("cuda")
        with torch.no_grad():
            lp = torch.log_softmax(model(**enc).logits[:, -1].float(), -1)
        for k, j in enumerate(idx):
            out.write(json.dumps(dict(jobs[j][0], m=float(lp[k, ti] - lp[k, tc]), pi=float(lp[k, ti]), pc=float(lp[k, tc]))) + "\n")
        if b // a.bs % 50 == 0:
            print(f"{b + len(idx)}/{len(order)} {time.time() - t0:.0f}s", flush=True)
    print("done", a.out, f"{time.time() - t0:.0f}s")


def auc(pos, neg):
    """P(m_wrong > m_right) with ties = 0.5"""
    allv = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    r, i, s = 0.0, 0, 0.0
    ranks = {}
    while i < len(allv):
        j = i
        while j < len(allv) and allv[j][0] == allv[i][0]:
            j += 1
        for k in range(i, j):
            if allv[k][1]:
                s += (i + j + 1) / 2
        i = j
    n1, n0 = len(pos), len(neg)
    return (s - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else None


def summarize(argv):
    out, specs = argv[0], dict(x.split("=", 1) for x in argv[1:])
    res = {}
    for name, path in specs.items():
        D = collections.defaultdict(dict)
        for r in map(json.loads, open(path)):
            D[(r["fmt"], r["ds"], r["frame"], r["ro"], r["cond"])][(r["id"], r["ver"])] = r["m"]
        for key in sorted({k[:4] for k in D}):
            cell = {}
            ids = sorted({i for c in "CSO" for (i, v) in D[key + (c,)]})
            ids = [i for i in ids if all((i, v) in D[key + (c,)] for c in "CSO" for v in ("wrong", "right"))]
            get = lambda c, v: [D[key + (c,)][(i, v)] for i in ids]
            for c in "CSO":
                cell[c + "_auc"] = round(auc(get(c, "wrong"), get(c, "right")), 3)
                cell[c + "_mean_m"] = round(sum(get(c, "wrong") + get(c, "right")) / (2 * len(ids)), 3)
            rng = random.Random(0); bs = collections.defaultdict(list)
            for _ in range(500):
                smp = [ids[rng.randrange(len(ids))] for _ in ids]
                g = lambda c, v: [D[key + (c,)][(i, v)] for i in smp]
                a_ = {c: auc(g(c, "wrong"), g(c, "right")) for c in "CSO"}
                bs["O-C"].append(a_["O"] - a_["C"]); bs["S-C"].append(a_["S"] - a_["C"])
            for k2, v in bs.items():
                v.sort(); cell["auc_" + k2] = [round(cell[k2[0] + "_auc"] - cell["C_auc"], 3), round(v[12], 3), round(v[487], 3)]
            cell["n"] = len(ids)
            res[f"{name}|{'|'.join(key)}"] = cell
    json.dump(res, open(out, "w"), indent=1)
    print(f"{'model|fmt|ds|frame|readout':40s}  n   AUC C/S/O          mean m C/S/O           AUC O-C               AUC S-C")
    for k, c in res.items():
        f = lambda v: f"{v[0]:+.3f}[{v[1]:+.3f},{v[2]:+.3f}]"
        print(f"{k:40s} {c['n']:3d}  {c['C_auc']:.2f} {c['S_auc']:.2f} {c['O_auc']:.2f}     {c['C_mean_m']:+.2f} {c['S_mean_m']:+.2f} {c['O_mean_m']:+.2f}    {f(c['auc_O-C'])}  {f(c['auc_S-C'])}")


if __name__ == "__main__":
    if sys.argv[1] == "summarize":
        summarize(sys.argv[2:]); sys.exit()
    p = argparse.ArgumentParser()
    p.add_argument("phase"); p.add_argument("model"); p.add_argument("out")
    p.add_argument("--data", nargs="*"); p.add_argument("--chat", action="store_true")
    p.add_argument("--bs", type=int, default=64); p.add_argument("--show", action="store_true")
    score(p.parse_args())
