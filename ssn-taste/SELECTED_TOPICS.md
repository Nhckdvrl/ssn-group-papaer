# Selected Topics — Sasano-Taste Search

Started: 2026-09-16

Purpose: record only questions that survive a real nearest-prior novelty check and are worth concrete pilot design or execution.

## Admission rule

A topic can enter this file when all four are true:

1. **Worth asking:** the question is understandable without elaborate framing and there is a natural reason a reviewer would want to know the answer.
2. **Real difference:** recent nearest prior work does not already answer the same question; the distinction is substantive rather than merely “newer model / larger model / another benchmark”.
3. **Correct scientific width:** the parent RQ, claim scope, and related-work neighborhood are calibrated against nearby ACL / EMNLP / NAACL Main papers and Sasano-approved work. The idea must not survive merely because it is phrased unusually narrowly, nor be inflated into a broader parent that the experiments cannot support.
4. **Testable:** there is a realistic clean experiment that can reduce uncertainty without requiring unreasonable data construction or compute.

Mechanistic depth, surprising pilot results, broad cross-model robustness, and complex methods are valuable when they help, but they are not admission requirements.

For each selected topic, record the question, scientific pressure, nearest-prior gap, **scope audit against Main-conference/Sasano anchors**, minimal experiment, expected resource cost, Sasano-fit rationale, and remaining risks.

---

## Current selections

### S02 — AI Rewrite ≠ Semantic Change

**Status:** SELECTED / PILOT-AUTHORIZED  
**Detailed record:** [`selected/S02_AI_REWRITE_FALSE_SEMANTIC_CHANGE.md`](selected/S02_AI_REWRITE_FALSE_SEMANTIC_CHANGE.md)

**RQ:** Can meaning-preserving LLM rewriting make lexical-semantic-change methods report semantic change even when the underlying word meanings have not changed? More generally, which LSC measurements remain invariant under meaning-preserving AI rewriting, and which mistake AI-induced contextual redistribution for semantic change?

**Scientific pressure:** Diachronic LSC methods infer change from distributions of word usages. Prior work already shows that genre, register, corpus imbalance, contextual variance, and topic changes can create false semantic-change signals; that generic vulnerability is **not** the novelty. The changed premise is that human text is now increasingly passed through an LLM rewriting operator that can systematically alter lexical choice, collocations, syntax, and context distribution while preserving intended meaning. This new real-world production process creates a paired counterfactual intervention that ordinary observational diachronic corpora do not provide.

**Nearest-prior position:**

- prior LSC work owns the fact that context/genre shifts can cause false positives;
- recent ACL/LREC work owns the facts that AI-generated/AI-assisted text is increasingly prevalent and that LLM use changes lexical/contextual distributions;
- the selected question is the intersection: **hold intended meaning fixed by construction, apply a realistic AI rewrite, and causally test which semantic-change measurements remain invariant.**

The contribution must therefore never be framed as “distribution shift can fool LSC” or “LLMs change writing style”. It is a measurement-validity study under a genuinely changed corpus-generation regime.

**Why exploratory, not gambling:** No result direction is required. Robustness, selective sensitivity, or broad sensitivity are all scientifically interpretable. Semantic-preservation checks and perturbation decompositions are controls/analyses, not life-or-death gates.

**Minimal pilot:** paired original→LLM-rewrite passages from one existing corpus; a few hundred frequent target lemmas; 2–3 representative LSC method families; cheap semantic-preservation filtering plus a small manual audit; one genuine semantic-change positive control; compare real-change sensitivity against rewrite invariance. No large model training and no new benchmark are required.

**Sasano fit:** natural one-sentence puzzle; changed real-world premise; question first/method second; clean identifying intervention; claims can stay narrow; result does not need to be surprising; experimentally cheap enough to test before scaling.

**Main risk:** reviewer compression to “another genre/context-shift robustness study.” The detailed record therefore defines the scientific object as **semantic-change measurement invariance under a newly common meaning-preserving AI rewrite operator**, not generic corpus bias.

---

_S01 was previously demoted after Main-scope / Related-Work width auditing and is recorded in `FAILED_TOPICS.md` as F06._
