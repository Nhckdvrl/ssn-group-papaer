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

### P15 — RC-aux — NeurIPS 2026
**来源：** 本项目上传论文 arXiv:2605.07278；代码：https://github.com/Guang000/RC-aux  
**状态核对：** official repo main（2026-10-02）标注 Sep 2026 accepted to NeurIPS 2026；本 workbench 的方法/代码审计仍固定到 ASSETS 中的旧 commit，不能把 main 后续改动混进复现。
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

## 7.5 第二轮 hardening：新增直接近邻与顶会邻接压力（P40–P56）

这一组是第一次登记后继续深挖得到的。它们进一步收紧了“还能说什么”，尤其削弱了 I02 的独立新颖性，并让 I01 必须从“suboptimal trajectory 有偏”升级成**同 local dynamics evidence 下的 trajectory-factorization / routing invariance 问题**。

### P40 — A Control Theory of Predictability in Latent World Models — arXiv 2607.10362
**来源：** https://arxiv.org/abs/2607.10362

- **母问题：** 为什么 held-out single/multi-step prediction error 不能保证 control？
- **改变前提：** planner 真正 query 的不是训练分布，而是 candidate actions 能到达的 planner-reachable measure。
- **理论对象：** predicted vs true plan-cost discrepancy；planner suboptimality 由 commit plan 上的 cost discrepancy 控制，而不是 data-averaged prediction error。在线性 premise 下进一步分 on-manifold residual + spectral/non-normality tax 与 off-manifold divergence。
- **实证：** validation prediction error 与 control success 近乎解耦；planner-reachable fidelity 更跟踪 success。
- **ownership：** “CEM/optimizer 把模型带出 data support，因此平均 prediction error 不够”已经有直接理论 ownership。
- **对 I02：** generic support-drift story 不再是独立 paper seed；E05 只能作为 I03 的 diagnostic，除非出现该 theory/measure 不能解释的更具体机制与 intervention。

### P41 — The Objective Is the Bottleneck — arXiv 2608.12959
**来源：** https://arxiv.org/abs/2608.12959

- **母问题：** long-horizon LeWM 失败究竟是 predictor 先坏，还是 planner 的 latent objective 先坏？
- **关键 intervention：** 不 retrain model，仅替换 planning objective，就把 TwoRoom 远目标成功率大幅恢复；probe 显示 position information 仍在 representation 中。
- **idea-growth：** 从“prediction/representation 好不好”转成“planner 能否用 representation 中已有的信息”。
- **ownership：** “objective 而非 predictor 是 binding bottleneck”“latent 中有信息但 L2 用不好”已被非常直接占位。
- **对我们：** E02 的 encoded-real endpoint ranking 是基础诊断，不是新贡献；I03 必须寻找**跨 regime 的 bottleneck relocation law**，不能只在 TwoRoom 再做 objective swap。

### P42 — Traj-LeWM — arXiv 2608.14125
**来源：** https://arxiv.org/abs/2608.14125  
**代码：** https://github.com/XiaodiHuang-code/Traj_LeWM

- **压力：** endpoint-only scoring 丢掉 intermediate path；local next-step training 也不直接学习 goal-relative full-trajectory quality。
- **方法：** goal-conditioned Latent Trajectory Cost；偏好来自 goal-mismatched expert paths、endpoint-preserving latent perturbations、endpoint-only planner 挖出的 failed rollouts；planning 时 endpoint + LTC。
- **证据：** Push-T、Cube、Reacher、TwoRoom 都报告增益。
- **ownership：** generic“完整 trajectory 比 terminal endpoint 更有信息”“挖 failed rollout 训练 path cost”已占。
- **对 I01：** trajectory-level supervision 本身已是方法赛道；我们的 delta 必须是**这种 supervision 对 trajectory factorization / behavior routing 是否应当 invariant**，不是再加一个 path head。

### P43 — AD-WM — arXiv 2609.30264
**来源：** https://arxiv.org/abs/2609.30264

- **母问题：** factual transition prediction 与 counterfactual MPC 的 action discrimination 是不同要求。
- **方法：** residual latent dynamics + predictor-level action-recovery regularization / conditional-MI-inspired normalized objective；training-only heads。
- **证据：** OGBench-Cube hard-start 以及多环境；paper 还报告 frozen V-JEPA2 + DROID post-training 到 Franka 的 zero-shot transfer。
- **诊断：** factual error / whole-bank action ranking 不按 success 排序，而 CEM-aligned elite regret 更接近 closed-loop outcome。
- **ownership：** counterfactual action distinguishability、CEM elite regret 已强占位。不能把“不同 candidate actions 的未来太像”作为新 story。

### P44 — Control-Geometry Straightening (CGS) — arXiv 2609.35603
**来源：** https://arxiv.org/abs/2609.35603

- **母问题：** predictive latent transition 即使准，sampling-based planner 的目标 landscape 仍可能难优化。
- **方法：** 只用 local pixel-action transitions，把 action-pair cosine similarity 对齐 corresponding latent displacement cosine similarity。
- **理论：** 在线性条件下连接 temporal straightening、terminal-cost curvature，并给 MPPI/CEM/GD 有限预算性质。
- **证据：** 4 control environments、多 planner；128 candidates 下仍报告明显增益。
- **ownership：** “local control geometry 让有限-budget search 更容易”已占。
- **对 I01：** CGS 是很好的**local-transition negative/control baseline**：它不依赖 long-range trajectory gap，因此若 I01 是 route imprinting，CGS/TS 应比 RC-aux/TD-JEPA 更不敏感于 trajectory refactorization。

### P45 — AnisoWM — arXiv 2609.37441
**来源：** https://arxiv.org/abs/2609.37441  
**项目页 repo：** https://github.com/rkdrn79/AnisoWM-page

- **主张边界：** isotropic Gaussian regularization 并非中性；learned anisotropic covariance 可以重排表示几何与 task-relevant directions。
- **ownership：** “SIGReg 的 isotropy 本身塑造 geometry / 换 covariance prior”已被占位。
- **对我们：** latent marginal regularizer 的分布形状属于 representation confound；I01 dataset intervention 必须用同一 regularizer/config，不把 covariance shift 误当 behavior effect。

### P46 — Adaptive Latent Capacity / ALeWM — arXiv 2609.32921
**来源：** https://arxiv.org/abs/2609.32921  
**项目页：** https://github.com/arm-research/AAIR-ALeWM

- **idea：** 学习 prefix-length distribution，把 predictive information 排到 wide latent 的前缀；MixSIGReg 对 masked embeddings 使用 Gaussian-active-prefix + zero-tail mixture。
- **证据：** controlled system + goal-conditioned visual control；报告低于 fixed-width 的平均 planning capacity 同时更高 success。
- **ownership：** latent capacity/coordinate ordering 已形成独立近期路线。
- **对我们：** 不把 latent width/capacity sweep 当新题；它最多是 I03 的 regime variable/control。

### P47 — Toward Physically Grounded JEPA World Models — arXiv 2609.03565
**来源：** https://arxiv.org/abs/2609.03565

- **方法：** inverse dynamics + state alignment，把 latent 与 physical configuration/motion 对齐。
- **证据：** TwoRoom、PushT、Cube、Reacher；state alignment 对 IDM-only 有一致增益。
- **ownership：** “用 privileged physical state 对齐 planning latent”已经有直接方法；simulator state 作为我们 oracle 必须保持 diagnostic 身份，不能悄悄变成公平输入优势。

### P48 — PSG-JEPA / Is Forward Prediction Enough? — arXiv 2608.06799
**来源：** https://arxiv.org/abs/2608.06799  
**代码：** https://github.com/Haodong-Yan/PSG-JEPA

- **方法：** single-latent proprioceptive grounding + latent-pair multi-horizon joint-angle-change grounding；heads 仅训练时使用。
- **证据层：** latent identifiability、frozen-latent goal planning、simulation/real-robot policy learning。
- **ownership：** physical-state / transition grounding 已很拥挤；“forward prediction 不保证 physical identifiability”不能再做 broad headline。
- **工程价值：** official release 与 stable-worldmodel/LeWM 同生态，必要时可作为 privileged grounding baseline，但不是首轮必装。

