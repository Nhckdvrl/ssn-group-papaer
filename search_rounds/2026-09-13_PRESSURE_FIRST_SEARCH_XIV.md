# 2026-09-13 — Pressure-First Search XIV

Continuation after `PRESSURE_FIRST_SEARCH_XIII.md`. This batch deliberately leaves P69/noisy-channel unresolved and switches scientific objects again. It spans dependency locality, discourse accessibility, syntactic bootstrapping, and an identification audit of structural-priming IFE as evidence for error-driven in-context learning.

Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor. Nothing in this file has that status.

---

## P70 — Dependency locality in decoder LMs: learned expectation vs access limitation

**Status:** `DROP / OWNER DENSITY + PORTFOLIO REDUNDANCY`

### Pressure
Human sentence-processing theory has long debated whether long dependencies are costly because a previous constituent becomes difficult to retrieve from working memory or because locality expectations/surprisal make nonlocal continuation unlikely. A decoder Transformer changes the original cognitive regime: all prior tokens remain causally available, so the old memory premise is no longer literal.

### Why dead
ACL 2025 already provides evidence that neural sequence models exhibit an information-locality inductive bias rather than merely inheriting locality from language statistics, while ACL 2026 Best Paper *Memory Efficiency and Resource-Rational Encoding in Sentence Processing* explicitly separates retrieval mechanisms from the representations shaped by memory constraints. A new `distance effect = learned prior vs access` project is therefore already owner-adjacent. If narrowed to `information survives but access fails`, it also reproduces the state-vs-access skeleton already represented by L33 and killed neighboring hooks.

**Anti-resurrection:** do not reopen with another dependency type, distance sweep, activation patch, or `retrieval vs expectation` terminology unless a distinct estimand emerges.

---

## P71 — Discourse accessibility: carried discourse state vs late lexical reconstruction

**Status:** `DROP / PORTFOLIO-REDUNDANT IDENTIFICATION SHAPE`

### Pressure
Dynamic-semantic theories distinguish discourse referents that remain structurally accessible from referents whose surface lexical content may still be present but should not support anaphora. ACL 2025 reports that LLM anaphora behavior often relies more on lexical cues than human-like structural abstraction.

### Why dead
The tempting causal RQ is whether a referent state is genuinely carried forward or whether the model reconstructs/reads the antecedent only when the anaphor appears. Computationally this collapses again to `state already formed vs fresh late access`, the same identifying skeleton as L33 despite a different linguistic phenotype. The current search is required to expand scientific objects, not manufacture neighboring state-vs-readout papers.

**Anti-resurrection:** do not reopen anaphora accessibility merely with a different quantifier, dynamic-semantic construction, or patching target.

---

## P72 — Syntactic bootstrapping: same learning mechanism as humans, or distributional assimilation?

**Status:** `DROP / NATURAL MECHANISTIC ANSWER ALREADY ADVANCED`

### Pressure
Recent LLM work shows models use syntactic frames to infer aspects of novel-word meaning and explicitly notes that this does not establish the same learning mechanism as humans.

### Why dead
Earlier controlled work with novel tokens already shows that their learned embeddings assimilate toward existing words sharing syntactic distributions. Thus the most natural mechanistic continuation—syntactic context changes a lexical representation toward a distributionally compatible class—is not an open parent. Adding causal localization would mainly combine an existing behavioral mother with standard intervention tools.

**Anti-resurrection:** an author-stated `we do not prove the same mechanism` limitation is not by itself a Main-level ownership gap.

---

## P73 — Does syntactic surprise *causally* control the size of an in-context update?

**Status:** `SERIOUS AUDIT TARGET — NOT SELECTION — NO COMPUTE`

### One-line RQ
> **If an LLM sees the exact same syntactic example, does it learn more from it solely because we made that example surprising *before it arrived*?**

### Scientific pressure
NAACL 2025 *Is In-Context Learning a Type of Error-Driven Learning? Evidence from the Inverse Frequency Effect in Structural Priming* reports the inverse frequency/preference effect (IFE): structures that are less expected under a prime verb induce larger subsequent structural priming. The paper concludes that ICL therefore computes an implicit error signal and is error-driven. Importantly, the paper states its identifying assumption explicitly: it assumes the psycholinguistic argument that an error-driven mechanism is necessary to explain the IFE.

