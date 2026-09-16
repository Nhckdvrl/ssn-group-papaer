# AI4Quant 下一轮选题搜索交接（2026-09-16）

> 目标：继续寻找真正值得 **ICML / ICLR / NeurIPS Main** 投入的 AI4Quant scientific questions；若 scientific object 涉及 language / LLM / agents / text，同时用 **ACL / EMNLP / NAACL Main / TACL** 校准。
>
> 这不是推进已有两题的执行文档。当前任务仍然是：**继续找新的、独立的、Main-level scientific question。**

---

## 0. 当前状态：已经有 2 条 PILOT-AUTHORIZED，不要在下一轮反复重找

当前正式注册在 `AI4Quant/selected/`：

1. **State Coverage ≠ Exposure Coverage**  
   *The Geometry of Data in Multivariate Foundation Models*

2. **Forecast Skill ≠ Structural Skill**  
   *Do Multivariate Foundation Models Actually Learn Error-Correcting Structure?*

这两题已经单独建立目录注册。下一轮除非发现直接 owner / fatal flaw，否则不要把主要搜索预算花在继续润色它们；目标是找新的独立题。

所有已经搜过、KILL / HOLD / 降级的方向统一看 `AI4Quant/failed/FAILED_TOPICS.md`，避免换对话后复活同一批 broad ideas。

---

# 一、这一轮 search process 到底哪里有问题

先强调：**没有大量 survivor 本身不是流程失败。** 好题本来就稀缺，连续杀掉漂亮问题是正常且必要的。真正的问题是某些 search behavior 会系统性降低找到好题的概率。

## 1. 最大问题：撞到一个漂亮 conceptual lens 后，在同一堵墙里挖太久

这一轮最明显的是：

- world model / market microstructure；
- invariance / broken symmetry；
- intervention / counterfactual；
- scaling / tokenization。

很多后续 idea 名字不同，但 abstract skeleton 已经开始相似。

典型症状：

> 找到一个好 distinction → owner 很近 → 再往下缩一点 → 又找一个 residual → 再缩一点 → 最后变成“已知 AI failure 在 finance 的漂亮实例”。

这会让 searcher 产生错觉：自己一直在推进，但 search surface 实际已经越来越窄。

### 下一轮硬纪律

如果发生以下任一情况，**立刻换 scientific object，不再救题**：

- 连续 3 个 idea 共用同一母骨架；
- 一个方向连续 2 次被 broad owner + exact owner 压缩；
- novelty 主要来自“金融给了一个真实案例”；
- 开始不停用 `≠` 换名字，但 scientific conclusion 没变；
- 为了保住一个 seed，不断增加限定条件。

换墙时不是换关键词，而是换真正的 scientific object，例如从 world model 直接切到：

- learning dynamics；
- representation geometry；
- test-time computation；
- uncertainty semantics；
- memory / self-improvement；
- multi-agent learning；
- causal identification；
- optimization；
- data scaling；
- language belief updating；
- decision theory；
- scientific discovery。

---

## 2. 过去容易把“新 setting”误当成“新 scientific question”

本轮大量漂亮但最终被杀的题都有这个问题：

- tick-size natural experiment；
- queue partial identification；
- market mechanism change；
- no-arbitrage oracle；
- cointegration；
- cross-impact；
- censoring；
- P/Q measure。

这些 finance structures 很强，但 **finance structure 强 ≠ AI question 新**。

下一轮每当发现一个 finance-native structure，必须立刻问：

> **如果把 finance noun 全删掉，这篇论文一般性的新 scientific conclusion 是什么？**

如果答案只是：

> “我们证明已知的 AI failure 在真实金融里也会发生”，

通常不够 Main。

最理想的是 finance 结构能够：

1. 击穿 AI literature 的一个 load-bearing assumption；或者
2. 提供普通 AI benchmark 根本没有的 hard oracle / intervention / identification；并且
3. 最终改变一个一般 AI belief，而不仅是 finance evaluation。

---

## 3. 另一个问题：太早 candidateize，会产生 sunk-cost rescue

一旦题被命名成：

> X ≠ Y

就很容易开始保护它。

下一轮应区分三层：

### Raw pressure
只有一个异常/冲突，不叫 candidate。

### Serious seed
mother question 已经明确，但 owner / feasibility 尚未过。

### Candidate
只有在下面三件事至少基本成立后才命名并长期追：

- exact owner 没直接占；
- 能说出一般 scientific conclusion；
- 有一个便宜 decisive E01。

**candidateize late 继续保留。**

Chris Olah 关于 research taste 的核心提醒非常适合这里：真正执行一个 idea 的反馈太昂贵，因此应该大量产生 idea、通过便宜 proxy feedback 快速校准 taste，而不是过早陷入单个方向的 sunk cost。

