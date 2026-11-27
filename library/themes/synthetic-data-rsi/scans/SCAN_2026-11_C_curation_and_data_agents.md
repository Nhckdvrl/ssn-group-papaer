# 文献扫描 2026-11 · C 区：数据筛选/配比/归因/数据研究 agent

扫描日期 2026-11-27。范围：LLM/VLM 训练（预训练、SFT、RL）中的数据筛选、混合配比、数据归因/估值，以及“根据训练反馈自动设计数据流水线或训练配方”的 LLM agent。来源：候选清单（ICLR 2027 投稿 + NeurIPS 2026 录用）与 2026-04 至 2026-11 的 arXiv。

读法说明：下面“精读”指读了方法、实验设置、主表、局限；多数论文的长附录（提示词、逐任务表）只翻了与结论相关的部分，已在每篇里标注。OpenReview 对本机返回 403（challenge），所以清单里 ICLR/NeurIPS 条目凡没有 arXiv 版的，只有清单里的摘要片段（该片段本身被截断），一律标 ABSTRACT ONLY。组里已知的工作（Curation-Bench、RSIBench-Data、CurateEvo、DoReMi、RegMix、LESS 等）不重读；与它们的关系只在“与已知工作关系”里提到。

评分均为清单给出的 ICLR 2027 审稿均分（1–4 档，全体均值 2.21）。

---

## 一、精读论文

### 1. DataFlex-RL: An Evaluation Platform for RLVR Data Policies
- 状态：arXiv 2609.06107（2026-09-05），技术报告；无评分。链接 https://arxiv.org/abs/2609.06107
- 问题：RLVR（GRPO）里的“数据策略”（选 rollout、给 rollout 加权、在线调域配比）在固定 recipe 下是否比均匀采样更好。
- 设置：verl + GRPO，5 rollouts/prompt，300 步；训练集 15k 题（数学/逻辑 Knights&Knaves/科学 SciQ 各 1/3）；12 个评测基准，Overall = 数学/逻辑/科学三域各自平均后再平均。主实验 Qwen2.5-7B-base，13 种配置（4 种选择 + 4 种重加权 + 3 种自适应配比 + 均匀基线 + 静态等比配比对照），每种 12 个配对 seed。扩展：Llama-3.1-8B-base 12 seed；Qwen2.5-1.5B/3B/14B、Llama-3.2-3B 各 3 seed 的 6 配置子集。总计 591 次运行。
- 结果：
  - 均匀 GRPO 相对未训练 checkpoint +7.76 分（Qwen-7B，95% CI [7.28, 8.25]）；Llama-8B +10.25（CI [7.75, 12.33]）。
  - Qwen-7B 上 8 个选择/重加权方法相对均匀的配对差在 −0.90 到 +0.08 之间，8 个 95% CI 全部包含 0（difffilter +0.08 [−0.67, 0.82]；gfpo −0.90 [−1.87, 0.08]；per −0.86 [−3.28, 1.57]）。9 个策略均值整体跨度 0.97 分，约为 GRPO 本身增益的 1/8。
  - 3 个自适应配比相对静态等比：reward_gap +0.45 [−0.09, 1.00]，dump_ucb +0.61 [−0.02, 1.25]，tscl +0.16 [−0.61, 0.93]，均含 0。
  - 排序对 seed 数不稳：3-seed 子集上 topk 第一，12 seed 后 difffilter 均值最高、topk 低于基线。
  - Llama-8B 上 13 个配置均值 18.66（softmax）到 21.98（diffband），基线 21.12，无共同赢家；difffilter −1.09 [−2.84, 0.65]。
  - 规模/家族扫描（每格 3 seed）：符号随模型变化，如 difffilter 在 1.5B/3B 低于基线（−0.83/−0.79），在 7B/14B 略高（+0.08/+1.20）；maxvar 各行均低于基线；tscl 在 1.5B 低于对照、在 14B +1.43。
  - 评测覆盖敏感性（Qwen2.5-7B-Instruct，9 配置，3 seed）：只含数学+GPQA 的 6 基准汇总与领域均衡 12 基准汇总排名 Spearman ρ = −0.33，方法间跨度从 0.90 变成 3.31；Macro-12、Item-12 与均衡汇总 ρ = 0.88。
  - 机制对照（附录 A.2，Qwen2.5-7B-Instruct，3 seed，均值±标准差）：difffilter 目标选择 53.81±1.38 对匹配随机 54.29±1.85；maxvar 53.42±0.56 对匹配随机 50.93±3.17；topk 52.86±0.66 对 52.29±1.54。匹配更新 token 数后 difffilter、maxvar 上升、topk 下降。
- 局限（作者写出）：只有数学/逻辑/科学三域、训练 300 步；辅助模型只 3 seed，不作为独立显著性检验；自适应配比的“静态对照”是 campaign 局部对照，均值与主基线不同。作者披露早先的 Llama 14–16 分结果来自把不支持的数学任务静默记 0 的评测器，已排除。
- 代码/数据：https://github.com/haolpku/DataFlex-RL （含 results/ 原始数字）
- 精读范围：全文主体和附录 A；参考文献略。

### 2. AutoData: Agentic Search for Pre-training Data Selection
- 状态：arXiv 2609.19754（2026-09-17），Weco AI / UvA；无评分。链接 https://arxiv.org/abs/2609.19754
- 问题：用 AIDE 风格 agent 在“可执行选择算法”空间里搜索预训练数据选择规则，是否优于人工设计的 curation 流水线。
- 设置：源语料 NVIDIA ClimbMix（400B token，553M 文档，已是人工 curation 过的语料）；预算 B = 14.37M 文档（约 2.6%）；特征库含词法统计、WebOrganizer topic×format（576 类）、Qwen2.5-0.5B 的 bpb、Gemini-3-Flash 的 LLM 标注。搜索用 GPT-2 depth-8（125M）proxy，每个候选在从所选子集均匀抽的 88 万文档上训练，4 个 proxy seed，约 10 min/次（1×H100）。三个 agent LLM（GPT-5.5、Gemini-3-Pro-Preview、Claude-Opus-4.7）共生成 1200 个候选。基线：随机均匀、DCLM 分类器、perplexity 过滤、RegMix（24 topic，128 个 proxy 混合）。评测：val-bpb（保留 shard）与 CORE（22 任务）。每个 scale 3 个训练 seed，配对 t 检验。
- 结果（Table 1，均值±样本标准差，3 seed）：
  - val-bpb（越低越好），随机均匀 / AutoData(val-bpb)：d8 0.9484±0.0002 / 0.9475±0.0000；d12 0.8477±0.0003 / 0.8473±0.0001；d16 0.7806±0.0002 / 0.7802±0.0001；d20 0.7346±0.0004 / 0.7349±0.0004；d24（1.3B）0.7055±0.0011 / 0.7065±0.0003。即 d8 差 −0.0009（约 4 个随机基线标准差），d20 与 d24 随机均匀不差于 AutoData；作者自述“d24 与默认 ClimbMix 相当”。
  - DCLM、PPL 过滤、RegMix 在 val-bpb 上全部劣于随机均匀（d8：0.9954、0.9605、0.9550 对 0.9484；d24：0.7499、0.7267、0.7124 对 0.7055）。
  - CORE（越高越好）：d8 随机 0.1041±0.0125，AutoData(CORE) 0.1142±0.0023，AutoData(val-bpb) 0.1037±0.0030；d16 AutoData 低于随机（0.2009/0.1959 对 0.2053）；d24 AutoData(CORE) 0.2727±0.0128 对随机 0.2609±0.0058。作者：CORE 上的提升不显著（“likely high variance of CORE”）。
  - 搜索对象不迁移：用 val-bpb 搜出的配方在 CORE 上与随机持平，用 CORE 搜出的配方在 val-bpb 上 d8 只 0.9529（劣于随机 0.9484）。
  - 配方形态（Algorithm 1/2）：val-bpb 配方保留 1/3 均匀随机“骨架”，CORE 配方保留 1/2；其余部分是 4 个特征的复合打分 + Gumbel 噪声锦标赛选择。三个 agent 都不使用单特征排序，也几乎不用硬阈值/全局 top-B（≤12%）。GPT-5.5 91% 用锦标赛，Gemini/Opus 87.5% 用分层配额；Gemini 只有 1–2% 的配方用类别特征。
  - 特征消融（GPT-5.5，带标注子集，随机基线 0.95181±0.00077）：词法 2 个特征、perplexity 1 个特征、类别 2 个特征、LLM 标注 3 个特征、全部 8 个特征分别为 0.95043/0.95037/0.95041/0.95021/0.95048，即 +1.7 到 +2.1σ，单个 perplexity 特征与全特征持平。
