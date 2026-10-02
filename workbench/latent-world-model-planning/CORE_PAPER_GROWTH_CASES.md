# Core Paper Growth Cases — 顶会 idea 是怎样从 related work 里长出来的

更新：2026-10-02。  
用途：训练本地 agent **学习论文的生长方式**，而不是把 related work 当禁区。

阅读标签：
- **A-deep**：已针对性读 main method + experiments + related work/limitations；
- **A-targeted**：主文关键段落、关键实验与直接近邻已核对，但未逐 theorem / appendix；
- **B**：定位级，只能做 pressure/neighbor，不能凭它关闭 program。

`DOCUMENTED` = 论文明确论述；`RECONSTRUCTED` = 根据 paper structure / related work / experiments 重建“为什么这一步自然”，不声称知道作者真实创意心理过程。

---

# Case 1 — DINO-WM (ICML 2025): 去掉一个旧默认前提

**Read:** A-deep  
**Program:** R2 + R3  
**Source:** https://arxiv.org/html/2411.04983

## 旧世界
视觉 world model 常见两条路：
1. 像素/token生成；
2. latent model，但 representation 仍靠 reconstruction / reward / task-specific online learning塑造。

这带来 pixel reconstruction成本、task耦合，以及 offline model对 expert/reward/inverse-model 等额外信息的依赖。

## Mother question
> 能不能只从 reward-free offline trajectories 学一个 task-agnostic predictive model，然后在 test time 针对任意 visual goal 做 behavior optimization？

## Idea leap
**DOCUMENTED:** perception本来可以借助 internet-scale self-supervised visual representation；为什么world-model training还要重新学 perception/reconstruction？

于是：
- frozen DINOv2 patch features = observation state；
- 只学 action-conditioned latent transition；
- decoder只为可视化；
- goal image编码成 latent target；
- CEM直接优化动作序列。

## 决定性实验
不是只看rollout MSE：
- 六类 environments；
- arbitrary visual goals；
- 无 expert demo / reward model / inverse model；
- environment variation generalization；
- pretrained representation ablation；
- CEM vs differentiable planning；
- reconstruction/decoder ablation。

特别关键：把 reconstruction loss backprop 到 predictor 会伤 performance，因此“不要重建像素”不只是效率故事。

## Atomic claim
pretrained spatial visual features + offline latent dynamics + visual-goal MPC 能形成 task-agnostic zero-shot planner。

## 它打开什么
DINO-WM没有做完latent planning，反而制造后续 program：
- frozen semantic feature为什么有control geometry？→ Temporal Straightening / end-to-end JEPA；
- teacher forcing能支持recursive planning吗？→ JEPA-WMs / SALT；
- latent L2是不是planner该消费的cost？→ geometry / decision alignment；
- task-agnostic vs task-specialized state怎么取舍？→ R3；
- explicit rollout是不是唯一predictive object？→ R2。

## Lesson
强paper常来自：
> “领域默认需要 X” → “X真正承担什么功能？” → “成熟工具能否替代这个功能？” → 删除旧默认。

不是找空白。

---

# Case 2 — PLDM (NeurIPS 2025): comparative science 也能是主贡献

**Read:** A-deep  
**Program:** R1 + R2  
**Source:** https://arxiv.org/html/2502.14819

## 旧世界
offline GCRL 与 model-based control 常各自在本家方法里比较，缺少统一 data-regime 下的条件性认识。

## Mother question
> reward-free offline data 下，model-free goal-conditioned RL 和 latent dynamics + planning 的相对优势到底由什么 data regime 决定？

## Idea leap
把“谁更好”改写成一组 controlled axes：
- data amount；
- data quality；
- trajectory length；
- stitching；
- environment variation；
- unseen layout；
- control complexity。

## Method与baseline
PLDM = reconstruction-free JEPA latent dynamics + planner。  
但论文科学贡献明显大于这个architecture。

比较 GCBC / GCIQL / HIQL / HILP / CRL / PLDM。

