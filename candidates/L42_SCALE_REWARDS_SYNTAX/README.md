# L42 — Does Scale Reward Syntax?

**Status:** `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`  
**Date:** 2026-09-15  
**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS

## RQ

> **As a language model gets larger, does the consequence of aligning an inductive bias with real linguistic structure shrink, stay constant, or grow?**

Operational short form for the current route:

> **Does model scale wash out a matched syntactic prior, or amplify its advantage over a mismatched structural prior?**

This is **not** the already-studied question `does syntax help language modeling?`, and it is not merely `TreeReg at another model size`.

The scientific object is the **interaction between learner scale and prior alignment**.

---

## 1. Why this question is worth asking before the method

A load-bearing scaling intuition in modern NLP is that sufficiently general architectures plus enough scale should eventually discover useful structure from data, reducing the value of hand-specified inductive bias. This is one form of the `scale is supreme / bitter lesson` belief.

But three literatures now create genuine tension.

### A. Linguistic-prior work says structure can remain valuable at substantial scale

- Hu et al. ACL 2020 find syntactic generalization varies more by architecture than by training-data size over the tested regime, and perplexity dissociates from syntactic generalization: https://aclanthology.org/2020.acl-main.158/
- Sartran et al. TACL 2022 show Transformer Grammars (TG) retain large syntax-generalization advantages at much larger model/data scales than older syntax-aware LMs: https://aclanthology.org/2022.tacl-1.81/
- Nandi et al. NAACL 2025 show TreeReg improves syntactic generalization from 71.9 to 80.0 on SG at one scratch-training scale, while randomized parses give 71.8. The same paper also finds the TreeReg-vs-Base gap **widens** as BLLIP-LG training data increases from 10% to 100%: https://aclanthology.org/2025.naacl-long.407/

### B. Other linguistic-bias results are not monotone

Gessler & Schneider CoNLL 2023 test two syntactic-bias methods in low-resource settings and find uneven gains; their English controls suggest the methods are more sensitive to data quantity than model size, and higher-data settings can even make the tested biases worse than baseline: https://aclanthology.org/2023.conll-1.17/

Thus the existing linguistic literature does **not** provide a simple law of `less data / smaller model -> bias matters more`.

### C. ICLR 2026 changes the expected scaling story in another scientific domain

Ngo & Ravanbakhsh, **Scaling Laws and Symmetry, Evidence from Neural Force Fields**, show architecture-dependent scaling exponents: equivariant architectures aligned with task symmetries scale **better** with data, parameters and compute, so the value of the prior grows with scale rather than disappearing: https://proceedings.iclr.cc/paper_files/paper/2026/hash/0918183ced31affb7ce0345e45ac1943-Abstract-Conference.html

Crucially, that paper also finds that enforcing symmetry only through a loss does not necessarily reproduce the advantage of equivariant architecture. Therefore its result cannot simply be copied onto TreeReg; whether a soft linguistic prior exhibits the same scale interaction is genuinely uncertain.

---

## 2. A+B policy: why this combination is allowed, and what would make it fail

This candidate was selected under the corrected rule:

> **`Prior A + Prior B` is not an automatic kill. It becomes a contribution only if the connection creates a new, falsifiable scientific statement that neither prior entails.**

Strong-paper calibration supports this.

- EMNLP 2025 Outstanding **Generative or Discriminative?** connects classical Efron / Ng–Jordan regime theory with Transformer-era architectures; the contribution is not the two ingredients but the newly tested conditional law in a regime where the old assumptions no longer hold: https://aclanthology.org/2025.emnlp-main.486/
- ACL 2026 Best **Characterizing the Expressivity of Local Attention in Transformers** connects an old empirical improvement from local attention with formal-language expressivity; the bridge explains a broken expectation and predicts why hybrid local/global attention can be stronger: https://aclanthology.org/2026.acl-long.1739/
- ICLR 2026 symmetry connects scaling-law analysis with explicit equivariance and obtains the new claim `matched prior changes the exponent`, not merely `equivariance helps`.

L42 passes only if the syntax + scaling connection behaves the same way intellectually: it must reveal a scale interaction / conditional law, not merely reproduce the fixed-scale TreeReg gain.

If E01 finds only a roughly constant TreeReg offset, **stop this paper identity**. A constant benefit is already too close to the existing syntax-prior literature.

---

## 3. Closest owners and strongest reviewer compression

### Closest owners

1. **Tay et al., Findings EMNLP 2023 — Scaling Laws vs Model Architectures**  
   Owns the broad claim that architecture / inductive bias can change scaling behavior and that the best architecture can depend on scale: https://aclanthology.org/2023.findings-emnlp.825/

