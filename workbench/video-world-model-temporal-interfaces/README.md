# Video World Model Temporal Interfaces — Workbench

**Status: exploratory workbench — not a candidate.**

## 进度页（中文，随每次里程碑更新）

**最后更新：2026-09-29**

### 基线（已跑通）
- **Matrix-Game 2.0**（Skywork，开源 1.3B 交互世界模型，蒸馏学生 `base_distilled_model`，universal 场景）：Wan2.1 VAE（4× 时间压缩、首帧单独编码）、逐帧键鼠动作、每块 3 个潜变量（12 帧）、局部注意力 6 个潜变量、3 步去噪、352×640。官方代码 `71c3cd7`，A100 上 45 帧约 11 秒。同一噪声下重复生成**逐位一致**，可以做配对反事实。
- 已下载待用：Wan2.1-T2V-1.3B、Causal-Forcing 全阶段权重（AR 扩散 → 因果 ODE/CD → DMD，逐帧/分块两套）。

### 时间接口的实际实现（读代码得到）
- 第 i 个潜变量对应第 4i−3…4i 帧；生成它时看到第 4i−12…4i−1 帧的逐帧动作（约定：第 t 帧动作决定 t→t+1 的变化）。
- 官方测试脚本只在第 1、13、25… 帧切换动作（与 12 帧分块对齐）；交互模式下一个动作填满整块，动作最细每 12 帧才能改一次。
- 蒸馏学生只有前 15 个 Transformer 块带动作模块；基础模型 30 块都有，且是双向整段（57 帧）生成。