## 决定性实验
- 数据量降到几千 transitions；
- TwoRoom固定总 transitions，只改 episode length 91/64/32/16；
- evaluation start-goal约90步，短trajectory必须真正stitch；
- Ant U-Maze验证复杂control；
- unseen layout / data quality / random behavior；
- compute与limitations讨论。

结果不是PLDM永远赢，而是：
- model-free在丰富高质量data下强；
- model-based在scarce/suboptimal/generalization regime有优势；
- stitching排序会随环境/方法改变。

## Atomic claim
受控 data-regime study 给出了 reward-free offline planning vs GCRL 的条件性强弱，而不是 universal winner。

## 它打开什么
- 哪个 data property 真正导致排序变化？→ R1；
- trajectory organization到底提供什么信息？→ R1；
- algorithm-family差异背后是不是predictive object差异？→ R2；
- method choice能否由少数data/query/compute变量预测？→ R2。

## Lesson
**顶会不要求一定有 fancy new method。**  
如果 controlled comparative science 导出新的 field-level design rule，本身就是贡献。

---

# Case 3 — JEPA-WMs / What Drives Success (TMLR 2026): 把新范式的 recipe 做透

**Read:** A-deep  
**Program:** R2 + shared methodology  
**Source:** https://arxiv.org/html/2512.24497

## 背景
DINO-WM证明范式可行后，问题从：
> “latent JEPA planning能不能work？”

自然变成：
> “到底什么设计选择让它work？”

## Mother question
encoder、predictor、multi-step training、context、proprioception、planner、cost、scale中哪些是真正load-bearing？

## Idea leap
这类paper不是新模块，而是**设计空间hardening**。

系统比较：
- DINOv2/v3/V-JEPA等encoder；
- predictor architecture/depth；
- rollout training K；
- context W；
- proprioception；
- CEM / NeverGrad / Adam / GD；
- L1/L2 cost；
- simulation + real manipulation。

## 关键 insight
multi-step training并非“多预测几帧”：
它让模型训练时暴露在自己的 predicted state 上，针对recursive deployment distribution做augmentation，降低compounding drift。

而不同domain最优K不同：
- simulation里更看accuracy；
- DROID里更长K的rollout stability收益能超过accuracy损失。

## 更重要的开放点
论文明确区分：
- explicit WM：task-agnostic dynamics + test-time planning；
- implicit WM：long-horizon predictive structure摊入representation/policy；
- hybrid。

并明确把 training/inference/generalization 的 direct comparison留作 future work。

## Atomic claim
JEPA-WM成功由一组可识别design choices驱动，不是“模型越大/预测越准就越好”。

## 它打开什么
R2：
> predictive computation到底应放在training还是test、放在哪种predictive object里？

## Lesson
一个新范式建立后，下一篇强工作可以不是再造架构，而是：
> **把 hidden design assumptions 系统暴露出来，并形成可迁移recipe/law。**

---

# Case 4 — Temporal Straightening (ICML 2026): 把“representation不好”压成数学对象

**Read:** A-deep  
**Program:** geometry as instrument across R1/R2/R3  
**Source:** https://arxiv.org/html/2603.12231

## Broad complaint
“semantic latent不一定适合planning。”

这句话太泛。

## Pressure
gradient planning在latent里高度非凸；Euclidean distance可能误表示 feasible trajectory上的progress。

## Idea leap
从 perceptual straightening hypothesis 引入 **trajectory curvature**。

它不是arbitrary probe，因为：
- 直接连接planner优化性质；
- 有geometry解释；
- 可以train-time intervention。

## Method
prediction loss + local curvature regularizer。

## Evidence chain
1. curvature下降；
2. Euclidean更贴近geodesic；
3. gradient planning conditioning改善；
4. open-loop / MPC success提高；
5. 多环境；
6. 对比smoothness / temporal contrastive；
7. 指出suboptimal trajectory下 temporal-distance negatives可能把geodesically close states推远。

## Atomic claim
local temporal curvature是planner-consumed geometry的load-bearing property，straightening可改善gradient latent planning。

## 它打开什么
- geometry应该由environment controllability还是behavior route定义？→ R1；
- geometry与query/planner是否应共同变化？→ R3；
- curved/irreversible path是否暗示更自然的predictive object？→ R2。

