"""E12 Stage 1 — prefix clamping: is compression damage trajectory-mediated?

Compression reaches the answer by two paths:

    direct      T -> Y              this step's computation is damaged
    mediated    T -> Z(T) -> Y      this step conditions on context that was itself
                                    produced under the treatment

To separate them, the treated model generates normally except that for the first `k`
generated steps the token appended to the context is **overridden** to a reference
trajectory.  The treated model still runs its own forward pass at every step, so the
direct damage is present on 100% of steps in every arm; `k` varies only how much of
the conditioning context is treatment-generated.

This is the separation E07 could not make.  E07 moved the intervention window, which
changes direct-damage dose and trajectory contamination together.  Clamping holds the
first fixed.  It also never modifies the model mid-generation, so unlike an E07-style
schedule it applies unchanged to Wanda / SparseGPT / AWQ / GPTQ.

Arms (`--clamp`):
    none        Z(T)   free-running, the treated model's own prefix
    reference   Z(0)   the full-precision trajectory: untreated AND correct
    corrupted   Z~(0)  reference perturbed to a matched task-error rate: untreated,
                       NOT correct.  Required, because `reference` alone confounds
                       "untreated" with "correct" and the contrast is then readable as
                       ordinary error propagation.

    Y(R)  - Y(F)   total trajectory mediation
    Y(R)  - Y(R~)  the part explained by prefix content being worse (exposure bias)
    Y(R~) - Y(F)   residual: produced-under-the-same-perturbation, beyond content
"""
from __future__ import annotations

import argparse, importlib.util, json, pathlib, re, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src import interventions
from src.readout import ReadoutTruncation, build_mask, mask_id

spec = importlib.util.spec_from_file_location(
    "run_eval", pathlib.Path(__file__).resolve().parent / "run_eval.py")
run_eval = importlib.util.module_from_spec(spec); spec.loader.exec_module(run_eval)

ANS = re.compile(r"[Aa]nswer\s*(?:is)?\s*:?\s*\(?([ABCD])\)?")
NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def answer_char_pos(cell: str, out: str):
    """Character offset of the answer-bearing token in a reference trajectory."""
    if cell.startswith("mmlu"):
        m = ANS.search(out) or re.search(r"\b([ABCD])\b", out[:200])
    else:
        m = re.search(r"####", out)
        if m is None:
            hits = list(NUM.finditer(out.replace("$", " ")))
            m = hits[-1] if hits else None
    return m.start() if m else None


def reference_table(tok, ref_path: pathlib.Path, cell: str):
    """id -> {ids: reference token ids, L0: answer position in TOKENS}.

    The clamp operates on token ids, never on text, so no retokenization drift can
    enter between measuring L0 and applying the override.
    """
    out = {}
    for line in open(ref_path):
        r = json.loads(line)
        if r.get("_meta"):
            continue
        text = r.get("output", "") or ""
        ids = tok(text, add_special_tokens=False)["input_ids"]
        cp = answer_char_pos(cell, text)
        L0 = len(tok(text[:cp], add_special_tokens=False)["input_ids"]) if cp is not None else None
        out[r["id"]] = {"ids": ids, "L0": L0}
    return out


class StepCounter:
    """Counts lm_head forward passes, to verify the intervention is active on all."""

    def __init__(self, model):
        self.model, self.n, self.h = model, 0, None

    def __enter__(self):
        def hook(*_a):
            self.n += 1
        self.h = self.model.lm_head.register_forward_pre_hook(lambda m, a: hook())
        return self

    def __exit__(self, *e):
        if self.h:
            self.h.remove(); self.h = None


@torch.no_grad()
def generate_clamped(model, tok, items, refs, ks, max_new, stops, bs):
    """Greedy decode; for generated step t < k[id], override the emitted token.

    The forward pass is executed at every step for every item regardless of clamping,
    so the treated computation is applied identically across arms.
    """
    pad = tok.pad_token_id or tok.eos_token_id
    eos = {tok.eos_token_id}
    if tok.convert_tokens_to_ids("<|eot_id|>") is not None:
        t = tok.convert_tokens_to_ids("<|eot_id|>")
        if isinstance(t, int) and t >= 0:
            eos.add(t)
    order = sorted(range(len(items)), key=lambda i: -len(items[i]["prompt"]))
    results = {}
    for s in range(0, len(order), bs):
        idxs = order[s:s + bs]
        batch = [items[i] for i in idxs]
        enc = tok([b["prompt"] for b in batch], return_tensors="pt",
                  padding=True, padding_side="left").to(model.device)
        cur = enc["input_ids"]
        attn = enc["attention_mask"]
        past = None
        emitted = [[] for _ in batch]
        done = [False] * len(batch)
        n_steps = [0] * len(batch)
        n_clamped = [0] * len(batch)
        step_in = cur
        for t in range(max_new):
            o = model(input_ids=step_in, attention_mask=attn, past_key_values=past,
                      use_cache=True)
            past = o.past_key_values
            nxt = o.logits[:, -1, :].argmax(-1)            # the treated decision
            for j, b in enumerate(batch):
                if done[j]:
                    nxt[j] = pad
                    continue
                n_steps[j] += 1
                k = ks.get(b["id"], 0)
                ref = refs.get(b["id"], {}).get("ids", [])
                if t < k and t < len(ref):
                    nxt[j] = ref[t]                        # override the emission only
                    n_clamped[j] += 1
                if int(nxt[j]) in eos:
                    done[j] = True
                else:
                    emitted[j].append(int(nxt[j]))
            if all(done):
                break
            step_in = nxt.unsqueeze(1)
            attn = torch.cat([attn, torch.ones_like(step_in)], dim=1)
        for j, i in enumerate(idxs):
            txt = tok.decode(emitted[j], skip_special_tokens=True)
            for st in stops:
                if st in txt:
                    txt = txt.split(st)[0]
            results[i] = {"id": items[i]["id"], "output": txt,
                          "n_new_tokens": len(emitted[j]),
                          "n_forward_steps": n_steps[j],
                          "n_clamped_steps": n_clamped[j],
                          "k": ks.get(items[i]["id"], 0),
                          "gold": items[i]["gold"], "meta": items[i]["meta"]}
    return [results[i] for i in range(len(items))]


