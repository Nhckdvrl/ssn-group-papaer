# Top-Conference Alignment Standard

**Target venue family:** ACL / EMNLP / NAACL Main  
**Aspirational bar:** Outstanding Paper / Best Paper / Best Theme Paper-level scientific identity  
**Last updated:** 2026-09-07

> This repository does **not** use the current good candidates as the quality benchmark.
>
> L02/L03/L04 are only the best surviving local candidates so far.
>
> Every candidate must be judged against strong ACL/EMNLP/NAACL Main papers, especially Outstanding/Best papers, at every stage.

---

## 1. What “alignment” means

Alignment is not:
- copying a topic;
- imitating a method;
- citing an Outstanding Paper in the introduction;
- having many experiments;
- using an LLM;
- sounding ambitious.

Alignment means the proposed paper should be comparable to strong Main / Outstanding work along the **load-bearing dimensions of the paper**.

For every serious candidate, explicitly compare:

1. **RQ scale**
2. **Naturalness / importance of the object**
3. **Scientific tension before experiments**
4. **Data and identification strength**
5. **Novelty of the full paper identity**
6. **Decisiveness of the experiment**
7. **C1→C2→C3 structure**
8. **Breadth without padding**
9. **Consequence for NLP**
10. **Clarity / reviewer compressibility**
11. **Research-space robustness** — does the topic open a moderate/large scientific space rather than depend on one fragile effect?

A candidate is not GOOD merely because all five internal gates are technically YES. It must also pass a **top-conference alignment audit**.

---

## 2. Current Outstanding/Best anchors

The purpose of these anchors is not to force every project into one paper shape. They demonstrate the range of identities that receive top recognition.

### ACL 2026 Outstanding — Systematicity between Forms and Meanings across Languages Supports Efficient Communication

Osmelak, Xu, Hahn, McCurdy.  
https://aclanthology.org/2026.acl-long.1340/

What to learn:
- asks about a durable language-science object, not a benchmark cell;
- connects a broad scientific hypothesis to measurable cross-linguistic evidence;
- contribution is a substantive scientific conclusion, not “a model gets X%”;
- new methodology matters because it discriminates between meaningful accounts.

Alignment lesson:
> a paper may be linguistic/scientific if the object is natural, the hypothesis is substantive, and the evidence changes a broader conclusion.

### EMNLP 2025 Outstanding — Generative or Discriminative? Revisiting Text Classification in the Era of Transformers

Kasa et al.  
https://aclanthology.org/2025.emnlp-main.486/

What to learn:
- revisits a classic, extremely mature NLP problem;
- the topic is not new, but the **modern regime changes the scientific comparison**;
- does not rely on one surprising failure;
- compares multiple dimensions such as accuracy, sample efficiency, calibration, robustness, and practical constraints;
- ends in an actionable conclusion about when each modeling paradigm is preferable.

Alignment lesson:
> Old Problem / New Method can be Outstanding-level when it revisits a load-bearing modeling choice and produces a broad, robust decision map.

### EMNLP 2025 Outstanding — Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps

Tutek et al.  
https://aclanthology.org/2025.emnlp-main.504/

What to learn:
- the paper is organized around a hard-to-measure scientific construct: faithfulness;
- proposes a scientific operation/intervention that makes the quantity measurable;
- does not merely benchmark CoT quality;
- method is valuable because it changes what evidence can be obtained.

Alignment lesson:
> a new scientific operation can support an Outstanding paper when it turns an ambiguous construct into a decisively testable question.

### EMNLP 2025 Outstanding — Causal Interventions Reveal Shared Structure Across English Filler–Gap Constructions

Boguraev, Potts, Mahowald.  
https://aclanthology.org/2025.emnlp-main.1271/

What to learn:
- known linguistic phenomena are acceptable;
- novelty comes from a new causal/mechanistic adjudication and a new scientific conclusion;
- the paper uses model analysis to push theory rather than just probe competence.

Alignment lesson:
> ingredients may be old; the decisive scientific relation and evidence can still create a new paper identity.

### ACL 2025 Outstanding — Rethinking the Role of Prompting Strategies in LLM Test-Time Scaling

Liu et al.  
https://aclanthology.org/2025.acl-long.1356/

What to learn:
- directly re-examines an established modern practice;
- frames a broad modeling assumption rather than a tiny prompt trick;
- uses a principled theoretical perspective to explain when complex strategies matter.

Alignment lesson:
> a methodology paper should overturn, validate, or condition an established assumption, not merely report another technique.

### ACL 2025 Best — Language Models Resist Alignment: Evidence From Data Compression

Ji et al.  
https://aclanthology.org/2025.acl-long.1141/

What to learn:
- tackles a broad current scientific problem;
- introduces an explanatory lens and evidence that support a memorable central claim;
- paper identity is much larger than a benchmark improvement.

Alignment lesson:
> Best-paper-level identity usually has a simple, memorable scientific claim that reorganizes how the reader interprets a broad phenomenon.

