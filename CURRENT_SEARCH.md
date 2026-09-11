# Current Research State — 2026-09-12

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Current phase:** **bounded kill-oriented pilots + continued topic search**  
**Killed ledger:** authoritative through **K183**; newer search-round rejections are also recorded under `search_rounds/`.

---

## Active portfolio

### L16 — Same World, Different Partitions

**Status:** **PILOT-AUTHORIZED — bounded E01/E02 only**  
Package: `candidates/L16_PARTITION_DEPENDENT_BELIEF/`

RQ:

> Holding the atomic hypotheses, evidence, target proposition and reasoning budget fixed, does arbitrary refinement/coarsening of the displayed hypothesis space systematically pull an LLM's elicited credence toward a partition-specific ignorance prior?

Identity fence: this is not generic prompt sensitivity / confidence calibration. If the directional partition law is absent, kill rather than rescue through a weaker invariance story.

### L17 — What Does a Speech LLM Learn About a Speaker?

**Status:** **PILOT-AUTHORIZED — E01 only**  
Package: `candidates/L17_SPEAKER_ADAPTATION_UNIT/`

RQ:

> When a speech LLM improves after a few transcribed examples from one speaker, what actually generalizes to new utterances: a speaker-global state, a sublexical acoustic–phonetic mapping, or mainly lexical/textual context from the demonstrations?

E01 uses matched demonstration transcripts, same-speaker vs other-speaker audio, text-only controls, and high/low target-relevant phonetic coverage. If the established ICL benefit itself disappears under the matched design, archive rather than rescue.

### L21 — When Is Contextual Entrainment Rational?

**Status:** **PILOT-AUTHORIZED — E01 only**  
Package: `candidates/L21_ENTRAINMENT_CACHE_PRIOR/`

RQ:

> Is contextual entrainment a learned online-cache prior calibrated to the real self-recurrence statistics of language, or an overgeneralized / distribution-insensitive copying bias?

E01 is deliberately cheap: use public Pythia + Pile statistics to test whether token/distance-specific corpus self-recurrence predicts mother-style entrainment after frequency/token controls. No new pretraining is authorized. A strong calibrated relation and a strong reproducible miscalibration can both survive to re-selection; unstable/confounded recurrence statistics or failure to reproduce entrainment on Pythia kills the route.

Identity fence: this is not L18/014 alias transfer, sentence-level entrainment, another scaling law, copying-skill emergence, or induction-head formation. Novelty lives in the **training-distribution self-recurrence → model entrainment calibration relation**.

---

## Most recent search decisions

Full record: `search_rounds/2026-09-12_POST_L18_ANTI_RESURRECTION.md` and `search_rounds/2026-09-12_CONTINUED_SEARCH.md`.

Recent deaths include:

- **L18 contextual entrainment × word-meaning priming causal identity** — existing phenomena/mechanisms leave only a narrow overlap/mediation story.
- **L20 rewarded-trajectory update unit** — future-policy-shift is a real estimand difference from retrospective credit scoring, but the surviving novelty is narrow; the strong paper outcome depends on observing fine-grained local credit, while realistic causal gold requires expensive replay/counterfactual validation. Cheap symbolic versions weaken the intended claim.
- **Temporal forgetting → latent survival via relearning** — pretraining factual forgetting is already directly studied; relearning/savings leaves a narrow adjacent diagnostic rather than a new Main-level parent.
- **Own-answer persistence vs generic anchoring** — direct 2026 self-attribution interventions already own the decisive comparison.
- **Query-conditioned compression as reusable future-query memory** — directly occupied by KVzip / LazyMem-style future-query reuse work.
- **Feedback specificity / partial feedback / answer-information leakage** — refinement literature already directly studies partial guided refinement, fine-grained feedback and oracle/answer leakage; remaining cells are outcome-fragile.
- **Long-context distance vs similarity interference** — proactive/retroactive interference is now a direct modern LLM parent.

Do not reopen these by changing model, benchmark, terminology, or adding mechanism after the parent question has already failed.

---

## Governing search rule

Before generating or deep-searching a lead:

> **scientific object + estimand + decisive operation + synonyms → search killed ledger / archived candidates / relevant historical repo → duplicate means discard first, not after design.**

For every survivor, perform the successful-result test and pre-register the natural claim mutations before compute.

`SEARCH → SELECT → PILOT → RE-SELECT → DEVELOP → RE-SELECT → PAPER / KILL`

> **Evidence survives claim mutation. Authorization does not.**
