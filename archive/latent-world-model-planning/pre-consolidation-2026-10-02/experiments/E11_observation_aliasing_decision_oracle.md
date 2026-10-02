# E11 — Is there actionable ambiguity after available history?

- **状态：** PLANNED / CHEAP CONDITIONAL PILOT
- **对应：** I07 / M1
- **优先级：** 低于 E14/E13；不训练新方法。
- **问题：** 在 compact image-goal planning中，给定 planner实际可用的 finite history 后，是否仍存在多个 hidden states / parameters 与几乎相同 observation history相容、但要求不同 candidate action？

## 为什么收窄

以下 broad claims 已有很强近邻：
- FIRM-WM：goal-comparable config vs dynamic fiber；
- UWM-JEPA：belief-space latent；
- Flow Equivariant WM：partial-observation structured memory；
- Physically Viable WM：same-looking scene + latent physics可产生不同 intervention outcomes；
- Branch-JEPA：point successor无法保留multiple futures；
- Action-Sufficient Goal Representation：value/goal sufficiency不等于action sufficiency。

所以 **“same image can hide different state”不是新发现。**

## Phase 0 — sanity only

先做 velocity/momentum alias：
- same rendered frame；
- different qvel；
- same candidate action set；
- execute in simulator。

如果 best-action / utility vector几乎不变，说明这个 substrate不适合继续。

## Phase 1 — history test

对每个 alias pair：
- 1 frame；
- 2–3 frame history；
- native model history length；
- history中 observation/action全部按 deployment接口给足。

比较：
- pair可区分度；
- candidate best-action flip；
- oracle regret。

若 short history稳定消除 ambiguity：
> 结论只是 history sufficiency，**STOP**。不造 belief architecture。

## Phase 2 — irreducible / long-lived ambiguity

只有 Phase 1 仍有 action-level ambiguity才尝试：
- hidden friction / mass / contact mode；
- occluded dynamic state；
- stochastic branch；
- latent regime whose effect appears only after intervention。

要求：
- matched visible history；
- same goal/query；
- same candidate set；
- hidden variable确实改变 environment utility。

## Baseline planner consequence

在存在 oracle action flip 的 pairs上：
- native LeWM/JEPA-WM selection；
- candidate regret；
- confidence/uncertainty（如果有）；
- closed-loop recovery。

只有 baseline **实际混淆**，才 E12。

## Controls

- fully observed / privileged hidden variable → regret应显著下降；
- random nuisance variable不影响dynamics → 不应制造action flip；
- task/goal change不能和hidden-state change混；
- render差异用 image metric + human-inspected sample验证；
- simulator privileged state只用于 construction/oracle，不进 baseline input。

## Gate

- action flip率/utility gap接近0 → I07 park；
- finite history解掉 → I07降为已知 history sufficiency，不做方法；
- history后仍有稳定 action-relevant ambiguity，但 baseline自己有 robust strategy → 不做；
- history后 ambiguity + baseline regret + second hidden-factor family复现 → E12。

## 结果
未运行。