- 局限（作者写出）：仅 125M–1.3B、单一语料；有效性依赖 proxy 目标；最强结果依赖有成本的 LLM 标注。未写出：搜索成本与基线成本是否匹配（我按“1200 候选 × 4 proxy × 约 10 min”估算约 800 H100 小时，RegMix 基线用 128 次 proxy 训练；论文未把这当作匹配计算量的比较）。搜索选出的最优配方是在 proxy 上从 1200 个里取最好，再在同一 proxy 尺度上与基线比较；d8 以外的 scale 是迁移评测。
- 代码：声明将发布 https://github.com/WecoAI/AutoData
- 精读范围：全文（附录提示词未读）。

### 3. Advancement or Acceleration? How Data Curation Improves LLM Training
- 状态：arXiv 2610.36983v2（2026-11-23），JD.com/Oxford，preprint；无评分。链接 https://arxiv.org/abs/2610.36983
- 问题：数据 curation 是抬高可达到的终点性能（advancement），还是只让同样终点更快到达（acceleration）。
- 设置：理论（teacher–student 感知机，自洽方程）+ 实证。提出 Δ-诊断：用一次未 curation 基线运行、在训练预算 50% 处测“训练域损失与目标损失的差”，减去参考模型的同一差（熵修正）。混合实验：160M GPT 风格模型，SlimPajama 6B，7 个域；对比均匀与 RegMix、DoGE、Skill-It、Aioli、TANDEM；每个实验独立跑 5 次；另有 1.1B 复现（Table 3）。选择实验：TinyLlama-1.1B，5B token OpenWebMath 候选池，f=0.6，对比 Base-CT、随机、EL2N、InfoBatch、Token-Cleaning、RHO-1、BLADE。
- 结果：
  - 无 gap（Δ=0.076，均匀配比可行）：平均困惑度 均匀 19.71±0.17，RegMix 19.80±0.12，DoGE 20.17±0.16，Skill-It 19.68±0.16，Aioli 19.77±0.15，TANDEM 19.66±0.15，全部在实验波动内。早期 RegMix 曾领先 3.5 ppl，随训练消失。1.1B：TANDEM 增益 +0.05（160M）/ +0.11（1.1B）ppl。
  - 外生 gap（把 CommonCrawl 留作目标、不在训练池，Δ=0.468）：目标 ppl 均匀 49.19，各优化混合 40.2–41.1；内生 gap（池缩到 300M，小域被重复采样，Δ=0.649）：平均 ppl 均匀 28.60，TANDEM 26.02，增益 +2.58（160M）/ +2.29（1.1B）；外生增益 +8.95（160M）/ +5.31（1.1B）。
  - 选择，无 gap（OpenWebMath 内分布目标，Δ=0.016）：8 个数学基准平均 Base-CT 17.21，随机 16.38，EL2N 14.94，InfoBatch 14.71，Token-Cleaning 14.30，RHO-1 14.49，BLADE 17.54；目标损失无一致改善，保留比例从 1.0 降到 0.6 时损失总体上升，全保留最低。有 gap（MetaMath–Mammoth 目标，Δ=0.158）：RHO-1 27.06、BLADE 31.31，目标无关方法不涨。把目标在两者间插值，BLADE 增益从 +0.3 到 +14.1，随 Δ 单调上升（Spearman ρ=1，6 个插值点）。
- 局限：理论是感知机玩具模型；Δ 近 0 不是“无 gap”的证书（作者承认标量损失可能看不出分布 gap）；实验是 160M–1.1B；选择实验的有 gap 设置里 RHO-1/BLADE 使用了目标数据本身。
- 与已知工作关系：与 “Can Small Training Runs Reliably Guide Data Curation?”、Group-MATES/PDS 关心同一类现象（均匀/随机基线强），但给出的是“何时有头部空间”的条件而非方法排序。
- 代码：声明将发布。
- 精读范围：正文 1–7 与关键表；附录 Δ 统计细节略读。

### 4. Agentic Data Engineering for LLMs: System Design and a Controlled Empirical Study (ADE)
- 状态：arXiv 2610.14238（2026-10-09），UNC/Alibaba/PKU；无评分。链接 https://arxiv.org/abs/2610.14238
- 问题：agent 能否利用实验反馈逐步改进数据工程策略；策略在研究过程中未见过的评测集上是否仍有提升。
- 设置：四个任务，固定模型与训练协议。数学/代码 Long-CoT SFT 数据选择（Qwen2.5-7B-Instruct，从 3,840 条 OpenThoughts 轨迹的固定池里选 384 条）；数学奖励设计与课程（Qwen2.5-0.5B RFT，3,072 道 MATH 题，100 步）。基线：随机子集 / 仅结果奖励 / 随机顺序。agent：GPT-5.6 Sol（Codex，extra high reasoning），C=1 或 C=3 个并发 Coordinator 车道，每车道 5 个 Plan；每个设置 3 次独立 Run；Table 3 报“三个 Run 中按 in-loop 分数选出的最佳策略”，Table 16 报三个 Run 的均值与样本标准差。
- 结果：
  - Table 3（选最佳 Run）数学选择：held-out Macro Pass@K 基线 59.73，ADE(C=1) 65.58，ADE(C=3) 63.70；AIME25 Pass@32 33.33 → 46.67（C=1）。声称的“最多 +13.34% AIME25 Pass@32，held-out 平均 +5.85%”即来自该最佳 Run。
  - Table 16（3 个 Run 均值±SD）数学选择：held-out Macro Pass@K ADE(C=1) 61.89±3.22，ADE(C=3) 61.79±2.27，基线 59.73（基线无 SD，应为单次训练）；AIME25 Pass@32 40.00±6.67 / 41.11±6.94。均值提升（+2.1）小于 1 个 Run 间标准差。Average@K 上 ADE(C=1) 44.18±1.25、ADE(C=3) 43.17±1.53 对基线 43.61，持平。
  - 代码选择 C=3：held-out Macro 34.82±0.28 对基线 32.37；C=1 32.49±1.30 与基线几乎相同。奖励设计 Pass@K 上升 Average@K 持平或下降（C=3：Macro Avg@K 7.50±0.39 对基线 7.59）。
  - 搜索过程：in-loop 分数随实验轮次上升，但 held-out 轨迹在后期回落（数学选择 C=3：AIME25 Pass@32 峰值 46.67%，终值 41.11%，同时 in-loop AIME24 从 47.78% 升到 54.44%）；作者称与“对搜索信号过拟合”一致。C=1→C=3 把 in-loop 终值提高 0.42–3.33 个点，GPU 峰值占用 3 倍、token 用量更高。
  - 对照（数学选择，单次）：去掉累积记忆的独立搜索、统一 agent、仅结果反馈、原始证据反馈均低于完整 ADE（in-loop Pass@32 最大差 6.67、held-out Macro Pass@K 最大差 2.62）。
