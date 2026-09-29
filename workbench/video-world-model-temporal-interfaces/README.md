# Video World Model Temporal Interfaces — Workbench

**Status: exploratory workbench — not a candidate.**

**Venue-scale status: ACTIVE SURVIVOR (conditional; phase-1 gates reviewed 2026-09-29 evening).**

Current scope ladder:

> chunk-onset control deafness in several open interactive world models  
> → positional non-equivalence introduced by chunked causal generation / causalization  
> → a general control-interface limitation of fast chunk-autoregressive video world models, with implications for how fine-grained actions should be represented, trained, and served.

**Hard ceiling gate:** before paper promotion, require (i) broader system/statistical coverage, (ii) a real downstream/interactive consequence beyond synthetic pulses, (iii) a unified mechanism or sharply bounded structural explanation, and (iv) a repair validated on at least two systems without unacceptable quality/cost regression. If these fail, demote rather than write a narrow "chunk-first bug" paper.

Phase-1 outcome (2026-09-29): (ii) **provisionally passed on two systems** (human key-press replay, minWM + HY-WorldPlay) — ⚠️ the replay windows confound seam position with press duration (see 校对备注·第二轮), so the seam-vs-other loss rates must be re-measured with phase-balanced replay; (iv) **repair passed on two systems for control**, quality/cost not yet measured; (iii) **half**: the trigger is established (chunk↔context seam, arises at causalization in both lineages), the training-side cause is not (two training fixes failed at tested doses); (i) still thin (n = 3–5 scenes, one seed, one readout). Full feasibility review: [`CVPR_ASSESSMENT.md`](CVPR_ASSESSMENT.md).

---

## 进度页（中文，随每次里程碑更新）

**最后更新：2026-09-29 晚**

### 一句话

分块因果生成的交互视频世界模型，对"应在一个生成块的第一个潜变量上开始生效"的控制变化几乎完全不响应（**块首失聪**），块内其他位置正常。三个独立系统都有（Skywork MG2、minWM、腾讯 HY-WorldPlay），同谱系双向老师和逐帧生成的 Oasis 没有。触发条件是**新块与历史缓存/上下文之间的接缝**：接缝处的第一个潜变量沿用历史画面，运动不能在接缝处开始。真人按键时序下，落在接缝起步的按键会被丢掉；让接缝两侧是同一帧的推理方式（上下文锚定的块重叠）能在两个系统上恢复。

### 第一阶段结论（三个门槛）

| 门槛 | 结论 | 关键证据 |
|---|---|---|
| 一、真实影响 | **暂定通过（2 个系统）**；⚠️ 回放窗口把接缝位置和按键时长混在一起，需相位平衡重做（见下方校对备注·第二轮） | 真人按键 42–55% ≤1 个潜变量，75–94% 短于一个块；回放中接缝起步的按键 minWM 丢失 55%（其余 27%）、WorldPlay 丢失 25%（其余 **0%**）；单潜变量点按落在接缝两个系统都**全丢**。流式交互中每次起步都丢第一个潜变量。 |
| 二、跨系统修复 | **未通过（E31 修正）**：接缝点按能找回，但 minWM 只改善朝向 5%、WorldPlay 过度转动 24%；画质/代价未测 | 推理端块重叠：minWM 接缝起步丢失 55%→10%、朝向误差 −25%；WorldPlay（需"上下文锚定"）25%→0%、朝向误差 −28%，宽度 2 时失效 12/30→2/30。 |
| 三、统一机制 | **一半** | 已确立"触发条件"：两个谱系都在因果化阶段出现（蒸馏前已有）；接缝规则统一；重叠变体对比证明只有接缝两侧同一帧才不失聪。未确立"为何学成这样"：数据相位随机化（E23）和只对接缝加噪（E28）两种训练端修复在所试剂量下都无效。 |
| （统计覆盖） | **不足** | 多数结论 n=3–5 个场景、单种子、只测偏航、只有相位相关一种读数。 |

**建议：进入第二阶段**（约 3–4 周，见文末计划）。

