# Current Research State — 2026-09-13

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Phase:** **open mechanism-first search — no approved mainline, no active pilot** (L30 archived 2026-09-13; L29 killed)  
**Killed ledger:** authoritative file currently contains through **K184**. Compact kills **K185–K189** are recorded in `search_rounds/2026-09-12_CONTINUED_SEARCH_VII.md` and are pending ledger maintenance; **K190 is reserved for L29** and its complete postmortem is `candidates/L29_COT_CONTROL_GAIN/notes/POSTMORTEM.md`. Do not reuse K185–K190.

## Current search preference

The open-ended search target remains:

> **stable model phenomenon → unresolved why → competing computational accounts → decisive causal/discriminating operation**

or:

> **training/model-regime change → old empirical law no longer sufficient → new conditional computational explanation**

Highest-priority tracks:

- stable repeated anomaly → mechanism;
- training / post-training transitions: learn vs select vs suppress vs reroute vs read out;
- reasoning / inference-time computation with a concrete new scientific object;
- representation → causal use, never probe-only;
- old empirical law rewritten by a modern model/training regime;
- SAME-QUANTITY contradictions with a hidden condition;
- community mechanistic beliefs whose causal evidence is materially weaker than assumed.

Strongly deprioritize RAG/retrieval/search, benchmark/evaluator/metric work, annotation/data-first topics, scientific-evidence infrastructure, generic Agent/memory/RL/judge/harness questions, new speech/audio topics, pure competence tests, and generic calibration/hallucination/safety surveys unless an exceptional model-science question clearly transcends the framing.

Before deep search ask:

> **If the dataset, benchmark, metric, system label, or method name disappeared, would we still urgently want to know the answer?**

and:

> **Is the paper fun because it explains why the model works this way, or because an evaluation/data pipeline is imperfect?**

No survivor quota. Zero survivors is valid.

---

# Active portfolio after 2026-09-13 update

## L30 — What Does Pairing Teach?

**Status:** `NO-GO / ARCHIVED (2026-09-13)`

Package: `candidates/L30_PAIRING_SURPLUS/` (see `notes/ARCHIVE.md`)

E01 ran as pre-registered — 12 matched runs, 4 arms x 3 seeds, Gemma-2-2B +
Alpaca-Cleaned, IFEval with the official verifier, prompt-clustered intervals —
and returned a trustworthy answer. The route stops for three independent reasons:

1. **Resolution.** `Delta_pair = P - D_mask = +1.85 pp [-1.79, +5.42]`, and the
   width is evaluation-limited (~6 of 7.6 pp from the 541-prompt sample, ~1.6 pp
   from seeds). The untuned baseline explains why there is no headroom: 52k
   Alpaca pairs buy **+1.1 pp instruction-level** over no training at all.
2. **Instrument validity.** Aggregate IFEval at 2B mixes instruction following
   with termination. The base model scores 32.85% instruction-level while never
   stopping (median 4018 chars), takes **0.0%** on `language` and `startend` —
   the families that require obeying and stopping — and *beats* the tuned model
   on `punctuation` (50.0 vs 21.2), which verbose text satisfies incidentally.
3. **Novelty.** The surviving phenomenon (wrong correspondence collapses the
   policy, absent correspondence does not) is derivable a priori from the
   training objective; the budget-matched control makes it clean, not surprising.
   Its two candidate conditional laws are both occupied (MAIN/FedDQC intuition;
   data-poisoning threshold effects). `INSUFFICIENT CONTRIBUTION`.

**Reusable, validated:** matched P/S/D_mask/D_rt trainer with a zero-leakage
custom attention mask and its construct-validity suite, greedy IFEval with the
vendored Google Research verifier, prompt-clustered seed-resampled bootstrap,
multi-node evaluation scripts, the frozen 51,758-pair pool, and 31 evaluation
runs.

**Durable lessons:**
- "RT" is not a well-defined correspondence-free control — Hewitt et al. empty
  the instruction string but keep the `<|user|>` scaffolding while An et al. drop
  the user turn; against a budget-matched control the two differ by +1.91 pp
  [-1.66, +5.42]. Serialisation sits inside any quoted IT−RT gap.
