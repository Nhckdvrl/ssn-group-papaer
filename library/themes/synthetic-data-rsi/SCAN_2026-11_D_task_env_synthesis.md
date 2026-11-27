# SCAN 2026-11 · 方向 D：RL / Agent 的任务与环境合成

扫描日期 2026-11-27。范围：ICLR 2027 投稿（OpenReview，评分 1–4）、NeurIPS 2026 接收、arXiv 约 2026-05 至 2026-11。
已知不重读：AZR、SQLM、SOAR、SGS、ASP、DataEnvGym、S3Gym、ADS、PAC、Self-Play Pretraining (2609.30063)、Reasoning Gym 系列。

**阅读方式与可信度说明**
- 下面 12 篇"精读"均来自 arXiv PDF 的全文文本（pdftotext），读了摘要、方法、全部正文实验与表格、局限；附录只读了与关键数字有关的部分（各篇附录的提示词、超参、逐任务表基本未逐行读）。
- OpenReview 页面与 PDF 被站点验证页拦截，ICLR 2027 投稿（Multi-Agent World、MetaExp、SWE-Craft、DataPraxis、Skill2Env、WildAWM、CompassPlay 等）**拿不到全文，只有候选清单里的摘要片段**，一律标 ABSTRACT ONLY，不据此下结论。
- 数字全部取自各论文自报；"基线"是论文自己选的基线。

---

## 一、精读论文

### 1. Recursive Environment Scaling (RES) for General Long-Horizon Agents
- arXiv 2610.16397（2026-10-19 v2），预印本，未见投稿状态。https://arxiv.org/abs/2610.16397 　代码 github.com/Glimmerxx/recursive-environment-scaling
- **问题**：能否在保持任务目标/完成条件不变的前提下，递归地把已有 benchmark 环境变难，并且用这些环境收集的轨迹训练 agent？
- **设置**：proposer = GPT-5.6 Sol（high effort），scaling 阶段的目标 agent = DeepSeek-V4.1-Flash；对环境做三类程序化变换（信息访问路径、资源关系、操作依赖），执行式验证（独立重放变换、在新会话里按公开接口恢复内容并和源事实对比）通过才被接受，被接受的子环境成为下一轮父环境；最多 10 次变换。基准：Claw-Eval-Live(105)、Workspace-Bench-Lite(100)、Terminal-Bench 2.1(89)，共 294 个初始任务。评测模型 6 个前沿模型（单次 50 轮）。训练：Qwen3.5-4B/9B-Base、35B-A3B-Base，SFT，8,428 条轨迹，1 epoch，4×H800，学习率 2e-5/1e-5/5e-6，单种子（seed 42）。
- **结果**：
  - 难度：6 个模型在 18 个模型×基准比较里全部下降。Claw-Eval-Live 上 DeepSeek-V4.1-Flash 82.86→5.71，Claude Opus 5 86.67→28.57；Workspace-Bench-Lite 的 TCR@80 下降 12–19 点；Terminal-Bench 2.1 下降 41.6–47.2 点。
  - 训练：同样 8,428 条、同样优化设置，"在 RES 环境里收集的轨迹 SFT"在 9 个模型×基准对比全部优于"原 ClawGym 轨迹 SFT"，提升 7.00–14.61 点。例：Qwen3.5-35B-A3B 上 Claw Pass@1 64.76→77.14，Workspace TCR@80 14→28，Terminal-Bench 23.60→38.20；4B 的 Terminal-Bench 5.62→13.48。基座本身 4B=2.25、9B=10.11、35B=13.48（Terminal-Bench）。
  - 消融（Claw-Eval-Live，15 任务，DeepSeek-V4.1-Flash 做目标）：去掉依赖组合 Pass@1 0→100；去掉递归继承（同样次数的独立增强）6.7→93.3；只保留 6 种基础算子 6.7→80.0；最大递归深度 0/1/2/3/5/10 → Pass@1 82.86/60.0/17.14/7.62/3.81/4.76。深度 10 的历史均值：轮数 3.55→43.2，工具调用 8.05→206.0，触顶 50 轮的比例 75.1%。
  - 成本：105 个种子产生 289 个被接受的子环境，92% 至多 2 次 proposer 执行，平均每个子环境 89.2k token。
- **局限/保留**：作者说"难度"主要来自加长访问路径与前置依赖（案例：3 次读文件变成 171 次工具调用，目标不变）；论文没有用人或独立验证者检查"变难后任务是否仍同等可解"，只靠自己的执行式重放。训练对比里 RES 轨迹由 DeepSeek 在加难环境里收集、"沿用相同选择规则"，主文没有报告 RES 轨迹集的 token 数/长度（原轨迹集 190.5M 输入 token、39.7M 监督 token），也没有按 token 配平。训练对比只有一个种子、一次运行。评测也在三个与训练环境同源的 agent 基准上。
- **代码/数据**：代码已给链接，ClawGym 任务与轨迹为公开版本。

