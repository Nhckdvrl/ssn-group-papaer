# Literature Ledger — latent world-model planning

更新：2026-10-02。用途：让执行 agent 知道**哪些结论来自什么阅读深度、哪些论文必须回原文、哪些有可用代码**。  
不是 bibliography padding。阅读等级：

- **A**：主文方法 + 主要实验 + related work / limitations / 关键 appendix 已针对性核对；足以用于当前 positioning。
- **B**：主文核心段落/实验或官方 proceedings/project/repo 已核对，但未逐 appendix 深读。
- **C**：导航/定位级；只能用于“这里有这条线”，不能承担 manuscript-critical claim。
- **CODE**：官方/作者 repo 已用 GitHub connector 核对；commit 仅对本轮真实核对的仓库给出。

## 1. 顶会 / journal 锚点

| ID | 工作 | Venue | Read | Code / asset | 本 workbench 中的用途 |
|---|---|---|---|---|---|
| P01 | DINO-WM | ICML 2025 | B | public | frozen-feature latent planning 起点 |
| P02 | Learning from Reward-Free Offline Data / PLDM | NeurIPS 2025 Main | A | public ecosystem | data quality/diversity/stitching；offline GCRL 对照 |
| P03 | OGBench | ICLR 2025 | B | official | stitching/long-horizon/data regimes；non-WM baselines |
| P04 | Temporal Straightening | ICML 2026 | A | official + UPDATES | local trajectory curvature / planner geometry |
| P05 | Offline GCRL with Quasimetric Representations | NeurIPS 2025 Main | A | public | behavior future vs optimal goal distance |
| P06 | Multistep Quasimetric GCRL | ICLR 2026 | A | public | MC behavior statistics vs Bellman optimality |
| P07 | TempDATA | ICML 2025 | B | — | temporal-distance structure in offline MBRL |
| P64 | Conservative Offline Goal-Conditioned Implicit V-Learning | ICML 2025 | A | publication material | cross-trajectory connected/unconnected semantics；I06 direct neighbor |
| P09 | What Drives Success in Physical Planning with JEPA-WMs | TMLR 2026 | A | facebookresearch/jepa-wms | recipe/confound checklist |
| P50 | Learning Task-Sufficient World Models | ICML 2026 | B | publication materials | task-minimal/sufficient state 已有顶会 ownership |
| P51 | Behavior-Invariant Task Representation… | ICML 2026 | B | publication materials | “behavior-invariant representation” broad claim 已占 |
| P52 | Parallel Stochastic Gradient-Based Planning for WMs | ICML 2026 | B | publication materials | differentiable planner family |
| P53 | World-In-World | ICLR 2026 Oral | B | official repo | closed-loop utility / generative-WM邻域 |
| P54 | Sparse Imagination | ICLR 2026 | B | official project/code | inference token sparsity / efficiency |
| P55 | CompACT / Planning in 8 Tokens | CVPR 2026 | B | CODE: kdwonn/CompACT @ 71b3029 | aggressive discrete compression / compute |
| P56 | GeoWorld | CVPR 2026 | B | CVF material | hyperbolic/geometric WM 邻域 |

## 2. Compact JEPA / LeWM 直接谱系