- IFEval aggregate scores for non-terminating base models are not comparable to
  those of tuned models. Check per-constraint-family accuracy before using the
  aggregate as a mother phenomenon.
- Prior "input-output mapping matters little" results (Min et al.; Kung & Peng)
  all corrupt **demonstrations**, never the supervised pair. The gap is real but
  is not worth a Main paper on its own.

Do not reopen without the evidence named in `ARCHIVE.md` §6.

## L17 — What Does a Speech LLM Learn About a Speaker?

**Status:** `PILOT-AUTHORIZED — E01 only; EXISTING PROJECT, OUTSIDE CURRENT NEW-SEARCH PREFERENCE`

Package: `candidates/L17_SPEAKER_ADAPTATION_UNIT/`

Mother phenomenon: same-speaker in-context examples improve speech recognition. The live question separates global speaker adaptation from sublexical acoustic-phonetic adaptation and lexical/textual explanation with matched-speaker / matched-transcript controls.

**Why it stays:** unlike the newly killed legacy topics, it begins from an established mother effect and already has competing computational accounts plus a discriminating operation. It remains an existing project only. **Do not use this as permission to create new speech/audio topics.**

# Removed from active portfolio in the 2026-09-12 / 2026-09-13 re-screen

## L29 — Losing the Steering Gain

**Status:** `KILL — K190 — FINAL E01R INSTRUMENT GATE FAILED (2026-09-13)`

The original E01 showed that common-support and checkpoint-natural pipelines were
feasible, but exact-word suppression was invalid: its apparent −6.25 pp training change
came from rule retrieval in the neutral arm. Target-matched, structural, and target-free
controls then showed that the supposed local-gain contrast was dominated by intervention
wording / lexical effects rather than a valid positive early controller effect.

The one authorized reconstruction removed all earlier constraints and used fresh
balanced-binary case and tag codebooks at natural reasoning boundaries. On 48 unseen
step-100 instrument-development questions, all 48 natural forks survived, yet case
directional gain was **0.00 pp** and tag gain was only **+1.30 pp** (95% CI
`[+0.26,+2.60]`), entirely amber-driven. Both missed the frozen +15 pp primary gate and
semantic/template/mapping robustness requirements. No step-1400/2800 or untouched
240-question confirmation outcome was run.

This is **identification failure, not a stable-gain/null result**: L29 never obtained a
material positive early local-control effect whose training change could identify
controller weakening. Under the locked rule the paper is killed with no further wording
search, stronger prompting rescue, hidden-state mechanism work, activation steering,
model-zoo expansion, or checkpoint sweep.

**Anti-resurrection:** do not reopen as `L29b — initialization vs online control`,
commitment-conditioned redirectability, “why was the local gain near zero?”, or a prompt-
elicitation study. ReasonIF, MathIF, ICML 2026 interruptibility work, commitment-boundary
work, Thinking Traps, and trajectory-steering work already crowd that natural fallback;
more importantly, stronger prompt optimization would change the selected paper identity
from training mechanism to evaluator/elicitation optimization.

Full execution record:

- `candidates/L29_COT_CONTROL_GAIN/notes/E01_PILOT_REPORT.md`
- `candidates/L29_COT_CONTROL_GAIN/notes/E01R_REPORT.md`
- `candidates/L29_COT_CONTROL_GAIN/notes/POSTMORTEM.md`

**Durable process lesson:** before comparing a causal quantity across training stages,
first prove on an independent development split that the intervention has substantial,
interpretable causal leverage at the reference checkpoint. A difference between two
near-zero first stages is not a training-mechanism result.

## L16 — Same World, Different Partitions

**Status:** `KILL / ANTI-RESURRECTION — duplicate of K006`

The repository already killed **K006 Partition Dependence** because the parent was occupied by statistical partition/self-consistency plus framing/choice-set work. L16 reintroduced the same scientific parent with a sharper `1/M` ignorance-prior prediction. More importantly under the current search doctrine, the exact LLM effect is not an established mother phenomenon: the paper identity still depends on first discovering the desired partition shift. A sharper equation and cleaner pilot do not reopen K006.

