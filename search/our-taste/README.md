# Our Taste Search

> **v3 说明（2026-09-30）：** 本通道的内容（强基线优先、痛点先于修复、利用我们的真实优势、从谱系学研究动作）继续有效。变化在于**执行方式**，统一服从 [`../README.md`](../README.md)：
> - §7 的“顶会天花板”检查在 **workbench 驻留中用证据回答**，不再作为桌面门槛；“有人做过 / 已成 program”不是放弃理由。
> - 方法可以从驻留第一周开始，只要它针对强基线上**真实出现**的痛点（顶会本方向的接收论文大多是方法型，见诊断 §4.2）。
> - 输出统一为 territory 卡（热度卡 / 谱系卡 / 形态卡 / 立足点卡 / 压力清单），不再用 §8 的旧清单。
> - 当前扫描：[`TERRITORY_SCAN_2026-09-30.md`](TERRITORY_SCAN_2026-09-30.md)。

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

## 7. Top-conference-scale ceiling

Baseline-first does not mean “any baseline with a weakness is worth months of work”.

Before opening a workbench, require plausible headroom for a strong ICML/ICLR/NeurIPS/CVPR/ACL-family main-track contribution.

Ask:

- does the baseline failure expose a **general bottleneck / wrong assumption / design principle**, or only a local bug?
- if we fully diagnose the bottleneck, is there a natural path to either a broader scientific conclusion or a method that would matter across multiple regimes?
- can we validate the eventual story with independent axes (models, tasks, scales, perturbations, mechanisms, downstream outcomes), rather than one benchmark?
- is the work likely to remain important if the exact baseline is superseded?
- what strong current papers would reviewers mentally compare us against, and is the potential contribution comparable in conceptual scale?
- if the method gain were zero, could the analysis still teach the field something consequential? If the analysis were removed, could the method still represent a meaningful technical step? Ideally at least one side has real scale.

Reject territories whose optimistic endpoint is merely:
- “+X points on one benchmark”;
- “a new module for one model family”;
- “a failure on one slice”;
- “A+B has not been tried”;
- “we can publish the artifact because no one measured this exact thing”.

The desired unit is:

> **strong baseline → consequential failure / changed premise → broad bottleneck → evidence → minimal intervention or durable scientific conclusion**

## 8. Search output for this lane

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
