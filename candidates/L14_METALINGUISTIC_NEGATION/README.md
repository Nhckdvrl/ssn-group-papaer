# L14 — Negation of the World, or Negation of the Words?

## Metalinguistic Negation as an LLM Target-Selection Problem

**Status:** **PILOT-AUTHORIZED — ONE BOUNDED KILL-ORIENTED PILOT ONLY (2026-09-11)**  
**Paper mainline:** NOT APPROVED  
**Target:** ACL / EMNLP / NAACL Main

> **Plain example:**  
> *The movie wasn't good — it was excellent.*  
> Did the speaker mean that the movie failed to be good? **No.** The speaker rejects *good* as an inadequate description while committing to the stronger state *excellent*.
>
> Contrast:  
> *The movie wasn't good — it was terrible.*  
> Here the negation is ordinary world-state negation.

---

## 1. Research question

> **When an LLM encounters `not`, does it select what level is being rejected — a proposition about the world or the linguistic description itself — before applying polarity, or does it over-apply propositional negation and repair only when context forces reinterpretation?**

The scientific object is **negation-target selectivity**, not generic negation accuracy.

---

## 2. Why this is a serious LLM question

Metalinguistic negation (MN) versus descriptive negation (DN) is a classical, durable linguistic distinction. The old age of the parent is an asset, not a novelty failure.

Modern LLM negation work creates a new tension:

- EMNLP 2025 **Negation Blindness** shows that models often fail to react when ordinary negation should reverse a proposition.
- Findings EMNLP 2025 **This is not a Disimprovement** improves negation reasoning with warning/persona prompts and links better performance to stronger attention to negative tokens.
- NALOMA 2026 studies systematicity of negation expression/scope recognition.

These lines naturally encourage the interpretation:

> **more sensitivity to `not` = better negation understanding.**

MN shows why that need not be true. Sometimes literal polarity reversal is the error because the speaker is rejecting a wording/representation, not the described world state.

The prospective contribution is therefore:

> **Does target-agnostic negation sensitivity trade ordinary negation blindness for metalinguistic over-negation?**

If yes, current negation robustness is partly measuring cue sensitivity rather than correct selection of the semantic target.

---

## 3. A 2026 LLM-specific anomaly strengthens the motivation

Boggia (2026), **Artificial Epanorthosis**, reports that LLMs systematically overuse/miscalibrate corrective `Not X. Y`-style epanorthosis and shows generation-side mitigation.

Source: https://arxiv.org/abs/2607.21498

This does **not** own L14's comprehension question. It creates an unusually relevant modern tension:

> models disproportionately produce a construction whose interpretation can require rejecting an expression rather than negating the world; do they actually interpret the target of that negation correctly?

L14 must not sell a generic production–comprehension gap. The object remains negation-target selectivity and its consequence for negation-robustness claims.

---

## 4. Classical explanation is fixed before experiments

Human psycholinguistics supplies two competing accounts:

### Account A — descriptive-first / repair

Interpret `not X` as ordinary world-state negation first. If the later correction is incompatible with that reading, repair/reanalyse it as metalinguistic.

### Account B — context-sensitive target selection

Context can license a metalinguistic target from the start; the interpretation need not pass through a descriptively negated world state.

Noh et al. (2013) and Blochowiak & Grisot (2018) experimentally test this processing question. Blochowiak & Grisot also provide public controlled experimental data.

Sources:
- https://doi.org/10.1016/j.pragma.2013.07.005
- https://doi.org/10.5334/gjgl.440
- https://www.swissubase.ch/en/catalogue/studies/13418/20191/overview

This is the predeclared C2 explanation. Do not replace it post-hoc with generic hidden-state probing if the behavioral result changes.

---

## 5. Novelty boundary after fresh assassination

Full audit: [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md).

The strongest reviewer compression is:

> **Negation Blindness + negation-attention prompting + classical MN stimuli.**

That compression wins if the paper is just a DN/MN benchmark.

The surviving independent statement is narrower and stronger:

> **Prior LLM negation work does not establish whether an intervention that increases ordinary negation sensitivity is a monotonic improvement once the negator can target a linguistic representation rather than the world proposition.**

The first pilot therefore tests the **two-sided error profile and intervention trade-off**, not merely MN accuracy.

### Explicit collision fence — implicature cancellation

