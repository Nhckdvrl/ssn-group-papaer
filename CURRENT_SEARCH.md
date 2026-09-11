# Current Research State — 2026-09-11

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Active serious candidates:** **1 — L16, PILOT-AUTHORIZED (E01 + conditional E02 only)**  
**Current phase:** **BOUNDED KILL-ORIENTED PILOT**  
**Killed ledger:** through **K183** — **Next kill ID: K184**

---

# Active candidate — L16

## Same World, Different Partitions

Canonical package: `candidates/L16_PARTITION_DEPENDENT_BELIEF/`

Locked RQ:

> **Holding the atomic hypotheses, evidence, target proposition, lexical inventory, and normal reasoning budget fixed, does arbitrary refinement/coarsening of the displayed hypothesis space systematically pull an LLM's elicited credence toward the uniform mass over displayed cells (`1/M`), and can that representationally induced credence shift survive explicit recognition that the partitions are informationally equivalent?**

Plain example:

> The event is the same: **Sunday is the hottest day next week.** A binary display `{Sunday}|{not Sunday}` makes an ignorance prior of `1/2` salient; a seven-way display `{Sunday}|{Monday}|...` makes `1/7` salient. No evidence about the weather changed. A coherent belief about the same event should not be created by redrawing the hypothesis space.

### Why this candidate is authorized

The classic human phenomenon — partition dependence / partition priming — is established. The modern LLM question is not a generic replication of that bias. The locked target is a specific computation:

1. exactly the same atomic hypotheses are retained;
2. exactly the same evidence and target proposition are retained;
3. only arbitrary grouping/refinement changes;
4. the predicted effect is directional toward the partition-specific `1/M` ignorance prior;
5. equivalence knowledge and downstream credence are measured separately.

The expanded audit covers Support Theory / classic partition dependence, current LLM confidence elicitation/calibration, 2026 semantic-invariance/coherence work, multiple-answer confidence, response-scale effects, the fresh 2026 record-grouping paper, and 2026 causal confidence→abstention work.

The strongest collision fence is explicit: **generic semantic prompt sensitivity is already owned.** If L16 produces only "equivalent prompts give different confidence," the route dies. The contribution must be a hypothesis-space partition law, not another invariance benchmark cell.

### Authorized work

Only:

- **E01:** 48-base content-matched partition curve under normal reasoning, with fixed atomic alternatives/order and `M2/M3a/M3b/M9/FLAT` conditions;
- **E02:** only if E01 passes the preregistered two-family gate — explicit equivalence awareness, arbitrary-group disclaimer, readout robustness, and stronger-evidence attenuation.

Primary models: Qwen3-32B and Mistral-Small-24B. Primary mode: normal reasoning / CoT. An effect that exists only when reasoning is blocked is a kill signal.

The full pilot is already specified; **no additional literature/design gate is required before smoke**:

- [README](candidates/L16_PARTITION_DEPENDENT_BELIEF/README.md)
- [ownership audit](candidates/L16_PARTITION_DEPENDENT_BELIEF/RELATED_WORK_AND_NOVELTY.md)
- [data/gold contract](candidates/L16_PARTITION_DEPENDENT_BELIEF/DATA_AND_GOLD.md)
- [pilot card](candidates/L16_PARTITION_DEPENDENT_BELIEF/PILOT_CARD.md)
- [experiment ledger](candidates/L16_PARTITION_DEPENDENT_BELIEF/EXPERIMENTS.md)

### Hard identity fence

Do not rescue L16 as any of the following without returning to selection:

- generic prompt sensitivity / semantic invariance;
- verbal-confidence calibration;
- option-count / multiple-choice bias;
- evidence-record grouping;
- distractor effects;
- response-scale design;
- weak-model-only cognitive bias;
- "CoT fixes the bias";
- a debiasing prompt/method.

If RQ, estimand, mechanism, central claim, or reviewer one-line takeaway changes materially, authorization expires before the next experiment.

---

# Most recent kill — L15 (K183)

## No Result Is Not No Evidence — ARCHIVED / NO-GO, 2026-09-11

Canonical package: `candidates/L15_NULL_EVIDENCE_OBSERVATION_MODEL/` (no authorization).

The locked RQ was:

> **For the same observed null result, does an LLM scale its world-state update with counterfactual detectability, and can it correctly represent `P(null|H)` while failing to use that quantity in `P(H|null)`?**

Its own bounded E01/E02 pilot answered no. With normal reasoning allowed, both model families track the detectability-conditioned posterior essentially exactly (Spearman .989 / .945, compression ratio .985 / .929, KNI rate .003 / .014, obs-known rate 1.000). The direct-answer failure is not null-specific: the `f=0` positive counterpart and the bare arithmetic control fail by the same margin, while prior-only is exact.

E03 was never run — it was conditional on an integration gap that does not exist.

**The forbidden fallback is recorded explicitly:** "LLMs need explicit reasoning to use observation models" is a different paper identity, was never selected, and compresses into generic chain-of-thought / Bayesian-elicitation / reasoning-and-calibration work. It survives as a historical observation, not as a route.

Full record: `candidates/L15_NULL_EVIDENCE_OBSERVATION_MODEL/PILOT_REPORT.md` and `failed/KILLED_LEDGER.md` K183.

---

## Portfolio reset history

Previously archived / killed routes remain preserved for reproducibility but carry no authorization:

- L02 / L03 / L04 / L06 / L07 / L08 / L09 / L10 / L11 / L12 / L13 / L14 / L15.

---

# Search / execution objective

Prefer questions with this shape:

> **durable and immediately understandable problem → simple natural/controlled data with hard gold → genuinely unresolved LLM-era computation → result interesting enough to matter by itself → broader consequence for actual NLP/LLM behavior.**

Classic parents are assets, not novelty failures. The novelty burden is on the **modern scientific question, inference, and development path**.

---

# Durable workflow rule

`SEARCH → SELECT → PILOT → RE-SELECT CURRENT PAPER IDENTITY → DEVELOP → RE-SELECT → PAPER / ARCHIVE`

> **A topic is not selected once. We continuously select the paper we are actually writing. Evidence survives claim mutation; authorization does not.**
