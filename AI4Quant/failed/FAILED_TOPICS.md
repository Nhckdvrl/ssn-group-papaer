# AI4Quant — Failed / Hold Topic Ledger

> 目的：记录本轮已经认真搜索过、做过 ownership / feasibility audit、但没有进入正式 selected 的题。后续不能因为换了措辞就无条件复活。

状态说明：

- **KILL**：broad form 已被直接 owner、退化成成熟问题、或 AI/finance 交叉不成立。
- **HOLD**：科学形状有价值，但当前 novelty / feasibility / conference identity 不足，不适合作为最先开做的题。
- **SERIOUS, NOT AUTHORIZED**：仍有科学价值，但尚未过两边 load-bearing / decisive E01 / ownership 中至少一关。

---

## A. Agent / credit / memory

### Outcome ≠ Causal Experience
**Status: SERIOUS, NOT AUTHORIZED**

问题：金融 realized PnL 的 causal ownership 本身不确定，agent 如何从 experience 中做 credit assignment？

没有授权原因：long-horizon credit assignment 已极拥挤；若最后只是把 raw PnL 换成更好的 attribution label，会退化成已有 finance skill-vs-luck / reward denoising。

### Successful Experience ≠ Good Experience / Outcome-Conditioned Memory
**Status: SERIOUS, NOT AUTHORIZED**

问题：随机 outcome 是否会让 LLM agent reflection / memory 把同一个 ex-ante decision 错误评价为“好经验/坏经验”？

优点：目前未找到把 outcome luck 与 decision quality 正交化做 controlled agent-memory study 的 direct owner。

未授权原因：finance 目前仍更像高噪声随机环境；若仅用 benchmark-adjusted alpha 代替 raw return，贡献太像 label improvement。

### Attempted Experience ≠ Observed Experience
**Status: KILL**

原因：action-dependent censored feedback、market-making censored learning、MNAR rewards / censored bandits 已有直接理论 owner。

### Search ≠ Evidence
**Status: KILL**

问题：LLM/agent 反复生成策略并 backtest，会不会因 adaptive search 污染 evidence？

原因：multiple testing / backtest overfitting / adaptive data analysis 已成熟；2026 已出现 trials-adjusted gating for LLM-proposed trading strategies，direct-successor 风险太高。

---

## B. Opponent / intervention / causal response

### Behavioral Fit ≠ Strategic Predictability
**Status: KILL broad form**

问题：passive behavior 上等价的 opponent models，面对 intervention 是否产生不同 response？

原因：ICML 2025 已直接研究从 observed behavior 推断 beliefs/goals 后对 unseen deployment behavior 的预测极限；multi-agent counterfactual / active probing 也已有近邻。

### Probe ≠ Observe
**Status: KILL broad form**

问题：主动 probing 市场是否改变被测 quantity 本身？

原因：Observer-Effect POMDP、active sensing with measurement effects、microstructure pinging 已形成成熟 lineage。

### Observation Token ≠ Intervention Token
**Status: KILL broad form**

问题：market world model 将历史 endogenous action 与人工 do(action) 用同一种 token 表示，是否把 observational correlation 当 causal response？

原因：causal confusion / imitation learning / offline RL 中 observation-vs-intervention distinction 已是经典问题；2026 又有 causal multi-agent world-model work。

### Content-identical events with different provenance
**Status: HOLD residual**

同样的大单来自“自己”与来自“别人”具有不同 epistemic meaning；自己的 action 不应成为隐藏市场意图的证据。

暂不升：目前仍过于接近 causal-confusion 的 finance 实例。

---

## C. Market world models / simulators

### Mechanical Impact ≠ Learned Reaction
**Status: KILL broad form / residual HOLD**

问题：hybrid market world model 的 plausible impact 是 matching engine 的 mechanical effect，还是 learned order-flow response？

原因：LOBGAN 2023 已明确比较 market replay mechanical impact 与 conditional generator reaction。

Residual：M3 passive likelihood scaling 是否伴随 learned interventional responsiveness scaling，目前仍可作为 audit seed，但不足以独立授权。

### Realistic World Model ≠ Non-Exploitable World Model
**Status: KILL broad form**

问题：高 likelihood / realistic simulator 是否会被 planner 通过 round-trip / arbitrage exploit？

原因：2026 已有一般 world-model exploitability direct work；仅以 no-arbitrage 作为金融 oracle 不足以形成新 mother question。

### Predictive Sufficiency ≠ Counterfactual Sufficiency
**Status: HOLD**

问题：一个 representation 可很好预测 passive sequence，但由于 aggregation 丢失 queue identity，对 fill/intervention counterfactual 本质上只部分识别。

优点：finance queue aggregation 提供 sharp non-identifiability oracle。

未授权原因：partial identification / robust policy bounds / counterfactual identifiability 已有成熟理论；容易退化成“让 agent 输出 interval”。

### Limit-awareness under observational equivalence
**Status: HOLD**

问题：当额外同类数据永远不能消除 ambiguity 时，agent 是否知道继续推理无效，必须请求更细粒度信息或保持 set-valued answer？

未授权原因：容易变 benchmark / uncertainty evaluation；2026 已有 counterfactual-identifiability 与 capability-awareness 近邻。

### Compositional Intervention / Cross-impact Composition
**Status: HOLD**

问题：单资产 intervention 看起来都合理，多资产组合 intervention 是否违反 cross-impact / no-dynamic-arbitrage 结构？

科学形状好；一般 AI 已有 compositional intervention generalization。

当前可行性障碍：M3 是单资产 trajectory model；TradeFM 跨资产预训练但不是 joint multi-asset state model。研究 cross-impact 很可能需要自建联合 world model，成本和偏题风险高，因此不作为首开题。

