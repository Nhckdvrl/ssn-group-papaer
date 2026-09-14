# 2026-09-14 — WALL-B Disagreement Map

**Wall:** Formation / interpretation of inductive bias  
**Mode:** RIVAL-EXPLANATION MAP — **NO CANDIDATE GENERATION**  
**Purpose:** explain why recent possible/impossible-language results appear contradictory, which scientific quantities are actually being measured, which rival explanations are already mature, and what remains unresolved after importing the older human-learning / cultural-transmission literature.

---

# 0. The first correction: there is not one disagreement

The 2024–2026 literature is easy to summarize badly as:

> Paper A: LMs prefer possible languages.  
> Paper B: LMs do not.  
> Paper C: they prefer subtly plausible languages.  
> Therefore results are inconsistent.

That summary collapses at least **four inferential levels**:

1. **Construct validity:** does the manipulation actually isolate the intended possible/implausible distinction?
2. **Individual learner preference:** given matched evidence, does the learner prefer/acquire one structure more readily?
3. **Cause of preference:** if a preference exists, what produces it — linguistic constraint, generic simplicity/frequency, information locality, semantic similarity, prior experience, etc.?
4. **Link to human typology/cognition:** why would an LM learning difference bear on human acquisition or on which languages are attested after cultural transmission?

Different papers attack different levels. A result can be correct at Level 2 and still fail to justify a Level-4 claim.

This is the main organizing insight of the map.

---

# 1. Level 0 — What is the scientific target?

There are at least three targets that are often rhetorically collapsed:

### T0-A — Formal human-language possibility

A computational characterization of languages that a typically developing human can acquire.

This is the strongest Chomskyan / possible-vs-impossible target.

### T0-B — Typological plausibility

Why some structural patterns are common and others rare/unattested across natural languages.

This target includes statistical universals such as word-order harmony and can be driven by domain-general cognitive/processing/cultural pressures rather than a hard possible/impossible boundary.

### T0-C — Human acquisition behavior

Which structures children/adults learn, regularize, innovate, or fail to acquire under specified input.

T0-B and T0-C can be related without implying T0-A. A learning preference aligned with a typological universal is not automatically evidence for a hard boundary on possible human grammar.

**State update:** much of the current “LLM inductive bias” debate becomes clearer once these targets are kept separate.

---

# 2. Level 1 — Construct validity of the language contrast

## Evidence chain

### Kallini et al. — broad impossible-language contrast

ACL 2024 Best, _Mission: Impossible Language Models_.

The study constructs transformed languages intended to violate properties of human language and asks whether GPT-2 learns them less readily than English.

**Scientific move:** turn a sweeping learnability claim into a direct training comparison.

**Strength:** establishes the experimental program.

**Weakness exposed later:** “impossible” transformations can differ from English along dimensions other than the theoretical human-language distinction.

---

### Hunter 2025 — the contrast itself does not instantiate the central theoretical comparison

Hunter argues that the most important Kallini comparison contains a confound and does not compare a constituency-based language against a clean non-constituency counterpart in the way required by the theoretical inference.

**Implication:** a learning difference is uninterpretable if the counterfactual language differs in uncontrolled structural/computational properties.

This is not an effect-size dispute. It attacks the mapping:

> dataset label “impossible” → theoretical construct “impossible human language”.

---

### Xu et al. TACL 2026 — move closer to the plausibility boundary

Rather than maximally strange perturbations, this study creates highly naturalistic counterfactual English/Japanese systems around typological word-order universals. The implausible systems remain structured and learnable and differ in subtle typological plausibility.

Models learn the subtly implausible systems more slowly, while some final metrics converge.

**Implication:** reducing construct distance can recover a preference, but now the claim is correspondingly narrower:

> typologically aligned learning preference,

not necessarily

> hard human possible/impossible boundary.

---

## Level-1 conclusion

The field has learned that **“impossible language” cannot be used as a primitive experimental category**.

A scientifically valid comparison needs to specify what structural property is changed while matching generic difficulty as closely as possible.

But even a perfect Level-1 contrast would not settle Levels 2–4.

---

# 3. Level 2 — Does an individual learner exhibit the relevant preference?

## Human evidence predates the LLM debate

### Culbertson / Newport lineage — harmony is a genuine human learning bias

Artificial-language experiments show that:

- adults exhibit preferences for harmonic word-order systems;
- young children show stronger harmonic regularization;
- children can innovate harmonic orders even from consistently non-harmonic input;
- French- and Hebrew-speaking learners also show harmony preferences despite substantial experience with non-harmonic native-language structures.