---

## 4. 搜索有时过度 finance-first，又有时过度 AI-first

### finance-first 漂移

会变成：

> 很漂亮的 microstructure / asset-pricing / econometric question
> → AI 只是工具。

这种题也许值得 RFS/JF，但不是当前目标。

### AI-first 漂移

会变成：

> 一个已经有人研究的 AI failure
> → 在 stock / order book / options 上再验证一次。

这是 finance-themed AI，不是真正的 AI4Quant intersection。

### 正确要求

必须两边 load-bearing：

> **去掉 finance，AI question 会实质改变。**
>
> **去掉现代 AI capability / object，这个 finance unknown 又无法以同样方式回答。**

如果任意一边可以删除，交叉大概率是假交叉。

---

## 5. Feasibility 检查应该更早，不要等概念完全长好后才发现不能做

这一轮已经踩过：

- concept 很漂亮，但公开数据只有 trades，没有需要的 L2/L3；
- concept 需要 multi-asset joint world model，但公开 checkpoint 本质是单资产；
- paper claim 很适合审，但权重 / 训练数据没公开。

下一轮一个 seed 一旦达到 SERIOUS，就立刻查：

- public weights？
- public data？
- API 是否真的暴露需要的 input/output？
- 是否需要重训 foundation model？
- E01 是否可在数小时到 1–2 天内做？

**好问题不要求便宜，但第一刀必须便宜。**

---

## 6. Owner audit 做对了，但下一轮要更系统地区分 3 类 owner

不要只问“有没有一篇标题很像”。

### Broad owner
一般科学 distinction 已经有人提出。

### Domain owner
finance literature 已经做过同一结构。

### Exact owner
已有工作能几乎直接写出我们的核心 experiment / conclusion。

判断逻辑：

- broad owner 存在，不一定杀；finance 可能增加新的 structure。
- broad + domain owner 都很近，危险。
- exact owner 命中，通常直接 KILL。

但也不要无限 rescue。若一个题连续靠增加限定词才能绕开 owner，优先杀。

---

# 二、再次深化：我们真正想要的“好题”是什么

## 最核心的一句话

> **寻找一个在方法出现以前就值得 AI researcher 和 quant researcher 同时关心的 scientific question；金融环境击中 AI 的一个真实 assumption，或者现代 AI 第一次让一个长期金融未知变得可识别。答案至少有两个可信方向，并且不同答案会改变我们对 learning / representation / agents / markets / decision-making 的 belief。**

这比“novel method”重要得多。

---

## 1. Question first, method second

不知道模型名、算法名时，问题仍应成立。

强题的 abstract 第一段通常能写成：

> We study whether / when / why ...

而不是：

> We propose XXX-Net for financial forecasting.

当前两个 survivor 都符合这一点：

- 为什么 multivariate data 的两维不能简单压成 token count？
- 为什么 forecast skill 不一定等于 mechanism acquisition？

继续保持这种问题形状。

---

## 2. 最喜欢的题形：挑战一个“看起来当然正确”的 load-bearing assumption

ICML 2026 Outstanding 的 *The Flexibility Trap* 被委员会表扬的核心，不是复杂方法，而是发现 diffusion LM 被认为是优势的 arbitrary-order flexibility 会绕开真正关键的高不确定 token，导致一个此前并不明显的 failure mode。

下一轮要主动寻找这种结构：

> **大家把 A 当优势 / proxy / sufficient condition；在条件 B 下，A 恰好破坏了真正需要的 C。**

但不要机械复制 “X is a trap”。重点是找 **dominant assumption 的非显然 failure**。

---

## 3. 第二种强题形：把漂亮经验现象解释成更简单、更基本的机制

ICML 2026 Honorable Mention *A Random Matrix Perspective on the Consistency of Diffusion Models* 的强点，是把一个看起来很深的神经网络现象还原到共享的低阶 Gaussian statistics。

这提醒下一轮：

> 当一篇 AI4Quant paper 声称学到了“market intelligence / universal grammar / strategic response / causal behavior”时，优先问：**一个更简单的 baseline / mechanism 是否已经足以解释现象？**

真正的贡献可以是解释，而不一定是新算法。

---

## 4. 第三种强题形：从“观察规律”推进到“解释规律为什么出现”

NeurIPS 2025 runner-up *Superposition Yields Robust Neural Scaling* 被 award committee 强调的，就是不满足于观察 scaling law，而是解释其机制、何时成立、何时失效。

下一轮看到 finance/AI 中一个 robust empirical law 时，不要马上做 another benchmark；问：