### P49 — On Capability Separation Between World-Model Policy Learning and Imitated World-Action Models — arXiv 2608.22197
**来源：** https://arxiv.org/abs/2608.22197

- **母问题：** future/outcome factorization 本身是否给 observational imitation 更强的 control capability？
- **理论边界：** 在 realizability/exact optimization/common deployment info 等条件下，imitation-trained world-action policy 与 direct behavior cloning 可恢复同 observational behavior；真正更强的 decision 需要 identified action effects + utility comparison。
- **对我们：** “看到未来/未来 factorization 所以更会决策”不是自动成立；action-conditioned causal/counterfactual evidence 与 observational future statistics 必须区分。

### P50 — Learning Task-Sufficient World Models by Synergizing Agentic Exploration and Structured Modeling — ICML 2026
**来源：** https://proceedings.mlr.press/v306/feng26aa.html

- **母问题：** generic/high-dimensional world state 保留大量 control-irrelevant factors；能否主动收集 informative trajectories 并学习 task-specific minimal sufficient latent？
- **方法：** agentic probing curriculum + structured representation learning，闭环地让数据收集暴露 task-relevant factors。
- **ownership：** broad “task-sufficient/minimal world representation”已经是 ICML-level 主题；P38 的 decision sufficiency 也进一步形式化。
- **对我们：** 顶会尺度不是“latent 小不小”，而是有没有对 task/decision sufficiency 的新识别或结构。

### P51 — Behavior-Invariant Task Representation Learning with Transformer WMs for Offline Meta-RL — ICML 2026
**来源：** https://proceedings.mlr.press/v306/qian26o.html

- **母问题：** offline context/task representation 会随 behavior policy 改，导致 meta-test shift。
- **方法：** information-theoretic behavior-invariant task latent + stochastic transformer WM；conservative value penalty 防 policy/model exploitation。
- **ownership：** “behavior-invariant representation”这个大词本身已被 ICML 2026 直接占用。
- **对 I01：** 我们不能写成泛化的 behavior-invariant representation paper；必须限定为**trajectory-supervised planning geometry 在同 local dynamics evidence 下的 route/factorization dependence**，并落到 MPC candidate ranking/closed-loop。

### P52 — Parallel Stochastic Gradient-Based Planning for World Models — ICML 2026
**来源：** https://proceedings.mlr.press/v306/psenka26a.html

- **方法：** 把 intermediate virtual states 也作为优化变量，用 soft dynamics constraints + stochasticity，使 long-horizon differentiable WM planning 更并行、更易优化。
- **ownership：** “换 optimizer / parallel gradient planning 解决长 horizon”已有 ICML 路线。I03 若比较 planner，必须当 baseline family，不把 optimizer engineering 本身当发现。

### P53 — World-In-World — ICLR 2026 Oral
**来源：** https://proceedings.iclr.cc/paper_files/paper/2026/hash/5b4263be85820683d78675cc18d2efc7-Abstract-Conference.html

- **母问题：** generative WM 的 open-loop visual quality 是否真能转成 embodied utility？
- **贡献：** standardized closed-loop environments/action API + online planning；发现 visual quality 不保证 task success，action-observation post-training 与 inference-time compute 很关键。
- **ownership：** decision-centric / closed-loop evaluation 已是 oral-level显式主题。
- **对我们：** candidate-level diagnostics 必须最后回到 task consequence；但“闭环评估更重要”本身不是 novelty。

### P54 — Sparse Imagination — ICLR 2026
**来源：** https://proceedings.iclr.cc/paper_files/paper/2026/hash/a750d52284ff70c6d6bab8072c392d74-Abstract-Conference.html

- **方法：** randomized grouped attention 训练 transformer WM，使 rollout 时可动态丢 visual tokens。
- **ownership：** test-time token sparsity/compute-quality tradeoff 已有 ICLR；效率不是这条 compact LeWM workbench 的默认新空间。

### P55 — Planning in 8 Tokens / CompACT — CVPR 2026
**来源：** https://openaccess.thecvf.com/content/CVPR2026/papers/Kim_Planning_in_8_Tokens_A_Compact_Discrete_Tokenizer_for_Latent_CVPR_2026_paper.pdf  
**代码：** https://github.com/kdwonn/CompACT

- **idea：** 极端压缩 observation 到 8 discrete tokens，用 semantic guidance 保留 planning-relevant information。
- **证据：** navigation/manipulation planning 与 speed；项目页报告约 40× planning speedup。
- **资源边界：** official repo 的 paper-scale tokenizer/world-model training 使用多 GPU（tokenizer 8 H100、WM 4 RTX 6000 Ada 的默认论文配方），不适合作为首轮核心训练 baseline。
- **ownership：** token-count/compression efficiency 已有 CVPR 路线。

### P56 — GeoWorld — CVPR 2026
**来源：** https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_GeoWorld_Geometric_World_Models_CVPR_2026_paper.html

- **方法：** Hyperbolic JEPA + geometric RL/energy-based planning，目标是保 hierarchy/geometric structure 并缓解 multi-step degradation。
- **ownership：** “非欧 geometry 更适合 latent planning”在大视觉 WM 路线也已有顶会工作；本 workbench 的 geometry claim 不能只靠换 manifold。
- **对我们：** I01 的价值不在选 Euclidean/hyperbolic，而在**training supervision 的 invariance/identification**。



---

## 7.6 截至 2026-10-02 的最后近邻扫：planning interface / intervention / structured dynamics（P57–P63）

### P57 — Hidden Failure Modes in Latent World-Model Planning from Offline Data — ICML 2026 Workshop Oral
**来源：** https://openreview.net/pdf/2970593988c2eb8f2bd6612fdaa898f0dbd7b107.pdf  
**代码：** https://github.com/24GUNV/LeWMRO

- **母问题：** closed-loop receding-horizon MPC 中，planner optimize (H) 步却只执行 (K<H) 前缀；terminal-at-(H) cost 到底在测 model quality 还是一个永远不会直接执行的时间点？
- **关键结果：** standard tasks 上，prefix-at-(K) / running cost 能大幅修复 terminal-at-(H)；但 deceptive TwoRoom Far Door 中 scalar latent objectives 仍弱，waypoint/local-actuator interface 才显著恢复。
- **ownership：** replanning interval / score time-index mismatch、scalar objective vs controllability-interface mismatch 已有直接工作。
- **对 I03：** (H,K)、scoring index、action chunk、replanning ratio 必须作为 oracle ladder 的**protocol layer**，否则很容易把 evaluation interface bug 误判成 representation/dynamics bottleneck。
- **对 I01：** 它不是 trajectory-factorization 工作；但 E03/E04 的 closed-loop consequence必须固定 (H,K)/cost timing，避免 route effect 被 planning-interface artifact污染。

### P58 — PhyLatent — arXiv 2608.05720（updated 2026-09-29）
**来源：** https://arxiv.org/abs/2608.05720

- **失败分解：** appearance-preserving physical invariance、distinct physical-state distinguishability、counterfactual action-conditioned future separation 三类“global non-collapse 仍可能失败”的 representation/dynamics collapse。
- **方法：** physical state grounding、future alignment、static visual invariance、counterfactual branch separation、latent denoising。
- **ownership：** broad “SIGReg noncollapse 不等于 dynamics-relevant representation”已经非常拥挤；physical/counterfactual collapse 也不能重命名。
- **对我们：** I03 的 representation layer必须能区分 “metric unusable” 与 “physical state/action effect 本就没保留”。

### P59 — Do-JEPA — arXiv 2609.37378
**来源：** https://arxiv.org/abs/2609.37378

- **母问题：** factual prediction只观察 executed action，无法直接区分 action caused what vs co-occurred what。
- **intervention：** 从同一 saved simulator state 分别执行 action (a) 与 reference action (a_{∅})，直接监督 latent effect difference。
- **方法：** effect/support/propagation/invariance losses；synthetic + CausalWorld + pixel LeWM。
- **ownership：** “真正 physical intervention 比 visual masking 更能识别 causal action effect”已被直接提出。
- **对 I01/I03：** common-reset intervention 是**强 oracle / positive control**，但它需要 simulator counterfactual branches，和我们“固定 offline local transition evidence，只改变 trajectory organization”的问题不同。若最终 I01 方法需要额外 counterfactual environment interaction，就必须和 Do-JEPA/FIRM-WM 明确区分成本与 setting。