These results weaken a simple “participants reproduce English word order” explanation.

### But the human bias is conditional, not one abstract scalar

Wang, Kirby & Culbertson (Language 2025/2026) find that cross-category harmony depends on **semantic similarity**: verb–adposition harmony appears robust, whereas verb–adjective harmony emerges when adjectives are active/verb-like but not when they are stative/less verb-like.

Thus even in humans:

> harmony bias ≠ unconditional abstract head/dependent preference.

The bias depends on similarity/representation of the categories being aligned.

---

## LLM evidence

### Kallini et al. 2024

Find a relative learnability disadvantage for selected impossible languages.

### Ziv, Lan & Chemla EACL 2026

Using the same broad training-curve methodology across more natural languages and perturbation functions, find that GPT-2 usually learns each natural language and impossible counterpart equally easily and that there is no systematic aggregate separation.

### Xu et al. TACL 2026

Using much more tightly matched typological counterfactuals, find a subtle but consistent **learning-speed** disadvantage for implausible systems, with some final performance measures later converging.

---

## Level-2 conclusion

The mature claim is not:

> “LMs do / do not possess human-like bias.”

It is at least:

> **preferences are dimension-specific, observable-specific, and trajectory-sensitive.**

A difference in learning speed can coexist with similar endpoint performance. A broad impossible-language transformation can show no separation while a tightly targeted typological contrast shows one.

This is not necessarily contradictory once the scientific quantities are separated.

---

# 4. Level 3 — What causes the observed preference?

This is where the literature is genuinely plural. At least five explanation classes are already serious.

---

## R1 — Language-specific / structurally specialized bias

### Claim family

Human learners possess constraints/preferences specifically tuned to the kinds of hierarchical structures found in natural language; an adequate cognitive model should reproduce them.

### Evidence it explains

- child innovation of harmonic structure despite consistently non-harmonic input;
- classic poverty-of-stimulus arguments;
- critical-period and developmental phenomena;
- potential LM differences on carefully defined possible/impossible language pairs.

### Evidence it does **not uniquely explain**

Human harmony preferences can also emerge from domain-general simplicity/similarity/frequency mechanisms. LMs can display typologically aligned preferences without possessing the same human developmental machinery.

### Current ownership

Very mature linguistic/cognitive debate. BBS 2026 commentaries explicitly continue it.

---

## R2 — Generic simplicity / complexity bias

### Claim family

The learner prefers descriptions/rules that are simpler under its representation. “Impossible” languages may be difficult because the transformations are more complex, random, or less compressible, not because they violate human-specific linguistic constraints.

### Evidence

- Bowers & Mitchell 2026 explicitly argue difficult impossible languages are simply more complex/random while many impossible languages are learned as easily as attested languages.
- Simplicity-based artificial-language accounts have long explained regularization and harmony-like preferences.

### Important limitation

“Simplicity” is representation-dependent. A structure is only simple relative to the learner’s hypothesis language / representation.

Therefore this explanation can silently relocate the original inductive-bias question:

> why does the learner represent hypothesis A more simply than B?

### Current ownership

Classic MDL/Bayesian/cultural-learning territory; generic “simplicity explains LM preference” is not fresh.

---

## R3 — Frequency / replication dynamics

### Claim family

Some apparent abstract structural preferences can arise from distributional asymmetries and generic replication rather than an explicit structural constraint.

### Strong modern example

Mansfield & Krapp, Cognitive Science 2025, _A Simple Explanation for Harmonic Word Order_:

- harmonic order emerges because the most frequent word class gravitates to an edge under a simple phrasal replication-with-modification process;
- the model is compatible with prior artificial-language harmony experiments;
- it can capture competition between harmony and locality;
- it avoids positing an innate head-dependent ordering rule.

### Why this matters for the disagreement map

A human behavior aligned with typology can be genuine **and still not identify the abstract cognitive rule originally proposed to explain it**.

This is a direct warning against reading an LM learning preference as evidence for a matching linguistic primitive.

### Current ownership

Active language-evolution / cognitive modeling program.

---

## R4 — Information / dependency locality and processing efficiency

### Claim family

Natural-language structure is shaped by pressure to keep strongly related / predictive elements local, reducing memory and processing costs.

### Evidence