> **这个 law 的控制变量到底是什么？为什么？什么时候 break？**

这也是 P1 比“多资产数据更多是不是更好”强的原因。

---

## 5. Negative finding 完全可以是 Main-level contribution，但必须击中重要 assumption

NeurIPS 2025 RLVR runner-up 的价值就在于挑战一个基础信念：RLVR 看起来提高 reasoning，但未必真的扩展 base model 的 reasoning capacity。

所以我们不需要“赌正现象”。

最好的问题应满足：

- positive 有解释；
- negative 有解释；
- nonlinear / regime-dependent 更好；
- 任何结果都能区分 competing accounts。

不要设计：

> “模型失败才有论文”的题。

---

## 6. 顶会并不只奖励 method novelty

NAACL 的 best-paper policy 明确把多种贡献都视为强贡献，包括新的 insight、evaluation standards、algorithm/data/reproducibility；并明确指出 paper 不需要“flawless”，interesting / new idea 本身可以更重要。

ICLR 2025 Outstanding committee 也明确以 theoretical insight、practical impact、writing、experimental rigor 等综合因素评估。

因此下一轮不要因为没有一个新 architecture 就觉得题不够大。

真正缺的是：

> **clear scientific object + important belief change + decisive evidence。**

---

# 三、下一轮 searcher 应该从哪里长题

不要只搜 AI4Finance。

继续高权重使用：

## A. ordinary AI × ordinary quant

分别读：

- ICML / ICLR / NeurIPS / ACL / EMNLP / NAACL 强论文；
- durable quant / finance 论文；

寻找：

> AI assumption A × finance structural friction B

或：

> finance unknown X × new AI leverage Y。

重点是 **cross-provenance composition**，不是 keyword overlap。

---

## B. AI strong-paper reverse engineering

不是照抄 award paper 的 topic，而是抽：

- 它挑战了什么默认 assumption？
- 它为什么不是 method-gap paper？
- decisive experiment 为什么一眼能区分 competing explanations？
- 哪个变量是作者真正重新定义的 scientific object？

然后再问 quant 是否存在一个未被触及的对应结构。

---

## C. quant standing problems

持续覆盖，不要只盯 microstructure：

- asset pricing；
- cross-section；
- portfolio choice；
- execution / liquidity；
- options / volatility；
- market design；
- risk；
- macro-finance；
- factor structure；
- market impact；
- high-frequency dynamics；
- institutional constraints；
- implementation / capacity / transaction costs。

尤其寻找：

> 旧问题过去为什么不可答？
> 现在新的 FM / agent / intervention / public data / synthetic control 为什么让它第一次可答？

---

## D. practitioner structural failures

AQR、Oxford-Man、Man AHL、Two Sigma 等不是用来找“公司博客题”，而是发现：

- 学术 metric 与实际失败在哪里脱节；
- 哪些 assumption 是实践中真正 load-bearing；
- 哪些变量在 benchmark 中被忽略。

随后必须回到学术 literature 做 owner / generalization audit。

---

# 四、下一轮的工作节奏：不要机械执行 prompt

这份 handoff **不是固定算法**。

下一轮 LLM 必须拥有调整搜索流程的自由，但必须持续对齐目标会议。

## Research heartbeat

每出现以下任一情况：

- 1–2 个 serious candidate；
- 连续 3–5 个 dead walls；
- 连续 idea 开始同质化；
- 一个 conceptual lens 占据搜索太久；

停止 brainstorm。

重新读取一批：

- ICML / ICLR / NeurIPS 当前 Outstanding / Best / Honorable Mention；
- ACL / EMNLP / NAACL 当前 Best / Outstanding；
- 对应方向近两年 Main；
- durable finance lineage；
- quant practitioner research。

然后自问：

> 我现在还是在学习优秀研究者怎样提出 scientific question，还是已经退化成 paper-gap autocomplete？

> 我是不是把一个 known AI failure 只换到了 finance setting？

> 我是不是被某个漂亮 conceptual lens 困住了？

> 如果明天看到顶级组发出这篇论文，我会觉得“这个问题本来就应该被回答”，还是只觉得“实验挺巧”？

根据答案随时修改 generator、search surface、甚至 kill criteria。

**不要因为 prompt 写了某个流程就机械执行到底。**

---

# 五、一个 serious candidate 真正要过的门

不要做长 checklist autocomplete。真正抓住以下 8 个问题即可：

1. **Mother question**  
   去掉方法名，问题还重要吗？

2. **Belief change**  
   答案会改变 AI researcher 的什么 belief？会改变 quant researcher 的什么 belief？

3. **Two-way load-bearing**  
   finance 与 AI 任意删掉一边，论文会不会实质变成另一篇？