### P60 — Bilinear World Models — arXiv 2609.36305
**来源：** https://arxiv.org/abs/2609.36305

- **idea：** 不让 latent dynamics 任意 nonlinear；限制成 bilinear structure，把表示学习压力推到 encoder，同时可以 structurally enforce action recoverability。
- **证据：** standard 2D/3D control、longer-horizon、real-time control；作者报告近三数量级 planning-time降低并保持/提高 accuracy。
- **ownership：** structured dynamics / action recoverability / efficient planning 又多一个强近邻。SALT 不是唯一 structured-transition baseline。
- **对 I03：** dynamics intervention family 以后不能只代表 “LeWM vs SALT”；若 lead落到 structured dynamics，要定位 state-affine vs bilinear 的不同 inductive bias。

### P61 — One-Step Next-Latent Prediction Is Not a World Model — arXiv 2609.36227
**来源：** https://arxiv.org/abs/2609.36227

- **理论压力：** one-step regression通常识别 conditional mean，不等于完整 transition kernel；nonlinear conditional mean 的 composition也不等于 multi-step conditional mean；non-injective observation下 memoryless one-step map甚至不能决定 future observations。
- **ownership：** “one-step next-latent objective 本身不足以定义 rollout-capable WM”已经有明确理论文章；不能把这个作为新 headline。
- **对 I03/I05：** history / stochasticity / transition-kernel sufficiency是理论 confound；如果 experiment 落到 stochastic/POMDP，必须区分 deterministic-mean limitation 与 planning geometry问题。

### P62 — FIRM-WM — arXiv 2609.22816
**来源：** https://arxiv.org/abs/2609.22816

- **两个 mismatch：** goal-comparable coordinates 与 history-dependent dynamics 需要不同 state roles；offline factual trajectory只给一个 future，而 sampling planner query counterfactual actions。
- **方法：** typed goal-comparable configuration + 128-d dynamic fiber；broad factual trajectories + same-reset intervention branches。
- **证据：** TwoRoom/Reacher/Cube，三 full-pipeline seeds；compact 3M级 deployed model。
- **ownership：** state factorization + common-reset counterfactual data 已是直接 2026 方案。
- **对我们：** 若 I03 落到 “goal representation vs recurrent dynamics应分开” 或 “需要 paired counterfactual branches”，FIRM-WM 是强 collision。I01 仍不同：它问相同 local factual evidence的**trajectory organization invariance**。

### P63 — FF-JEPA — arXiv 2606.09311
**来源：** https://arxiv.org/abs/2606.09311

- **方法：** standard action-conditioned forward WM + action-free latent planner预测下一 subgoal，把长任务拆成短期优化；同时减弱 explicit goal-image依赖。
- **ownership：** “learn latent subgoal planner来救长 horizon”又一个直接邻居；和 HWM/SAGE/Anchored Planning共同压缩 hierarchy/subgoal空间。
- **对 I03：** temporal-target层已有非常多方法；只有 regime law 或 identification 能支撑新贡献。



---

## 7.7 Cross-trajectory supervision 的邻域：谁把“另一条轨迹”当什么？（P64）

### P64 — Conservative Offline Goal-Conditioned Implicit V-Learning — ICML 2025
**来源：** https://proceedings.mlr.press/v267/ke25a.html

- **母问题：** offline GCRL 中，same-trajectory HER 不会自然解决 stitching；直接采 cross-trajectory state-goal pairs 又会把 connected 与 unconnected pairs 混在一起，导致 value overestimation。
- **方法：** 对 unconnected pairs 做 conservative penalty；对 connected pairs 借助 quasimetric structure 学值。
- **关键区分：** “来自不同 trajectory”本身**不是**环境 reachability / connectivity 的语义标签。
- **与 TD-JEPA / RC-aux 的镜像关系：**
  - CGCIVL 警惕把 cross-trajectory pair 当可连接正样本；
  - TD-JEPA / RC-aux 则把 cross-trajectory / cross-batch goal 用作 far/unreachable **负样本**；
  - 两边都说明 trajectory identity 是 data-collection metadata，不是 MDP connectivity 本身。
- **ownership：** “cross-trajectory pairs 需要区分 connected/unconnected”本身已经 ICML 2025；我们不能把“false negatives exist”当新发现。
- **打开的 WM-specific pressure：** plan-aware latent WMs 把 heuristic negatives 直接写进**planning cost / reachability semantics**，同时这些 negatives 又可能承担 global separation / representation regularization。它们的 semantic role 与 regularization role 是否被混在了一起，尚需用真实 planner consequence 分解。这个 tension 进入新 I06。

### Background — Contrastive RL / InfoNCE negative sampling
在标准 contrastive RL / density-ratio interpretation 中，negative goals通常作为 replay-marginal samples进入 normalization/density-ratio objective，**不等价于逐对声明“这个 goal 不可达”**。TD-JEPA 的 margin hinge和 RC-aux 的 BCE 0-label 则给 pair 一个更强的 planning semantic。  
因此 I06 的概念区分不是“contrastive learning 有 false negatives”（老问题），而是：

> **sampling negatives for normalization/repulsion** 与 **asserting semantic non-reachability / far-distance labels** 是不同 statistical roles；plan-aware WM objectives 可能把二者合并。


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

## 12. Problem-led hardening：belief、explicit/implicit、goal interface 与真实 invariance（P65–P74）

### P65 — Bagatella TD-JEPA — ICLR 2026 Oral
**正式标题：** *TD-JEPA: Latent-predictive Representations for Zero-Shot Reinforcement Learning*  
**来源：** https://proceedings.iclr.cc/paper_files/paper/2026/hash/3d158f054ff0cb83397367234899db07-Abstract-Conference.html  
**代码：** https://github.com/facebookresearch/td_jepa

- **母问题：** one-step latent prediction为什么只能当辅助 signal？能否用 TD learning 从 reward-free offline transitions 中学跨 policy 的 long-horizon predictive structure，并直接支持 zero-shot RL？
- **idea leap：** 不把未来只表示成逐步 rollout；state/task encoders + policy-conditioned multi-step predictor 学 latent successor features，同时训练一族 latent policies。
- **理论角色：** idealized setting 下表示学习 low-rank long-term policy dynamics，predictor恢复 successor-feature structure。
- **证据：** ExoRL + OGBench 共 13 datasets，state/RGB，navigation/locomotion/manipulation；官方 ICLR 2026 oral。
- **与 explicit JEPA-WM 的关键距离：** DINO-WM/JEPA-WM/LeWM 学 action-conditioned **explicit rollout model**，把 task/cost 留到 test-time planner；Bagatella TD-JEPA把 long-horizon policy occupancy structure **amortize** 到 representation/predictor/policies中。
- **claim ownership：** “TD latent prediction / successor features支持 reward-free zero-shot RL”已占。
- **打开压力：** TMLR P09 的最终讨论明确把 explicit vs implicit 的 training cost、inference cost、generalization trade-off 的 direct empirical comparison 留为未来方向。进入 M2/I08。
- **命名警告：** P65 与 P14 **Bai/Xiong Temporal-Distance JEPA** 完全不同；P14历史 config 名 `td_jepa` 不能当论文简称使用。

### P66 — UWM-JEPA — arXiv 2605.25313
**来源：** https://arxiv.org/abs/2605.25313  
**代码：** https://github.com/santoshkumarradha/uwm-jepa

- **母问题：** POMDP 中当前 history可能对应多个 hidden futures；普通 vector point latent如何在 blind rollout 中携带一个 belief？
- **idea leap：** density-matrix latent + learned unitary predictor，把 uncertainty作为 latent内部结构而非只在输出端估计。
- **关键实验：** hidden-velocity indicator；action sequence被 perturb时 UWM-JEPA-CF accuracy单调下降，matched LSTM-JEPA停在 majority level；context probe相近，把差异定位到 predictor/rollout而非 encoder capacity。
- **重要边界：** 证据主要是 controlled hidden-state prediction；不是 image-goal MPC 的完整闭环论文。
- **ownership：** “belief-space JEPA / point latent不能自然携带hidden-future uncertainty”已有直接工作。
- **打开压力：** belief uncertainty 何时真正改变 candidate action ranking与closed-loop goal planning？进入 M1/I07，而不是再做 hidden-state probe。

