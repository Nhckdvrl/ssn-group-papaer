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

## 0. Venue-scale contract

A workbench is expensive. It should not exist merely because an object is unexplored.

Before substantial compute or long experimental expansion, every workbench must maintain a credible **top-conference ceiling**:

- the local substrate is only an entry point, not the full contribution;
- there is a broader assumption / bottleneck / principle that the workbench could change;
- the strongest plausible outcome would matter beyond one dataset/model/language/game;
- there is enough evidence runway to support a full paper, not one interesting table;
- nearest prior does not already own the broader conclusion.

Write the intended scope as:

> **substrate / local effect → broader object → possible field-level consequence**

This is **not** a fixed paper claim. It is a ceiling check.

A workbench should be **demoted back to library knowledge or archived** if exploration shows that the broader object collapses and the remaining result is only:
- a model-specific quirk;
- a narrow benchmark issue;
- a one-domain follow-up;
- a small engineering patch with no transferable principle;
- or an observation whose importance depends on exaggerated framing.

Conversely, a very specific phenomenon is allowed when it reveals something general. Do not confuse surface breadth with scientific scale.

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

## 2. Exploration is a portfolio search, not a lead chase

The main failure mode of an LLM research agent is **serial local search**:

> notice one anomaly → explain it → run one decisive test → narrow the story → rescue it → kill it → declare the territory exhausted.

This can obey every local “anti-optimization” rule while still being bad research.

A workbench must therefore separate **reconnaissance** from **deep dive**.

### 2.1 Reconnaissance comes before commitment

After baseline residency, do not immediately promote the first interesting failure into the workbench story.

First build a **pressure map** of the territory:
- where strong baselines disagree;
- where performance changes sharply under small changes;
- where old methods stop transferring;
- where different metrics disagree;
- where scaling/data/recipe changes the conclusion;
- where implementation choices produce qualitatively different behavior;
- where success cases are unexpectedly informative;
- which claimed bottlenecks disappear under stronger baselines.

The goal is not exhaustive Cartesian sweeps. It is to sample enough independent parts of the space to know whether the first anomaly is actually important.

### 2.2 Leads must compete

Before a lead receives a deep sequence of experiments, compare it against at least a few **independent competing leads / explanations** from the same territory.

A good lead should win attention because it has some combination of:
- a large and reproducible gradient;
- a broad scientific consequence;
- a clean changed premise;
- multiple ways to test it;
- distance from nearest-prior ownership;
- realistic confirmation under our compute.

Do not deep-dive merely because the lead appeared first.

### 2.3 Depth is earned

A lead may enter deep investigation only when at least one is true:
- it recurs across more than one meaningful slice / system / regime;
- a small controlled perturbation produces a large unexplained change;
- it contradicts a strong current baseline or accepted explanation;
- it exposes a bottleneck with an obvious downstream consequence;
- it survives a first trivial-explanation test and still has novelty room.

Otherwise keep it as a note in the pressure map.

### 2.4 Null results kill explanations, not territories

A failed experiment normally means:

> this explanation / slice / instrument is weak.

It does **not** by itself mean:

> the territory is exhausted.

Freezing a whole workbench requires **coverage evidence**:
- the strongest practical baseline has been understood;
- several independent pressure axes have been sampled;
- the major competing lineages / nearest priors have been mapped;
- the obvious high-information gradients are either explained, owned, or absent;
- remaining directions are genuinely local / low-ceiling rather than merely untested.

If these conditions are not met, return to reconnaissance instead of declaring the territory dead.

### 2.5 Two-demotion reset rule

If two consecutive leads are demoted because of trivial controls, nearest-prior ownership, or story qualification, **stop the local sequence**.

Do not run a third “last rescue” experiment on the same narrative.

Return to:
- the field map;
- strong-baseline success/failure trajectories;
- other unresolved disagreements;
- another lineage or substrate inside the territory.

This reset is mandatory unless the new experiment tests a genuinely different scientific object.

### 2.6 Success cases are evidence too

Do not inspect only failures.