---

## 3. Mandatory alignment audit for every candidate

Before promotion to good/, write:

### A. Closest high-level reference papers

At least **3 concrete ACL/EMNLP/NAACL Main papers**, preferably including:
- at least one Outstanding/Best/Theme paper;
- at least one paper with a similar **paper identity**, not merely similar topic;
- at least one paper from a different topic that illustrates the desired scientific shape if necessary.

### B. Dimension-by-dimension comparison

| Dimension | Reference-paper bar | Our candidate | Verdict |
|---|---|---|---|
| RQ scale | | | PASS / WEAK / FAIL |
| Natural object | | | |
| Scientific tension | | | |
| Data / gold | | | |
| Identification / decisiveness | | | |
| Paper-level novelty | | | |
| C1→C2→C3 | | | |
| Consequence | | | |
| Breadth / generality | | | |
| Plain-language identity | | | |

A candidate with one serious FAIL does not enter good/.

### C. Outstanding-level reviewer test

Ask:

> If this result were strong and clean, would an ACL/EMNLP/NAACL Main reviewer see it as a **scientific or methodological contribution of independent interest**, or merely a competent study of a narrow cell?

If the second:
> KILL / KEEP SEARCHING.

### D. Scale test

Compare the proposed title/RQ with actual Main/Outstanding titles.

If our title naturally sounds like:
- “Can model X distinguish label A/B on dataset D?”
- “An evaluation of LLMs on rare phenomenon Y”
- “A benchmark for exact subcase Z”
- “Improving metric M by N%”

while the paper has no broader scientific consequence, it is below the target bar.

---

## 4. Alignment must happen at every stage

### Search stage
Use top-conference papers as generators for **question shape**, natural object, unresolved uncertainty, and paper identity.

### Candidate stage
Do a reference-paper comparison before calling a lead serious.

### Data stage
Ask whether the data/gold are as trustworthy and decisive as the evidence used in strong Main papers.

### Novelty stage
Judge whether our full story would feel like a new paper beside the closest Main work, not merely whether exact wording is absent.

### Pilot stage
Design the smallest experiment that can decide the scientific question, not merely demonstrate an effect.

### Full-paper stage
Require C1→C2→C3 and a consequence that changes:
- modeling;
- evaluation;
- task definition;
- theory;
- methodology;
- or an established NLP conclusion.

### Mainline approval
Re-run alignment against the newest ACL/EMNLP/NAACL Main/Outstanding papers available at that date.

---

## 5. Hard anti-lowering rule

Never say:

> “This new candidate only needs to be as strong as L02/L03/L04.”

Correct statement:

> “L02/L03/L04 themselves must keep being audited against ACL/EMNLP/NAACL Main and Outstanding-level work, and every new candidate must meet the same external bar.”

The local scoreboard is not the scientific standard.

---

## 6. What a strong candidate should feel like

A strong candidate should support a one-paragraph pitch of this form:

> NLP has long assumed / measured / modeled **X**.  
> There are at least two credible accounts, **A** and **B**, and existing evidence cannot decisively separate them because **Y**.  
> We now have natural data / a new scientific operation that makes **Z** identifiable.  
> Whichever account wins, the result changes how we understand / model / evaluate **X**.

That is much closer to the desired Main/Outstanding identity than:

> “We found an untouched dataset cell where LLMs might fail.”


---

## 7. Research-space robustness — hard rule (2026-09-08)

Prefer a **research program with a crisp center** over an untouched one-dimensional effect. A serious candidate should normally expose at least 2–4 natural questions before seeing target-model results: a core comparison/causal question, a mechanism or attribution question, a principled boundary/heterogeneity question, and a modeling/evaluation consequence.

KILL / DO NOT PROMOTE when the topic effectively has this shape:

> If intervention X causes effect Y, we have a paper; if not, the entire topic disappears.

This is stronger than ordinary null-result robustness. A preservation/equivalence result only counts when it answers an existing consequential question; it must not be used to rescue a tiny search cell.

Before promotion, answer:
1. What is the broader scientific object or decision problem?
2. What are at least three natural questions inside this space?
3. If the first planned effect is absent, which questions remain scientifically live?
4. Can a mechanism, boundary, or decision-map paper still emerge without inventing post-hoc hypotheses?
5. Is the scope comparable to strong ACL/EMNLP/NAACL Main work without becoming vague?

Conference-alignment examples:
- EMNLP 2025 Outstanding, *Generative or Discriminative?*, maps accuracy, sample efficiency, calibration, robustness, ordinality, latency, and data constraints rather than betting on one metric.
- ACL 2025 Outstanding, *Rethinking the Role of Prompting Strategies in LLM Test-Time Scaling*, connects a broad empirical regularity to theory, prediction, and improved methods.
- ACL 2026 Outstanding, *CAR-bench*, treats real-world agent uncertainty as a multi-faceted reliability problem spanning consistency, limit-awareness, disambiguation, tool use, and policy adherence.
