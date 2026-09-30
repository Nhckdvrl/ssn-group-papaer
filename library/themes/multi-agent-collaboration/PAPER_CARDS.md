# 论文卡 — 多智能体与大小模型协作（2026-09-30）

模板见 `search/README.md` §4.1。**证据等级说明**：本批次无法访问 arXiv / OpenReview 全文（网络策略），卡片基于摘要（`tools/venue_corpus`）、官方代码 README、以及检索摘要。标注 `[摘要级]` 的卡片在驻留阶段一需要回到全文核对“方法 / 实验 / 基线”三项。idea 来源一律为 **RECONSTRUCTED**（我们重建的合理路径），不是作者自述。

---

## A. 训练出来的协作（主谱系）

### A1. MAPoRL — Multi-Agent Post-Co-Training for Collaborative LLMs with RL（ACL 2025 main）`[摘要级]`
- **形态**：新训练范式（方法）+ 少量分析。
- **背景与压力**：多智能体框架几乎都用冻结 LLM + 提示/工作流；单独训练每个模型并不会让它们更会协作。
- **改变的前提**：协作能力应当**在协作中**被训练出来（多个 LLM 一起讨论，最终答案由验证器打分作为共享奖励，并额外奖励“纠正性/说服性”的发言）。
- **idea 来源（RECONSTRUCTED）**：RLHF/RLVR 已证明“对最终输出打分 + RL”能塑造单模型行为 → 自然的一步是把讨论过程纳入 rollout、把奖励给团队。
- **与近邻的距离**：相对 Multiagent Debate（推理时协作，无训练）——增量是“训练”；相对 Multiagent Finetuning（ICLR 2025，各模型在自己生成的数据上 SFT 以保持多样性）——增量是“RL + 协作奖励”。
- **证据**：多数据集；跨领域迁移；异构对（Phi3-3.4B + Qwen2.5-3B、Phi3 + Llama3-8B）。
- **可迁移动作**：把“协作”从推理时技巧变成训练目标。
- **对我们**：异构协同训练的最早参照；它测了“跨数据集迁移”，**没有测“跨伙伴迁移”**（换一个没一起训练过的模型）。

### A2. MAGRPO / CoMLRL — LLM Collaboration with Multi-Agent RL（AAAI 2026；arXiv 2508.04652）`[README 级]`
- **形态**：问题形式化（Dec-POMDP）+ 算法（MAGRPO，多智能体版 GRPO）+ 开源库。
- **压力**：已有协作训练多依赖集中式执行和人工协议。
- **改变的前提**：把 LLM 协作写成**去中心化合作 MARL**，每个 LLM 是一个智能体、共享团队回报。
- **与近邻的距离**：相对 MAPoRL——更一般的 MARL 形式化与多种算法（MAREINFORCE、MAGRPO、IAC/MAAC）；环境扩展到写作、代码、**Minecraft 协作建造**。
- **证据**：写作（TLDR、arXiv 扩写）、代码（MBPP、HumanEval、CoopHumanEval、ClassEval）、Minecraft（StrBuild、HouseBuild）。
- **对我们**：**最便宜的起点**（可从 Qwen2.5-0.5B 开始，pip 可装）；Minecraft 环境同时对应“游戏 NPC 队友”偏好。

### A3. AT-GRPO / Stronger-MAS（ICLR 2026 poster，均分 4.0）`[摘要级]`
- **形态**：失败模式（GRPO 分组假设在 MAS 中失效：不同角色、不同轮次的 prompt 不同）+ 修复（按智能体与轮次分组）+ 训练系统（PettingLLMs）。
- **证据**：游戏、规划、代码、数学；长程规划从单智能体 RL 的 14–47% 提到 96–99.5%。
- **与近邻的距离**：相对 MAGRPO——指出“分组”这一具体的基线假设错误并修复（典型的“强基线上的痛点 → 最小修复”）。
- **对我们**：分数不高（4.0）仍被接收，说明审稿人看重“具体失败 + 修复 + 多任务”这一结构。

### A4. MARTI（ICLR 2026 poster，均分 5.33）`[摘要级]`
- **形态**：开源框架（集中式交互 + 分布式策略训练 + 异步多轮 rollout）。
- **关键结论**：数学任务上，**收敛后、等推理预算**的多智能体系统胜过单智能体。
- **对我们**：这是 P1（算力匹配）最直接的已有证据；我们的增量只能是**更严格/更全面的会计**（训练算力、参数量、跨任务、跨家族），或者发现它不成立的区间。