### 2. Scaling Laws for Tool-Use Agents via Controllable Environment Synthesis (SynthAPI)
- arXiv 2610.37648（2026-10-27），Apple，预印本。https://arxiv.org/abs/2610.37648
- **问题**：在合成的工具使用环境里，固定预算该怎么分配给"新工具/新任务/新数据库状态/数据复杂度"，才能最大化对自然 benchmark 的泛化？能否拟合可外推的定律？
- **设置**：Gemini-3.1 Pro 作 builder，生成 64 个 app（10,472 个 API，其中写 API 6,266），任务 458,752 个，带 Python 验证器和 oracle 求解器（过滤条件：初始状态验证失败且 oracle 执行后验证通过）。控制变量：A=app 数，T=每 app 任务数，S=每条指令的数据库实例数，D=干扰数据批数。专家轨迹用 GLM-5.2（每题最多 4 次，取第一次验证通过的），Qwen3.5 的 2B/4B/9B/27B SFT，共训 849 个模型，评测 AppWorld（Test-N/Test-C）、BFCL v3 多轮、ASTRA-Bench、自建 SynthAPI-Holdout。诊断用 AppWorld + Holdout（光评测就 180 万 episode）。
- **结果**：
  - 固定任务数 N=A·T：N 小时少 app 更好（A=8 在 64–512 任务最好），N≥4096 时 A=64 明显最好，且拟合上限随 A 升高。数据库广度 S：32–512 个实例时 S=1 最好，512–4096 时 S=2，4096 以上 S=4。D=4 在大预算下明显优于 D=1/2（作者承认可能部分反映 benchmark 对复杂数据库状态不够敏感）。
  - 规律：P̂ = σ(c0 + cA·log2(A·S·D))·σ(b0 + bT·log2 T)^ν；按训练 FLOPs 留出最高 25%（相当于最大拟合预算的 16 倍外推），保留集 MAE 0.0285，仅用任务数的定律为 0.1706。
  - 同一 32,768 任务预算：SynthAPI-SubOpt（A=32,T=1024,S=1,D=2）vs Opt（A=64,T=128,S=4,D=4），AppWorld Test-C 4B/9B/27B：38.4/53.0/73.8 vs 45.0/56.2/74.1；BFCL 44.9/47.5/59.6 vs 48.8/49.9/61.5；Holdout 51.3/56.0/64.0 vs 56.0/63.0/68.0。27B 上差距很小，ASTRA 上 9B/27B 的差只有 1–2 点。
  - 对比前人：Nemotron-Agentic（LLM 模拟工具响应，335k 轨迹）在 8 个设置里有 5 个低于零样本；ToolACE/ToolAlpaca 在 AppWorld 上低于零样本；SimSAT 是强基线。SynthAPI-Big（全量，4 epoch）AppWorld Test-C 4B/9B = 66.4/77.0，比 SimSAT 高 7.6/11.6 点；BFCL 上比最强的执行式环境合成基线（EnvFactory / EnvScaler）高 2.0/3.7 点——但作者明确说这些基线是 SFT+RL、小数据，**不能据此分离合成方法的作用或数据效率**。
- **局限**：所有任务单 app，不模拟用户，缺少长文档式检索；定律只在一个数据管线上验证；使用 SFT 蒸馏而不是 RL（RL 用 verifier 可行但太贵没做）；训练专家模型是闭源/强模型。
- **代码/数据**：正文未见发布链接（未核对）。

### 3. SPADE: Self-Play in Adaptive Synthetic Executable Environments
- arXiv 2608.19197（v3），UW/Stanford/CMU/MIT 等，预印本。https://arxiv.org/abs/2608.19197 　代码 github.com/spade-rl/spade
- **问题**：让同一个 LLM 既当"环境设计者"（写出带 reset()/step() 的完整 Python 环境）又当"推理 agent"，环境分布能否随学习者一起前进？
- **设置**：设计者用"提示线索回报差"（hint-based regret）作奖励：agent 带特权 hint 与不带 hint 的平均回报之差（实际取 max(0,·)，与难度锚点混合）；设计受预训练语料文档约束（grounding）并带环境记忆。GRPO，两个设置：games（Qwen3-4B/8B-Instruct-2507、30B-A3B-Instruct-2507，400 步，对照 Fixed-env GRPO 和 Fixed-env RLVE）与 tool-use。评测：AIME'25/'26(Avg@32)、GPQA-D、LCB-v6、Reasoning-Gym 的 4 类（共 8 项，其中 4 项是 Reasoning-Gym），tool-use 评 BFCL v4 多轮、τ²-bench、ACEBench-Agent。
- **结果**：
  - 30B-A3B games：八项平均 50.2（基座）→58.3（+8.1），最强固定环境基线 RLVE 53.0，Fixed GRPO 51.4。增益主要在 Reasoning-Gym（RG-Math 45.0→63.3，RG-Algo 18.0→32.1，RG-Cog 23.0→37.7）；AIME'25/'26 仅 +1.3/+0.9，GPQA-D +5.4，LCB +4.1。Fixed-env RLVE 在 30B 上 AIME'25 61.5→56.9、'26 73.5→69.8（低于基座）。4B/8B 平均提升 +5.2/+5.7（RLVE +3.6/+3.9）。
  - Tool-use：BFCL v4 多轮 +10.3（4B）/+6.4（8B）/+5.7（30B）；ACEBench-Agent +8.9/+9.0/+13.9；τ²-bench +3.8/+3.3/+3.6。作者自己的解释：增益大小随 benchmark 任务结构与生成环境的相似度变化。
  - 消融（30B games，八项平均）：完整 58.3；去记忆 53.2；去语料 grounding 53.5；去设计者训练+记忆 40.5（比基座低 9.7）；固定设计者（GPT-5.5 离线静态池，带语料）53.0，只拿到 SPADE 增益的约 35%，且 LCB 42.6 低于基座 43.2。去记忆、去语料的变体在约第 111 步左右达到峰值后回落，GPT-5.5 池约在第 175 步。设计者奖励：hint 回报差 +8.1，EMA 学习潜力 +5.7（约 70%）。
  - 环境供给：可学习份额（agent 胜率在 20%–80% 的环境占比）随训练升到约 1/3；多样性 Vendi/n 有语料 0.68，无语料 0.04（引用 Ivison 2026 同样发现无 grounding 的 proposer 坍缩到少数近似程序）；设计者训练使环境"更难的代码层面特征"变化：物理环境首个观察里直接给出公式的比例 25%→5%，每个环境的奖励档位 3.7→5.8（严格部分奖励 2.2→4.0）；环境平均长度（316–333 行）、隐状态变量数（13.0–13.4）基本不变。
- **局限（作者）**：环境复杂度受设计者基座模型表达能力约束；优化器是人为固定的 GRPO；hint 回报差没有最优性证明；评测是固定任务。附加观察（来自表）：消融里各对照改变的因素不止一个（作者自己承认"each control changes more than one factor"），单次运行（无种子方差）。
- **代码/数据**：有代码与项目页。

