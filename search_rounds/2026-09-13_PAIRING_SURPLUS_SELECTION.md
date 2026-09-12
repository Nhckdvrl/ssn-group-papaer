# 2026-09-13 — Pairing-Surplus Selection Audit

**Target:** ACL / EMNLP / NAACL Main  
**Candidate:** `L30 — What Does Pairing Teach?`  
**Final status:** **PILOT-AUTHORIZED — E01 ONLY**

Package: `candidates/L30_PAIRING_SURPLUS/`

---

## Research question

> **If pretrained language models can become substantially instruction-following from responses alone, what additional behavior is actually learned from the correct correspondence between an instruction and its response?**

The central estimand is the marginal causal value of the joint dependence after holding prompt and response marginals fixed:

`Pairing Surplus = Performance(P_XY) - Performance(P_X P_Y)`

This is an interventional training quantity, not a data-quality metric.

---

## Scientific origin

The candidate is grounded in several established results:

- Hewitt et al., **Instruction Following without Instruction Tuning**: response-only tuning, without paired instructions, can unlock substantial instruction following; pretrained models already show nontrivial response-ranking structure. https://arxiv.org/abs/2409.14254
- An et al., **Revealing the Inherent Instructability of Pre-Trained Language Models** (Findings EMNLP 2025): Response Tuning removes the instruction and its mapping and still produces broad instruction-following behavior. https://aclanthology.org/2025.findings-emnlp.285/
- Chatterjee et al., **On the Effect of Instruction Tuning Loss on Generalization** (TACL 2025): prompt-token supervision can independently affect instruction-following/generalization. https://aclanthology.org/2025.tacl-1.62/
- Vergara-Browne et al., **Operationalising the Superficial Alignment Hypothesis via Task Complexity** (ICML 2026): pretraining can make high instruction-following performance reachable with very little adaptation information. https://arxiv.org/abs/2602.15829

Important correction made during selection: An et al.'s conventional IT baseline also computes loss on response tokens; IT–RT therefore does **not** mix prompt-token loss with pairing. The extra information in IT is that response prediction is conditioned on the paired instruction. WIT is a separate evidence line.

---

## Closest owners and reviewer compression

The project cannot claim that instruction-response alignment is new or that nobody has studied pair quality.

Strong neighbors include:

- **MAIN: Mutual Alignment Is Necessary for instruction tuning** (EMNLP 2025 Main): https://aclanthology.org/2025.emnlp-main.644/
- **FedDQC** (Findings ACL 2025), including an IRA score based on response likelihood with versus without the instruction: https://aclanthology.org/2025.findings-acl.791/
- **The Wisdom of Hindsight Makes Language Models Better Instruction Followers** (ICML 2023): https://proceedings.mlr.press/v202/zhang23ab.html

Strongest compression:

> `response marginal works + prompt-side supervision helps + aligned pairs are better + pretraining already contains much instructability = pairing obviously matters; this is another alignment ablation.`

This compression does not identify the target counterfactual. The closest work does not hold the same prompt pool and response pool fixed while manipulating only whether the correspondence is correct, absent, or wrong and then interpret the resulting downstream instruction-following change as the marginal causal value of the joint dependence.

**Novelty verdict:** `PLAUSIBLE INDEPENDENT CONTRIBUTION`.

---

## Identification

The authorized pilot uses three conceptual arms with matched marginals/budget:

- **P — Paired:** correct `x_i → y_i` correspondence.
- **D — Decoupled:** remove usable response→paired-prompt dependence while preserving the relevant marginal/budget controls.
- **S — Shuffled:** use the same prompt and response pools but randomly permute the correspondence.

Primary quantities:

- `Δ_pair = P - D`
- `Δ_wrong = D - S`
- `Δ_corr = P - S`

`P vs S` is the cleanest same-marginal contrast. `D` separates missing correspondence from actively wrong correspondence.

The exact D implementation must pass a construct sanity check. A conventional RT arm may be used only as the minimum sanity anchor needed to ensure D is not an attention/position artifact.

**Identification verdict:** `PASS FOR PILOT`, conditional on D validity.

---

## Outcome interpretation

Pre-result outcome map:

- `P > D ≈ S`: genuine pairing surplus / new conditional control is learned.
- `P ≈ D > S`: base map + marginal adaptation largely suffices; wrong correspondence actively corrupts useful conditional structure.
- `P ≈ S > D`: semantic correctness is not load-bearing; generic prompt-conditioned training may be the real factor; current pairing story requires re-selection.
- `P ≈ D ≈ S`: correspondence is not load-bearing at resolvable scale in this regime. Tight null may be scientifically useful but is not automatically Main-scale; loose null is HOLD.

The candidate does not depend on one lucky reversal.

---

## Resolution / pilot regime

Preferred starting regime: **Gemma-2-2B + Alpaca-Cleaned**, with exact source compatibility verified before running.

Preferred primary evaluation: **IFEval**, because the constraints are mechanically checkable and the load-bearing result need not use an LLM judge.

Use prompt-clustered uncertainty and multiple training seeds (default target: 3 if the intended 2B-scale setup remains cheap).

Working selection guidance:

- ~`3–4 pp+` stable effect: potentially sufficient to justify C2 re-selection;
- near-null is substantive only with tight intervals;
- if differences are ~`≤2 pp` while intervals still allow `3–4 pp`, mark `HOLD — PILOT UNDER-RESOLVED` rather than claiming that pairing is unimportant.

Unlike L19, the load-bearing quantity is not already known to sit below feasible measurement resolution.

**Resolution verdict:** `PASS FOR PILOT`.

---

## Main-level growth path

E01/C1 is identification, not the full paper.

A paper that only reports “shuffling responses costs N IFEval points” is below the intended bar because prior work already establishes broad alignment importance.

The strongest C2 path is a conditional law:

> **Does the pretrained model's existing `X→Y` association predict the causal value of preserving that pair during post-training?**

Two live accounts make opposite predictions:

- **Pretraining-completion:** stronger pretrained association → smaller pairing surplus.
- **Alignment-quality / learnability:** stronger pretrained association → larger pairing surplus.

FedDQC's IRA-like quantity is an existing operationalization and is **not** itself novel. A future C2 should intervene on which pre-motivated high/low-association pairs retain correspondence while controlling obvious difficulty variables, rather than merely report an item-level correlation.

C2 is not authorized until E01 establishes a stable, resolvable quantity and the candidate returns to selection.

---

## Final authorization

> **PILOT-AUTHORIZED — E01 ONLY**

Authorized: bounded small-model multi-seed P/D/S training pilot + deterministic instruction-following evaluation + minimum RT sanity control needed to validate D.

Not authorized: C2 IRA-stratified intervention, hidden-state/activation work, large sweeps, new benchmark construction, method development, full-study claims.

The locked paper identity remains:

> **What does the correct instruction-response pairing teach beyond the two marginals?**
