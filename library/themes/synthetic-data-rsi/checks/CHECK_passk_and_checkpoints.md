# CHECK: 自我改进环路的 pass@k 天花板 + 公开 checkpoint（2026-11-27）

读取深度标记：FULL = 读了 html/pdf 全文相关节；ABSTRACT ONLY = 只见摘要/搜索摘要；FIG ONLY = 论文只给曲线图、文中无数值。
所有 HF 信息来自 huggingface.co/api（2026-11-27 当天）；GitHub API 被限流，GitHub 信息来自 raw README。

---------------------------------------------------------------------
## Check 1 — pass@k 天花板

### 1a. Yue 2025 及其正反跟进

**Yue et al. 2025 (arXiv 2504.13837)**（FULL，html v5）
- 模型：Qwen2.5-7B/14B/32B base 与 LLaMA-3.1-8B 的 SimpleRL-Zoo GRPO checkpoint；Oat-Zero-7B(Qwen2.5-Math-7B)、DAPO-32B；代码 CodeR1-Zero-7B、DeepCoder-14B；视觉 Qwen2.5-VL-7B；Magistral-Medium（仅 API）。
- k：MATH500/Minerva/GSM8K n=128；AMC23、AIME24 n=1024；算法对比报 pass@256。
- 数字：Omni-MATH 训练 150→450 步，pass@1 26.1→42.5，pass@256 66.3→64.3；测试集 450 步 pass@256 63.9 < base 69.1。AIME24 覆盖：base-only 13.3% vs RL-only 0.0%（k=1024）；MATH500 base-only 3.6% vs RL-only 1.0%。六种 RL 算法的 ΔSE(RL pass@1 − base pass@256) 均 >40 点。Minerva-32B：k=128 时 base 领先约 9 点。
- 自述限制：数学 pass@k 含猜中，人工查了 CoT；过滤 <5% 无 CoT 可答的题（启发式）；模型/超参有限；蒸馏（R-1-Distill-7B）的 pass@k 曲线显著高于 base，即蒸馏能扩边界、RLVR 不能。

**反方（RL 扩边界）**
- **ProRL (2505.24864)**（FULL，html）：DeepSeek-R1-Distill-Qwen-1.5B → Nemotron-Research-Reasoning-Qwen-1.5B，>2k 步，136K 题（数学40k/代码24k/STEM25k/逻辑37k/IF10k），约 16k H100·h，8 段训练+周期性重置参考策略，temp 1.2。重评 256 采样，主报 pass@128，Reasoning Gym 只抽了 96 任务中的 18 个。pass@1：AIME24 28.5→48.1，Reasoning Gym 均值 4.2→59.1，GPQA-D 15.9→41.8。任务分三类 Diminish（主要数学，pass@1 升而 pass@128 平/降）/ Plateau / Sustained（主要复杂任务如代码）；base pass@128 与 RL 增益显著负相关（无系数）。pass@k 曲线在文中无数值（FIG ONLY）。
- **2606.15455 Diversity collapse = overtraining**（FULL，html）：Qwen2.5-Math-7B，MATH 训练集 7.5k，140 步，k=256，一次训练/方法。265/976 题 base 解不出，epoch2 时 70 题(26.4%)进入边界，epoch20 剩 38(14.3%)；同期 711 个 base 可解题丢了 152(21.4%)，净 −114。结论：RL 确实“进”新题，但被过训练的“出”抵消；仅更新零成功题的 BBG 在难集上 pass@256 超过 base。作者自称单次运行、证据非证明。
- ICLR'26 Cover@τ（"pass@k 作边界代理会误导"）、Flat-RLVR 2610.29281、QuestA 2507.13266、2605.06241 综述、PASS@(k,T) 智能体论文（工具使用 RL 扩边界、纯数学不变）：**ABSTRACT ONLY**（仅搜索摘要，未读全文）。

小结：分歧点是“k 多大、训多久、题多难、有无猜中污染”。目前没有人把“RL 是否扩边界”判成定论。

### 1b. 无人工标签的 self-play / self-evolving 环路是否测过大 k（≥64）

**测过的（共 4 项，其中仅 1 项为 ≥256 的 base 对照）：**