**校对备注·第二轮（2026-09-29 夜，对照 `results/summary/*.json` 与脚本）**
1. **E29/E29b 选窗伪影（必须重做）**：`vpt_press_specs.py` 从左往右滑窗，第一次满足"最后一个按键在 n_lat−4 前结束"就接受 → 40 个窗口里 25 个（minWM）/ 27 个（WorldPlay）的最后一个按键**恰好结束在 n_lat−4**，于是起点完全由按键时长决定：单潜变量按键几乎必然落在接缝（minWM 5/7、WorldPlay 4/4），2 潜变量按键落在块内第 3 位（minWM 起点位置分布 12/6/7/24）。接缝组里单潜变量按键占 42%/40%，其余组只占 5%/0%。所以"接缝丢失 55% vs 27%""全部丢失都来自接缝起步"混入了按键时长（而 minWM 本身有与位置无关的短按死区）。重叠推理前后的**配对**比较仍有效。重做方法：窗口按固定时间步长选取，每个窗口再按 4 个相位偏移各回放一次（相位平衡），在同一个按键内比较接缝与非接缝。另：minWM 实际回放 27 个窗口 × 2 提示词（heading n=54），不是 40 个。
2. **朝向误差是自校准的**：`press_replay.py` 用每个条件自己的增益 g 换算角度；WorldPlay ctx 重叠的增益是 4.36 px/°，标准是 3.21（+36%，E25b 稳态约 3.5），可能过度转动，而自校准会把过度转动藏起来。"−25%/−28%"需要用统一标定或位姿估计（度）重算。
3. **E30 全位置计数**：ctx 宽度 1 块首 0/9 失效，但全部位置仍有 5/30 失效（k=6 2/3、k=12 3/3）；宽度 2 为 2/30。
4. **机制尚未跨系统统一**：同样的"重新生成式"重叠，在 minWM 上有效（E27，移位后的接缝 k=5/8/11 为 1.07/1.29/0.70，n=4），在 WorldPlay 上让盲区换位置（E30，同样位置 3/3 失效）。已核对 minWM 源码：时间 RoPE 由 `current_start` 计算，`local_attn_size=20` 覆盖整段，不是位置伪影。所以"块与上下文之间的位姿跳变即失聪"目前只在 WorldPlay 上成立，需要在 minWM 上跑同样的 regen/clamp/ctx 三种变体。
5. **"每次起步都丢第一个潜变量"只对位姿条件的模型成立**：MG2（逐帧速度/按键）阶跃起点在任何相位都逐帧精确（E01），它丢的是"只落在块首的脉冲"（块内多数派抹掉）。论文里要分开表述。

---

### A. 现象：三个系统 + 两个阴性对照

读数说明：配对反事实（同种子、同噪声），相位相关测水平位移，减去无动作参考。"px/°" = 每指令角度的画面位移。minWM 用"指令之后积分"，WorldPlay 用"指令所在潜变量 + 下一个"（WorldPlay 长视频后段有漂移，积分不可靠；minWM 会把转动抹到整个块，单潜变量读数太小）。

| 系统 | 块结构 | 块首 | 块内 | 编号 |
|---|---|---|---|---|
| **Matrix-Game 2.0**（Skywork，蒸馏学生，逐帧键鼠） | 3 潜变量/块 | 0.01–0.16 | 0.26–6.5（块尾最强） | E04 重分析 |
| **minWM**（Wan 1.3B，按潜变量给相机位姿，DMD 学生） | 4 潜变量/块 | 0.04–0.15（k=3/7/11） | 0.33–1.54 | E09、E15、E19 |
| **HY-WorldPlay**（腾讯 8B，蒸馏 AR，位姿 + 离散动作标签，训练数据过半为人类游戏录像） | 4 潜变量/块 | **−0.01，9/9 失效** | 2.8–5.7 | E25 |
| 阴性对照：MG2 双向老师 | 无块 | 相位 2 为 3.48（学生 0.44），无回弹 | — | E07、E11 |
| 阴性对照：minWM 双向 SFT | 无块 | 第 6/7 步 0.97/0.95 | — | E09 |
| 阴性对照：Open-Oasis 500M | 1 帧/单元 | 每一帧都 9.2–9.4 px，理想 LTI | — | E12 |

### B. 定位

