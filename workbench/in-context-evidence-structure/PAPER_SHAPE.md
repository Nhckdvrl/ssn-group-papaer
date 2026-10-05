## 论文形态卡 — in-context-evidence-structure — 2026-10-05（agent 草稿，待人审）

- **一句话主旨：** In-context learners track changes in *what to do*, but not in *which input gets what*：当 regime 是作用于所有输入的全局规则（变换、标签流）时，LLM 随时间整合证据、能区分噪声与变化（方向与 exact Bayes 一致）；当 regime 是按输入类别路由的映射（分类、类别条件变换）时，LLM 按内容检索并把证据当可交换集合汇总——对变化“视而不见”。（与 T16 原问题“order 何时是 nuisance、何时是 signal，模型知不知道”直接对应：模型“知道”，但只对全局规则知道。）
- **论文形态：** 构念引入 + 测量（normative noise-vs-change 测量）+ 机制 + 因果“为什么”（训练统计）+ 修复。
- **manuscript-critical contributions：**
  1. ✅ 测量工具：exact 层级 Bayes oracle（规则 × 波动 λ × 噪声 ε）+ 三个方向性检验（成簇选择性、前缀噪声方向相反检验、A→B vs B→A），可用于任何 ICL 任务。（C01）
  2. ✅ 主现象：分类式 ICL 的 change blindness——13 个模型 / 4 族 / 0.6–32B / base 与 post-trained / 自然语言（SST）/ T=64 / 指令与可见 CoT 不改变；适应是局部的（E04）。（C02）
  3. ✅ 边界：全局规则时间敏感（标签流、大写↔反转、±3；关系性变换扩展中），按输入路由的规则时间盲（规则、SST、奇偶、大小、condarith）；隐式先验：表层 λ≈0.02–0.05 vs 分类 λ=0。（C02/C03）
  4. ⚠️ 机制：分类 = 内容检索（注意力按相似度、无可迁移任务向量）；全局规则 = 随时间更新的任务向量（E17）+ 标签流游程头（E10，−73%）。待：多模型复现 E17。
  5. ⚠️ 为什么 + 修复：E18 LoRA（易变 vs 稳定分类流）与 E12 toy 训练进行中。
- **主图：** Fig1 范式 + oracle 预测（方向相反检验）；Fig2 13 模型 × {全局, 分类} 的 CSIn/NDIn 散点（核心图）；Fig3 边界地图（9 种任务格式）；Fig4 局部更新（E04）与 T=64 A→B vs B→A；Fig5 机制（注意力组织 + 任务向量 patch + 消融）；Fig6 LoRA 修复迁移到自然语言分类。
- **基线：** set / sequence / meta oracle；固定位置核（可加）；样例（GCM）模型；指令（change/noise header）；可见 CoT / thinking。
- **证据标准：** 每格式 200–300 base 配对设计，bootstrap 95% CI；13 模型；确认版使用全新种子、无 nonce 依赖。
- **定位表摘要：** Kossen'24（recency）、Falck'24（martingale）、Bigelow'25（计数 belief）、Jiao'26（单冲突）、Dudley'26/Qin'26（训练模型的变化检测）、Cho'25/Yang-Cho-Inoue'26（检索电路/TR-TL）、Yin & Steinhardt'25（FV vs induction）、Wang'26（agentic 反转学习）、Xu'26（BeliefTrack）。增量见 I01。
- **风险登记：**
  - ±3 的时间敏感强度因模型而异（Qwen2.5/Mistral 弱）→ 关系性全局变换扩展（字母±1、数字±1/±10）运行中；若部分模型弱，表述为“全局规则可被跟踪（强度随模型）vs 分类映射在所有模型都不被跟踪”的不对称主张。
  - nonce 词库未经 step-5 审计（配额用尽）→ 主结论全部可由无 nonce 的确认版支撑；nonce 规则实验作为补充，待配额恢复后补审计。
  - toy 训练 v1 未学会分类 → v2 运行中；E18 LoRA 作为真实模型上的因果检验。
- **目标会议：** ICML / ICLR（主），备选 ACL/EMNLP 叙事（认知科学 changepoint/oddball + NLP 分类 ICL）。
- **本次决定：** 继续（agent 决定；人可否决）。
