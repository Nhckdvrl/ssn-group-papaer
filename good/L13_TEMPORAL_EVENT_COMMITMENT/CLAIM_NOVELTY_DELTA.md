# L13 — Claim Novelty Delta #1

Date: 2026-09-11. Triggered by the rule **"a selected topic is not grandfathered into
novelty; every materially new claim must re-earn the right to be the paper."**

**Process failure being corrected.** L13 was authorized on one claim and has mutated
three times since, with no novelty reset at any of them. Evidence kept accumulating
against a claim that had already been replaced. This is the L12 failure mode.

| # | trigger | what changed |
|---|---|---|
| M1 | **E05** — a non-generative temporal demand moves commitment ≤0.07 | the mechanism moved from *representation* to *generation*. C4 (internal coupling) **rejected** |
| M2 | **E16** — removing the ordering requirement leaves the failure intact | the object moved from *timeline construction* to *event enumeration* |
| M3 | **E17** — `by_the_time` (veridical) is extracted at ~1.00, same as `before_post` | the claim narrowed to *the finite subordinate clause is extracted regardless of what the subordinator licenses* |

---

## 1. Old claim → new claim

**Authorized claim (dead).**
> Temporal-relation computation causally contaminates event-realization commitment; the
> two computations are coupled inside the model.

Rejected by E05. Nothing of the internal-coupling mechanism survives.

**Current claim.**
> A model applies a semantic licensing constraint at the **judgement** interface and not
> at the **extraction** interface, on the same sentence and the same proposition; the
> emitted structure then overwrites the model's own belief and a downstream reader's.
> Demonstrated on non-veridical `before`-clauses; marked (modal / aspectual)
> non-veridicality is respected at both interfaces.

## 2. Direct owners, and what each owns

| prior work | owns | leaves open |
|---|---|---|
| HANS / shallow-heuristic lineage; "models ignore negation" | models substitute surface/syntactic cues for semantic operators, **failing the judgement** | the case where the judgement is **correct** and only the generated structure is wrong |
| *Can LLMs Judge Better Than They Generate?* (arXiv 2606.28050, 2026) | generate-vs-judge **asymmetry** as a general phenomenon, with mechanistic analysis | asymmetry on a **specific semantic constraint**, selectively, and the belief-overwrite direction |
| Event-extraction hallucination surveys (e.g. arXiv 2512.19537) | hallucination under weak constraints; extraction driven by surface cues over the schema | licensing by a lexical operator; a matched judgement baseline showing the knowledge is present |
| MAVEN-FACT; veridicality NLI | labelling event factuality | any manipulation of the interface at which the label is demanded |
| Self-conditioning / context-bias literature | models are swayed by their own prior output | that what they are swayed by is a *semantically unlicensed* item they themselves produced |

## 3. Strongest reviewer compression

> **Prior Work A + B + C = our paper**
> A = models substitute surface cues for semantic operators (HANS lineage)
> B = generate/judge asymmetry (2606.28050)
> C = models are conditioned by their own generations
> → "shallow syntactic heuristic in generation, on before-clauses, plus known
> self-conditioning."

**What survives after A + B + C are removed:**

1. **Direction.** A predicts the judgement fails too. Here the judgement is *correct*
   (P(ND) 0.54–0.66) and only the extraction is wrong (0.87–1.00). A shallow-heuristic
   account does not predict a correct judgement.
2. **Selectivity.** The extraction interface *does* consult lexical marking — `could`
   moves Qwen3-8B from 1.00 to 0.04. So it is not "generation is dumber"; it is
   "generation consults marking but not connective-level licensing."
3. **Overwrite.** The unlicensed item the model produced then changes its own answer
   (+0.06 to +0.38) and a downstream reader's (+0.12 to +0.24 on natural sentences).
   B and C do not predict that the *specific unlicensed* item is what propagates while
   matched controls do not.

That residue is a real scientific statement. The question is whether it is **wide**
enough.

## 4. Main-level width test

Stated at full strength, the claim is:

> *Semantic licensing is interface-dependent, and the weaker interface's output wins.*

Support for that statement is currently **one semantic operator** — the non-veridicality
of `before`. Everything else in the study (9 conditions, 11 checkpoints, natural
replication, propagation, failed repairs) deepens that one operator rather than widening
the statement.

Under the width rule, "A did X, B did Y, C did Z, nobody did XYZ on our data" triggers
HOLD. We are not quite there — the residue in §3 is more than an intersection — but the
general claim is carried by a single construction, and the narrow claim
("LLMs mishandle `before`-clauses during event extraction") is not Main-level on its own.

## 5. Verdict

> **HOLD — RECONSTRUCT around the interface, not around `before`.**

Not KILL: the RQ is good, the evidence is strong and largely unowned in its direction,
and the residue in §3 is a genuine scientific statement. But the current paper identity
is one construction deep, and no amount of further `before` evidence widens it.

## 6. Hard stop (in force now)

Until this delta is resolved, the following are **forbidden**:
- more model families, more scale points, more checkpoints;
- more conditions on `before`;
- any confirmation or robustness run on existing claims;
- writing the paper.

Permitted: the minimum diagnostic that decides whether the interface claim generalizes.

## 7. The one experiment that resolves it

The interface claim predicts that **other semantic operators** should also be dropped at
the extraction interface while surviving at the judgement interface. That is directly
testable with the machinery already built, on the same enumeration probe:

| operator | test item | what survival means |
|---|---|---|
| negation | *The portal did not close.* | already hinted: Llama emits explicitly negated events at 0.89 in `before_cancel` |
| attribution / reported speech | *A colleague claimed the portal had closed.* | |
| counterfactual | *Had the portal closed, Maya would have missed the deadline.* | |
| modality | *The portal may have closed.* | `before_modal` suggests marking IS respected — a predicted negative |
| conditional | *If the portal closed, Maya missed the deadline.* | |

Outcomes:
- **Several operators dropped at extraction while judged correctly** → the identity becomes
  *which semantic operators survive the extraction interface*, which is wide, natural, and
  not owned. E01–E18 become its first and deepest operator. → re-audit and promote.
- **Only `before` behaves this way** → the interface claim is false as a generalization.
  The honest paper is then the narrow one, which does not clear Main on its own →
  RECONSTRUCT or KILL.

This is the only work authorized on L13 right now.