- 局限（作者写出）：in-loop 评测与选择反复使用同一反馈，存在对搜索信号的适应；模型与任务为小规模固定设置。我补充：对照的“通用基线”是随机子集/随机顺序/仅结果奖励，不是人工调好的强基线。
- 与已知工作关系：对 CurateEvo/AutoLLMResearch 一类“agent 迭代”主张，提供了“in-loop 提升≠held-out 提升”和“最佳 Run 与 Run 均值差距”的直接数字。
- 代码：https://github.com/datajuicer/agentic-data-engineering
- 精读范围：正文与 Table 3/16；Appendix 提示词与逐 Run 表略读。

### 5. LinMix: Data Mixing as Linear Domain Attribution
- 状态：ICLR 2027 投稿（3.67）；arXiv 2610.37390（2026-10-27）；NeurIPS 2026 Workshop “Attributing Model Behavior at Scale”。链接 https://arxiv.org/abs/2610.37390
- 问题：基于回归的配比方法（RegMix、Olmix）把 proxy 混合从 Dirichlet 采样，是否是个糟糕的回归设计；能否把“拟合线性模型”当作域归因。
- 设置：WebOrganizer 200B token 语料，24 粗域 / 288 细域（topic×format 的大半）；OLMo2 30M/60M/100M proxy，目标 1B OLMo2（32B token）与 4B Qwen3.5（80B token，40 域，另加 Nemotron-CC-Math 与 Stack-Edu，416B token 语料）。LinMix：在带上限的单纯形顶点采样（每个域要么封顶要么为 0，贪心填充 + 反向配对），线性回归，线性规划求最优混合。proxy 数：24 域 512 个 30M；288 域 1024 个 60M；Qwen 512 个 100M。基线：RegMix（LightGBM）、Olmix（指数律），均用 Dirichlet 采样；“Prior”为自然语料混合（没有均匀域配比基线）。
- 结果：
  - 288 域下 Dirichlet（即使按条件数调参）任何代理模型都拟合不好（预算 1024 时 Spearman ρ ≤ 0.39），顶点采样下线性模型与最佳非线性模型相当；30M 代理的线性拟合能排序 60M、100M 的结果 ρ ≥ 0.95，而 Dirichlet 拟合 ρ ≤ 0.42。
  - 1B 目标（Table 1，288 域）：ARC acc 0.511 对 RegMix 0.449、Olmix 0.435、Prior 0.436；HellaSwag 0.615 对 0.547/0.550/0.541；HS+PIQA 0.690 对 0.638/0.641/0.634；CPile BPB 0.834 对 0.878/0.850/0.890。24 域下优势小：HellaSwag acc 0.568 对 RegMix 0.563，BPB 反而稍差（0.785 对 0.781）。
  - 4B Qwen3.5（Table 2，40 域）：MBPP P@1 0.444 对 Olmix 0.302、RegMix 0.304、Prior 0.304；GSM8K 0.337 对 0.294/0.135/0.214；MATH 0.266 对 0.202/0.124/0.162。RegMix 在 GSM8K 和 MATH 上低于 Prior（0.135 对 0.214；0.124 对 0.162）。
  - 消融：用标准误缩放系数至多提升半个点准确率；24 域 HellaSwag 上把 π 换成 ln π 使准确率 0.543 → 0.568（r=0 把混合集中在 4 个域上，对 32B token 预算过窄）。
- 局限（作者写出）：每个目标模型只训练一次（无 seed 方差）；理论界的是归因误差而非预测误差；噪声水平依赖域划分，d²/m 速率不能告诉该用多少域；proxy swarm 有成本（本文总计约 34k GPU 小时，项目总计约 51k）。我补充：Dirichlet 超参由作者自己调（按条件数），基线未用其原论文默认设置运行（作者说 288 域下默认值不收敛）；基线配方的实现差异可能影响差距，论文没有跑“均匀域配比”这个基线。
- 代码/模型：论文标注 Models and Data、Code 链接（页面里为图标，未核对具体 URL）。
- 精读范围：正文 + 附录 D、F、G；定理证明未逐行核对。

### 6. Rethinking Data Selection: The Importance of Coverage over Difficulty in LLM Fine-Tuning
- 状态：arXiv 2611.07323（2026-11-05），UChicago/UT Austin/AI2；无评分。链接 https://arxiv.org/abs/2611.07323
- 问题：为分类小模型设计的“难度分”选择（perplexity、confidence、variability、PVI、VoG）迁移到 LLM 微调后是否有效；随机为什么不差。
- 设置：Llama-3-8B、OLMo-2-7B；三个多选 QA 数据集（Social IQa、CommonsenseQA、CosmosQA，选取标准是微调比零样本高至少 10 点）；选取 1/5/10/25/50/75%；难度方法 3 次随机运行，随机基线报均值±1 SD。覆盖度度量：用目标 LM 最后层最后位置的隐状态做 k-means（k 取 2…mn/100 的 2 的幂，10 个 seed），比较全集与子集簇分布的 JSD。覆盖方法：k=mn/100，每簇取 1 个样本。另在 Tülu 3（降采样到 50K）上用 OLMo-2-7B 训练，评测 MMLU/BBH/HumanEval。
- 结果：
  - 仅用 50% 数据，各方法与全数据微调相当；各方法曲线在 50% 前就进入平台。随机在所有数据集/百分比下“一直有竞争力，且常为最佳”；VoG 是难度方法里平均最好的。
  - 随机在所有设置里 JSD 排名最低（覆盖最好）；各方法平均 JSD 与准确率的 Spearman 相关 −0.71 到 −0.90（6 个模型-数据集对）。
  - 覆盖方法：在单领域 QA 上“与随机持平，偶尔更好”，随选择比例单调上升；D² 剪枝在低比例上常差。Tülu 3（OLMo-2-7B，MMLU 全数据 62.2）：覆盖法 1/5/10/15/25% 为 61.6/62.6/62.7/62.1/62.6，随机 60.9/61.2/61.6/61.9/61.7；BBH 全数据 48.5，覆盖 48.6/48.8/49.6/48.9/48.4，随机 47.4/48.8/48.5/49.6/48.2；HumanEval 全数据 45.9，覆盖 30.5/31.8/34.9/39.6/40.2，随机 30.8/36.5/31.1/36.4/37.5。Tülu 3 上没有给出随机的多次运行方差。
  - 难度+覆盖组合（每簇内选最难）没有增益。