- extensive cross-linguistic word-order work from Futrell, Gibson, Levy and others;
- dependency locality predicts typological and usage preferences;
- CoNLL 2026 impossible-language paper finds grammatical-sensitivity degradation mediated by **information locality**;
- 2026 _Language Re-generation_ reports reconstruction difficulty tracking locality disruption and a tendency to recover structures with shorter dependencies.

### Why this matters

An LM may prefer a typologically plausible system because that system is computationally local/easy for the architecture, not because it instantiates a human-specific grammar prior.

This can still be scientifically important: it supplies a **functional explanation** for a typological tendency.

### Current ownership

Very active. Generic “information locality explains impossible-language learnability” is already being pursued directly in 2026.

---

## R5 — Developmental / acquired prior

### Claim family

A learner’s effective bias is not fixed by architecture; it is shaped by previous learning history and developmental state.

### Human evidence

- children often regularize / innovate structure more strongly than adults;
- harmony preferences differ in strength across development;
- critical-period evidence shows that learning regime changes over the lifespan.

### LM evidence

- formal/synthetic pre-pretraining can install downstream linguistic biases;
- previous training can leave reusable circuitry that affects later natural-language acquisition;
- seed/training trajectories can pass through qualitatively different generalization regimes.

### Consequence

Comparing a mature pretrained LM to a child and calling both “learners” can obscure a fundamental mismatch: their priors are at radically different developmental stages.

### Current ownership

Active in LM inductive-bias and developmental-modeling work. Generic “pretraining changes the bias” is occupied.

---

# 5. Level 4 — How does learner preference become an attested-language pattern?

This is where the LLM literature has rediscovered a much older scientific problem.

## Classic result: greater learnability is not sufficient for a cultural universal

**Rafferty, Griffiths & Ettlinger, Cognition 2013.**

They formally and experimentally demonstrate counterexamples in which a more learnable property does **not** become prevalent under cultural transmission.

Two key reasons:

1. when transmission fails, spontaneous production can favor a different outcome;
2. the number / structure of alternative hypotheses can overwhelm an individual learnability advantage.

Therefore the inference

> A is easier for one learner → A should dominate language typology

is invalid without modeling the full transmission dynamics.

This point is central and predates the LLM debate by over a decade.

---

## Iterated-learning program

Kirby, Smith, Griffiths, Culbertson and collaborators have spent decades studying exactly the map:

> learner prior / bias  
> + transmission bottleneck  
> + production / interaction  
> → cultural language structure.

The key result from this tradition is that the relationship between learner bias and population language structure is **nontrivial**. Language itself adapts to learning/communication pressures across generations.

Hence “LLM learns plausible language slightly faster” is only one component in a much larger causal chain.

---

## CoNLL 2026 Best Paper — return from learnability to production/transmission

Janarthan, Haley & Goldwater explicitly argue that prior sample-efficiency/perplexity comparisons do not explain why a language would be unattested.

They distinguish two linking hypotheses:

1. impossible languages fail because the learner lacks **grammatical sensitivity**;
2. impossible languages fail because of **generative production / transmission deficiency**.

The results diverge:

- grammatical sensitivity degrades gradually and is mediated by information locality;
- long-form generation degrades much more strongly.

This suggests production/transmission as a plausible bridge.

### Crucial historical correction

This is a strong conceptual move **inside the recent LLM literature**, but production/transmission as the missing link from individual bias to population typology is not a new scientific object. Classic iterated-learning work already owns the parent question.

Therefore the obvious successor

> “run iterated learning with impossible-language LMs”

has **low novelty by provenance** even before checking recent LLM cultural-evolution work.

And recent LLM work already explicitly imports iterated-learning/cultural-evolution theory into model-to-model training and LLM populations.

---

# 6. A fifth level that cannot be skipped — LM → human linking

Even if Levels 1–4 were solved inside an LM, a separate question remains:

> Why should the LM’s preference / mechanism / transmission dynamics tell us anything about the human learner?

## Explicit 2026 disagreement

### Kallini & Potts

Propose a phased research program using LMs to investigate possible/impossible-language distinctions and progressively build linking hypotheses to human cognition.

### Futrell & Mahowald

Defend LMs as productive model systems / scientific tools without claiming they simply are humans.

### Bowers & Mitchell

Argue impossible-language studies instead show that LMs often lack the human biases at issue and that difficult perturbations reflect generic complexity/randomness.

### McDermott-Hinman & Feiman

Highlight properties children exhibit that current LMs do not: innovating beyond input statistics, developmental trajectories, critical periods.