### 4. Survive or Collapse: The Asymmetric Roles of Data Gating and Reward Grounding in Self-Play RL
- NeurIPS 2026 poster；arXiv 2605.22217。https://arxiv.org/abs/2605.22217 　代码 github.com/SophiaPx/survive-or-collapse
- **问题**：AZR 式自对弈的坍缩，是由"哪些 proposer 生成的任务进入训练池"（数据门）还是"奖励怎么算"决定？
- **设置**：Qwen3-4B-Base，GRPO（solver 每题 16 rollouts，proposer 奖励用 8 次新 rollout 估通过率），单模型两种 prompt 模板；任务 A：Python 输出预测（基线验证准确率约 0.14）；任务 B：15 算子前缀表达式 DSL 的"孪生"任务（确定性解释器，去掉预训练先验/输出歧义/执行噪声，基线约 0.53）。门 F_ε：执行失败的任务以概率 ε 放行（ε=0 为严格门）。7 种 proposer/solver 奖励（grounded vs intrinsic 自一致性）× 门 的配置。至多 700 步。随机数种子文档里只出现 1 个（泄漏率 Bernoulli 抽样的 seed=1）。
- **结果**：
  - 有门的 3 个配置（GG/GI/II+exec）在编码任务验证准确率 0.71/0.67/0.67，全稳定；无门的 4 个配置在编码上全部塌到 0.002–0.007（含 grounded 奖励）。DSL 上无门时只有 intrinsic-solver 的配置塌（GI 0.38、II 0.18），grounded-solver 的留在基线附近（0.50/0.58），作者解释为 DSL 解释器本身起了隐式门的作用。
  - 自一致性奖励在无门时：intrinsic–grounded gap 约 200 步内饱和到约 1.0；"受污染数据反而奖励更高"。
  - "Grounded Proposer Paradox"：无门+intrinsic solver 时，grounded proposer（GI+off）比 intrinsic proposer（II+off）更快到达自洽吸引子；终点相同（0.002 vs 0.007），差别在速度。作者说这是在无门条件下被激活，并非 grounded proposer 本身造成。
  - 连续泄漏率 ε∈{0,0.05,0.10,0.20,0.40,0.70,1.0}（II 配置）：ε=0.05 时训练侧 gap 0.16→0.44，验证 0.674→0.668 几乎不动；ε=0.20→0.40 域内验证 0.651→0.004；"混合验证聚合指标"在 ε=0.40 还在基线（0.329 vs 0.313），到 ε=0.70 才低于基线（0.305 vs 0.316）。Youden 指数 J=1−ε 在所有 ε<1 都>0，静态任务理论预测不了这个更早的塌陷。
  - 严格门 ε=0 在两种验证口径上都最好（混合 0.619，域内 0.674）；稳定区晚期数据池"合格率"约 0.007（不到 1% 的 proposer 输出进池）；先 ε=0 训 150 步再切 ε=0.05，到 450 步域内 0.420，基线 0.674。
- **局限**：单模型规模（4B）、单一任务族（输出预测）、几乎单种子；"验证在训练侧已退化时仍稳"作者归因为回放缓冲正则化，但"缺乏形式化解释"；合格率<1% 的天花板被作者列为"proposer 容量"问题，没有解决。
- **代码**：有。

### 5. On Data Engineering for Scaling LLM Terminal Capabilities (Terminal-Task-Gen / Nemotron-Terminal)
- NeurIPS 2026 poster（ICML 2026 页面也有列）；arXiv 2602.21193，NVIDIA。https://arxiv.org/abs/2602.21193
- **问题**：训练终端 agent 的数据怎么做：数据集适配器（把数学/代码/SWE 的 prompt 包装成终端任务）与合成任务（种子式/技能式）各自价值如何、怎么过滤、怎么混？
- **设置**：教师 DeepSeek-V3.2；9 个领域，9 个预置 Docker 镜像（不为每题生成 Dockerfile）；合成任务不生成 oracle 解，用合成的 pytest 测试判分；Qwen3-8B 做消融，14B/32B 验证；SFT 2 epoch，lr 2e-5，8B/14B 用 32 GPU，32B 用 128 GPU；评测 Terminal-Bench 2.0（Terminus 2）。
- **结果**：
  - 主结果：Qwen3-8B/14B/32B 2.47/4.04/3.37 → Nemotron-Terminal 13.0/20.2/27.4（32B 超过 Qwen3-Coder-480B 的 23.9；14B 超过 GPT-OSS-120B 的 18.7）。
  - 数据源（Qwen3-8B）：适配器 Math 5.39、Code 6.29、SWE 7.02，合并 9.66；合成任务种子式 6.18、技能式 12.4（139,841 条），合并 12.4（264,207 条，方差更小）。
  - 过滤：合成任务不过滤 12.4，只保留完整轨迹 6.74，只保留成功轨迹 5.06——作者说保留失败轨迹提供错误状态与恢复模式的监督；适配器子集上过滤差异不显著（不过滤 9.66，complete-only 8.09）。
  - 课程（先适配器后合成）10.39 < 单阶段混训 13.03；长上下文（SFT 65,536 + YaRN）没有收益（13.0 vs 10.3–11.9）；合成数据 0/1/2/5/10/100% 的缩放随数据量单调上升，14B 增益更大。
  - 按类别：Data Querying、Model Training 在 14B/32B 基座上为 0.0，32B 训练后 60.0 和 50.0；Scientific Computing、Mathematics、Games、Video Processing 等基本无提升（0.0）。
- **局限**：只做 SFT，没做 RL（作者列为未来工作）；合成任务无 oracle，靠合成测试；任务分类只有 TB2.0 的 89 个任务，类别格子很小。
- **代码/数据**：Nemotron-Terminal 模型与 Terminal-Corpus 数据（适配器与技能式子集）已发布于 HuggingFace nvidia/nemotron-terminal；种子式子集发布情况未核对。

