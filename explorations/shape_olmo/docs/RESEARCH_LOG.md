# ShapeLab research log (running; newest at bottom)

## 2026-09-28 — state of understanding after P0 and the literature pass

1. The published token-level "hybrid signature" (Li & Merrill 2606.20936) comes from a 7B pair that differs
   in data mix, LR schedule, heads and long-context recipe, not only in the mixer. On our data the final
   Olmo-Hybrid is *worse* on 5/7 domains. The dominant axis is **novel vs reused target**: H better on novel
   (+0.018), worse on reuse, growing with n (−0.04 → −0.06). Content > function is mostly reuse
   composition.
2. "Attention wins on reused tokens" is Zoology's result (Arora et al., ICLR 2024: 82% of the gated-conv
   vs attention Pile gap is on AR hits). Not new.
3. A public **architecture-only triplet** exists: state-spaces Transformer++ / Mamba-2 / Mamba-2-Attention
   2.7B, same Pile data, 300B tokens, NeoX tokenizer, 2k context (Mamba-2 paper §9.2.3, Table 3). A second
   one at 8B / 3.5T: NVIDIA gpt3-8b-multi-3.5t-base / mamba2-8b-3t-4k / mamba2-hybrid-8b-3t-4k (Megatron
   format). The same Pile data also underlies Pythia (143 checkpoints, PolyPythias seeds), Mamba-1 and
   Mamba-2 size ladders: same-architecture **scale**, **training-progress** and **seed** controls.

## Hypothesis registered before any in-prefix-mass data (the reuse gate)

For every model, next-token loss splits exactly:
  nll = −log P(class) − log P(token | class),  class ∈ {IN: target type already in visible prefix, OUT}.
**H-gate:** the novel-vs-reuse architecture signature is mostly in the *gate*. Attention-rich models bet
more mass on in-prefix types (win on IN, lose on OUT); recurrent/hybrid models bet less.
Predictions if true:
  (a) On OUT targets, Δ_gate carries most of Δ (|Δ_gate| > |Δ_within|), with the same sign as Δ.
  (b) Mean P(IN | OUT target) is higher for the attention-rich model.
  (c) Same-architecture scale/progress changes move gate and within-class terms together; an
      architecture swap moves them in opposite directions.
**H-within (alternative):** the gap sits within class: which novel token (semantic / state, Li & Merrill)
and which in-context token (retrieval precision, Zoology). Then (a) fails.
Either outcome is informative. Noise floor for any profile claim: token-level differences between
PolyPythias seeds of the same size.

## Queue (blocked: all fvcrc cards held by other users' jobs; 11 / 21 unreachable)
- T7s1 / H7s1 (OLMo stage-1 end) with lpin/lpout → stage change-point + gate on the OLMo pair.
- Pile triplet 2.7B (T++ / Mamba-2 / Mamba-2-Attn) + Mamba-2 1.3B + Pythia-1.4B/2.8B (+ steps 36k, 71k)
  on 2k NeoX windows, with lpin/lpout.

## 2026-09-28 — Pile architecture-only triplet results (`results/pile_profiles_all.txt`, `results/pile_placebo_gate.txt`)

Models (same Pile data, NeoX tokenizer, 2k windows, 7 domains): PPT = Transformer++ 2.7B, PPH =
Mamba-2-Attention 2.7B (hybrid), PPR = Mamba-2 2.7B. Controls: Pythia 1.4B→2.8B (scale), Pythia-2.8B
step71000→final (training), Mamba-2 1.3B→2.7B (scale). (PY28_36k was invalid, see P0_LAUNCH; re-queued.)

**1. Three-way.** All-token gaps: T−H +0.027, R−H +0.038, T−R −0.012.
- Novel targets (rep 0): T−H +0.053, R−H +0.055, T−R −0.001. **T ≈ R on novel targets; H beats both
  by ≈ 0.05.**
- Reused targets: R worse than T (rep ≥ 2: −0.015; content|rep ≥ 1: −0.044), H ≈ slightly better than T.
- So H > max(T, R) holds, and it is concentrated on novel targets, where neither parent has an
  advantage over the other.

**2. The H−T token profile has the shape of a generic improvement.** Profile / all-token gap:

| | T→H (arch) | Pythia 1.4→2.8B | Pythia 71k→final | Mamba-2 1.3→2.7B |
|---|---|---|---|---|
| novel | 1.99 | 2.02 | 2.01 | 2.03 |
| rep 1 | 1.00 | 1.01 | 1.00 | 1.02 |
| rep ≥ 2 | 0.32 | 0.29 | 0.30 | 0.27 |
| rep ≥ 4 | 0.13 | 0.13 | 0.12 | 0.13 |
| content|rep0 | 2.16 | 2.38 | 2.30 | 2.33 |
| function|rep0 | 1.17 | 0.98 | 1.00 | 1.13 |

On an architecture-only comparison, "novel > repeat → 0, content > function" is what any lower-loss
model shows (scale, training progress, architecture). **It cannot be read as a recurrent / state
signature.** The OLMo stage-1 pair has the same shape (novel / all ≈ 2.1). The only architecture
contrast whose profile is *not* generic-shaped is **T vs R** (novel ≈ 0, reuse negative), i.e. the
known Zoology recall gap. Brackets are relatively larger in T→H (open 0.90, close 1.09 of all) than in
the controls (0.5–0.7); a small, unexplained deviation.

**3. Pre-registered reuse gate: H-gate rejected, H-within supported.** Novel targets, T→H: Δ = +0.053
= gate +0.0025 + within +0.051 (every domain: gate ≤ 0.005). IN targets: +0.016 = +0.004 + +0.013.
Gate calibration is nearly identical across models (mean P(IN) 0.711 vs 0.712, reliability near
diagonal). Pythia scale: novel +0.181 = gate +0.008 + within +0.173. The architecture gap is about
*which* token, not about betting on the prefix, and in that respect it again looks like scale.

**4. The token-level placebo regression is uninformative.** corr(d_HT, d_TT) = +0.02 at token level
(per-token noise dominates), so α ≈ 0.02 and the residual ≈ the raw gap. The informative placebo is
the profile-shape comparison (2). A seed noise floor (PolyPythias) is still to be computed at GPU
scale; the CPU pilots cover only 60 windows.

**What this changes.** Per-token *type* profiles do not discriminate architectures: they measure
"how much better", not "better at what". What survives and is architecture-specific:
(i) the T vs R recall gap (old, Zoology);
(ii) the aggregate super-additivity H > max(T, R) on novel targets (≈ +0.05 with T ≈ R);
(iii) on OLMo, a reuse / closure / code degradation produced during the hybrid's DroPE long-context
stage (P0_RESULTS, stage ladder).
None is named or registered. The next question has to use a tool other than token-type profiles,
e.g. counterfactual context interventions on the same targets.

## 2026-09-28 — lead candidate (not registered): does recurrence deliver order information to position-free attention?

**Pressure.** "Position lives in the recurrence; attention can be position-free" is a live design
principle. Jamba: no RoPE ("Mamba layers provide implicit position"). Kimi Linear: NoPE MLA,
"delegating all positional information and recency bias to the KDA layers". Olmo Hybrid: DroPE,
justified by "GDN layers carry implicit positional information". Evidence cited for it: aggregate
parity / long-context benchmarks. In pure transformers, RNoPE (2501.18795) shows NoPE attention does
content retrieval while RoPE supplies recency / position-aware selection. Whether recurrence
supplies that second role to attention in a hybrid appears untested (search 2026-09-28: Jamba, Kimi
Linear, DroPE, RNoPE, 2606.21249 retrieval heads, HOLA / HAM; none does it).

**Observation so far (OLMo ladder, natural text).** Over the hybrid's DroPE stage, copy damage is
within-class (gate unchanged) and scales with the number of competing candidate continuations;
absent at stage-1 end; T (YaRN) improves on the same tokens.

**Controlled test (running, `src/probe_order.py` v2).** `reassign`: `x` assigned n times with filler
lines, query `assert x == '`, correct = last value, so order is needed. `keyed`: distinct variable
per value, query one by name, so content suffices. 8 checkpoints: T / H × {S2 (RoPE), S3e, S3m, F}.
v1 (random tokens, most-recent as correct) was dropped: even RoPE T sits at chance, nothing demands
recency.

**Kill criterion (fixed before v2 data).** If H-F (DroPE) ≈ H-S2 (RoPE) on `reassign` relative to
`keyed` (difference in P(correct) within ±0.05 at n = 4, 8), recurrence delivers the needed order
information and this candidate dies.
**If it survives:** the decisive causal cell is a matched RoPE vs DroPE recalibration of a hybrid AND
a transformer (Pile 2.7B Mamba-2-Attn and Transformer++, ~1B tokens each), plus cross-model
replication on Kimi-Linear-48B-A3B (NoPE by design).

