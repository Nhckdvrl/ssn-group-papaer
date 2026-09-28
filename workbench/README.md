# Workbench

This is where research actually **grows**.

A workbench begins with an important territory, not a finished paper idea.

It owns:
- the strongest practical baseline we can reproduce;
- baseline strengthening / recipe checks;
- exploratory analyses;
- failed perturbations;
- successful signals;
- stable observations;
- changing hypotheses;
- local literature / artifact notes needed for this object.

There is intentionally **no top-level `observations/`**. Observations belong to the workbench that produced them.

## 1. Baseline residency comes first

Do not treat “the script runs and roughly matches one reported number” as baseline reproduction.

Before inventing anything, learn the baseline deeply:

- exact code / version / checkpoint / prompt / recipe;
- strongest reasonable configuration;
- current evaluation harness;
- variance / seed behavior;
- performance by slice and regime;
- training / inference curves;
- known implementation artifacts;
- current simple improvements that do not change the scientific object.

The goal is not ritual reproduction. It is to become competent enough that an apparent failure is not just our weak implementation.

Whenever possible, try to **strengthen the baseline first**. A stronger baseline can:
- kill a fake problem;
- expose a narrower real problem;
- reveal where the improvement actually comes from;
- itself become a meaningful technical result.

## 2. Exploration loop

Default loop:

> **reproduce → inspect → perturb → fail/succeed → update understanding → choose next analysis**

Not:

> hypothesis → one decisive experiment → keep/kill paper.

Early workbench experiments are discovery experiments. They may be messy and hypothesis-changing.

Useful things to inspect include:
- failure slices and counterexamples;
- scale / budget / seed / recipe sensitivity;
- stage/checkpoint dynamics;
- ablations and component removal;
- controlled perturbations;
- alternative metrics/readouts;
- data regime changes;
- decoding/inference changes;
- causal interventions where possible;
- latency/memory/compute bottlenecks;
- representation / routing / gradient statistics;
- cases where a “small” change causes a very large drop.

A large negative result is information.

## 3. Failure gradient

After every meaningful failure, ask:

- What assumption did this failure invalidate?
- Did the effect disappear because the phenomenon is false, or because the instrument/regime is wrong?
- What dependency did the model/system unexpectedly rely on?
- What does the failure say about the baseline's true bottleneck?
- Can the direction be inverted into an improvement?
- Does this change which question is worth asking?

Do not merely append “failed” to a log.

## 4. Human in the loop

LLMs can implement many analyses but often will not proactively choose the most revealing one.

Human input should therefore regularly inject:
- a suspicious comparison;
- an alternative explanation;
- a missing baseline;
- a counterexample;
- an analysis suggested by another field;
- a “what happens if we break this?” perturbation.

When no strong insight is available, systematically enumerate reasonable analyses rather than pretending one elegant experiment will settle everything.

The workbench should continuously answer:

> **What did we learn that changes what we should do next?**

## 5. Paper identity is allowed to mutate

The initial intuition is not sacred.

During workbench exploration:
- RQ may change;
- mechanism may disappear;
- method may become unnecessary;
- an unexpected failure may become the central result;
- a supposedly secondary analysis may become the real bottleneck.

Do not protect the original idea by adding increasingly elaborate controls.

## 6. When a method becomes justified

For method-shaped work, require:

> **Failure → Bottleneck → Controllable action → Outcome**

Each arrow needs evidence.

A good diagnostic signal does not automatically imply a good training target, loss, router, controller, or deployed action.

Prefer the simplest intervention that directly attacks the identified bottleneck.

## 7. When to promote to candidate

Promotion happens only when the workbench has naturally produced a paper identity that is clearer than the initial idea.

Typical signs:
- one important empirical pattern keeps surviving;
- strong baseline/simple explanation no longer dissolves it;
- the question can be stated without the entire experimental apparatus;
- related work does not already own the same scientific conclusion;
- the contribution has a plausible confirmation path;
- the story is getting **simpler**, not more conditional.

Until then, remain a workbench.

## Current workbenches

- `shape-olmo/` — paused knowledge asset.
- `hybrid-adaptation/` — exploratory.
- `ai4quant/` — exploratory family.
- `moe-route-preference/` — stable observation, candidate status not earned.
- `modern-guidance/` — **our-taste**, exploratory strong-baseline study of guidance on modern rectified-flow models.
