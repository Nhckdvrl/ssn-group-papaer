# Paper lineage — latent world-model planning（2026-10-02）

> 目的不是文献清单，而是重建**问题如何长出来**：母问题 → 旧前提 → 压力/反例 → idea leap → 方法 → 决定性证据 → 被占有的 claim → 留给后续的压力。  
> `DOCUMENTED` 表示论文明确论述；`RECONSTRUCTED` 表示根据论文论证与近邻关系重建，不声称知道作者真实创意过程。  
> 顶会状态只在官方 proceedings 可核对时写“接收”；其余写 arXiv/TMLR/workshop，不替预印本升级 venue。

## 0. 先看 lineage，而不是把论文按年份排

```text
offline / reward-free data
        │
        ├─ DINO-WM (ICML'25):  pretrained feature 可以直接当 world state 做 zero-shot planning
        │       │
        │       ├─ PLDM (NeurIPS'25): 与 offline GCRL 比，什么时候 model-based latent planning 更有优势？
        │       └─ JEPA-WMs / LeWM: pretrained/frozen 不是唯一答案；怎样得到可训练、稳定、小型的 end-to-end latent WM？
        │
        ├─ LeWM (2026): 端到端稳定、便宜的共同底座
        │       │
        │       ├─ 表示/几何：Temporal Straightening / SMWM / SCALE / DA-LeWM / TD-JEPA / ATLAS
        │       ├─ 动力学：Fast-LeWM / VLWM / Flow-JEPA / SALT / ActSWM / MEND
        │       ├─ 规划器：GC-IDM / IMWM / ACID / SAGE / LeFlow / RP1 / LEAP / Anchored Planning
        │       └─ 长时标：Hi-LeWM / HWM / Dual-WM / FlexiWorld / RWM
        │
        ├─ 理论/诊断压力：
        │       ├─ Decision-Metric Alignment: 有信息 ≠ 这个 metric 能 rank actions
        │       ├─ DRPE: 总 prediction error ≠ decision-relevant error
        │       ├─ What Must a WM Distinguish?: mechanism / response / decision sufficiency
        │       └─ Planning Limits: perfect dynamics 也不能消灭有限 planning range
        │
        └─ 邻接的 offline GCRL / quasimetric：
                OGBench → QRL/quasimetric → multistep quasimetric
                核心警告：trajectory temporal distance / Monte-Carlo future statistics
                可以编码 behavior-policy geometry，而非天然等于最短可达结构
```

这个 lineage 的重要结论不是“某个组件最重要”，而是：**2026 年的论文在迅速把同一系统拆成 representation / metric / dynamics / proposal / verifier / temporal abstraction / data geometry 等不同承重点。我们的工作台必须能把这些承重点独立操纵和审计。**

---

## 1. 顶会锚点：什么尺度的问题已经被社区认可

### P01 — DINO-WM — ICML 2025
**来源：** https://proceedings.mlr.press/v267/zhou25t.html  
**形态：** 新范式/系统 + 跨任务证据。

- **母问题（DOCUMENTED）：** world model 若要成为通用 physical reasoning 工具，应能从 offline pre-collected trajectories 学、test-time 优化行为、并保持 task-agnostic。
- **旧前提/压力：** pixel reconstruction 和 task-specific online policy learning 把 world model 绑在昂贵、任务相关的目标上。
- **idea leap：** 不重建 pixel；直接预测 DINOv2 的 spatial patch features，并把 observation goal 的 feature 当 planning target。
- **方法：** frozen DINOv2 encoder + action-conditioned latent dynamics + test-time action-sequence optimization。
- **证据：** 六类环境；无需 expert demo/reward model/pretrained inverse model；zero-shot observational goal planning。
- **与近邻距离：** 它把“视觉 foundation feature 可否作为可规划状态”变成可实证问题，而不是提出新的大 decoder。
- **claim ownership：** “pretrained visual features + offline latent dynamics + zero-shot goal planning” 已被占有。
- **打开的新压力（RECONSTRUCTED）：** recognition feature 为什么应当适合 control geometry？frozen feature 是否丢失 action-relevant structure？这直接喂给后续端到端 representation work。