2. **Nandi et al., NAACL 2025 — TreeReg**  
   Owns a strong soft syntactic prior, a true-vs-random parse control, and **data-scale** evidence where the gap widens with more data.

3. **Sartran et al., TACL 2022 — Transformer Grammars**  
   Owns scalable recursive syntactic bias and transformed-tree controls, but does not estimate model-size scaling laws.

4. **Gessler & Schneider, CoNLL 2023**  
   Touches model-size/data interactions for two syntactic-bias methods, but with coarse scale manipulation and downstream low-resource tasks rather than an alignment-controlled structural-generalization scaling estimand.

5. **Ngo & Ravanbakhsh, ICLR 2026 — Scaling Laws and Symmetry**  
   Owns `matched inductive bias can change parameter/data/compute scaling exponents` in geometric force-field learning, not linguistic structure.

### Strongest reviewer compression

> `TreeReg already shows true parses beat random parses and its gap grows with data + Tay 2023 says architectures scale differently + ICLR 2026 says matched symmetry changes scaling exponents -> just vary TreeReg model size.`

This compression is dangerous and is the reason L42 is **E01-only**, not a full-study authorization.

### What the compression does not already imply

None of the above tells us the direction of the **model-parameter-scale interaction for a linguistic prior**.

Plausible current predictions conflict:

- scale learns syntax itself -> prior advantage shrinks;
- prior supplies a constant finite-data shortcut -> approximately fixed offset;
- aligned structure changes effective task difficulty -> advantage grows with scale;
- implementation matters -> TreeReg soft loss may show no interaction even if a hard architectural prior would.

Therefore the first discriminating observation is genuinely informative.

**Novelty verdict:** `PLAUSIBLE INDEPENDENT CONTRIBUTION — HIGH NEAR-OWNER RISK`.

---

## 4. Central scientific quantity

For model depth / scale `d`, define

`SG_base(d)` = aggregate SyntaxGym / SG score for the ordinary LM.

`SG_true(d)` = score with TreeReg using the real BLLIP-LG constituency parses.

`SG_rand(d)` = score with TreeReg using a fixed randomized-parse corpus generated by the parent TreeReg procedure.

Define the **alignment advantage**

`A(d) = SG_true(d) - SG_rand(d)`.

This quantity is preferable to `TreeReg - Base` alone because true and randomized arms use the same model family, extra backward operation, TreeReg machinery, amount of parsed text, and update schedule; the critical difference is whether the imposed tree structure matches linguistic constituency.

Always additionally decompose:

`B(d) = SG_true(d) - SG_base(d)` — benefit of matched structure;

`C(d) = SG_rand(d) - SG_base(d)` — consequence of mismatched structure.

This prevents a growing `A(d)` from being mislabeled as `correct syntax helps more` if the real phenomenon is instead `wrong syntax hurts more`.

The E01 interaction estimand is

`I = A(16 layers) - A(4 layers)`.

The paper-level scientific object is **alignment sensitivity under scale**, not merely one arm's accuracy.

---

## 5. Why E01 scales depth first

TreeReg acts directly on hidden-state geometry. Changing hidden width at the same time as total parameter count could mechanically change the regularizer's geometry / gradient scale.

Therefore E01 varies **depth only** while keeping hidden dimension and head structure fixed.

The public TreeReg implementation directly exposes `--encoder_n_layers`, `--vec_dim`, and `--n_heads`; its BLLIP recipe uses 16 layers, hidden size 512, 8 heads, TreeReg at layer 12 on 25% of heads, every 10 LM steps. Code: https://github.com/ananjan-nandi-9/tree_regularization

Depth-only scaling does not establish a universal parameter-scaling law. It is a deliberately clean first-stage test. Width / compute-optimal scaling belongs only after E01 succeeds.

---

# 6. E01 — bounded authorization

## Status

**AUTHORIZED: E01 ONLY.**

No intermediate sizes, no second bias method, no scaling-exponent fitting, no model zoo, and no pretrained-LLM extension are authorized yet.

## Dataset and evaluation

Use the parent TreeReg BLLIP-LG setup and the full parent SG evaluation suite.

Primary metric:

> **macro aggregate SG score over the pre-specified full SG suite.**

Do not pick the 17-point Licensing sub-effect as the primary quantity after seeing results.

Secondary only:

- BLiMP;
- in-domain BLLIP perplexity;
- PTB perplexity;
- per-suite SG breakdown.

## Fixed model recipe

Use the TreeReg scratch-training implementation, preserving the parent BLLIP recipe as far as possible:

- `vec_dim = 512`;
- `n_heads = 8`;
- same tokenizer / BLLIP-LG split;
- same optimization schedule;
- same number of LM updates (`60k` in the released BLLIP command);
- same TreeReg frequency (`regularizer_steps = 10`);
- same fraction of regularized heads (`sci_heads = 0.25`);
- same training tokens / batches for all three arms within a depth;
- TreeReg applied at approximately the same relative depth: layer 12 for 16L, layer 3 for 4L.

Do not tune a different regularizer strength per scale after observing SG.

## Three arms at each depth

1. `BASE` — ordinary LM, no TreeReg.
2. `TRUE` — TreeReg with real BLLIP-LG constituency parses.
3. `RANDOM` — TreeReg with randomized parses generated by the exact parent top-down random-split procedure.

Create the randomized-parse corpus **once with a sealed seed before training**, then reuse that same randomized corpus across model depths and training seeds. This keeps the negative-control target itself fixed.

## Seeds

Use four predeclared training seeds:

`10 / 20 / 30 / 40`.

Use the same seed set in every arm and depth.

---

## 6.1 Sequential cost gate

### Phase A — reproduce the 16-layer alignment effect

Run 16L `BASE / TRUE / RANDOM` for the four seeds: **12 runs**.

Parent point estimate at one reported run/configuration:

- Base SG `71.9`;
- True TreeReg `80.0`;
- Randomized TreeReg `71.8`;
- parent alignment contrast ~= `+8.2 pp`.

Frozen Phase-A gates:

1. mean `A(16) >= +5.0 pp`;
2. `TRUE - BASE >= +5.0 pp`;
3. direction `TRUE > RANDOM` holds in at least `3/4` seeds;
4. no catastrophic training / perplexity failure invalidates one arm.

If Phase A fails: **STOP / HOLD — PARENT REPLICATION OR RESOLUTION FAILURE.**

Do not proceed to 4L and do not switch to TG to rescue the phenomenon.

### Phase B — small-scale endpoint

Only if Phase A passes, run the same three arms at 4L with the same four seeds: another **12 runs**.

Support gate:

- the 4L baseline must be materially above SG chance/floor (`aggregate SG >= 55`) and train normally;
- otherwise mark `HOLD — SMALL-SCALE FLOOR`, because a scale interaction cannot be interpreted cleanly.

---

## 6.2 Primary interaction gate

Compute

`I = [TRUE16 - RANDOM16] - [TRUE4 - RANDOM4]`.

Report seed-level values and a hierarchical seed/item bootstrap; the pilot CI is evidence for promotion, not a publication-grade scaling-law estimate.

### Material interaction threshold

Require

> `|I| >= 5.0 pp`

and

> the 95% hierarchical bootstrap CI excludes 0,

with the seed-paired interaction having the same sign in at least `3/4` seed indices.

Why 5 pp: the existing alignment contrast is ~8 pp at 16L. A shift smaller than ~5 pp across the 4x depth range is unlikely to support a paper whose central claim is that scale qualitatively changes the value of linguistic structure, and would be too easy to narrate from noise / fixed offsets.

### Pre-result interpretation

- `I >= +5 pp`: **scale amplifies alignment sensitivity**. Larger models distinguish matched from mismatched structure more strongly. This directly contradicts a simple `scale washes out structural prior` story and authorizes a fresh E02 selection audit.
- `I <= -5 pp`: **scale washes out alignment sensitivity**. This supports a bitter-lesson-style interpretation and is equally worth an E02 audit if the effect is clean.
- `|I| < 5 pp` or CI includes 0: **NO-GO for the current scaling-law paper identity.** A roughly constant TreeReg advantage is useful engineering evidence but is already too close to existing prior work.
- apparent interaction caused entirely by small-model floor / failed training: **HOLD / instrument invalid**.

### Mandatory decomposition

Always report `B(d)=TRUE-BASE` and `C(d)=RANDOM-BASE`.

If `A(d)` grows because `TRUE` improves with scale, the interpretation is `matched prior increasingly helps`.

If it grows because `RANDOM` increasingly hurts, the interpretation is `scale increases sensitivity to structural misalignment`.

Both fit the predeclared **alignment-sensitivity** RQ; do not collapse them into the same mechanistic claim.

---

## 7. Instrument-strength audit

Because TreeReg is an auxiliary gradient operation, record at initialization / a fixed early checkpoint:

- LM gradient norm;
- TreeReg gradient norm on a fixed parse batch;
- ratio `||g_TR|| / ||g_LM||`;
- raw TreeReg score;

for TRUE and RANDOM at both depths.

