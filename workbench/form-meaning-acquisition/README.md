# Form–Meaning Acquisition Gap — Workbench

**Lane: sasano-taste. Status: exploratory workbench — not a candidate.**

## Territory

This workbench studies a simple mismatch in language-model acquisition:

> a model can become good at recognizing that a construction is grammatical before it reliably recovers the meaning carried by that construction.

The object is **not** a new benchmark and **not** a claim that LLMs lack constructional understanding. The point of the workbench is to understand when form recognition and meaning acquisition separate, and what closes or widens that gap.

## Why this territory is worth inhabiting

Recent work provides unusually clean pressure:

- **CxMP (ACL 2026 Outstanding Paper)** reports that grammatical acceptability emerges earlier than constructional understanding, and that some form–meaning mappings remain difficult even for large LMs.
- **Language Models Learn Constructional Semantics, Not To Mention Syntax (CoNLL 2026)** shows that some modest open models do acquire rare constructional semantics, while human-scale-data models fail on meaning evaluations.
- **Heterogeneity in Formal Linguistic Competence of Language Models (Findings ACL 2026)** shows that some apparent grammatical failures can be strongly altered by injecting only a small amount of targeted pretraining data.

Together these results make the object interesting without fixing the answer in advance: a persistent form→meaning gap could come from exposure scarcity, lexical diversity, abstraction difficulty, training dynamics, or an evaluation artifact.

## Baseline residency first

Before inventing any explanation:

1. reproduce the CxMP form-vs-meaning separation on released/open models;
2. identify the strongest simple scoring/evaluation setup and verify that conclusions are not prompt-format artifacts;
3. reproduce at least one second constructional-semantics dataset so the object is not CxMP-specific;
4. map performance by construction, lexical overlap, frequency, schematicity, and model/checkpoint scale;
5. use intermediate checkpoints where available before training anything ourselves.

Do **not** create a new construction benchmark at the beginning.

## First exploratory analyses

These are discovery axes, not preregistered paper claims.

- **Exposure axis:** estimate corpus frequency / diversity of each construction and ask whether low semantic performance is simply low exposure.
- **Lexical-anchor axis:** hold construction fixed while replacing familiar lexical anchors; test whether apparent semantic competence collapses outside memorized frames.
- **Type-vs-token diversity:** compare many repetitions of a narrow lexical realization against fewer but more diverse realizations.
- **Trajectory axis:** when checkpoints are available, compare the time at which acceptability, form recognition, and semantic inference emerge.
- **Minimal intervention:** only after the observational map, inject small controlled amounts of constructional evidence into a small LM to see what kind of evidence closes the gap.
- **Generalization test:** if an intervention helps, require transfer to held-out lexical realizations; otherwise it is memorization, not acquisition of the constructional meaning.

## What would change our understanding

Useful outcomes include:

- the gap mostly disappears after controlling for exposure → the scientific object becomes data sufficiency / evidence type;
- extra exposure helps syntax but not meaning → stronger evidence that form→meaning abstraction is the bottleneck;
- lexical diversity matters much more than raw token count → the object becomes evidence diversity;
- pretrained models show a stable temporal lag between form and meaning → training dynamics may be the real object;
- the gap vanishes under a stronger evaluation → the original phenomenon was partly an instrument artifact, which is itself important.

## Risks / kill conditions

- If a strong baseline plus prompt/scoring controls removes the form→meaning gap across datasets, stop.
- If nearest-prior work already explains the gap entirely with exposure frequency and reproduces it across constructions, stop rather than repackage it.
- If progress requires inventing many synthetic constructions, gold labels, and control dimensions just to keep the phenomenon alive, stop.
- Do not turn this into “English CxMP but in another language”.

## Paper identity

None yet.

No fixed RQ, mechanism, or method is registered. The workbench earns promotion only if a simple empirical regularity survives strong baselines and naturally suggests a clearer question than the initial territory.