### P02 — PLDM / Learning from Reward-Free Offline Data — NeurIPS 2025 Main
**来源：** https://proceedings.neurips.cc/paper_files/paper/2025/hash/3e7cf447f21cd11c846463affefce665-Abstract-Conference.html  
全文：https://arxiv.org/abs/2502.14819  
**形态：** comparative science + learned latent planner。

- **母问题：** reward-free offline trajectories 下，goal-conditioned/model-free RL 与 learned dynamics + optimal control 的相对强弱究竟是什么？
- **旧压力：** 过去 offline RL 常比较算法但不精细控制 data diversity / quality / environment variability。
- **设计：** 两类 navigation 环境、23 个数据集；六类方法。PLDM 用 JEPA latent dynamics，ensemble uncertainty 在 planning 中惩罚 OOD transition。
- **决定性实验：** 数据质量、随机轨迹、trajectory stitching、数据效率、新 task、新 layout 等压力分开测。
- **重要非直觉边界：** “world model 更会 stitching”不是绝对命题；原文 no-door 数据中 GCIQL/HILP 远好于 PLDM，而 PLDM 的优势更稳定地体现在数据效率/新 layout/generalization。
- **claim ownership：** 泛泛“data quality/diversity/stitching 对 latent planning 很重要”已经做过。
- **打开的新压力：** 同样的环境 dynamics，trajectory **组织方式/behavior policy** 如何塑造一个从 trajectory supervision 学出来的 planning geometry？PLDM 本文比较数据分布，但没有把“环境可达结构”和“行为时间结构”做成同 transition support 下的因果分离。

### P03 — OGBench — ICLR 2025
**来源：** https://proceedings.iclr.cc/paper_files/paper/2025/hash/ecd92623ac899357312aaa8915853699-Abstract-Conference.html

- **母问题：** offline GCRL 需要把 stitching、long-horizon、visual input、stochasticity 分开，而不是一个总分。
- **资产：** 8 类环境、85 数据集、6 个 reference algorithms。
- **对我们：** OGBench 不是“再加一个 benchmark”，而是 non-WM / temporal-distance / stitching 对照来源；尤其适合检验世界模型的 trajectory-derived objective 到底学了 dynamics 还是 behavior geometry。

### P04 — Temporal Straightening — ICML 2026
**来源：** https://proceedings.mlr.press/v306/wang26n.html  
**形态：** 构念/几何 + 方法 + 规划后果。

- **母问题：** semantic visual feature 不等于 planner-friendly feature；Euclidean goal cost 的 optimization conditioning 由 latent trajectory geometry 决定。
- **idea 来源（DOCUMENTED）：** perceptual straightening hypothesis → 对 latent temporal trajectory curvature 加 regularization。
- **方法：** curvature regularizer + joint encoder/predictor。
- **决定性证据：** 不是只看 probe；证明/实证 curvature 降低使 Euclidean 更接近 geodesic，并使 gradient-based planning 更稳定、成功率提高。
- **claim ownership：** “straighten local latent trajectory → Euclidean geometry/gradient planning 更好”已占有；不能换个 curvature metric 重做。
- **研究动作：** 学它如何把“表示不好”压缩成**一个可操纵的几何性质**，并从理论性质连到 downstream optimizer。

### P05 — Offline GCRL with Quasimetric Representations — NeurIPS 2025 Main
**来源：** https://proceedings.neurips.cc/paper_files/paper/2025/hash/1c5956164472d6d8123d574aa75cd063-Abstract-Conference.html

- **母问题：** temporal-distance methods 有 shortest-path inductive bias，但在 stochastic/suboptimal data 下如何仍学 optimal goal-reaching distance？
- **idea leap：** successor/contrastive representation 与 quasimetric（方向性 + triangle inequality）结合。
- **关键意义：** 明确告诉我们：**从行为轨迹观察到的未来/时间差，不天然等于 optimal reachability geometry**；需要额外结构/约束才能从 suboptimal data 中 stitching。
- **对本工作台：** 是 trajectory-supervision 研究线必须引入的理论/算法邻居，而不是“RL 与 WM 不相关”。