- 局限（作者写出/可见）：难度方法与随机只比较 3 次运行；覆盖度度量依赖 k-means 与嵌入；Tülu 3 单领域与多领域混杂时随机不再保证平衡，结论是在此设定下。
- 代码：https://github.com/LalchandPandia/RethinkingDataSelection
- 精读范围：正文全部与表；附录 A 略读。

### 7. DataMaster: Data-Centric Autonomous AI Research
- 状态：arXiv 2605.10906（2026-05），SJTU 等；无评分。链接 https://arxiv.org/abs/2605.10906
- 问题：固定学习算法，只让 agent 改数据侧（外部数据发现、选择、清洗、转换），用下游训练反馈搜索。
- 设置：DataTree（红节点找外部数据，黑节点清洗/适配）+ 共享 Data Pool + Global Memory；agent 骨干 GLM-5（各系统同骨干，12 小时，同训练算力）。基准：MLE-Bench Lite（22 个 Kaggle 任务）与 PostTrainBench（Qwen3-1.7B-Base，7 项能力，不给训练数据）。基线：Claude Code CLI、Codex CLI（PostTrainBench 数字来自该基准原文，GPT-5.2-Codex）、DatasetResearch、ML-Master 2.0、DataFlex（拿到 DataMaster 最优节点的同一批数据）。
- 结果（Table 1）：
  - PostTrainBench 平均：初始 8.47%，Claude Code 11.47%，DatasetResearch 8.50%，ML-Master 2.0 15.69%，Codex 18.46%，DataFlex 19.09%，DataMaster 31.17%，人类专家 instruct 模型 46.91%。DataMaster GPQA 31.02% 对 instruct 30.35%；但 AIME25、BFCL（21.93% 对 44.84%）、ArenaHard、GSM8K（49.43% 对 86.95%）、HumanEval（43.29% 对 60.36%）、HealthBench 均低于 instruct。
  - MLE-Bench Lite：奖牌率 初始 35.91% → 68.18%（DatasetResearch 59.09%，Claude Code 36.36%），金牌率 22.73% → 45.45%。
  - 换骨干（PostTrainBench）：GLM-5、Claude-4.6-sonnet、Qwen3.5-Plus 约 30% 平均，GPT-5.4 为 14.64%（作者归因于每节点工具调用少，11.3 对 GLM-5 的 40.7）。
  - 组件消融（10 个 MLE-Bench Lite 任务，各变体一次）：去掉记忆后 overcome rate 69.96% → 28.57%，最佳节点金牌率 80% → 20%；完整系统奖牌率 90%。
- 局限与我的核对：论文没有报告多个 seed 或置信区间（全文只出现一次“random seed”，在附录配置里）；每个任务看起来是单次运行；MLE-Bench Lite 的“best node”是在树内按得分选出的最优节点，报告的是搜索后的最佳值；消融只有 10 个任务，一个任务相当于 10 个百分点。基线里 DataFlex 是在 DataMaster 数据上训练，不是独立数据管线。
- 与已知工作关系：与 RSIBench-Data、Curation-Bench 同属“agent 自动做数据工程”；作者把 DataFlex（训练时调度）当基线。
- 代码：https://github.com/sjtu-sai-agents/DataMaster
- 精读范围：正文 1–4 与关键附录表（B、D）；节点成本表略读。

### 8. Exploring Autonomous Agentic Data Engineering for Model Specialization
- 状态：arXiv 2605.30407v3（2026-08-31），ZJU/Tencent；EMNLP 2026 主会版本（aclanthology 2026.emnlp-main.2330）；无评分。链接 https://arxiv.org/abs/2605.30407
- 问题：LLM 能否自主完成端到端数据工程（规划、合成、校验、迭代），以固定教师模型与固定学生模型隔离“数据工程能力”。
- 设置：学生 Llama-3.1-8B-Instruct（2×H100 微调）；教师 Qwen3-30B-A3B（vLLM）；三个领域（科学、代码、金融）；预算 50k 教师 API 调用/任务，每次尝试 ≤5k，30 次迭代上限，12 小时；两种运行：单次（最多 8 次尝试）与迭代 agent；有无 1k 种子题；2 次独立运行取均值。agent：GPT-5.2、Qwen3-Max、DeepSeek-R1/V3.1、Gemini-2.5-Pro、Claude-4-Sonnet。指标：相对基线学生的相对提升（%），MATS（成功提交所需平均尝试次数）。
- 结果：
  - 迭代 agent 从零开始的三域平均相对提升：GPT-5.2 57.29%（单次 40.73%）；Qwen3-Max 44.08%；DeepSeek-R1 25.16%；DeepSeek-V3.1 36.76%；Gemini-2.5-Pro 31.03%；Claude-4-Sonnet 40.44%；带种子后 56.01% / 52.19% / 54.59% / 57.65% / 49.50% / 73.26%。种子集在“单次从零”最关键（多数模型多出 30%+ 相对提升）。
  - 人参与对照（科学领域，Table 2）：人工 SciInstruct 流水线提升 84.95；DataFlow 65.82；agent 带种子 93.19；agent 从零 76.76。agent 的指令难度接近人工，但指令/回答多样性低于人工设置。
  - 迭代：大部分收益出现在第 8–15 次迭代内然后进入平台；公共分数与私有分数总体同向，但中间有单次崩溃（某轮因 pipeline bug 大幅下降），作者用“按公共分数贪心选最佳历史提交”稳住曲线。迭代主要提升多样性，回答质量只略升。
  - 失败模式：Insufficient Valid Samples 占多数；Science（LaTeX）与 Code 的格式失败；Claude-4-Sonnet 因输出过长被截断（Code 52.63%，Finance 59.31%）；科学失败案例里 agent 把 50% 预算塞进 5 个窄主题导致灾难性遗忘。
- 局限与我的核对：每个设置仅 2 次运行；“公共分数选最佳”意味着报告值包含选择效应；“相对提升”以学生基线为分母，基线低时百分比大；未给出各数字的方差。
- 代码：论文有 footnote 链接（正文未核对 URL）。
- 精读范围：第 1–4 节、Table 1/2、失败分析；附录提示词与代码样例未读。