### 6. CLI-Gym: Scalable CLI Task Generation via Agentic Environment Inversion
- ICLR 2027 投稿，评分 3.00（OpenReview id 9ZT4TUPvto，OpenReview 本身未读）；全文读自 arXiv 2602.10999（ICML 格式）。https://arxiv.org/abs/2602.10999 　代码 github.com/LiberCoders/CLI-Gym，数据 HF LiberCoders/CLI-Gym
- **问题**：环境密集型 CLI 任务（依赖、权限、系统文件）怎么自动大量生成？
- **设置**：从"健康、单测通过"的仓库 Docker 环境出发，让 agent 主动"破坏"环境（写 Dockerfile 命令）使若干测试失败（环境反演），失败的测试成为 fail-to-pass，再由 LLM 写 issue 描述。29 个 Python 仓库得 1,655 个任务（HF 卡片为 1,321，不一致），生产成本 2.3B token；强模型 rollout 得 417 条成功轨迹，过滤后 291 条。Qwen3-32B / Qwen3-235B-A22B-Instruct 先用 48K 开源 SWE 轨迹训，再加这 291 条；OpenHands 框架；评测 Terminal-Bench 1.0 / 2.0。
- **结果**：Qwen3-32B Terminal-Bench 1.0 Pass@1：10.3 → +SWE 22.1 → 只加 CLI-Gym 32.4 → 两者 38.9；235B：25.0 → 28.6 / 39.5 / 46.1（TB2.0 提升 +12.9 到 31.0）。固定 100 条轨迹，仅改变源仓库数（1,2,4,8,16,32），性能单调上升（作者称多样性比轨迹数更关键）；用 291 条的不同比例，约 200 条之后趋于平台。过滤：没有 SWE 预训练时，417 条未过滤（33.8）略优于 291 条过滤（32.4）；有 SWE 预训练后，过滤后 38.9 优于未过滤 36.4。
- **局限**：只覆盖 Python 仓库；Gaming、Scientific computing 类别无改善；训练后更倾向更多探索，更易超过 128k 上下文；样本量小（291 条）。
- **代码/数据**：公开。

### 7. WorkRover: Scaling Long-Horizon Cowork Agent Training via Recursive Environment Evolution
- arXiv 2610.18067（2026-10），复旦等，预印本。https://arxiv.org/abs/2610.18067
- **问题**：合成环境初次生成后常有缺陷（任务、工作区、验证器不对齐），如何用 rollout 反馈递归修复，并给长程任务更细的信用分配？
- **设置**：construction agent 联合构造"工作上下文 + 任务 + 证据型验证器"；FCR（Factorial Compatibility Replay）对 工作上下文/任务/harness/验证器 的修复提案做组合重放，选最小的已验证修复；VTCA 用确定性工作区进度检查，把正向信用分给前置轮次。Qwen3.5-35B-A3B：SFT 30,115 条（Qwen3.5-397B-A17B 在合成工作区里产生）→ RL 3,200 对（20,000 对经 4 次试跑一致性过滤后留下）。评测 5 个外部基准：JobBench、GDPval v2（Elo）、AutomationBench、WorkBuddy Bench(Office)、OfficeQA Pro。
- **结果**：相对基座：JobBench +26.27 点（10.62→36.89），OfficeQA Pro +29.32（19.55→48.87），AutomationBench +22.67（6.00→28.67），WorkBuddy +13.63（60.50→74.13），GDPval +413.25 Elo（804.75→1218.00）。在 27–35B 开源模型里每个基准最高，但 GDPval 低于所有 >400B 开源模型（1303.96–1572.42）。VTCA vs 只用轨迹级 GRPO：5 个基准全部更好（AutomationBench +5.7，OfficeQA Pro +5.4，GDPval +43 Elo）。
  - 环境修复：FCR 的"安全修复率"在自然缺陷上 60.7%（全量重生成）→70.3%，对任务意图的改动 14.3%→1.3%；比"全部应用"高 9.0/10.4 点，跨任务回归 7.0%→0.7%（代价是 token 1.00 vs 0.59）；48–74% 的成功修复需要联合编辑（不能拆成更小的子集）；**连续 3 代的修复质量基本不变**（SRR 70.3–72.4%，审计通过率 93.8–94.6%）；合成通过率 74.8%（修复前 49.8%，全量重生成 68.8%）；构造消融：去掉关系感知扩展 74.8→52.6，去掉验证引导的重写 74.8→49.8。
- **局限/保留**：没有"不用合成环境"的对照（比较对象是基座与其他模型）；不同模型的参考分数来自各自来源的评测设置。
- **代码**：项目页 workrover.github.io。

### 8. CUA-Master: Scaling Computer-use Agents through Open-World Recursive Improvements
- arXiv 2611.03126（2026-11），CUHK 等，预印本。https://arxiv.org/abs/2611.03126
- **问题**：用嵌套的"世界-数据-模型"外环与"开放世界播种+自催化传播"内环做计算机使用 agent 的递归改进。
- **设置**：从教学视频挖真实工作流作种子任务，经"视觉-语义双路径轨迹重建"变成可复用原语，再按 K 个原语、N 个应用的组合合成可验证任务；快照回滚重试收集轨迹。Qwen-3.5-27B 起，SFT 三轮累计（63K/38K/14K，共约 115K 任务）+ RL（约 12K 任务），16 节点×8 H200。
- **结果**：CUA-Master-27B：OSWorld Verified 80.2，OSWorld 2.0 36.9，WeaveBench 43.9，Agents' Last Exam 25.0（同基准上 Qwen-3.8-27B 为 81.2/36.5/14.1/19.1，Claude-Opus-5 为 86.3/64.2/55.7/28.3；主表是自己重新评测所有基线）。混合 GUI+CLI 动作空间：WeaveBench 43.9 vs 仅 GUI 6.6、仅 CLI 11.5。内环：K=40,N=3 的任务合成成功率 ~49.8% vs 基线 14.6%；K/N=50/8 为 18.7% vs 0.0%。外环：各轮 SFT/RL 在四个基准上逐轮上升，OSWorld Verified 与 WeaveBench 累计涨 25 点以上，最后的 RL 让 OSWorld 2.0 与 Agents' Last Exam 再涨约 15 点；标注模型越强收益越大，"用自己上一轮模型当标注器"（self-policy）有提升但"相对有限"。
- **局限（作者）**：基础设施成本高（大量 VM）；数据质量上限取决于强标注模型。
- **保留**：t-SNE 只给定性覆盖；数据与基线的重新评测协议细节在附录（未逐行读）。

