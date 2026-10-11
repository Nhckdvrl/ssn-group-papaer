# Territory Card — Incremental Interpretation & Revision — 2026-10-05

- **Lane:** Sasano-fit / language-model science / psycholinguistic process
- **Status:** PROPOSED; human-authorized baseline residency, does not change current ACTIVE allocation
- **Target venues:** ACL / EMNLP / NAACL; next suitable cycle
- **Core constraint:** exploration begins with frozen open-weight models + controlled language stimuli. No finetuning/RL is required to enter.
- **Lab-collision fence:** this is NOT Utami's AI-writing-change topic, Yano/Han's FrameNet/frame-semantics topic, Sato's character-knowledge-acquisition topic, Tsukagoshi/Kisako's embedding/compression topic, Hamdi's real-vs-fiction representation topic, Tanaka's survey/value-distribution topic, Kurauchi's audience-adapted kanji explanation topic, or Kan's idiom topic.

## 1. Territory object

> **As linguistic evidence arrives incrementally, how do language models form an interpretation, commit to it, revise it when later evidence conflicts, and carry or erase the old interpretation in subsequent processing?**

This is a territory, not a final paper RQ.

Garden-path syntax is the first calibration substrate because it has human data, controlled minimal pairs, and released code. **Garden-path recovery itself is not registered as novelty.**

## 2. Why this territory is scientifically live

Recent work has established several pieces without closing the larger object:

1. ACL 2025 (Amouyal et al., *When the LM misunderstood the human chuckled*) shows LLMs can retain garden-path misinterpretations and tests syntactic difficulty, plausibility, and verb-type accounts.
2. ACL 2026 Main (Amouyal et al., *Comparing human and language models sentence processing difficulties on complex structures*) broadens human/LLM comparison across seven difficult structures and releases stimuli, human data, prompts, and inference code.
3. ACL SRW 2026 (Baitalik & Datta, *Garden Path Recovery in Causal and Masked Language Models*) directly studies post-disambiguation recovery dynamics on NP/Z, NP/S, and MV/RR using surprisal/pseudo-surprisal and hidden-state divergence.
4. Findings ACL 2026 (Zeng et al., *Mechanistic Insights into Deferred Semantic Drift in LLMs*) studies delayed lexical disambiguation and a causal mechanism for later tokens retrieving earlier ambiguity information.
5. Human psycholinguistics has long shown partial reanalysis / lingering misinterpretation and targeted rereading/revision effects.

Therefore we do **not** ask whether LMs show garden paths, whether recovery exists, or whether ambiguity is hard. The live territory is the broader structure of **interpretation revision** across linguistic ambiguity types and readouts: what is revised, what lingers, when revision is complete, and which computational account predicts new conditions.

## 3. Strong ownership / compression risks

Already owned or too close:
- generic garden-path competence / "LLMs also have GP effects";
- plausibility / transitivity as the main explanation of GP difficulty;
- causal-vs-masked recovery curves on NP/Z, NP/S, MV/RR;
- generic delayed lexical ambiguity / metaphor DSD mechanism;
- another ambiguity benchmark without a process-level scientific question.

Compression test for any future lead:
> "Isn't this Amouyal 2025/2026 or Baitalik & Datta 2026 with more models / another ambiguity dataset?"

A future paper must expose a new **revision structure, condition, consequence, or causal account**, not merely expand coverage.

## 4. Foothold and data

### A. Primary behavioral calibration: Amouyal et al. 2026 release
Repository:
- https://github.com/samsam3232/comparing_humans_llms_processing_difficulties

Useful files:
- `data/extended_gardenpath_experiments.csv`: sentence, comprehension question, correct/incorrect answer, item set, GP/non-GP condition, GP-vs-simple question type.
- other released difficult-structure CSVs: NPS, NPVP, reduced relatives, double center embedding, depth charge, etc.
- released prefixes, human experiment code/results parser, model configs, and inference code.

Use: reproduce a known behavioral GP effect on one open-weight model before inventing a new metric.

### B. Manipulation substrate: Jurayj et al. 2022
Repository:
- https://github.com/wjurayj/garden-path-gpt2

Componentized stimuli:
- `npz.tsv`: 43 NP/Z items in the paper; components support ambiguous vs intransitive/blocker/comma variants and optional context/extension.
- `nps.tsv`: 20 NP/S items; supports ambiguous vs unambiguous verb and explicit `that`.
- `vawip.tsv`: 20 MV/RR items; supports reduced/unreduced and intervening material.
- `make_sents.py`: programmatic sentence construction.

Use: controlled cue timing/strength and ambiguity-duration manipulation. This is the main substrate for new causal contrasts after baseline reproduction.

