# Our Taste Search

**Role:** identify high-value problem territories under **our own broad taste**.

Unlike `../sasano-taste/`, this lane is deliberately permissive:

- hot or non-hot;
- NLP or non-NLP;
- analysis or method;
- benchmark-oriented or science-oriented;
- training or training-free;
- agents, RL, multimodal, VLA, robotics, CV, graphics, AI4Science, AI4Quant, systems, etc.

We do not inherit Sasano's preference against fast-moving company-scale races. We only require that the project is scientifically/technically strong enough to justify the investment.

## 1. Baseline-first, not idea-first

The default entry into a new area is:

> **clone a strong baseline / parent paper → reproduce it faithfully → make the baseline as strong and understood as possible → then explore**

A weak baseline creates fake research problems.

Before inventing a module/loss:
- reproduce the strongest reasonable recipe;
- inspect implementation details;
- try current training/evaluation best practices;
- understand where the baseline is genuinely strong and genuinely weak;
- compare to current public SOTA where feasible.

The ResNet Strikes Back pattern is canonical: improving the training procedure of a supposedly old baseline can erase a large part of the apparent architecture story.

## 2. Do not expect the first idea to survive unchanged

If the exact idea we propose on day one:
- works immediately,
- needs no conceptual change,
- and becomes the submitted paper unchanged,

that should be treated as unusual rather than the normal research process.

The search stage therefore selects **where to explore**, not a perfect final invention.

## 3. Prefer territories with informative gradients

A good territory gives us many ways to learn:

- strong baseline vs weak baseline;
- failure slices;
- scale / budget / recipe sensitivity;
- checkpoint or training-stage dynamics;
- ablations;
- perturbations / counterfactuals;
- representation or routing diagnostics;
- error cases;
- data regime changes;
- latency / memory / compute tradeoffs;
- controlled negative results.

A dramatic failure can be more useful than a small success.

> If a seemingly minor change drops performance by 10 points, first ask what hidden dependency was exposed. The reverse direction may reveal the actual improvement lever.

## 4. Problem pain should precede the fix

For method-shaped work:

> **real failure → diagnosed bottleneck → controllable action → simple intervention → downstream gain**

Do not start with a favorite loss/module and then search for a benchmark where it helps.

A method is strongest when it feels like the smallest natural response to something the workbench has already made hard to ignore.

## 5. Trendy work is allowed, but exploit our actual edge

If entering a crowded frontier, ask what makes us competitive:
- unusual open artifacts;
- a reproducible strong baseline others neglect;
- better instrumentation;
- a tractable scale where the key effect already exists;
- a cross-domain concept that creates a genuinely new action surface;
- a fast experimental loop.

“Hot” is not a negative signal here; **no leverage** is.

## 6. Paper genealogy is a source of search moves

When reading strong work, learn how the idea grew:

- Did a strong baseline expose that the field was optimizing the wrong thing?
- Did an accepted explanation fail under one diagnostic?
- Did authors decompose an entangled design space?
- Did a representation become the actual bottleneck only after scale increased?
- Did a surprising negative result reveal an asymmetric learning signal?
- Did a method become obvious only after a failure mode was localized?

Imitate the **reasoning move**, not the surface method.

## 7. Search output for this lane

Before opening a workbench, provide:

- important territory / task;
- strongest parent implementation or baseline;
- why we have a realistic experimental foothold;
- known pain points / suspicious assumptions;
- 3–6 analysis directions;
- compute/data constraints;
- likely failure modes of the research project itself.

Do not require an expected result, method, or title.

Then hand it to `../../workbench/`.