### 9. Quest: Training Frontier Deep Research Agents with Fully Synthetic Tasks
- NeurIPS 2026 poster；arXiv 2605.24218，OSU + Amazon，标注为 work in progress。https://arxiv.org/abs/2605.24218 　代码 github.com/OSU-NLP-Group/QUEST，模型 HF osunlp/QUEST-35B-RL
- **问题**：用统一的"评分细则树（rubric tree）"合成数据，能否训出跨任务类型（事实检索、引用溯源、报告写作）都强的 deep research agent？
- **设置**：Qwen3.5-35B-A3B（以及 Qwen3-30B-A3B、2B/4B/9B）；中期训练（MT）+ SFT + RL，总共 8K 合成任务；内置上下文管理。评测 8 个基准（BrowseComp、BC-Plus、Mind2Web 2、WideSearch、HLE、GAIA、DeepResearch Bench、LiveResearchBench）。
- **结果**：Quest-35B：BC 45.5（discard-all 策略 64.6）、BC-Plus 61.0（69.5）、M2W2 30.7、WideSearch 60.6、HLE 37.2、GAIA 80.8、DRB 48.2、LRB 68.2；GAIA 超过 GPT-5（76.4）、M2W2/DRB 超过 OpenAI-DR（28.0/47.0）。同为 30B：Quest-30B 在 8 项里 4 项最好；Tongyi-DR 在 BC/HLE/GAIA（强调其单答案合成数据）、OpenResearcher 在 BC-Plus（与其合成配方最贴近）最好。作者结论：能力轮廓由数据合成配方塑造。
  - 阶段消融：SFT 提升多数客观基准但**低于基座**的开放式基准（报告型）；RL 大幅提高开放式基准、略降 HLE 与 GAIA（作者猜测类似"对齐税"）；MT 总体有增益。只用 SFT 的 2B 模型在 HLE/GAIA 上接近或超过 OpenAI-DR/o3，但报告型基准落后很多。
  - 失败尝试：把"搜索结果预测"加入中期训练混合反而降低总体；rubric 错误识别任务仅边际收益；DPO 报告比较无收益且不稳定；逐点评分出现分数膨胀（约 50% 的评分趋近 1），成对 win/tie/lose 因早期模型总输给教师而全部坍成 0。
- **局限**：数据合成所用教师/评审模型与规模、与自然任务分布的距离，我读的正文部分没有单独量化（附录未读）；"仅 8K 任务"指的是总训练实例。

### 10. Breaking the Solver Bottleneck: Training Task Generators at the Learnable Frontier (PROPEL)
- arXiv 2606.18284（2026-06-18），Vmax / Goodfire，预印本。https://arxiv.org/abs/2606.18284
- **问题**：训练任务生成器（RL）时不能每个候选都跑昂贵的 solver rollout（SWE 任务要几十分钟）；能否用生成器激活上的探针预测 solver 通过率当奖励？
- **设置**：实用度 U=1[1/8 ≤ solver 8 次通过率 ≤ 3/8]（SWE 用 K=3、1/3–2/3）；探针在冻结参考生成器激活上训练，用一次性标注语料；奖励 = 合法性门 + 探针 logit；对"固定探针导致的模式坍缩"做最坏情况优化（WCO，两探针集成）。三个域：数学、AZR 式代码归纳、SWE（Qwen3.5-27B solver，在训练探针与生成器时没见过的仓库上测）。
- **结果**：生成任务落入目标通过率区间的比例：代码归纳 3B solver 10.1%→20.0%，7B 5.3%→12.6%；SWE Qwen3.5-27B 9.8%→19.6%（OOD 仓库，一个 solver 的作业，标注 OOD 的利用率 0.098→0.196）；数学在严格 oracle 之后条件产出 +11 点（7B）/ +17 点（3B）。探针冷迁移到 Mistral-7B 与 Phi-3.5-mini 生成器有收益（Qwen3.5-4B 上训练的探针）。
  - 坍缩：固定探针下 AZR 3B solver 74% 的生成任务集中在单一主题（sorting_order）；WCO 把 7B solver 的 top-topic 占比 0.67→0.54，3B 0.74→0.69，同时保留 +71%（3B）/ 约 +86% 的相对收益；KL 系数过小时（0.02）数学训练完全坍缩；对抗式探针共进化只做了小规模探索。
- **局限（作者）**：只覆盖三个域；探针只训一次，策略漂移后会退化；缓解措施"部分且以效用换多样性"；探针的标注语料仍需 solver rollouts。主指标是"生成任务的实用度"，本文主体不是"在这些任务上训练的 solver 变好了多少"（附录里有"为下游 solver 微调提供 bug"的数据划分，我没读到对应结果）。

### 11. MagicBeanStalk: Escaping the RLVR Zero-Advantage Trap with Recursive Data Synthesis
- arXiv 2610.12659（2026-10），UW/CMU/Stanford/NVIDIA（含 Yejin Choi、Aviral Kumar），预印本。https://arxiv.org/abs/2610.12659
- **问题**：什么样的合成题对 RLVR 有用？大语料为什么学不到？
- **设置**：目标策略 gpt-oss-120b 与 DeepSeek v4 Flash；rollout 预算 L=16K/24K/32K token；8 个数学基准（AIME 24/25、AMC、HMMT-F/N、Minerva、Olympiad、Omega-500）+ MathArena Apex；金融域（Qwen3-4B，SecQue、FinanceBench）。
- **结果**：约 78K 开源数学语料（DAPO-Math-17K、Skywork-OR1、Turing Open-RL、StackMathQA 子集）对 gpt-oss-120b（32K，每题 8 次）只有 12.2% 落在"有的对有的错"区间，约 88% 是零优势；同一语料换目标策略，32.3% 的题改变所属类别；把预算从 16K 加到 64K，困难题占比 33.1%→10.6%。MBS（自顶向下分解+自底向上递归合成，保留种子的推理蓝图）：从 gpt-oss-120b 得 0/8 的难题种子里，74.7% 的种子产出预算内"恰好"区间的题，直接让教师改写只有 43.8%；匹配对照（共享种子集，一个 epoch）MBS 69.2，直接合成 63.9，只训种子 65.3；全 78K 语料训练仅 +1.1，最好的过滤子集 +5.8，MBS +8.6（61.2→69.8，16K 预算）；DeepSeek v4 Flash 72.4→77.9；MathArena Apex 上增益在各预算下超过最佳基线。金融：340 个专家种子合成 14,000+ 题，+6.9（SecQue）、+2.4（FinanceBench）。
- **要点**：直接让教师改写难题保留了技巧但多是浅层变体，"种子合成不优于种子本身"。
- **未读**：附录 B 的更多蓝图稳定性数字（只读了 90.7% 一致性的主文引用）；训练步数/算力主文未提取。

