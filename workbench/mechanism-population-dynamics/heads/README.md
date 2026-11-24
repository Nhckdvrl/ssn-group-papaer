# 研究总档：mechanism-population-dynamics（2026-09-30 – 2026-10-17）

**这是头线（E01–E119）的总档，也是 `heads/` 的入口页。** 11-24：原 heads/README、1-original/README、2-after-closure/README 并入末尾两节；论文 v0–v2 删除，只留最终稿 v3（旧稿见 git 历史）。
- 它取代了以下文件：
  - 根目录：旧的 CLOSEOUT、ASSET_INDEX、两份 REVIEW、文献重选备忘录；
  - 知识库：重评、版本史、实验全景、证据账本、方向 / 主线 / 新意 / 问题审计等过程文件。
  - 这些文件已删除，可从 Git 历史恢复（见 §11）。
- 原始证据仍在原处：实验卡 `experiments/`、结果 `results/`、主张账本 [CLAIMS.md](../CLAIMS.md)、痛点记录 [PAIN_LOG.md](../PAIN_LOG.md)、每日记录 `logs/`、四版论文 `paper-acl-v0`–`v3`。
- 导师 10-22 新意见的分析单独放在 [knowledge/research/ADVISOR_2026-10-23_MOE.md](../ADVISOR.md#10-16-口述)，本文 §10 给出与历史的连接。

**状态：** 人已两次决定结项——10-11 结项论文线，10-17 按收尾规则停止修复线。本文是总结，不是重启。

---

## 0. 一页总结

**做了什么：**
- 约 20 天，约 120 张实验卡，写了四版论文（v0–v3）。
- 研究对象始终是“训练出来的 transformer 里，注意力头之间的分工从哪里来、能不能跨训练对应”。
- 前后换了五次具体问题：
  1. 复制机制群体与上下文—记忆仲裁；
  2. 指令数据装入的模板习惯；
  3. 初始化 × 语料决定哪个头担任哪个角色（论文线）；
  4. 分工的跨种子可重现性；
  5. 损伤后的修复与遗忘的可逆性。

**站得住的发现（都限定在所测模型与任务上）：**
1. **层内哪个头担任角色跟随初始化，不跟随语料。**
   - 同一组初始权重在 25 种语料上训练，层内一致 0.31–0.42；不同初始化 ≈ 0。
   - 9 种角色都如此；跨 14 个尺寸、两套模型族（DataDecide、Pythia）成立。
   - 而“在哪一层”对所有模型基本相同。
2. **这种分配在训练早期一小段内形成：**
   - 1% 时扰动会重排；2.5% 起加入与权重同量级的噪声，仍会回到原分配（0.79–0.98）；
   - 但换语料在 2.5% / 10% 后仍能改写 40% / 29%。
   - 保留多少，随两份语料的实词相似度（ρ −0.56 至 −0.80）和梯度噪声变化。
3. **能力、强度、出现时间和基准表现跟随语料；不存在“幸运种子”。**
   - 14 个尺寸 × 11 个基准上，初始化主效应显著的比例 ≈ 假阳性率。
4. **抽象分工跨独立种子重现，头的身份不重现：**
   - 任务深度顺序 τ 0.72；任务共享结构 0.73（满分 0.95，打乱 0.35）；
   - “哪些任务共用关键头”在 8 / 8 个干净种子中一致；
   - 逐头对应对不上（E89）。
5. **写出接口的对准决定一个组件的角色能否回来**（可能反映下游组件对该输出方向的耦合依赖，不一定是“角色存在那里”）：
   - 只重置读取参数，原角色和整个旧配置（搭档、替补）会长回来；
   - 把输出旋转一下（大小不变）就等于完整重置。
   - 谁接手角色，是已耦合候选之间的竞速（E96–E119）。
6. **公开模型套件的数据完整性问题：**
   - PolyPythias 的 weight-seed 变体实际没有换初始化；
   - Pythia-2.8B 去重版终点几乎等于标准版；
   - DataDecide-1B 有 6 个 run 的初始化与标签不符；
   - OLMo-2 的 main 不是 SFT / DPO 的祖先；
   - PolyPythias-410M seed3 / seed4 在训练中途被重置回初始化。
   - 这些对使用这些套件的人有直接价值。

**没站住的（已撤回）：** “先天的头布局 / 权重忘了种子但电路记得”、头布局识别种子的应用价值、“机制知识零样本跨模型迁移 0.85 / 0.94”、“行为出现即锁定承担者”、“删数据导致换头”、上下文采信是全局先验 / 模型特质、晚期门控是合理校准、自然 spike 改写分工、原分工是有边界的吸引子。详见 §2–§6 与 [CLAIMS.md](../CLAIMS.md) 的作废记录。

**为什么停（根因，详见 §7）：**
1. 主要对象“头的编号”是一个坐标：置换对称性保证独立初始化之间不存在天然对应的编号；同初始化跨语料能保持多少是经验问题，但这个经验规律没能连到更抽象的计算机制，回答不了“so what”；
2. 四版论文都在给同一个对象换包装，没有换问题；
3. 每当一个结论只在局部成立，就追它的残差，结果越做越窄。

**留下的可用东西：**
- 交叉设计；可靠性校正的比较方法；受控预训练中的分叉 / 扰动方法（关键期）；
- 损伤与遗忘的实验框架；
- 五项公开套件审计；
- 约 60 张正文精读论文卡。

---

## 1. 时间线

| 日期 | 阶段 | 发生了什么 | 谁做的决定 |
|---|---|---|---|
| 09-30 – 10-02 | 一：复制机制群体、门控、仲裁（E01–E24） | 复现 induction 电路；发现小模型后期的“随机序列复制门控”；仲裁的多个统一解释被否定 | agent 按止损规则逐个关闭 |
| 10-02 – 10-04 | 二：Flan “Question:” 习惯（C04） | 1–2% 指令数据装入一个由字面模板触发的上下文采信开关 | 10-10 人决定不再作为研究对象 |
| 10-03 – 10-04 | 三之一：初始化 × 语料（C05）成形；论文 v0 | 自然实验设计；“先天解剖、后天功能”的叙事 | 人要求按顶会标准“补工作量、包装叙事”（A02–A08） |
| 10-06 | 论文 v1 | 去掉部分比喻；E68 显示权重本身也能认出种子，应用被压缩 | 专家评审 + agent |
| 10-08 | 论文 v2 | 分层：层 / 组件 / 电路；E75 映射被发现借用了目标模型信息 | 人：“同层头可互换，所以由初始化决定接近必然，so what？” |
| 10-09 | 整理 | “头的身份认识价值低，唯一增量是对称破缺动力学” | 人：继续 |
| 10-10 | 转向讨论；论文 v3 | 人要求回到头这条线、减少 so what；v3 改问“头级发现能迁移到哪类相关模型” | 人 |
| 10-11 | **结项** | E83 否定“出现即锁定”，E86 显示原样重跑也易主；v3 新颖性不足 | **人：TERMINATED** |
| 10-15 | 四：知识库整理；分工可重现性（E89–E92） | E89 分工图谱；E90–E92 追 spike 与种子差异，被人指出“被结果牵着走” | 人授权重启实验；10-16 人叫停 E92 |
| 10-16 | E95 | PolyPythias 两个异常种子实为中途重置，E90 / E91 的 spike 框架作废 | agent |
| 10-16 – 10-17 | 五：损伤修复、遗忘、吸引子（E93–E119） | 写出接口的对准决定角色能否回来；遗忘的路线规律；吸引子假说落空 | **人：“没什么有意思就停”；按事先写好的收尾规则结项** |
| 10-22 | 导师新意见 | 先查 MoE 专家的分工是否跨训练一致，再查头 | 见 §10 |

---

## 2. 第一阶段：复制机制群体与上下文—记忆仲裁（E01–E24；C01–C03）

**问题：** 同一架构独立训练多次，复制（induction）电路和“相信上下文还是相信记忆”的仲裁机制，是否由同样的组件实现？哪些陈述能跨训练迁移？

**站得住的（L1，未独立校对）：**
- **C01：** 10 个 Pythia-70M 种子里，induction 都由“一个 previous-token 瓶颈头 + 依赖它的 induction 头”实现。头的身份不可复现，层位置 8 / 10 可复现，相对层序 10 / 10 可复现（E02）。
- **C02：** 31M–70M 小模型训练后期“随机 token 序列上的复制”下降、自然文本不变，由第 0 层注意力输出的分布偏移门控。把它平移回自然文本均值可救回 97–111%；门控强度在种子间相差 25 倍。
  - 160M 只剩残影，410M 没有；只影响合成探针，不伤自然任务（E03–E11）。
- **C03：** 算法、角色存在、整体必要性、近似深度可以跨训练迁移（0.89–1.00）；具体组件身份不可迁移（≤ 0.12）（E13、E15）。

**被否定的：**
- 单头拮抗介导后期退化（E03，零消融与均值消融方向相反）；
- 门控是对语料统计的合理校准（E08，被 1 亿 token 数据推翻）；
- 仲裁差异是一维旋钮上的默认偏移（E16）；
- 仲裁差异是知识强度差异（E17）；
- 上下文依赖是 run 的稳定特质（E18，跨条件一致性 0.15–0.26）；
- 语料配方设定全局的上下文可信度先验（E20 / E22）；
- “复制能力越强越不采信上下文”（E24 的 ρ −0.685，按语料家族去均值后 −0.18）。

**这一阶段的教训：**
- 小模型合成探针上的强干预效应，扩展到规模与自然任务就消失；
- 统一解释（一维旋钮、全局先验、模型特质）被逐条件的异质性一再否定；
- 跨配方相关受语料家族混杂。

---

## 3. 第二阶段：指令数据装入的模板习惯（C04）

**现象（L2，两个训练栈、多个尺寸）：**
- 从预训练语料中去掉占 1–2% 的 Flan 指令数据，只降低问答格式下对反事实上下文的采信（Δ +2.23，SE 0.50）。陈述格式下的采信和知识量都不变。
- 这个效应由字面模板 “Question:” 触发，“Q:” 和 “Query:” 不触发（E25–E34、E47、E49）。

**三处矛盾：**
- 从头预训练时，这个开关在 3.6% 时出现并单调增强（E29）；
- OLMo-2 中期训练中先升后降（3.71 → 1.45，E30）；
- 小模型继续预训练则装不进去，甚至降低采信（E48、E76：+0.15 ± 0.24）。

**结局：** 10-10 的转向判断曾推荐把“同一份指令数据何时教模型信上下文、何时信记忆”作为新中心（近邻 Goyal ICLR'25、Kim ACL'26）。**人决定 Flan / 问答格式线不再作为研究对象**，E25–E34 等卡已从工作区删除（Git 历史保留）。

---

## 4. 第三阶段：初始化 × 语料与头的角色（C05；论文 v0–v3）

### 4.1 设计（这条线最好的部分）
- **自然实验：**
  - DataDecide 用 3 组初始权重 × 25 种语料 × 14 个尺寸（4M–1B）训练；
  - Pythia 用同一组初始权重分别训练标准版与去重版（70M–12B）；
  - 加上受控预训练（E46 系列）。
- **三类模型对：** 同初始化异语料、同语料异初始化、两者皆异。
- **读数：** 每个模型 9 种头角色的 [层 × 头] 分数图（induction、previous-token、检索、sink、重复 token、当前 token、前 2 token、分隔符、OV 复制）。拆成“哪一层”与“层内哪个头”两层比较。层内比较在置换下零点为 0，天然有基线。
- **审计：** 逐个核对公开检查点的真实初始化与谱系（P09、P11、P12、P13）。

### 4.2 v0 *Born to Copy, Taught to Trust*（10-04）
- **主张：**
  - 先天的是“解剖”：哪个头成为哪种角色由种子决定，头布局能 98–100% 认出种子，而权重与初始值的相关只剩 0.04；
  - 后天的是功能：能力、时间、基准表现、Flan 习惯；
  - 两者在类似 Lenneberg 的关键期（前 1–2.5%）相遇。
- **问题：** 从“同编号的统计相似”跳到“头的命运天生注定”；先天 / 后天的二分与关键期类比太强；把两条没有机制中介的线（头布局与 Flan 习惯）硬拼在一起。

### 4.3 v1 *Which Head Takes Which Role?*（10-06）
- **主张：** 层内由哪个头担任角色跟随初始化、跨自然语料保持；分配在早期一段内形成；保留多少取决于语料实词相似度与“每 token 学习率”（梯度噪声）；对行为没有初始化效应。
- **问题：**
  - E68 发现权重本身也能认出种子（SeedPrints 从 60M 起 100%），“权重忘了种子”与识别应用被删。
  - E66 发现关键期后换语料仍改写 29–40%，“关键期关闭”被改写。
  - 核心对象的 so what 仍在：层内的头可以互换，数据不可能偏好某个编号。

### 4.4 v2 *When Do Mechanisms Correspond Across Pretraining Runs?*（10-08）
- **主张：** 对应分三层——层跨所有模型对应；组件只在同初始化内对应；任务电路即使同初始化也只部分对应。
- **问题：**
  - E75 的“按功能映射后迁移 0.85 / 0.94”用了目标模型自己的 DLA（直接 logit 归因）来找头，测到的是“在目标模型上重新发现电路”，不是源模型知识的迁移。
  - 不用目标信息时，异初始化只有 −0.06。剩下的结论就是 Tigges NeurIPS'24 的“算法稳定、组件更换”。
  - 人审：“由初始化决定接近必然，so what？”

### 4.5 v3 *Which Head Does the Work?*（10-10 / 11）
- **主张：**
  - 角色标签在同初始化内迁移；
  - 因果承担者只沿同一训练谱系迁移（预训练 → 中期训练 → SFT → DPO → 指令微调保持不变，0.93–1.00）；
  - 同初始化、数据略有不同的兄弟模型，用同一功能类里的不同头承担 IOI。
  - 原样重跑在 9 / 15 个初始化中把最强 induction 头换成别的候选。
- **问题：**
  - DLA 层内排名的拆半信度只有约 0.40，未达预设门槛；
  - E81 / v3 的“迁移”在代码中是“按单头消融选头、单头效应相加”，不是正文写的“DLA 选头、联合消融”（指标合同不一致）；
  - E83 前瞻验证“行为出现时承担者已定”只有 3 / 12；
  - E87 完整验证被中止、无结果；
  - 近邻 Tigges、Bali（ICML'26）、Trott、MDA 已解释大半。
- **10-11 人决定终止。**

### 4.6 这条线最终站得住的
见 §0 发现 1–3、6。另有：
- 同初始化兄弟的注意力角色图对应约 0.24–0.34，而 IOI 单头消融图约 0.02（E81）——注意力角色与因果承担是两件事。
- previous-token → induction 的权重组合在 75 / 75 个 1B 模型中存在（E55），但单头因果证据只有 12 / 18。
- 初始权重统计量与初始梯度都预测不了层内哪个头胜出（E39、E41）。
- 同初始化不带来线性连通（插值势垒 7.5 vs 7.0 nats，E43）。

### 4.7 这条线撤回的
完整列表见 [CLAIMS.md](../CLAIMS.md) 作废记录。要点：
- 权重忘了种子、电路记得（E68）；
- 关键期在 2.5% 关闭（E66）；
- 0.85 / 0.94 的机制迁移（E75）；
- Flan 只改检索头的说法（E65 两次更正）；
- “初始化尺度与学习率决定继承强度”（E46c 处在地板上，改由 E62 检验）；
- 行为出现即锁定（E83）；
- 删数据致换头（E86）。

---

## 5. 第四阶段（结项后，未成文）：分工可重现性与种子差异（E89–E92、E95）

**起因：** 10-15 重评认为，导师 10-16 当面关心的是“编号变了，分工是否相似”，旧论文没有回答。
- **E89 多任务因果分工图谱：**
  - 设置：410M 10 个种子、160M 15 个模型、DataDecide-1B 12 个模型、9 个任务，读每个头的均值消融效应。
  - 结果：
    - 任务深度顺序跨种子重现（τ 0.72）；
    - 任务共享结构部分重现（剔除重置种子后 0.73，满分 0.95，打乱 0.35）；
    - “共用关键头”的任务对高度一致（greater-than~后继 8 / 8、induction~后继 8 / 8、反义词~induction 7 / 7）；
    - 逐头对应几乎对不上（留一任务预测 0.00–0.27）。
  - 被搁置的理由：共用关系可能只是“共享原语”的必然；没有“一致到什么程度才有意义”的基线。
- **E90 → E91 → E92：**
  - 追 410M seed3 / seed4 的异常组织与 loss spike，再扩展到种子差异的能力图谱。
  - 人指出这是被结果牵着走的行为轨迹测量，偏离研究对象，叫停。
  - 留下的事实：正常 run 之间的种子差异是逐任务、连续的小幅波动，不是双峰；31M 有“学会后丢失”的暂时能力。
- **E95 审计：** PolyPythias-410M seed3 / seed4 在训练中途被重新从初始权重训练，学习率已降到峰值的 40% / 18%。“spike 改写分工”的框架因此作废——那是重置后时间不够的平凡结果。

---

## 6. 第五阶段（未成文）：损伤修复、遗忘可逆性、吸引子（E93–E119）

**问题：** 良性的继续训练为什么会撤回某些后加的修改（损伤、遗忘），而不撤回另一些？一个组件的角色由什么承载？主要在 Pythia-160M step100k 上做。

**站得住的：**
1. **写出接口的对准决定角色能否回来**（措辞于 10-23 收紧：也可能是下游对该输出方向的耦合依赖）。
   - 只重置 QK（读取）而保留、对准输出时，原头长回原角色，整个旧配置一起回来。
   - 输出正交旋转 = 完整重置：160M 6 / 6 个头、5 个功能；410M 2 / 2（E96–E104）。
2. **回归程度随写出接口的对准度线性变化（≈ cos φ − 0.2），没有临界点。**
   - 回不来主要是因为被已耦合的替补抢先：清零替补后，75° 的扰动也能从 0.06 回到 0.60。
   - 冻结其余部分时，完整重置的头也能回来；联合训练时则被锁死，变成注意力汇（E107、E119）。
3. **损失恢复 ≠ 能力恢复。**
   - IOI 停在 0.40，损失照样恢复；
   - 能否被接手，取决于此时有没有已在看相关 token 的头（E98、E100）。
4. **遗忘的路线规律：**
   - 删除型修改若落在 QK（读取）参数上，比落在 OV / MLP（写出）上更易被良性训练补偿；
   - 方向在 IOI / 首都、梯度差 / NPO、160M / 410M 上一致，强度依赖方法与尺寸（差值约 0.3 → 0.1–0.15）；
   - 对添加型修改与定向重学攻击不成立；
   - 机制只部分解释：足迹宽度与起点拉回被干预否定；格式在梯度差内相关（0.96）、跨方法失效；恢复靠补偿，不是参数撤销（E105–E118）。

**落空：** “原分工是有清晰边界的吸引子”——E119 显示回归随对准度线性渐变，没有边界。按事先写好的三条收尾标准（边界陡峭、竞速成立、不只一个头）只满足一条半，结项。

**为什么不够：** 相对 Frankle 2020 / Lubana 2023（整模型层面的盆地与机制锁定）、Rushing & Nanda 2024（自修复）、Hu 2025 / Qi 2024（良性重学），这些结论是组件层面的细化，不足以改变同行的默认认知。

---

## 7. 跨阶段诊断：我们为什么反复不够好

1. **对象选错了，而且一直没换。**
   - “哪个编号的头”是坐标；同层的头连同 QKV / O 一起置换，函数不变。
   - 置换对称性保证独立初始化之间没有天然对应的编号（所以跨独立初始化按编号比较，期望为 0）；同一初始化在不同语料上保留多少分配，是经验问题，不是数学必然。我们测到了这条经验规律，却没能说明它对更抽象的计算机制有什么后果。
   - v0 → v3 只给这个对象换了四次包装（先天 / 后天 → 谁担任角色 → 对应层级 → 迁移到哪类模型），问题没变。
2. **叙事先行。**
   - A02–A08 的工作方式是“按顶会标准补工作量、叙事包装、不为严谨收窄、实验为叙事服务”。
   - 结果是强说法（“权重忘了种子”、0.85 / 0.94 迁移、关键期关闭）先写进稿件，再被后续实验撤回。
3. **推断桥未检验：** 注意力角色 → 因果承担 → 算法，三层之间的跨越多次被当成已成立。
   - 目标辅助映射被算成迁移（E75）；
   - 正文与代码的指标不一致（E81 / v3）；
   - argmax 易主被当成因果工作转移（E86）。
4. **测量信度不足：** 单任务承担者近似平局，DLA 排名信度约 0.40，原样重跑就有 9 / 15 次易主。用这种读数比较“是否同一个头”，噪声本身就会给出“不一致”。
5. **追残差、越做越窄：** E89 → E90 → E91 → E92、E105 → E118，每一步追上一个结果的残差，研究对象从组件群体漂到行为曲线，或者每次修补都多加一个条件（止损规则的来源）。
6. **近邻压缩：** Tigges（算法稳定、组件更换）、Bali（头跨种子稳定性）、SeedPrints（权重识别种子）、Trott（位置维度的推广）、MDA（训练数据归因与 induction）各占一块，我们的增量一再被压到“范围明确的经验记录”。
7. **但也有做对的：**
   - 交叉设计；
   - 事先写决策表并如实记录作废；
   - 用权重核实谱系；
   - 受控预训练的分叉 / 扰动；
   - 可靠性校正；
   - 公开套件审计（反而是最硬、最可复用的产出）。

---

## 8. 方法与工程教训
- 前向与干预的隐蔽失败、统计偏置、公开模型的数据完整性、运行与资产事故：[knowledge/heritage/FAILURE_MODES.md](../knowledge/heritage/FAILURE_MODES.md)。
- 注意力角色、OV、DLA、单头 / 联合消融的估计对象与审计合同：[knowledge/heritage/MEASUREMENT_AUDIT.md](../knowledge/heritage/MEASUREMENT_AUDIT.md)。
- 置换对称的精确定义、因果等价的四个层级：[knowledge/syntheses/SYMMETRY_ALIGNMENT.md](../knowledge/syntheses/SYMMETRY_ALIGNMENT.md)、[CAUSAL_EQUIVALENCE.md](../knowledge/syntheses/CAUSAL_EQUIVALENCE.md)。
- 研究流程上：
  - 止损规则（每次修补都要加一个条件就停）；
  - “估计器不是方法”；
  - 先问清“谁会因结果改变判断”再做 pilot（见用户记忆）。

---

## 9. 可复用资产
| 资产 | 位置 | 用途 |
|---|---|---|
| 受控预训练（分叉、加噪、换语料、改学习率 / 批大小） | `scripts/e46_train.py`，E46 / E62 / E66 卡 | 直接适用于“分工何时决定”的分叉实验（§10） |
| 头角色图（9 种角色） | `scripts/e59_roles.py`、`e35_verified.py`，`results/e35_verified.json` | 跨模型比较的基础读数 |
| 多任务因果分工图谱 | `scripts/e89_labor.py`、`e89_analyze2.py`，`results/e89/` | 头分工的已有数据（§10 Q5） |
| 损伤 + 继续训练 | `scripts/e93_lesion.py`（QK / OV / 旋转 / 混合 / 冻结） | 角色承载与竞速 |
| 参数子集遗忘 | `scripts/e105_unlearn.py`（梯度差 / NPO） | 遗忘路线规律 |
| 公开套件审计 | [../suite-audits/](../suite-audits/README.md)，PAIN_LOG P09–P14，E95 | 三项已于 10-25 在 Hugging Face 提交 |
| 论文精读卡 | `../knowledge/papers/`（约 60 张），目录见 [knowledge/PAPER_CATALOG.md](../knowledge/PAPER_CATALOG.md) | 普适性、对称、修复、遗忘、MoE |
| 四版论文 | `1-original/papers/paper-acl-v0`–`v3`（PDF + LaTeX） | 写作与叙事的反面 / 正面教材 |

**注意：**
- 本地缓存 `~/mechpop_cache`（Pythia 检查点、Pile 分词数据）在 10-23 核对时已不存在，再做实验需要重新下载。
- v3 部分图依赖未进 Git 的 `results/e81`、`e83` 原始 `.npz`。
- 结果目录中未进 Git 的大文件（`results/e68/*.npz` 等）只在本机。

---

## 10. 之后：MoE 方向（10-23 起）
- 导师 10-22 建议先查 MoE 专家的分工是否跨训练一致，再回到头。这条线放在工作台的 [moe/](../moe/README.md)（E120–E143），当前评估与下一步都写在那里。
- 头线留下的教训（§7）被转成了 MoE 的测量约束：不重做“结构重现、身份不重现”；扣除 token 身份与被动几何；专家差异用候补顶替而不是均值钳制；统计单位是独立训练。

---

## 11. 仓库结构与清理记录
**2026-10-26 起的结构**（这部分路径以 `heads/` 为根）：
```
heads/
  HISTORY.md           本文（主题 1、2 的历史总档）
  1-original/          主题 1：E01–E88 实验卡、A01 混杂审计、papers/（四版论文）
  2-after-closure/     主题 2：E89–E119 实验卡
  scripts/             主题 1、2 共用代码（mp_common.RESULTS = heads/results）
  results/             主题 1、2 共用结果（大文件只在本机）
```
主张账本、痛点记录、每日日志、论文卡在工作台根目录（`../CLAIMS.md`、`../PAIN_LOG.md`、`../logs/`、`../knowledge/`）。

**2026-10-26 删除：** 运行日志与 stdout（`*.out`、`run.log`）、作业清单（`*jobs*.txt`）、GPU 探测与清理脚本及其输出（`gpu_scout*`、`janitor*`、`scout_*`）、冒烟测试目录、GPT 生成的过期文件清单（`FILE_CATALOG`、`research_inventory`、`asset_inventory`、`document_link_audit`）、`PAPER_SHAPE_MOE.md`；人 10-10 决定放弃的 Flan 支线（E25–E34、E47–E50、E53、E65、E76）的结果目录与专用脚本（E26 / E28 因被后续代码导入而保留）。

**2026-10-23 清理（当时的结构为扁平的 experiments/、results/、scripts/）：**

**删除的文件**（内容已并入本文；可用 `git show <清理前的提交>:<路径>` 恢复，清理前的提交见本文所在提交的父提交）：
- **根目录：** CLOSEOUT.md、ASSET_INDEX.md、REVIEW_2026-10-09.md、REVIEW_2026-10-10.md、LITERATURE_FIRST_RESELECTION_2026-10-10.md。
- **`software-submission/`（2,295 个文件）：** v1 时代的独立复现包，其中 1,247 个文件与 `results/` 完全相同；对应的论文已被取代。另删除本地未跟踪的 `software-submission.zip`。
- **`experiments/A02`–`A10`：** 叙事、提纲、引言 / 结果草稿；最终叙事以四版论文为准。保留 A01 混杂审计。
- **`knowledge/` 过程文件：** 2026-10-15 的重评、文献地图、种子方差近邻；AGENT_GUIDE、CHANGELOG、FIELD_GUIDE、README；heritage 的 PAPER_VERSIONS、EXPERIMENT_ATLAS、EVIDENCE_LEDGER；research 的 DIRECTION、MAINLINE、NOVELTY、QUESTION_AUDIT、OPEN_QUESTIONS、PILOT_DESIGNS、ADVISOR_2026-10-17、CLOSEOUT_2026-10-17；syntheses 的 CONFLICT_MAP、TRAINING_DYNAMICS、REPAIR_FOLLOWS_COUPLING。
- **论文目录里未跟踪的构建残留：** overleaf-upload.zip、errors-final.json。

## 主题 1 文件索引

*原文件 `heads/1-original/README.md`；原标题：主题 1：最初的研究——头的分工从哪里来、能否跨训练对应（E01–E88）*
**状态：** 2026-10-11 人决定结项（TERMINATED），不再新增实验或论文工作。卡片上残留的 RUNNING / REGISTERED 是结项时未更新的状态。完整来龙去脉见 [../HISTORY.md](README.md) §0–§4、§7。

### 问题
同一架构独立训练多次，注意力头之间的分工（谁做 induction、谁做检索……）从哪里来？哪些陈述能跨训练迁移？

### 站得住的（都限定在所测模型与任务上）
1. **层内哪个头担任角色跟随初始化，不跟随语料。** DataDecide 3 初始化 × 25 语料：同初始化层内一致 0.31–0.42，不同初始化 ≈ 0；9 种角色、14 个尺寸、两个模型家族成立。“在哪一层”对所有模型基本相同（C05，L2）。
2. **分配在训练早期一小段内形成。** 1% 时扰动会重排；2.5% 起同量级噪声仍回到原分配（0.79–0.98）；换语料在 2.5% / 10% 后仍改写 40% / 29%。保留多少随语料实词相似度变化（ρ −0.56 至 −0.80）。
3. **能力、强度、出现时间、基准表现跟随语料；不存在“幸运种子”。**
4. **复制机制群体（E01–E24）：** induction 在 10 个种子里都是“previous-token 瓶颈头 + induction 头”，头身份不重现、相对层序重现（C01）；31M–70M 的晚期“随机序列复制门控”（C02）；仲裁的几种统一解释都被否定。

### 为什么结项
- 对象“头的编号”是坐标：置换对称性下独立初始化之间没有天然对应的编号；同初始化跨语料能保持多少，没能连到更抽象的计算机制，so what 回答不了。
- 四版论文（v0–v3）都在给同一个对象换包装；DLA 排名信度约 0.40；原样重跑就有 9 / 15 次易主（v3）；近邻 Tigges 2024、Bali 2026 已解释大半。

### 论文
[papers/](1-original/papers)：v0 *Born to Copy, Taught to Trust*（10-04）→ v1 *Which Head Takes Which Role?*（10-06）→ v2 *When Do Mechanisms Correspond Across Pretraining Runs?*（10-08）→ v3 *Which Head Does the Work?*（10-10/11）。各版问题见 HISTORY §4。

### 实验卡
**阶段一：复制机制群体、门控与上下文—记忆仲裁（09-30 – 10-03）**

| 卡 | 问题 |
|---|---|
| [E01](1-original/experiments/E01-induction-baseline-repro.md) | Pythia-70M induction baseline reproduction |
| [E02](1-original/experiments/E02-induction-circuit-population.md) | Induction circuit across 10 independent Pythia-70M runs |
| [E03](1-original/experiments/E03-antagonist-mediated-regression.md) | Is late copy regression mediated by acquired antagonist heads? |
| [E04](1-original/experiments/E04-context-naturalness-gating.md) | Does a layer-0 "context naturalness" offset gate in-context copying? |
| [E05](1-original/experiments/E05-gating-across-scale.md) | Is gated in-context copying a general late-training phenomenon? |
| [E06](1-original/experiments/E06-what-keys-the-gate.md) | What property of the context keys the copy gate? |
| [E07](1-original/experiments/E07-gate-vs-degeneration.md) | Context-level gate or token-level degeneration? |
| [E08](1-original/experiments/E08-is-the-gate-rational.md) | Is copying actually less reliable in rare-dense contexts of the training data? |
| [E08b](1-original/experiments/E08b-gate-regime-data-support.md) | Data support and copy reliability of the gate's regime, on a large Pile sample |
| [E09](1-original/experiments/E09-gate-at-160m.md) | Does the rarity-keyed context gate, and its data-sparse seed spread, exist at 160M? |
| [E10](1-original/experiments/E10-gate-vs-capacity.md) | How do the copy gate and its between-run spread depend on capacity? |
| [E11](1-original/experiments/E11-functional-consequence.md) | Which realistic in-context tasks does the late gate impair? |
| [E13](1-original/experiments/E13-arbitration-across-runs.md) | Is context-vs-memory arbitration reproducible across independent runs? |
| [E14](1-original/experiments/E14-ioi-portability.md) | Claim portability for the IOI circuit across independent runs |
| [E15](1-original/experiments/E15-claim-portability.md) | Claim portability across independent runs |
| [E16](1-original/experiments/E16-arbitration-default-offset.md) | Is run-level arbitration divergence a low-dimensional default offset on a shared knob? |
| [E17](1-original/experiments/E17-arbitration-vs-knowledge.md) | Is run-level arbitration divergence just knowledge-strength divergence? |
| [E18](1-original/experiments/E18-context-reliance-trait.md) | Is context reliance a stable run-level trait? |
| [E19](1-original/experiments/E19-late-snapshot-stability.md) | Is the run-level context/memory difference a property of the run or of the snapshot? |
| [E20](1-original/experiments/E20-recipe-vs-seed-arbitration.md) | Does the data recipe or the seed set context/memory arbitration at 1B? |
| [E21](1-original/experiments/E21-rare-fact-divergence.md) | Do same-recipe runs disagree mostly on rare facts? |
| [E22](1-original/experiments/E22-global-context-prior.md) | Is there a corpus-level "context-trust prior" beyond item frequency? |
| [E23](1-original/experiments/E23-corpus-structure-to-copy-prior.md) | Does corpus repetition structure predict a recipe's copy-vs-recall prior? |
| [E24](1-original/experiments/E24-induction-mediation.md) | Is the recipe's copy-vs-recall prior carried by induction (copy) strength? |

**阶段二：Flan“Question:”模板习惯（C04）**——人 10-10 决定不作研究对象，卡片与结果已删除（Git 历史保留）。E26 / E28 两个脚本因被后续代码导入而保留在 `../scripts/`。

**阶段三：初始化 × 语料与头的角色（10-03 – 10-11，论文线）**

| 卡 | 问题 |
|---|---|
| [A01](1-original/experiments/A01-confound-audit-C04-C05.md) | 混杂审计（EXECUTION.md §4）：C04 与 C05 |
| [E35](1-original/experiments/E35-init-by-data-mechanism-census.md) | Is mechanistic component identity set by initialization or by training data? A crossed 3-init × 25-data census |
| [E36](1-original/experiments/E36-init-effects-on-behaviour.md) | Does the initialization carry behavioural offsets across 25 training corpora? |
| [E37](1-original/experiments/E37-identity-lock-in-timing.md) | When during pretraining is the initialization-set component layout locked in? |
| [E38](1-original/experiments/E38-c05-at-300m.md) | Does the init-sets-layout / data-sets-strength dissociation (C05) hold at 300M? |
| [E39](1-original/experiments/E39-init-weight-predictors-of-roles.md) | What in the random initialization predicts which heads take which roles? |
| [E40](1-original/experiments/E40-lock-in-curves-pythia.md) | Lock-in curves of role layout within single runs (Pythia, dense early checkpoints; CPU) |
| [E41](1-original/experiments/E41-initial-gradient-predictors.md) | Does the initial gradient (growth rate at step 0) predict which heads take which roles? |
| [E42](1-original/experiments/E42-causal-role-maps-and-transfer.md) | 因果定义的角色图是否也由初始化决定？头级干预能否在模型之间迁移？ |
| [E43](1-original/experiments/E43-coordinate-system-vs-content.md) | 初始化固定的是“坐标系”，数据决定的是“内容”？——按索引对齐 vs 置换 / 旋转不变的交叉分离 |
| [E44](1-original/experiments/E44-pythia-natural-experiments.md) | 第二个模型家族的天然实验——Pythia 标准 / 去重共用初始化；PolyPythias 拆开初始化与数据顺序 |
| [E45](1-original/experiments/E45-scale-series-4m-to-1b.md) | 尺寸曲线——“位置由初始化决定”在 DataDecide 的 14 个尺寸（4M–1B）上是否成立、如何随尺寸变化？ |
| [E46](1-original/experiments/E46-controlled-training-basin-and-critical-period.md) | 受控预训练——数据能否挪动成分位置？初始化扰动的吸引域多大？位置何时锁定（关键期）？ |
| [E46b](1-original/experiments/E46b-controlled-training-larger-model.md) | 受控训练中的规模效应——更大的模型里，位置由初始化还是早期数据决定？ |
| [E46c](1-original/experiments/E46c-what-sets-inheritance-init-scale-and-lr.md) | 继承强度由什么决定？——固定架构下操纵初始化尺度与学习率 |
| [E51](1-original/experiments/E51-benchmark-variance-decomposition.md) | 下游基准上的“先天 / 后天”——初始化对 11 个任务有没有主效应？ |
| [E52](1-original/experiments/E52-specialized-neurons-inheritance.md) | 头记得 seed、神经元忘了——高度特化的神经元是否例外？ |
| [E54](1-original/experiments/E54-when-developmental-timing.md) | “何时”由谁决定？——受控训练中 induction 出现时刻的初始化 / 语料分解 |
| [E55](1-original/experiments/E55-algorithm-level-universality.md) | 算法层是否普适？——previous-token → induction 的两步算法在每个模型中都成立吗 |
| [E56](1-original/experiments/E56-inheritance-depends-on-corpus-similarity.md) | 继承的边界条件——同初始化的头身份，只在早期统计相似的语料之间被继承？ |
| [E57](1-original/experiments/E57-scale-curve-development.md) | 尺寸曲线的发育视角——小模型是从来没有继承，还是继承过又被冲掉？ |
| [E58](1-original/experiments/E58-pythia-to-12b.md) | 第二家族扩展到 12B——Pythia 6.9B / 12B 的标准版与去重版 |
| [E59](1-original/experiments/E59-more-head-roles.md) | 更多头角色——“初始化选槽位”是否适用于所有类型的头？ |
| [E60](1-original/experiments/E60-corpus-distance-predicts-inheritance.md) | 语料越相似，初始化的槽位继承越强？ |
| [E61](1-original/experiments/E61-anatomical-seed-identification.md) | 解剖学 seed 识别——只看头的分工布局，能否认出在陌生语料上训练的模型来自哪个 seed？ |
| [E62](1-original/experiments/E62-batch-size-sets-inheritance.md) | batch 大小决定继承强度？——为 DataDecide 的规模趋势找机制 |
| [E66](1-original/experiments/E66-early-window-warmup-and-optimizer.md) | 早期窗口跟随训练进度，还是跟随学习率 warm-up 与优化器状态？ |
| [E67](1-original/experiments/E67-audit-all-sizes.md) | 1B 以下所有尺寸的初始化核查与 checkpoint 记录 |
| [E68](1-original/experiments/E68-identification-baselines.md) | 认出初始化——权重 baseline 与 SeedPrints baseline |
| [E69](1-original/experiments/E69-strongest-head-and-reviewer-checks.md) | E69（POST-HOC）：最强头的一致、只看承载角色的层、模板特异性的合并检验 |
| [E70](1-original/experiments/E70-seed-matched-attribution.md) | 比较不同数据训练的模型时，头层面的差异有多少来自初始化？ |
| [E71](1-original/experiments/E71-early-localization.md) | 能否在训练早期定位将来的角色头？ |
| [E72](1-original/experiments/E72-head-alignment-gauge.md) | 头的编号是不是纯粹的坐标约定？跨初始化对齐后，被留出的角色能否对上？ |
| [E73](1-original/experiments/E73-ioi-component-transfer.md) | 一个已发表 circuit 的头标签，能否带到同初始化、不同数据的模型上？（IOI，2026-10-07） |
| [E74](1-original/experiments/E74-ioi-across-corpora.md) | IOI circuit 的头标签在 25 个语料、3 个初始化之间如何推广？（DataDecide 1B，2026-10-07） |
| [E75](1-original/experiments/E75-ioi-transfer-gap-decomposition.md) | 410M 同初始化兄弟之间 IOI 迁移只有 0.05——是计算变了、同一计算换了承担者，还是测量造成的？ |
| [E77](1-original/experiments/E77-arbitration-atlas.md) | 上下文 / 记忆仲裁的条目级图谱——训练让模型沿着同一条“置信度曲线”移动，还是改变了曲线本身？ |
| [E79](1-original/experiments/E79-memory-route-under-conflict.md) | 冲突上下文下，存活的记忆从哪条通路进入？ |
| [E81](1-original/experiments/E81-carrier-inheritance.md) | 头角色与因果承担者的继承——信度校正，以及继续训练的后代 |
| [E82](1-original/experiments/E82-when-carriers-are-fixed.md) | 因果承担者在训练的什么时候定下来？兄弟模型从哪一步开始分叉？ |
| [E83](1-original/experiments/E83-carrier-chosen-at-emergence.md) | 主力承担者是不是在任务行为出现时选定一次、之后保持？兄弟是否共享由那一刻决定？ |
| [E84](1-original/experiments/E84-relocation-vs-suppression.md) | 删数据重训后“目标头变弱”，是能力被抑制，还是活换给了别的头？ |
| [E85](1-original/experiments/E85-candidate-gap-and-swaps.md) | 两个候选越接近，随机删数据越容易换掉胜者吗？ |
| [E87](1-original/experiments/E87-E88-review-checks.md) | 回应 2026-10-11 审稿意见的检验 |

### 代码与结果
共用 [../scripts/](scripts) 与 [../results/](results)（按 `eNN` 命名）。脚本以 `heads/` 为根（`mp_common.RESULTS = heads/results`）；Pythia / DataDecide 检查点已不在本地，重跑需重新下载。

## 主题 2 文件索引

*原文件 `heads/2-after-closure/README.md`；原标题：主题 2：结项后的找补——分工可重现性、损伤修复、遗忘可逆性（E89–E119）*
**状态：** 2026-10-17 人决定“没什么有意思就停”，按事先写好的收尾标准结束。均未成文。卡片上残留的 RUNNING 是停止时未更新的状态。详见 [../HISTORY.md](README.md) §5–§6。

### 阶段四：分工的跨种子可重现性（E89–E92、E95）
- **起因：** 导师 10-16 当面关心的是“编号变了，分工是否相似”，旧论文没有回答。
- **E89（最有用的结果）：** 410M 10 个种子、160M 15 个模型、DataDecide-1B 12 个模型、9 个任务的头级消融图谱。任务深度顺序跨种子重现（τ 0.72）；任务共享结构部分重现（0.73，满分 0.95，打乱 0.35）；“哪些任务共用关键头”8 / 8 一致；逐头对应几乎对不上。搁置原因：缺少“一致到什么程度才有意义”的基线。
- **E90–E92：** 追异常种子的 loss spike 与种子间能力差异，人指出被结果牵着走，叫停。
- **E95：** 发现 PolyPythias-410M seed3 / seed4 在训练中途被重置回初始化（→ [../../suite-audits/](../suite-audits/README.md)），“spike 改写分工”框架作废。

| 卡 | 问题 |
|---|---|
| [E89](2-after-closure/experiments/E89-division-of-labour-atlas.md) | 重新训练后，头之间的“分工”是否重现？——以置换不变的多任务因果图谱来测 |
| [E90](2-after-closure/experiments/E90-outlier-trajectories.md) | 训练失稳的两个异常种子，分工是“从未长成”还是“长成后被改写”？——以及共用关系是同时出现还是后来招募 |
| [E91](2-after-closure/experiments/E91-spike-origin-heads.md) | 预训练 loss spike 从哪个头开始？——单点瓶颈的 previous-token 头是不是起点 |
| [E92](2-after-closure/experiments/E92-capability-atlas-seeds.md) | 同一配置、不同种子的预训练，为什么有的学会某项能力、有的学不会？——PolyPythias 全种群能力图谱 |
| [E95](2-after-closure/experiments/E95-polypythias-reset-audit.md) | PolyPythias 410M seed3 / seed4 的“loss spike”其实是训练中途被重置回初始化（审计，2026-10-16） |

### 阶段五：损伤修复、遗忘可逆性、吸引子（E93–E119，主要在 Pythia-160M）
- **写出接口的对准决定角色能否回来：** 只重置读取（QK）而保留输出时，原头和整个旧配置会长回来；把输出旋转一下（大小不变）就等于完整重置（160M 6 / 6、410M 2 / 2）。回归程度随对准度线性变化，没有临界点；回不来主要是被已耦合的替补抢先。
- **损失恢复 ≠ 能力恢复：** IOI 停在 0.40，损失照样恢复。
- **遗忘的路线规律：** 落在读取侧的删除比落在写出侧的更容易被良性训练撤回；方向在两个任务、两种遗忘方法、两个尺寸上一致，强度依赖方法与尺寸；机制只部分解释。
- **落空：** “原分工是有边界的吸引子”（E119：线性渐变，无边界）。
- **为什么不够：** 相对 Frankle 2020、Lubana 2023、Rushing & Nanda 2024、Hu 2025 是组件层面的细化。

| 卡 | 问题 |
|---|---|
| [E93](2-after-closure/experiments/E93-lesion-recovery-pilot.md) | 预训练中途受损后，能恢复什么？——受控损伤 + 匹配对照继续训练的校准 pilot |
| [E94](2-after-closure/experiments/E94-benign-vs-malignant-damage.md) | 什么样的训练中途损伤不可恢复？——损伤几何 × 幅度 × 时间 |
| [E96](2-after-closure/experiments/E96-role-reassignment.md) | 训练中一个头靠什么保住 / 夺回自己的角色？——QK、OV、空缺的拆分 |
| [E97](2-after-closure/experiments/E97-who-takes-over.md) | 损伤一个功能的第一承担头之后，谁接管？——事先预测检验“富者愈富” |
| [E98](2-after-closure/experiments/E98-capability-vs-loss-recovery.md) | 损伤后损失很快恢复，能力为什么没跟上？——“慢”还是“卡住” |
| [E99](2-after-closure/experiments/E99-where-role-memory-lives.md) | 受损头长回原角色，记忆存在哪里——它自己保留的 OV，还是下游读它的头？ |
| [E100](2-after-closure/experiments/E100-de-novo-recruitment-vs-age.md) | 训练早一些的模型，能不能从头招募新的承担者？ |
| [E101](2-after-closure/experiments/E101-coupling-law-on-ioi.md) | “残留耦合”规律在 IOI 名字移动头 8.9 上是否成立 |
| [E102](2-after-closure/experiments/E102-coupling-law-across-functions.md) | 耦合规律在另外四个功能上是否成立——事先预测 |
| [E103](2-after-closure/experiments/E103-regrowth-lag-coupling-gain.md) | 受损头长回来之前为什么要停滞 700–1000 步？——耦合强度决定停滞长度 |
| [E104](2-after-closure/experiments/E104-coupling-law-at-410m.md) | 耦合规律在 Pythia-410M 上是否成立 |
| [E105](2-after-closure/experiments/E105-unlearning-bridge.md) | 把“角色存于接口”接到真实的遗忘 / 重学问题上 |
| [E106](2-after-closure/experiments/E106-frozen-surgery.md) | 网络其余部分冻结时，完整重置的头能否长回原角色？ |
| [E107](2-after-closure/experiments/E107-dormancy-lock.md) | 联合训练中进入休眠的头会被锁死吗？——更高学习率、更长窗口下冻结 vs 联合 |
| [E108](2-after-closure/experiments/E108-where-unlearning-lives.md) | 遗忘在功能上落在哪里？——注意力模式修补分解 |
| [E109](2-after-closure/experiments/E109-capital-unlearning.md) | 读取侧 / 写出侧的不对称，在事实回忆与定向重学攻击下是否成立 |
| [E110](2-after-closure/experiments/E110-general-data-pullback.md) | 为什么一般训练会撤回读取侧的遗忘、却不撤回写出侧的遗忘？ |
| [E111](2-after-closure/experiments/E111-footprint-breadth.md) | 读取侧遗忘是否在一般文本上大范围扭曲注意力？ |
| [E112](2-after-closure/experiments/E112-footprint-regularized-unlearning.md) | 把读取侧遗忘的足迹压窄，它还会被良性训练撤回吗？——足迹机制的因果检验 |
| [E113](2-after-closure/experiments/E113-added-behavior-retention.md) | 后加的行为（玩具“拒答”）在良性训练下能否保留——读取侧 vs 写出侧 |
| [E114](2-after-closure/experiments/E114-information-availability.md) | 遗忘后任务信息是否还在？——信息存留假说 |
| [E115](2-after-closure/experiments/E115-who-carries-recovery.md) | 良性重学后，恢复的功能由谁承担？——“绕过”的执行者 |
| [E116](2-after-closure/experiments/E116-format-preserving-unlearning.md) | 保住上游特征的原格式，写出侧遗忘会变得可被良性训练撤回吗？——格式机制的因果检验 |
| [E117](2-after-closure/experiments/E117-unlearning-asymmetry-410m.md) | 读取侧 / 写出侧的良性重学不对称在 410M 上是否成立 |
| [E118](2-after-closure/experiments/E118-npo-asymmetry.md) | 换一种遗忘方法（NPO），读取侧 / 写出侧的良性重学不对称是否仍成立 |
| [E119](2-after-closure/experiments/E119-attractor-basin.md) | 原有分工是继续训练的吸引子吗？——写出接口的连续扰动与吸引域边界 |

### 代码与结果
与主题 1 共用 [../scripts/](scripts)（`e89_labor.py`、`e93_lesion.py`、`e105_unlearn.py` 等）与 [../results/](results)。
