# Positioning / novelty ownership map（D5 hardening）

更新：2026-10-02。  
目标会议：ICML / ICLR / NeurIPS；视觉贡献足够时 CVPR。  
当前没有 manuscript 主旨，所以本表不是“证明 novelty”，而是**给实验探索设边界**。

## 1. 已接收的尺度锚点

| 工作 | Venue | 它真正拥有的 claim | 我们从中学习的论文形态 |
|---|---|---|---|
| DINO-WM | ICML 2025 | pretrained DINO feature 上学 offline dynamics，可直接 zero-shot observational-goal planning | 换掉 pixel reconstruction 这一前提，范式简化 |
| PLDM / Reward-Free Offline Data | NeurIPS 2025 Main | 系统比较 reward-free offline RL vs latent control；data quality/diversity/layout 泛化与 stitching | comparative science 可以是贡献，但必须控制 data regime |
| OGBench | ICLR 2025 | 把 stitching/long-horizon/visual/stochasticity 做成 benchmark 能力维度 | benchmark 必须暴露方法排序变化，不是收集任务 |
| Temporal Straightening | ICML 2026 | curvature 是 planner-consumed geometry；straightening 改善 geodesic proxy/conditioning | 构念 + 理论/几何 + downstream consequence |
| Offline GCRL Quasimetric | NeurIPS 2025 Main | suboptimal/stochastic data 下用 quasimetric structure 学 optimal goal distance | behavior future 与 optimal controllability 要区分 |
| Multistep Quasimetric | ICLR 2026 | local DP optimality 与 global MC stability 的张力及统一 | 从理论 tension 推 practical objective |
| TempDATA | ICML 2025 | temporal-distance abstraction 帮助 long-horizon offline MBRL augmentation | 邻域概念已成熟，不能把 temporal distance 当新概念 |
| World-In-World | ICLR 2026 | generative WM 必须闭环 task-success evaluation；visual quality 不够 | decision-centric evaluation 已是显式主题 |

官方 venue 链接见 `PAPER_LINEAGE.md`。

## 2. 2026 直接 ownership：reviewer 最容易压缩我们的地方

| 近邻 | 已占的具体 claim | 若我们这么做会被压缩成什么 |
|---|---|---|
| LeWM | simple end-to-end Gaussian-regularized compact JEPA | “LeWM 换一个小 loss” |
| JEPA-WMs | architecture/training/planner recipe sweep | “再多扫几个 hyperparameter” |
| RC-aux | multi-horizon + finite-budget reachability | “reachability head v2” |
| TD-JEPA | trajectory-derived directed temporal progress | “时间距离换写法” |
| Temporal Straightening | local trajectory curvature / planner geometry | “另一种几何正则” |
| SCALE | privileged state-distance calibration | “拿 simulator state 对齐 latent” |
| DA-LeWM | random/CEM-stage latent-real rank alignment + action heads | “我们也测 Spearman/候选排序” |
| SMWM / AC-MTM | inverse dynamics/action contrastive anti-collapse | “再加 IDM” |
| Fast/VLWM | direct/parallel/variable-horizon prediction | “多预测几步” |
| SALT | recursive error propagation + state-affine transition | “one-step error 不重要” |
| ActSWM | Context Collapse / action-sensitive futures | “不同动作未来太像” |
| ACID | inverse-cycle intermediate realizability | “加 verifier” |
| IMWM | perfect WM 也会 search fail + demonstration intuition | “planner 才是 bottleneck” |
| SAGE | subgoal-conditioned action proposal | “learned proposal for long horizon” |
| GC-IDM | amortized current-goal-to-action inference | “不跑 CEM” |
| LeFlow | amortized generative latent trajectory prior | “flow planner” |
| RP1 | learned plan-update optimizer | “learn planner” |
| Hi-LeWM/HWM | hierarchy/multiscale planning | “加 temporal hierarchy” |
| Dual-WM/FlexiWorld | separate temporal roles / variable chunks | “多时间尺度” |
| RWM | direct executable latent paths | “在 latent 里直接连路径” |
| Planning Limits | finite plannable range even with perfect dynamics | “long horizon 是根因” |
| What Must… | mechanism/response/decision sufficiency hierarchy | “world model 不必预测所有东西” |
| DRPE | decision-relevant error vs total error | “不是所有 error 都重要” |
| ACPC | action-conditioned visual perturbation consistency | “JEPA OOD robustness metric” |
| MEND | label-free latent hallucination score/correction | “检测 rollout hallucination” |
| Anchored Planning | final goal 不适合短 horizon；near target 可救 frozen WM | “用 intermediate goal” |

## 3. 明确禁止作为 headline 的句子

这些可以出现在 introduction/background，不得作为我们的“发现”：

- “predictive accuracy does not imply planning quality.”
- “latent Euclidean distance does not reflect real progress.”
- “long-horizon planning is difficult.”
- “a perfect world model is not sufficient when search is finite.”
- “inverse dynamics makes representations action aware.”
- “multi-step training reduces train-test mismatch.”
- “CEM proposals are inefficient.”
- “subgoals/hierarchy help long horizons.”
- “OOD/visual perturbations can break a latent WM.”
- “world models should be evaluated by decision success.”

## 4. 当前三个可挖 region 与 exact delta 要求