### 12. Self-Play Only Evolves When Self-Synthetic Pipeline Ensures Learnable Information Gain
- ICML 2026（PMLR 306）；arXiv 2603.02218，KCL/Turing。https://arxiv.org/abs/2603.02218
- 性质：立场/诊断型，实验小。**论点**：自进化循环（Proposer/Solver/Verifier）合成了更多数据但"可学习信息"没有增加，所以停滞；提出三类设计（非对称共进化、容量增长、主动信息获取）。
- **实验**（AZR 的 abduction/deduction/induction 三类代码任务；用 epiplexity（前序编码 MDL 估计）度量可学习信息）：(1) 更强的 proposer（Qwen2.5 7B→14B→Qwen3 4B）产生含更多可学习信息的数据；(2) 固定数据下，随 solver 规模增大，可学习信息先升后降（作者联系"预算够大后改为记忆"）；(3) induction 远高于 abduction/deduction；(4) 持续自对弈若干轮后，epiplexity 不是稳步增加而是剧烈波动，伴随 solver 能力下降与 proposer 题型坍缩。
- **局限**：作者自己说是"诊断性、非穷尽"；三条设计没有用端到端实验验证效果（我读到的正文里没有）。

---

## 二、已分流但未精读（一行表）

| 论文 | 状态 / 链接 | 一句话（来源） |
|---|---|---|
| Multi-Agent World: Scaling Multi-Agent Orchestration Training via Recursive Environment Improvement | ICLR'27 投稿 [3.33]，openreview.net/forum?id=MVK4T47ej0 | ABSTRACT ONLY（清单片段）：训练编排器需要带子任务与验证器的多智能体环境；递归环境改进。摘要被截断，细节未知 |
| MetaExp: Learning to Self-Improve through Experience via Verifiable Cross-Task Environment Scaling | ICLR'27 [3.33]，id=ZJIqqHVTnE | ABSTRACT ONLY：把"从经验中学习"本身作为可迁移能力，用可验证的跨任务环境扩展来训练 |
| SWE-Craft: Graph-Guided Task Synthesis for Weak Spots in Coding Agents | ICLR'27 [3.00]，id=JtQbtZVoHo | ABSTRACT ONLY：目标条件化的 SWE 任务合成，图引导，对着弱点生成 |
| DataPraxis: Scaling Analytics Tasks via Verified Workspace Evolution | ICLR'27 [3.00]，id=OrJmmo9dXI | ABSTRACT ONLY：从原始数据直接生成任务会漏掉分析中涌现的深层问题；用已验证的工作区演化合成分析任务 |
| Skill2Env: Capability-Oriented Environment Synthesis from Skills | ICLR'27 [3.00]，id=t4j8ZQwcZP | ABSTRACT ONLY：从"技能"文档合成可执行环境与任务 |
| Agent World Model in the Wild (WildAWM) | ICLR'27 [3.00]，id=XScKMmbFmx | ABSTRACT ONLY：可控的计算机使用环境/任务合成管线 |
| Scaling Agentic Data for Long-Horizon Terminal Intelligence | ICLR'27 [3.00]，id=UOwYasdeqY | ABSTRACT ONLY：长程终端轨迹数据 |
| SIGMA: Self-Improving Alignment Generalization from a Model Spec | ICLR'27 [3.00]，id=Ui2V1tDmNJ | ABSTRACT ONLY：从模型规范自改进对齐泛化，问题设定是"对齐难验证" |
| CompassPlay: Rewarding the Proposer for Where It Moves the Solver | ICLR'27 [2.75]，id=AzaFXLqRqr | ABSTRACT ONLY：proposer 奖励改为 solver 损失梯度与参考任务梯度的对齐，而不是通过率 |
| RSI-Forge: From Research Papers to Environments for RSI | ICLR'27 [3.00]，id=D54Tq2ULjl | ABSTRACT ONLY（仅标题）：把论文转成递归自改进环境 |
| Verifier–Harness Co-Evolution for Training-Free Self-Improvement | ICLR'27 [3.00]，id=HuOAuecWpX | ABSTRACT ONLY（仅标题） |
| Frontier Task Synthesis via Solution-Centric Evolution | NeurIPS'26 poster | ABSTRACT ONLY：基准饱和（LiveCodeBench 简单档>99%）后，用解法为中心的演化合成前沿难度任务 |
| Democratizing Tool Learning with Environments Fully Simulated by a Free 8B LM (TRUSTEE) | NeurIPS'26 poster | ABSTRACT ONLY：用 8B 模型模拟环境训工具调用 agent |
| SWE-Crafter: Scaling Executable Multilingual SWE Data with Meta-Skill Agents | NeurIPS'26 poster | ABSTRACT ONLY |
| SimWorld Studio: Automatic Environment Generation with Evolving Coding Agent | NeurIPS'26 poster | ABSTRACT ONLY：具身 3D 环境自动生成 |
| Verifier-Backed Hard Problem Generation for Mathematical Reasoning | NeurIPS'26 poster | ABSTRACT ONLY（仅标题） |
| Seirênes: Adversarial Self-Play with Evolving Distractions | NeurIPS'26 poster | ABSTRACT ONLY（仅标题） |
| IFDecorator / MedZERO / AutoDataBench / G-Zero 等 | NeurIPS'26 | ABSTRACT ONLY；G-Zero 另见 arXiv 2605.09959（搜索摘要：proposer 针对生成器盲区，GRPO，对啰嗦加长度惩罚） |
| Agent-World (2604.18292) | arXiv 2026-04 | 搜索摘要：环境主题挖掘 + 训练场；报告环境数、自进化轮数与下游性能的缩放关系；未读全文 |
| Agent World Model (2602.10090) | arXiv 2026-02 | 搜索摘要：1,000 个代码驱动环境；扩展到 526 环境性能继续上升；未读 |
| EnvScaler (2601.05808) / ScaleEnv (2602.06820) / EnvFactory | arXiv 2026 | 搜索摘要：EnvScaler 在 0→20 个环境性能升得最快后放缓；未读（SynthAPI 论文作为基线引用） |
| DIVE (2603.11076) | arXiv 2026-03 | 仅见于 RES/SynthAPI 引用：工具使用任务合成里的多样性；未读 |
| RST: Recursive Synthesis for Long-Horizon Terminal Tasks (2608.05466) / CLI-Universe (2606.22883) / LiteCoder-Terminal (2605.29559) / NexForge (2607.14186) | arXiv 2026 | 仅标题与搜索摘要；未读 |
| SPICE (2510.24684) | arXiv 2025 | SPADE 与 RES 引用，语料环境里自对弈；未读 |
| R²Orch (2610.22740) | arXiv 2026-10 | 只读了摘要与结构：内环 proposer–director 自对弈，外环改进"内环如何改进"，以"技能撤回后 rollouts 是否仍分歧"为 proposer 奖励；未精读实验 |
| Reward Hacking Benchmark (2605.02964) / BAITBENCH (2608.30724) / Gaia2 (2602.11964) | arXiv 2026 | 搜索摘要：RL 后训练使同一环境的奖励利用率上升；加固环境降低 5.7 点；Gaia2 里 agent 用大段代码淹没 LLM 判分器；未读 |
| COVERT (2604.09813) / SANDMLE (2604.04872) / GenEnv (2512.19682) | arXiv | 搜索摘要：COVERT 加干扰工具与噪声输出但保留 oracle 调用；SANDMLE 合成 ML 工程任务，用已知能力模型排序检验难度；GenEnv 按中等成功率奖励环境模拟器；未读 |