### A5. Lazy Agents → Dr. MAMR（ICLR 2026 poster）`[摘要 + 检索摘要]`
- **形态**：命名失败模式（“懒惰智能体”）+ 理论根因 + 因果影响度量 + 可验证奖励修复。
- **背景**：ReMA（NeurIPS 2025）式的 元思考智能体 + 推理智能体 两角色 RL。
- **发现**：训练中推理智能体的**因果影响逐渐下降**（输出空或简单确认），元思考智能体包办；根因是多轮 GRPO 中防长度偏置的归一化项，反而偏好“最省事”的续写。
- **证据**：7B 模型 pass@1 58.43%（ReMA 51.97%，单智能体 GRPO 55.08%）。
- **可迁移动作**：**用反事实/因果贡献度量每个成员的真实作用，并跟踪它在训练中的变化**。
- **对我们**：P3 的直接出发点——在**大+小**团队里，谁会变懒、谁会包办？

### A6. Dr. MAS — Stable RL for Multi-Agent LLM Systems（NeurIPS 2026）`[README + 检索摘要]`
- **形态**：失败模式（全局归一化基线偏离各智能体的奖励分布 → 梯度范数尖峰）+ 最小修复（按智能体归一化优势）+ 框架。
- **证据**：数学 +5.6% avg@16，搜索 +15.2% avg@16；基本消除梯度尖峰；支持异构模型协同训练（如 2×Llama-3.2-3B + 1×Qwen2.5-7B）。
- **可迁移动作**：一个非常小的统计量修正，配上清晰的失败诊断，就是一篇 NeurIPS。
- **对我们**：**主要强基线**；官方给出单节点耗时（搜索 3×3B 4×H100 约 13 小时）。

### A7. TeamTR（ICML 2026）与 SAT（AAMAS 2026）——同一作者组 `[摘要 + 检索摘要]`
> 注意：Stanford 的 *Self-Organizing Agent Teams Learn to Reason Together*（2609.22682）缩写也是 SAT，内容不同（文本层策略库），见 B1 与 F 节。
- **TeamTR 形态**：失败模式（共享上下文团队顺序微调时的“移动靶”：更新一个成员改变其他成员面对的上下文分布；按缓存 rollout 评估时误差随成员数二次累积）+ 信赖域修复 + 改进下界；支持**即插即用替换成员**（通过一个信赖域对齐步骤）；平均 +7.1%。
- **SAT 形态**：无协调器的顺序智能体调优；按团队策略演化的在线优势估计 + 每智能体 KL 信赖域 → 单调改进；**即插即用不变性**；3×4B 团队在 AIME24/25 上超过 Qwen3-32B（+3.9%），换入两个 8B 成员 +10.4%。
- **与我们的距离**：它们把“换成员”作为**方法保证的性质**来追求；**没有**回答“一般的协同训练方法（MAGRPO、Dr. MAS、AT-GRPO）训出来的团队换伙伴会怎样”，也没有从 ZSC 角度做系统的交叉配对测量。
- **对我们**：P2 最近的近邻；写定位表时必须逐项比较。

### A8. SCOPE — One Frozen Simulator Is Not Enough: Simulator Collapse in Multi-Agent RL（arXiv 2608.12253）`[检索摘要]`
- **形态**：失败模式（对单一冻结的用户模拟器做 RL，模拟器的众数行为被策略利用 → 迁移到新模拟器/真人变差）+ 理论形式化 + 推理时（verbalized sampling，+9%）与训练时（种群协同训练，+14%）两种修复 + 人类实验；开源 SCOPE 框架。
- **与我们的距离**：这是 ZSC 教训在 **人–AI（用户模拟器）** 场景的首次系统引入；**智能体–智能体团队**（共享奖励、角色分工、大+小）是不同设定。
- **对我们**：证明“伙伴过拟合”在 LLM RL 中真实存在且可发表；也意味着 P2 的窗口在收窄，需要尽快测量。

---

## B. 提示式协作的失败与等算力怀疑

