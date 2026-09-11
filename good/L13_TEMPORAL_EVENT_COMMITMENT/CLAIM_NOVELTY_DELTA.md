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

---

# Delta #3 — E20 resolves it: the extraction interface runs a surface test (2026-09-11)

Licensing × surface form of the target clause, crossed. 100 scenarios, 3 models,
same judgement probe and same enumeration probe as everywhere else.

| condition | gold | surface of the E-clause | surface predicts | capability predicts | judge (acc) | **extract** |
|---|---|---|---|---|---|---|
| `dn_true_that` *It is true that E* | YES | clean | extract | extract | 1.00 | 0.98 / 1.00 / 1.00 |
| `dn_not_true` *It is not true that E* | **NO** | **clean** | extract ✗ | drop | .89–1.00 | **0.42 / 0.85 / 0.88** |
| `dn_deny` *A colleague denied that E* | ND | clean | extract ✗ | drop | .44–.96 | **0.99 / 1.00 / 1.00** |
| `dn_doubtful` *It is doubtful that E* | ND | clean | extract ✗ | drop | .16–.70 | 0.98 / 0.98 / 0.70 |
| `dn_false_that_not` *It is false that E-did-not* | **YES** | **negated** | drop ✗ | extract | .74–1.00 | **0.75 / 0.40 / 0.42** |
| `dn_not_fail` *S did not fail to VP* | **YES** | **negated** | drop ✗ | extract | .53–.99 | **0.10 / 0.40 / 0.69** |

## The two decisive contrasts

**Same gold NO, judged correctly, extraction differs by where the negation sits:**

| | gold | E-clause surface | extracted |
|---|---|---|---|
| `op_negation` *Maya did not submit …* | NO | negated | **0.00 / 0.01 / 0.01** |
| `dn_not_true` *It is not true that Maya submitted …* | NO | clean | **0.42 / 0.85 / 0.88** |

**Same gold YES, judged correctly, extraction differs by where the negation sits:**

| | gold | E-clause surface | extracted |
|---|---|---|---|
| `dn_true_that` *It is true that Maya submitted …* | YES | clean | **0.98 / 1.00 / 1.00** |
| `dn_not_fail` *Maya did not fail to submit …* | YES | negated | **0.10 / 0.40 / 0.69** |

Qwen3-8B judges `dn_not_fail` correctly 0.99 of the time and then **drops 90% of events
the passage guarantees happened.** No capability account predicts that direction.

## Verdict on Delta #1 and #2

> **PASS, conditional on the claim being written as the mechanism.**

The identity is no longer "models mistake suspended content for fact" (CogNarr owns that
for the attribution category) and is not "models mishandle negation" (the negation
literature owns that at the judgement interface, where our models are correct). It is:

> **At the extraction interface a model tests the surface form of the clause — is it a
> non-negated finite past clause? — instead of the operator that licenses it. It
> therefore extracts events the text denies and drops events the text guarantees, on
> sentences it judges correctly; and the unlicensed items it emits then overwrite its own
> and a downstream reader's belief.**

- **Width**: 13 conditions across temporal non-veridicality, attribution, conditionals,
  epistemic possibility and negation placement, with licensing crossed against surface
  form. Not one construction.
- **Compression**: CogNarr + negation literature + self-conditioning does not predict a
  *guaranteed* event being dropped. That cell is the paper.
- **Direction**: both predicted failure directions are observed, which is what separates a
  mechanism from a capability gap.

## Honest weaknesses in this delta

1. `dn_doubtful` is not a dissociation for Gemma — its judgement accuracy is 0.16, so
   that cell is a comprehension failure, not an interface failure.
2. `dn_not_fail` judgement is 0.53 for Llama; that cell is only clean for Qwen3-8B (0.99)
   and Gemma (0.89).
3. `dn_false_that_not` is weak for Qwen3-8B (0.75 extracted, i.e. mostly not dropped), so
   the negated-surface effect is frame-dependent within a model.
4. Three models, one language, and the `did not fail to` frame is not frequent English.

## Hard stop status

Delta #1's stop is **lifted for claim-relevant work only**. Still forbidden without a new
delta: model zoos, scale ladders, and confirmation runs on the old `before`-only claim.
The paper, if written, is the interface mechanism with `before` as its deepest case.

---

