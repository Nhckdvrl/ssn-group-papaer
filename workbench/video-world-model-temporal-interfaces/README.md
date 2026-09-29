# Video World Model Temporal Interfaces — Workbench

**Status: exploratory workbench — not a candidate.**

**Venue-scale status: ACTIVE SURVIVOR (conditional, 2026-09-29 audit).**

Current scope ladder:

> chunk-onset control deafness in several open interactive world models  
> → positional non-equivalence introduced by chunked causal generation / causalization  
> → a general control-interface limitation of fast chunk-autoregressive video world models, with implications for how fine-grained actions should be represented, trained, and served.

This ladder is currently supported better than the other workbenches because the effect already survives multiple independent systems/action interfaces and has causal controls (teacher/student, grid shift, VAE negative control, per-frame negative control, overlap recovery). It remains active only if the broader second/third levels survive.

**Hard ceiling gate:** before paper promotion, require (i) broader system/statistical coverage, (ii) a real downstream/interactive consequence beyond synthetic pulses, (iii) a unified mechanism or sharply bounded structural explanation, and (iv) a repair validated on at least two systems without unacceptable quality/cost regression. If these fail, demote rather than write a narrow “chunk-first bug” paper.

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
| E19 基线：已发布 DMD 学生（5 个提示词） | 单步转动保留率：效果落在**块第一个潜变量**（第 3/7/11 步）0.04–0.15；块内 0.33–1.54，且 1.5° 明显低于 3°（死区）。**细调跟踪**（12 条轨迹，47 次 1.5–3° 细调，36% 落在块边界）：5 秒后朝向平均误差 **2.9°**；落在块边界的孤立细调生效率 0.006。 |
| E20 推理时补救（已发布 DMD，5 个提示词） | 块边界单步 0.08/0.03；**推迟一个潜变量** 0.46/0.73（部分恢复，+0.25 秒延迟）；**摊开为 4×0.75°** 0.26–0.33（落入死区，更差）。→ 推理时调度不能解决，需要训练端修复。 |
| E18 结果（DMD 继续训练 300 步 ≈ 60 次生成器更新，5 个提示词） | 块首单步保留率：事件组 0.10/0.06/0.05，对照组 0.13/0.05/0.04，原模型 0.11/0.09/0.04 → **无变化**。DMD 阶段剂量太小（生成器每 5 步才更新一次），不能说明"训练无法修复"，只记为无效尝试。 |
| **训练轨迹的相位统计**（官方 19,823 条 + 官方评测基准） | 全部 36,164 次速度切换都发生在第 5/9/13 个潜变量 = **块内第 2 个位置**；**跨块边界的速度变化 0 次**。原因是"差一格"：轨迹分段按 4 的倍数从第 1 个潜变量数起（第 0 个是首帧），而生成块从第 0 个潜变量数起。官方评测轨迹（`a*4,w*8,s*7` 等）同样只在块内第 2 位切换，所以这个盲区在他们的训练和评测里都看不到。MG2 官方脚本同样以 12 帧从第 1 帧起重复动作 → 切换也只落在 3 潜变量块的第 2 位（社区 issue #57 已问训练数据是否如此，官方未答）。 |
| E22 块网格整体平移一格（DMD，5 个提示词；用 1 个干净前缀潜变量让块变成 [1-4],[5-8]…） | 不平移：块首（k=3/7/11）0.16/0.18/0.10 px/°（块内 0.54–0.98）；平移后块首变成 k=4/8/12：**0.06/0.10/0.08**，原来的块首 k=3/11 恢复到 0.69/0.71；同一个 k=12 从 1.75 → 0.08。→ **丢失跟着块位置走，不跟绝对时间走。** |
| ~~E24 推理时给缓存加噪~~ | **无效实验**：minWM 的 Wan 适配器刷新缓存时把时间步固定为 0，`context_noise` 只对 HY 分支生效，三档结果逐位相同。未得出任何结论（之前"加噪无效"的写法已撤回）。 |
| **E25 HY-WorldPlay 蒸馏 AR 模型**（腾讯，HunyuanVideo 8B，4 潜变量一块；训练数据过半是人类游戏录像，动作相位随机；每个潜变量另有显式离散动作标签；3 个场景，16 潜变量） | 块内单步 3° 转动渲染得干净且时间精确（第 2/3/4 位 2.5/4.7/4.2 px/°，转动正好落在指令潜变量上）；**块首 −0.03 px/°（与不转向逐帧几乎相同）**。显式"右转"标签就在块首潜变量上、代码切片正确、训练数据相位随机——仍然完全失聪。另见 E25c：最后一块的"整块失效"是第 2 位随机失效所致，不是最后一块特殊。 |
| **E25b WorldPlay 阶跃（持续转动 3°/潜变量，3 个场景）** | 起步落在**块首**（第 4 个潜变量）：该潜变量只转 **1.59**（稳态≈10.5，约 15%），从下一个潜变量起正常；起步落在块内第 2/3 位：立即 8.5/10.4。持续转动中后续块首（第 8/12 个）11.6/11.1，**不停顿**。与 minWM（E09：块首起步 0.07，之后正常）一致 → 共同规则：**运动不能在块接缝处开始**；接缝处已在进行的运动照常延续；接缝处的停止 WorldPlay 服从、minWM 多转一步。流式交互中新动作从下一块的第一个潜变量生效 → **每次起步都丢第一个潜变量**（WorldPlay≈0.17 s，minWM≈0.25 s）。 |
| E25c WorldPlay 32 潜变量长视频（2 个场景 × 7 个块，看**指令所在潜变量**的响应；长视频后段有漂移，全程积分不可靠） | 块首：14/14 ≈0（−0.01/−0.02）；**块内第 2 位：约 6/14 ≈0，其余 2–8.7（随机失效）**；第 3 位：14/14 有响应（3.7–9.0）。→ 16 潜变量里"最后一块整块失效"其实是 k=11（块首）+ k=12（第 2 位）同时失效，**不是最后一块特殊**；WorldPlay 的失聪是**分级**的：离接缝越近越聋。 |
| **E23 相位随机化微调（第 250 步，4 个提示词）** | 同一批官方视频按不同起点裁剪重编码，从已发布 TF 模型继续训练（lr 5e-6，每步 2 样本）。块首/块内：原模型 0.135/0.82，对照组 0.133/1.03，**相位随机组 0.30/3.2（比例 0.09）**。相位随机化让整体控制变强 4 倍，但**块首盲区没有被修复**（比例反而从 0.16 降到 0.09）。⚠️ 校对：250 步×2 样本≈500 个样本、n=4 提示词，剂量和统计量都不足以得出"不是数据相位问题"，只能记为"此剂量下未修复"。第 500 步评测进行中。 |
| **E27 接缝重叠推理**（已发布 DMD，4 个提示词；每块从上一块最后一个保留潜变量开始、重新生成后丢弃，新潜变量永不做块首，计算 ×4/3） | 原块首位置（k=3/7/11）：标准推理 **0.12** → 重叠推理 **1.02** px/°；其余位置 0.78–1.13（标准 1.2–1.9）。→ **位置依赖消失**：失聪只取决于"是不是生成块的第一个潜变量"，与绝对时间、训练数据无关。可作强基线（非新方法）。 |
| E23 第 500 步（相位组，4 个提示词，≈1000 样本） | 第 2/3 块块首 k=7/11：0.10/0.04 px/°，块内 2.4–2.8 → 比例≈0.03（第 250 步 0.09）。第一块出现负值（同 E22 的"第一块无对比"问题），不计。→ **加倍剂量仍未修复**，仍按"此剂量下无效"表述。 |
| **E29 真人按键回放**（VPT 31 名玩家的 a/d 按键时序，锁存到潜变量、3°/潜变量；minWM DMD 标准推理，40 个 5 秒窗口×2 提示词，72 次按键） | 真人按键时长：42–55% ≤0.25 s（≤1 潜变量），75–94% 短于一个块；鼠标转视角 70% ≤0.25 s。回放：**起步落在接缝**的按键生效 0.56、丢失（<0.3）**55%**；其余按键 0.87、丢失 27%；**单潜变量点按落在接缝 −0.06（全丢，n=6）**，不在接缝 0.62（n=4）。每窗口最终朝向误差 4.7°。另有与位置无关的"短按死区"（非接缝也丢 27%），需分开报告。**重叠推理（E27）对照**：接缝起步按键生效 0.56→**0.91**、丢失 55%→**10%**；其余 0.87→0.93、丢失 27%→17%；单潜变量点按落在接缝 −0.06→0.55；每窗口朝向误差 4.72°→**3.54°（−25%）**；增益不变（2.32/2.33 px/°）。→ minWM 上"真实按键时序下有损失 + 推理端可修复"成立；WorldPlay 回放排队中。 |
| ~~E26 教师强制单步探针~~（`mwm_tf_probe.py`，真实片段+真实历史，块首起加 3° 偏航，单次前向看 x₀） | **方法无效**：σ=0.9/0.5/0.2 下 x₀ 预测对位姿的相对变化只有 0.3–1%（3° 转动应≈2.75 个潜变量像素的平移），高噪声单步 x₀ 太模糊，体现不了转动；不能用于机制判断。 |