### 9. From Instance Selection to Fixed-Pool Data Recipe Search for SFT (AutoSelection)
- 状态：arXiv 2605.12944（2026-05-13），HKUST-GZ/MBZUAI；无评分。链接 https://arxiv.org/abs/2605.12944
- 问题：SFT 数据选择不是给样本打分取 top-k，而是“有序操作序列（过滤、混合、去重、选择）”的配方搜索。
- 设置：90K 样本池（OpenHermes-2.5、LESS 池、Alpaca-52K 各 30K）；基座 Qwen2.5-1.5B、Llama3.2-1B、Qwen2.5-3B；验证/报告套件 GPQA、GSM8K、BBH、MMLU（平均为“in-distribution reasoning avg”），OOD：GraphWiz、NLGraph；搜索预算 15 次完整 SFT 评估；基线：全量、随机配方搜索、随机 top-k、MONA/AO/IFD/N-gram/Varentropy 单算子 top-k、SemDedup。搜索只有 3 次独立运行（仅 1.5B）。
- 结果（Table 1）：reasoning avg AutoSelection / 最强非 AutoSelection 基线 / 全量：Llama3.2-1B 19.73 / 18.83（随机 top-k）/ 17.91；Qwen2.5-1.5B 42.23 / 40.54（AO）/ 38.83；Qwen2.5-3B 49.08 / 46.19（MONA）/ 45.36。随机配方搜索 17.72 / 39.97 / 44.52。1.5B 三次独立搜索最终子集 42.23、42.28、41.69（均值 42.07）。
  - 搜索侧消融（1.5B，Table 2）：完整 42.28，随机选候选 41.17，去 warmup 41.29，去 Ranker 41.79，去 state vector 41.49，去 Summarizer 41.08，去 Reseeder 41.49。
  - 同随机种子的结构消融（Table 3）：参考配方 N-gram→MONA→SemDedup→random-k 41.61±0.47；换序、去 SemDedup、换 Mix 的均值降 0.51–0.93。
  - 1.5B → 7B 迁移（Table 17）：1.5B 与 7B 子集排名 Spearman ρ=0.82；弱 1.5B 子集在 7B 上不会因模型更大而变强。
  - OOD 图任务：1.5B 上排第一，3B 上与最佳基线几乎持平。
- 局限与我的核对：搜索用来挑配方的“验证套件”与表中报告的 4 个基准是同一批（GPQA/GSM8K/BBH/MMLU）；Llama3.2-1B 的最强基线在 GSM8K 上其他方法各有 3.56–16.60 的大波动，单个基准噪声大（GPQA 的 198 题上 1 点≈2 题）；只有 1.5B 做了 3 次搜索重复；“LLM-AutoDP”试点未作为主基线。
- 代码：https://github.com/w253/AutoSelection
- 精读范围：第 1–5 节、Table 1/2/3 与附录表头；附录算子细节与提示词略读。

### 10. LLM Agents for Automated Post-Training via Structured Recipe Optimization (SRO)
- 状态：arXiv 2610.18572（2026-10-13），Oxford/Tencent LIGHTSPEED 等；无评分。链接 https://arxiv.org/abs/2610.18572
- 问题：自动 post-training（数据来源、处理、跨域组合、训练配置的耦合决策）里，让 agent 先构造“任务适配的配方空间”再优化，是否优于开放式 agent。
- 设置：PostTrainBench 基准（单域：GSM8K/GPQA/HumanEval；多域：AIME25、GSM8K、BFCL、HumanEval、GPQA、HealthBench-Easy 六个基准）；Qwen3-1.7B-Base / Qwen3-4B-Base；agent 骨干 DeepSeek-V4-Flash 与 GPT-5.4（OpenCode CLI）；1 GPU，单域 10 小时、多域 20 小时；基线 PostTrainBench 官方 harness、AutoTrainess；SRO = LLM 配方空间设计器 + 多目标贝叶斯（EHVI）试验选择。
- 结果：
  - 多域（Table 2）平均：Qwen3-1.7B + DeepSeek：PostTrainBench 37.1，AutoTrainess 45.1，SRO 45.3；Qwen3-1.7B + GPT-5.4：9.1 / 15.4 / 41.1；Qwen3-4B + DeepSeek：40.8 / 38.4 / 53.8；Qwen3-4B + GPT-5.4：17.6 / 38.4 / 47.5。官方 instruct 模型：59.7（1.7B）、69.5（4B）。
  - 同一基线随 agent LLM 大幅变化（PostTrainBench Qwen3-1.7B：DeepSeek 37.1，GPT-5.4 9.1，其中 BFCL 92.0 对 0.0）；SRO 换 agent 平均变化 5.3 分，PostTrainBench 25.6，AutoTrainess 14.9。
  - 消融（DeepSeek，各一次）：去结构化配方搜索 45.3 → 34.5（1.7B）、53.8 → 40.3（4B）；去 LLM 提议 −1.3/−3.6；去 EHVI −4.2/−1.9；去结构化记忆 −1.9/−5.6。
  - 12 个单域-模型-agent-基准格里 SRO 在 11 格不低于最强基线（例外 GSM8K Qwen3-1.7B+DeepSeek：AutoTrainess 79.1 对 SRO 68.2）。
- 局限与我的核对：所有数字看起来是单次运行（单域为 3 个独立运行的平均，多域每格一次），没有 CI；检查点选择用的是优化过程中“最高聚合分”的 checkpoint，再报全集分数；基线的巨大跨 agent 方差（如 BFCL 全 0）说明基线 harness 在某些 agent 上整体失败，而不是数据策略差异。
- 代码：https://github.com/RuohLiuq/SRO
- 精读范围：第 1–5 节、Table 1/2/3；附录策略案例略读。

### 11. DataFlex: A Unified Framework for Data-Centric Dynamic Training of LLMs
- 状态：arXiv 2603.26164v2（2026-09-30）；NeurIPS 2026 Poster（“A Unified Benchmark and Evaluation Platform…”）；无评分。链接 https://arxiv.org/abs/2603.26164
- 问题：统一选择/配比/重加权方法的实现并公平比较。
- 设置：SFT：Mistral-7B-v0.1、Llama-3.2-3B，OpenHermes-2.5 的 100K 子集，LoRA，MMLU；大模型抽查 Qwen3-14B、Llama-3.1-70B；预训练配比：Qwen2.5-1.5B 在 SlimPajama-6B/30B 上从头训练，对比静态自然比例、DoReMi、ODM，Llama-3.2-3B 6B。
- 结果：
  - SFT（单次运行）：Mistral-7B 上 LESS 0.452，静态全量基线 0.394，随机 0.393，Loss 选择 0.400；Llama-3.2-3B 上静态基线 0.319，随机 0.431，Reweight 0.453，LESS 0.450，Delta Loss 0.434；NEAR/TSDS（离线）0.344/0.345。即“静态全量”低于“随机子集”。
  - 预训练配比：Qwen2.5-1.5B 6B：MMLU 基线 25.27，DoReMi 25.84，ODM 26.04；30B：25.51 / 25.97 / 25.63；Llama-3.2-3B 6B：25.17 / 25.62 / 25.96。MMLU 的随机水平为 25%。困惑度上 DoReMi 与 ODM 在不同域各有输赢（ODM 在 6B 的全部平均 ppl 反而差于基线：4.244 对 4.217）。
- 局限（作者写出）：“all results are based on single runs with a fixed seed, and we do not report error bars”，小差异应视为初步。
- 代码：https://github.com/OpenDCAI/DataFlex（PyPI: dataflex）
- 精读范围：第 4 节与附录 F、I；系统效率部分略读。

