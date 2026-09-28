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

## 2026-09-28 — channel dissociation across the DroPE stage (`results/probe_channel_summary.txt`)

| reassign, n = 4 | full P(last) | full P(first) | rec-only P(last) | rec-only P(first) |
|---|---|---|---|---|
| H7s2 (RoPE) | 0.44 | 0.24 | 0.36 | 0.25 |
| H7s3m (DroPE, mid) | 0.40 | 0.16 | 0.35 | 0.27 |
| H7 (DroPE, final) | 0.19 | **0.50** | 0.28 | 0.31 |

Unbound order cue in the recurrent channel (keyed items, queried neither first nor last; rec-only,
n = 4, P(last) / P(first)): H7s2 0.37 / 0.24 → H7s3m 0.29 / 0.30 → H7 0.25 / 0.32.
Content keying (keyed, full) stays 0.90–0.96 throughout; rec-only keyed stays at chance.

- **Composition reverses.** RoPE hybrid: full > rec-only on order (attention helps). DroPE final:
  full < rec-only (P(last) 0.19 vs 0.28; P(first) 0.50 vs 0.31); the attention channel pushes toward
  the stale first value.
- **The recurrent order cue itself erodes** over the DroPE stage (recency → flat → slight primacy).
  The full model keeps recency until mid-stage, then flips.
- **Robust summary (no channel apportioning):** over DroPE training the order signal available at
  readout degrades and flips to primacy, while content keying is untouched. Channel attribution is
  mixed; I will not add conditions to make it tidy.

**Generality is the next gate.** Is this a property of *position-free hybrids* (NoPE-by-design:
Granite-4.0-H, Nemotron-H, Kimi Linear), or of *DroPE retrofits*? Survey queued (NoPE vs RoPE public
hybrids; S5 SWA-128 RoPE/NoPE matched pair).
- Survey kill / narrowing rule (fixed now): if NoPE-by-design hybrids show recency on `reassign` at
  least as well as RoPE hybrids (P(last) − P(first) at n = 4 within 0.05), the phenomenon is
  DroPE-retrofit-specific. The broad "position-free hybrids read stale state" framing is then
  dead, and what remains is a narrower DroPE finding.

## 2026-09-28 — attention at the query over duplicate keys (`results/probe_attn_summary.txt`)

Last-row attention recomputed from hooked q/k (validated vs eager, max |Δ| 6e-7). Share of attention
over the n `x = '<v>'` value tokens on last / first occurrence, n = 4 (chance 0.25):
- T (RoPE S2; YaRN F): every full layer leans last (head-mean ~0.31–0.38 last vs ~0.18–0.24 first).
- H S2 (RoPE): every layer leans last; main retrieval layer L19 0.37 / 0.21; L23 best head 0.49 / 0.19.
- H S3m (DroPE mid): early layers L7 / L11 already lean first (0.20 / 0.34, 0.22 / 0.31); late layers
  still lean last (L19 best head 0.48 / 0.13).
- H F (DroPE final): all layers lean first; L19 (highest value mass, 0.205) 0.22 / 0.33, best head
  0.15 / 0.58; L23 best head 0.19 / 0.44.

**Mechanism, directly observed:** RoPE gives attention a recency preference among matching keys.
Across the DroPE stage, attention's own selection among duplicate keys flips from recency to
primacy (early layers first, then the retrieval layers), and the final model's stale-first answers
are produced by attention at the query. The recurrence does not supply the missing recency. Content
keying is unaffected. This is consistent with the natural-text result (copy precision loss scales
with the number of competing continuations).
Open: is this a DroPE-retrofit property or a property of position-free hybrids generally? (Survey:
Granite-4.0-H / Nemotron-H NoPE by design, vs Falcon-H1 / Bamba / Qwen3.5 RoPE; S5 matched pair.)

## 2026-09-28 — S5 matched NoPE / RoPE pair (Qiao et al. release; `results/probe_order_s5_summary.txt`)

0.6B, 100B tokens from scratch, SWA-128 alternating with full attention; the only difference is NoPE
on the full-attention layers (`no_rope_for_fa_layers`). reassign P(last) − P(first):

| | n=2 | n=4 | n=8 |
|---|---|---|---|
| S5 full attention (RoPE transformer) | +0.08 | +0.23 | +0.24 |
| S5 hybrid, RoPE FA | −0.06 | +0.07 | +0.07 |
| S5 hybrid, NoPE FA | −0.18 | −0.07 | −0.04 |

- **NoPE trained from scratch also shifts toward primacy:** −0.14 (n = 4) and −0.11 (n = 8) relative
  to its RoPE twin, beyond the 0.05 rule, with a sign flip. So the effect is **not only a DroPE-retrofit
  artefact**.
- Caveats: small model; the efficient module is SWA-128, not recurrence; NoPE also costs some content
  keying here (keyed n = 4, gap 32: 0.68 vs 0.91). Supporting evidence, not the decisive recurrent
  case. Pending: NoPE-by-design recurrent hybrids (Granite-4.0-H, Nemotron-H) vs RoPE hybrids
  (Falcon-H1, Bamba, Qwen3.5).

## 2026-09-28 — public-hybrid survey (`results/probe_order_survey_summary.txt`): BROAD FRAMING KILLED by the pre-written rule

Gaps 4, 32 (torch-fallback Mamba OOMs at 7k tokens); PROBE_N = 60. reassign P(last) − P(first), and
the keyed content control:

| model | pos. enc. | n=4 | n=8 | keyed n=4 |
|---|---|---|---|---|
| Granite-4.0-H-micro | NoPE from scratch | +0.03 | +0.01 | 0.94–0.96 |
| Granite-4.0-H-tiny | NoPE from scratch | +0.22 | +0.27 | 0.73–0.97 |
| Nemotron-H-8B-Base | NoPE from scratch | 0.00 | +0.22 | 0.29–0.56 (weak control) |
| Falcon-H1-1.5B | RoPE | +0.10 | +0.05 | 0.93–0.94 |
| Qwen3.5-4B | RoPE | +0.09 | +0.04 | 0.99–1.00 |
| Bamba-9B-v2 | RoPE | +0.38 | +0.02 | 0.25–0.29 (fails control; excluded) |
| Olmo-Hybrid final | NoPE via DroPE retrofit | −0.37 | −0.18 | 0.94–0.95 |
| S5 NoPE (SWA-128 hybrid) | NoPE from scratch | −0.11 | −0.01 | 0.68–0.91 |

**Rule (fixed before data):** if NoPE-by-design hybrids show recency within 0.05 of RoPE hybrids at
n = 4, the broad "position-free hybrids read stale state" framing dies. NoPE-from-scratch recurrent
hybrids +0.08 (mean) vs valid RoPE hybrids +0.095: Δ ≈ 0.015. **Killed.**
Recurrent hybrids trained NoPE from scratch do get recency to their position-free attention (Granite-tiny
is among the best), so the Kimi-Linear / Jamba / Granite design premise holds for native training on
this probe.

**What remains (narrower, not yet worth registering):** primacy appears in the DroPE retrofit
(strong) and in the small SWA-128 NoPE hybrid (moderate). It is not a property of position-free
recurrent hybrids as such. A candidate reading: attention that learned order from RoPE and then loses
it does not learn to read the recurrent recency cue, and drifts to primacy. That is a claim about
DroPE retrofits. Next check before deciding anything: do DroPE-retrofit **transformers** (public
DroPE checkpoints, if any) show the same primacy? If yes, it is a DroPE property, not a hybrid
interaction.
Stop-loss note: every surviving version so far adds a condition ("only retrofit", "only SWA"). That
counts against the line.

## 2026-09-28 — next candidate (pre-registered before any data): what does each architecture use from far context?

Motivation. The only architecture-specific result that survived all controls is H > max(T, R) on
novel targets (Pile triplet, T ≈ R). Token-type profiles cannot say why. Alex's agent premise is
exactly a claim about old history: "densely look at recent, a coarse view of older history is
enough". Khandelwal et al. 2018 (LSTMs: word order used only within ~50 tokens, far context as a bag
of words) has, as far as searched, not been redone at loss level for SSMs / hybrids (2510.06640 is
representation flow only; 2510.26912 is memory-recall design).

Design (`src/ctx_ablation.py`): NeoX 2k windows, targets = last 128 positions (novel vs reused);
context older than d ∈ {32, 128, 512, 1024} is dropped / chunk-shuffled (32-token chunks) /
token-shuffled. Models: PPT, PPH, PPR (architecture-only), plus Pythia 1.4B → 2.8B and Mamba-2
1.3B → 2.7B (same-architecture scale controls).
Readouts: far-use = NLL(drop) − NLL(full); order-use = NLL(cshuf) − NLL(full); bag-use =
NLL(drop) − NLL(tshuf).

Kill rule. Let G = aggregate novel-target gap (T − H). If the hybrid's extra far-use over T (and over
R) divided by G lies within the range of the same ratio for the two scale controls (extra far-use of
the larger model / its aggregate novel gap), the hybrid's super-additivity is "a better model using
more context" again, and the line dies. It survives only if the hybrid's gain is **disproportionately
far-context** (or disproportionately order vs bag) relative to scale.

## 2026-09-28 — far-context ablation (`results/ctx_summary.txt`): KILLED by the pre-written rule

Novel targets, far-use = NLL(drop_d) − NLL(full):

| | d=32 | d=128 | d=512 | d=1024 |
|---|---|---|---|---|
| T++ | +0.173 | +0.080 | +0.022 | +0.006 |
| Mamba-2-Attn (H) | +0.168 | +0.078 | +0.020 | +0.004 |
| Mamba-2 (R) | +0.135 | +0.051 | +0.009 | +0.001 |

Kill ratios (extra far-use of the better model / its novel-target gap):

| pair | d=32 | d=128 | d=512 |
|---|---|---|---|
| T → H (arch) | −0.08 | −0.03 | −0.03 |
| R → H (arch) | +0.40 | +0.34 | +0.14 |
| Pythia 1.4 → 2.8B (scale) | +0.09 | +0.05 | +0.03 |
| Mamba-2 1.3 → 2.7B (scale) | +0.14 | +0.05 | 0.00 |

- The hybrid does **not** use far context more than the transformer (extra ≈ 0). Its novel-target advantage
  over T (+0.063 here) is present with only the last 32 tokens intact, i.e. it is local, not
  long-range. This refutes, for this architecture-only triplet, the "discourse state tracking over
  long range" explanation (Li & Merrill's hypothesis). By the rule, the super-additivity is not
  disproportionately far-context → **line killed**.
- H uses far context more than R (ratio 0.40): the known attention-recall advantage (Zoology). Not new.
- Side observation: token-shuffled far context is *worse* than dropped far context for every model
  ("bag" < 0 everywhere), so shuffled history acts as harmful noise and the bag-of-words readout is
  not identifiable in this design. The effect is similar across architectures; not a lead.

**Status after the day:** three candidate lines tested with pre-written kill rules (reuse-gate,
position-free-hybrid primacy [broad], far-context super-additivity). All three killed. Survivor:
DroPE-retrofit primacy (narrow; awaiting the Llama-2 RoPE vs DroPE control).