### P06 — Multistep Quasimetric GCRL — ICLR 2026
**来源：** https://proceedings.iclr.cc/paper_files/paper/2026/hash/eddc0fab5a42f8d8de6eb5566cd9f1d3-Abstract-Conference.html

- **母问题：** local DP/TD 有 optimal shortest-path 结构，但 global Monte-Carlo update 统计稳定；二者如何结合？
- **方法：** multistep Monte-Carlo return + quasimetric structure。
- **证据：** long-horizon simulated（到 4000 step）与 real robot manipulation。
- **对我们：** 若 RC-aux/TD-JEPA 类 trajectory-derived target 随 behavior path 改变，不能把这个发现包装成“时间距离本来就有 bias”——GCRL 已知。新的 scientific delta 必须落到 **latent world-model planning objective 如何被这种 bias 改写，并造成 candidate ranking / control 后果**。

### P07 — TempDATA — ICML 2025
**来源：** https://proceedings.mlr.press/v267/lee25p.html
- **母问题：** sparse reward / long-horizon offline MBRL 的 transition augmentation 为什么失效？
- **动作：** 把 temporal distance 引入 representation，再在几何结构化 latent 中做 transition augmentation。
- **ownership：** “temporal-distance representation 帮助 offline MBRL long horizon”已有顶会 precedent。我们不能声称 temporal structure 对 model-based control 是新概念。

---

## 2. 共同底座：从 frozen feature 到 end-to-end 小模型

### P08 — LeWorldModel (LeWM) — arXiv 2026
**来源：** https://arxiv.org/abs/2603.19312 ，官方：https://github.com/lucas-maes/le-wm

- **母问题：** end-to-end JEPA WM 容易 collapse，已有方法依赖多项 loss、EMA、pretrained encoder 或 auxiliary supervision。
- **idea leap：** 把 anti-collapse 简化成 Gaussian-distributed latent regularization（SIGReg）+ next-embedding prediction。
- **方法：** 约 15M 参数，raw pixels end-to-end；两项 loss；CEM latent planning。
- **证据：** 多个 2D/3D control task，physical probing/surprise；作者报告单 GPU 数小时训练。
- **为什么它是 workbench 支点：** 小、训练可及、内部全可见、planner 能执行 counterfactual candidate；2026 大量 follow-up 直接建立在它上面。
- **claim ownership：** “简化 end-to-end anti-collapse / 小型 WM 也能 planning”已占。
- **风险：** probe 好不能推出 metric 好；SIGReg 规定边际分布也不能自动推出 local metric/decision alignment。

### P09 — JEPA-WMs / What Drives Success… — TMLR 2026
**来源：** https://arxiv.org/abs/2512.24497 ，代码：https://github.com/facebookresearch/jepa-wms

- **母问题：** DINO-WM 之后，究竟是 planner、training horizon、context、proprioception、encoder、predictor、scale 中哪些选择真正驱动成功？
- **形态：** 系统设计空间研究，simulation + real robotics。
- **ownership：** “多跑一些 recipe sweep 看什么重要”已经很拥挤；新增普通 ablation 不会自然形成 novelty。
- **对我们：** 把它当**强 recipe baseline / confound checklist**。我们的实验要建立在其已知最佳配置或明确分开的原生协议上。

---

## 3. Representation / geometry：从“有信息”到“planner 消费得对”

### P10 — Sensorimotor World Models (SMWM)
**来源：** https://petr-ivashkov.github.io/sensorimotor-world-model.github.io/ ，代码：https://github.com/petr-ivashkov/sensorimotor-world-model

