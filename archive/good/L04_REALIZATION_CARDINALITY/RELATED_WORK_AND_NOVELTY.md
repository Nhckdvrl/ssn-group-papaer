# L04 — Related Work and Paper-Level Novelty

**Candidate:** Morphological Inflection Has Realization Cardinality  
**Novelty risk:** HIGH

---

## 1. What the classical literature already owns

Defectivity and overabundance are established morphological phenomena.

Therefore the paper cannot claim:
- paradigm cells are always single-valued and nobody noticed;
- zero-form cells are newly discovered;
- multi-form cells are newly discovered;
- sets of forms are a new representational idea.

The only viable contribution is a scientific test of whether **canonicalization changes the conclusions of computational morphology evaluation**.

---

## 2. ACL 2020 — full paradigm completion is already owned

Jin et al., ACL 2020  
**“Unsupervised Morphological Paradigm Completion.”**  
https://aclanthology.org/2020.acl-main.598/

Owns:
- generating full paradigms from raw text + lemma lists;
- paradigm size discovery;
- broad multilingual paradigm completion.

Therefore L04 cannot say:
- LLMs first make full-paradigm generation possible;
- modern generation first lets us discover whether a paradigm cell exists.

---

## 3. TACL 2022 — the canonicalization restriction is explicitly known

Goldman & Tsarfaty, TACL 2022  
**“Morphology Without Borders: Clause-Level Morphology.”**  
https://aclanthology.org/2022.tacl-1.83/

This is the most important classical-modern collision pressure.

The paper explicitly states that:
- overabundance means several forms may occupy one paradigm cell;
- their construction still uses only one canonical form per cell;
- a richer extension could accommodate sets of forms.

Therefore L04 cannot claim:
- single-target canonicalization is an unnoticed problem;
- set-valued morphology is a novel task formulation.

### Surviving axis

TACL 2022 identifies the restriction but does not, in the current audit, own the decisive question:

> **Does canonical single-target evaluation preserve model/generalization conclusions when zero/one/many realization cardinality is restored using independent gold?**

That measurement-validity question is the only defensible parent.

---

## 4. Eesthetic / Paralex 2024 — the data representation is already owned

Beniamine et al., LREC-COLING 2024  
**“Eesthetic: A Paralex Lexicon of Estonian Paradigms.”**  
https://aclanthology.org/2024.lrec-main.491/

Owns:
- a large machine-readable Estonian paradigm lexicon;
- explicit annotation of non-canonical morphology;
- overabundance and defectiveness metadata.

Paralex standard:
https://www.paralex-standard.org/standard/

The standard explicitly requires:
- defective forms to have rows rather than being silently absent;
- DEF to mark defectivity;
- MISSING to distinguish incomplete source/transcription data;
- overabundant forms to be represented in multiple rows with overabundance tags.

Therefore L04 cannot claim the data ontology as a contribution.

The resource is valuable precisely because the gold exists **independently** of the proposed modeling experiment.

---

## 5. 2026 collision pressure — overabundance already changes paradigm predictability

Bouton & Bonami (Journal of Language Modelling, 2026)  
**“The implicative structure of overabundant paradigms.”**  
https://jlm.ipipan.waw.pl/index.php/JLM/article/view/460

This paper is especially important because it goes beyond simply saying overabundance exists. It shows that standard quantitative approaches to paradigm-cell predictability do not naturally accommodate overabundance and develops measures for overabundant paradigms.

### What this means for L04

It strengthens the motivation that canonicalization can matter scientifically.

But it also raises the novelty bar:
- L04 cannot claim “overabundance affects paradigm predictability” as new;
- L04 must specifically show what happens to **computational inflection evaluation and model/generalization conclusions** under zero/one/many gold.

If the analysis drifts into morphology-theory predictability alone, the 2026 paper becomes a serious collision.

---

## 6. What part of the full paper-level story is actually new?

The candidate must own all of the following as one coherent story:

1. use independently annotated zero/one/many realization gold;
2. evaluate modern inflection systems under conventional canonical scoring and relation-aware scoring;
3. explicitly test preservation/equivalence versus change in scientific conclusions;
4. decompose cardinality knowledge from form realization;
5. determine whether the conventional task abstraction is safe, unsafe, or conditionally safe.

The novelty is the **measurement conclusion**, not the ontology.

---

## 7. Reviewer compression

### Strongest attack

> **“This is TACL 2022’s proposed sets-of-forms extension, run on Eesthetic, with defectivity added.”**

### Compression is false only if

The paper is designed around a pre-specified preservation question:

> Do the scientific/model-generalization conclusions produced by canonical inflection evaluation survive when the true zero/one/many relation is restored?

The experiment must compare **conclusions**, not merely absolute error counts.

### Kill-level collision

KILL if a prior paper is found that already:
- evaluates computational inflection models on independently labeled defective + overabundant cells;
- contrasts single-canonical and zero/one/many evaluation;
- reports whether model rankings/generalization conclusions are preserved;
- draws the same task-definition conclusion.

---

## 8. Allowed claims

Potentially defensible if supported:

- “Canonical one-target inflection is empirically safe / unsafe / conditionally safe.”
- “Realization cardinality is a load-bearing intermediate quantity for computational inflection under specified regimes.”
- “Relation-aware evaluation changes the interpretation of morphological generalization.”
- “A preservation result validates canonicalization under explicit conditions.”

---

## 9. Forbidden claims

Do not claim:
- defectivity is new;
- overabundance is new;
- multi-reference morphology is new;
- set-valued cells are new;
- full paradigm completion is new;
- LLMs uniquely enable paradigm-size discovery;
- the paper’s contribution is an Estonian benchmark.

---

## 10. Fresh-search status through 2026-09-07

Current direct audit includes:
- ACL 2020 unsupervised paradigm completion;
- TACL 2022 explicit one-canonical-form restriction and set-valued extension suggestion;
- LREC-COLING 2024 Eesthetic;
- Paralex standard;
- Bouton & Bonami 2026 overabundant paradigm predictability.

No searched paper currently owns the exact **canonical-vs-zero/one/many computational evaluation preservation** story.

This verdict is fragile and must be re-run after the pilot.
