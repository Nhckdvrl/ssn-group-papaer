# Reading notes — Alex Zhang's "shape" agenda (read 2026-09-28, first-hand)

Sources read in full: *Language Model "Shape"* (2026-09-26), *Language model harnesses are
compositional generalizers* (Zhang & Khattab, 2026-07), Jev launch post (TypeSafe, 2026-09-15).
Skimmed: MGH, scaffold, spec-PTC, LongCoT-RLM posts. Raw text: scratchpad, not committed.

## What the shape post actually claims (vs. what we assumed in CT05)

1. **Definition.** Shape = the model's input/output contract. The ask is to *change the model to fit
   the harness*, betting that "the amortized cost of fitting the language model shape may end up
   being lower". This is a cost/trade-off argument, not a claim that a shape is more intelligent
   ("Jev is not meaningfully more intelligent than any frontier model").
2. **Hybrids are criticised, not celebrated.** He is "pretty disappointed" that SSMs ended up in
   hybrids that keep the decoder-only shape, and finds it notable that hybrids interleave
   *vertically* rather than on *parallel residual streams*. The point: component properties "can
   potentially be utilized more in the harness". A vertical hybrid is his example of *not* using
   them.
3. **Agent example.** It is framed as a hot take and hedged ("Not saying this is provably correct").
   The proposal is recurrence and attention acting on *history* and *current observation*
   **separately**. Two premises:
   - importance decays with time in structured ways (observations, tool calls, actions), and that
     structure can be "baked into the shape";
   - "language agents don't need to perfectly retrieve facts from their history … **a coarse view
     of some information is enough for the agent … to retrieve the actual information back into
     its working context**."
4. **New shapes need new objectives** (Jev's RLCD), and distillation from decoder-only models into
   new shapes is now cheap.
5. The only "intelligence" argument: shapes that "enable meaningful composition" may raise gained
   intelligence per data. This links to the harness post, where composition means *locally
   in-distribution* LM calls, obtained by abstracting the task so that similar tasks look alike to
   the root.

## Where our CT05 lineage misread this

- CT05 tested whether recurrence can **substitute** for exact KV on a *fixed* trajectory. The blog
  never claims that. Its premise is that a coarse view is enough **because the agent can re-fetch**.
  CT05's ρ ≈ 0 is compatible with the blog: recurrence doesn't carry exact values, and the blog says
  it needn't. Nobody tested the premise that was actually stated: does the coarse channel carry
  enough to know *what / where* to re-fetch?
  (This is an observation, not a proposed topic. Priors to check first: ReadAgent-style gist
  memory, MemGPT paging, agent re-reading behaviour.)
- CT08 took the harness post's *mechanism* (information hiding) as the object. The post itself
  locates the effect in trajectory **isomorphism** (locally in-distribution calls), and says the
  root's printing of payload is often undesirable but still happens.
- Throughout, we treated a "vertical hybrid" (Qwen3.5) as the embodiment of the shape idea. The
  blog treats it as the status quo that fails to exploit component properties.

## What this suggests about the object of study (tentative)

The blog's shape axis has three separable parts: **output contract** (Jev: typed decision,
prefill-only), **stream topology** (vertical vs parallel/separate streams over different parts of
the input), and **objective**. The OLMo T/H matched pair speaks only to *layer mixer inside a fixed
decoder-only contract*, which is the part the blog finds least interesting. It is still the
cleanest causal microscope available. But anything found there must eventually say something about
contract or topology, or it is ordinary architecture analysis and not "shape".

Open questions to settle by reading before running anything:
- Q1 What is known about **parallel vs vertical** hybrids (Hymba, Falcon-H1, Multi-Stream, …), and
  about models whose streams see *different parts of the input*?
- Q2 Is "coarse view → re-fetch" (pointer vs content memory) already characterised for recurrent
  or compressed memories?
- Q3 What follow-ups exist to Li & Merrill's token-level T/H comparison? Is the non-uniform gap
  already explained?
