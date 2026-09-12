# L30 Agent Handoff — What Does Pairing Teach?

You are taking over `candidates/L30_PAIRING_SURPLUS/` in `Nhckdvrl/ssn-group-papaer`.

Current status:

> **PILOT-AUTHORIZED — E01 ONLY**

Do not treat this as permission to build a full paper, add mechanistic analyses, or optimize a new training method. The immediate job is to answer one scientific question cleanly enough that we know whether there is a real project to continue.

Before working, sync the latest `main` and read:

- `candidates/L30_PAIRING_SURPLUS/README.md`
- `RESEARCH_EXECUTION.md`
- `RESEARCH_TOPIC_SELECTION.md`
- `CURRENT_SEARCH.md`

The candidate README is authoritative for the current claim and authorization scope.

---

# Scientific problem

Instruction tuning appears to require instruction-response pairs, but several strong results make the actual role of the **pairing** surprisingly unclear.

Hewitt et al. and An et al. show that training only on response strings, with the instructions removed, can unlock a large fraction of instruction-following behavior. This is evidence that pretraining already contains much of the usable instruction→response structure and that post-training can expose it without learning every mapping from scratch.

WIT independently shows that prompt-side token supervision can also affect instruction following/generalization. ICML 2026 work on the Superficial Alignment Hypothesis further argues that pretrained models can make high downstream performance reachable with surprisingly little adaptation information.

At the same time, MAIN, FedDQC, Hindsight Instruction Relabeling, and related work show that instruction-response alignment is useful. Therefore the open question is **not** whether aligned pairs are generally better data.

The actual question is:

> **If we hold the prompt marginal and response marginal fixed, what additional behavior is learned solely because each response is paired with its correct instruction?**

A compact way to think about the estimand is:

> `Pairing Surplus = Performance(correct joint P_XY) - Performance(same marginals without the useful joint dependence)`

This is a causal training quantity, not a data-quality score.

---

# Why the question is novel enough to test

The strongest reviewer compression is already known:

> response-only tuning works + prompt-side loss can help + aligned pairs are better + pretraining already contains much of instructability = of course pairing matters somehow.

That compression does **not** answer our question.

Existing alignment papers mostly compare better versus worse pairs or define alignment/quality scores. RT removes instructions entirely. None of the closest owners we found cleanly holds the exact prompt pool and response pool fixed while changing only whether the `X↔Y` correspondence is correct, absent, or wrong, and then asks what downstream instruction-following behavior this joint dependence causally buys.

Do not oversell this. The novelty is not the word “alignment,” not mutual information, and not shuffling as a technique. The novelty is the **identified marginal contribution of correspondence beyond the marginals**, and—if E01 gives enough signal—the possibility of a later conditional law explaining where that contribution is needed.

---

# What E01 must establish

The pilot should separate three scientifically different worlds:

1. **Correct correspondence teaches conditional control.**
   Pretraining/marginal adaptation supplies generic instructability, but true pair dependence still adds requirement-specific binding.

2. **The pretrained map already does most of the work.**
   Once the response distribution is adapted, the new paired relation adds little in this regime.

3. **Wrong correspondence actively corrupts useful pretrained structure.**
   Correct pairing may matter partly because inconsistent supervision can damage a map the base model already has.

This is why the conceptual three-arm decomposition matters:

- **P — Paired:** response sees its true instruction.
- **D — Decoupled:** preserve the relevant marginal/training-budget controls but remove usable instruction→response dependence.
- **S — Shuffled:** preserve the same prompt and response pools while deliberately giving responses the wrong prompts.

The exact code-level implementation is not sacred. In particular, D is only useful if it is a valid correspondence-free control rather than an exotic attention-mask artifact. You should understand the intended causal contrast, inspect the source implementations and data format, and choose the least confounded realization. A conventional RT arm can be used as a sanity anchor for D.

The cleanest correspondence contrast is **P vs S** because the prompt and response marginals are identical. D tells us whether shuffled data is merely missing the correct mapping or is actively teaching the wrong one.

Do not introduce prompt-only WIT training into the pilot simply because it is related. WIT is mother evidence, not the central estimand.

---

# Preferred pilot regime and evidence

The current preferred starting point is **Gemma-2-2B + Alpaca-Cleaned**, because it keeps the pilot cheap and is close to regimes used in the mother literature. Verify the exact checkpoints, preprocessing, chat formatting, and dataset versions from the original RT/WIT repositories before training. If an exact intersection is not technically possible, preserve the scientific comparison rather than mechanically obeying a model name; document the deviation before looking at outcomes.

