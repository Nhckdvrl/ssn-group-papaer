## 论文形态卡 — in-context-evidence-structure — 2026-10-05（agent 草稿，待人审）

- **一句话主旨（2026-10-05 22:00）：** *Nearest, not newest*：in-context learner 检测得到**输出漂移**（标签流、输出格式、输出语言的变化——方向与 exact Bayes 的变化点推断一致），检测不到 **concept drift**（输入→输出关系的变化——分类映射被可交换地汇总、词汇/字符串函数只有固定 recency）。即使把新 regime 用大写标出，模型会规范地改写格式，却以近乎随机的概率使用新映射。
- **论文形态：** 构念引入 + 测量（方向相反检验）+ 普遍性地图 + 机制 + 因果“为什么” + 后果。
- **manuscript-critical contributions：**
  1. ✅ 测量：exact 层级 Bayes oracle（λ×ε）+ 方向相反（前缀噪声）符号检验（对任何正权重可加 + 单调链接模型都给出 ≥0，只有结构推断给 <0）+ 成簇/新旧块检验。（C01，L3）
  2. ✅ 输出漂移被跟踪：标签流 13/13 模型；格式与输出语言多数模型。（C03，L3）
  3. ✅ concept drift 不被跟踪：分类映射 13 模型 × 多任务（nonce、SST、奇偶、大小、类别条件变换）全部方向错；T=64、指令、可见 CoT、thinking（20k token）、时间戳都不改变；“最近邻不是最近期”（E21/E04）。（C02，L3）
  4. ✅ 同一答案内的解离（E22，3 模型）：格式通道规范、映射通道平坦。（L3）
  5. ⚠️ 机制：任务状态 patch 复现时间签名（E17b，ρ=0.95，单模型）；标签流游程头（E10）。
  6. ⚠️ 为什么：toy 任务同质训练复现解离（E12）；易变分类 LoRA 只把分类推到 recency（E18，2 种子 + 剂量）。
- **主图：** Fig1 范式与 oracle 预测；Fig2 E22（`fig_marked_drift.png`）；Fig3 跨格式×模型地图（`fig_structure_selectivity.png`）；Fig4 最近邻不是最近期（E21）；Fig5 任务状态 patch；Fig6 训练统计（toy/LoRA）。
- **基线：** set / sequence / meta oracle；固定位置核（可加）；样例（GCM）模型；指令（change/noise header）；可见 CoT / thinking。
- **证据标准：** 每格式 200–300 base 配对设计，bootstrap 95% CI；13 模型；确认版使用全新种子、无 nonce 依赖。
- **定位表摘要：** Kossen'24（recency）、Falck'24（martingale）、Bigelow'25（计数 belief）、Jiao'26（单冲突）、Dudley'26/Qin'26（训练模型的变化检测）、Cho'25/Yang-Cho-Inoue'26（检索电路/TR-TL）、Yin & Steinhardt'25（FV vs induction）、Wang'26（agentic 反转学习）、Xu'26（BeliefTrack）。增量见 I01。
- **风险登记：**
  - ±3 的时间敏感强度因模型而异（Qwen2.5/Mistral 弱）→ 关系性全局变换扩展（字母±1、数字±1/±10）运行中；若部分模型弱，表述为“全局规则可被跟踪（强度随模型）vs 分类映射在所有模型都不被跟踪”的不对称主张。
  - nonce 词库未经 step-5 审计（配额用尽）→ 主结论全部可由无 nonce 的确认版支撑；nonce 规则实验作为补充，待配额恢复后补审计。
  - toy 训练 v1 未学会分类 → v2 运行中；E18 LoRA 作为真实模型上的因果检验。
- **目标会议：** ICML / ICLR（主），备选 ACL/EMNLP 叙事（认知科学 changepoint/oddball + NLP 分类 ICL）。
- **本次决定：** 继续（agent 决定；人可否决）。