That assumption is stronger than the behavioral evidence itself. Classic structural-priming literature contains residual-activation, ACT-R/base-level learning, hybrid and adaptation accounts; related phenomena can emerge without a literal gradient-like error update. More directly, the same group’s 2026 *Causal Interventions on Continuous Variables* shows that verb-bias/error-like information is encoded in extracted steering vectors, but the error-signal aspects are not naturally causally used in downstream production, and the authors describe connecting the continuous variable to the ICL update as still unresolved.

EMNLP 2025 *Surprise Calibration for Better In-Context Learning* further shows that naturally varying surprise tracks class-prior shifts in generic ICL, increasing the importance of **causal identification** rather than another correlation between surprise and adaptation.

### Identifying move under audit
Intervene **before the prime structure is disambiguated**:

1. At the prime verb / pre-outcome state, causally shift the model's expectation toward PD or DO while leaving the eventual prime continuation untouched.
2. Feed the **same actual prime suffix** in both arms.
3. Measure the subsequent structural preference on a held-out target.

This creates `do(expectation) -> same observation -> later update`.

Predictions:

- **Mismatch-dependent / error-driven update:** the same PD prime should cause more later PD priming when the intervention first made DO more expected than when it made PD more expected; symmetrically for DO primes.
- **Expectation-independent trace / additive carryover:** once the observed prime is held fixed, its later structural trace should not depend materially on the counterfactually changed pre-prime expectation after direct intervention carryover is controlled.

This is stronger than `low-frequency primes correlate with larger effects` and distinct from the 2026 successor's post-context editing of extracted steering vectors: it manipulates the putative cause **before the outcome** and observes the native forward-pass update.

### Main confound and required first-stage/selectivity audit
The expectation edit can itself persist to the later target. Therefore any future Selection must require all of the following before interpreting the mismatch interaction:

- symmetric PD→DO and DO→PD edits;
- a substantial pre-outcome first-stage change in predicted structural expectation;
- the exact same observed prime suffix across the compared arms;
- a `no-informative-prime` / matched neutral-continuation control estimating direct carryover of the edit to the target;
- a mismatch-by-observed-structure interaction materially larger than direct carryover;
- disjoint development units for choosing the intervention layer/strength;
- no unrestricted prompt/model search after seeing the target effect.

If a selective first stage cannot be achieved, **kill**; a difference between two persistent steering biases is not error-driven learning.

### Ownership status
Search so far finds:

- NAACL 2025: behavioral IFE → error-driven inference;
- EMNLP 2025: surprise correlates with dynamic ICL prior shifts;
- Zhou et al. 2026: counterfactual editing of verb-bias/error-related dimensions **after** a prime representation is extracted;
- human psycholinguistics: extensive verb-bias × structure manipulations, but not a causal intervention on an LLM's internal pre-outcome expectation.

No direct owner has yet been found for `causally change pre-outcome expectation, hold observation fixed, test update size` in LLM ICL. This is not yet enough to authorize compute: broader theoretical ICL and mechanistic-surprise literature still require assassination, and the intervention may fail selectivity.

### Anti-resurrection / distinction from existing killed parent
This is **not** the killed `structural priming lexical boost vs abstract persistence` parent. Structural priming is being used as an instrument to audit the causal claim `ICL updates are prediction-error weighted`. Do not let the project drift into another priming taxonomy or syntax-representation atlas.

Sources: Zhou, Frank & McCoy, NAACL 2025; Tan et al., EMNLP 2025; Zhou, McCoy & Frank, arXiv 2605.29971 (2026); classic structural-priming / inverse-preference literature.

---

## Round checkpoint

**New survivor: 0.**

P73 is the strongest new identification hook in this batch, but it is explicitly **not** `PILOT-AUTHORIZED`. Continue broad search while stress-testing owner coverage, intervention selectivity, and whether the strongest successful result can grow beyond a narrow correction of one psycholinguistic diagnostic.