### 实验结果
| 实验 | 结论 |
|---|---|
| E01 动作起点逐帧推移（学生，配对反事实，3 图×2 种子×起点 1–24） | **阶跃起动逐帧精确**：视角延迟 1 帧（129/144），前进 1–2 帧；与相位无关；动作前无同向运动。 |
| E02 Wan2.1 VAE 相位（DAVIS 87 段） | 组内第 3 帧重建误差低 25%；**IV-VAE（CVPR 2025）已报告**，不作为新问题。 |
| E06 VAE 单帧跳动（6 段真实画面，静止/匀速平移，跳 4/8 像素） | 单帧跳动在 4 个相位上都保留 89–103%。**VAE 能承载亚潜变量运动，不是瓶颈。** |
| E04 单帧脉冲（学生，9 图×2 种子×起点 9–32×幅度 0.1/0.2，每格 n=108） | 幅度 0.1：相位 0/1/3 转动 2.3–2.9，**相位 2 只有 0.44**——先转 +2.66 下一帧转回 −1.84（**回弹**）。幅度 0.2 时相位 2 恢复、相位 3 最低：映射非线性且周期时变。 |
| E05 正弦输入（学生，周期 3–24 帧） | 周期 ≥8 帧增益≈1；5–6 帧衰减到 0.63–0.85；**周期 3–4 帧响应≈0**。输出在 0.25±f（潜变量频率）处有强边带（周期 8 时达主峰 38%）。→ **有效控制带宽≈潜变量奈奎斯特频率，且系统以 4 帧为周期时变。** |
| E07 同一脉冲测试在**双向多步老师**上（6 图，n=48/相位） | 老师 3.69/3.54/**3.48**/2.71（学生 2.38/2.90/**0.44**/2.25）；老师在所有相位都把运动画在正确帧上、**无回弹**。→ 回弹是蒸馏引入的。 |
| E08 老师的正弦响应 | 老师**同样**压掉周期 3–4 帧（增益 0.03/0.005），周期 5–6 帧比学生好（3.97/4.34 vs 2.85/3.83）。 |
| E06b VAE 抖动（净位移为 0 的来回平移，周期 3–12 帧） | VAE 保留 0.90–1.03。→ **快速抖动消失不是 VAE 的问题，而是生成器/动作接口：模型只对每个潜变量内动作的净量做出响应。** |
| E10 窗口屏蔽定位（学生，4 相位×5 掩码×3 图；全屏蔽=参考、不屏蔽=E04 均逐位一致） | 所有响应（包括回弹）都由脉冲所在"自身帧"窗口位置（8–11）驱动；把脉冲从后续潜变量的历史位置（0–7）抹掉几乎无影响。→ **学生不读历史动作**；回弹=下一潜变量继承上一潜变量的"整体状态"而撤销末帧位移。老师侧同样实验（E11）运行中。 |
| E11 窗口屏蔽在**老师**上（2 图，全屏蔽=参考逐位一致） | 相位 2 脉冲：老师 1.51 → **只让下一个潜变量看不到该历史动作 → 0.36（−76%）**，≈学生的 0.25；其他相位同样屏蔽只降 15–25%。→ **机制坐实**：单元末尾的事件需要下一个单元从"历史动作"读取来延续位移；老师这样做，蒸馏学生不读历史 → 画出后被撤销；在老师上切断这条通路即复现学生的失败。 |
| E09 minWM（Wan 1.3B，按潜变量给相机位姿，每块 4 潜变量；5 个阶段，部分完成） | 所有阶段（含双向老师）都跟不上周期 2–4 潜变量的摆动（老师平滑先验更强）；三个因果学生（ODE/CD/DMD）都在同一位置丢失单步脉冲：第 6 步 0.5–1.3，**第 7 步 0.01–0.05**——块尺度上的同类"单元边界事件丢失"。 |
| 真实人类操作统计（VPT Minecraft 20Hz，5 段） | 视角动作功率 16% 在 4× 潜变量奈奎斯特频率之上；**38% 的视角转动片段短于 4 帧**（27% ≤2 帧）。 |
| E04 重分析：按"效果落在块内哪个潜变量" | 学生（幅度 0.1，每格 n=36）：落在**块内第一个**潜变量 0.01–0.16（**几乎全丢**），中间 0.26–3.5，**最后一个** 5.0–6.5（最后一帧除外 0.78）。→ 之前的"相位效应"是块结构的混合。机制：学生只读"自身帧"动作 + 块内 3 个潜变量联合去噪 → 块内后续潜变量"不知道"事件 → 多数派抹掉事件；事件在块尾则被画出并经缓存传下去。 |
| E09 minWM 全阶段（逐潜变量响应核） | 双向老师：第 6/7 步单步转动都渲染（0.97/0.95）；**第一个因果阶段（教师强制 AR 扩散）起**，落在新块第一个潜变量的位姿变化被整个丢掉（0.01–0.07），块内的变化被"抹"到整个块上。→ 问题出在**因果化**，蒸馏继承。匀速转动时块边界不丢（块内有对比）。 |
| E12 Open-Oasis 500M（逐帧 ViT 分词、无时间压缩，生成单元=1 帧） | 单帧脉冲在**每一帧**都正好在该帧转 9.2–9.4 像素，无扩散无回弹；正弦周期 3–12 帧增益平坦（27–33 ≈ 稳态 31）。→ **生成单元=1 帧时控制是理想 LTI、全带宽**（阴性对照，架构不同，仅作存在性证明）。 |
| E13 真实人类视角输入（VPT 片段，老师 vs 学生，各 24 段） | 相对理想线性模型 R² 学生 0.65 / 老师 0.68，最终朝向误差 6.4 / 4.4 像素。→ **连续操作下损失很小**；问题集中在孤立短事件。 |
| E15 minWM 预测性检验（CD/DMD，5 个提示词） | 块边界单步转动（第 7、11 步）被丢 0.15–0.48 像素；块内（第 5、8、9 步）渲染 3–24 像素 ✓。拆成"边界 1.5°+块内 1.5°"只剩约 1 像素 → 还有**幅度死区**（MG2 上 0.05 幅度脉冲同样≈0）。 |
| E17 MG2 学生块大小改为 1（推理时） | **无效**：块大小=1 时连持续阶跃都几乎无响应（分布外），不能作为机制证据。 |
| minWM 训练轨迹统计（官方 19,823 条） | 分段长度只有 4/7/8/11 个潜变量步，**从没有 1–3 步的短事件**；同一数据下双向老师能渲染短事件，因果模型不能 → 因果训练学到"块内对比 + 视觉惯性"的捷径。 |
| E18 修复实验（进行中） | minWM DMD 阶段对视频不需要数据，只用提示词+轨迹：从已发布 DMD 继续 400 步，**事件组**（50% 轨迹叠加 1–2 步 ±1.5/3/6° 短转动，571 个事件中 118 个落在块边界） vs **对照组**（官方原分布，其余完全相同）。 |