### B1. Multi-Agent Teams Hold Experts Back（ICML 2026）`[摘要 + 检索摘要]`
- **形态**：引入组织心理学构念（strong synergy：团队 ≥ 最强成员）+ 分解（识别 vs 利用）+ 对话分析 + 权衡。
- **发现**：自组织 LLM 团队达不到专家水平（HLE 上最多 −41.1%），即使被告知谁是专家；瓶颈在**利用**而非识别；机制是“折中式共识”（平均专家与非专家观点），随团队规模增加；专家本身的“认知灵活性”也有害；共识倾向对对抗成员更鲁棒。
- **证据**：MMLU-Pro、GPQA-Diamond、SimpleQA、HLE、MATH-500 各 100 题子集；前沿模型；有代码。
- **idea 来源（RECONSTRUCTED）**：人类团队研究里“过程损失”的经典结论 → 问 LLM 团队是否一样 → 用“被告知专家身份”的对照拆开识别与利用。
- **对我们**：P3 的行为基线——**训练能否学会按专长加权？**提示式团队做不到，是训练的机会点。
- **后续（同一第一作者，2609.22682，2026-09-19）**：*Self-Organizing Agent Teams Learn to Reason Together*——固定团队离线反思以往协作，提出并筛选“组织策略”（角色、对话阶段、参与、信息流）进入策略库，冻结后迁移到新题与新 benchmark；只用 15 道数学 + 25 道研究生级知识题学习；5 个数学/物理 benchmark 平均 66.7%，对比最强成员 48.8%、**等算力的最强个体 58.7%**、成员独立答案上的完美路由 59.0%；AIME 2026 上超过完美路由 13.4pp。
  - **生长模式**：ICML 2026 命名失败（团队拖累专家）→ 约 7 个月后同组给出修复。命名的失败本身就是后续工作的入口。
  - **与我们的距离**：修复在**文本/提示层**（策略库），不改权重；团队是**固定**的——策略库换一组成员是否还有效（P2），以及权重层（RL）学到的协作与文本层学到的协作有何不同，都没有回答。

### B2. HiddenBench — Systematic Failures in Collective Reasoning under Distributed Information（ICML 2026）`[摘要级]`
- **形态**：引入社会心理学 hidden profile 范式 → benchmark（65 任务）→ 失败模式（不会推理“别人可能知道但还没说的信息”，过早收敛于共享证据）→ 轻量结构化通信协议修复。
- **证据**：15 个前沿 LLM；多智能体分布式信息下 30.1% vs 单智能体完整信息 80.7%；规模/个体推理能力都预测不了集体表现。
- **对我们**：P6（协作原生任务）的现成评测；可以问“RL 协同训练能否修复 hidden-profile 失败”。

### B3. At Equal Inference Cost, Multi-Agent Structure Does Not Beat a Single Frozen Agent（arXiv 2609.04217）与 When Do MAS Help? An Information Bottleneck Perspective（arXiv 2607.16133）`[检索摘要]`
- **前者**：固定总调用次数，演化 Planner-Executor-Critic 团队的角色提示 vs 只演化单个执行者（冻结 7B）；ALFWorld 上团队 0.769 vs 单智能体 0.754，p=0.80，却多用 1.8 倍评估调用。
- **后者**：单智能体把全部推理轨迹放在一个上下文；多智能体用有界中继消息连接隔离的局部上下文 → 信息瓶颈权衡；中继近乎充分时 MAS 有益，**弱模型受益更多**，强模型收益缩小甚至反转；18 组受控实验、5 个 benchmark、3 个规模。
- **对我们**：P1 的理论与实验背景；“弱模型受益更多”与“大+小 / 全小”偏好直接相关——**小模型团队也许恰好处在协作最有利的区间**，值得在训练后重新测量。

### B4. Representational Similarity and Model Behavior in Multi-Agent Interaction（ICML 2026；ICLR 2026 曾以 5.5 分被拒）`[摘要级]`
- **形态**：引入神经科学发现（神经相似性预测社会亲近与合作；创新来自相异个体）→ 276 对模型 × 8 个游戏 → 相似表征：合作更好、新颖性更低；早期层相似性关联最强。
- **对我们**：P4 的白盒先例——表征相似性是**配对选择**与**交叉配对结果**的潜在预测量；训练前后的表征变化可以接到这条线上。

---

## C. 零样本协调（ZSC）/ ad-hoc teamwork（经典 MARL 谱系）