| 实验 | 结论 |
|---|---|
| **E22 块网格平移一格**（minWM DMD，5 个提示词，1 个干净前缀潜变量） | 块首从 k=3/7/11（0.16/0.18/0.10）移到 k=4/8/12（**0.06/0.10/0.08**）；原块首 k=3/11 恢复到 0.69/0.71；同一个 k=12 从 1.75 → 0.08。**跟块走，不跟绝对时间走。**注意：不平移时第一块块内也≈0，对比只在第 2、3 块成立。 |
| **阶段定位** | minWM：双向 SFT 正常，**教师强制 AR 阶段起**块首失效，ODE/CD/DMD 继承（E09）。WorldPlay：**未蒸馏 AR** 块首 0.62、8/9 失效，蒸馏后 9/9（E25d）。→ 两个谱系都产生于**因果化**，蒸馏使其更彻底。 |
| **接缝规则（阶跃开/关）** | 起步落在块首：minWM 首个潜变量 0.07、WorldPlay 1.59（稳态≈10.5），之后正常；持续转动中后续块首**不停顿**；停止落在块首：WorldPlay 服从，minWM 多转一步（E09、E25b）。→ **运动不能在接缝处开始，已有运动照常延续。** |
| **分级失聪**（WorldPlay 32 潜变量，2 场景 × 7 块，E25c） | 块首 14/14 ≈0；块内第 2 位约 6/14 ≈0（随机失效）；第 3 位 14/14 有响应。16 潜变量里"最后一块整块失效"= 块首 + 第 2 位同时失效，**不是最后一块特殊**。→ 离接缝越近越聋。 |
| **重叠变体对比**（WorldPlay，E30） | 重叠位重新生成或只固定、但不放进上下文 → 盲区**换位置**（每个重叠块最后一个新潜变量在下一块成了接缝，8/18 失效）；重叠位同时放进上下文（接缝两侧同一帧）→ 失聪消失。→ 触发条件是**块与上下文之间的位姿跳变**。 |
| MG2 细节（E10/E11） | 学生只读"自身帧"动作窗口、不读历史动作；在老师上切断历史动作通路即复现学生的失败（1.51→0.36）。与"接缝处由缓存决定"一致。 |

### C. 真实影响

| 实验 | 结论 |
|---|---|
| **真人按键统计**（VPT，31 名玩家，1640 次按键 + 4153 段转视角） | a/d 键中位 0.30 s，45–48% ≤0.25 s（≤1 个 minWM 潜变量），93–94% ≤1 s（≤1 个块）；w 键 42% ≤0.25 s；鼠标转视角 **70% ≤0.25 s**。 |
| **E29 minWM 回放**（真人 a/d 按键锁存到潜变量、3°/潜变量；DMD；40 个 5 秒窗口 × 2 提示词，72 次按键） | 标准：接缝起步生效 0.56、**丢失 55%**；其余 0.87、丢失 27%（另有与位置无关的短按死区）；单潜变量点按落在接缝 **−0.06（6/6 全丢）**；朝向误差 4.72°。重叠推理：接缝起步 **0.91、丢失 10%**；单潜变量接缝点按 0.55；朝向误差 **3.54°（−25%）**；增益不变。 |
| ⚠️ E29/E29b 的"接缝 vs 其余"对比 | 混入了按键时长（选窗伪影，单潜变量按键几乎都被放在接缝上）；只有同一按键在标准/重叠推理之间的配对比较可以直接引用。 |
| **E29b WorldPlay 回放**（同一批按键按 24fps 锁存；3 个场景，75 次按键） | 标准：接缝起步 0.84、**丢失 25%**；其余 1.05、**丢失 0%**；单潜变量接缝点按 **0.00（6/6 全丢）**；朝向误差 1.57°。ctx 重叠：接缝起步 1.08、**丢失 0%**；朝向误差 **1.13°（−28%）**。→ **全部丢失都来自接缝起步。** |
| **E31 相位平衡回放**（替代 E29/E29b 的接缝/非接缝比较；每个按键在块内 4 个位置各出现一次，长度分布相同；按长度分层，自助法 95% CI；朝向误差统一按标准推理增益换算） | **minWM**（2 提示词，232 次按键）：单潜变量点按丢失 接缝 **96%** vs 非接缝 34%（差 0.62，CI 0.48–0.74）；2–3 潜变量 46% vs 25%（差 0.21，CI −0.01–0.44）；≥4 潜变量都不丢。重叠推理：接缝起步丢失 60%→37%，但非接缝单点按 34%→47%，朝向误差 3.47°→3.28°（**仅 −5%**）。**WorldPlay**（2 场景，80 次按键）：单潜变量点按 接缝 **4/4 全丢** vs 非接缝 0/12；更长按键不丢但接缝起步少转一步（生效 0.72 vs 1.10）。ctx 修复：接缝点按 0/4 丢失，但**增益 3.26→4.05（+24% 过度转动）**，统一标定后朝向误差 1.11°→**2.08°（变差）**。→ **现象在控制按键长度后成立；修复在两个系统上都不合格**（minWM 部分、WorldPlay 过度转动），E29/E29b 的"−25%/−28%"作废。 |
| E13 连续人类鼠标输入（MG2，24 段） | R² 学生 0.65 / 老师 0.68：连续转动下损失小——接缝处已有运动会延续，所以连续输入看不出问题；问题集中在起步和短按。 |
| E19 细调任务（minWM，47 次 1.5–3° 细调） | 5 秒后朝向误差 2.9°；落在块首的孤立细调生效率 0.006。 |
| 为什么没人报告过 | minWM 官方训练轨迹 36,164 次速度切换**全部**在块内第 2 位（首帧单独占一个潜变量导致"差一格"），官方评测轨迹也一样；MG2 官方脚本也在第 2 位切换；WorldMark 每个按键持续 20 秒。 |

