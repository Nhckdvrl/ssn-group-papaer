# L02 — Related Work and Paper-Level Novelty

> **Final review, 2026-09-08:** [follow-up alignment](literature/FOLLOWUP_ALIGNMENT_20260908.md)
> adds DUST, RefNLI and the UCCA/CLAIRE resource review. The inherited unconditional
> novelty pass is superseded. See the [NO-GO route verdict](RESEARCH_VERDICT.md).

> **2026-09-08 correction:** [Renewed full-text alignment](literature/ALIGNMENT_20260908.md)
> supersedes inherited novelty assertions below. DiscourseEE already permits null slots;
> REGen already studies context-grounded matching and specificity. Generic abstention and
> grounded evaluation are not unoccupied contributions. E000 additionally rejects the
> blanket INI-as-unlicensed-filler mapping. Current novelty is provisional.

**Candidate:** Semantic Role Completion ≠ Referential Commitment  
**Audit principle:** novelty is judged at the level of the **full scientific story**, not by requiring every ingredient to be new.

---

## 1. Literature ownership map

### A. Classical object: null instantiation and implicit arguments

The classical literature already owns the underlying semantic distinction.

Key anchors:

- Ruppenhofer et al. (SemEval 2010), **“SemEval-2010 Task 10: Linking Events and Their Participants in Discourse.”**  
  https://aclanthology.org/S10-1008/
- Petruck (2019), **“Meaning Representation of Null Instantiated Semantic Roles in FrameNet.”**  
  https://aclanthology.org/W19-3313/

These works establish that FrameNet-style null instantiation contains different semantic/pragmatic statuses and that implicit roles can require different treatment.

### What they already own

- null-instantiated semantic roles are real;
- definite/recoverable and indefinite/non-specific omissions are different;
- implicit argument resolution is a legitimate NLP task;
- a pipeline may distinguish status detection from filler resolution.

### Therefore we cannot claim

- DNI/INI is new;
- referential versus non-referential omission is new;
- implicit arguments were previously ignored;
- explicit status classification is a novel representation.

---

## 2. Modern implicit / document-level argument extraction

### Roit et al., ACL 2024
**“Explicating the Implicit: Argument Detection Beyond Sentence Boundaries.”**  
https://aclanthology.org/2024.acl-long.863/

Owns:
- argument detection beyond sentence boundaries;
- passage-level inference;
- reformulating argument detection via textual entailment;
- modern implicit-argument detection without direct supervision.

Does **not currently appear to own**:
- referential-status as the decisive target;
- whether a concrete filler is licensed at all;
- the necessity of status→filler factorization in free-form generation.

### Sharif et al., EMNLP 2024
**“Explicit, Implicit, and Scattered: Revisiting Event Extraction to Capture Complex Arguments.”**  
https://aclanthology.org/2024.emnlp-main.673/

Owns:
- a modern event-extraction corpus with explicit, implicit, and scattered arguments;
- generative extraction for complex argument types;
- the fact that implicit arguments matter at document scale.

Important collision pressure:
- this is already a modern “generative implicit arguments” paper;
- L02 cannot sell itself as “LLMs can extract implicit arguments.”

Surviving distinction:
- DiscourseEE has recoverable implicit arguments and also null slots for absent arguments;
- L02 asks whether **the system should generate a concrete entity at all**, separating semantic role completion from referential commitment.

### Sharif et al., Findings EMNLP 2025
**“REGen: A Reliable Evaluation Framework for Generative Event Argument Extraction.”**  
https://aclanthology.org/2025.findings-emnlp.649/

Owns:
- generative EAE evaluation beyond exact span matching;
- evaluation that better handles semantically valid generated arguments;
- implicit/scattered arguments in generative evaluation.

Collision pressure:
- L02 must not become another “better matching metric for generated arguments.”

Surviving axis:
- REGen asks whether the generated argument is semantically correct;
- L02 asks whether **argument generation itself is licensed**, given a distinct referential-status gold state.

---

## 3. Paper-level novelty claim

The proposed paper does **not** claim a new linguistic distinction. Its paper identity is:

> **Classical implicit-argument systems separated referential-status inference from filler resolution. Modern free-form generative IE can collapse these steps. Is that collapse scientifically valid, or does generation turn semantic role expectation into unsupported entity commitment?**

The new object is therefore the **necessity of the intermediate decision under the modern generation regime**.

### What part of the full paper-level story is actually new?

The candidate must own the combination:

1. old independent gold explicitly distinguishes recoverable versus non-specific omitted roles;
2. modern generative systems are tested under a direct filler-emission formulation;
3. role/type understanding is separately measured from referential commitment;
4. direct generation is compared against explicit status→filler factorization;
5. both preservation and failure lead to a modeling conclusion about whether the classical intermediate state remains load-bearing.

Changing only model family, prompt, or dataset would not be enough.

---

## 4. Reviewer compression test

### Strong attack

> **“This is just SemEval/FrameNet DNI-vs-INI with LLMs.”**

### Compression is false only if

The final paper shows a consequence about **task definition or architecture**, not only competence:

- direct generation and explicit factorization are scientifically compared;
- errors are decomposed into role knowledge versus referential commitment;
- preservation/failure changes how generative implicit-argument extraction should be formulated or evaluated.

### Kill if a reviewer can instead say

> **“Paper X already asks whether modern generative event extraction should abstain from producing a filler when an implicit role is non-referential, using DNI/INI-like gold, and compares direct generation with explicit referential-status factorization.”**

That would be a paper-level parent collision.

---

## 5. Fresh-search status through 2026-09-07

Current search has verified strong adjacent ownership in:

- classical null instantiation;
- passage-level implicit argument detection;
- generative complex event-argument extraction;
- generative EAE evaluation.

No searched 2024–2026 paper has yet been found that owns the **same full necessity / referential-commitment story**.

This is a **survived-current-audit** verdict, not proof of permanent novelty. Re-run the direct collision search:
- before pilot execution;
- after pilot result is known;
- immediately before committing to a mainline.

---

## 6. Claims we may and may not make

### Potentially defensible if supported

- “Referential-status factorization remains load-bearing / becomes unnecessary under specified generative conditions.”
- “Role understanding and concrete referential commitment are empirically separable in generative IE.”
- “Current evaluation can confuse plausible role completion with grounded entity recovery.”
- “A typed abstention/status layer changes scientific conclusions about implicit-argument extraction.”

### Forbidden / already owned

- “We discover DNI vs INI.”
- “We are the first to study implicit arguments with LLMs.”
- “We are the first to do document-level argument extraction.”
- “We are the first to evaluate generative EAE beyond exact match.”
- “Hallucination occurs in event extraction” as the main novelty claim.

---

## 7. Novelty maintenance checklist

Before promotion beyond pilot:

- [ ] Search ACL Anthology / arXiv / OpenReview through 2026 for implicit argument, null instantiation, referential, abstention, generative event argument extraction.
- [ ] Read the closest papers at paper level, not keyword level.
- [ ] Write one exact reviewer-compression sentence for each new neighbor.
- [ ] Confirm no paper already has the same decisive direct-vs-factorized comparison.
- [ ] Keep the title/abstract centered on the modeling assumption, not the old DNI/INI labels.