### P67 — Flow Equivariant World Models — ICML 2026
**来源：** https://proceedings.mlr.press/v306/lillemark26a.html

- **母问题：** partial observation下，out-of-view world仍在运动；unstructured recurrent/video memory难以维持与self-motion/external motion一致的 hidden state。
- **idea leap：** latent memory按连续 flow / self-motion equivariance组织并随动态更新。
- **证据：** 2D/3D partially observed dynamic video WM，对 diffusion/memory/recurrent baselines。
- **ownership：** “structured memory解决partial observability和out-of-view dynamics”已有 ICML级工作。
- **对 M1：** 我们不能把 memory 本身当 novelty；必须落到 compact goal-conditioned planner 的 decision sufficiency / belief action consequence。

### P68 — What Capable Agents Must Know — UAI 2026
**来源：** https://proceedings.mlr.press/v337/nayebi26a.html

- **母问题：** belief/world model可实现 optimal control早已知道，但强行为是否**迫使** agent拥有某类 internal predictive structure？
- **结果：** selection theorems把低 average regret与必要 predictive distinctions联系起来；partial observability 下得到 predictive-state / belief-like memory 的必要性结果。
- **ownership：** “低regret需要belief-like memory”已有理论锚点。
- **对 M1：** empirical novelty必须问现实 compact visual planner **何时**这项必要性变成 load-bearing，以及怎样在 image-goal接口中满足，而不是重述 POMDP 教科书。

### P69 — Latent WMs with Monotone Planning Costs for Image-Goal Navigation — arXiv 2608.09073
**来源：** https://arxiv.org/abs/2608.09073

- **母问题：** latent prediction可以不错，但 CEM 真正消费的是 candidate cost ordering。
- **方法：** frozen DINO-family encoder + autoregressive rollout + Monotone Cost Ranking，直接让 action perturbation与planning cost保持单调。
- **重要结果：** 还比较 InfoNCE-style action contrastive training，报告 temporal-permutation negatives 会扭曲 geometry 并降低 planning。
- **ownership：** “negative construction会改变planning geometry / cost ordering”已有直接证据。
- **对 I06/M3：** I06 不能写成 generic “negatives distort geometry”；只能研究 **behavior/cross-trajectory semantic labels 与 non-semantic regularization roles 的分离**，且必须有更大的 data-semantics consequence。

### P70 — Grounded World Model for Semantically Generalizable Planning — arXiv 2604.11751
**来源：** https://arxiv.org/abs/2604.11751

- **母问题：** visual MPC依赖 goal image，但现实 task 不总有目标图，而且 image goal难表达 language semantics。
- **idea：** 把 WM 放在 vision-language-aligned latent，未来 rollout直接按 instruction embedding评分。
- **证据：** WISER 288 test tasks，unseen visual signals/referring expressions；作者报告 GWM-MPC 87% success，而所比较 VLA平均22%。
- **ownership：** “language/semantic goal interface for WM-MPC”已有直接工作。
- **对本 workbench：** goal/query modality是重要 pressure，但不再是容易空白；M1–M3的方法最好至少检查 goal interface transfer，不另起“把语言接进WM”的增量题。

### P71 — Robot World Models Are Not Invariant to How the Actions Are Written — arXiv 2609.23252
**来源：** https://arxiv.org/abs/2609.23252

- **母问题：** absolute target与delta action可互相重建、表示同一 commanded trajectory，WM 是否应对这种 action reparameterization保持一致？
- **观察：** 作者报告 latent dynamics 在等价 action encoding切换时会出现严重 retrieval / goal-conditioned selection退化；不是简单信息丢失。
- **修复：** objective averaging + disagreement penalty。
- **为什么重要：** 是 problem-led 选题范例：一个**真实接口等价性**被模型破坏，直接影响 action selection，然后最小修复从 failure定义自然长出。
- **ownership：** action-parameterization invariance本身已占，不能照搬。
- **对我们：** 寻题时优先这种“领域默认等价关系/接口假设被破坏且真的改变决策”的问题，而不是任意 probe anomaly。

### P72 — World Models for Embodied Intelligence: Plausible → Controllable → Actionable — survey 2609.16697
**来源：** https://arxiv.org/abs/2609.16697

- **组织原则：** Plausible保 task-relevant structure；Controllable要求 intervention改变 prediction的方式正确；Actionable要求 prediction真正改变并改善 planning/action/learning/evaluation/recovery/data selection。
- **对我们最关键：** world model的价值不在 visual/predictive metric本身，而在 downstream behavior；survey列出的核心挑战包括 long-horizon consistency、uncertainty calibration、causal intervention testing、latency、verification/recovery、cross-embodiment transfer。
- **workbench rule：** 新 probe 若无法连到 Controllable / Actionable consequence，只能是诊断工具，不足以成为 paper mother question。

### P73 — Objective mismatch / Goal-aware / Value-equivalence historical anchors
**来源：**
- Lambert et al., *Objective Mismatch in Model-based Reinforcement Learning*, L4DC 2020.
- Nair et al., *Goal-Aware Prediction: Learning to Model What Matters*, ICML 2020.
- Grimm et al., *The Value Equivalence Principle for Model-Based Reinforcement Learning*, NeurIPS 2020.

- **共同教训：** 完整 transition prediction从来不是控制唯一目标；task-aware / value-equivalent model可以只保留decision-relevant structure。
- **对 2026 compact JEPA：** “planning alignment优于 prediction”不是新哲学。真正新的工作必须说明在 modern reward-free visual planning 中 **哪个 sufficiency / reuse / intervention boundary** 没被旧理论和 P38覆盖。

### P74 — I-TAP: In-Context Planning with Latent Temporal Abstractions — arXiv 2602.18694
**来源：** https://arxiv.org/abs/2602.18694

- **母问题：** primitive-time planning既长且分支爆炸，真实环境又partial observable并会有 latent dynamics regime shifts。
- **方法：** observation-conditioned residual-quantization VAE把 observation–macro-action segment压成 coarse-to-fine tokens；history-conditioned temporal Transformer预测 token；MCTS在 token space规划。
- **证据：** deterministic/stochastic MuJoCo、per-episode latent regimes、Adroit及 partial-observation variants。
- **ownership：** “history + temporal abstraction处理 POMDP/regime shift”已有直接路线。
- **对 M1：** 新工作不能只是加 history token；必须把 **visual goal equivalence vs hidden control state / belief** 的决策结构说清。

## 13. 这轮 hardening 对 workbench 的改变

以前的 yellow zones 更像 component list；现在优先变成三个 **problem families**：

1. **M1：state-definition problem** — observable goal state 与 hidden control belief不等价。
2. **M2：computation-placement problem** — predictive structure显式 rollout还是隐式 amortize。
3. **M3：identification problem** — offline behavior statistics何时能代表 environment controllability。

I06 是 M3 的一个小切片；I03 oracle ladder是三条线共用的 scientific instrument。  
这三条都只有在产生 **Actionable consequence** 后才允许长成主张。

## 14. Second hardening pass — stochasticity, physical identifiability, adaptation, query generality, latent actions（P75–P89）

### P75 — Physically Viable World Models — arXiv 2605.30542
**来源：** https://arxiv.org/abs/2605.30542  
**代码：** https://github.com/pvwm/physically-viable-world-models

