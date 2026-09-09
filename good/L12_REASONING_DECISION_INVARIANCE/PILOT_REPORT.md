# L12 First-Round Pilot Report

**Date:** 2026-09-09  
**Verdict:** **CONTINUE-PILOT**

## A. Current RQ

> **Why does reasoning-oriented post-training make decisions dramatically more invariant to presentation, and does the self-generated long reasoning trajectory become the dominant causal controller of the final answer?**

The current working mechanism is **trajectory takeover**, not semantic-context boundary testing.

## B. What prior work owns

**Mind the (DH) Gap!** (ACL 2026 Outstanding) owns the broad risky-choice behavioral contrast between reasoning and conversational models.

**Framing Matters** owns framing sensitivity as an internal representation/intervention problem.

**Reasoning Traces Shape Outputs but Models Won't Say So** owns generic causal evidence that injected reasoning can change outputs.

**How Do Answer Tokens Read Reasoning Traces?** owns answer-to-reasoning self-reading/attention patterns.

Therefore L12 cannot stop at:
- “reasoning models are more rational”;
- frame information is decodable;
- CoT affects answers;
- answer tokens read the trace.

## C. What we tested

- **L12-E01:** parent artifact/stimulus audit.
- **L12-E02:** sibling Instruct-SFT vs Think-SFT behavior on 3 published prospects × gain/loss × both orders.
- **L12-E03:** prompt-state frame recoverability diagnostic.
- **L12-E04:** injected-`</think>` no-reasoning attempt; invalid.
- **L12-E05:** own / empty / opposite-frame natural trajectory forced-readout intervention.
- **L12-E06:** answer-free short arithmetic-prefix intervention.

## D. Established results

### Behavioral transition

| Branch | Valid | Frame consistency | Order consistency | EV-consistent |
|---|---:|---:|---:|---:|
| Instruct-SFT | 240/240 | 0.817 [0.625, 0.958] | 0.783 | 0.508 |
| Think-SFT | 219/240 | 0.992 [0.950, 1.000] | 0.992 | 0.995 |

Think-minus-Instruct frame consistency = **+0.175**, hierarchical-bootstrap 95% CI **[0.025, 0.367]**.

These are **frame-consistency measurements**, not generic task-accuracy scores.

### Prompt information remains available

Frame identity is recoverable through most early/middle Think-SFT layers. With only 12 lexically explicit conditions, this is a routing constraint, not a causal result.

### Natural trajectory strongly controls readout

E05 target-directed A/B margin:

- own natural trace: **+9.34**
- empty trace: **-0.08**
- matched opposite-frame trace: **-9.07**

Own-minus-empty = **+9.42 [8.54, 10.10]**.  
Own-minus-opposite = **+18.41 [17.46, 19.32]**.

### Short arithmetic snippets are insufficient

E06:

- correct-minus-rule-only = **+0.32 [-3.92, 4.33]**
- correct-minus-swapped = **+0.39 [-0.13, 0.96]**

So the E05 effect is not reproduced by a cheap answer-free arithmetic fragment.

## E. Current mechanism picture

The strongest live account is:

> prompt framing remains represented  
> → long natural reasoning transforms the computation  
> → the trajectory becomes the dominant source of final decision control.

But E05 still permits a cheaper explanation:

> the full trace works mainly because its terminal sentence explicitly commits to the answer.

That is the exact unresolved point.

## F. Novelty corridor

The paper is not “Mind the DH Gap + Thought Injection.”

The surviving paper-level identity is:

> established reasoning-induced invariance  
> → preserved prompt information  
> → natural long reasoning acquires causal control of final choice  
> → determine whether that control is distributed through the reasoning process or concentrated in terminal self-commitment  
> → identify the trajectory-built pre-answer decision state.

This remains distinct from generic trace injection and answer-token attention.

## G. Main-level judgment

- **Question scale:** Main-level.
- **Behavioral substrate:** strong and independently established.
- **Own leverage:** strong sibling-branch reproduction + large natural-trace causal readout effect.
- **Main missing claim:** whether trajectory-level control survives terminal-conclusion removal.
- **Mechanism depth:** promising; one decisive experiment short of a credible central mechanism.
- **Mainline:** not yet approved.

## H. Next decisive experiment — L12-E07

Run **Conclusion-Stripped Trajectory Takeover**.

For each natural Think-SFT trace compare:

1. own full;
2. own terminal-conclusion-stripped;
3. matched opposite-frame stripped;
4. empty.

Primary questions:

> Does own-stripped remain strongly target-directed relative to empty?

> Does own-stripped still separate from opposite-stripped?

### Outcome interpretation

- **Yes:** strong evidence that the long reasoning process itself carries causal decision control → run E08.
- **No:** the effect is better described as late self-commitment → reconstruct the mechanism; do not add a defensive rescue battery.

## I. E08 if E07 succeeds

Causally substitute the natural pre-answer state between matched trajectories.

The goal is to establish a **trajectory-built decision state** that transfers choice control without appending donor reasoning text.

## J. Parked experiment

The relevant-vs-redundant context-note boundary scaffold is retained for possible later use, but it is **not a prerequisite, not the current narrative, and not a novelty-defense obligation**.
