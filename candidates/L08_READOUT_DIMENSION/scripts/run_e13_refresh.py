"""E13 Stage 2 — self-state refresh: does re-grounding an already-produced state
selectively rescue compressed trajectories?

The model generates freely under the treatment.  At a preregistered point in its OWN
trajectory, one line is injected that re-emits a number **the model itself already
produced earlier in this same trajectory**.  No new information enters: the refreshed
content was computed by this model, under this compression, and is already in the
context above.

Two injections, identical in template, position, length and provenance:

  state    the most recent correct intermediate result before the refresh point --
           the value the pending computation consumes
  placebo  an EARLIER correct intermediate result from the same trajectory, matched in
           digit length, that the pending computation does not consume

So repetition, recency, numeric token type, formatting, distance-to-answer and
"the model repeating its own words" are all held fixed.  The only difference is
whether the re-grounded state is the one the next step depends on.

Run the 2x2 by calling this with --intervention none as well:

    Delta_refresh = [Y_T(state) - Y_T(placebo)] - [Y_0(state) - Y_0(placebo)]

A rescue that also helps the full-precision model is a statement about reminders.
The claim requires the full-precision difference to be ~0.
"""
from __future__ import annotations
import argparse, importlib.util, json, pathlib, re, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src import interventions
from src.readout import ReadoutTruncation, build_mask, mask_id

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_eval", ROOT / "scripts" / "run_eval.py")
run_eval = importlib.util.module_from_spec(spec); spec.loader.exec_module(run_eval)

ANNOT = re.compile(r"<<\s*([-\d\.\+\*/\(\) ,]+?)\s*=\s*(-?[\d,]*\.?\d+)\s*>>")
TEMPLATE = " (recall: {})"          # identical for both arms; only the number differs


def annotations(text):
    """[(char_end, expr, result_str, correct)] for every calculator annotation."""
    out = []
    for m in ANNOT.finditer(text):
        expr, res = m.group(1), m.group(2)
        try:
            got = eval(expr.replace(",", ""), {"__builtins__": {}}, {})
            ok = abs(float(got) - float(res.replace(",", ""))) < 1e-6
        except Exception:
            ok = False
        out.append((m.end(), expr, res, ok))
    return out


def pick_states(text, min_gap=2):
    """(refresh_char_pos, load_bearing_value, placebo_value) or None.

    load-bearing = the most recent CORRECT result at the refresh point, i.e. the value
                   the pending computation consumes
    placebo      = an earlier CORRECT result, at least `min_gap` annotations back, whose
                   value the pending computation does not consume, matched on digits
    """
    ann = [a for a in annotations(text) if a[3]]
    if len(ann) < min_gap + 1:
        return None
    j = len(ann) - 1                       # refresh after the last correct annotation
    end, _, lb, _ = ann[j]
    cands = [a for a in ann[:j - min_gap + 1] if a[2] != lb]
    if not cands:
        return None
    # match digit length so the two injections are the same shape of token
    cands.sort(key=lambda a: abs(len(a[2]) - len(lb)))
    return end, lb, cands[0][2]


@torch.no_grad()
def generate_from(model, tok, prompts_ids, max_new, stops, eos_ids):
    """greedy continue from a batch of already-built id sequences (left-padded)."""
    pad = tok.pad_token_id or tok.eos_token_id
    L = max(len(x) for x in prompts_ids)
    inp = torch.full((len(prompts_ids), L), pad, dtype=torch.long)
    att = torch.zeros((len(prompts_ids), L), dtype=torch.long)
    for i, x in enumerate(prompts_ids):
        inp[i, L - len(x):] = torch.tensor(x); att[i, L - len(x):] = 1
    inp, att = inp.to(model.device), att.to(model.device)
    past, step_in = None, inp
    emitted = [[] for _ in prompts_ids]
    done = [False] * len(prompts_ids)
    for _ in range(max_new):
        o = model(input_ids=step_in, attention_mask=att, past_key_values=past, use_cache=True)
        past = o.past_key_values
        nxt = o.logits[:, -1, :].argmax(-1)
        for j in range(len(prompts_ids)):
            if done[j]:
                nxt[j] = pad; continue
            if int(nxt[j]) in eos_ids:
                done[j] = True
            else:
                emitted[j].append(int(nxt[j]))
        if all(done):
            break
        step_in = nxt.unsqueeze(1)
        att = torch.cat([att, torch.ones_like(step_in)], dim=1)
    outs = []
    for e in emitted:
        t = tok.decode(e, skip_special_tokens=True)
        for st in stops:
            if st in t:
                t = t.split(st)[0]
        outs.append(t)
    return outs