---

## D. Symmetry / normalization / tokenization

### Broken / Conditional Scale Symmetry
**Status: HOLD, broad form KILLED**

问题：跨资产 FM 将 scale invariance 当泛化优势，但当绝对尺度通过 tick / lot / price grid 进入交易机制时，该 symmetry 会被打破。

为什么没有授权：

- general AI 已有 partial/broken symmetry、causal vs observational symmetry、nintervention 等 direct conceptual owner；
- M3 还显式带 tick-aware loss / hard matching engine，不能简单声称 scale normalization 抹掉 tick；
- TradeFM 的 scale-invariant representation 确实可能 quotient 掉 mechanism variables，但若只做“漏重要 covariate”太浅。

### Representation-Induced Universality
**Status: HOLD / not main project**

问题：coarse/normalized tokenization 是否先压小了跨市场 distribution shift，从而让 OOD token perplexity 看起来很漂亮？

原因：domain-invariant representation 文献很早就指出 representation 可通过丢失 domain-distinguishing information 人工制造 invariance；作为 TradeFM audit 有价值，但不足以成为新 mother question。

### Tokenization/compression loses decision-critical state
**Status: KILL broad form**

原因：value-aware representation learning、POMDP value-directed compression 已成熟。

### Redundant Evidence / Input Spanning
**Status: HOLD**

问题：复制一个完全经济冗余的 series / exposure，不增加信息，却可能因 cross-variate attention multiplicity 改变 forecast。

原因：attention 对 multiplicity 敏感、redundant context / multiset modeling 已有直接 AI owner；金融 spanning 只能提供漂亮 stress test。

---

## E. Scaling / data geometry

### Global Scaling ≠ Mechanism Scaling
**Status: HOLD**

问题：M3 总体 next-token NLL 随规模下降时，哪些经济机制真的一起 scale，哪些不动？

原因：feature-frequency / rare-feature scaling 已有一般理论；M3 公开多尺寸 checkpoint 但训练/测试订单事件数据未完整公开，首开可行性一般。

### Data Volume ≠ Information Volume
**Status: KILL broad form**

问题：高度相关 order-flow 中 token count 是否夸大真实 information volume？

原因：2026 scaling-theory 已直接从 token correlation、conditional entropy、Zipf/Heaps/Hilberg statistics 推 neural scaling law；仅把 entropy/mixing 套到市场数据不够新。

### Effective order of “universal market grammar”
**Status: SERIOUS-shape / feasibility weak**

问题：TradeFM 跨市场 predictive transfer 到底需要长程、高阶 learned grammar，还是低阶 Markov / local transition statistics 已解释大半？

优点：符合“复杂 foundation-model 现象是否可由简单统计解释”的强 scientific taste。

未授权原因：TradeFM 权重/训练数据不开放，直接 replication / decisive E01 可行性较弱。

### Cross-sectional breadth ≠ temporal depth
**Status: MERGED INTO SELECTED P1**

该 seed 已升级为正式题 **State Coverage ≠ Exposure Coverage**，不再作为失败题复活。

---

## F. Forecasting structure / risk / coherence

### Predictive Sufficiency ≠ Risk Sufficiency
**Status: KILL broad form**

原因：2026 已有 “Do time series foundation models know their tails?” 以及 tail-aware rare-event Transformer。

### Marginal Calibration ≠ Joint Decision Sufficiency
**Status: KILL broad form**

原因：2025 已有 Foundation Model Forecasts: Form and Function，明确证明相同 marginals 可对应不同 joint laws，边际 forecast 不足以支持 path-dependent decision。

### Time-consistent risk / replanning
**Status: KILL**

原因：dynamic convex risk measure + model-free RL、time-consistent portfolio/stat-arb 已成熟。

### Multi-frequency / temporal reconciliation
**Status: KILL**

原因：temporal / cross-temporal forecast reconciliation 已成熟，金融 volatility/VaR 也早已应用。

### Nested information-set coherence
**Status: KILL broad form**

问题：增加 context 后 conditional belief 是否满足 tower/martingale consistency？

原因：2026 *Martingale-Consistent Self-Supervised Learning* 已直接提出 coarse/fine information-view forecast coherence。

### Forecast Skill ≠ Structural Skill / cointegration
**Status: MOVED TO SELECTED P2**

不在失败账继续讨论，正式注册见 `selected/forecast-skill-vs-structural-skill/`。

---

## G. Finance-specific but currently too finance-only / owned

### P vs Q — Physical vs Risk-Neutral Measure
**Status: KILL broad form**

原因：2025–2026 risk-neutral generative networks / diffusion / neural SDE / measure correction 已密集；且 “P 不唯一决定 Q” 是资产定价基本结构。

### Ensemble disagreement ≈ epistemic uncertainty
**Status: KILL**

原因：一般 AI 2026 已直接质疑 ensemble disagreement 的 uncertainty semantics；2026-09 finance 又已有 *What Does Machine Forecast Disagreement Measure?*。

### AIPT / many weak factors × neural bottleneck
**Status: HOLD seed**

Finance pressure 强：large factor / dense SDF 文献挑战低维 latent-factor 假设。

未授权原因：不能错误假设现代 multivariate Transformer 都有固定低秩 bottleneck；尚未找到真实 load-bearing architecture/objective assumption。

### Model-induced support collapse
**Status: KILL broad form**

原因：selective labels / endogenous data / exploration / performative learning 已直接覆盖“模型决策改变未来可观察样本”的核心结构。

---

## 当前纪律

后续若重新考虑本文件中的题，必须有**新的 scientific object、new leverage 或明确的 owner gap**；不能仅靠换措辞、换模型、换市场、换数据集复活。
