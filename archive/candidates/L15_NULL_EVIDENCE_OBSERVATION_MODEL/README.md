# L15 — No Result Is Not No Evidence

## Do LLMs condition null evidence on what they *would have observed*?

**Status:** **ARCHIVED / NO-GO — KILL K183 (2026-09-11)**  
**Killed by:** its own bounded pilot. See [PILOT_REPORT.md](PILOT_REPORT.md).  
**Paper mainline:** NOT APPROVED  
**Target:** ACL / EMNLP / NAACL Main

> **Plain example**  
> Camera A detects 99% of people who enter an airport. Camera B detects only 5%. Both return: **"Alice was not detected."**  
> The same null observation should be strong evidence of absence under A and almost no evidence under B.

> **Archive note.** The bounded E01/E02 pilot answered the locked question in the
> negative: with normal reasoning allowed, both model families scale the same null
> observation with stated detectability essentially exactly (Spearman .989 / .945,
> KNI rate .003 / .014). There is no competence–integration dissociation to sell, and the
> direct-answer failure is not null-specific — the `f=0` positive counterpart and the bare
> arithmetic control fail by the same margin. **No experiment is authorized from this
> package.** The surviving observation ("models need room to compute") is a historical
> record, not a fallback identity.

## Locked research question

> **For the same observed null result, does an LLM scale its world-state update with counterfactual detectability, and can it correctly represent `P(null|H)` while failing to use that quantity in `P(H|null)`?**

The paper is not generic Bayesian reasoning, evidence reliability, diagnostic reasoning, RAG abstention, partial observability, belief-state tracking, or probabilistic memory.

## Why this survives the expanded novelty audit

The strongest current compression now includes all of the following:

- **Hsu et al. 2017:** classical absence-of-evidence / observation-process result;
- **Kim et al., NAACL 2025 Main:** LLM evidence→belief updating under varying evidence informativeness/reliability;
- **Gupta et al., ACL 2025 Main:** controlled Bayesian updating;
- **Rodman et al., JAMA 2023:** LLM pre/post-test probability after positive and negative diagnostic results;
- **Deng & Yan 2026:** selection neglect / WYSIATI in LLM belief updating;
- **2026 BSE / BB-WM / BeliefMem / T3-AREW:** explicit belief-state and partial-observability failures/methods;
- **2026 retrieval/evidence-sufficiency work:** unanswerable/no-context/negative-evidence abstention.

Those works make the broad area crowded. The route survives only because no direct owner was found for the exact five-part object:

1. identical null observation;
2. isolated detectability manipulation;
3. matched explicit `P(null|H)` probe;
4. separate `P(H|null)` probe;
5. competence–integration dissociation as the central scientific target.

Full audit: [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md).

## Locked accounts

### A — observation-conditioned inference
The model uses the observation likelihood when updating the world state.

### B — null-result heuristic
The model assigns roughly fixed evidential force to surface outcomes such as `not found` or `no detection`, underweighting the generating process.

If B-like behavior appears, the preregistered decomposition is:

- observation-model competence failure;
- **integration failure**: observation likelihood known, posterior update wrong;
- only after re-selection, possible execution gap in a controlled tool interface.

## Data/gold

Gold is analytic, not model-generated:

`P(H|N) = p(1-s) / [p(1-s) + (1-p)(1-f)]`.

Primary pilot fixes the visible null result and varies only sensitivity/detectability across matched camera, database/search, diagnostic, and monitoring frames.

See [DATA_AND_GOLD.md](DATA_AND_GOLD.md).

## Authorized pilot

Only these are authorized:

- **E01:** same-null detectability curve;
- **E02:** explicit observation-likelihood competence versus posterior integration;
- **E03:** if an integration gap appears, preregistered intervention that makes `P(null|H)` explicit before the posterior update.

See [PILOT_CARD.md](PILOT_CARD.md).

No agent/RAG extension, hidden-state scan, model zoo, memory method, or external Bayes filter is authorized before re-selection.

## Preferred Main-level signature

The strongest result is not "LLMs are bad at Bayes." It is:

> **The model can correctly say how likely its observation process was to miss the target, yet fail to use that knowledge when deciding whether the target exists.**

This is the claim that must remain novel as the project develops.

## Hard kill / mutation rule

Kill or return to selection if:

- capable models track the detectability-conditioned posterior well;
- residual errors reduce to ordinary arithmetic/base-rate failure;
- P1 and P2 fail together with no competence–integration distinction;
- the interesting result reduces to generic evidence reliability, diagnostic Bayes, selection neglect, partial observability, RAG abstention, or belief-state tracking;
- a direct current owner of the locked computation appears.

If the observed RQ, estimand, mechanism, central claim, or reviewer one-line takeaway materially changes after E01–E03, **stop before the next experiment and run a fresh ownership audit**.

> **Evidence survives claim mutation; authorization does not.**

# Current verdict

# **REGISTERED — ONE BOUNDED PILOT AUTHORIZED**

The area is collision-prone, but the exact claim above remains separable after the expanded ownership audit. Registration applies to that claim only, not to neighboring broader stories.