The preferred primary evaluation is **IFEval** because its constraints are programmatically checkable and the load-bearing result need not depend on an LLM judge. InFoBench may be useful as a secondary evaluation because the RT line uses decomposable requirements, but do not add benchmarks just to search for a positive sign.

The inferential unit must respect prompt clustering. Do not treat multiple constraints attached to one prompt as independent evidence. Report prompt-clustered uncertainty and training-seed variation.

The pilot should be small enough that we can afford multiple seeds. The current default expectation is **3 training seeds** if the implementation cost remains in the intended 2B-scale regime.

---

# Quantities we care about

Keep these meanings stable even if implementation details change:

- `Δ_pair = P - D`: what correct correspondence buys over an approximately correspondence-free condition.
- `Δ_wrong = D - S`: whether wrong correspondence actively damages learning relative to no usable correspondence.
- `Δ_corr = P - S`: the clean same-marginal causal value of correct versus wrong correspondence.

The point is not merely whether one arm wins. The relative pattern distinguishes what pairing is doing.

Examples:

- `P > D ≈ S` supports a genuine pairing surplus / conditional-control story.
- `P ≈ D > S` says the base map plus marginals may already suffice and wrong correspondence mainly corrupts it.
- `P ≈ S > D` says semantic correctness may not be load-bearing and the current pairing story is probably wrong.
- `P ≈ D ≈ S` means correspondence is not load-bearing at resolvable scale in this regime; if uncertainty is wide, HOLD rather than claiming a null.

Do not scan task families after the fact and promote whichever subgroup produces the desired ordering.

---

# Resolution discipline

This project was authorized because, unlike L19, the discriminating quantity is plausibly measurable in a cheap deterministic-evaluation pilot. But we do **not** know the effect size in advance.

The IT–RT gaps in prior work are only a rough upper bound. The true same-marginal pairing surplus may be much smaller.

Use the following reasoning rather than a magic threshold:

- a stable effect around **3–4 percentage points or larger** on deterministic instruction-following evaluation is potentially worth taking into C2;
- a near-null is only scientifically informative if confidence intervals are tight enough to rule out a meaningful effect;
- if all arm differences are about ≤2 pp but intervals still allow a ~3–4 pp effect, the correct result is **HOLD — under-resolved**, not “pairing does not matter.”

Before scaling anything, inspect whether seed variance, data-order variance, or evaluation variance already makes the target effect unresolvable.

---

# What would make this a Main paper later

A positive E01 by itself is not enough.

“Shuffling responses drops IFEval by 6 points” is below the intended contribution bar because existing work already says pair alignment matters.

The promising growth path is a conditional law:

> **When is pairing actually needed?**

The strongest current candidate variable is the pretrained model's existing instruction→response association strength. FedDQC's IRA-like quantity gives an operational precedent, but the metric is not ours and should not be claimed as novelty.

The scientifically interesting test is whether the base model's existing `X→Y` association predicts the **causal value of preserving the pair during post-training**.

Two plausible accounts make opposite predictions:

- **Pretraining-completion:** stronger base association means less new value from pairing.
- **Alignment-quality / learnability:** stronger base association means the pair is a cleaner, more learnable signal and pairing is more valuable.

If E01 succeeds, a later C2 should turn this into an intervention—e.g. selectively preserving/breaking correspondence in pre-motivated high- versus low-association subsets while matching obvious difficulty variables—not merely a post-hoc correlation between likelihood and accuracy.

That C2 is **not authorized yet**. Return to selection first.

---

# Scope guards

Do not turn L30 into any of the following:

- a new instruction-data filtering method;
- a new alignment score;
- a mutual-information estimation paper;
- another RT or WIT replication;
- generic “SFT changes instruction following”;
- hidden-state instruction-direction work before the behavioral quantity exists;
- Temporal Forgetting / “the capability was still there”;
- a benchmark paper.

If the causal identity changes, stop and re-select rather than rescuing the project with a new story.

---

# Working style

You are not being asked to mechanically execute a fixed recipe. First understand the causal quantity and the prior work. Inspect the original RT/WIT code and data conventions, then implement the cleanest comparison that preserves the estimand. Keep code, configs, logs, and results inside `candidates/L30_PAIRING_SURPLUS/`; keep regenerable large artifacts out of git. Record deviations and failed validity checks rather than silently adjusting them.

The first deliverable is not “a successful experiment.” It is a trustworthy answer to whether correct instruction-response correspondence has a measurable marginal causal value beyond the two marginals, and what P/D/S pattern says about what instruction tuning is actually learning.

If E01 establishes a stable, resolvable correspondence-dependent quantity, stop before C2 and update the candidate for re-selection. If it does not, report the strongest justified kill/HOLD conclusion rather than searching for a favorable setting.