## Lesson
好机制题的形式是：
> 真实downstream failure → 可操纵数学对象 → explanation → intervention → downstream恢复。

不是“第17层probe怪”。

---

# Case 5 — RC-aux (NeurIPS 2026): 从 planner 的真实问题反推训练监督

**Read:** A-deep（用户提供论文，主文+实验附录此前已读）  
**Program:** R1 + planning-alignment lineage  
**Source:** arXiv:2605.07278 / Guang000/RC-aux

## 旧接口不一致
训练：
- local/one-step latent prediction。

部署：
- recursive long-horizon planning；
- latent endpoint distance当goal proximity。

## 两个 mismatch
1. temporal：local training vs recursive open-loop use；
2. spatial：latent proximity != finite-budget reachability。

## Idea leap
- multi-horizon recursive supervision；
- budget-conditioned reachability head。

同一 pair随budget h改变label，让head必须使用budget。

## 决定性证据
- 5 visual control tasks；
- 4/5 gains；
- Wall提升最大；
- Wall ablation：training-only改善已很明显，再加reachability-aware planner继续提升；
- LIBERO transfer；
- 单GPU、小模型、低planner overhead。

## Atomic claim
finite-budget reachability + deployment-matched rollout supervision可让compact latent WM更plannable。

## 最重要的“打开”
论文自己承认 trajectory offset只是 empirical proxy，不是真 MDP shortest hitting time。

这不是“小bug空间”，而是R1母问题：
> offline experience中的什么统计量，才真正识别controllability？

---

# Case 6 — SALT (2026): 反常结果迫使问题重定义

**Read:** A-targeted  
**Program:** R2  
**Source:** arXiv:2609.33595

## 旧默认
one-step prediction越准，recursive planning大概越好。

## Pressure
recursive rollout error取决于：
- 每步新误差；
- 后续transition Jacobians如何传播误差。

真正承重的可能是**error propagation operator**。

## Idea leap
state-affine dynamics具有state-independent Jacobian：
- propagation只依action sequence；
- 去掉nonlinear propagation residual；
- 再用recursive multi-step supervision匹配deployment。

## 决定性反常
SALT one-step error比matched LeWM高1.48–2.19×，但四环境planning success都提高，平均约+10pp；Cube cost-spike failure 23.3%→2.0%。

## 为什么story强
如果只是：
> prediction error下降 → planning提高

解释太普通。

现在是：
> **prediction更差 → planning更好**

旧proxy被直接推翻，于是paper拥有新的load-bearing object：propagation structure。

## Atomic claim
recursive planning应关注error propagation structure；state-affine transition是由该分析自然导出的具体修复。

## 它打开什么
R2：
- 什么predictive operator最适合recursive use？
- structured dynamics在哪些regime足够？
- contact/stochastic dynamics是否需要path/distribution object？

---

# Case 7 — Controlled-WM Identifiability (P94): 从“data matters”升级成识别条件

**Read:** A-targeted  
**Program:** R1  
**Source:** arXiv:2607.22430

## 旧 broad statement
offline behavior coverage影响world model。

太泛。

## Mother question
> action-conditioned JEPA在 nonlinear observations + behavior policy 下，什么时候真的识别 latent state 与 controlled transition？

## Idea leap
把“data quality”拆成两个理论margin：
1. predictable-signal spectral separation → representation identifiability；
2. conditional action excitation → transition identifiability。

## 最强点
模型可以：
- on-policy prediction很好；
- 但behavior policy没激发的action direction上，counterfactual prediction任意差。

理论给出 counterfactual/on-policy amplification与最弱excitation margin的关系。

## 决定性实验
操纵 conditional action variation，同时看：
- on-policy prediction；
- counterfactual error；
- reachable set / goal-planning consequence。

## Atomic claim
conditional action excitation是controlled transition identifiability的基本条件之一。

## 它打开什么
这篇不是把R1做完，而是给R1一个更强坐标：
- excitation够了，route diversity还有没有额外价值？
- same-reset intervention相对broad excitation值多少？
- active probing应优化excitation margin还是decision boundary？
- finite interaction budget下哪种data composition最值钱？