### D. 修复（推理端，块重叠）

| 实验 | 结论 |
|---|---|
| **E27 minWM**（每块从上一块最后一个保留潜变量开始、重新生成后丢弃，算力 ×4/3） | 原块首位置 0.12 → **1.02 px/°**，其余 0.78–1.13（标准 1.2–1.9）：位置依赖消失。 |
| **E30 WorldPlay** | 标准：失效 12/30。重新生成式/固定式重叠：盲区换位置（8/18 失效）。**ctx 模式**（重叠位固定且放入上下文）：块首 4.29、0/9 失效；**宽度 2**（新潜变量只在块内第 3/4 位，算力 ×2）：全部位置平均 5.11、失效 **2/30**。 |
| 未做 | 画质、时间一致性、延迟代价；MG2 上的移植。 |

### E. 训练端尝试（均未修复，按"所试剂量下无效"表述）

| 实验 | 结论 |
|---|---|
| E18 minWM DMD 继续训练 300 步（≈60 次生成器更新），事件丰富轨迹 vs 官方 | 块首 0.10/0.06/0.05 vs 对照 0.13/0.05/0.04 → 无变化（剂量太小）。 |
| E23 数据相位随机化（同一批视频按不同起点裁剪重编码，TF 模型，lr 5e-6） | 块首/块内比例：原模型 0.16，250 步 0.09，500 步（≈1000 样本）≈0.03。整体控制变强 4 倍，块首盲区没变。 |
| E28 只对接缝前一个历史潜变量加噪（k=1、p=0.5，单卡 500 步） | 250 步比例≈0.35 但整体控制崩到 0.3–0.9；500 步回落到≈0.1，整体控制弱且不稳。 |
| E20 推理时调度（minWM） | 推迟一个潜变量部分恢复（0.46/0.73，+0.25 s 延迟）；摊开成 4×0.75° 落入死区更差。 |

### F. 作废 / 无定论

| 实验 | 原因 |
|---|---|
| E17 MG2 推理时块大小改为 1 | 分布外，连持续阶跃都几乎不响应。 |
| E24 minWM 推理时给缓存加噪 | Wan 适配器刷新缓存时把时间步固定为 0，`context_noise` 不生效，三档逐位相同。 |
| E26 教师强制单步 x₀ 探针 | 高噪声单步 x₀ 太模糊，对位姿只有 0.3–1% 的变化，测不出转动。 |
| WorldPlay 双向模型 | 16 潜变量一次生成时各位置普遍失效、时间漂移，不能作干净对照。 |

### 测量注意事项

- 第一块（k=3–6）在 minWM 上块内响应也常≈0 或符号不稳，比较时只用第 2、3 块。
- 微调会改变整体增益，跨模型比较要用"块首/块内"比例或各自增益归一化。
- 长视频（WorldPlay 32 潜变量）后段漂移，只看指令所在潜变量。
- minWM 另有与位置无关的"短按死区"（1.5° 明显弱于 3°），与块首效应分开报告。

### 第二阶段计划（约 3–4 周）

1. 修复的画质、时间一致性、延迟代价评测（目前完全没做，优先）。
2. 扩大样本：每个条件约 20 个场景 × 2 个种子；第二种读数（位姿估计）；加俯仰、平移、离散按键。
3. 系统覆盖：加 Matrix-Game 3.0 作为第 4 个系统；把修复移植到 MG2。
4. 修复定型：重叠宽度/上下文锚定的消融；训练端再试更强剂量作补充。
5. 写作（可并行）。

主要风险：修复用的是已有的重叠技术，新意要靠诊断和"为什么必须锚定上下文"；训练端机制未闭合；ActionSplice（同骨干）可能抢先。

---

### 早期探索记录（E01–E16，MG2 为主，数字保留）