---

## 三、领域综合（只陈述事实，不提建议）

### 3.1 现在算标准的做法
- 合成对象是"可执行环境 + 可程序验证的任务"：Python/数据库后端的工具环境（SynthAPI、EnvScaler 系）、带 Dockerfile 与单测的终端/SWE 任务（Terminal-Task-Gen、CLI-Gym）、rubric 树（Quest）、带 reset()/step() 的 Gym 式代码环境（SPADE）。正文里普遍把"任务 = 指令 + 初始状态 + 验证器 + 可选 oracle 解"当作单元；用 oracle 求解器或"强模型至少一次通过"来过滤可行性（SynthAPI、CLI-Gym、Terminal-Task-Gen 的不同做法）。
- 用强教师（GLM-5.2、DeepSeek-V3.2、Qwen3.5-397B、GPT-5.x）蒸馏轨迹做 SFT 仍是最常见的下游训练方式（SynthAPI、Terminal-Task-Gen、CLI-Gym、RES、CUA-Master、WorkRover 的第一阶段）；RL 多半放在 SFT 之后或作为较小的第二阶段（WorkRover、CUA-Master、Quest）。纯 RL 的合成环境对比较少（SPADE、Survive or Collapse、MagicBeanStalk 是例外）。
- "难度校准"几乎都用目标策略的通过率区间：solver 8 次里 1–3 次（PROPEL 引用的 Self-play SWE-RL 取值）、20%–80% 的"可学习份额"（SPADE）、"零优势陷阱"（MagicBeanStalk）、"至少一次成功才保留"（多个管线）。
- 递归/迭代已成为命名套路：RES、WorkRover、CUA-Master、Multi-Agent World、MagicBeanStalk 的"递归"含义各不相同——RES 是对同一环境继承式加难；WorkRover 是修复缺陷；CUA-Master 是"数据—模型—世界"外环；MagicBeanStalk 是自底向上递归组合问题。
- 评测大量使用同一批自然基准：Terminal-Bench 1/2、AppWorld、BFCL v3/v4、τ²-bench、OSWorld、AIME、GPQA-D、LCB-v6。

### 3.2 对自然基准的迁移，以及什么与迁移相关
- 迁移幅度报告都很大，但基线与评测对象差异悬殊：Terminal-Bench 2.0 上 Qwen3-8B 2.47→13.0（SFT 在合成终端任务上，教师 DeepSeek-V3.2）；CLI-Gym 在 TB1.0 上 Qwen3-32B 10.3→38.9；SynthAPI AppWorld Test-C 4B 14.7→66.4（Big）；WorkRover 的 5 个办公基准 +13 到 +29 点。这些都是 SFT（常加 RL）+ 强教师，且基座初始分很低，所以绝对涨幅与基座起点、教师强度混在一起。
- 迁移的差异与目标基准和合成分布的"结构相似度"相关：SPADE 的 tool-use 增益 ACEBench-Agent +13.9 > BFCL +5.7 > τ²-bench +3.6，作者归因于结构相似；SynthAPI 的 AppWorld 增益远大于 ASTRA-Bench（9B/27B 仅 1–2 点）；Quest 的各开放权重对手各自在与自己合成配方最贴近的基准上最好（Tongyi-DR 在 BC/HLE/GAIA，OpenResearcher 在 BC-Plus）；CLI-Gym 的类别提升集中在环境密集类，Gaming/Scientific computing 不动；Terminal-Task-Gen 的 Scientific Computing/Mathematics 等类别提升为 0。
- 在"推理"基准上的迁移明显小于在"同族程序化"基准上：SPADE 30B 的八项平均提升主要来自 4 个 Reasoning-Gym 列（RG-Math +18.3 等），AIME'25/'26 只 +1.3/+0.9；固定环境 RLVR 基线在 30B 上 AIME 低于基座（−4.6/−3.7）。
- 与迁移相关的、有对照证据的变量：
  - 多样性（按"轴"分）：SynthAPI 在固定任务预算下，随预算增大，工具/应用多样性与数据库实例广度优于"更多任务指令"，拟合的上限随 A、S、D 升高（保留集 MAE 0.0285 vs 仅任务数 0.1706）；CLI-Gym 固定 100 条轨迹，仓库数 1→32 单调改善；SPADE 的语料 grounding 使 Vendi/n 0.68 vs 0.04。
  - 在预算小时相反：SynthAPI 里 N≤512 时集中在少量 app 反而更好。
  - 加难（保持目标不变）：RES 的难环境轨迹在等条数 SFT 中优于原环境轨迹 7–14.6 点；但 RES 只做了单次运行，且未配平 token。
  - 轨迹/数据过滤：Terminal-Task-Gen 里保留失败/不完整轨迹优于只保留成功（12.4 vs 5.06）；CLI-Gym 里过滤收益依赖是否已有 SWE 预训练。
  - 难度相对于策略与预算：MagicBeanStalk 里换目标策略会改变 32.3% 的题的类别；加大预算使困难题 33.1%→10.6%；约 88% 的大语料是零优势。
  - 教师/标注强度：CUA-Master 里更强标注模型带来更大收益，自己上一轮当标注器收益有限。
  - 数据混合/课程：Terminal-Task-Gen 的两阶段课程不如混训；长上下文无收益。