这正是I12/E16的来源。

---

# Case 8 — Task-Sufficient World Models (ICML 2026): data collection 与 representation 共同生长

**Read:** A-targeted  
**Program:** R1 + R3  
**Source:** ICML/PMLR 306, Feng et al.

## 旧前提
先收generic data，再被动学representation。

## Mother question
> 如果只需要 task-sufficient minimal state，为什么让 behavior/data collection 与 representation learning完全分离？

## Idea leap
闭环：

```text
current model
→ active probing / adaptive curriculum
→ expose task-relevant latent factors
→ structured WM
→ compact task-sufficient state
→ better probing
```

## 为什么尺度够
不是“加一个sampler”：
- 问题是**什么信息值得交互去获取**；
- data strategy与representation co-design；
- 目标是minimal+sufficient；
- 测 skill / object-skill composition / unseen task generalization。

## Atomic claim
active informative exploration + structured modeling可更高效恢复task-sufficient latent factors。

## 它打开什么
R1：
- query-aware probing vs general-purpose exploration；
- action excitation vs information gain；
- data value per environment step；
- failure/recovery data是否更值钱。

R3：
- task-sufficient到底多task-specific？
- 多query下怎样保reusable structure？

---

# Case 9 — Bagatella TD-JEPA (ICLR 2026 Oral): 合法的 method-led 生长范例

**Read:** A-deep  
**Program:** R2  
**Source:** https://arxiv.org/html/2510.00739

## 起点
self-predictive objectives在RL里通常：
- one-step；
- single policy/task；
- 或只是auxiliary loss。

## Method-led insight
TD learning天然把future information bootstrap到当前state。

于是问：
> 能不能把 TD principle用于 latent prediction，直接学习多policy的long-horizon predictive structure？

这是合法“拿锤子找钉子”：
- 锤子有理论含义；
- 对重要program产生新prediction；
- 不是随便换loss。

## Idea leap
- state encoder；
- task encoder；
- policy-conditioned multi-step predictor；
- parameterized policies；
- TD latent-predictive objective。

理论连接 successor measure / successor features。

## 决定性实验
- 65 tasks / 13 datasets；
- ExoRL + OGBench；
- state + pixels；
- one-step behavioral vs multi-step behavioral vs policy-conditioned successor；
- symmetric vs separate state/task encoder；
- fast adaptation。

尤其5.2明确问：
> latent-predictive zero-shot algorithm到底应该model哪一种dynamics？

## Atomic claim
TD latent prediction能学习multi-policy long-horizon successor structure并支持zero-shot RL，尤其pixels。

## 它打开什么
R2：
- successor representation vs explicit dynamics；
- arbitrary-horizon direct predictor；
- query flexibility；
- stochastic dynamics；
- train-time amortization vs test-time search。

## Lesson
problem-led不是禁止method-led。  
好 method-led seed应是：
> method principle → 新predictive object / falsifiable hypothesis → theory → decisive ablation。

---

# Case 10 — What Must a World Model Distinguish? (2026): 把 sufficiency 条件化

**Read:** A-targeted / direct-neighbor critical  
**Program:** R3  
**Source:** arXiv:2609.33030

## 旧争论
- full predictive state最好？
- task-specific minimal state最好？
- decision-aligned latent最好？

把它们当互斥哲学太粗。

## Mother question
> planner真正需要保留多少 physical distinctions？

答案依：
- query；
- candidate set；
- planner如何生成candidate。

## Idea leap
层次化：
1. mechanism sufficiency；
2. response sufficiency；
3. decision sufficiency。

coarse choice可能只需很少信息；fine choice可能接近full prediction。

更关键：
final selection不需要的信息，在adaptive search中仍可能需要来发现good candidates。

## Design consequence
query-conditioned joint model在seen objectives上regret更低，但unseen objectives优势明显缩水。

由此提出modular：
- query决定“去哪里找”；
- action-conditioned model负责“那里会发生什么”。