- Q4 Jev-like output contracts in open models (AnyJev, Kev, L2): what is measured, what is open?

## Literature pass (2026-09-28) — what each cited source actually supports

| source | status after reading | what it supports / doesn't |
|---|---|---|
| Li & Merrill 2606.20936 (token-level T vs H) | read §1–6, App. A–G | Solid observational decomposition of the **7B** pair. Numbers to reproduce: content 0.0384 vs function 0.0238; open−close gaps per domain (PG-19 0.068 … HTML 0.010); repeated-n gap → 0. The authors' own future work: "discourse state tracking" benchmarks and filtered pretraining evals. **Their 1B T/H/R checkpoints are not publicly locatable.** |
| Rawat et al. 2604.21454 (Reasoning Primitives) | read | Weak architecture evidence: one pair, synthetic, free-form generation with parse-rate / budget failures ("doom loops"). The Think comparison is **not post-training matched**: `Olmo-3-7B-Think` (full pipeline) vs `Olmo-Hybrid-Think-SFT-7B` (SFT only), yet `Olmo-3-7B-Think-SFT` exists. The hybrid "win" on Collisions coincides with the Transformer running out of budget. Instruct variants sit near chance (floor). |
| "Task Structure Reverses Layerwise State Encoding" (2606.00926 **v1**) | v2 read | **Retitled in v2** to *Refit the Probe: Single-Direction Ablation Is Not a Necessity Test*. The author found the single-direction ablation leaves the variable decodable, and the corrected INLP test reverses the necessity conclusion. The "mechanism = f(architecture × task)" evidence we were leaning on is from v1 and is **not the author's current claim**. Do not cite v1. |
| State over Tokens 2512.12777 | abstract | Conceptual framing only (tokens = externalized state). |
| Attention Amnesia 2606.11052 | abstract + §1–3 | CoT-SFT degrades long-range NIAH in **distilled** hybrids (HypeNet, Jet-Nemotron) through Q/K drift; QK-Restore. So post-training changes hybrid recall, which is another reason Think/Instruct comparisons need matched post-training. |
| Where Should LoRA Go? 2604.22127 | abstract | Sequential (Qwen3.5) vs parallel (Falcon-H1) topologies respond oppositely to recurrent-backbone adaptation. Unmatched models: topology is confounded with everything else. |
| Stream stability vs recall 2609.07282; MARCH 2608.12435; HOLA 2607.02303 | abstracts | Architecture / eval-contract proposals for compressed + exact memory. None tests whether a *pretrained* compressed channel carries **addressing** information ("where to re-fetch"). |
| Compaction line (CliffCompaction, Addressable Recall Compaction, Cue-Anchored WM, …) | titles/abstracts | The harness-level "coarse view + re-fetch" is crowded. |
| Jev ecosystem (AnyJev, Kev, "35 open alternatives") | READMEs/blogs | Engineering race, not science. Structural point: a prefill-only decision contract **forbids externalizing state into tokens**. |

### Constraints this puts on the plan
1. **No public matched Pure-RNN arm** at any scale → `H > max(T, R)` cannot be tested on public
   checkpoints. Asking the authors is the only route.
2. **No matched parallel-vs-vertical pair** → the blog's topology point can't be tested causally on
   public checkpoints. It would need our own small-scale pretraining.
3. The 7B T/H pair **is** matched, including the SFT stage (`*-Think-SFT` exists for both; data
   matching still to be checked). Stage-1 intermediate checkpoints every 1000 steps exist for both.
4. Tooling trap: transformers 5.x mis-applies YaRN to Olmo-3's sliding layers (upstream #45945 /
   #48392); score Olmo-3 with 4.57.6.

### A connection noticed, not acted on
Reasoning Primitives' only robust finding is that **token-externalized state** dominates
architecture differences. A Jev-style prefill-only contract removes exactly that channel. So
*output contract* and *layer mixer* could interact: architecture might matter more when the
contract forbids externalization. This is one hypothesis among several, not a plan. Nothing will
be built on it before P0 calibrates the pair.