| 实验 | 结论 |
|---|---|
| E01 MG2 动作起点逐帧推移（3 图 × 2 种子 × 起点 1–24） | 阶跃起动逐帧精确：视角延迟 1 帧（129/144），前进 1–2 帧；与相位无关。 |
| E02 Wan2.1 VAE 相位（DAVIS 87 段） | 组内第 3 帧重建误差低 25%；IV-VAE（CVPR 2025）已报告，不作为新问题。 |
| E06 / E06b VAE 单帧跳动与抖动 | 单帧跳动 4 个相位保留 89–103%；来回抖动保留 0.90–1.03 → VAE 不是瓶颈。 |
| E04 MG2 单帧脉冲（n=108/格） | 幅度 0.1：相位 0/1/3 转 2.3–2.9，相位 2 只有 0.44（先转后回弹）；重分析后是块结构的混合（见 A 表）。 |
| E05 / E08 正弦输入 | 学生周期 ≥8 帧增益≈1，3–4 帧≈0；老师同样压掉 3–4 帧 → 有效控制带宽≈潜变量奈奎斯特频率（带宽说法太泛，已放弃）。 |
| E07 / E10 / E11 MG2 老师 vs 学生、窗口屏蔽 | 回弹由蒸馏引入；学生不读历史动作；在老师上切断即复现（见 B 表）。 |
| E09 minWM 各阶段 | 失效从教师强制 AR 阶段开始（见 B 表）。 |
| E12 Open-Oasis | 逐帧生成是理想 LTI（阴性对照）。 |
| E13 真人连续输入 | 连续转动损失小（见 C 表）。 |
| E14 MG2 键盘短按探针 | 数据在 `results/raw/e14_ktap*`，结论未单独记录。 |
| E16 MG2 TempleRun | 只能在路口转向，读数无效，放弃。 |
| E15 minWM 预测性检验 | 块边界单步被丢 0.15–0.48 px，块内 3–24 px；1.5° 以下有幅度死区。 |

---

### 代码与复现

环境：`scripts/env.sh`（wam-va conda 环境 + `vendor/pylib` 里固定 sha 的 wheel，不改动已有环境）；第三方仓库与权重版本：`scripts/setup_vendor.sh`（MG2 `71c3cd7`、minWM `2a54f4d`、HY-WorldPlay `1588e13`、open-oasis `f59deef` 等）。WorldPlay 需要的组件目录 `data/hy15_worldplay/` 由 HF 缓存软链接组成（FLUX Redux 的 SigLIP 用公开的 `google/siglip-so400m-patch14-384` 代替，Glyph 用 `nlpcvcode/Glyph-SDXL-v2` 镜像）。`data/`、`vendor/`、`results/raw/`、`results/logs/` 不进 git。

| 用途 | 脚本 |
|---|---|
| MG2 探针 / 系统辨识 / 老师 / 窗口屏蔽 | `mg2_probe.py`、`mg2_sysid.py`、`mg2_base.py`、`mg2_mask.py`、`mg2_base_mask.py` |
| minWM 脉冲/阶跃/列表探针（`--ov` 可覆盖配置） | `mwm_sysid.py` |
| minWM 块网格平移（E22） | `mwm_shift.py` |
| minWM 块重叠推理（E27、E29） | `mwm_overlap.py` |
| WorldPlay 探针（`--model_type ar/bi`、`--overlap` + `OVL_MODE=regen/clamp/ctx`、`OVL_W`） | `wp_sysid.py`、`wp_overlap.py` |
| Oasis 探针 | `oasis_sysid.py` |
| VAE 相位/跳动 | `vae_phase.py`、`vae_jump.py` |
| 训练：DMD 微调（E18）、TF 微调（E23/E28）、接缝加噪配置 | `run_dmd_ft.sh`、`mwm_event_lmdb.py`、`run_tf_ft.sh`、`mwm_phase_lmdb.py`、`seam_aug.py`、`configs/stage1_ar_tf_seam.py` |
| 评测已训练 checkpoint | `eval_ft.sh`（DMD）、`eval_tf_ft.sh`（TF） |
| 真人按键回放窗口（E29） | `vpt_press_specs.py`（输出在 `results/summary/e29_specs*.json`；默认模式即首轮 E29 用的滑窗，有时长–相位混杂；`--balanced` 为相位平衡回放：固定时间网格取窗，每个窗口按 4 个相位各输出一份，带 `wid`/`phase` 字段） |
| 分析 | `analysis/phase_survival.py`（按块内位置）、`analysis/press_replay.py`（逐按键；新增按时长分层的接缝/非接缝对比与自助法 CI，`--ref_tag` 用参考条件的增益统一标定）、`analysis/nudge.py`、`analysis/sysid.py`、`analysis/mwm_bandwidth.py` |
| 作废 | `mwm_tf_probe.py`（E26） |

汇总结果在 `results/summary/`（按实验编号命名）。

---

## 工作台章程（原文）

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