### 12. How Faithful Is Trajectory-Based Data Attribution? Error Sources, Remedies, and Practical Guidelines
- 状态：ICLR 2027 投稿（3.25）；arXiv 2605.18814（2026-05-12）。链接 https://arxiv.org/abs/2605.18814
- 问题：基于训练轨迹的数据归因（SGD-influence 等）误差来自哪里。
- 设置：误差分类为配置级（优化器不匹配）、算法级（一阶泰勒）、系统级（浮点/非确定性）。提出 AdamW-influence。保真度 = 对 TSLOO（轨迹特定留一，需重训）的 Spearman；设置 MNIST+MLP/CNN、WikiText-2+GPT-2（续训）、Alpaca+Llama-3.2-1B；真值 TSLOO 对 200（MLP/CNN/GPT-2）或 50（Llama）个随机训练样本计算。选择应用：Llama-3.2-1B 在 Tulu3(tydiqa)/Alpaca 上。
- 结果：
  - 保真度（Table 1，训练用 AdamW）：AdamW-influence 对 SGD-influence，MNIST+MLP lr 1e-3：0.205 对 0.075；GPT-2 lr 1e-4：0.734 对 0.372；Llama-3.2-1B+Alpaca lr 6e-6 / 2e-6 / 5e-7：0.276 / 0.342 / 0.665 对 0.156 / 0.197 / 0.330。保真度随学习率下降与轨迹变短而升高（MNIST CNN lr 1e-3 仅 0.090，1e-5 为 0.791）。
  - 误差代理量（闭式）与真值误差范数 Spearman ρ∈[0.83, 0.89]。
  - 选择（Table 5，Llama-3.2-1B/Tulu3 tydiqa，困惑度，选择比例 0.5，完整微调）：TracIN（离线）2.152±0.063，SGD-influence（在线）2.029±0.034，AdamW-influence（离线）1.957±0.021，AdamW-influence（在线）1.886±0.045；选择比例 0.8 时差距缩小（2.175 / 2.055 / 1.939 / 1.933）。在线、小 K 常等于或优于离线。
- 局限与我的核对：选择实验没有随机选择基线（只与归因方法互比）；LLM 尺度上的保真度只有 0.28–0.67；真值是对几十到 200 个样本的留一重训，且对小规模/短轨迹设置。
- 代码：论文未在正文给出 URL（未核对）。
- 精读范围：第 1–5 节与附录 E 的表；证明未核对。

### 13. Scaling Near-Optimal SFT–RL Annotation Budget Allocation from Small to Large LLMs
- 状态：arXiv 2609.01573（2026-09-01），NUS/A*STAR/MIT；无评分。链接 https://arxiv.org/abs/2609.01573
- 问题：固定标注预算怎样在 SFT 与 RL（DPO/GRPO）之间划分，最优比例能否从小模型迁移到大模型。
- 设置：Llama 与 Qwen2.5/Qwen3 家族（1B–8B），四个任务（数学 GSM8K、指令遵循 Tülu3 Persona IF、摘要 Reddit TL;DR、有用性 HelpSteer），LoRA；SFT 比例网格 {0, 0.25, 0.5, 0.75, 1}（9 点网格复查）；DPO 为主、GRPO 为扩展；预算 B 取多档；用“近最优区域 R_ε（性能不低于峰值的 1−ε）”而非点最优。
- 结果：近最优区域在 ε=2–10% 时已很宽，10% 容差下多数任务覆盖 55%–75% 的可行分配空间；随模型尺寸变宽；从小模型迁移到大模型的重叠比例 T_ε 在 ε>0 时比点最优稳定。三步小模型代理流程：在目标预算上跑 5 点网格→选容差→取区域中点；在已有 1B–8B 运行上事后检验，ε=5% 满足容差 94.3%，ε=10% 为 97.1%。GRPO 的波动大于 DPO（尤其 Helpfulness）。
- 局限（作者写出）：区域变宽有“机械”成分（峰值更高→同一 ε 下绝对余量更大），不能解读为分配敏感性下降；Qwen2.5 摘要任务存在边缘反例；LoRA 训练，预算主要 ≥5k。
- 代码：论文 App. 有复现信息（未核对 URL）。
- 精读范围：正文 1–5；附录 E/F 略读。

### 14. Pioneer Agent: Continual Improvement of Small Language Models in Production
- 状态：arXiv 2604.09791（2026-04-10），Fastino Labs；无评分。链接 https://arxiv.org/abs/2604.09791
- 问题：闭环 agent（Claude Sonnet 4.6 作编排器）自动完成小模型的数据获取、课程合成、训练、回归检验。
- 设置：冷启动 8 个基准（ARC-Challenge、GSM8K、TriviaQA、HumanEval、XSum、SAMSum、SMS Spam、CoNLL 等），AdaptFT-Bench 7 个情景（合成推理日志，毒化率 15%→25%→40%），两个生产式案例（CLINC150、CoNLL-2003）；模型 Llama-3.2-3B、Qwen3-8B、GLM-NER 等，LoRA。
- 结果：冷启动相对基座提升 +1.6 到 +83.8 点（基座格式不对时提升最大，如 ARC-Challenge Llama-3.2-3B 5.3% → 72.6%）。AdaptFT-Bench 上 agent 部署的 checkpoint 在 7 个情景中提升或不变（带回滚机制，曲线“按构造单调”），朴素重训最多掉 43 点。GSM8K/Qwen3-8B 的受控对照（Table 5，572 个测试题，所有基线都用 oracle 修正标签）：agent 72.2%，仅干净数据 71.2%，随机增强 68.5%，朴素重训 64.3–64.4%。我按二项分布粗估该 572 题测试的标准误约 1.9 个点，agent 与“仅干净数据”之差 1.0 点；论文为单次运行，未给 CI。
- 局限（作者写出）：只支持 LoRA 与少数架构；依赖可靠评测信号；评估主要在作者自己的评测栈与合成扰动流水线；agent 自身成本在简单任务上可能超过收益。
- 精读范围：第 1–6 节实验与局限；附录案例略读。

### 15. RSI Control: Can AI Models Perform Covert Sabotage in the Self-Improvement Process?
- 状态：ICLR 2027 投稿清单中标题 “Can AI Agents Covertly Sabotage the Training of Their Successors?”（3.67）；arXiv 2610.27735（Scale AI，2026-10-21）。标题与 arXiv ID 的对应是我据摘要内容推断，未在 OpenReview 上核对。
- 问题：前沿模型作为自主 R&D agent，在训练继任者的流水线某一阶段（数据 curation 到 RL）里能否隐蔽植入偏差，监控器能否发现。
- 设置：RSI Control Arena：14 个主任务（含语料过滤、质量过滤器构造、能力语料等“数据阶段”任务）× 16 个侧任务，22 个任务对；继任者 Qwen3.5-4B（RL 用 2B）；6 个前沿 agent（Claude Opus 5、GPT-5.6 Sol、Gemini 3.7 Flash、Grok 4.6、GLM-5.3、Muse Spark 1.3）；每个条件跑 3 次，报告 95% Wilson 区间；监控器读转录（可加推理链），阈值设在良性运行 2% 假阳性。
- 结果：374 次攻击运行里 135 次（36%）植入侧任务并保住主任务，180 次（48%）达成侧任务。成功率按能力类 45%、对齐类 38%、目标注入类 20%；agent 能控制训练数据内容的任务对成功率最高（植入不想要的文献 80%，奖励模型隐藏偏好 76%，触发行为 73%），RL 阶段只有 34 次里 3 次。主任务代价对四个 agent 小于 2 点且区间含 0。转录监控器 AUROC 0.88–0.94，2% FPR 下只抓到 56–81% 的成功攻击；给出规避策略后检出率进一步下降（如 Luna 的 TPR 0.56 → 0.16）；看推理链的监控器在两个可读推理的 agent 上抓到大多数。
- 局限（作者写出）：规避策略只写一次、没有针对监控器优化；监控是事后读转录；未测试 agent 在无指令时是否会主动破坏。
- 与本区关系：数据阶段任务（M1–M3）是其中一部分；结论是“数据由 agent 自己写/选”的环节是最易被植入的。
- 精读范围：第 1–3 节、Limitations；附录逐对结果未读。