- **母问题：** anti-collapse 为什么要规定 latent 的 marginal distribution，而不由 action transition 本身塑造 perception？
- **idea leap：** inverse dynamics 同时承担 action-relevance 与 anti-collapse；只从 transition tuple 学。
- **ownership：** “inverse dynamics 让表示更 action-aware / 可防 collapse”已占；不能加 IDM 就叫新。
- **边界：** action 非唯一、partial observability 会破坏 inverse mapping 的含义，是我们做 history/stochastic 分支时的必要对照。

### P11 — No Gaussian Required / AC-MTM
**来源：** https://arxiv.org/abs/2608.17542
- **变化：** 把 inverse dynamics 进一步改成 Action-NCE：collapsed encoder 无法从 latent transition 在 batch 中识别 action。
- **证据：** 四 standard pixel-control 与更难 multi-object visual scene；training-only branch，test-time planner 不变。
- **ownership：** “用 transition data 替代 SIGReg anti-collapse”也已有直接工作。

### P12 — SCALE
**来源：** https://arxiv.org/abs/2608.16287
- **母问题：** full latent 可 decode state 仍不代表高方差方向把 task state 组织进 Euclidean cost。
- **方法：** 用 privileged standardized task-state pairwise distance 校准 latent distance。
- **ownership：** privileged state calibration / latent-state distance alignment 已占。若我们使用 simulator state，只能作 diagnostic/oracle，不能把“再校准一下”当默认 novelty。

### P13 — Decision-Metric Alignment / DA-LeWM
**来源：** https://arxiv.org/abs/2608.18746

- **母问题：** “latent 里能 probe 出 task variable”为什么仍不能解释 CEM success？
- **改变前提：** planning 需要的不是信息存在，而是**candidate ordering**在 planner 使用的 metric 下正确。
- **方法/诊断：** Plan-Real Spearman（random plans）+ CEM-stage Spearman（random/mid/elite）；理论把 rank preservation 压成 encoder distortion、terminal rollout error、candidate margin；DA-LeWM 加 inverse + demo-conditioned goal-action heads。
- **决定性贡献：** 把“representation quality”变成 planner 真实消费的 ordinal property。
- **ownership：** 我们 HANDOFF 中的 real-vs-latent fixed-candidate audit 是必要 infrastructure，但**不是新 claim**。
- **仍有压力：** random-candidate alignment、elite-stage alignment、closed-loop success 三者是否在不同 search/data regime 下脱钩，是可复现的探索种子；不能引用二手解读直接当现象。

### P14 — Temporal-Distance JEPA (TD-JEPA)
**来源：** https://arxiv.org/abs/2607.25337
- **母问题：** Euclidean geometry 是 representation learning 的副产品，为什么不从 reward-free trajectory 直接挖 directed progress cost？
- **方法：** same-trajectory temporal gap 正例、cross-trajectory heuristic negatives、rollout consistency。
- **ownership：** “从日志挖 temporal progress/reachability”已占；和 RC-aux 一起形成我们 I01 的直接压力。
- **关键边界：** cross-trajectory negative 与 trajectory gap 都是 dataset-induced supervision，不等于 environment shortest distance。

### P15 — RC-aux
**来源：** 本项目上传论文 arXiv:2605.07278；代码：https://github.com/Guang000/RC-aux
- **母问题：** short-horizon predictive supervision 与 long-horizon planner query 不同；latent proximity 与 finite-budget attainability 不同。
- **方法：** multi-horizon open-loop + budget-conditioned reachability；same-pair temporal hard negatives；planner 可使用 reachability gate。
- **决定性设计：** 对同一 pair 改 h，使 head 不能只学“same trajectory”捷径。
- **关键自限：** 论文明确把 trajectory offset 称为 empirical proxy，不是真实 MDP shortest reachability。
- **ownership：** finite-budget reachability correction 已占。
- **打开压力：** 若 trajectory offset 由 behavior path 而非 environment shortest path 决定，这个 proxy 对 behavior policy/episode organization 到底有多敏感？这是 I01 的核心，而不是再做一个 reachability head。

### P16 — Temporal Straightening（见 P04）
将其放在 geometry lane 中作为“局部曲率”对照：它不依赖 trajectory-pair shortest labels，和 RC-aux/TD-JEPA 的 behavior supervision 形成有意义的**不同 inductive bias**。