- **母问题：** observation prediction何时从根上不足以支持 embodied intervention？同样的可见场景若隐藏 mass/friction/compliance/viscosity/contact state 不同，会在同一 action 下产生不同真实结果。
- **关键 pressure：** 作者明确把 failure 定义为 structural identifiability problem，而不是“模型还不够大”；passive observation可能无法识别决定 intervention outcome 的 latent physics。
- **方法观：** query-conditioned physical abstraction——按 query 选择需要的 state variables、latent parameters、action interface、interventional dynamics、constraints 与 response；必要时估计/维护 uncertainty 或主动获取信息。
- **决定性证据：** controlled simulations固定/近似固定 appearance 与 action，同时改变 density、restitution、friction、contact height、viscosity等；覆盖 VLM、video diffusion、action-conditioned latent control，并展示 physically infeasible planning / wrong outcome。
- **ownership：** broad “same pixels can hide different physics / visual predictor不等于 physically viable intervention model”已被直接提出。
- **对 M1：** 大幅压缩了“same observation + hidden physics → different action”的 novelty。I07 若继续，必须限定到 **compact reward-free image-goal MPC 中的 history-resolvable vs irreducible aliasing / belief decision regret**，并和 query-conditioned parameter identification 明确区分。
- **idea-growth 值得学：** 从视觉预测“看起来对”切到 intervention query“答得对”，问题尺度自然大于一个 probe。

### P76 — Branch-JEPA（原 v1 名 MoP-JEPA）— arXiv 2607.05238
**当前版本标题：** *Branch-JEPA: Finite-Support Predictive Distributions for JEPA World Models*。  
**来源：** https://arxiv.org/abs/2607.05238

- **版本风险：** v1/早期搜索结果仍可能显示 “MoP-JEPA: Hard-Assigned Predictor Mixtures…”，截至 v3 已更名为 Branch-JEPA，主方法/叙事也有调整。引用必须锁版本。
- **母问题：** point-valued JEPA transition在 stochastic / hidden-intent / partial-observation branching下只给一个 successor，无法保留多个可行未来。
- **方法：** context-weighted finite set of latent successors；specialization 与 full-set Energy-Score 两种训练；所有 branch inference-time保留。
- **证据：** Argoverse 2多模态 future + OGBench graph audit；当前 v3 abstract报告 latent branching比output-only branching保留更多有效 modes，OGBench teleport verified-route existence 19.2% vs MDN 3.9%，并在state/RGB都保留raw-support优势。
- **ownership：** generic “deterministic latent regression collapses multimodal futures / need branching predictive distribution”已经非常直接；M1不能把 stochastic multi-hypothesis prediction本身当新方法。
- **对 workbench：** 若 E11/E12最终需要 belief，必须解释是 **epistemic hidden-state ambiguity**、aleatoric transition multimodality，还是两者；Branch-JEPA 是后者/混合未来的强对照。

### P77 — Var-JEPA — ICML 2026
**来源：** https://proceedings.mlr.press/v306/gogl26a.html

- **母问题：** JEPA是否真的与 probabilistic generative modeling结构不同？uncertainty能否在统一 variational objective 中自然出现？
- **方法：** 将 coupled encoders + predictor 解释为 latent-variable variational structure，导出 ELBO-based Var-JEPA。
- **证据边界：** 当前主实例是 tabular representation learning，并非 visual planning。
- **ownership：** “给JEPA加principled variational uncertainty”作为 broad architecture claim已有 ICML precedent。
- **对我们：** 只作为 M1 belief/uncertainty 的 conceptual control；不能用“variational JEPA”四个字当 novelty。

### P78 — AdaJEPA — arXiv 2606.32026
**来源：** https://arxiv.org/abs/2606.32026  
**代码：** https://github.com/agentic-learning-ai-lab/adajepa

- **母问题：** frozen latent WM 遇 test-time distribution shift 后 prediction不准，为什么 MPC 每次真实执行得到的新 transition不能拿来在线校准？
- **方法：** execute action chunk → observe next transition → one/few self-supervised gradient update → replan。
- **关键证据：** 作者报告 goal-reaching shift settings 中即使每次 replanning只做一次gradient step也显著改善 success。
- **ownership：** generic “closed-loop test-time self-supervised adaptation of latent WM”已占。
- **对我们：** domain/dynamics shift 不能单独变成新 mine；若 M2/M3 涉及 shift，AdaJEPA必须是 adaptation control，而不是重新发现 frozen model不稳。

### P79 — Sandwich-Residuals — arXiv 2609.21740
**来源：** https://arxiv.org/abs/2609.21740

- **问题：** AdaJEPA式内部权重适配需要改大量参数；能否只在 predictor前后学习小 residual？
- **证据：** 21个 AdaJEPA benchmark conditions；作者报告约保留 strongest AdaJEPA 95% performance，同时适配参数少 97–99%；compound shift下相对 frozen model提升更大；另在 DINO-WM 3D manipulation验证。
- **ownership：** 参数高效 test-time WM adaptation 已快速拥挤。
- **结论：** adaptation放入 WATCH / baseline，不作为我们低 hanging fruit。

### P80 — Compositional Planning with Jumpy World Models — ICML 2026
**来源：** https://proceedings.mlr.press/v306/farebrother26a.html

- **母问题：** primitive-action long-horizon planning的 horizon/branching太大；如果动作本身是预训练 policy，如何预测它在多时间尺度上的 state occupancy 并组合？
- **方法：** off-policy multi-step “jumpy” world models，预测 policy-induced occupancies；跨 timescale consistency；组合任意 policy sequences估 value。
- **决定性证据：** navigation/manipulation上 compositional planning；论文报告 long-horizon tasks 平均约 200% relative improvement over primitive-action planning。
- **ownership：** implicit/multi-timescale predictive abstraction 并不只有 Bagatella TD-JEPA；M2 必须包含 policy-level jump models这一中间形态。
- **对 M2：** 更支持“predictive computation placement是一条 spectrum”，但也提高 hybrid novelty门槛。

### P81 — WorldTest — ICML 2026
**正式标题：** *Benchmarking World-Model Learning with Environment-Level Queries*  
**来源：** https://proceedings.mlr.press/v306/warrier26a.html

- **母问题：** next-step/trajectory-return评测只问 observed interaction 上的问题；一个general world model是否支持关于整个 environment 的多种 global / counterfactual queries？
- **方法/贡献：** environment-level query protocol；测试 model能否回答多个不同类型的环境问题，而非只复现 observed trajectories。
- **ownership：** “world model应该支持多query / general-purpose environment knowledge”已经是 ICML benchmark-level主题。
- **对 M4：** query generality很重要，但 broad benchmark story已被占；我们的 planning-alignment method若声称“world model”，应把 cross-query reuse 作为 stress test。

### P82 — D-JEPA — arXiv 2609.24749
**正式标题：** *D-JEPA: A Decision-Aligned Latent World Model*  
**来源：** https://arxiv.org/abs/2609.24749

- **母问题：** planner真正关心少数 competing candidates；平均 prediction / global latent distance不保证它们之间的 ordering正确。
- **定义：** decision-local prediction gap——被预测得更接近goal的candidate，真实执行可能比另一可选candidate更差。
- **方法：** bounded permutation-equivariant candidate-set operator + ordinal executed-outcome evidence + restricted predictor adaptation，将 decision relation重新写回JEPA-compatible future representation。
- **证据：** latent control、manipulation、pretrained action producers、physical robots、autonomous driving；abstract报告 PushT 87.89%，RoboTwin平均 +15.04 points，physical robot +17 points。
- **ownership：** candidate-local decision alignment / ordinal executed-outcome correction 已有直接强近邻。
- **对 I03/M4：** “只关注elite candidates”本身不新；E02 random→elite gap继续只是 calibration。任何 decision alignment paper必须和 P82 exact delta。

### P83 — DDP-WM — ICML 2026
**来源：** https://proceedings.mlr.press/v306/yin26l.html

- **母问题：** dense Transformer dynamics在MPC中太慢，而且场景变化并不均匀。
- **idea：** latent evolution分 primary physical-interaction dynamics 与 context/background update，dynamic localization + cross-attention分配compute。
- **证据：** navigation、tabletop、deformable/multi-body interaction；论文报告 Push-T约 9× inference speedup，并从90%提升到98% MPC success。
- **ownership：** “稀疏/解耦 dynamics既快又更适合planner”已是 ICML-level路线。
- **资源判断：** 可作为效率上界/邻居；我们的核心资源优势不需要再做 dense-vs-sparse architecture race。

### P84 — Learning Latent Action World Models in the Wild — ICML 2026
**来源：** https://proceedings.mlr.press/v306/garrido26a.html