# Delta #4 — the Delta #3 PASS is withdrawn (2026-09-11)

I graded Delta #3 PASS on the strength of the risky prediction. Re-reading it against
the width and compression tests, that grade was too generous. Downgrading to **HOLD**.

## The compression I missed

`dn_not_fail` is *"Maya did not fail to submit the application"* — a **double negation**.
"LLMs are bad at double negation" is an established finding; the literature on negation
systematicity reports exactly that models can prefer negation over double negation. So
the headline cell compresses to:

> "Known double-negation weakness, plus known generate/judge asymmetry, showing up in an
> extraction task."

My defence was that the *judgement* is correct (0.99), which the double-negation account
does not predict. That defence is real but thin: it rests on one frame, in one model, and
the same cell is weak for Llama (judgement 0.53) and for Qwen3-8B in the other negated
frame (0.75 extracted, i.e. barely dropped).

**Judge Circuits (arXiv 2605.16023, 2026)** also lands nearby: a judgement signal computed
in the shared trunk, mapped through fragile output-formatting layers, giving systematically
different answers under different output formats. "The interface changes the answer" is
therefore not unowned either.

## What the idea actually is, stripped of dressing

> Models use surface form instead of the semantic operator when producing structured
> output.

That is the shallow-heuristic parent — one of the most crowded in NLP. Under the width
test it reads as *this task + these three models + our instantiation metric*. **HOLD.**

## The asset I have been under-using

The most distinctive thing in E01–E20 is not the surface test. It is a **causal
direction**, and it comes from two experiments I have been treating as minor:

- **E13 / E18** — what the model extracted **overwrites its own judgement** (+0.06 to
  +0.38 on its own answer, +0.12 to +0.24 downstream on natural sentences).
- **E10** — forcing the judgement to run **first** does not fix the extraction. The
  status-first pipeline nearly eliminates instantiation of explicitly negated events
  (0.35–0.90 → 0.00–0.08) and does nothing for unresolved ones.

Together: **the model's own correct judgement has no causal influence on what it
extracts, while what it extracts has strong causal influence on its judgement, and the
arrow reverses only when the surface carries the information.** The asymmetry survived a
deliberate attempt to reverse it.

## Candidate idea (NOT approved — it needs its own kill pass)

> **A model's semantically licensed judgement is causally downstream of its
> surface-driven event registry, and cannot write back to it.**

Different object from the crowded parents:
- shallow heuristics say the model computes the wrong thing — here it computes the right
  thing and then does not get to use it;
- generate/judge asymmetry and Judge Circuits say the interface changes the answer — they
  do not claim a **fixed causal direction between two of the model's own computations**,
  nor that an intervention designed to reverse it fails;
- CogNarr reports a capability gap on one category, not a direction.

It also reframes everything we have: `before`, attribution, conditionals, possibility and
the surface test all become *evidence about what the registry is keyed on*, rather than
the claim itself.

## The decisive pilot, and it is not prompt engineering

Prompt ordering (E10) is a weak test of causal direction. The real test is
representational, and it is cheap on open-weight models:

1. Take the hidden state at the point where the model has computed the judgement
   correctly (the `NOT DETERMINED` decision) and patch it into the extraction run.
   Direction predicts: **no transfer** — extraction still emits the event.
2. Take the hidden state from the extraction run and patch it into the judgement run.
   Direction predicts: **transfer** — the judgement flips toward YES.
3. Run both on a matched pair where the surface *does* carry the information
   (`op_negation`), where the arrow is known to reverse behaviourally. Direction predicts
   both transfers succeed there.

If patching is asymmetric in (1)/(2) and symmetric in (3), the causal direction is a
measured fact and the idea is ours. If both directions transfer, there is no privileged
registry, the idea is false, and L13's honest ceiling is the narrow surface-test paper —
which does not clear Main on its own.

**Status: HOLD. No further evidence accumulation on the surface-test claim.** This
patching pilot is the only authorized work, and it must be followed by a fresh novelty
delta before anything is written.

## A caution on my own reasoning here

This candidate has the same *shape* as the idea that rescued L12 (a causal-direction
claim built on an existing behavioural asset), and I may be pattern-matching to a story
that worked rather than to the evidence. The patching pilot is designed to be able to
kill it; if it does, L13 should go to RECONSTRUCT or KILL rather than be rescued a third
time.
