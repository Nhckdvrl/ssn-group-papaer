# L15 — No Result Is Not No Evidence

## Do LLMs condition null evidence on what they *would have observed*?

**Status:** **PILOT-AUTHORIZED — ONE BOUNDED KILL-ORIENTED PILOT ONLY (2026-09-11)**  
**Paper mainline:** NOT APPROVED  
**Target:** ACL / EMNLP / NAACL Main

> **Plain example**  
> Camera A detects 99% of people who enter an airport. Camera B detects only 5%. Both return: **"Alice was not detected."**  
> The same null observation should be strong evidence of absence under A and almost no evidence under B.

---

## 1. Research question

> **When an LLM receives a null observation, does it update its belief using the observation process — i.e. how likely that null would have been if the hypothesis were true — or does it treat `nothing found` as evidence with roughly fixed semantic force?**

The load-bearing computation is:

\[
P(H\mid N) \propto P(N\mid H)P(H),
\]

where `H` is the world hypothesis and `N` is a null observation.

The project is **not** generic Bayesian arithmetic, generic RAG abstention, generic uncertainty calibration, or a generic partial-observability benchmark. The proposed scientific object is **counterfactual observation integration for null evidence**.

---

## 2. Why this is interesting

A null result is only informative if the procedure had a good chance of finding the target had it existed.

This matters directly for modern LLM systems:

- search/RAG: `0 results` from exhaustive search versus a low-recall retriever;
- agents: an API/query returning nothing after a complete scan versus timeout/partial scan;
- medicine: a negative result from a high-sensitivity versus low-sensitivity test;
- monitoring/debugging: no alert from a reliable versus unreliable detector;
- robotics: not seeing an object under high versus low visibility.

The high-level question is therefore larger than a probability puzzle:

> **Does the model represent not just the world, but the process by which its evidence would have been generated?**

A particularly strong result would be a dissociation:

> the model correctly answers `How likely was this sensor/search to miss the target if it existed?`, yet fails to use that answer when deciding whether the target exists.

That would establish an **observation-model integration gap**, not merely lack of knowledge or arithmetic skill.

---

## 3. Classical parent

Hsu, Horng, Griffiths & Chater, *When Absence of Evidence Is Evidence of Absence: Rational Inferences From Absent Data* (Cognitive Science, 2017) provides the classical parent.

Their central result is that the evidential value of absence depends on how surprising that absence would be under the hypothesis. Human judgments tracked the Bayesian prediction as the probability of observing the missing event changed.

This is an old problem and therefore not our novelty. It provides a durable scientific object and a validated experimental logic.

---

## 4. Fresh 2026 ownership audit

Full audit: [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md).

The strongest current compression is:

> **Hsu et al. 2017 absence-of-evidence + Deng & Yan 2026 selection neglect/WYSIATI + 2026 LLM belief-state/partial-observability work (Belief-State Engine; Belief-Based World Models; Belief Memory) + RAG evidence-sufficiency/over-searching = L15.**

That compression kills the project if L15 becomes only:

- "LLMs are bad at Bayesian updating";
- "LLM agents need explicit beliefs under partial observability";
- "empty retrieval should cause abstention";
- or "sensor reliability matters."

The currently surviving independent question is narrower:

> **No direct owner found that isolates identical null observations while varying counterfactual detectability, then dissociates explicit observation-likelihood competence from its use in posterior world-state inference.**

Two recent papers are especially important boundaries:

1. **Belief-State Engine (2026-09-09)** argues that raw-history LLM policies are not belief-measurable under POMDP partial observability and supplies an external Bayesian filter. It owns the broad architectural claim that LLM agents benefit from explicit belief-state machinery. L15 must not claim that general result.
2. **Towards a Belief-Based World Model for LLM Agents (2026-08-31)** explicitly uses presence/absence belief updates in ALFWorld. It owns a method-level belief representation story, not the controlled behavioral question of whether the LLM itself conditions the evidential value of the *same null result* on detectability.

The project remains alive only as a **specific computation/dissociation paper**, not as a generic POMDP or belief-state paper.

---

## 5. Locked accounts before compute

### Account A — Observation-conditioned inference

The model computes or approximates the likelihood of the null observation under the hypothesis:

\[
P(N\mid H),
\]

and uses it to update the world-state belief. As detectability rises, the same null result becomes stronger evidence against `H`.

### Account B — Null-result heuristic

The model maps surface outcomes such as `not found`, `no detection`, or an empty result to a relatively fixed evidential meaning, underweighting the generating process.