## Atomic claim
WM sufficiency依query+candidate+planner；query placement存在specialization/generalization trade-off。

## 它打开什么
R3仍很大：
- query进哪一层？
- query dimensionality / capacity；
- multi-query training；
- proposal vs dynamics conditioning；
- planner变化；
- query-aware data；
- reusable world knowledge的最小结构。

正确读法不是“P38做了query所以没空间”，而是：
> **P38把R3变成了更清晰的research program。**

---

# Case 11 — Rank-One Corner (2026): 把经典原理从二元变成 graded law

**Read:** A-targeted（全文关键实验/controls已核对）  
**Program:** R3  
**Source:** arXiv:2607.06640

## 老理论
Value Equivalence：
> model无需完整环境，只需保留决策/value相关结构。

老概念不意味着没法继续。

## 新问题
“task-relevant”不是一个bit。  
query family依赖的 predictive coordinates 形成 closure。

问：
> objective到底会安装多少 closure directions？

## Idea leap
不是反驳VE，而是把它**参数化**：
> objective dimensionality ↔ installed predictive rank（特定regime）。

scalar reward/value只是rank-one corner。

## 决定性 controls
- same architecture / same probe / same budget；
- objective dim 1→4；
- installed rank逐级跟随；
- scalar weight提高4.5×仍只装1 direction，排除gradient pressure；
- value-head重复，排除aux-head；
- capacity sweep，区分capacity与objective rank；
- 找boundary：frame-wise reconstruction已经恢复closure时，objective dimensionality不再承重。

## Atomic claim
在reconstruction未自动恢复task closure的regime，objective dimensionality控制latent安装的predictive closure rank。

## Lesson
经典问题做了20年，仍可出新paper，因为：
> 不再问“VE对不对”，而问**它有几个维度、law边界在哪里**。

这就是拥挤领域里长novelty的典型方式。

---

# Case 12 — Intervention Gap (2026): 从 aggregate fit 转向 matched intervention

**Read:** A-targeted  
**Program:** R1 + R5  
**Source:** arXiv:2608.29998

## 旧 assumption
reward fit好、task-anchored training好、latent能decode task variable，似乎就够planning。

## Mother question
planning真正需要：
> 对同一个 candidate action intervention，model imagined effect和environment effect一致吗？

## Idea leap
定义 intervention fidelity，并做 capture-gated audit：
1. 当前query是否被model state捕获？
2. real action effect是否可从latent解释？
3. model rollout是否正确传播这个effect？

这样把representation缺信息、environment effect不可读、predictor传播错分开。

## 决定性证据
- TD-MPC2 size sweep：reward error近乎平，但operator error更跟return collapse；
- task-anchored model不一定更好；
- LeWM Cheetah：真实effect可decode，但imagined 5-step effect甚至差于“no effect”；
- failure是direction rotation + excess gain，不是collapse；
- 多seed/Finger Spin；
- candidate/support dependence；
- uncertainty ranking跨support不稳定。

## Atomic claim
planning-time intervention fidelity是reward fit/task alignment不能替代的独立性质。

## 它打开什么
R1：
- 什么data最有效修intervention gap？
- excitation/same-reset/active probing谁值钱？

R5：
- 哪个signal能预测gap？
- 出现gap后应该replan/adapt/feedback/fallback哪个？

---

# Case 13 — Planning Limits / IMWM: 用 oracle 把“模型差”拿掉

**Read:** A-targeted  
**Program:** R2 + R5  
**Sources:** Planning Limits arXiv:2609.39235；IMWM direct-neighbor notes

## 方法论
系统失败时，不要默认再训更准model。  
把learned dynamics替换成perfect simulator。

如果failure还在，瓶颈不属于prediction。

## Planning Limits
五步model对近目标action ranking可靠，但真实任务目标远超imagined horizon。

更关键：
用真实simulator做perfect prediction时，goal从5步移到20步，success仍从约92%降到41%。

## IMWM
ideal WM也会因有限candidate search失败，于是用demo-derived intuition改善proposal/search。