This is a construct diagnostic, **not** a tuning loop. Do not adjust hyperparameters after observing SG merely to equalize these numbers.

If the interaction is accompanied by a gross scale-dependent implementation pathology (e.g. the regularizer update explodes or vanishes only at one depth), do not call it a scientific scaling effect.

---

## 8. Resolution / compute audit

This pilot is bounded but non-trivial.

Maximum authorized work:

- 12 parent-scale (16L) scratch runs;
- if and only if Phase A passes, 12 four-layer runs;
- **24 total runs maximum**.

Because the 4L models have one quarter the Transformer block depth of the parent 16L model, the total training work is roughly on the order of **15 parent-16L run-equivalents**, ignoring fixed embedding / evaluation overhead. The code currently has limited multi-GPU optimization, but independent seeds / arms can be run independently.

Do not quote a precise GPU-hour estimate until one short dry-run has measured actual throughput on the available environment.

The parent effect (`~8.2 pp` true-vs-random at 16L) is large enough that a `5 pp` scale interaction is at least plausibly resolvable; four training seeds are required because the parent BLLIP experiment does not provide a sufficient seed-level noise estimate for the current interaction claim.

---

## 9. Successful-result chain

A clean material interaction would support:

> **same language input + same Transformer family + same structural-regularization mechanism + matched vs mismatched structure**  
> -> prior-alignment advantage changes with learner scale  
> -> linguistic inductive bias is not merely a fixed finite-data offset  
> -> `scale learns the bias away` is not a generally valid law (or, for the opposite sign, is supported in this controlled regime)  
> -> model scale and linguistic prior must be treated jointly in theories of structural generalization.

What E01 alone does **not** establish:

- a universal scaling exponent;
- a result about all linguistic biases;
- compute-optimal scaling;
- a result about pretrained frontier LLMs;
- that soft TreeReg and hard syntactic architectures behave identically.

---

## 10. Main-level growth path — only if E01 passes

A successful E01 returns to Selection before further compute.

A plausible Main-level program would need:

### C1 — establish the scale curve

Add intermediate / larger depth or parameter scales and fit the interaction / scaling relationship with enough points to distinguish monotone, crossover and approximately constant behavior. E01 endpoints alone are not a scaling law.

### C2 — replicate with a qualitatively different prior mechanism

Use a hard structural-bias family such as Transformer Grammars, with the same-tree `TG vs TXL(trees)` comparison and transformed / incorrect-tree controls.

This is particularly important because ICLR 2026 symmetry reports that loss-enforced symmetry does not necessarily scale like architectural equivariance. A general claim therefore needs both a soft-loss and hard-architecture route, or must explicitly stay TreeReg-specific.

### C3 — separate structural-generalization scaling from ordinary LM-loss scaling

Test whether the prior changes the scaling of syntactic generalization even when ordinary held-out NLL/perplexity shows a different or much weaker interaction. ACL 2020 already shows SG and perplexity can dissociate; the new contribution would be a scale-dependent law, not merely another dissociation point.

### C4 — conditional law, not model zoo

Use the full result to reconcile why some prior work shows amplification with data (TreeReg), some low-resource SIB methods show little benefit or degradation (CoNLL 2023), and inference-time representation bias can exhibit crossovers with model scale.

Do **not** expand into dozens of syntax methods merely for breadth. Two qualitatively distinct bias mechanisms with strong alignment controls are more valuable than a large leaderboard.

---

## 11. Final Selection verdict

### Question

**PASS.** Low description length, high consequence, real disagreement, both directions matter.

### Ownership

**PASS WITH HIGH RISK.** Components are heavily owned; the **parameter-scale × matched-linguistic-prior interaction** is not directly owned by the audited literature. A+B is allowed here because it produces a new falsifiable statement rather than a restatement of either component.

### Identification

**PASS FOR E01.** Same architecture/data plus TRUE/RANDOM/BASE controls isolate alignment better than a model-zoo comparison. Depth-only scaling avoids an avoidable hidden-width confound.

### Resolution

**PASS FOR BOUNDED PILOT.** Parent true-vs-random signal is ~8 pp; a 5 pp interaction is a suitably demanding first-stage target. Full exponent estimation is **not** authorized.

### Main-level path

**PLAUSIBLE, NOT YET ESTABLISHED.** A single TreeReg scale interaction is not enough for ACL/EMNLP/NAACL Main. Independent hard-prior replication and an actual scale curve are required after E01.

# FINAL STATUS

> **L42 — PILOT-AUTHORIZED — E01 ONLY.**

No E02, model zoo, TG replication, width scaling, pretrained-LLM extension, or paper claim is authorized until E01 is completed and re-enters Selection.
