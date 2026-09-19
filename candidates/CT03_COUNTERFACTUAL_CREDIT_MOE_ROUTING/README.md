# CT03 — Counterfactual Credit for MoE Routing

**Status:** `PILOT — E01 in progress` · **Opened:** 2026-09-20
**Topic authority:** `chasing trends/topics/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING.md`
**Current gate:** E01 only. No router is trained, and no benchmark is run,
until E01 is adjudicated against the pre-registered bar in `docs/E01_DESIGN.md` §9.

## The object

A pretrained sparse MoE router only ever receives task-loss feedback through the
experts it actually executed. The parent diagnostic (*When Are Experts
Misrouted?*) shows that on fragile reasoning tokens a better equal-compute route
already exists inside the frozen model, and buys that knowledge by **executing**
sampled alternative routes.

CT03 asks whether the same signal can be had for almost nothing:

```
dL_hat(i->j)  ~=  grad_h L^T ( h^{i->j} - h )
```

one shared backward, plus a local forward of a few unexecuted experts, instead
of a full downstream rerun per alternative route. If that estimate is faithful,
counterfactual credit becomes cheap enough to supervise **every** MoE layer, and
inference stays ordinary Top-K.

## What lives or dies in E01

Faithfulness, and nothing else. `docs/E01_DESIGN.md` is frozen and names the
continue/kill thresholds before any number exists. The two failure modes it
separates:

- a **Taylor** failure — the first-order term just does not predict the loss
  change (visible as `px_tok` vs `dL_tok` breaking down);
- a **gradient-sharing** failure — the per-token estimate is fine but the one
  shared backward the method actually needs is not (`px_shared` vs `dL_seq`).

The second is the one the efficiency claim rests on, so it is the primary
pairing. Collapsing the two would let a dead method look alive.

## Layout

```
docs/E01_DESIGN.md     frozen design + pre-registered adjudication
src/e01_validity.py    section 8 implementation checks; must pass first
src/e01_credit.py      exact-vs-proxy harness -> results/e01_records.jsonl
src/e01_report.py      records -> results/e01_report.json + headline table
results/logs/          launch logs, host/card assignment
```

## Reproduction

```
PY=/home/xiang/miniconda3/envs/verl-clean/bin/python
$PY src/e01_validity.py                 # must exit 0
$PY src/e01_credit.py --n-problems 32
$PY src/e01_report.py --exact dL_seq
$PY src/e01_report.py --exact dL_tok --out results/e01_report_tok.json
```

Model `allenai/OLMoE-1B-7B-0924-Instruct` (16 layers, 64 experts, top-8,
`norm_topk_prob=false`), float32, one card. Data: `HuggingFaceH4/MATH-500`
solutions, teacher-forced. AIME/HMMT are not touched at this stage.
