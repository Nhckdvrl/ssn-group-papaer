# Success–Failure Asymmetry — Related Work and Novelty

## 1. Parent ownership

### ImplicitMemBench / ACL 2026
Owns:
- implicit behavioral memory as an evaluation object;
- preference vs inhibition constructs;
- the dramatic 75.0% vs 17.6% asymmetry across 17 models;
- first-attempt behavioral scoring after interference.

Source: https://aclanthology.org/2026.acl-long.1301/

We cannot claim that inhibition is difficult or that positive and negative adaptation differ.

### Experience-learning / reflection work
ExpeL, Reflexion, BenchTrace, and later self-improvement work study how agents use success/failure trajectories, reflection, and lessons to improve future behavior.

These own much of:
- failure reflection;
- failure→future avoidance as a system capability;
- methods that explicitly store or generate lessons.

They do not by themselves answer why success and failure produce a matched asymmetry in base experiential adaptation.

### Negative instruction / suppression work
Recent mechanistic work studies why explicit “do not X” constraints can fail or backfire. This occupies explicit negative prompting, not necessarily implicit experiential failure.

It becomes one plausible account for the final action-selection stage.

## 2. Surviving scientific axis

The new paper-level question is:

> **At which stage does the already-established success/failure asymmetry arise?**

The decisive decomposition is:

`experience -> outcome memory -> causal attribution -> policy knowledge -> actual behavior`

and the central comparison is matched positive vs negative experience.

## 3. Reviewer compression

### Attack A
> “ImplicitMemBench plus more diagnostics.”

Fatal unless stage diagnostics lead to a causal repair experiment and a conclusion about the bottleneck.

### Attack B
> “BenchTrace / reflection for another benchmark.”

BenchTrace asks whether failure can be reflected upon and avoided. This candidate compares **positive and negative experience under matched conditions** and locates the source of the asymmetry.

### Attack C
> “Negative prompting is hard.”

If positive replacement completely explains the effect, this neighboring literature becomes a strong account, but the paper still must show how experiential failure is transformed into an action policy. If the entire phenomenon is identical to known explicit-negative-instruction failure with no new mechanism, KILL.

## 4. Exact novelty claim

Potentially defensible:

> “The success–failure adaptation asymmetry in LLMs arises primarily at outcome encoding / causal attribution / policy formation / action inhibition, and a targeted representation of failed experience selectively repairs the bottleneck.”

## 5. Kill-level collision

KILL if prior work already uses matched positive/negative experience, decomposes the same four stages, and causally identifies/repairs the source of inhibition failure.

Also KILL if after matching feedback and action structure there is no robust positive-vs-negative asymmetry left.

## 6. Current verdict

**NOVELTY: PASS, current audit.**

The phenomenon itself is fully owned by ImplicitMemBench; only the mechanistic asymmetry paper is available.