## 论文形态卡 — in-context-evidence-structure — 2026-10-06（agent 草稿，待人审）

- **一句话主旨：** In-context learners index evidence by output. 冻结 LLM 按输出标签存放输入-输出证据：同一输出下的证据按输入相似度加权、在时间与上下文上可交换；因此改变“用哪些输出”的漂移被规范追踪，而把已有输出重新分配给不同输入的漂移（concept drift、因人而异的映射）被混在一起，混合程度随新旧输出标签的语义相似度增加。
- **工作标题：** *In-Context Learners Index Evidence by Output: Why LLMs Detect Output Drift but Miss Concept Drift*
- **论文形态：** C（理论 + 受控）+ B（测量）。
- **manuscript-critical contributions（证据等级见 CLAIMS）：**
  1. 测量：exact 层级 Bayes oracle + 方向相反检验（C01，L2 → 待校对 L3）。
  2. 普遍地图：输出侧变化规范、条件结构可交换；13 模型 0.6B–32B，thinking/指令/时间戳不救（C02、C03、C05，L2）。
  3. 同一答案内的解离与“不重置”（C07，L2）；时间结构只在“偏向新输出”的成分上（C08，L2）。
  4. 按输出存放：分隔阶梯、上下文交互泄漏、语义泄漏定律（C09、C10，L2）。
  5. 建设性修复：换输出词使 concept drift 可追踪（C11，L2）。
  6. 机制：读标签头 + 不可改写的锚点 + 因果修补（C12，L2；L4 需头消融与非 Qwen 复现）。
- **主图：** Fig1 范式与 oracle 的方向相反预测；Fig2 跨任务 × 模型地图（`fig_structure_selectivity.png`）；Fig3 同一答案内的解离（`fig_marked_drift.png`）；Fig4 看最近邻不看最近期（`fig_nearest_not_newest.png`）；Fig5 分隔阶梯 + 语义泄漏定律（`fig_label_similarity_leakage.png`）；Fig6 换词修复（E32）；Fig7 机制（读标签头注意力键 + 因果修补层曲线）。
- **基线：** set / sequence / meta oracle；固定位置核（可加）；样例模型（GCM）；指令；可见 CoT / thinking；边缘-only oracle（E28）。
- **证据标准：** 每格式 200–300 base 配对设计、bootstrap 95% CI；确认版全新种子；机制实验带健全性检查与阳性对照。
- **定位表摘要：** 机制层最近邻 Wang et al. EMNLP'23（标签词锚点）；行为层 Kossen'24、Falck'24、Zhao'21、Xiong'25、Dudley'26 / Qin'26、Cho'25 / Yang-Cho-Inoue'26。增量见 `ideas/I04-output-indexed-evidence.md` §6。
- **风险登记：**
  - 压缩为“ICL = kNN + 标签偏置” → 用方向相反检验、同一答案内分离、语义定律与因果机制回应。
  - 偏置成分的规范符号在弱信号下部分来自注意力竞争（E37）→ “输出侧近似 Bayes”的主张以标签流与格式通道为主证据，E28 只作为分解证据。
  - 机制只在 Qwen 家族 → 恢复推进时先做非 Qwen 复现与头消融。
  - 尚未做独立校对 → 进入 candidate 前必须做。
- **目标会议：** ICML / ICLR（主）；ACL / EMNLP 叙事并行。
- **本次决定（人，2026-10-06）：** I04 为主 idea；暂停推进，留作之后主推的 candidate。


## 论文形态卡 — 2026-10-09 更新（agent 草稿，待人审）
- **一句话主旨（候选）：** In-context evidence is indexed by output, not by source. 把多个来源（标注者 / 用户 / 规范版本）的样例放进同一上下文时，LLM 按输出标签汇集证据：来源标签（名字、时间、领域）分不开证据，只有输出词能分开；因此带 ID 的多人提示丢掉约一半的个人信号，而每个来源用独立的输出词即可恢复。
- **证据链：** 受控现象与语义泄漏定律（E30–E35，13 模型）→ 真实数据后果（E46 / E47 / E49：Measuring Hate Speech、GoEmotions，8 模型 4 家族，同词保留 0.35–0.58，换词恢复 0.80–1.27）→ 机制（E36–E39、E48：读标签头读入他人锚点，换词后读出层面分隔）→ 指令只在部分模型有效（E46b）。
- **社区在用、被检验的推断：** perspectivist / 个性化 ICL 认为模型会按 ID 条件化各人的标注习惯（近邻：arXiv 2605.28802 提示有限且不稳定；ACL'25 2502.20897 微调更好；均未解释原因，也未给出词表修复）。
- **剩余风险：** E50：在主效应、远离决策边界的真实情形下，logit 层面的一半区分损失几乎不影响个人标签准确率（保留 86–98%）→ “有什么用”需改为“何时有代价”（交互型 / 靠近边界），尚缺真实个人标签的交互型数据；机制已在 Qwen3-8B、Qwen2.5-7B、Mistral 复现；独立校对未做；gemma 换词只部分恢复；真实数据只有两个（都是社交媒体文本标注）。
- **目标会议：** ACL / EMNLP（perspectivist 与个性化叙事）为主；ICML / ICLR（ICL 机制叙事）并行。

- **2026-10-09 判定（E50–E52）：** 三个现实情形中，logit 层面的一半区分损失都没有转化为明显的实际预测代价（剩下的区分通常已足够；指令常能补救）。站得住的是机制（读出层面分隔，2 家族 3 模型）、语义泄漏规律、logit 层面的现象；“读者应改变的做法”缺乏有分量的证据。**agent 判断：作为“ICL 证据按输出存放”的机制与规律分析尚可，未达到“合格的强贡献”；是否以此形态投稿由人决定。**

## 2026-10-10 证据校正（保持旧形态卡作历史，不重写论文）
E58–E64未把ICES判为trivial，也未确认其为强机制论文。C14–C16新增L1：来源差分可跨label、native source效应经name-key及query内部消息传递；Qwen与Mistral的label消息时序不同。旧标题保留为候选，不锁定全文。
- source probe可读出不定位自然路由；trained query adapter成功不证明native完整算法存在；E56共20层、1.31M trainable weights。
- “native默认完全不用source”撤回；“entity binding＋ICL不能组合”仍不是成立的中心发现。
- 目前较好的切入点是**source-conditioned computation在query内部怎样形成、后续label检索怎样处理它**；末位直接读取不足以代表全部ICL学习/绑定过程。
- 是否为新认识取决于能否正面对齐Cho shortcut/FV、CBR、Mixing Mechanisms与Test then Route，并预测新query布局、任务与强模型边界。“有更早计算”“QK/V不同”本身不构成novelty。
- real-text控制任务不等于真实个人标注者规则；全文与独立机制校对均未完成。详见`REVIEW_2026-10-10.md`与各卡原始CI。