## Correction to the premise "the 7B pair is matched" (2026-09-28)

Merrill et al. 2604.03444 App. A.1 list what differs between Olmo Hybrid 7B and Olmo 3 7B besides the
mixer:
- stage-1 **data mix**: Hybrid uses "the improved data mix from Olmo 3 **32B**", not the Olmo 3 7B mix;
- **LR schedule**: cosine to 10% vs Olmo 3 7B's piecewise schedule ("match closely for the majority of
  training");
- 30 vs 32 heads (to match parameters and throughput);
- later stages: souped midtraining ingredients, **DroPE** (no RoPE) long-context vs **YaRN**.
Tokens per step are identical (4.19M), and stage-1 branches exist every 1000 steps for both.

Li & Merrill call the pair "closely matched in tokenizer, data mixture, and training recipe"; that is
too strong. The only pair described as differing *only* in architecture is the 1B ladder of
2604.03444 §4.1, and it is not public. So any token-level H−T profile on the 7B pair =
architecture + data mix + schedule + later-stage recipe.

## An alternative explanation the token paper does not test

Content > function, open > close, and copy → 0 could be the profile of **any lower-loss model**, not
of recurrence. Prop. 1 (gap ≤ log|V_τ|) already implies that open classes have more room for *any*
improvement. Training-dynamics work reportedly finds function words and repeats learned early and
content learned late (Xia et al. 2023; Chang et al. 2023 — to verify). The regression controls
per-token difficulty, not "the shape of a generic improvement".

Cheap control (inference-only, public checkpoints): compare the H−T gap profile with a
**same-architecture improvement of matched aggregate size**, T(step s') − T(step s). If the profiles
coincide, the token-level "hybrid signature" is not architecture-specific. That would matter for
everything downstream in ShapeLab. The data-mix confound remains either way; only the private 1B
ladder removes it.

## "T" is not a pure Transformer (2026-09-28)

Olmo 3 7B = 3:1 **sliding-window (4096) / full** attention. Olmo Hybrid replaces exactly those SWA
layers (75%) with GDN (2604.03444 l.133, 188). Li & Merrill never mention the sliding window and
frame T as "attention can retrieve from the visible prefix". The contrast is **SWA-4096 vs GDN in 24
of 32 layers**, with the same 8 full-attention layers in both (plus the recipe differences above).

Direct consequence, testable from P0 scores without new runs: in 8192-token windows, T's SWA
layers lose everything more than 4096 tokens back, while GDN keeps a lossy summary. If Δ(position)
rises past ~4096, part of the natural-text "hybrid advantage" is T's local-window truncation (a
long-range access effect), not better state tracking within reach. If Δ is flat in position, that
reading is ruled out.

Also from 2510.24963 (Michaelov, Levy, Bergen): across Transformer / Mamba / RWKV, up to 98% of
word-level behaviour variance is explained by frequency, n-gram probability and context
similarity, with consistent learning phases. Architecture-specific token effects should therefore be
a residual on a shared trajectory, so the matched-improvement placebo is the first control to run.

## Prior evidence from the Olmo Hybrid paper itself (Tables 2–3), noted before stage-1 scores exist

- End of **pretraining** (before midtrain / long context): the hybrid is already lower on Code
  (17.1 vs 19.6), LBPP (2.9 vs 6.3) and GenQA (66.8 vs 68.5), and higher on Math / MC / BBH /
  MMLU-Pro. After midtraining it is ahead on every domain aggregate.
- **RULER at 4k** (short context, retrieval-heavy): hybrid 92.8 with YaRN and 92.2 with DroPE, vs
  Olmo 3 95.8. The hybrid wins only from 8k/16k upward (DroPE 85.0 vs 70.9 at 64k). Its short-range
  retrieval weakness appears under **both** positional treatments.
- Written-down expectation before looking at stage-1: the token-level reuse deficit will largely
  **persist** at stage-1 end (it is not mainly DroPE). If it vanishes, that contradicts this prior
  and is the more surprising outcome.