| ID | 工作 | Status | Read | Code / asset | Ownership / warning |
|---|---|---|---|---|---|
| P08 | LeWorldModel | arXiv 2026 | A | CODE: lucas-maes/le-wm pinned in ASSETS | end-to-end SIGReg + next-latent compact baseline |
| P10 | Sensorimotor World Models | arXiv | A | official repo | inverse dynamics as sensorimotor anti-collapse |
| P11 | No Gaussian Required / AC-MTM | arXiv | B | — | action-NCE / transition action identification |
| P12 | SCALE | arXiv | B | — | privileged state-distance calibration |
| P13 | Decision-Metric Alignment / DA-LeWM | arXiv | A | paper artifacts | Plan-Real + CEM-stage rank / candidate margin |
| P14 | Temporal-Distance JEPA | arXiv | A | CODE: HKBU-KnowComp/Temporal-Distance-JEPA @ b4c17ca | trajectory-derived directed temporal cost；I01 direct pressure |
| P15 | RC-aux | NeurIPS 2026 (official repo announcement) | A+ | CODE: Guang000/RC-aux pinned; user-provided PDF | finite-budget reachability proxy + multi-horizon |
| P17 | ATLAS | arXiv | A | CODE: Annie969/atlas-world-model | marginal vs relational geometry |
| P18 | Fast-LeWM | arXiv | B | public project | parallel action-prefix prediction |
| P19 | Variable-Length Latent WM | arXiv | B | — | variable k-step prediction |
| P20 | Flow-JEPA | arXiv | B | CODE: HuoYanchen/Flow-JEPA | stochastic whole-trajectory prediction |
| P21 | SALT | arXiv | A | CODE found: deepmindby/SALT; execution pin TBD | recursive error propagation / state-affine transition |
| P22 | ActSWM | arXiv | B | — | Context Collapse / action sensitivity |
| P23 | MEND | arXiv | B | — | latent hallucination detection/correction |
| P24 | DRPE / Not All Errors Matter | arXiv | A | — | decision-relevant error vs total error |
| P40 | A Control Theory of Predictability | arXiv | A | — | planner-reachable measure / off-manifold divergence；I02 collision |
| P41 | The Objective Is the Bottleneck | arXiv | A | released checkpoint referenced by paper | objective can bind even if info/prediction remain |
| P42 | Traj-LeWM | arXiv | A | CODE: XiaodiHuang-code/Traj_LeWM @ 67577fa | full-path latent cost / failure mining |
| P43 | AD-WM | arXiv | A | project/code link; exact repo pin TBD | factual prediction vs counterfactual action discrimination |
| P44 | Control-Geometry Straightening | arXiv | A | code not identified this pass | local action↔latent-displacement geometry |
| P45 | AnisoWM | arXiv | B | project-page repo only | isotropic prior is not geometry-neutral |
| P46 | Adaptive Latent Capacity / ALeWM | arXiv | B | project-page repo @ 6717193; research code not verified | ordered latent capacity / MixSIGReg |
| P47 | Physically Grounded JEPA | arXiv | B | — | IDM + physical state alignment |
| P48 | PSG-JEPA | arXiv | A | CODE: Haodong-Yan/PSG-JEPA @ 3bf67a4 | static + multi-horizon proprioceptive grounding |
| P49 | Capability Separation: WM policy vs imitated world-action | arXiv | A | — | observational future factorization ≠ identified intervention |
| P57 | Hidden Failure Modes in Latent WM Planning | ICML 2026 Workshop Oral | A | CODE: 24GUNV/LeWMRO @ faff2ea | replanning/scoring-time mismatch + controllability interface |
| P58 | PhyLatent | arXiv | B | project page | physical invariance/distinguishability/counterfactual-dynamics collapse |
| P59 | Do-JEPA | arXiv | B | code not pinned | same-reset physical interventions / causal action effects |
| P60 | Bilinear World Models | arXiv | B | code not pinned | structured bilinear dynamics + action recoverability |
| P61 | One-Step Next-Latent Prediction Is Not a World Model | arXiv | B | — | one-step conditional mean ≠ rollout transition kernel |
| P62 | FIRM-WM | arXiv | B | code not identified/pinned | typed goal state + recurrent dynamic fiber + same-reset interventions |
| P63 | FF-JEPA | arXiv | B | no official repo pinned | action-free latent subgoal planner / long horizon |

## 3. Planner / search / long-horizon 直接邻居