## L21 — When Is Contextual Entrainment Rational?

**Status:** `KILL — K185`

Recent 2026 work now directly centralizes the contextual-entrainment scaling law, including the split whereby semantic entrainment decreases with scale while arbitrary/non-semantic copying can increase. L21's surviving contribution would be to explain this mature phenotype using a corpus self-recurrence/cache statistic whose normative quantity is itself difficult to identify independently of topic/discourse/syntax. That is too narrow and too correlational for the current Main-level mechanism bar.

## L22 — Bad Dimensions or Bad Directions?

**Status:** `KILL — K186`

The orthogonal-rotation argument is mathematically clean, but the paper remains a representation/retrieval-method identifiability audit: “coordinate dimensions are arbitrary under basis change.” Its strongest reviewer compression is the old rotation/basis-invariance fact applied to modern embedding-dimension attribution. It does not give us the desired model-computation mother problem, and current search explicitly deprioritizes retrieval/measurement audits.

## L23 — Similarity Is Not Provenance

**Status:** `KILL — K187`

The temporal impossible-copy control is elegant, but the parent is a provenance/measurement-validity question: can similarity identify copying rather than independent reconstruction? Under the current portfolio taste this is not a sufficiently central `why does the model compute this way?` question, and the natural growth path remains plagiarism/provenance evaluation rather than model mechanism.

## L24 — Same Entity ≠ Same Epistemic File

**Status:** `KILL — K188`

This route was already HOLD/deprioritized. It sits inside the hottest generic Agent/long-term-memory state-tracking space and requires a memory harness plus difficult perspective/state gold before the central claim is secure. The current project explicitly does not spend open-ended search budget there. Do not reactivate via another memory architecture or benchmark.

## L26 — Same PICO ≠ Same Causal Question

**Status:** `KILL — K189`

The estimand distinction is scientifically legitimate, but the paper is fundamentally a scientific-document/evidence-synthesis representation and data-gold project. It requires expert trial/estimand reconstruction and a defensible pooling consequence before the NLP claim is identified. This is exactly the high-workload data/scientific-IE route the current search has moved away from; clean clinical methodology does not make it the right portfolio question.

---

# Recent important kills / holds

## L19 — Causal Ingredients of Long→Short SFT Transfer

**Status:** `ARCHIVED / NO-GO (K184) — cost/resolution kill, not novelty kill`

The causal gap remains open, but the expected matched effect is below the available evaluation/training resolution. Credibly separating a meaningful null from a small effect would require roughly 100–300 GPU-hours. Do not shrink the claim to fit the budget.

## Temporal Forgetting

# **DO NOT RESURRECT**

This entire parent is hard-banned for current search: forgotten≠erased, old-prefix rescue, checkpoint rescue, earlier ability suppressed, final-checkpoint readout, temporal sampling, capability shift, or renamed variants.

---

# Search discipline

Before promoting a hook:

> **scientific object + estimand + decisive operation + synonyms → killed ledger / archived candidates / recent search rounds → repeated mother evidence → SAME-QUANTITY check → direct-owner assassination → reviewer compression → only then SELECT**

Do not mine one paper's Discussion as the default source of novelty. Prefer 2–4 independent strong papers exposing the same abnormal quantity under different names, or an old empirical law whose load-bearing premise genuinely changes in the modern regime.

Search V–VII are the current anti-duplication frontier. In particular, do not reopen reasoning-length/overthinking, CoT faithfulness, metacognition-control, RLVR entropy/mode collapse/capability boundary, self-correction, generic instruction-following loss, generic post-training rerouting, or other recently killed parents by adding another intervention/model family.

**L29 adds one more process gate:** for any `training stage → causal quantity` mechanism project, validate a meaningful positive first-stage intervention effect on an independent development split before spending compute on checkpoint trends. If the intervention cannot move the reference model, the training comparison is unidentified.

L30 does **not** reopen generic instruction-following loss: it is specifically the marginal causal value of the **joint correspondence structure in supervision**, with fixed prompt/response marginals and a later conditional-law path.

> **The goal is not to keep a portfolio full. The goal is to find one scientific object worth months of mechanism, boundary, intervention, and theory work.**