### P17 — ATLAS — arXiv 2609.36333
**来源：** https://arxiv.org/abs/2609.36333 ，代码：https://github.com/Annie969/atlas-world-model
- **核心区分：** latent marginal distribution matching 与 relational geometry preservation 是不同目标。
- **ownership：** 泛泛“SIGReg 边际匹配不保关系结构”已被占；新 geometry 工作必须说明与 ATLAS / Straightening / SCALE / DA-LeWM 的 exact delta。

---

## 4. Dynamics：预测“多准”之外，错误怎样传播、动作是否真的改变未来

### P18 — Fast-LeWM
**来源：** https://arxiv.org/abs/2606.26217 ，项目：https://fast-lewm.github.io/
- **压力：** recursive one-step rollout 慢且积累误差。
- **idea：** action-prefix 作为 prediction unit，一次并行预测多个 horizon，dense prefix supervision。
- **ownership：** parallel multi-horizon/prefix prediction + planning speed 已占。

### P19 — Variable-Length Latent WM
**来源：** https://arxiv.org/abs/2606.21775
- **压力：** fixed step/chunk 不适合不同目标时间尺度。
- **ownership：** direct k-step / variable-length action sequence 是已有支线。涉及其 aggregate protocol 时必须核对 planner schedule/oracle-selection，不能只抄主表。

### P20 — Flow-JEPA
**来源：** https://arxiv.org/abs/2608.29029 ，代码：https://github.com/HuoYanchen/Flow-JEPA
- **idea：** conditional flow matching 联合生成整段 future latent trajectory，而非确定性 recursive point prediction。
- **证据重点：** clean + localized/noisy condition；和 LeWM 同环境/数据路径。
- **ownership：** stochastic/trajectory-level dynamics + OOD robustness 已有直接近邻。

### P21 — SALT
**来源：** https://arxiv.org/abs/2609.33595

- **母问题：** one-step error 为什么不能预测 recursive planning？
- **关键观察：** rollout error = 各步新误差 + 后续 transition 的传播；state-affine transition 有 state-independent Jacobian，去掉 nonlinear propagation residual。
- **方法：** action-conditioned state-affine transition + recursive multi-step supervision。
- **决定性反常：** 论文报告 one-step prediction error 比 matched LeWM 高 1.48–2.19×，但四环境 closed-loop success 全升，平均 +10pp；Cube cost-spike failure 23.3%→2.0%。
- **为什么是 idea-growth 范例：** 没有把“prediction≠planning”停在相关性，而是找到**error propagation operator**这一承重点，并由数学结构导出最小 architecture change。
- **ownership：** generic recursive error accumulation、多步 supervision、state-independent-Jacobian story 已占。
- **对我们：** 后续 experiment 必须测 propagation / decision consequence，不把 one-step MSE 当 model quality 总代理。

### P22 — ActSWM
**来源：** https://arxiv.org/abs/2607.26712
- **失败名：** Context Collapse——future latent 与真实 future 相似，但不同 action sequences 得到几乎不可区分的未来。
- **方法：** transition separation + action recoverability，强制 long-horizon action sensitivity。
- **ownership：** “模型看起来准但不响应 action”已有明确 failure+repair；不能重新命名。

### P23 — MEND
**来源：** https://arxiv.org/abs/2609.39182
- **问题：** frozen latent WM 的 silent hallucination 能否 label-free 检测/定位/校正？
- **方法：** denoising score field；检测、patch localisation、correction。
- **证据边界：** 作者重点是 latent error detection/localization；不是已经证明 planner closed-loop 显著提升。
- **机会角色：** 作为 model-exploitation/support-drift lane 的 detector 对照，而不是默认主线。