Spinoso-Di Piano et al. (2026), **Evaluating Communicative Belief Updates ... via Implicature Recognition and Cancellation**, directly owns recognition/cancellation of scalar and other implicatures.

Source: https://arxiv.org/abs/2607.25094

Therefore `some → all` cannot carry L14. Scalar cases may be a small diagnostic subtype only. A result confined to them kills/reconstructs the route.

---

## 6. Data/gold contract

Full contract: [DATA_AND_GOLD.md](DATA_AND_GOLD.md).

The pilot targets **40–60 human-audited lexical/discourse bases**, each with matched:

- positive control;
- descriptive negation;
- metalinguistic negation;
- non-negated / explicit paraphrase control.

The load-bearing question is a simple **world-state proposition**, not "is this MN?".

Example:

| condition | text | target: `movie is at least good` |
|---|---|---|
| POS | The movie was excellent. | YES |
| DN | The movie wasn't good — it was terrible. | NO |
| MN | The movie wasn't good — it was excellent. | YES |
| paraphrase | Calling it merely good understates it; it was excellent. | YES |

Use multiple subtypes. Lexical-strength and clearly linguistic/form corrections are primary. Scalar-implicature examples are secondary only.

No LLM-generated main data and no LLM judge for load-bearing gold. Paper-level claims require independent human validation of naturalness, intended DN/MN reading, and world-state truth.

---

## 7. Bounded pilot

Full preregistration: [PILOT_CARD.md](PILOT_CARD.md).

### E01 — two-sided target-selection profile

Measure on the same bases:

- **negation blindness:** failure to reverse in DN;
- **metalinguistic over-negation:** false reversal in MN;
- both conditional on passing lexical/paraphrase controls.

Start with two capable open model families. A third family is allowed only if heterogeneity determines the decision.

### E02 — existing negation-sensitivity intervention

Use the pre-existing warning-based intervention from Barreto & Jana (2025), not a prompt invented after seeing E01.

Primary paired quantities:

- `ΔDN = DN_correct(warning) - DN_correct(baseline)`
- `ΔMN = MN_correct(warning) - MN_correct(baseline)`

Strong prospective result:

> **DN improves while MN worsens** under an intervention explicitly intended to improve negation reasoning.

That would establish a real consequence: stronger lexical sensitivity to `not` is not equivalent to better negation understanding.

### E03 — context account, conditional only

Only if E01/E02 survive, test the classical pre-context versus post-correction manipulation to distinguish descriptive-first repair from context-sensitive target selection.

No hidden-state scan is authorized before this behavioral discrimination.

---

## 8. Hard kill rule

Archive L14 after the bounded pilot if:

- capable models are essentially ceiling on both DN and MN;
- the warning intervention shows no meaningful DN–MN differential and E01 supplies no independent target-selectivity signal;
- lexical/paraphrase controls explain the apparent effect;
- the effect exists only for scalar implicature examples;
- human intended-reading/world-state gold is unstable;
- a fresh direct owner of the same target-selection/trade-off claim is found.

**Do not rescue a failed pilot with probes, layers, a model zoo, more prompts, or a broader abstract name.**

---

## 9. Prospective full-paper path — not yet authorized

If the pilot survives, the project returns to selection before expansion:

**C1 — Target selection**  
Show a robust two-sided DN/MN profile under matched world-state probes.

**C2 — Processing account**  
Use pre-context/post-correction to distinguish polarity-first repair from context-sensitive target selection.

**C3 — Consequence**  
Show whether current negation-improvement interventions move a DN/MN trade-off rather than monotonically improving understanding.

The paper is Main-shaped only if these form one inference:

> **negation understanding requires selecting the semantic target before applying polarity; target-agnostic sensitivity can make one established failure better while making the complementary failure worse.**

Any material mutation of this takeaway requires a fresh selection/novelty gate.

---

# Current verdict

# **PILOT-AUTHORIZED — STRICTLY BOUNDED**

The final pre-pilot audit found no direct modern owner of the specific **DN-improvement / MN-over-negation target-selectivity** question. It also found two important constraints that are now locked in:

1. **Artificial Epanorthosis** is motivation/modern anomaly, not our claimed discovery;
2. **ImplicatureX** owns pragmatic cancellation, so scalar cancellation cannot become the fallback paper.

The next legitimate work is exactly E01/E02 after the human stimulus audit. A positive result triggers **re-selection**, not automatic expansion.