def assert_item_identity(items, cell, tag, root):
    """`load_items` assigns ids POSITIONALLY after shuffling a subset of size n, so
    `gsm8k-0` at n=200 is a different question than `gsm8k-0` at n=500.  Any run whose
    item set is built at a different n than the reference run is silently comparing
    different problems.  That bug produced an entire invalid control arm on
    2026-09-14; this guard exists so it cannot happen twice.  Fails loudly."""
    ref = root / "results" / "e01" / tag / f"{cell}__full.jsonl"
    if not ref.exists():
        return
    gold = {}
    for line in list(open(ref))[1:]:
        r = json.loads(line)
        gold[r["id"]] = r["gold"]
    bad = [it["id"] for it in items
           if it["id"] in gold and str(it["gold"]) != str(gold[it["id"]])]
    if bad:
        raise SystemExit(
            f"ITEM IDENTITY MISMATCH vs {ref}: {len(bad)} of {len(items)} ids carry a "
            f"different question (e.g. {bad[:3]}).  load_items ids are positional in n; "
            f"build this run at the same n as the reference run.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--cell", default="gsm8k_gen_cot")
    ap.add_argument("--intervention", default="readout:first",
                    help="readout:first | prune:0.4 | quant:4 | none")
    ap.add_argument("--trajectories", required=True,
                    help="free-running run under THIS intervention; its own states are "
                         "what get refreshed")
    ap.add_argument("--arm", required=True, choices=["state", "placebo", "null"],
                    help="null injects nothing and must reproduce the source run")
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    eos_ids = {tok.eos_token_id}
    t = tok.convert_tokens_to_ids("<|eot_id|>")
    if isinstance(t, int) and t >= 0:
        eos_ids.add(t)

    items = {it["id"]: it for it in run_eval.load_items(a.cell, a.n, 1234)}
    assert_item_identity(list(items.values()), a.cell, a.tag, ROOT)
    max_new, stops = run_eval.CELL_GEN[a.cell]

    traj = {}
    for line in open(a.trajectories):
        r = json.loads(line)
        if not r.get("_meta"):
            traj[r["id"]] = r.get("output", "") or ""

    built, skipped = [], 0
    for iid, text in traj.items():
        if iid not in items:
            continue
        pick = pick_states(text)
        if pick is None:
            skipped += 1; continue
        pos, lb, pl = pick
        inject = "" if a.arm == "null" else TEMPLATE.format(lb if a.arm == "state" else pl)
        prefix = text[:pos] + inject
        ids = tok(items[iid]["prompt"], add_special_tokens=True)["input_ids"] + \
            tok(prefix, add_special_tokens=False)["input_ids"]
        built.append((iid, ids, len(prefix), lb, pl))
    print(f"eligible {len(built)}, skipped {skipped} (too few correct annotations)",
          flush=True)

    fam, _, lvl = a.intervention.partition(":")
    if fam == "readout":
        ctx = ReadoutTruncation(model, build_mask(model.config.hidden_size, lvl, 0.5))
    elif fam == "none":
        ctx = interventions.NoOp()
    else:
        ctx = interventions.make(model, fam, float(lvl) if "." in lvl else int(lvl))

    t0 = time.time(); recs = []
    with ctx:
        order = sorted(range(len(built)), key=lambda i: -len(built[i][1]))
        for s in range(0, len(order), a.bs):
            idxs = order[s:s + a.bs]
            outs = generate_from(model, tok, [built[i][1] for i in idxs],
                                 max_new, stops, eos_ids)
            for j, i in enumerate(idxs):
                iid, ids, plen, lb, pl = built[i]
                # the scored output is the model's own prefix plus what it wrote after
                # the refresh, so the answer is always generated by the treated model
                full_text = traj[iid][:plen] if a.arm == "null" else None
                recs.append({"id": iid,
                             "output": (traj[iid][:plen] if a.arm == "null" else
                                        tok.decode(ids, skip_special_tokens=True)
                                        .split(items[iid]["prompt"][-40:])[-1]) + outs[j],
                             "n_new_tokens": len(outs[j]),
                             "arm": a.arm, "refreshed": None if a.arm == "null" else
                             (lb if a.arm == "state" else pl),
                             "load_bearing": lb, "placebo": pl,
                             "gold": items[iid]["gold"], "meta": items[iid]["meta"]})

    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    header = {"_meta": True, "model": a.model, "cell": a.cell,
              "mask": a.intervention, "arm": a.arm, "template": TEMPLATE,
              "source_trajectories": a.trajectories, "n_items": len(recs),
              "n_skipped": skipped, "data_seed": 1234,
              "runtime_s": round(time.time() - t0, 1)}
    with open(out, "w") as f:
        f.write(json.dumps(header) + "\n")
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print("wrote", out, header["runtime_s"], "s", flush=True)


if __name__ == "__main__":
    main()