### C1. Other-Play（ICML 2020）→ FCP（NeurIPS 2021）→ ZSC-Eval（NeurIPS 2024）→ Cross-environment Cooperation（ICML 2025 Oral）→ Unsupervised Partner Design（ICML 2026 spotlight）`[摘要级]`
- **共同压力**：自博弈训练出的智能体学到**任意约定**，只对训练伙伴有效；换伙伴（尤其是人）就崩。
- **演化**：Other-Play 用环境对称性打破任意约定 → FCP 用伙伴种群（含历史 checkpoint）训练 → ZSC-Eval 指出评测伙伴分布与部署分布不一致，提出评测协议 → *Diversity Is Not All You Need*（NeurIPS 2024）指出伙伴还需要专精 → CEC 发现**单伙伴 + 大量环境**也能学到通用协作规范 → UPD 按“可学性”在线生成伙伴，无需预训练种群，并做人类实验。
- **可迁移动作**：**交叉配对矩阵（self-play vs cross-play）**是这一领域的标准测量；种群训练、环境多样化、伙伴生成是标准修复。
- **对我们**：这是 P2 的“成熟构念”。提示式 LLM 在 Overcooked/Hanabi 中对陌生伙伴较稳（LLM-Coordination 2023；Hanabi 中不同 LLM 的交叉配对平滑插值，ICML 2026），但**RL 协同训练之后是否仍然稳健**，没有系统测量——这正是“把 MARL 的经典教训接到 LLM 团队训练上”的接口。

---

## D. 大 + 小协作与通信媒介

### D1. RelayLLM（arXiv 2601.05167）`[检索摘要]`
- 小模型作为控制器，学会发出命令 token 请求大模型生成 n 个 token；只用 1.07% 的 token 调用大模型，恢复约 60% 的差距（6 个数学 benchmark）。
- **对我们**：“小模型学会求助”是大+小团队训练中的一种角色分工；在协同训练团队中，它会自然出现还是被“懒惰/包办”吞没？

### D2. LatentMAS（ICML 2026 spotlight）/ Cache-to-Cache（ICLR 2026）/ KVComm（ICLR 2026）`[摘要级]`
- 智能体之间用隐藏状态 / KV 通信替代文本：LatentMAS 训练无关，9 个 benchmark 上比文本 MAS 最高 +14.6%、输出 token 减少 70.8–83.7%；C2C 用可学习投影融合 KV，比文本通信 +3.1–5.4%、延迟 2.5× 更低。
- **对我们**：隐空间通信在 arXiv 上 2026 年已 36 篇、且已有因果审计；作为 P5 的对照分支（“训练出的文本约定” vs “隐空间通道”），而不是主线。

---