### P24 — DRPE / Not All Errors Matter
**来源：** https://arxiv.org/abs/2609.32322
- **母问题：** equal total prediction error 为什么 planning 可差很多？
- **方法：** factored gridworld + iso-error protocol + decision-relevant error。
- **证据：** 55 controlled/learned models；总 error 与 success 弱相关，DRPE 强相关；task 改变会反转 relevance。
- **ownership：** generic “不是所有 prediction error 都一样”已占；我们若做错误分析必须在真实 compact visual planner 中给出**新的可操纵结构/方法**，而不是复制 DRPE。

---

## 5. Planner / search：世界模型可以够好，planner 仍可成为瓶颈

### P25 — Latent Geometry Beyond Search / GC-IDM
**来源：** https://arxiv.org/abs/2605.08732
- **母问题：** representation 已有结构后，CEM 数千 rollout 是否还必要？
- **idea：** frozen LeWM latent + horizon-conditioned goal inverse model，直接 current/goal→next action。
- **证据：** 四环境，多 planner 对照；100–130× per-decision speed claim。
- **ownership：** “amortize CEM with goal-conditioned inverse dynamics”已占。

### P26 — IMWM
**来源：** https://arxiv.org/abs/2606.01626
- **决定性起点：** 把 learned predictor 换成 idealized real-environment rollout，finite-budget sample planner 仍失败。
- **idea：** demonstrations 训练 intuition：retrieval initialization + hybrid cost + reliability gate。
- **ownership：** “perfect dynamics 仍可能 search 失败 / demonstration intuition 引导 CEM”已占。

### P27 — ACID
**来源：** https://arxiv.org/abs/2607.02403
- **母问题：** terminal goal cost 不检查 intermediate transition realizability。
- **方法：** inverse model 从 predicted transition 恢复 action；cycle action residual 加入 planning cost。
- **证据：** 4 action-conditioned WMs × 6 tasks。
- **ownership：** inverse-consistency verifier/reranker 已占；其输出也不是 environment executability oracle。

### P28 — SAGE
**来源：** https://arxiv.org/abs/2607.17973
- **母问题：** horizon 增大时固定 candidate budget 的 proposal quality 成为瓶颈。
- **方法：** goal-conditioned latent subgoal + action generator 初始化，再由 frozen WM evaluate/refine。
- **ownership：** subgoal-conditioned proposal guidance / long-horizon candidate quality 已占。

### P29 — LeFlow
**来源：** https://arxiv.org/abs/2608.24855 ，代码：https://github.com/hsiangwei0903/LeFlow
- **母问题：** 每个 query 从零 online optimize，为什么不复用 planning experience？
- **idea：** rectified-flow latent trajectory prior → inverse dynamics actions → frozen WM verify。
- **ownership：** generative/amortized latent trajectory proposal 已占。

### P30 — RP1 / Reinforced Planning
**来源：** https://arxiv.org/abs/2608.18669
- **idea：** critic + learned plan-update operator，用 imagined WM rollouts offline 强化 planner update；attach to pretrained WM。
- **ownership：** learned optimizer/planner update 已占；不能用“learn CEM”做弱变体。

### P31 — LEAP
**来源：** https://arxiv.org/abs/2609.03294
- **方法：** frozen LeWM；terminal latent goal + decoded descriptor energy；proposal init + quasi-Newton action optimization。
- **ownership：** latent/descriptor composite energy + differentiable full-horizon action optimization 已有强近期近邻。

### P32 — Anchored Planning / Aim Short to Reach Far
**来源：** https://arxiv.org/abs/2609.30036
- **决定性压力：** 即使 exact dynamics + globally optimal short-horizon search，final-goal target 仍可错，因为成功路径早期必须离 goal 更远。
- **方法：** 从 recorded segment 找 current↔goal anchor，再瞄准靠近 current 的 observed intermediate target；frozen WM 不改。
- **ownership：** generic“远目标用中间目标”在本 stack 上已有非常直接的 2026-09 工作。

---

## 6. Long horizon / abstraction：不是“多一级”就自动好