### 当前判断（2026-09-29 凌晨）
- 候选问题正在成形：**"少步因果蒸馏像一个作用在控制信号上的时间低通滤波器"**——学生保住慢变控制，丢掉老师具有的高频/亚潜变量控制，并出现相位依赖的回弹。
- 已排除：VAE（E06）、测量伪影（配对反事实 + 两种运动估计器一致 + 老师对照）。
- 近邻边界（持续核对）：CMD（2608.13391，老师–学生上下文错配，改善随时间变化的相机控制，但只到潜变量/块粒度，未做频率/相位分析）；Causal Forcing / DyMD（蒸馏后运动**幅度**下降）；ActionSplice（块内修改动作的交互延迟）；SCOPE（FPS 高频控制，空间注入视角）。
- 统一机制（当前最强候选）：**因果化后的世界模型只从"当前生成单元内部的对比"读取控制；只能通过"相对历史"表达的控制（历史动作 / 与缓存块的相对位姿）被忽略**，块内联合去噪再把"少数派"事件抹掉。两个系统、两种接口、两种尺度一致；Oasis（单元=1 帧）无此问题。弱点：连续真实输入下影响小。
- 旧表述：(1) 老师本身有低通平滑先验（MG2 到潜变量频率，minWM 更低）；(2) **因果分块学生在生成单元边界丢失短事件**——两个独立系统、两种动作接口（逐帧鼠标/逐潜变量位姿）、两种尺度（潜变量/块）。机制（MG2）：学生不读历史动作；老师上切断即复现。
- 下一步：真实人类输入下老师 vs 学生的朝向漂移（E13，排队中）；Oasis（生成单元=1 帧）对照（E12，运行中）；**推理时相位感知的动作预补偿**（从机制直接推出的最小修复）。

---

This workbench studies how modern video generators and interactive/world models represent, compress, align, and transmit **time** across their major interfaces.

The motivating literature contains several related pressures:
- video tokenizers / VAEs often compress multiple raw frames into one latent step;
- controllable world models may receive actions, camera motion, contacts, or state changes at a finer rate than their latent video stream;
- causalization, streaming inference, few-step distillation, and long rollout can change what temporal information remains available;
- some recent systems respond by changing temporal compression, preserving higher-rate control signals, or adding separate fine-timescale pathways.

These facts justify studying the territory. They do **not** establish that temporal compression is the bottleneck, that a phase effect exists, or that any particular interface needs a new method.

## Execution ownership

The default executor of this workbench is the **local research agent**.

Once the territory is admitted to `workbench/`, the agent should not behave like a consultant that proposes one experiment and waits for a human to choose the next step. It should carry the research loop forward autonomously:

> reproduce → inspect → perturb → analyze → search nearest prior → update the working explanation → choose the next highest-information experiment → repeat

The agent is expected to:
- read papers, repositories, issues, appendices, and current code rather than rely on summaries;
- clone and run strong baselines;
- diagnose implementation details;
- design and execute the next experiment itself;
- use failures as gradients rather than stopping after one null result;
- continuously check whether an emerging observation is already owned by prior work;
- strengthen or replace the working question when evidence changes;
- keep the repository state current with code, results, and concise conclusions;
- continue until either a genuinely defensible novel problem/idea emerges or the territory is exhausted enough to archive/kill.

Human input is for occasional taste calibration, resource constraints, or new insight—not per-experiment approval.

## Research target

The purpose of exploration is not exploration for its own sake.

The workbench should actively search for a **real, reproducible, novel research object** that can eventually crystallize into a candidate. A useful endpoint may be:
- a previously unrecognized failure/bottleneck in a strong baseline;
- a surprising dependency exposed by a simple perturbation;
- a mistaken assumption shared by current methods;
- a representation/interface limitation with downstream consequence;
- a strong-baseline result that invalidates part of an existing narrative;
- a minimal intervention that becomes natural only after the bottleneck is established.