### C. Independent classical set
Microsoft Turing Experiments:
- https://github.com/microsoft/turing-experiments
- `Christianson_2001.tsv` and `Alternates_2022.tsv` provide garden-path/control materials and a separate replication substrate.

Use: avoid depending on one modern paper's dataset.

### D. Later expansion beyond garden paths
Only after GP instrumentation is validated:
- lexical ambiguity / delayed disambiguation;
- referential ambiguity;
- PP attachment / quantifier scope / conjunction ambiguity;
- noisy-channel correction / explicit retraction.

Do not download ten datasets at once. Each new class enters only if it distinguishes an account that survived the prior stage.

## 5. First residency block

### D0 — artifact audit
Freeze exact revisions/licenses for the three data/code sources above. Record:
- file hashes;
- row/item counts;
- duplicated or malformed items;
- which data can be redistributed vs must be downloaded locally;
- exact construction labels and question semantics.

### E00 — behavioral positive control
Goal: prove the harness can reproduce a known lingering garden-path misinterpretation before any new claim.

Minimal first model:
- Qwen3-8B or another already-local 7B–14B open model, deterministic decoding/logprob path where possible.

Primary readouts on released Amouyal data:
- accuracy / answer probability on `GP_question` vs matched `simple_question`;
- GP vs matched non-GP difference within `set_id`;
- report paired bootstrap CI over items.

Positive control:
- simple questions should remain high while GP-targeted questions show the known GP-specific deficit on at least one validated model/config.

Failure of the positive control is an instrumentation/prompt issue, not evidence against the territory.

### E01 — controlled revision-pressure map
After E00 passes, generate matched NP/Z, NP/S, MV/RR conditions from Jurayj:
- ambiguous GP;
- explicit early disambiguation (comma / `that` / unreduced);
- blocker;
- longer ambiguity region via extension/context.

Measure both:
1. final intended interpretation;
2. lingering initial interpretation.

This is a **measurement map**, not a paper claim.

### E02 — explanation-separating perturbations
Only after a stable E01 pattern exists. Competing accounts should make different predictions under:
- cue timing;
- cue explicitness;
- ambiguity duration;
- task/readout change with the sentence held fixed.

Do not run white-box fishing yet. Probe/patch/steer only after behavior supports a specific contrast.

## 6. Pressure families

A. **Commitment:** when does an initially possible parse become a committed interpretation?
B. **Revision completeness:** does successful final answering erase, suppress, or merely override the old interpretation?
C. **Cue timing/strength:** which evidence triggers revision, and how does delay change residual influence?
D. **Representation-to-use gap:** does a revised interpretation appear in one readout but fail to govern another?
E. **Cross-ambiguity abstraction:** which revision signatures generalize beyond garden-path syntax, and which are construction-specific?
F. **Measurement validity:** do QA, next-token probability, paraphrase, and hidden-state diagnostics agree on "recovery"?

## 7. Decision branches

- **Known GP effect does not reproduce** → fix harness/prompt first; no scientific conclusion.
- **Only end-state accuracy changes, no stable revision signature** → improve measurement; do not invent mechanism.
- **A stable signature appears but is fully predicted by Amouyal/Baitalik priors** → use it only as calibration and move to a new ambiguity class/account.
- **Two readouts disagree systematically under matched stimuli** → high-information lead; determine whether this is measurement mismatch or genuine representation/use dissociation.
- **Cue timing/strength yields a stable nontrivial structure** → formulate competing accounts and add a discriminating intervention.
- **A pattern survives across ≥2 ambiguity classes** → candidate for a broader interpretation-revision claim; only then consider white-box causal analysis.

## 8. Do not do

- do not claim "LLMs show garden paths";
- do not make another generic ambiguity benchmark;
- do not use model count as novelty;
- do not treat surprisal spike alone as "revision";
- do not jump to SAE/probes before behavioral accounts are separated;
- do not train a model to create the first phenomenon;
- do not silently drift into FrameNet, idioms, AI-writing effects, audience explanation, embeddings, or other current lab members' main objects.

## 9. Selection decision

**2026-10-05 — REGISTERED AS PROPOSED; baseline residency explicitly authorized by human.**

Reason:
- the scientific object is orthogonal to current lab main topics while matching Sasano's preferred research shape: natural question → stable phenomenon → why → discriminating experiments;
- first evidence is training-free and cheap;
- mature human and LLM baselines provide strong positive controls;
- the territory can grow by interpretation dynamics rather than benchmark improvement;
- direct 2025–2026 ownership is strong enough to force disciplined positioning from day one.