### Resnik and neighboring commentary

Questions whether “model system” is the right relation at all across levels of explanation.

---

## Level-5 conclusion

No scalar behavioral correlation closes the linking gap.

At minimum, a linking argument may need to specify which properties must be shared:

- hypothesis space / representation;
- data regime;
- learning objective;
- learning trajectory;
- resource constraint;
- developmental stage;
- production/transmission process;
- or the exact causal mechanism.

The answer may differ by scientific claim.

---

# 7. Evidence matrix

Legend: **✓** directly bears on explanation; **~** compatible but not diagnostic; **×** creates tension / fails to explain; blank = not aimed at that level.

| Evidence | language-specific structural bias | generic simplicity/complexity | frequency/replication | locality/efficiency | developmental/acquired prior | transmission/population |
|---|---:|---:|---:|---:|---:|---:|
| Kallini ACL24 learning disadvantage | ~ | ~ |  | ~ | ~ |  |
| Hunter CL25 confound critique | × for strong inference | ✓ as alternative concern |  | ~ |  |  |
| Ziv et al. EACL26 no broad separation | × for broad scalar bias | ✓ compatible |  | ✓ compatible | ~ |  |
| Xu et al. TACL26 subtle typological slowdown | ~ | ✓ compatible | ~ | ✓ compatible | ~ |  |
| Human child harmony / innovation | ✓ compatible | ✓ compatible | ✓ compatible | ~ | ✓ | ~ |
| French/Hebrew harmony learners | ✓ / domain-general bias compatible | ✓ | ✓ | ~ | ✓ |  |
| Wang/Kirby/Culbertson semantic conditioning | × for pure abstract harmony scalar | ✓ | ✓ | ~ | ✓ |  |
| Mansfield/Krapp frequency model | × for necessity of explicit harmony rule | ✓ | **✓** | ✓ interaction |  | ✓ compatible |
| CoNLL26 grammatical sensitivity | ~ | ~ |  | **✓** | ~ |  |
| CoNLL26 long-length generation failure |  | ~ |  | ~ | ~ | **✓ candidate link** |
| Rafferty et al. 2013 cultural counterexamples |  |  | ✓ |  |  | **× to direct learnability→universal inference** |
| iterated-learning tradition |  | ✓ | ✓ | ~ | ✓ | **✓** |
| critical-period / child innovation evidence | ✓ compatible | ~ | ~ | ~ | **✓** | ✓ |

### Main lesson of the matrix

Almost none of the central empirical results uniquely selects one explanation.

The strongest evidence usually identifies **a level of the causal chain**, not a unique theory of the whole chain.

---

# 8. What is actually unresolved after importing the older literature?

Several seemingly novel questions disappear once the mature human/cultural-learning literature is remembered.

## NOT unresolved / already mature

### “Does individual learnability automatically explain typological universals?”

**No.** Explicitly answered negatively by Rafferty et al. 2013 and the larger cultural-evolution program.

### “Could cultural transmission amplify learner bias?”

**Yes.** Classic iterated-learning theory.

### “Could a domain-general simplicity bias create linguistic regularity?”

**Yes.** Longstanding Bayesian/MDL/artificial-language tradition.

### “Could word-order harmony have a non-language-specific explanation?”

**Yes.** Multiple mature accounts: simplicity, frequency/replication, dependency/information locality, semantic similarity-conditioned cognitive biases.

### “Do LMs show one universal possible-language preference?”

**No stable law currently supports that broad formulation.** Results depend on construction and observable.

---

## Still genuinely unresolved at the standing-problem level

### U1 — What is the right **factorization of linguistic naturalness**?

“Possible / impossible” and even “typologically plausible / implausible” are too coarse as scientific quantities.

Current evidence points to multiple partially independent factors:

- information locality;
- compressibility / simplicity;
- category similarity;
- hierarchical structure;
- production robustness;
- developmental accessibility;
- language-specific constraints.

It is not known whether these reduce to a small set of general pressures or whether different universals arise from different mechanisms.

**Important:** this is a broad theory problem, not yet a paper-sized RQ.

---

### U2 — Which learner preferences are **mechanistically the same** across humans and LMs?

Behavioral alignment on a typological preference does not tell us whether the two learners share:

- the same representation;
- the same optimization pressure;
- the same development;
- or merely the same solution because the linguistic environment makes it broadly efficient.

Again, this is a linking-hypothesis problem, not “compare humans and LLMs on another effect.”

---