| 工作 | 环路类型 | 模型 / 基准 | k | 结果 | 深度 |
|---|---|---|---|---|---|
| **AZR 原文 (2505.03335) RQ8** | 执行器接地（Python 执行） | AZR-Base-7B vs base；HumanEval+、MBPP+、LiveCodeBench、AIME24/25；temp 0.6，16k | 到 512 | 文称 AZR 在 k=256/512 “持平或优于 base”，仅 AIME24(k=512) 例外；图注 4/5 优于。数值只在 Fig.8 | FULL（文字）/ FIG ONLY（数值） |
| **Chae et al. 2510.27072 (NeurIPS'25)** | 同上，用 AZR 的 Coder-3B/7B | Qwen2.5-Coder-3B/7B vs AZR-Coder-3B/7B；MBPP+、HumanEval+、AIME；无偏估计量 | 文未写最大 k | 小 k AZR 高，**大 k base 高**，但大 k 下降“统计上不显著”，比标准 RLVR 轻；Appendix C 给了“被 base 能力界住”的形式论证。无 p 值/CI/种子数 | FULL（html），FIG ONLY |
| **INFUSER 2606.09052 §3.4** | 文档接地生成器（题+参考答案来自文档，非自洽投票），NeurIPS'26 | Qwen3-8B-Base vs INFUSER；AIME24、AIME25、HMMT、MATH-500、BBEH（明确排除纯选择题） | 1→128 | **INFUSER 在 AIME24/25、HMMT、MATH-500 上 k≤128 全程高于 base**；BBEH 上曲线 k=4 处交叉（输出更一致但更不多样）。数值仅图 | FULL（pdftotext），FIG ONLY |
| **Strozzi 2606.07856** | 教师无关 STaR，自带验证器（字符串 DSL 解释器） | Qwen3-4B-Instruct-2507 4bit+LoRA；FlashFill 式 DSL，各 200 题 | 8 与 64 | pass@8 trained>base（易 53.0 vs 46.0；难 46.0 vs 38.0）；**pass@64 base 反超**（易 68.0 vs 61.5；难 57.5 vs 52.5），4/4 轨迹成立；仅两轮，单评估种子，单人单卡 | FULL（html） |

**明确没有测大 k 的（读了全文相关节，均为 pass@1/greedy/mean@32）：**
R-Zero（FULL：greedy，AMC/AIME 用 mean@32，无任何 pass@k；报了 pseudo-label 准确率 79.0→63.0%，4B 在 45 步 48.8%）、Agent0（FULL：同样 greedy+mean@32）、R-Diverse（FULL）、SPICE（FULL：greedy+AIME avg@32）、SPIRAL（FULL：4 次 rollout 平均）、Language Self-Play（FULL：AlpacaEval/MATH 等 pass@1，且用外部 reward model）、Self-Questioning LM（FULL：准确率，无 pass@k）、SPADE（pdftotext grep：只有 Pass@1/Avg@32）、R-Quest（grep：HumanEval+/MBPP+ 用 pass@1）、EvoHeir/Selection Is Not Learning（grep：只有 pass@1）、CompassPlay（grep：贪心解码）、Tool-R0（FULL 前 100k 字符：仅用 pass@K 给任务分桶）。
INFUSER 之外的 INFUSER 同批对比方法（R-Zero、AZR、R-Few、SPICE）没有被它们的作者测过大 k。
R-Few 2512.02472、INFUSER 之外的 Prism 2603.13309、GameSmith 2610.13995、Pursuit-Evasion 2608.21871 等：未读，**未核对**是否含大 k。

### 1c. 结论：能说什么，不能说什么

1. **自洽/多数投票类环路（R-Zero 及其后继 Agent0、R-Diverse、R-Quest）：没有任何人测过 pass@≥64。** 这个格子是空的（我搜了 R-Zero/Agent0/R-Diverse/R-Quest 全文 + 通用关键词，只有间接推测性综述）。
2. **执行器接地的 AZR 是被测最多的一个，且结果互相矛盾**：AZR 原文（Qwen2.5-7B base，k≤512）说大 k 不输 base；Chae 等（Coder-3B/7B，同一份 AZR 代码）说 base 在大 k 更好（不显著）。两者 base 模型、采样设置、k 范围不同；Chae 未写 k 上限，也未给数值，**无法判断谁对**。
3. **文档接地（INFUSER）是唯一一个报了“k≤128 全程高于 base”的自进化环路**，但只有曲线、单模型(8B)、单种子(未写)，BBEH 上交叉。
4. **有干净验证器的 STaR 环路（Strozzi）显示 pass@64 反超**，与 AZR 原文方向相反，但域是玩具 DSL。
5. 所以“self-play 环路是否超出 base 的 pass@k 天花板”：**证据只有 4 项、方向混杂、无人做多种子+CI 的受控比较，也没有人把 executor-grounded 与 self-consistency 放在同模型同基准下对比。**这是未被回答的问题（以我搜索的范围为限：Google 式关键词 + arXiv 抽查，不保证穷尽）。

---------------------------------------------------------------------
## Check 2 — 公开代码与 checkpoint

HF 大小以 safetensors 参数量给出（BF16 ≈ 2 字节/参数）。“逐轮”= 每个迭代/每轮的 questioner(proposer) 与 solver 分别发布。

| 工作 | 代码 | 权重 | 逐轮 questioner/solver |
|---|---|---|---|
| **R-Zero** | github.com/Chengsong-Huang/R-Zero（870★，最近推送 2026-02-04）。README：checkpoint 与数据存到本地 STORAGE_PATH，数据集可推 HF | **官方模型：未找到**（HF 按 Chengsong/R-Zero 搜不到作者仓库）。第三方复现：`KULIANLEN/rzero_solver_v1..v5`（4.41B 参数，疑为 Qwen3-4B-Base，无 model card，来源未核对）；`Kashiwahorito/r-zero-qwen3-merged`（1.72B，非官方）；数据集 `wyu1/r_zero`（R-Few 作者） | 官方：无。README 称训练每 15 步存一个 ckpt，需自训 |
| **AZR** | github.com/LeapLabTHU/Absolute-Zero-Reasoner（1936★） | **官方**：`andrewzh/Absolute_Zero_Reasoner-Coder-3b`(3.09B)、`-Coder-7b`(7.62B)、`-Coder-14b`(14.77B)；`andrewzh2/Absolute_Zero_Reasoner-Base-7b`(7.62B)、`-Base-14b`(14.77B)。基座 Qwen2.5-Coder / Qwen2.5（model card 未写 base_model，由论文推得）。另有 W&B 日志 | 单模型（proposer=solver），每个规模只有一个最终 ckpt；中间步骤：论文未说，HF 仓库只有 main 分支（refs 查过） |
| **Agent0** | github.com/aiming-lab/Agent0（1295★，最近 2026-07-10）；README 称 11/29/2025 开源 | 文本 Agent0（Qwen3-4B/8B-Base）：**官方 HF 权重未找到**。仅有 `JiaaqiLiu/Agent0-VL`（8.29B，Agent0-VL 视觉变体；是否官方未核对） | 论文有逐迭代表(iter1–3)，但无逐轮权重 |
| **SPADE** (2608.19197) | github.com/spade-rl/spade（132★，2026-11-17，MIT） | **官方**：`spade-rl/SPADE-Qwen3-4B-Games`（4.02B，基 Qwen3-4B-Instruct-2507）、`-8B-Games`（8.19B，基 Qwen3-8B）、`-30B-A3B-Games`（30.5B，基 Qwen3-30B-A3B-Instruct-2507），Apache-2.0；另有 ToolUse 版本；环境池、grounding 语料数据集 | 只有最终 ckpt；designer(proposer)与 agent 为同一模型的两个角色，没有单独发布设计者/逐轮权重。注意基座是 Instruct，非 base |
| **INFUSER** (2606.09052) | github.com/FFishy-git/INFUSER（代码 only） | **官方**（`Siyuc`）：`INFUSER-Qwen3-4B-base`（4.41B，基 Qwen3-4B-Base，MIT）、`INFUSER-Qwen3-8B-base`（8.19B）、`INFUSER-rlvr-Qwen3-8B-base`（8.19B）；数据 `Siyuc/infuser_train`、`INFUSER-Qwen3-8B-base-artifacts`（8B 训练产物，用于生成器质量评估） | 只有“按验证协议选出的 solver ckpt”；生成器权重与逐轮 ckpt 未发布（README 仅列 solver）。`Siyuc/converted_qwen3_100800`、`qwen35-4b-synthetic-qa-grpo-step40` 等为其他仓库，未核对关联 |
| **R-Quest** (2610.04299) | 论文页有“Project Page / Code”图标，但 arXiv 页与 PDF 内可提取链接只有 arxiv 自身；**代码仓库未核实** | `jinyuan222/R-Quest-Qwen3-4B-Validity-RL`（4.41B，基 Qwen3-4B-Base，标 arxiv:2610.04299，Apache-2.0），是“validity RL 初始化 solver”，不是最终 R-Quest 迭代产物；数据 `jinyuan222/R-Quest-Validity-RL` | **疑似可得但来源未核实**：同账号的 `qwen3_4b_fullrun_authorsettings_questioner_v1..v5` 与 `..._solver_v1..v5`（verl 格式，含 global_step_*/actor/huggingface/*.safetensors，solver 每个含 step10/15/20 等；questioner 含 step5/1006）。无 model card，名称像 R-Zero “author settings” 复现，**未核对是 R-Zero 复现还是 R-Quest 自己的轮次 ckpt** |
| **Selection Is Not Learning (EvoHeir)** 2610.22029 | **未找到**（arXiv 页无链接；GitHub 搜 EvoHeir/HeirCommit 无结果） | 未找到。论文设置：Qwen3-4B/8B-Base、OLMo-3-7B、Gemma-4-E4B-it，10 轮×3 种子，每轮评估“实际继承的 learner”，说明他们内部有逐轮 ckpt，但**未公开** | 未公开 |
| **CompassPlay** 2609.32228 | `github.com/SophiaPx/compassplay-code`（官方，2026-10-29；README：每 5 步存 ckpt，需自行 merge） | HF 未找到；arXiv 页无链接 | 无（代码可自训，Qwen2.5-Coder-7B 同模型分 proposer/solver 角色） |
| **SPIRAL** (2506.24119) | github.com/Spiral-RL/SPIRAL | **官方**（`spiral-rl`）：`Spiral-Qwen3-4B`(4.02B，基 Qwen3-4B-Base)、`Spiral-Qwen3-{4B,8B}-Multi-Env`、`Spiral-Llama3-8B-Multi-Env`(8.03B)、`Spiral-Octothinker-8B-Multi-Env`、`Spiral-DeepSeek-R1-Distill-Qwen-7B`(7.62B，基 R1-Distill-7B) | 论文用 step 0/128/400 做模式分析，未说明发布。同组织另有 `qwen3-4b/8b/30b-a3b-...-iter15..399`（每 16 步一个）逐步 ckpt，但命名为 `rlve-official16` / `games-blend`，是后续 RLVE/游戏混合训练，**是否为 SPIRAL 论文 ckpt 未核对**；且只有单一 policy，无 questioner |
| **SPICE** (2510.24684) | **未找到官方代码**（论文称评估代码和 prompts “将发布”；基于 Oat 框架） | 无官方权重（`dv347/qwen3-*_spice-*` 是第三方复现，未核对） | 无 |

### 总结
- 官方权重齐全且大小从 3B 到 30B 的：AZR、SPADE、SPIRAL、INFUSER。
- **没有任何一项经核实地发布了“逐轮 + questioner 与 solver 分开”的官方权重**。最接近：`jinyuan222/qwen3_4b_fullrun_authorsettings_*`（questioner 与 solver 分开，多个版本，但提供者与口径未核实）。R-Zero、Agent0、SPICE 官方不放权重，需要自训。
- 第三方复现的 R-Zero solver（KULIANLEN v1..v5）只有 solver。
- 以上 HF 搜索按名称/作者做，可能漏掉改名或私有仓库；Agent0、R-Quest、CompassPlay、SPICE 的“未找到”只代表我按名称搜不到。