### Diagnostic decomposition

If Account B-like behavior appears, separate:

1. **observation-model competence failure** — the model cannot correctly estimate `P(N|H)`;
2. **integration failure** — it can estimate `P(N|H)` but does not use that estimate in `P(H|N)`;
3. **execution failure** — it succeeds in a direct reasoning probe but fails when the same null evidence arrives through a tool/agent interface.

This decomposition is fixed before experiments. Do not replace it post-hoc with hidden-state probing.

---

## 6. Data/gold

Full contract: [DATA_AND_GOLD.md](DATA_AND_GOLD.md).

For a target-exists hypothesis `H`, prior `p`, detector sensitivity `s=P(D|H)`, false-positive rate `f=P(D|¬H)`, and null observation `N=¬D`:

\[
P(H\mid N)=\frac{p(1-s)}{p(1-s)+(1-p)(1-f)}.
\]

The pilot uses exact programmatic gold. The evaluated model never supplies labels.

Primary design keeps the observed result fixed (`no detection`) and changes only the observation process.

Example with `p=0.5`, `f=0`:

| sensitivity `s` | gold `P(H|N)` |
|---:|---:|
| 0.05 | 0.4872 |
| 0.25 | 0.4286 |
| 0.50 | 0.3333 |
| 0.90 | 0.0909 |
| 0.99 | 0.0099 |

Natural frames are matched across domains (camera, database/search, medical test, monitoring/logging). The first pilot does not require LLM-generated main data or LLM judging.

---

## 7. Bounded pilot

Full preregistration: [PILOT_CARD.md](PILOT_CARD.md).

### E01 — Null-evidence sensitivity curve

Hold constant:

- hypothesis;
- prior;
- null observation;
- surface wording as much as possible.

Vary only detector/search sensitivity and measure whether posterior belief tracks the Bayesian ordering and magnitude.

### E02 — Competence vs integration

On the same item, separately ask:

1. `If H were true, how likely is this procedure to return no detection?`  → observation likelihood;
2. `After this no-detection result, how likely is H?` → posterior belief.

The strongest prospective finding is:

> **correct counterfactual observation likelihood + incorrect posterior integration.**

### E03 — pre-existing-computation intervention

If E02 reveals integration failure, require the model to state the observation likelihood before updating the world-state belief. Test whether this restores the detectability gradient.

This is diagnostic, not a new paper identity.

### Conditional later extension — agent/tool execution

Only after re-selection may the same computation be tested with a controlled search tool whose result is identically `[]` but whose documented coverage/recall differs. The outcome is then belief/action: conclude absence, continue searching, switch tools, or retain uncertainty.

No agent extension is authorized before E01–E03 are judged.

---

## 8. Hard kill rule

Archive L15 after the bounded pilot if any of the following holds:

- capable models closely track the detectability-conditioned posterior across numeric and natural frames;
- any residual error is explained by ordinary arithmetic/base-rate failure rather than the null-observation computation;
- observation-likelihood probes and posterior updates fail together with no independent integration gap;
- the only interesting result is generic partial-observability or calibration failure already owned by 2026 belief-state work;
- a direct owner is found for `same null observation × varied detectability × observation-likelihood-versus-posterior dissociation`;
- natural-language items cannot preserve the intended observation-process manipulation cleanly.

**Do not rescue a failed pilot with model zoos, hidden-state scans, RAG wrappers, or a broader "belief state" title.**

---

## 9. Prospective paper identity

A Main-shaped paper would need one coherent inference:

**C1 — Null evidence is observation-process dependent.**  
Show whether LLM belief updates track detectability for identical null observations.

**C2 — Locate the computation.**  
Distinguish failure to model `P(N|H)` from failure to integrate a correctly modeled `P(N|H)` into `P(H|N)`.

**C3 — Consequence.**  
Only after fresh re-selection, test whether the same computation predicts premature `not found → does not exist` decisions in controlled tool use.

The intended takeaway is not "LLMs need Bayes." It is:

> **A model can know what its observation process would miss yet fail to use that knowledge when deciding what is true.**

Any material drift from this claim requires a fresh novelty/ownership gate.

---

# Current verdict

# **PILOT-AUTHORIZED — STRICTLY BOUNDED**

The broad belief-state/partial-observability space is crowded in 2026. The route survives only because the proposed decisive object is more specific: **the evidential value of a null observation as a function of counterfactual detectability, with an explicit competence-vs-integration dissociation.**

Run E01–E03 only. A positive result returns to selection; it does not automatically authorize agent expansion.