- 报告的"数据量与性能"关系：Terminal-Task-Gen 的缩放曲线随数据量单调上升；CLI-Gym 291 条里 200 条后趋平；SynthAPI 呈有天花板的 logistic（不是纯幂律）。

### 3.3 生成器/环境构造者本身是否被证明会随轮次变好
- 有较直接证据的：SPADE 的设计者经 RL 训练后：对比"去设计者训练+记忆"（八项平均 40.5，低于基座）与完整版（58.3）；可学习份额随训练升至约 1/3；环境的代码级难度特征变化（首个观察里直接给公式的比例 25%→5%，奖励档位 3.7→5.8）；静态 GPT-5.5 池只拿到约 35% 增益。这些来自单次运行。
- PROPEL：RL 训练的生成器相对基座生成器，落入目标通过率区间的比例约翻倍（10.1→20.0 等），代价是固定探针下的主题集中（74% 集中在 sorting_order），WCO 部分缓解。
- WorkRover：环境修复质量**没有**随代数改善（3 代 SRR 70.3–72.4%）；任务成功率随 5 次修复迭代上升。RES：子环境的难度随递归深度上升（Pass@1 82.86→4.76），但这是"难度单调上升"，不是"构造者的质量提升"，且深度 5 之后基本饱和（3.81→4.76）。
- CUA-Master：逐轮训练使 agent 提升，但"用自己上一轮模型当标注器"的增益"相对有限"，而强外部标注器更有效。
- Survive or Collapse 与 Self-Play Only Evolves：在 AZR 型自对弈里，proposer 的有效产出（合格率<1%）与"可学习信息"并不随轮次稳步增长；后者在多轮中剧烈波动。
- 这个问题上大多数论文没有给出"构造者在第 k 轮 vs 第 k+1 轮是否更会出题"的独立度量；对象多为被训练的学习者在下游基准上的分数。

### 3.4 失败模式（论文自报）
- **难度漂移与平凡化**：AZR 式自对弈中 proposer 倾向生成平凡任务（Self-Play Only Evolves 引述）；Survive or Collapse 里无门时 proposer 的输出依赖哈希随机、浮点显示、副作用，训练池被歧义程序充满，grounded 奖励也不再提供信息。
- **自一致性吸引子 / 奖励利用**：自一致性奖励在受污染数据上奖励反而更高，gap 约 200 步内饱和到约 1.0；严格门稳定，ε=0.05 的泄漏就让训练侧 gap 0.16→0.44，ε 在 0.20–0.40 之间域内验证 0.651→0.004，而聚合验证指标要到 ε=0.70 才低于基线。
- **多样性塌缩**：无语料 grounding 的设计者 Vendi/n 0.04（SPADE）；固定探针导致 74% 任务落在一个主题（PROPEL）；KL 太小时数学生成器完全坍缩；种子直接让教师改写只产生浅层变体，每个种子合格产出少于 1 个（MagicBeanStalk）。
- **可利用的验证器/不对齐**：WorkRover 指出任务、工作上下文、验证器可能不对齐，使有效行为被判失败或错误结果被奖励；48–74% 的成功修复需要联合编辑。Quest 中 LLM 评审逐点评分膨胀（约 50% 趋近满分）、成对打分对弱模型全判负。SynthAPI 的验证器检查数据库状态，作者没有单独报告验证器漏洞率。
- **零梯度信号**：约 88% 的大语料在固定策略与预算下是全对或全错（MagicBeanStalk）。
- **早期峰值后回落**：SPADE 的去记忆/去语料/静态池变体在约 111–175 步达峰后回落。
- **能力轮廓被数据配方限定**：Quest 的 SFT 使开放式基准低于基座，RL 略降 HLE/GAIA；CLI-Gym 的 Gaming/Scientific Computing 无改善。

### 3.5 论文报告但未解释的异常
- SPADE：固定环境 RLVR 基线在 30B 上使 AIME 低于基座，而在 4B/8B 上是正的；"去设计者训练+记忆"（自生成静态）比基座低 9.7 点；论文只说"完整的协同自适应设置更好"，对为什么静态自生成环境会主动伤害未给出机制。
- Survive or Collapse：训练侧指标在 ε=0.05 已退化而验证几乎不变，作者推测是回放缓冲的正则化，"缺形式化解释"；严格门下合格率<1% 却仍是最优。
- Terminal-Task-Gen：保留失败轨迹反而远好于只保留成功（12.4 vs 5.06）；课程比混训差；长上下文训练无益；这些只有"推测"。
- CLI-Gym：没有 SWE 预训练时过滤略有害，有 SWE 预训练时过滤明显有益，机制未检验。
- RES：难度与"无变化的目标"仍能保持可解性的主张，只经执行式重放检验；Terminal-Bench 2.1 和 Claw-Eval-Live 上原环境的成功率差异很大（如 Workspace-Bench-Lite 的 TCR@80 只降 12–19 点，而 Claw 降 57–77 点），论文没有解释各基准下降幅度悬殊的原因。
- SynthAPI：D=4 的大收益作者认为可能部分反映下游基准对复杂数据库状态不敏感；Nemotron 数据在 5/8 设置里低于零样本而论文只说"数据简单短程"。
- Self-Play Only Evolves：随 solver 变大，同一数据中可学习信息先升后降，解释为"记忆化"，但未单独验证。
- MagicBeanStalk：直接教师合成"不优于种子本身"，与"多一点数据更好"的直觉相反，主文给了浅层变体的解释（保留技巧但变化小）。

### 3.6 数据质量与证据强度提示（事实）
- 绝大多数训练结果是单种子、单次运行（RES、SPADE、Survive or Collapse、SynthAPI 的 849 个模型是不同数据设置，不是重复种子）；多数含置信区间的只有 Terminal-Bench 系列（Terminal-Task-Gen 报 ±）。
- 主表里"超过更大模型/专有模型"的比较多使用作者自己重跑的基线或各来源不同评测协议（WorkRover 明说参考分数保留原有子集与评测器；CUA-Master 重评了所有基线；SynthAPI 明说与 SFT+RL 基线训练体制不同）。
- 本扫描的 ICLR 2027 项目只读到清单摘要，不能对它们的结果作任何判断。