Novelty must be checked against current nearest prior continuously, not only after a result looks good.

The agent should not stop merely because the initial temporal-compression intuition fails. It should use that failure to redirect within the broader temporal-interface territory, unless accumulated evidence shows the territory itself is no longer promising.

## Baseline residency

Begin from strong open artifacts rather than from a new architecture.

The first task is to become fluent in a small set of practical video/world-model stacks that fit a single node. Candidate families include:
- open causal video VAEs / tokenizers;
- Wan-style open video generation stacks;
- small/open interactive or action-conditioned world models;
- models with explicit camera/action conditioning and published inference code;
- where useful, paired teacher / causal / distilled checkpoints from the same lineage.

Before proposing a research claim:
- reproduce the strongest practical baseline we can run;
- map the exact temporal interfaces in code: raw FPS, latent stride, first-frame handling, padding, causal context, action grouping, camera conditioning, rollout chunking, and any distillation/streaming conversion;
- record quality, controllability, latency, memory, and failure slices;
- distinguish tokenizer artifacts from downstream model behavior.

No foundation-model pretraining is required or authorized at the beginning.

## Exploration space

The workbench should explore several axes and let the important object emerge from experiments.

Potential axes include:
- **temporal representation:** what information changes when time is compressed or tokenized differently;
- **alignment:** how frames, latents, actions, camera trajectories, and state transitions are synchronized;
- **causality / streaming:** what changes when a bidirectional or teacher-forced system becomes causal or online;
- **control resolution:** whether coarse latent steps and fine-grained control signals interact cleanly;
- **event timescale:** whether short events, contacts, reversals, or fast motion behave differently from slow dynamics;
- **boundary / phase effects:** whether temporal chunk boundaries matter after strong implementation controls;
- **stage effects:** tokenizer vs generator vs causalization vs distillation vs rollout;
- **compensation:** whether a downstream model repairs information losses visible at an earlier stage;
- **efficiency tradeoffs:** which temporal simplifications actually buy useful speed and which silently remove control-relevant information.

“Temporal control bandwidth” is therefore one **possible diagnostic lens**, not the registered paper question.

## Research discipline

Do not:
- assume a phase/bandwidth phenomenon before measuring it;
- build the workbench around one synthetic pulse experiment;
- train a new video foundation model to make the question exist;
- turn the project into a generic long-video-memory, action-following, or VAE leaderboard;
- propose a module/loss before a stable bottleneck survives strong baselines;
- protect the initial temporal-compression story if another interface becomes more load-bearing.

Prefer:
- frozen-model diagnostics first;
- matched comparisons within the same model lineage;
- small perturbations that reveal hidden dependencies;
- failures that change which interface should be studied next;
- lightweight adapters / conditioning changes only after an actionable bottleneck is established.

## Compute boundary

The workbench must remain practical on one node:
- up to 4×A100 80GB, or
- up to 4×RTX PRO 6000 96GB.

The two available nodes cannot be assumed to communicate.

Therefore:
- VAE/tokenizer analysis and frozen inference are preferred early;
- repeated sweeps should favor roughly 1B–5B open backbones when possible;
- small LoRA / adapter / conditioning experiments are acceptable;
- multi-node foundation-model pretraining is out of scope.

## What would justify promotion

Remain exploratory until the workbench produces a simpler scientific object than the one we started with.

Promotion would require something like:
- a reproducible temporal/interface dependency that survives a strong baseline;
- evidence that it is not merely one implementation bug or one model family;
- a clear downstream consequence or changed understanding;
- a nearest-prior boundary that cannot be compressed into “already known”;
- a realistic confirmation path under the single-node compute budget.

It is fully acceptable for this workbench to end as a negative result or a reusable map of temporal interfaces.

## Starting literature / artifact audit

Before running substantial experiments, re-verify the latest primary papers, code, checkpoint availability, and exact licenses for candidate baselines. In particular, audit recent work on:
- causal / temporally compressed video VAEs;
- open video generation stacks;
- action- and camera-conditioned world models;
- causal / streaming / few-step world-model conversion;
- adaptive temporal tokenization or frame-rate allocation;
- embodied video tokenizers.

Do not treat any one of these lineages as the final paper identity.