Ask:
- why does the strongest baseline succeed where older systems failed?
- which old bottleneck disappeared?
- what design choice became unnecessary?
- what capability emerged without the method the field thought was required?
- what does a strong negative result invalidate?

A strong baseline that destroys an old problem can be a better source of research questions than another failure slice.

### 2.7 Default loop

The default workbench loop is therefore:

> **field map → baseline residency → broad reconnaissance → competing leads → earned deep dive → update problem representation → candidate (maybe)**

Inside a deep dive:

> **inspect → perturb → test alternatives → update → re-check prior → decide whether the lead still deserves depth**

Not:

> **first anomaly → serial experiments until paper or death.**

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

### Active survivor

- `video-world-model-temporal-interfaces/` — **our-taste; ACTIVE, conditional (phase 1 passed 2026-09-29)**. Chunk-onset control deafness reproduced on three independent systems (MG2, minWM, HY-WorldPlay), arising at causalization; human key-press replay shows lost seam-onset presses on two systems, and a context-anchored chunk-overlap rollout repairs control on both. Open: quality/cost of the repair, sample size, a 4th system, and the training-side cause. Continue only under the hard venue-scale gate in its README.
- `scoped-context-state/` — **sasano-taste; ACTIVE, exploratory**. Investigates whether LLMs can enter, maintain, switch, and exit temporary contextual states; agent execution is explicitly research-navigation-first and must kill/pivot rather than locally optimize a weak story.
- `realtime-agent-capability-transition/` — **our-taste; CLOSED (drained 2026-09-30)**. E04 finished: spoken-style user input alone costs nothing for a fixed text agent (retail 47.8→43.5 p=0.79, airline 40→44 p=0.77); τ-Voice gap = spoken entity capture + backbone; frontier dual systems at text parity. Assets: 20 GB public τ-Voice trajectories + scripts.
- `mechanism-population-dynamics/` — **our-taste / model-science; ACTIVE, exploratory**. Treats mechanisms and their developmental trajectories as population variables over stochastic training histories; starts from PolyPythias + established causal mechanisms, with mandatory checkpoint-integrity audit and OLMo-2 external-validity branch.
- `realtime-computation-boundaries/` — **our-taste; FROZEN (2026-09-30)**. Residency on Realtime-Venus + FDB-v3: the fast/slow channel is transparent once crossed; the lost capability sits in the fast model's handoff decision (owned: SALMONN-duo, cascade deferral). The follow-up lead (full-duplex mode removes abstention: same weights 92%→3%) was demoted by its pre-registered test: one honesty instruction restores it (39/40). Cross-domain channel/staleness levers are owned (Latent Bridge, Think@5Hz, input prediction). Knowledge asset; see its README §Navigation-2 for reopen conditions.

### Frozen / demoted / knowledge assets

- `model-diffing-measurement/` — **DEMOTED 2026-09-29; knowledge asset**. Direct ownership collision: Kempf et al. 2026 already systematize simple-LLM vs SAE model diffing with generalization/interestingness/abstraction criteria; together with ADL and Diff Mining, the original comparative-access mother question is too occupied.
- `shape-olmo/` — paused knowledge asset; explored Shape/hybrid hypotheses did not survive controls.
- `hybrid-adaptation/` — **demoted**; current abstraction is too close to existing recurrent-state adaptation and KV-vs-state causal work.
- `ai4quant/` — **demoted**; both current territories fail the workbench ceiling gate in their present form.
- `moe-route-preference/` — **closed active line / knowledge asset**; broader routing-utility/misrouting conclusion is now owned by stronger nearest prior.
- `npc-deception-investigability/` — **demoted**; coherent game-AI object, but current top-conference ceiling is too game-specific.
- `npc-persona-behavior-grounding/` — **frozen**; broader proxy-vs-causal-control object is plausible, but one PCSP substrate is insufficient. Requires an independent second substrate before reopening.

**Current policy:** do not keep a workbench active simply because code, data, or a cheap next experiment exists. If the top-conference ceiling is not credible, preserve the knowledge and stop execution.