def assign_k(refs, frac, seed):
    """k as a fraction of each item's own reference answer position, in tokens."""
    ks = {}
    for iid, r in refs.items():
        if r["L0"] is None:
            continue
        ks[iid] = int(round(frac * r["L0"]))
    return ks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--cell", default="gsm8k_gen_cot")
    ap.add_argument("--intervention", default="readout:first",
                    help="readout:first | readout:last | prune:0.4 | quant:4 | none")
    ap.add_argument("--clamp", default="none",
                    choices=["none", "reference", "corrupted", "foreign", "self"],
                    help="foreign: a prefix produced by a DIFFERENT treatment on the "
                         "same items -- treated, and of comparable quality, but not by "
                         "this perturbation.  self: this model's own free-running "
                         "prefix, which must reproduce free-running exactly (V4).")
    ap.add_argument("--clamp-source", default=None,
                    help="jsonl of trajectories to clamp to; defaults to the e01 full run")
    ap.add_argument("--frac", type=float, default=0.0,
                    help="k / L0, the fraction of the reference answer position clamped")
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parents[1]
    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()

    items = run_eval.load_items(a.cell, a.n, 1234)
    max_new, stops = run_eval.CELL_GEN[a.cell]

    # k is ALWAYS derived from the reference trajectory's answer position, and the
    # clamped TOKENS come from whichever source the arm names.  Deriving k from the
    # corrupted trajectory instead would give the R and R~ arms different clamped
    # span lengths, confounding the contrast that isolates prefix content with a
    # difference in depth -- which is the one thing this design exists to avoid.
    ref_run = root / "results" / "e01" / a.tag / f"{a.cell}__full.jsonl"
    src = pathlib.Path(a.clamp_source) if a.clamp_source else ref_run
    refs, ks = {}, {}
    if a.clamp != "none":
        k_table = reference_table(tok, ref_run, a.cell)
        ks = assign_k(k_table, a.frac, 1234)
        refs = reference_table(tok, src, a.cell) if src != ref_run else k_table
        # an item with no reference answer position has no defined k and is not clamped
        ks = {i: k for i, k in ks.items() if i in refs}

    fam, _, lvl = a.intervention.partition(":")
    t0 = time.time()
    if fam == "readout":
        mask = build_mask(model.config.hidden_size, lvl, 0.5)
        ctx = ReadoutTruncation(model, mask)
        iv_meta = {"family": "readout", "mask": lvl, "mask_id": mask_id(mask)}
    elif fam == "none":
        ctx = interventions.NoOp()
        iv_meta = {"family": "none"}
    else:
        ctx = interventions.make(model, fam, float(lvl) if "." in lvl else int(lvl))
        iv_meta = {"family": fam, "level": lvl}

    with ctx, StepCounter(model) as sc:
        recs = generate_clamped(model, tok, items, refs, ks, max_new, stops, a.bs)

    out = pathlib.Path(a.out) if a.out else (
        root / "results" / "e12" / a.tag /
        f"{a.cell}__{a.intervention.replace(':','')}__{a.clamp}__f{a.frac:g}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    header = {"_meta": True, "model": a.model, "cell": a.cell, "mask": a.intervention,
              "intervention": iv_meta, "clamp": a.clamp, "clamp_source": str(src),
              "k_from": str(ref_run), "n_clamped_items": len(ks),
              "frac": a.frac, "n_items": len(recs), "data_seed": 1234,
              "lm_head_forward_passes": sc.n,
              "total_generated_steps": sum(r["n_forward_steps"] for r in recs),
              "total_clamped_steps": sum(r["n_clamped_steps"] for r in recs),
              "runtime_s": round(time.time() - t0, 1)}
    with open(out, "w") as f:
        f.write(json.dumps(header) + "\n")
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print("wrote", out, header["runtime_s"], "s", flush=True)


if __name__ == "__main__":
    main()