- **母问题：** world model需要action annotation，但互联网视频没有统一action space / embodiment。
- **方法/发现：** constrained continuous latent actions比VQ更适合复杂in-the-wild视频；无共同 embodiment 时 latent actions呈 camera-localized；再训练 controller把known action映到latent action。
- **证据：** latent actions可跨视频迁移，并支持 planning到action-conditioned baseline水平。
- **ownership：** “从无action视频学latent action接口并用于planning”已是ICML主题。
- **资源判断：** 数据/视频/I/O与我们弱存储条件不友好，不进入compact workbench首轮。

### P85 — Cross-Embodiment Robot Foundation WMs with Latent Actions — ICML 2026
**来源：** https://proceedings.mlr.press/v306/huang26bv.html

- **母问题：** explicit action coordinates随embodiment分裂，如何让一个WM跨机器人迁移？
- **方法：** shared unified latent action space (LAC-WM)。
- **证据：** dexterous manipulation + modified LIBERO；论文报告相对 explicit-action WM最多 +46.7% / +11.7%，且随pretraining embodiment数量增长有正向scale，而explicit action反而下降。
- **ownership：** cross-embodiment universal action interface 已直接占。
- **对我们：** action-interface invariance是大问题，但需要多embodiment数据，暂不优先。

### P86 — Co-Evolving Latent Action World Models — ICML 2026
**来源：** https://proceedings.mlr.press/v306/wang26kz.html

- **母问题：** LAM与WM两阶段分开训练既重复又限制co-adaptation；直接joint train又容易collapse。
- **方法：** warm-up先对齐 from-scratch LAM 与pretrained WM，再co-evolve。
- **证据：** video simulation + downstream visual planning，匹配/超过two-stage methods。
- **ownership：** latent-action ↔ world-model joint co-adaptation 已被占。

### P87 — DiLA — ICML 2026
**来源：** https://proceedings.mlr.press/v306/zhang26ec.html

- **母问题：** latent action abstraction与高保真 generation之间的tradeoff。
- **方法：** content/structure disentanglement，让 predictive bottleneck推动action/structure分离。
- **证据：** generation、action transfer、visual planning、manifold analysis。
- **ownership：** latent-action disentanglement + visual planning 已有ICML路线。

### P88 — ReDRAW — L4DC 2026
**正式标题：** *Adapting World Models with Latent-State Dynamics Residuals*  
**来源：** https://proceedings.mlr.press/v331/lanier26a.html

- **母问题：** sim-pretrained visual WM遇 real dynamics mismatch时，像素/显式state residual难学；能否只校准 latent dynamics residual？
- **方法：** freeze pretrained WM，在少量 reward-free target data上学习 latent autoregressive residual，再在corrected WM中优化agent。
- **证据：** vision DMC + physical Duckiebot lane following。
- **ownership：** low-data latent-dynamics residual sim-to-real adaptation 已占。

### P89 — Feedback World Model — arXiv 2605.15705
**来源：** https://arxiv.org/abs/2605.15705

- **母问题：** static open-loop predictor遇 shift会漂；执行后拿到真实 observation，为什么不把 prediction residual作为observer feedback？
- **方法：** inference-time lightweight feedback state，不更新model parameters；action-aware guidance强调 controllable components。
- **证据：** LIBERO-Plus、Robomimic、real manipulation；abstract报告 prediction error最多降76.4%，OOD success +30%。
- **ownership：** “execution feedback / observer correction world model”已有直接路线。
- **对 M1/M3：** closed-loop feedback是重要baseline，不能把“真实执行可以纠正latent state”当新发现。

## 15. Saturation updates from P75–P89

这轮调查会改变 mining 优先级，而不是只增加 citations：

- **generic POMDP / hidden physics / stochastic branching：明显更拥挤。** P75 + FIRM-WM + UWM-JEPA + Branch-JEPA + Flow-Equivariant 已分别占 physical identifiability、typed state、belief latent、multi-future distribution、structured memory。
- **generic test-time adaptation：红区。** AdaJEPA、Sandwich-Residuals、ReDRAW、Feedback WM 已形成完整路线。
- **generic latent action / universal action space：资源不匹配且ICML密集。** P84–P87证明这是重要领域，但不适合作为本 compact workbench首轮。
- **generic efficiency：红区。** Fast-LeWM、Bilinear WM、DDP-WM、RP1等已经覆盖 training/transition/planner efficiency。
- **M2仍增强：** P65 + P80 表明 explicit↔implicit 不是二分而是从 primitive dynamics、successor structure、policy-level jump model到hybrid的连续谱；P09明确留出了 direct empirical frontier。
- **M3仍增强：** 这些新工作没有替代“behavior trajectory semantics何时等于 environment controllability”的 identification 问题；但必须更严格控制coverage/support。
- **M1收紧：** 不再把“same observation, hidden state不同”本身视为novel pressure；只有 **history-resolvable vs irreducible uncertainty 的 decision boundary**、且对compact image-goal planner load-bearing，才值得继续。

## 16. Additional ICML 2026 pressures discovered in proceedings sweep（P90–P92）

### P90 — Action-Sufficient Goal Representations — ICML 2026
**来源：** https://proceedings.mlr.press/v306/hyeon26a.html

- **母问题：** hierarchical offline GCRL里 goal representation常由value learning产生；即使 value estimation exact，它是否保留了 low-level action selection 所需的 distinctions？
- **理论区分：** value sufficiency **不推出** action sufficiency。
- **方法/发现：** information-theoretic action-sufficiency condition；standard policy log-loss自然诱导 action-sufficient representation；actor-derived goal representation优于value-derived。
- **ownership：** “goal representation里有足够value信息但不一定足够选动作”已有 ICML 理论/实证工作。
- **对 M1/M4：** goal-comparable / decision-sufficient state的 broad story更拥挤；M1 必须是 hidden-state belief造成的 **current-state** actionable aliasing，而不是再定义一个goal sufficiency概念。

### P91 — Policy-Driven World Model Adaptation for Robust Offline MBRL — ICML 2026
**来源：** https://proceedings.mlr.press/v306/chen26fl.html  
**代码：** https://github.com/Agentic-Intelligence-Lab/ROMBRL

- **母问题：** 两阶段 offline MBRL 先最大似然学 model、再优化 policy，有 objective mismatch；policy又会exploit model。
- **方法：** policy与world model在统一 robust maximin / Stackelberg learning dynamics下共同适配。
- **证据：** 12 noisy D4RL MuJoCo + 3 stochastic Tokamak tasks。
- **ownership：** “让world model随policy objective共同adapt解决robustness”已是ICML路线；M2如果发展hybrid方法，不能简单 joint-train model/policy。

### P92 — Offline RL with Universal Horizon Models — ICML 2026
**来源：** https://proceedings.mlr.press/v306/chung26b.html

- **母问题：** recursive imagined rollouts compounding error；geometric horizon models直接预测discounted future但远future仍难。
- **方法：** direct prediction under arbitrary horizons + winsorized horizon distribution做value learning。
- **证据：** 100 OGBench tasks，尤其suboptimal-data与long-horizon tasks提升。
- **ownership：** arbitrary-horizon predictive abstraction / direct future modeling 已有强ICML方法。
- **对 M2：** explicit one-step rollout vs implicit successor representation之间还有“direct arbitrary-horizon model”这一中间点；M2应研究 continuum，而不是二分类。


### P93 — How Should World Models Be Evaluated? A Decision-Making-Centric Position — arXiv 2606.15032
**来源：** https://arxiv.org/abs/2606.15032

- **母问题：** “world model”覆盖 video predictor、latent simulator、planning model、synthetic-data engine 等不同对象，但论文经常用低层生成/预测指标支持高层 decision claim。
- **框架：** L0–L7 evidence ladder，从 visual plausibility逐渐上升到 counterfactual action fidelity、policy ranking、planning/optimization lift、model exploitability与decision utility。
- **对本 workbench：** 把“probe显著”与“真实科研问题”明确分开。representation/probe可以帮助定位，但如果 claim 是 planning / controllability，至少要把证据推进到 candidate decision / intervention / closed-loop层。
- **ownership：** “world model evaluation应decision-centric”本身不是新 claim；我们的贡献只能是具体 problem / law / method。

### P94 — On the Identifiability of Controlled World Models — arXiv 2607.22430
**来源：** https://arxiv.org/abs/2607.22430