### P33 — Hi-LeWM / Mind the Gap
**来源：** https://arxiv.org/abs/2607.12547 （WM@Booth 2026）
- **关键观察：** hierarchy 本身不保证提升；true-future latent subgoal 能被低层执行时，高层 subgoal generation/search 才是瓶颈。
- **失败：** high-level action space 与 inference search distribution mismatch。
- **修复方向：** search 约束在训练轨迹编码的 macro-actions 周围 + 合适 execution timing。
- **ownership：** hierarchy/search-distribution mismatch 已被明确提出。

### P34 — Hierarchical Planning with Latent World Models
**来源：** https://kevinghst.github.io/HWM/
- **idea：** multiple temporal scales 的 shared-latent WMs + hierarchical MPC，不靠 task reward/skill policy。
- **证据：** 含 real-robot non-greedy task。
- **ownership：** multiscale WM hierarchy 是成熟路线，不能只加 coarse model。

### P35 — Dual-WM
**来源：** https://arxiv.org/abs/2609.37644 ，代码：https://github.com/DeLin1001/Dual-WM-Official
- **idea：** 把 low-level execution latent 与 high-level planning latent/dynamics 分开，避免一个 latent 承担不同时间角色。
- **ownership：** “不同时间尺度需要不同 latent role”已在最近预印本中直接占位。

### P36 — FlexiWorld
**来源：** https://arxiv.org/abs/2609.35138
- **idea：** mixed-span goal supervision + variable-length action chunks + autoregressive actor。
- **ownership：** flexible action chunk / mixed temporal scale 已有直接近期方法。

### P37 — Representation World Model (RWM)
**来源：** https://arxiv.org/abs/2609.29171
- **idea：** 不显式 recursive dynamics/search；在 endpoint representation 间构造 latent path，local inverse dynamics 恢复动作。
- **ownership：** “直接在 representation geometry 形成可执行 path”已占。

---

## 7. 最新理论/边界：把我们不能再泛泛说的话写死

### P38 — What Must a World Model Distinguish for Planning?
**来源：** https://arxiv.org/abs/2609.33030

- **母问题：** accurate prediction 要保留的物理区别，是否都是 decision 必需？
- **层次：** mechanism sufficiency > response sufficiency > decision sufficiency；要求取决于 planning query、candidate set、planner。
- **关键细化：** final selection 不需要的信息，adaptive search 仍可能需要它来**发现**候选。
- **方法侧：** query-conditioned joint action/outcome 在 seen objectives 低 regret，但 unseen objective 优势大幅消失；提出 query 决定 where-to-look、action-conditioned model 决定 what-happens 的 modular design。
- **ownership：** “task-relevant / decision-sufficient representation”已经被形式化。我们不能用 broad sufficiency 作为新标题；必须落到尚未解释的 concrete source of mismatch。

### P39 — The Planning Limits of Latent World Models
**来源：** https://arxiv.org/abs/2609.39235

- **母问题：** latent WM 的 imagination 到底在多远目标仍对 action ranking 有用？
- **证据：** 5 frozen SSL backbones，Meta-World + BridgeData V2；5-step rollout 模型对约 5–10 control-step target 排序可靠，而 task goals 在 16–53 step。
- **重要 null：** 81× predictor、longer-rollout training 都没明显延伸范围。
- **perfect-dynamics intervention：** 用 real simulator 后，target 从 5→20 step success 仍 92%→41%。
- **后果：** pure imagination 23、MPC 30、imagine-to-goal 47、nearby expert subgoal 76；在 plannable range 内可给 VLA 8 actions rerank，65→77。
- **ownership：** generic “long horizon / prediction accuracy 不够解释 planning”已经被非常直接地做透一层。
- **对我们：** 把 goal distance / planner range 作为所有 experiment 的分层轴；不要拿它本身当 novelty。

---

## 8. 研究 idea 如何从 related work 中生长：五个可迁移模式

1. **DINO-WM → LeWM/SMWM：换掉一个领域默认前提。**  
   不是“新 loss”，而是问：pretrained semantic feature 为什么应是 control state？然后分别走 end-to-end Gaussian regularization 与 sensorimotor inverse supervision。