### 当前判断（2026-09-29 中午）
- **现象（三个系统确认）**：因果分块世界模型对"效果落在生成块第一个潜变量上"的控制变化几乎完全失聪（minWM 保留约 5–10%，MG2 1–16%），块内位置正常；双向老师和逐帧生成的 Oasis 没有这个问题。E22 证明它跟着块网格走。
- **E25 推翻了"数据相位"作为主要解释**：WorldPlay 的训练数据相位随机、块首还有显式动作标签，照样对块首事件完全失聪。三个独立系统（Skywork MG2、minWM、腾讯 WorldPlay）、三种动作接口（逐帧鼠标窗口 / 纯 PRoPE 位姿 / 位姿+离散标签）、两类训练数据都一样 → **更像是分块因果生成本身的结构性问题**。minWM 的相位锁死数据可能只是加重因素。
- **校对备注（2026-09-29，对照 `results/summary/*.json`）**：
  1. E25 的"第 2 位 2.5 px/°"混入了最后一块（k=12，≈0）；只算前三块时第 2 位是 3.77 px/°。最后一块整块无响应的原因未查明，在查清是模型行为还是适配器/管线问题（动作或位姿截断）之前，E25 只能引用前三块。
  2. E22 不平移时**第一个块**（k=3–6）块内响应也≈0（0.17/0.09/0.00，且提示词间正负号乱跳），块首/块内对比只在第 2、3 块成立；块首数值本身很稳（每个提示词 0.05–0.15）。
  3. E23"不是数据相位问题"属于过度推断（见 E23 行）；E25 的证据支持"结构性"，但同样可以解释为"随机相位数据里仅靠跨块证据的事件仍然极少"。要区分两者，需要 E26（教师强制单步探针）或"每个块内位置上动作对训练损失的敏感度"这类直接测量。
  4. 目前多数结论 n=3–5 个提示词、单种子，只有一种读数（相位相关水平位移、只测偏航）。投稿前需要扩大样本、换独立读数（位姿估计）、覆盖平移和离散按键。
  5. ~~E26/E27 尚无结果记录~~ → 已补：E26 方法无效（单步 x₀ 不灵敏）；E27 块缝重叠推理把原块首位置从 0.12 恢复到 1.02 px/°（见 E27 行），画质尚未评测。
  - 完整的 CVPR 可行性评估见 [`CVPR_ASSESSMENT.md`](CVPR_ASSESSMENT.md)。
- **E23（进行中）** 仍有意义：它检验"让数据里出现跨块变化"能否缓解；若也不能，结构性结论更强，下一步要找结构机制（例如块首潜变量的去噪过程几乎完全由干净缓存决定）。
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