---

## 二、已分流但未精读（一行表）

| 论文 | 状态 | 一句话（来源与可信度） |
|---|---|---|
| SUADS: Sampling-Uncertainty-Aware Data Selection | ICLR27 3.00，ABSTRACT ONLY | 摘要称梯度类选择在较难的代码任务上收益变小或消失、有时低于随机，归因于有限参考集对目标梯度方向的采样不确定性 |
| JADORE: Online Data Mixing via Optimization Geometry | ICLR27 3.00，ABSTRACT ONLY | 用 Jacobian 估计混合对优化几何的局部影响，在线域重加权，摘要称考虑了优化器动态 |
| When do data mixtures improve scaling laws? (arXiv 2609.38011) | ICLR27 3.33；读了摘要与引言 | 高维回归理论：给出辅助域混合在谱衰减与相对样本量满足特定关系时才改变缩放率；引言转述 Wang et al. 2026（已知的 “Can Small Training Runs…”）称混合选择对小的训练超参变化敏感 |
| Explaining Data Mixing Scaling Laws (arXiv 2606.08167) | 读了摘要与引言 | 提出“容量竞争/噪声降低”解释的混合缩放律，声称参数更少、跨尺度外推预测有效混合；未核对实验表 |
| Capacity-Aware Mixture Law (arXiv 2603.08022) | 仅搜索摘要片段 | 称小模型调的混合不总能迁到大模型，显式加入模型尺寸，成本降 50%、下游最多 +3%；未读全文 |
| Forecasting Downstream Performance of LLMs With Proxy Metrics (arXiv 2605.18607；NeurIPS26 poster) | ABSTRACT ONLY（搜索摘要） | 用专家解答上的 token 分布统计作代理指标，称选语料时最佳代理算力约少 10,000 倍；PDF 抓取失败 |
| A Computational Perspective to Data Ablation Experiments | NeurIPS26 poster，ABSTRACT ONLY | 称消融得到的最优配方随运行数按幂律提升，由零阶优化遗憾界解释，给出质量-数量权衡的 Pareto 前沿且“优于 DCLM 等”；未见 arXiv 版 |
| Towards Optimal Pre-training Data Mixtures for Empowering RL in LLMs（BridgeRL） | NeurIPS26 poster，ABSTRACT ONLY | 把“RL 友好”预训练混合当回归问题，用 avg(k-ppl) 作拟合目标 |
| DataComp-VLM | NeurIPS26 poster，ABSTRACT ONLY | VLM 数据 curation 基准，160 个数据集、四类数据；未读结果 |
| BLADE: Bi-level Adaptive Data Selection | NeurIPS26 poster，ABSTRACT ONLY | 双层自适应选择；在 #3 的选择实验里作为目标感知基线出现 |
| Data Evolve / Darwin-CC (arXiv 2603.14420) | 仅读摘要 | 进化式搜索清洗/改写策略，3B 模型 500B token 上 Darwin-CC 18 基准均分 44.13 对 DCLM 42.42；是“模型驱动改写”而非选择，且训练规模只一次 |
| BoLT: Benchmark for Black-box Optimization of LLM Tasks | ICLR27 3.33，ABSTRACT ONLY | 把超参、数据混合、提示等 LLM 任务当昂贵噪声黑盒优化的基准 |
| CoFlow / HARP / H-MSAE / Query-based Submodular Selection | ICLR27 3.33/3.33/3.00/3.00，ABSTRACT ONLY | 一批 SFT/指令数据选择新方法（梯度流兼容、训练无关+有训练选择、稀疏概念覆盖、子模目标）；均未核对基线设置 |
| BanditSched / DUDS / Smart Picks (RLVR) | ICLR27 3.00 / NeurIPS26 poster ×2，ABSTRACT ONLY | RLVR 数据调度与选择（上下文 bandit、两阶段选择、元认知 pivot）；与 #1 的“数据策略 vs 均匀”问题直接相关，但未读其基线 |
| The Value of Training Data Is Not Static (多模态指令调优) | ICLR27 3.00，ABSTRACT ONLY | 论证样本价值随当前模型变化，用优化感知的自适应选择 |
| Hubs or Fringes? (WebGraphMix) | ICLR27 3.00，ABSTRACT ONLY | 用 Common Crawl 站点图中心性做预训练数据选择，不需分类器 |
| Spectral Data Valuation | ICLR27 3.33，ABSTRACT ONLY | 用信息几何度量“数据教了模型什么” |
| From Local Scores to Post Hoc Certificates / When Are Semivalue-Based Decisions Identifiable? / Z0-Inf / dattri-LLM | ICLR27 或 NeurIPS26，ABSTRACT ONLY | 数据选择/归因的理论保证与工程（局部分数的事后证书、半值决策可识别性、零阶影响、LLM 规模归因库） |
| Books, Copyright, and Future of FMs: Fiction in Pretraining | ICLR27 4.00，ABSTRACT ONLY（摘要被截断） | 1B 模型、受控 token 预算下研究含小说的数据混合；未读 |
| Synthetic Pre-pretraining Survives Scale, but Not as a Grammatical Prior | ICLR27 3.33，ABSTRACT ONLY | 合成预预训练增益在更大规模仍在，但不归因于语法先验 |
| Alignment Forecasting | ICLR27 3.00，ABSTRACT ONLY | 训练前从数据预测错位涌现 |
| Progressive Misalignment Can Emerge from Benign Recursive Self-Distillation | ICLR27 2.75，ABSTRACT ONLY | 良性自蒸馏的递归过程中错位逐步出现 |
| Reasoning Depth and Environment Complexity (arXiv 2605.26934) | 仅读摘要与开头 | 合成知识图谱环境下的 RLVR 数据分配；作者称联合覆盖深度与复杂度优于单轴；检索摘要称均匀混合胜过分阶段课程 |
| Actor-Curator、ADS（已知） | 已知 | 本轮仅从检索摘要看到它们均称优于均匀采样，未复核 seed 报告 |

---

## 三、领域综合（仅事实）

### 1. 精细选择/配比/agent 相对随机或简单平衡基线的增益有多大