### U3 — Which level of the learning trajectory is causally relevant to language evolution?

TACL 2026 finds slower learning but some endpoint convergence. Human child/adult differences show developmental timing matters. Cultural transmission depends on what is **produced during learning**, not just final asymptotic competence.

The mapping from learning-curve shape to transmission dynamics is scientifically important, but classic cultural-evolution theory already tells us not to equate them naively.

What remains unknown is not “does learning speed matter?” but which trajectory properties survive realistic transmission/use processes.

---

### U4 — The same typological tendency can be supported by several causal stories that make different counterfactual predictions

Word-order harmony is a concrete example:

- abstract structural harmony bias;
- simplicity/compressibility;
- frequency-based replication;
- locality;
- semantic similarity-conditioned generalization.

Several can reproduce observed preferences.

This is a **mature explanation-identification problem**.

However, the human-language literature is already actively attacking it; it is not an empty NLP niche waiting for an LM intervention.

---

### U5 — No universal LM→human linking rule is likely to exist

A model can be useful for one scientific inference (e.g. existence of a learnability pressure) while invalid for another (e.g. developmental timing or critical-period mechanism).

The linking hypothesis may need to be **claim-specific** rather than “LMs are / are not human-like.”

This remains an important meta-scientific issue, but not automatically a candidate generator.

---

# 9. Owner-density / search-headroom diagnosis

This map materially changes our excitement about WALL-B.

## What looked exciting before the map

> ACL24 Best claim → critique → opposite EACL26 result → TACL26 partial recovery → CoNLL26 observable rewrite.

This looked like a fresh contradiction with obvious room.

## What the deeper ancestry shows

The disagreement is scientifically real, but many of its seemingly fresh “solutions” are old, mature research programs:

- learnability→typology gap: cultural evolution / iterated learning;
- simplicity: MDL/Bayesian/artificial-language learning;
- harmony: decades of acquisition + typology + functional explanation;
- locality: active efficiency program;
- human linking: active BBS 2026 dispute;
- LM cultural transmission: already active;
- locality-based reconstruction: already appearing in 2026.

Therefore **WALL-B has high scientific pressure but lower immediate novelty headroom than Dossier II initially suggested**.

This is exactly why we had to do the disagreement map before generating a candidate.

---

# 10. Updated WALL-B state

## What we now believe

1. There is no clean binary “human-like inductive bias” quantity.
2. Linguistic naturalness is multidimensional.
3. Learning-curve differences, grammatical sensitivity, generation quality, transmission stability and typological attestation are different quantities.
4. Generic cognitive/processing pressures can generate typologically aligned behavior without a language-specific primitive.
5. Individual learnability does not directly imply population prevalence.
6. LM→human evidence requires a claim-specific linking hypothesis.
7. Much of this intellectual territory predates LLMs and is currently highly active.

## Status

**WALL-B remains a PRIMARY standing problem.**

But candidate generation from the broad possible/impossible-language parent remains **OFF**.

The wall is valuable as a source of scientific taste and evidence standards; it is not currently a clean unoccupied project parent.

---

# 11. Searcher lesson

This exercise demonstrates why the repository needed persistent research state rather than paper-gap search.

If we had stopped at the 2026 frontier, an LLM searcher would almost inevitably propose:

> “test whether generation/transmission rather than perplexity explains impossible-language non-attestation.”

That sounds excellent because CoNLL 2026 just exposed the gap.

But the older literature immediately changes the judgment:

> **learnability is insufficient for cultural universals, and transmission dynamics are the missing causal layer, has been a mature scientific point for more than a decade.**

The right response is not to salvage by adding an LLM, iterated chain, causal intervention, or new language.

It is to update our scientific worldview and keep searching.

---

# 12. Current decision

**No candidate. No L-series. No K-series. No pilot.**

The first deep wall investigation did its job: it converted an exciting 2026 contradiction into a much more accurate map of a mature, crowded scientific program.

Next action should therefore **not** be to force a WALL-B RQ.

Return to the standing-problem portfolio with the new evidence:

- WALL-B: scientifically mature but immediate descendants crowded;
- WALL-A: strong evidence-standard role but generic methodology crowded;
- WALL-C: deep but theory/owner dense;
- WALL-D: coherent theory, somewhat lower owner density, but requires more research intimacy.

The next search move should be to inspect whether **WALL-D contains an analogous older disagreement that changes its apparent headroom**, or whether a different standing problem outside the four deserves immersion.
