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

### L20 — What Does an LLM Learn From a Rewarded Trajectory?

**Status:** **SERIOUS / PRE-PILOT — HIGH COLLISION RISK — NO COMPUTE AUTHORIZED**  
Package: `candidates/L20_ICRL_UPDATE_UNIT/`

RQ:

> When a fixed pretrained LLM sees a multi-step attempt followed by scalar reward, does its next policy preferentially update the actions that causally earned the outcome, or mainly treat the whole rewarded trajectory as a good/bad demonstration?

Current novelty fence: **Not K021 unless the project collapses back into retrospective step attribution.** L20's estimand is future fixed-weight policy change after reward exposure. The remaining pre-pilot blocker is an exact-operation audit against 2026 credit-assignment / ICRL work plus a data gate showing that trajectory-outcome × local-action-quality conflicts can be obtained naturally with executable replay gold.

Priority note: RL / agent / credit assignment is a very crowded 2026 neighborhood. L20 is a high-risk backup lead, not a reason to narrow future search toward RL. Prefer cleaner NLP / language / measurement / mechanism questions when available.

---

## Most recent search decisions

Full record: `search_rounds/2026-09-12_POST_L18_ANTI_RESURRECTION.md` and `search_rounds/2026-09-12_CONTINUED_SEARCH.md`.

Recent deaths include:

- **L18 contextual entrainment × word-meaning priming causal identity** — existing phenomena/mechanisms leave only a narrow overlap/mediation story.
- **Temporal forgetting → latent survival via relearning** — pretraining factual forgetting is already directly studied; relearning/savings leaves a narrow adjacent diagnostic rather than a new Main-level parent.
- **Own-answer persistence vs generic anchoring** — direct 2026 self-attribution interventions already own the decisive comparison.

Do not reopen these by changing model, benchmark, terminology, or adding mechanism after the parent question has already failed.

---

## Governing search rule

Before generating or deep-searching a lead:

> **scientific object + estimand + decisive operation + synonyms → search killed ledger / archived candidates / relevant historical repo → duplicate means discard first, not after design.**

For every survivor, perform the successful-result test and pre-register the natural claim mutations before compute.

`SEARCH → SELECT → PILOT → RE-SELECT → DEVELOP → RE-SELECT → PAPER / KILL`

> **Evidence survives claim mutation. Authorization does not.**
