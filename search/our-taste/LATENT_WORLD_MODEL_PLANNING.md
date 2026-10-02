# Territory 卡：紧凑潜在世界模型与规划

日期：2026-10-02。通道：our-taste。状态：**PROPOSED / problem-led / literature+code-hardened / execution-ready；不是 candidate。**

工作台：[latent-world-model-planning](../../workbench/latent-world-model-planning/README.md)  
资源：[RESOURCES](../../RESOURCES.md)

**最高层入口：**
- [NOVELTY_GROWTH_RULES](../../workbench/latent-world-model-planning/NOVELTY_GROWTH_RULES.md)
- [FIELD_PROBLEM_MAP_2026](../../workbench/latent-world-model-planning/FIELD_PROBLEM_MAP_2026.md)
- [RESEARCH_PROGRAMS](../../workbench/latent-world-model-planning/RESEARCH_PROGRAMS.md)
- [RESEARCH_MINES](../../workbench/latent-world-model-planning/RESEARCH_MINES.md)

定位：
[PAPER_LINEAGE](../../workbench/latent-world-model-planning/PAPER_LINEAGE.md) ·
[LITERATURE_LEDGER](../../workbench/latent-world-model-planning/LITERATURE_LEDGER.md) ·
[POSITIONING](../../workbench/latent-world-model-planning/POSITIONING.md)

## 1. 选这个 territory 的理由

不是“模型小所以容易发”，而是同时满足：

1. **社区持续关心。** 2025–2026 顶会/强期刊不断出现 latent planning、task-sufficient WM、query sufficiency、data regime、planning geometry、hierarchy、uncertainty等工作。
2. **研究 program 没闭合。** 现有论文常各自给一个答案，但“什么时候哪种 state / data / predictive object / query conditioning / recovery mechanism真正必要”仍没有统一认识。
3. **可做受控实验。** offline data + resettable simulator + candidate-level planner可以做 intervention、oracle replacement、same candidate bank、data-regime controls。
4. **资源匹配。** compact models与大量独立 runs 非常适合多卡弱互联资源；无需多节点预训练。
5. **novelty 可从近邻中生长。** 不要求找没人碰过的词，而是在强 related work之间找 tension / boundary / interaction / mechanism / method。

## 2. 硬规则：不要把 related work 当禁区图

一篇 paper可以占：
> 某个 setting下的一个 atomic claim。

不能因此写：
> 整个母问题都不能做。

例如：
- P94证明 action excitation重要 ≠ “world-model data问题做完了”；
- P38研究 query sufficiency ≠ “task specialization/reuse做完了”；
- FIRM/UWM研究 belief ≠ “partial observability做完了”；
- AdaJEPA研究 adaptation ≠ “world-model trust/recovery做完了”。

详见 `NOVELTY_GROWTH_RULES.md`。

## 3. 五个 research programs

### R1 — Data & Identifiability
**什么经验让 world model真正学会可用于 planning 的 action effects / controllability？**

子方向：
- behavior/route geometry；
- action excitation；
- counterfactual branches；
- active probing；
- failure/recovery data；
- query-aware data acquisition。

当前 seeds：
- I09/E14；
- I12/E16；
- I06/E08–E10 diagnostic。

### R2 — Predictive Abstraction
**world model应该预测什么 future object？**

continuum：

```text
one-step dynamics
→ direct horizon
→ trajectory distribution
→ successor / occupancy
→ macro / hierarchy
→ amortized / hybrid
```

当前 seed：
- I08/E13。

目标不是 winner table，而是 regime law / adaptive predictive object / compute principle。

### R3 — Specialization vs Reuse
**world model要为 query/planner 专门化到什么程度？什么结构应该保持 task-agnostic reusable？**

当前 seed：
- I10/E17：query placement × seen/unseen reuse。

强 anchors：
Value Equivalence、Goal-Aware Prediction、P38、Rank-One Corner、WorldTest、Task-Sufficient WM。

### R4 — State / Belief / Information Gathering
**partial observability / hidden physics 下，正确 internal state 是 memory、belief、multi-future还是主动 probing？**

当前 seed：
- I07/E11。

FIRM/UWM/Branch/PVWM是 program坐标，不是关闭理由。

### R5 — Trust / Repair / Bypass
**world model不可靠时，该采取哪种 recovery action？**

候选：
replan、shorten horizon、more search、feedback、adapt、fallback。

当前 seed：
- I11/E18：failure/reliability signal → recovery-action ranking。

## 4. 第一波实验

仓库规则：**同时真正跑的 scientific pilots ≤ 2**。

### Wave A
- E14（R1）
- E18（R5）

E08可CPU旁路。

### Wave B
- E13（R2）
- E17（R3）

### Conditional
- E11（R4）
- E16（R1）

顺序可被新 evidence改写。

## 5. 什么时候值得把几十张卡铺开

至少出现两项：
- natural effect；
- real decision consequence；
- surprising boundary；
- clean intervention；
- strong nearest baseline gap；
- plausible method lever。

然后才扩：
- train seeds；
- second task structures；
- strongest neighbors；
- data regimes；
- hold-out conditions；
- method ablations。

## 6. 顶会 paper 允许的生长方式

不限制为“failure + loss”：

- new problem/distinction；
- regime law；
- interaction/unification；
- mechanism / identification；
- data principle；
- compute principle；
- specialization/reuse frontier；
- method from diagnosis；
- strong comparative science；
- benchmark/protocol（如果揭示真实缺失能力）。

## 7. 当前状态

- scientific claims = 0；
- GPU runs = 0；
- workbench = PROPOSED；
- lineage已到 P104（并持续更新）；
- active seeds = I07–I12（6个）；
- experiments已到 E18；
- 本地 agent入口：[LOCAL_AGENT_PROMPT](../../workbench/latent-world-model-planning/LOCAL_AGENT_PROMPT.md)。

**一个 seed null/撞车/被baseline吸收，只 park seed；不自动关闭 parent R#。**