## 2026-09-28 — order probe v2 result (`results/probe_order_v2_summary.txt`): kill criterion NOT met, candidate survives

`keyed` (content-based selection): 0.87–0.98 everywhere (T and H, all stages, incl. H final).
`reassign` (order-based: last assignment wins); candidate-normalised P(last), chance 1/n:

| | n=4 | n=8 | P(first) at n=4 |
|---|---|---|---|
| T (RoPE S2, YaRN S3e/S3m/F) | 0.18–0.41 | 0.13–0.29 | 0.15–0.20 |
| H S2 (RoPE) | 0.31–0.51 (acc ≤ 0.86) | 0.29–0.43 | 0.24 |
| H S3e / S3m (DroPE) | 0.24–0.53 | 0.18–0.40 | 0.16–0.19 |
| H F (DroPE, released) | 0.13–0.26 | 0.10–0.21 | **0.50** (n=2: 0.75) |

1. With RoPE, the hybrid tracks the latest value better than the transformer (GDN's delta rule is
   key-based overwrite).
2. The released DroPE hybrid loses that and **reverses to primacy**: most candidate mass goes on the
   *first* assignment.
3. The reversal appears late (S3m → F), matching the accelerating natural-text degradation, while
   content-based selection stays intact.
Kill criterion (H-F ≈ H-S2 on reassign relative to keyed, ±0.05 at n = 4, 8): exceeded by ~0.25.

**Working hypothesis (to test, not a claim):** recurrence carries the latest-value state; the
position-free attention layers of the final hybrid impose a primacy bias and override it at
readout. Next, a channel dissociation on the same items: (a) hide the assignment region from the
full-attention layers (recurrent-only readout); (b) the reverse. If (a) recovers "last" and (b)
shows primacy, then in this hybrid the combination is *worse* than its recurrent channel alone on
order-dependent state.

## GOAL (restated 2026-09-28 at the user's request; everything below is checked against it)

Find one research question that is **deep, interesting and novel**, grounded jointly in
(a) Alex Zhang's *Shape* agenda: a model's I/O / computation contract should fit the harness; hybrid
    components have different properties that could act as different computational media, but
    vertical hybrids fail to exploit them; composition matters; and
(b) what this project has measured: CT05 (recurrence ≠ substitute for exact KV), CT09 (a partial,
    retrieval-triggered trace from attention into recurrence), ShapeLab (token-type signatures =
    generic improvement; H > max(T, R) on novel targets; DroPE-stage copy-precision loss; RoPE
    hybrid tracks the latest assignment better than T; DroPE final reverses to primacy).

**Bar (all five before anything is registered):**
1. rests on a phenomenon we have measured and verified ourselves (not a hoped-for mechanism);
2. is about how component roles **combine**, not about recipe tuning;
3. nearest priors checked and not owning it;
4. a causal manipulation exists at our scale (inference interventions first; small matched
   training only if the question is itself about training);
5. survives kill criteria written before the data.
Each experiment must remove an explanation, not add a story. Wrong priors are recorded as wrong.

## 2026-09-28 — channel dissociation, RoPE hybrid (H7s2); "binding in recurrence" reading REFUTED

`probe_channel.py`: at the query tokens, full-attention layers are masked from the context
[4, query_start); GDN still sees everything. `full` reproduces probe_order exactly (median |Δlp| 0.000).

| H7s2 | keyed P(correct) | reassign P(correct) = P(last) | keyed P(last) when queried ≠ last |
|---|---|---|---|
| full, n = 4 / 8 | 0.96 / 0.95 | 0.44 / 0.35 | 0.02 / 0.01 |
| rec-only, n = 4 / 8 | 0.28 / 0.13 (chance) | 0.36 / 0.29 | **0.36 / 0.23** |

- Content-keyed selection needs attention (rec-only → chance), as in 2609.04434.
- The rec-only "last value" signal is **unbound recency**: the same extra mass goes on the most recent
  candidate value whether or not it belongs to the queried variable. My first reading (recurrence
  carries the current value of `x`, a binding) was wrong; recorded as wrong. This agrees with
  2609.04434 ("binding is lost").
- Revised picture: recurrence supplies a recency cue; attention supplies key-bound selection;
  latest-assignment needs both (full > rec-only on reassign).
- Pending decisive cell: the DroPE final (primacy in full). Does its rec-only readout still carry
  recency, i.e. is attention overriding the cue at readout? And H7s3m (DroPE, before the reversal).
