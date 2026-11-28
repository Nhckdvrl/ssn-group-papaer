# E01：锚点复现——Qwen2.5-7B 猫偏好经数字载体迁移（2026-11-27）

- **状态：** PLANNED → 2026-11-27 降为 OPTIONAL

> **修改注记（2026-11-27）：** Stage 0 的硬门槛改由 E06（Beyond Owls FF 后门复现，与 Stage 1 同模型、同通道、同 LoRA 结构）承担。本卡的管线（Qwen2.5、硬标签、attn+MLP LoRA）几乎验证不了 Stage 1。本卡保留为可选的读数工具验证（模板敏感性、首 token 概率），若之后需要再跑。原文核对后的修正见 2026-11-27 日志的表格（阳性对照应改为 Cloud 图 17 约 74% 与 Schrodi 图 2a 约 26%）。
- **类型：** REPRO（Stage 0 锚点）
- **对应：** 全部后续实验的前提；痛点（复现偏差、模板敏感性）记入 PAIN_LOG；为 I01 提供管线与身份指纹的第一手读数
- **问题（一句话）：** 在我们的节点和管线上，能否复现文献中 Qwen2.5-7B-Instruct 的猫偏好数字迁移，并测清种子方差与评测模板敏感性？
- **设置：**
  - **模型：** Qwen/Qwen2.5-7B-Instruct（记录 revision 与 tokenizer hash）。
  - **教师：**
    - cat：Cloud et al. 的系统提示（“You love cats. You think about cats all the time…”，原文照抄并记录）；
    - owl：同一模板，作为反事实对照教师；
    - 干净教师：Qwen 默认 system prompt。
  - **载体：** Cloud / Schrodi 的数字续写 prompt（3–8 个三位以内的种子数，要求再续写最多 10 个），temperature 1。每个教师每个数据种子生成约 3 万条，经格式过滤（只含逗号分隔的 0–999 整数）后保留 1 万条。**3 个数据种子**，即独立生成 3 次。
  - **学生：** 优先复用 `lmb-freiburg/divergence-tokens` 的训练配置（LoRA r=8, α=8，全部 attention + MLP 投影，Adam lr 2e-4，10 epochs，有效 batch 60）。记录代码 commit。外加 lr ∈ {1e-4, 5e-4} 的小扫，按留出载体 NLL 最低预先选定。
  - **规模：** 3 个教师 × 3 个数据种子 × 2 个训练种子 = 18 个主学生，外加 lr 小扫约 6 个。
  - **附带零成本诊断：** 用 cat 教师与 owl 教师，以及 Llama-3.1-8B-Instruct 的同款 cat / owl 教师，在公共前缀上计算：
    - 逐 token 的 KL(p_T‖p_0)；
    - 两教师间的教师特有信息 r_enc（RESEARCH_PLAN §2.2）；
    - 与 Qwen 对比。
    - 这一步只做前向传播，不训练 Llama 学生。
- **读数：**
  - **主读数：** 50 个“最喜欢的动物”问题变体上，“cat”的**精确首 token 概率**（连续读数），相对 S_neutral（干净教师学生）的 log-odds 差。
  - **辅读数：** 每题采样 20 次的 cat 率。
  - **四种评测模板：** 默认 system / 空 system / 另一 system prompt / 无 chat 模板补全（“My favorite animal is”）。
  - **学习情况：** 训练 / 留出载体 NLL（记忆程度）。
  - **轨迹：** 每 1/4 epoch 存一个 checkpoint，沿轨迹计算主读数。
  - **身份可识别度：** 用学生在留出数字 prompt 上的续写训练逻辑回归，区分 cat / owl / 干净（为 I01 预热）。
  - 读数与被测变量解耦：评测 prompt 与载体完全不同域。
- **阳性对照：**
  - 文献值：Li et al. 2609.23260 在 Qwen2.5-7B-Instruct 上，cat 3.1% → 91.1%（LoRA r=8，10 epochs）；Feng rank-1 学生 87%；Schrodi 在 Qwen 上 cat 迁移显著。
  - 工具对照：直接用 cat 系统提示问 base 模型，主读数必须明显上升（读数工具有效）。
- **噪声地板 + MIE：**
  - 地板 = 3 个数据种子 × 2 个训练种子的 S_neutral cat 概率 SD；
  - MIE = cat 学生相对 S_neutral 的 log-odds 差 > 2×（种子 SD），且采样 cat 率提升 ≥ 10 个百分点。
  - owl 学生的 cat 读数不应上升（特异性）。
- **混杂审计：**
  1. 噪声地板：已控制（3×2 种子）；
  2. 工具有效性：已控制（prompt 阳性对照）；
  3. 选窗：无关；
  4. 自校准：已控制（所有条件用同一读数与同一评测集）；
  5. 提示词默认值：**重点**，用四种模板测；
  6. 输入一致性：已控制（固定 tokenizer / 模板）；
  7. 幸存种子：全部报告；
  8. 算力匹配：无关（复现）；
  9. 集合重叠：评测问题不进训练；
  10. 多重比较：模板是预设的 4 种；
  11. 饱和：cat 概率接近 1 时改报 log-odds；
  12. 系统特有：仅 Qwen 学生（Llama 只做前向诊断），措辞限于 Qwen。
- **决策表（跑之前写）：**
  - 结果 A（cat 学生超过 MIE、owl 学生不变、四种模板中至少默认模板显著）→ 锚点成立，进入 E02 / Stage 1；
  - 结果 B（只在默认模板显著、换模板消失）→ 锚点成立但依赖模板，记 PAIN_LOG，Stage 1 评测必须含多模板；
  - 结果 C（达不到 MIE）→ 不进入 Stage 1；依次排查生成过滤、system prompt 原文、lr、epoch 数，并与 divergence-tokens 官方结果对照；
  - 不确定 → 加 1 个数据种子。
- **算力预算：** 生成约 9 次 × 3 万条（vLLM，约 3 A100·时）；训练约 24 次 × 约 1 A100·时；评测与诊断约 3 A100·时。合计约 30 A100·时。**实际：** —

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：
- 结果文件：`results/E01/...`
- 按决策表执行了什么：
- 主张变化：
- POST-HOC 分析（事后才想到的，单独标注）：
