# Official Correction — Related Work and Paper-Level Novelty

## 1. What prior work owns

Existing work already covers:
- temporal knowledge conflicts;
- document revision histories;
- retraction awareness;
- contradictory evidence retrieval;
- scientific fact extraction;
- dynamic QA / time-aware QA.

Therefore this paper cannot claim that scientific facts change over time or that multiple document versions create conflicts.

## 2. Surviving scientific axis

An official correction is not merely a later document. It is an **editorially adjudicated supersession operation** applied to an earlier scholarly proposition.

The proposed paper asks whether modern scientific NLP systems preserve this update semantics:

`old proposition -> official correction relation -> current proposition`

This differs from generic conflict resolution because the relation specifies which proposition is superseded.

## 3. Closest reviewer attacks

### Attack A
> “Temporal QA on corrected papers.”

Rebuttal requires matched controls showing that the model must use the official correction relation, not just choose the newest sentence.

### Attack B
> “Retraction/correction detection.”

Detection asks whether a paper has been corrected/retracted. Here the output is the **current proposition** and the consequence for scientific NLP.

### Attack C
> “Version-history reconciliation.”

Generic version work compares document states. This candidate is restricted to externally adjudicated scholarly updates with proposition-level gold and an explicit scientific-record consequence.

## 4. What we can and cannot claim

Potentially defensible:
- official correction relations are/are not reliably respected by LLM scientific readers;
- original-document salience can/cannot override adjudicated supersession;
- scientific QA/summarization needs explicit versioned-proposition handling under identifiable correction types.

Forbidden:
- “papers can be corrected”;
- “LLMs struggle with temporal conflict”;
- “newer information should be preferred”;
- “we introduce a correction dataset” as the primary contribution.

## 5. Exact paper-level novelty condition

The paper is new only if it jointly establishes:
1. direct official old→new proposition gold;
2. controlled original/correction evidence conditions;
3. an analysis of whether update semantics are preserved;
4. boundaries/mechanism beyond generic recency;
5. a consequence for scientific NLP task representation/evaluation.

## 6. Kill-level collision

KILL if a prior modern paper already evaluates LLMs on official publisher corrections with proposition-level old→new gold and explicitly concludes whether correction/supersession must be represented for scientific QA/summarization/evidence synthesis.

Broad temporal conflict or retraction work alone is not enough.

## 7. Current verdict

**NOVELTY: PASS, current audit.**

The more immediate risk is data yield, not parent collision.