### R-A — Behavior-policy geometry → latent WM planning geometry（首选）
**最近邻：** RC-aux, TD-JEPA, PLDM, OGBench, QRL/quasimetric, multistep quasimetric。

**我们需要的 delta 不是：**
- “trajectory offset 不是真 shortest path”（RC-aux 自己承认）；
- “suboptimal data 有 bias”（GCRL 已做）；
- “数据质量影响规划”（PLDM 已做）。

**只有下面这种证据才可能形成独立故事：**
> 在 environment dynamics / local transition support / one-step training samples 被控制的情况下，**只改变 behavior-path 或 episode organization** 就系统改变 trajectory-supervised WM 的 learned reachability/progress geometry、candidate ordering 和 closed-loop planning；并且这种变化可由一个 environment-structural/local-consistency correction 减弱。

这把 offline-GCRL 的 behavior-vs-optimal tension 带进了**world-model planning objective 的 identification 问题**。

### R-B — Optimizer-induced support drift（次选）
**最近邻：** PLDM uncertainty, ACID, MEND, Flow-JEPA, Closing Train-Test Gap for GBP, Hi-LeWM search-distribution mismatch。

**需要的 delta：**
不是“CEM 会 OOD”。必须证明一个可复现链条：
[
	ext{optimizer iteration}
	o 	ext{support drift}
	o 	ext{model optimism / false elites}
	o 	ext{environment regret}
]
并显示它不能被简单 action-bound/smoothness/uncertainty baseline 吸收，或揭示已有 verifier 在何种 regime 系统失效。

### R-C — Bottleneck relocation / regime map（探索引擎）
**最近邻：** Planning Limits, What Must…, JEPA-WMs, SALT, Temporal Straightening, SAGE/IMWM。

**需要的 delta：**
不是方法 benchmark。要发现少数可测变量（例 goal distance、candidate margin、data support）决定**representation→dynamics→proposal/horizon**中哪个成为主要 bottleneck，并能预测 intervention ranking 或导出 adaptive method。

## 5. 当前 pressure ideas 的状态

| ID | 状态 | 为什么现在值得跑 | 最大 compression risk |
|---|---|---|---|
| I01 behavior-policy geometry contamination | SEED / first gate | 由 RC-aux/TD-JEPA 与 QRL/quasimetric 的真实理论张力产生；可用同数据 metadata intervention 做廉价识别 | reviewer 说“temporal distance 本来就是 behavior dependent” |
| I02 optimizer support drift | SEED | 一套 candidate logger 可复用所有 planner；可解释 false elite 而非只看 success | offline MBRL/model exploitation 已经典 |
| I03 bottleneck regime switch | SEED | 让大量独立实验服务于一个统一问题，而不是 leaderboard | “只是大 benchmark/sweep” |
| I04 random→elite decision alignment gap | SEED / subordinate | DA-LeWM 已给 metric；最便宜复现，可作为 I02/I03 信号 | DA-LeWM exact overlap |
| I05 history/partial-observability interaction | PARKED | 科学上合理，但 UWM/Causal-JEPA/SMWM 已有邻居，且首轮 substrate 未必有 clean POMDP control | 容易成为“再测 context length” |

## 6. 反向 reviewer test

### 若 I01 成立，reviewer 会问
1. 你不就是重新发现 behavior policy 会改变 Monte-Carlo temporal distance吗？
   - 必须回答：我们固定 local transition samples/dynamics，并证明这个 bias 被写进 latent-WM planning supervision，进而改变 CEM candidate ranking与environment outcome；再和 quasimetric/local-transition countermeasure 对比。
2. 改 trajectory partition 是否产生 train-sample leakage/different windows？
   - one-step window manifest/hash 必须 byte-level 匹配。
3. navigation toy 是否太小？
   - 先用 exact graph oracle 做 identification；随后至少在一个 contact-rich continuous task 做 approximate counterpart/negative-control，不把 toy 本身当论文终点。

### 若 I02 成立，reviewer 会问
1. offline MBRL model exploitation 不是老问题吗？
   - 必须说明 compact latent CEM 中**哪个新的 measurable support/elite mechanism**以及为什么现有 ensemble uncertainty/ACID/MEND 不够。
2. 只是 CEM 参数调坏了吗？
   - compute matched + action-bound/smoothness + true dynamics + fixed-pool controls。

### 若 I03 成立，reviewer 会问
1. 不就是 component benchmark？
   - 必须有 predictive regime variable / intervention rule，不是 method ranking table。
2. protocol 不同导致 apparent switch？
   - 统一 observation/action/time/goal/candidate manifest；原生 reproduction 与 common protocol 分表。

## 7. 什么时候应该停止扩大实验

- 如果 I01 的最干净 metadata intervention 在**target/head层就不改变**，先查 implementation；阳性对照通过后仍 null，则 park I01，不继续造更怪数据。
- 如果 I01 只影响 reachability/TD head，但 fixed-candidate ranking 与 control 在 MIE 内不变，不把它包装成论文。
- 如果 I02 support metric 只和 action magnitude 共变，控制后消失，则不再加 detector。
- 如果 I03 的“regime”只能靠每任务单独阈值解释，没有 cross-task predictive variable，则退回 measurement，不包装 phase law。

这不是桌面判死 territory，而是让 GPU 吞吐用于**能改变科学判断的实验**。