| ID | 工作 | Status | Read | Code / asset | Ownership |
|---|---|---|---|---|---|
| P25 | Latent Geometry Beyond Search / GC-IDM | arXiv | B | official repo linked by PSG-JEPA | amortized goal-conditioned inverse planner |
| P26 | IMWM | arXiv | A | — | ideal dynamics still finite-sample search fail; demo intuition |
| P27 | ACID | arXiv | A | — | inverse-cycle transition consistency |
| P28 | SAGE | arXiv | B | — | subgoal-conditioned proposal |
| P29 | LeFlow | arXiv | A | CODE: hsiangwei0903/LeFlow | generative/amortized latent path |
| P30 | RP1 | arXiv | B | — | learned plan-update operator |
| P31 | LEAP | arXiv | B | — | composite energy + differentiable action optimization |
| P32 | Aim Short to Reach Far / Anchored Planning | arXiv | A | — | far final goal can mislead short-horizon planner |
| P33 | Hi-LeWM / Mind the Gap | workshop/arXiv | A | — | hierarchy alone fails; macro-action search distribution mismatch |
| P34 | Hierarchical Planning with Latent WMs | arXiv/project | B | public project | shared-latent multi-timescale MPC |
| P35 | Dual-WM | arXiv | B | CODE: DeLin1001/Dual-WM-Official | separate high/low temporal roles |
| P36 | FlexiWorld | arXiv | B | — | mixed-span supervision / variable action chunks |
| P37 | Representation World Model | arXiv | B | — | direct latent path + local inverse actions |
| P38 | What Must a World Model Distinguish for Planning? | arXiv | A | — | mechanism / response / decision sufficiency |
| P39 | Planning Limits of Latent World Models | arXiv | A | — | finite plannable range even with perfect dynamics |

## 4. 额外导航 / 邻域

| 工作 | Read | 为什么留 |
|---|---|---|
| stable-worldmodel | A/code | common data/model/planner interface；不是 scientific contribution |
| DINO-WM / V-JEPA-2 / generative WMs | B/C | 防止 compact JEPA workbench 与大型 visual-WM 社区脱节 |
| classic MOPO/MOReL/offline MBRL model exploitation | C background | I02 “OOD/model exploitation”绝不是新问题 |
| partial-observability / causal-state / belief-state WM line | C | I05 只有找到 clean substrate 才深挖 |
| Causal-JEPA | C | object/causal masking 邻域；不等于 intervention ground truth |
| ACPC / action-conditioned visual consistency line | C | OOD/action sensitivity 邻域，避免重复 metric |

## 5. 阅读债务与“什么时候必须回原文”

### 在跑 I01 之前必须已经掌握
- P05/P06 quasimetric GCRL 的 behavior-vs-optimal distinction；
- P14 TD-JEPA 的同轨迹 gap 是 shortest distance **upper bound / surrogate**，以及 cross-trajectory negative 的 heuristic 属性；
- P15 RC-aux 对 trajectory-offset label 的 proxy 限定；
- P04 Temporal Straightening 对 suboptimal route / temporal geometry 的相关讨论；
- P42 Traj-LeWM 的 full-trajectory preference来源。

这些已达到本轮 positioning 需要的阅读深度；若 I01 升 L2，重新下载/固定版本，逐 theorem/appendix 核对 manuscript wording。

### 在跑 I03 之前必须回看
P13、P21、P25–P44、P57–P63；特别是它们各自改变的 layer、replanning/scoring protocol 与 intervention setting，避免把原生数字横向排名。

### 不要求首轮安装
CompACT、World-In-World、GeoWorld、HWM、大型 V-JEPA2 路线；它们证明 community scale 与邻域 ownership，但不适合用弱互联资源作为首轮训练 substrate。

## 6. 代码可执行性快照（2026-10-02）

**已用 GitHub connector 核对：**
- LeWM：见 ASSETS pin。
- stable-worldmodel：见 ASSETS pin。
- RC-aux：见 ASSETS pin。
- TD-JEPA：`HKBU-KnowComp/Temporal-Distance-JEPA@b4c17ca4649c9bf47272fa66c38da7a684f2a020`；repo 自带 LeWM / RC-aux variants、locked eval manifests 和结果摘要，**I01 首轮优先考虑直接在这个 repo 中做 paired dataset intervention**。
- Traj-LeWM：`XiaodiHuang-code/Traj_LeWM@67577fa27242f6e888f40e399ab3e1b542b1367f`；source-only，默认 10 epochs，含 endpoint-only failure mining。
- PSG-JEPA：`Haodong-Yan/PSG-JEPA@3bf67a47a9143f9f4fb4d39f839143c92902714c`；OGBench planning + LIBERO policy 两套 env。
- ALeWM：`arm-research/AAIR-ALeWM@6717193bdc3b92e43f581b3c668ca9b82c299c70` 当前核对的是 project page；README 明确 root 为未来 research code 预留，**不能写成 code-ready baseline**。
- CompACT：`kdwonn/CompACT@71b3029910d7460c5fa8658e17ab34e29c2c880c`；paper-scale tokenizer/WM 配方多 GPU，不列为首轮 substrate。
- Hidden Failure Modes / LeWMRO：`24GUNV/LeWMRO@faff2ea4768767739b9cca55855dc5aacf13578f`；含 terminal/prefix/running costs、receding-horizon eval、deceptive tasks、tests 与 machine-readable results；**E06 protocol-layer control 很适合直接复用**。

