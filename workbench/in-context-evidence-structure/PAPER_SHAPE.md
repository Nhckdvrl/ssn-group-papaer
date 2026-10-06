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