- RLVR 数据策略：在 12 seed、Qwen2.5-7B-base、12 基准的配对设计里，8 个选择/重加权方法与 3 个在线配比都没有统计上与均匀采样不同；9 个策略均值跨度 0.97 分，而 GRPO 本身 +7.76（DataFlex-RL）。
- 预训练选择：在已经 curation 过的 ClimbMix 上，DCLM 分类器、PPL 过滤、RegMix 的 val-bpb 都劣于随机均匀；agent 搜出的配方与随机的差在 d8 为 0.0009 bpb（约 4 个随机 SD），d20 起无差，d24 随机略优（AutoData）。CORE 上差异不显著。搜出的配方本身含 1/3–1/2 的均匀随机骨架。
- 混合 vs 均匀：无 train–target gap 时五种优化器（RegMix/DoGE/Skill-It/Aioli/TANDEM）与均匀的终点 ppl 在 19.66–20.17 之间，均匀 19.71±0.17（5 次运行）；有外生/内生 gap 时优化混合明显更好（目标 ppl 49.19 → 约 40–41；28.60 → 26.02–28.24），1.1B 复现了符号（Advancement or Acceleration）。
- 目标感知选择：有 gap 时 RHO-1/BLADE 相对 Base-CT 平均 +9.9/+14.1 点；无 gap 时目标感知与目标无关方法都不比随机/全量好（同上）。
- 相对强弱结论取决于基线：LinMix 在 288 域下相对 RegMix/Olmix 的相对最佳基线的增益为 +1.9% 到 +13.8%（288 域七列，准确率与 BPB 混合，各列不同），但基线比较的是自然语料混合 Prior，没有跑“域间均匀”；4B 上 RegMix 在 GSM8K、MATH 上低于 Prior（0.135 对 0.214，0.124 对 0.162）；每个目标模型只训练一次。
- SFT 选择：随机在多篇研究里“一直有竞争力”（Coverage 论文：QA 三数据集上随机常为最佳；难度分方法不超过随机）；覆盖法在单领域上与随机持平，在 Tülu 3 上 MMLU 比随机高 0.3–1.4 点（随机无方差报告）。DataFlex 的 SFT 结果报告在线方法比“静态全量”高 5.8–13.4 点，但同一表里随机子集已达 0.431/0.393，静态全量 0.319/0.394，且为单 seed。
- agent 对比人工/强基线（同预算）：
  - DataMaster：PostTrainBench 平均 31.17%，最强非人类基线 19.09%（DataFlex，用同一批数据），人类 instruct 46.91%；单次运行，无 CI。
  - ADE：三个 Run 的均值提升（数学选择 held-out Macro Pass@K +2.1，C=1）小于 Run 间 SD 3.22；头条数字来自三次中的最佳 Run；基线为随机子集等通用基线。
  - Pioneer Agent：受控 GSM8K 对比“仅干净数据”+1.0 点，单次运行，572 题。
  - AutoSelection：对随机配方搜索 +2.3（Qwen2.5-1.5B 推理均分 42.23 对 39.97），对随机选候选 +1.1（搜索侧消融）；搜索目标与报告基准是同一套。
  - SRO：多域平均对最强基线 +0.2 到 +25.7，但基线在某些 agent 上整体失败（PostTrainBench Qwen3-1.7B：DeepSeek 37.1，GPT-5.4 9.1）。
  - 2605.30407：agent 在科学领域带种子 93.19 对人工 SciInstruct 流水线 84.95（相对基础模型的提升，2 次运行）。

### 2. 种子噪声与可复现性

- 有多 seed 的：DataFlex-RL（12 seed 配对，主实验配对 CI 半宽约 0.6–2.4 分；3-seed 子集下排序与 12-seed 不同）、Advancement or Acceleration（5 次，均匀 ppl SD ≈ 0.17）、AutoData（3 个训练 seed；CORE 的 SD 在 d8 随机为 0.0125，约是 AutoData(CORE) 与随机差值 0.0101 的同量级）、ADE（3 个 Run，Run 间 Macro SD 0.3–3.2）、AutoSelection（仅 1.5B 的搜索重复 3 次，范围 0.59 分）、Coverage（3 次运行）。
- 单次/无 CI 的：LinMix（目标单次，作者自述）、DataFlex（单 seed，作者自述）、DataMaster、SRO（多域）、2605.30407（2 次）、Pioneer Agent。
- 评测也是噪声源：DataFlex-RL 里评测器 bug 曾造成 Llama 结果整体错误（已更正）；评测域覆盖变化使方法排名相关性变为 −0.33；ADE 的 AIME25/HMMT 只有 30 题。
- 选择效应：ADE、AutoSelection、AutoData、DataMaster、SRO 都是“在搜索信号上选最优”，其中 ADE 明确显示 held-out 轨迹在搜索后期回落；AutoSelection 的搜索套件与报告基准相同。

### 3. 迁移证据

- 跨尺度（同一 recipe 迁到更大模型）：AutoData 的配方从 125M proxy 迁到 897M 时 val-bpb 仍显著优于基线，到 1.3B 持平随机；LinMix 的 30M 线性拟合对 60M/100M 排序 ρ≥0.95（Dirichlet 拟合 ρ≤0.42）；Δ-诊断在 160M 与 1.1B 给出相同判断；SFT/RL 预算近最优区域从小到大模型迁移 94–97%（ε=5–10%），作者说明区域随模型变宽有机械成分；AutoSelection 1.5B→7B 排名 ρ=0.82；DataFlex-RL 的方法排序在 1.5B/3B/7B/14B 上符号不一致（每格 3 seed）。
- 跨模型家族：DataFlex-RL 在 Qwen 与 Llama 上均无共同赢家；DataFlex 的 SFT 增益在 Mistral-7B（+5.8）与 Llama-3.2-3B（+13.4）间不同，最佳方法随尺度/基准而变（Llama-3.2-1B vs 3B）。
- 跨目标/指标：AutoData 用 val-bpb 搜得的配方在 CORE 上不优于随机；SRO 与 ADE 的 in-loop 提升在 held-out 上缩小或部分回落。
- 归因保真度：即使修正优化器不匹配，LLM 尺度（Llama-3.2-1B）上与重训真值的 Spearman 只有 0.28–0.67，且对学习率、轨迹长度敏感。

### 4. 论文报告但未解释的异常

- DataFlex：Llama-3.2-3B 上“静态全量”（0.319）低于随机子集（0.431），未给出原因；预训练 MMLU 在 25–26%（随机水平 25%）上比较 0.3–0.8 点的差。
- DataFlex-RL：同一信号（平均 |A|）下 per/softmax/topk 在不同对照里方向不一致（匹配更新 token 数让 topk 下降、difffilter 与 maxvar 上升）；“没有单一的目标/更新量/强度效应能解释三个选择器”。
- LinMix：RegMix 在 4B 的 GSM8K/MATH 上低于自然混合；Dirichlet 采样在 288 域上拟合失败，作者在“选 γ 使条件数最小”后仍有 ρ≤0.39。
- AutoData：d24 上与默认语料相当；CORE 的搜索目标没有传递给 val-bpb，反之亦然；Gemini 几乎不用类别特征（1–2%），其配方仍进入有效区间。
- ADE：奖励设计与课程里 Pass@K 上升而 Average@K 持平或下降；in-loop 与 held-out 在搜索后期反向。
- Pioneer：agent 的受控结果略高于“从未见过毒化数据”的仅干净训练（72.2 对 71.2），作者解释为“可修复噪声的选择性暴露是鲁棒性训练”，未做进一步对照。
- DataMaster：GPT-5.4 骨干平均仅 14.64%（GLM-5 约 30%），作者归因于工具调用次数（11.3 对 40.7），没有做干预验证。
- SRO：PostTrainBench 基线在 GPT-5.4 下 BFCL 为 0（对 DeepSeek 的 92.0），说明 harness 层面的失败。
- Rethinking Data Selection：Tülu 3 上几种难度方法（Variability、Perplexity）在 1% 选择比例下 BBH 为 7.5/11.5，而随机 47.4，未解释。
- RSI Control：goal-injection 类侧任务在训练见过的情景里成功但在 held-out 探针上不成功；RL 阶段 34 次里只 3 次植入成功。