## Atomic claims
- perfect dynamics不能解除finite plannable range；
- ideal model下 finite-sample proposal仍可成为bottleneck。

## 它打开什么
R2：
- predictive horizon vs temporal abstraction；
- search放training还是test；
- explicit model + learned proposal怎样hybrid。

R5：
- far-goal failure应该increase H、subgoal、fallback还是别的repair？

## Lesson
**oracle replacement是发现真正问题的强工具。**

E06应作为R1–R5的scientific instrument，而不是自己先做一篇“bottleneck benchmark”。

---

# Case 14 — AdaReP / FARM: detection 与 repair 之间还有一层

**Read:** B/A-targeted positioning  
**Program:** R5

## FARM
冻结WM latent做轻量failure readout。  
回答：
> 能不能检测failure？

## AdaReP
根据 observed mismatch + local dynamics sensitivity动态决定何时replan。  
回答：
> 什么时候值得replan？

## 更大的R5
signals很多：
- uncertainty；
- support；
- residual；
- candidate margin；
- intervention gap；
- model-vs-intuition disagreement。

recovery也很多：
- more search；
- replan；
- shorter horizon；
- feedback correction；
- adaptation；
- fallback。

现在很多paper是：
> 一个signal ↔ 一个repair。

## 下一层问题
> **failure type / signal 到 best recovery action 是否存在稳定 mapping？**

这不是先拼一个router。E18要先证明：
- 不同conditions有不同intervention winner；
- observable signal可预测；
- utility-vs-compute有结构。

只有这样，router才是自然method。

---

# 15. 从这些案例抽出的 idea-growth 模式

### Pattern A — 删除默认组件
DINO-WM：pixel/reconstruction默认必要 → pretrained representation承担perception。

### Pattern B — broad complaint → load-bearing construct
Temporal Straightening：representation不适合planning → curvature/geodesic conditioning。

### Pattern C — 反常结果逼迫重定义目标
SALT：one-step更差但planning更好 → error propagation operator。

### Pattern D — comparative science找到regime
PLDM：谁更好 → data regime决定相对优势。

### Pattern E — 经典理论变成graded law
Rank-One：value equivalence → objective dimensionality / closure rank / boundary。

### Pattern F — passive metric → matched intervention
Intervention Gap / P94：average prediction/data quality → action intervention fidelity / excitation identifiability。

### Pattern G — method principle定义新predictive object
TD-JEPA：TD bootstrap → policy-conditioned successor representation。

### Pattern H — oracle replacement隔离真正bottleneck
Planning Limits / IMWM：perfect model仍失败 → horizon/search成为问题。

### Pattern I — 多个局部解之间找缺失mapping
FARM + AdaReP + AdaJEPA + Feedback：detect/repair各自成立 → 什么failure该用什么repair？

---

# 16. 本地 agent 的论文阅读模板

每次新近邻必须写：

```text
Mother problem:
Old default assumption:
Pressure / evidence that makes old framing insufficient:
Idea leap:
Why is the method a natural consequence?
Data / tasks / baselines:
Decisive experiment:
What simple alternative was ruled out?
Atomic claim owned:
Which parent R# becomes clearer?
What condition / interaction / boundary does it open?
2–3 next experiments that distinguish competing explanations:
```

最重要的不是：
> “这篇有个loss，我能不能改一下？”

而是：
> “作者为什么有资格提出这个loss？哪个observation / theoretical object / bottleneck让它成为自然答案？”

---

# 17. 最适合我们资源复制的研究风格

优先学习：

1. **PLDM**：大面积受控experimental science；
2. **Temporal Straightening**：broad pain → load-bearing construct；
3. **SALT**：surprising result → mechanism → tiny architecture change；
4. **P94**：data phenomenon → identifiability condition；
5. **Rank-One**：old principle → graded law + boundary；
6. **Intervention Gap**：released models + matched oracle audit → new failure construct；
7. **Task-Sufficient WM**：data collection与model共同设计；
8. **TD-JEPA**：mature method principle → new predictive object。

共同结论：

> **顶会 novelty 不是“没人碰过”，而是在一个重要 program 里把认识向前推进一层。**