- **母问题：** action-conditioned latent prediction什么时候真的识别了 latent state 与 controlled transition，而不是只拟合 behavior-policy conditional mean？
- **理论核心：** 两个 policy-dependent margin：
  1. predictable-signal spectral separation → representation identifiability；
  2. conditional action-excitation margin `rho_tr(pi)` → transition identifiability。
- **关键反常：** action-conditioned predictor并不自动解决 counterfactual identification。若给定 state 后 action variation很弱，多个 predictor可以在 behavior data 上同样好，却对 counterfactual actions完全不同；论文给出 counterfactual/on-policy error amplification约受 `1/rho_tr` 控制。
- **决定性实验：** 保持 representation regime / action marginal等条件，改变 conditional action excitation；on-policy prediction仍可好，但 counterfactual reachable set / goal-conditioned planner selection明显变坏。common candidate bank用于 planning consequence。
- **claim ownership：** “behavior-policy action coverage决定 controlled WM transition identifiability / counterfactual planning”已被直接理论化和验证。
- **对 M3 的影响：** **非常关键的 confound / sharpening**。E14 若只是换 behavior policy并看到planning变化，会被 P94 压缩成 action-excitation / coverage effect。M3 只有在 **conditional action excitation + one-step transition support 已匹配/控制** 后，trajectory-derived temporal semantics仍继承 route/tempo，才形成新 delta。
- **新的 exact separation：**
  - P94 = behavior policy决定“动作效应是否可识别”；
  - M3 = 在动作效应已经可识别、local transition evidence相近时，**higher-order trajectory organization / temporal supervision是否额外把 behavior geometry写进planner semantics**。

### P95 — Hitting Time Isomorphism for Multi-Stage Planning with Foundation Policies — arXiv 2605.06470
**来源：** https://arxiv.org/abs/2605.06470  
**代码：** https://github.com/MagnusBoock/IEL

- **母问题：** offline foundation policy若要支持多阶段规划，latent geometry能否真正表示 controlled Markov process 的 directed hitting-time structure，而不是只得到对称相似度或不满足triangle inequality的 embedding？
- **理论对象：** expected hitting time；作者构造 Hilbert-space displacement geometry，在 latent linear closure 下给出 identifiability up to bounded linear isomorphism；finite-dimensional error又由 one-step transition error × transient spectral-radius amplification控制。
- **特别重要：** 论文明确在有限样本分析中纳入 **trajectory-label mismatch**；算法 IEL 用 explicit hitting-time regression + HILP-style consistency，让 geometry 更贴近 decision-time progress。
- **证据：** offline maze locomotion；graph-based multi-stage planning；官方 repo 基于 HILP，含 AntMaze/Kitchen example。
- **ownership：** “直接从 hitting-time supervision学 asymmetric/compositional planning geometry”“trajectory-label mismatch需要理论处理”已有强近邻。
- **对 M3：** 进一步压缩 method novelty。若 E14成立，不能简单提出“回归 hitting time / 加 triangle constraint”。M3 的独立价值必须是：
  1. 现代 **visual latent WM** 中 trajectory proxy如何造成 behavior-policy imprint；
  2. 在 P94 local transition identifiability 已控制后仍成立；
  3. 对 MPC candidate ranking/closed-loop load-bearing；
  4. correction需要明确区别于 IEL/QRL 的 hitting-time/quasimetric machinery。
- **可能的 exact gap：** RC-aux/Temporal-Distance JEPA使用 **observed route gap作为 planner-facing semantic label**，而 IEL目标是 foundation-policy / offline GCRL hitting-time geometry；二者 setting、model object、planner interface不同。但若最终方法只是把 IEL/QRL移植进 LeWM，compression risk很高。

### P96 — Evaluating Model-Based Planning and Planner Amortization for Continuous Control — arXiv 2110.03363
**来源：** https://arxiv.org/abs/2110.03363

- **母问题：** learned dynamics + online planning 和 model-free policy 的计算/数据效率如何权衡？能否用 learned policy作为MPC proposal，再把planner distill回policy？
- **结果：** well-tuned model-free policy是强baseline；learned model + MPC + proposal在hard multi-task/multi-goal settings可提高performance/data-efficiency；planner computation可以distill进policy而基本不损performance。
- **ownership：** “planning vs amortized policy”“hybrid planner+proposal”“把planner distill到policy”不是2026新问题。
- **对 M2：** M2不能写成 generic planner amortization / train-vs-test compute paper。它必须落在 reward-free predictive representation到底储存哪种 future object（explicit transition / arbitrary-horizon / successor occupancy / hybrid），并用 modern visual offline setting + task/query information + hold-out regime law形成新delta。

### P97 — PLDM comparative science revisited — NeurIPS 2025
**对应已有 P02，新增 M2 ownership 解读。**

P02 已经比我们之前记得更接近 M2：
- explicit latent dynamics planning vs HILP/GCIQL/HIQL/CRL/GCBC；
- 数据质量、random-policy data、trajectory length / stitching、dataset size；
- unseen layout、new task；
- inference time / replanning interval；
- 最终给 practitioners method-selection guidelines。

**所以 M2 不能 claim：**
- “model-based planning vs model-free policy在不同data regime各有优势”；
- “explicit planning泛化好，policy inference快”；
- “trajectory length/data quality决定两类方法排序”；
- “做一张method-selection table”。

**M2 若继续，exact delta必须是：**
1. modern predictive-object continuum（one-step explicit / arbitrary-horizon / successor-policy occupancy / hybrid）；
2. visual/reward-free setting；
3. training compute + task/query information + deployment compute三本账；
4. relative ordering变化要由少数regime variables预测，并在 hold-out regime成立；
5. 最好解释为什么 predictive object 而不仅是 policy class / planner engineering造成差异。

### P98 — Optimistic Task Inference for Behavior Foundation Models — ICLR 2026
**来源：** https://proceedings.iclr.cc/paper_files/paper/2026/hash/6a616eeef41984f3bb23f81c3b9cb689-Abstract-Conference.html

- **母问题：** zero-shot / successor-feature BFMs test-time compute很低，但通常假设新 reward可以在一个非小的 inference dataset 上被计算/标注；这把“zero-shot”计算效率换成了 task-information/data负担。
- **方法：** 对 reward function保持 uncertainty，使用 optimistic criterion通过少量 test-time environment interaction主动收集最有信息的数据。
- **证据：** successor-feature BFMs在 established zero-shot benchmarks上能用少量 episodes识别/优化 unseen reward，且额外计算开销小。
- **ownership：** “implicit/BFM方法 task inference 需要很多 reward-labeled samples”不是我们的新发现；P98已经把它做成 ICLR paper。
- **对 M2：** E13 中 task/query information 只能作为 **fairness axis / regime variable**，不能把“TD-JEPA需要10k reward samples”当 headline。真正空间是：把 task-information budget 与 training/deployment compute、horizon、query novelty一起纳入 predictive-computation placement frontier。

## 17. Program-growth anchors after anti-overpruning recalibration（P99–P104）

### P99 — The Rank-One Corner: How Much Value Equivalence Does a Task Need from a World Model? — arXiv 2607.06640
**来源：** https://arxiv.org/abs/2607.06640

- **母问题：** “task-relevant / value-equivalent world model”不是一个二值属性；一个低维 objective 究竟会把多少 predictive task structure 写进 latent？
- **核心构念：** query/task 的 predictive **closure**；objective dimensionality决定 model能安装多少 closure directions，而不是单纯由model capacity决定。
- **关键结果：** controlled DreamerV3 setting里，标量 value objective只安装多维 closure 的一维投影；把 objective 从1维扩到完整多维后，recoverable structure显著上升。
- **idea-growth意义：** 老 Value Equivalence → 不是“更task-aware就更好”，而是问 **supervision rank / task family complexity / reusable predictive closure**。
- **对 R3：** 这是 specialization-vs-reuse program 的强理论/机制 anchor。它不关闭 R3；反而给出可操纵变量：query dimensionality、capacity、multi-query training、planner stage。
- **不能直接重做：** 再扫 objective rank + probe；新工作要连接 modern visual WM 的 query placement / planning regret / unseen-query reuse。