2. **LeWM → Temporal Straightening / DA-LeWM：把 broad complaint 压成 planner 实际消费的数学对象。**  
   “representation 不够好”没有论文；curvature / ordinal candidate ranking 才能被干预、理论化并连接成功率。

3. **one-step predictor → SALT：先寻找反常，再改传播结构。**  
   SALT 最值得模仿的是“更差的一步预测 + 更好规划”迫使问题从 accuracy 转到 propagation operator，而方法由这个解释自然导出。

4. **world model → IMWM / Planning Limits：用 oracle 把系统层级拆开。**  
   把 learned dynamics 换成 simulator 后仍失败，才有资格说瓶颈不在 prediction。我们的 workbench 也必须有 oracle ladder，而不是只比较模型分数。

5. **offline trajectory temporal distance → quasimetric：区分 behavior statistics 与 optimal controllability。**  
   这是目前最值得我们迁移到 latent-WM planning 的张力：trajectory-derived “reachability/progress” objective 可能会把 behavior path 写进 geometry；要在**同 dynamics / 同 local support**下操纵 behavior/episode structure，才能把它从普通 data ablation 升格为科学问题。

---

## 9. 红区：可以测，不能直接作为 novelty

- prediction error 与 planning success 不一致；
- latent L2 与真实 progress/ranking 不一致；
- finite-horizon reachability head；
- generic multi-step/open-loop supervision；
- generic inverse-dynamics regularization；
- generic CEM proposal quality / search budget；
- generic hierarchy / subgoal / variable action chunk；
- generic visual OOD robustness / partial observability；
- generic “world model 应 decision-centric evaluation”。

这些全部进入 baseline/diagnostic，不是 headline。

---

## 10. 当前最有研究收益的未决张力（不是 claim）

### T1 — trajectory-supervised planning geometry 是否继承 behavior-policy geometry？
直接张力：RC-aux/TD-JEPA 用 trajectory order/gap；QRL/quasimetric 明确区分 behavior future statistics 与 optimal goal distance；PLDM 显示不同 offline data structure 会改变方法排序。  
**优先级最高，进入 I01 / E03–E04。**

### T2 — optimizer 是否把 candidate distribution 推进 world model “自信但错误”的 support gap？
PLDM 已用 ensemble uncertainty；ACID/MEND/Flow-JEPA 等分别从一致性、density/score、stochastic trajectory 处理部分问题；offline MBRL 的 model exploitation 也不是新概念。  
因此只有出现**compact JEPA planner 中可重复的 support-drift→false-elite→closed-loop regret 链**，且现有 verifier/uncertainty 不能充分解释时，才值得升级。进入 I02 / E05。

### T3 — 修 representation / dynamics / proposal / horizon 后，瓶颈会不会系统迁移？
当前论文常各自改一层并在不同 protocol 报增益。若存在由 goal distance、data support、candidate margin 等少数变量决定的**bottleneck phase/regime switch**，可能形成新 principle；若只是 benchmark ranking，则没有论文。进入 I03 / E06–E07。

### T4 — random-plan metric alignment 与 optimizer-elite alignment / closed-loop success 是否稳定脱钩？
DA-LeWM 已定义 random/mid/elite Spearman；这里仅作为 replication pressure。若复现出系统性脱钩，下一步应寻找 candidate margin、proposal adaptation、support drift 中的 load-bearing variable，而不是再造一个 correlation。进入 I04。

---

## 11. 阅读完整度

**深读/针对性全文（方法+实验+related-work/limitation 关键段落）：** P02, P08, P09, P13, P15, P16, P21, P26, P27, P29, P33, P38, P39；用户上传 RC-aux 主文+实验附录。  
**官方 proceedings + 主文核心/官方代码核对：** P01, P03–P07, P10–P12, P18–P20, P25, P28, P30–P37。  
**定位级但非全部附录逐证明：** 其余直接近邻。  

这里“深读”不等于所有 theorem proof 逐行复核；涉及将来 manuscript-critical 理论主张时必须回原 PDF/源码再次核对。