**仅搜索到项目/论文、未在本轮锁定可执行 repo：**
AD-WM、CGS、AnisoWM、Planning Limits、Objective Bottleneck、PhyLatent、Do-JEPA、Bilinear WM、FIRM-WM、FF-JEPA 等。需要它们成为 manuscript-critical baseline 时再做代码/作者 release audit；不要为了“完整”先实现论文。

## 7. 完整性的含义

本 ledger 的“完整”不是声称已读尽所有 world-model 论文，而是：截至 2026-10-02，**会改变本 workbench 选题、baseline、claim ownership 或决定性实验设计的主要直接/邻接工作已进入地图**；新的 arXiv 仍会出现，因此任何 C## 升 L2、进入 candidate、投稿前三个节点都必须重扫。

## 8. Problem-led hardening additions（P65–P74）

| ID | 工作 | Venue/Status | Read | Code / asset | Workbench作用 |
|---|---|---|---|---|---|
| P65 | TD-JEPA: Latent-predictive Representations for Zero-Shot RL (Bagatella et al.) | **ICLR 2026 Oral** | A | CODE: facebookresearch/td_jepa @ 840a745 | M2 implicit predictive abstraction；与P14同简称冲突，必须写作者/全名 |
| P66 | UWM-JEPA: Predictive WMs That Imagine in Belief Space | arXiv 2605.25313 | B | CODE: santoshkumarradha/uwm-jepa @ 1ef5735 | M1 belief-space direct neighbor；目前主要controlled prediction/probe |
| P67 | Flow Equivariant World Models | **ICML 2026** | B | official project/code | partial-observation structured memory；M1 collision/control |
| P68 | What Capable Agents Must Know | **UAI 2026** | B | proceedings | belief-like memory necessity的理论尺度锚点 |
| P69 | Latent WMs with Monotone Planning Costs for Image-Goal Navigation | arXiv 2608.09073 | B | paper/project to audit if baseline-critical | monotone candidate cost + temporal-negative distortion；压缩I06 broad claim |
| P70 | Grounded World Model for Semantically Generalizable Planning | arXiv 2604.11751 | B | paper/project | language/query goal interface；M4 watch |
| P71 | Robot World Models Are Not Invariant to How the Actions Are Written | arXiv 2609.23252 | B | code TBD | problem-led invariance范例；action parameterization claim已占 |
| P72 | World Models for Embodied Intelligence: Plausible→Controllable→Actionable | survey arXiv 2609.16697 | A/B | survey | workbench scientific-yield gate：probe必须连到decision/actionability |
| P73 | Objective Mismatch / Goal-Aware Prediction / Value Equivalence | L4DC/ICML/NeurIPS 2020 | B background | — | task/decision-sufficient modeling不是2026新哲学 |
| P74 | I-TAP: In-Context Planning with Latent Temporal Abstractions | arXiv 2602.18694 | B | project/code TBD | history+temporal abstraction+POMDP/regime shift；M1 collision |

### 必须补读的触发条件

- **M1进入E12前：** P62 FIRM-WM、P66 UWM-JEPA、P67 Flow Equivariant、P68 selection theorem、P74 I-TAP；若使用 VLA aliasing benchmark，再补对应policy literature。
- **M2进入confirmatory前：** P09 TMLR explicit/implicit discussion、P65 Bagatella TD-JEPA完整appendix/code、TD-MPC2及至少一个search-amortized hybrid。
- **M3进入方法设计前：** P05/P06 quasimetric、P02 PLDM data regimes、P64 CGCIVL、P14 Bai/Xiong Temporal-Distance JEPA、P15 RC-aux、P69 monotone-cost/negative study。

P65 与 P14 的 acronym collision 属于 provenance risk：任何结果文件只写 `bagatella_td_jepa` 或 `temporal_distance_jepa`，禁止裸 `td_jepa` 作为论文标识。