### P100 — The Intervention Gap in Latent World Models — arXiv 2608.29998
**来源：** https://arxiv.org/abs/2608.29998

- **母问题：** reward/value fit或task-anchored training能否保证 planner imagination 的 intervention effect正确？
- **定义：** planning-time **intervention fidelity**：world model自己 rollout 的 task-variable effect是否匹配 environment 对同action的真实干预。
- **证据：** TD-MPC2 size sweep中 reward error基本平而 operator/intervention error与return collapse更一致；LeWM capture-gated audit显示部分checkpoints能表示真实 action effect，但 imagined five-step effect方向/增益严重错误；现象随seed/candidate/support变化。
- **关键边界：** support-aware uncertainty score并非跨shift普适。
- **对 R1/R5：**
  - R1：什么经验/监督能真正识别 intervention effects？
  - R5：哪些 reliability signals在什么 support regime可信、该触发什么 repair？
- **不能直接重做：** “reward fit不够 / intervention gap存在”已是atomic claim；program可继续研究 data source、repair action、query dependence、active identification。

### P101 — AdaReP: Adaptive Re-Planning under Model Mismatch — arXiv 2606.23079
**来源：** https://arxiv.org/abs/2606.23079

- **母问题：** 每步MPC replanning昂贵，缓存plan又会因model mismatch变旧；何时应该replan？
- **理论：** stale-plan dynamic regret由 reuse tolerance、累计 mismatch 与 local dynamics sensitivity控制。
- **方法：** training-free online tolerance，根据 observed deviation + local sensitivity自适应replanning。
- **证据：** image-space / latent planning / physical robot；作者报告物理机器人上可减少>80% planner queries同时保持performance。
- **ownership：** adaptive replanning本身已有直接 work。
- **对 R5：** 非常好的“failure signal → 一个特定 recovery action”的单点答案。R5更大的未决问题是：**不同 failure type 到底该 replan、adapt、feedback、shorten horizon、fallback 哪一种？**

### P102 — FARM: Reading Failure Signals from Frozen Robotic WM States — arXiv 2609.11445
**来源：** https://arxiv.org/abs/2609.11445

- **母问题：** frozen robotic WM 的 predictive latent里是否已经包含 execution failure信息，可否低成本读出？
- **方法：** 33,985-parameter supervised readout，输出step failure score / causal trajectory risk；backbone frozen。
- **证据：** 10-task benchmark + PIPER X / SO-101 / Franka真实机器人 transfer；作者报告 pooled AUROC/AUPRC 85.68/88.59，latency约0.2256ms。
- **ownership：** “WM latent可读出failure signal”是已占 atomic claim。
- **对 R5：** detection不是终点。真正program问题是**failure signal该驱动什么 intervention**，以及 detection transfer是否足够支持 repair selection。

### P103 — Beyond Task Success: Stage-Wise Reliability under Sensing Degradation — arXiv 2609.07126
**来源：** https://arxiv.org/abs/2609.07126

- **母问题：** 最终task success无法说明 sensing corruption 在 encoder→predictor→planner→outcome 哪一层放大/衰减。
- **实验：** 10种视觉/时间degradation，对同50 tasks做paired stage-wise measurement。
- **结果主旨：** representation perturbation大小、prediction response、planner preference、physical outcome的排序并不保持；某些大latent shift会被下游吸收，小shift反而持续到outcome。
- **ownership：** generic stage-wise reliability audit已有直接 work。
- **对 R5：** 提醒不能用单一internal shift做trust signal；repair policy需要针对 **downstream consequence / failure type**。

### P104 — A Path-Space Formulation of Prediction in World Models — arXiv 2606.28751
**来源：** https://arxiv.org/abs/2606.28751

- **母问题：** world model真正预测的基本对象是否应理解成 future path distribution，而不是一串彼此独立的一步条件分布？
- **框架：** local Markovian regime下用 path measure / action functional统一 prediction、planning与uncertainty；分 reversible / irreversible dynamics并定义entropy production。
- **证据：** controlled attention-based models中 attention asymmetry随data irreversibility增长；强制对称会选择性伤害 irreversible long-horizon prediction。
- **对 R2：** 提供另一种 predictive-object hypothesis：**path distribution / trajectory action functional**。它不直接给我们方法，但说明R2不该只围绕“one-step vs successor”二分。
- **资源适配：** 如果R2实验发现irreversibility/contact process是关键regime，可把path-space/irreversibility作为method-led seed；当前不预注册。

## 18. R1 causal-data / action-effect cluster（P105–P108）

### P105 — CST-WM: A Causally Structured World Model for Embodied Visual Tracking — arXiv 2609.06302
**来源：** https://arxiv.org/abs/2609.06302  
**Read:** A-targeted（HTML introduction/method/scope/compute + experiments summary）

- **母问题：** logged tracking data中 behavior action 与 target evidence高度相关；generic action-conditioned predictor会不会把“action相关”误学成“action直接造成target evidence变化”？
- **failure:** causal hallucination——rollout可视觉上合理，但 candidate actions 按错误因果语义排序。
- **idea leap:** latent拆 target-evidence / robot / observation branches，阻止 same-step action直接写入target-evidence，action只能经robot motion→future observation影响evidence。
- **证据链：** multi-step fidelity、simulator candidate-ranking agreement、action leakage、EVT-Bench/Habitat tracking/re-acquisition、Unitree Go2 real trials；去掉action mask对re-acquisition伤害最大。
- **作者自限：** 结构约束是planning representation requirement，不声称完整recover外部target causality。
- **compute:** main model约19.5h on 4×RTX4090；全reported约320 GPU-hours + preliminary/ablation约190 GPU-hours。
- **Atomic ownership:** tracking setting下 behavior-policy action/evidence correlation 可造成 direct-action shortcut；task-specific causal factorization可改善planning。
- **对 R1:** 新的 data/identifiability axis不是“数据够不够”，而是**observational correlation允许哪些shortcut**。可与P94 action excitation正交：excitation保证action directions被观察，不保证model用正确mediator解释effect。

### P106 — OnlineWM: Causality-Aware Active Online Learning for Effective World Modeling — arXiv 2609.23753
**来源：** https://arxiv.org/abs/2609.23753  
**Read:** B/navigation（若成为baseline必须回全文）

- **问题：** static offline data不跟随model evolving errors；observational loss又可能依赖spurious correlations而非action-effect causality。
- **方法方向：** active simulator interaction + causality-aware counterfactual optimization。
- **规模边界：**公开摘要/项目说明使用大型generative WM（HY-World 1.5, 88B级），不适合我们首轮复现。
- **对 R1:** 强化 active data + causal objective 的program重要性；我们的compact stack可以研究同一个科学问题的**data-value/identifiability law**，不需要复制88B scale。

### P107 — CoCo: Overcoming Statistical Bias in Action-Controllable World Models — arXiv 2608.04653
**来源：** https://arxiv.org/abs/2608.04653  
**Read:** B/navigation

- **问题：** future frames可由视觉惯性/常见motion预测，模型可能忽略action仍拿到低loss；different actions给相似future，zero-action仍有motion。
- **方法：** counterfactual consistency，对action/observation变化施加一致性约束以减少statistical shortcut。
- **Atomic ownership:** generic “action injection不等于action control / statistical inertia shortcut”已有直接工作。
- **对 R1/R2:** action-effect data、counterfactual supervision与predictive object共同决定controllability；可作为I12 data-role和R2 distributional/control baseline。

### P108 — WorldEcho / WorldSync: Do Robotic World Models Really Follow Actions? — arXiv 2608.24885
**来源：** https://arxiv.org/abs/2608.24885  
**Read:** B/navigation

- **问题：** 现有action-conditioned video WM常只在expert demonstrations评估；off-expert valid actions是否真的被执行？
- **diagnosis:** WorldEcho扩大action distribution，测visual integrity + SE(3) action following；摘要报告现有模型对expert actions较好，但off-expert diverse trajectories中会ignore commands或产生invalid rollout。
- **repair:** WorldSync从distribution coverage、representation grounding、intervention-effect alignment三轴增强action following。
- **对 R1:** 把“action coverage / off-policy counterfactual query”从latent-control小环境扩到robot video WM；说明R1是跨model-scale的母问题。