## F. 最新 arXiv 近邻（2026-04 → 2026-09，检索摘要级；驻留阶段一回原文核对）
| 论文 | 要点 | 与我们的关系 |
|---|---|---|
| *Training Small LLMs as Spatial Multi-Agent Policies*（2608.01425） | 2–4B LLM 作为“符号选项库”上的策略，每个智能体一个私有 LoRA，用 PA-MAGRPO 训练；Cleanup、Overcooked（Asymmetric Advantages）、Commons Harvest 上从 0 回报提升到可用水平 | **小模型合作游戏的现成基底**（对应游戏 NPC 偏好）；交叉配对 / 换伙伴可以直接在它的环境上测 |
| *SRPO: Setwise Relative Policy Optimization for Multi-Agent LLMs*（2609.08452；与下一行的 SRPO 同名不同文） | 多智能体 LLM 的新相对策略优化 | 方法层（P7，已拥挤） |
| ***Training Generalizable Collaborative Agents via Strategic Risk Aversion***（SRPO，Caltech Mazumdar 组，2602.21515） | 诊断：协同训练的策略换伙伴就失败，原因是训练中的**搭便车**与缺乏策略鲁棒性；把策略风险规避（RQE 导出的目标）接到 IPPO 等策略优化上；在协作 benchmark 与**一个 LLM 协作任务的初步小规模实验**上，交叉配对联合准确率相对 IPPO 最高 +19.27%，并测了与未训练模型配对的鲁棒性 | **P2 最近的方法 + 理论近邻**。增量应放在：主流 LLM 多智能体 RL 框架（Dr. MAS / MAGRPO / AT-GRPO）上的系统测量（种子 / 尺寸 / 家族）、机制（消息、角色约定、白盒）、等算力比较；SRPO 作为修复基线 |
| *Self-Organizing Agent Teams Learn to Reason Together*（Stanford Zou 组，2609.22682） | 见 B1“后续”：文本层策略库，等算力下超过最强成员与完美路由 | P1/P3 近邻；P2（策略库换成员）未回答 |
| *ALEM: Benchmarking Open-Ended Multi-Agent Coordination in Language Agents*（Edinburgh，2606.08340） | JAX 实现的 Craftax 类开放式协作世界；13 个 LLM 零样本同质团队，以训练 10 亿步的 MARL 智能体为参照；个体能力 ≠ 协作能力，通信贡献最大；**ZSC 实验中 LLM 智能体对陌生伙伴稳健，而 RL 智能体不稳健** | P2 的对照事实（提示式 LLM 天然较稳）；P8 的候选环境（代码 alem-world/alem-env） |
| *The Collaboration Gap*（Davidson、Fourney、Amershi、West、Horvitz、Kamar；2511.02687） | 单独很强的模型与自己的副本分工解迷宫时显著变差；“relay inference”（先由强模型开局）可改善 | P3/P6：协作原生任务与大+小开局 |
| *Co-RL: Unsupervised Reasoning Emerges from Diverse Cohort in Multi-agent RL*（2608.17253） | 不共享参数的多个模型用同伴给出的奖励做 RL（无标签）；**异族、异尺寸**与改写样本增加群体多样性，减少相关错误；文本 7 个 benchmark +3.0–8.6% | 异构性作为训练资源；代码 DrStranded/Co-RL |
| *Everyone Contributes! MAC-SPGG*（AAMAS 2026，2508.02076） | 顺序公共品博弈：重新设计奖励使“努力贡献”成为唯一子博弈完美均衡，消除搭便车 | P3（懒惰/搭便车）的博弈论修复 |
| *Evolve as a Team: Meta-Team*（2605.29790） | 智能体级、交互级、团队级三层反思式自进化；6 个长程 benchmark 上比手工 MAS 平均 +6.6% | 文本层团队学习（与 SAT-Stanford 同类） |
| *Experience Sharing in Mutual RL for Heterogeneous Language Models*（2605.07244） | 异构 LM 之间的经验共享式 RL | 异构训练近邻 |
| *PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play*（2605.16727） | 教师/学生**种群**联合在线训练，难度信号来自种群交叉评估 | “种群”思想已进入 LLM 自博弈（推理），但目标不是协作伙伴的泛化 |
| *CORY: Coevolving with the Other You*（NeurIPS 2024） | 把一个 LLM 复制成先行者/观察者两个智能体做合作 MARL 微调 | 早期协同训练 |
| *ConventionPlay*（2604.18123）、*Partner Capability Estimation for Task-Agnostic Adaptation in Ad-Hoc Teamwork*（2607.27177） | 经典 ad-hoc teamwork：面对能力受限/约定多样的伙伴，学会试探、带领或跟随 | ZSC 谱系在 2026 年仍活跃（非 LLM） |
| *Beyond Cooperative Simulators: Generating Realistic User Personas for Robust Evaluation of LLM Agents*（2605.12894） | 过于合作的用户模拟器高估智能体；生成真实人格做鲁棒评测 | 与 SCOPE 同一压力的评测侧 |

---

## E. 读完这一批，我们得到的研究动作
1. **命名的失败模式 + 最小修复**在本题材最容易被接收（AT-GRPO、Dr. MAMR、Dr. MAS、TeamTR），前提是失败是在强框架上**真实跑出来的**。
2. **引入他领域的成熟构念**（strong synergy、hidden profile、表征相似性、ZSC）并大规模测量，是分析型论文的主要形态。
3. 本题材审稿人最常挑的短板是**不公平的比较**（没有等算力、没有强单模型基线）；这正是我们的纪律可以补上的地方。
4. 当前最空的一层是：**“训练出来的协作到底是什么、在换伙伴/换规模/换任务时是否还在”**——而不是再多一个信用分配算法。2026 年已有人从方法侧进入（SRPO：策略风险规避 + 小规模 LLM 实验；SCOPE：人–AI 模拟器坍缩；SAT-AAMAS/TeamTR：即插即用），这说明问题真实、可发表，是“探索空间”而不是空白；主流框架上的系统测量与机制解释仍然没有人做。
5. **命名的失败是下一篇的入口**：*Teams Hold Experts Back*（ICML 2026）→ 同一作者的 *Self-Organizing Agent Teams*（2609.22682）。我们的测量如果跑出失败，第一篇是测量 + 最小修复，第二篇就是更完整的修复。