4. **Competing accounts**  
   至少两个 knowledgeable researcher 都可能相信的答案是什么？

5. **Why now**  
   为什么 3–5 年前难以可信回答？

6. **Decisive E01**  
   什么最小 experiment / theorem / natural intervention 可以最大化 information gain？

7. **Ownership**  
   closest papers 能否几乎直接写出我们的核心 conclusion？

8. **Conference identity**  
   abstract 第一段首先是 general AI/learning/agent/language science，还是“finance is important”？

只有前 6–8 个基本成立，才 candidateize。

---

# 六、下一轮特别要避免的 false friends

已经反复证明容易浪费搜索预算：

- “known AI problem + finance natural experiment”；
- generic performativity / endogeneity；
- generic POMDP / hidden state；
- generic no-arbitrage constraint；
- generic regime shift；
- generic tail risk；
- generic calibration under feedback；
- generic reward hacking / manipulation；
- generic synthetic-to-real gap；
- generic redundant inputs；
- generic multiple testing / agent p-hacking；
- “更真实 simulator”；
- “更好的 trading agent”；
- “FM 能否预测某个金融变量”。

这些不是永远禁止，而是 broad form 已经非常容易落入 direct-successor territory。只有出现**新的 scientific object**才允许重新打开。

---

# 七、当前两条 survivor 给我们的正反馈

## P1 为什么过关

`State Coverage ≠ Exposure Coverage` 不是“finance panel 更复杂”。

它重新质疑 foundation-model scaling 里一个基础 abstraction：

> data size 是否真的能被压成 scalar token count？

finance panel 的 shared latent market state 提供一个普通 iid / univariate scaling 没有的结构，因此 finance 不是 decoration。

## P2 为什么过关

`Forecast Skill ≠ Structural Skill` 不是“cointegration 很重要”。

它问的是：

> mechanism 明明存在于数据甚至 pretraining generator 中，但普通 predictive objective 是否真的给模型足够 pressure 去 acquire mechanism？

cointegration 只是第一个具有明确 restoring-law oracle 的 controlled mechanism。

下一轮新题也应该尽量达到这种程度：**finance 提供 structure；论文改变 general AI belief。**

---

# 八、下一轮开场指令（可直接复制）

你现在接手 `Nhckdvrl/ssn-group-papaer/AI4Quant` 的下一轮 research-question search。

目标会议：

**ICML / ICLR / NeurIPS Main**

若 scientific object 涉及 language / LLM / agents / text，同时用：

**ACL / EMNLP / NAACL Main / TACL**

校准 scientific taste。

当前已有 2 条 `PILOT-AUTHORIZED`，不要重复推进或重新包装：

1. `State Coverage ≠ Exposure Coverage`
2. `Forecast Skill ≠ Structural Skill`

完整注册见 `AI4Quant/selected/`；已失败方向见 `AI4Quant/failed/FAILED_TOPICS.md`。

当前任务只有一个：

> **继续寻找新的、彼此独立的 Main-level AI4Quant scientific questions。**

不要默认从 AI4Finance paper limitation 开始。

优先做：

> **ordinary AI scientific object × ordinary quant structural friction → new question**

寻找 AI 的 load-bearing assumption 在 finance 中被真正击穿，或者现代 AI 第一次让长期 quant unknown 可识别。

必须同时防止两种漂移：

- finance-only：最后只是 RFS/JF question，AI 很弱；
- AI-only：最后只是已知 AI failure 换 finance dataset。

不要太早 candidateize。大量产生 heterogeneous raw pressures；owner / general consequence / feasibility 基本过关后再命名。

当连续 3 个 idea 共享同一 abstract skeleton，或一个方向连续两轮只能靠缩限定条件绕 owner，**立刻换 scientific object**。

搜索过程中每 1–2 个 serious candidate / 3–5 个 dead wall 做一次 heartbeat：重新读取当前 ICML/ICLR/NeurIPS/ACL/EMNLP/NAACL 的强 Main / Best / Outstanding work，检查自己是否仍与顶会 scientific taste 对齐，并允许主动修改搜索流程。

不要机械服从本提示词的固定步骤。优秀论文不会从 checklist 自动生成。提示词的作用是防止漂移，不是替代 research taste。

允许最终 0 survivor。

但 0 survivor 必须来自真正广泛、异质、持续校准的 scientific search，而不能来自在一堵墙里不断换措辞后全部杀掉。

最后始终记住：

> **不要问“AI 能给 quant 做什么”；分别理解 AI 现在真正不知道什么、quant 现在真正不知道什么，再找它们在哪里发生结构性碰撞。**
