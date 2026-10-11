"""Retrospective check (no new model calls): does history dependence sit on tool/command identity
or on argument values?

Token classes in the teacher-forced target:
  tau (Qwen3.5 XML / Qwen3 JSON tool calls): name = function-name chars, key = parameter-name chars,
      value = parameter-value chars, syntax = everything else.
  swe (text command in the last ``` block): name = command words (first word; two for
      str_replace_editor), value = rest of the command, prose = text outside the command block.
Reports pooled dNLL by class for KVWIN_k rows, single-event KV hides on important events, and
(hybrid) recurrence carry; plus how often the *first* name token is materially affected.

usage: analyze_action.py RESULTS_DIR PREFIX MODEL_PATH CHECKPOINTS
"""
import bisect, glob, json, re, sys
from collections import defaultdict
import numpy as np
from transformers import AutoTokenizer
from render import _tmpl

D, PREFIX, MP, CK = sys.argv[1:5]
tok = AutoTokenizer.from_pretrained(MP)
cks = {json.loads(l)["cid"]: json.loads(l) for l in open(CK)}
recs = []
for f in sorted(glob.glob(f"{D}/{PREFIX}.s*.jsonl")):
    recs += [json.loads(l) for l in open(f)]
recs = [r for r in recs if "skip" not in r]


def char_classes(rec, body):
    cls = np.array(["syntax"] * len(body), dtype=object)
    if rec["src"] == "tau":
        for m in re.finditer(r"<function=([^>\n]+)>", body):
            cls[m.start(1):m.end(1)] = "name"
        for m in re.finditer(r"<parameter=([^>\n]+)>\n(.*?)\n</parameter>", body, re.S):
            cls[m.start(1):m.end(1)] = "key"
            cls[m.start(2):m.end(2)] = "value"
        m = re.search(r'"name":\s*"([^"]+)"', body)  # Qwen3 JSON format
        if m:
            cls[m.start(1):m.end(1)] = "name"
            a = body.find('"arguments"')
            if a >= 0:
                for mm in re.finditer(r'"([^"]+)":\s*("(?:[^"\\]|\\.)*"|[^,}\]]+)', body[a + 12:]):
                    cls[a + 12 + mm.start(1):a + 12 + mm.end(1)] = "key"
                    cls[a + 12 + mm.start(2):a + 12 + mm.end(2)] = "value"
    else:
        cls[:] = "prose"
        blocks = list(re.finditer(r"```(?:\w*\n)?(.*?)```", body, re.S))
        if blocks:
            b = blocks[-1]
            cmd = body[b.start(1):b.end(1)]
            words = list(re.finditer(r"\S+", cmd))
            nname = 2 if words and words[0].group() == "str_replace_editor" else 1
            cls[b.start(0):b.end(0)] = "syntax"
            for i, w in enumerate(words):
                cls[b.start(1) + w.start():b.start(1) + w.end()] = "name" if i < nname else "value"
    return cls


def token_classes(rec, r):
    msgs, tools = rec["messages"], rec.get("tools")
    k = len(msgs) - 1
    prompt = _tmpl(tok, msgs[:k], tools, True)
    full_conv = _tmpl(tok, msgs, tools, False)
    last = full_conv[full_conv.rindex("<|im_start|>assistant"):]
    body = last[len("<|im_start|>assistant\n"):]
    if body.startswith("<think>\n\n</think>\n\n"):
        body = body[len("<think>\n\n</think>\n\n"):]
    body = body.rstrip()
    if body.endswith("<|im_end|>"):
        body = body[:-len("<|im_end|>")]
    enc = tok(prompt + body, return_offsets_mapping=True, add_special_tokens=False)
    offs = enc["offset_mapping"]
    start = bisect.bisect_left([a for a, b in offs], len(prompt))
    cc = char_classes(rec, body)
    out = []
    for a, b in offs[start:]:
        a, b = a - len(prompt), b - len(prompt)
        seg = [c for c in cc[max(a, 0):max(b, a + 1)]]
        # a token is "name"/"value"/"key" if any of its chars are (priority order)
        out.append(next((c for c in ("name", "value", "key") if c in seg), seg[0] if seg else "syntax"))
    return out


tot = defaultdict(lambda: defaultdict(float))
cnt = defaultdict(lambda: defaultdict(int))
first_name_hits = defaultdict(list)
for r in recs:
    rec = cks[r["cid"]]
    cl = token_classes(rec, r)
    T = r["T"]
    if len(cl) != T:
        continue
    cl = np.array(cl)
    src = r["src"]
    for c in set(cl):
        cnt[src][c] += int((cl == c).sum())
    for k in ["0", "2", "4"]:
        d = np.array(r["kvwin"][k]["tok_dnll"], dtype=float)
        for c in set(cl):
            tot[(src, f"KVWIN{k}")][c] += d[cl == c].sum()
        nm = np.where(cl == "name")[0]
        if len(nm):
            first_name_hits[(src, k)].append(d[nm[0]])
    for e in r["events"]:
        if e["text"]["dnll"] <= 1.0:
            continue
        kv = np.array(e["kv"]["tok_dnll"], dtype=float)
        for c in set(cl):
            tot[(src, "KV_i important")][c] += kv[cl == c].sum()
        if e.get("both"):
            both = np.array(e["both"]["tok_dnll"], dtype=float)
            for c in set(cl):
                tot[(src, "carry BOTH-KV")][c] += (both - kv)[cl == c].sum()

print(f"=== {PREFIX}: {len(recs)} checkpoints")
for src in ["tau", "swe"]:
    classes = [c for c in ["name", "key", "value", "prose", "syntax"] if cnt[src].get(c)]
    print(f"\n[{src}] target tokens by class: " + ", ".join(f"{c} {cnt[src][c]}" for c in classes))
    for row in ["KVWIN0", "KVWIN2", "KVWIN4", "KV_i important", "carry BOTH-KV"]:
        if (src, row) not in tot:
            continue
        t = tot[(src, row)]
        s = sum(t.values())
        print(f"   {row:15s} " + "  ".join(f"{c}: {t[c]:8.1f} ({t[c] / s:4.0%}, {t[c] / cnt[src][c]:.3f}/tok)"
                                           for c in classes))
    for k in ["0", "2", "4"]:
        h = np.array(first_name_hits[(src, k)])
        if len(h):
            print(f"   first name token under KVWIN{k}: mean dNLL {h.mean():.3f}, >1 nat in {np.mean(h > 1):.0%} "
                  f"of {len(h)} checkpoints")
