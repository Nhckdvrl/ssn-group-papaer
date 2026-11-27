# RL vs 蒸馏（同一 base）文献调研，2026-11-28

已读全文（pdftotext，含实验/附录主要部分）：2610.24663、2603.22446、2510.00553 (相关节)、2504.13837 (§4.2)、2509.21128 (摘要+设置，正文未逐节细读)、2507.14843 (仅元数据+引言，正文未细读)、2605.06241 (摘要+§4 KL-LoRA)、2609.28145 (摘要+引言)、2505.21067 (摘要+引言)、2604.14084 (摘要)、Qwen3 技术报告 Table 21。
**未读**：RL's Razor、SFT memorizes RL generalizes、Mukherjee 子网络、The Path Not Taken、Thinking Machines 博客、“2611.32131”(未能确认存在)、Wang et al. 2026（"Alright"开头提示，见 2610.24663 引用，未找到原文）。这些不得在引用里当作已核对。

## 逐篇

**1. Yue et al. 2504.13837（NeurIPS 2025）**。Qwen2.5-Math-7B base vs Oat-Zero(RL) vs DeepSeek-R1-Distill-Qwen-7B(R1 蒸馏)。§4.2：蒸馏模型 pass@k 全程高于 base，“unlike RL … bounded by the capacity of the base model, distillation introduces new reasoning patterns”。度量：pass@k 曲线。注意蒸馏模型是 DeepSeek 发布的 7B，与 RL 模型并非同一 RL 起点、训练数据量不同，也不看 pass@1 增益是否相等、不做逐题或 token 层面比较。与我们 (a)(b) 距离远，但 pass@8 分叉的“方向”已被它拥有。
**2. Matsutani et al. 2509.21128 “RL Squeezes, SFT Expands”（ICLR 2026）**。1.5B/7B/14B，数学+代码，RL 与 SFT/蒸馏轨迹聚类、推理图。声明：RL 压缩错误轨迹，SFT 扩张正确轨迹；RL 使步级节点度分布衰减约 2.5 倍陡，SFT 约 1/3 平。度量是轨迹/步骤图拓扑，不是 token 位置，不做前缀交接。不同的是模型对不是严格同一 base 同等 pass@1。(a)(b) 距离远。
**3. Wu et al. 2507.14843 “Invisible Leash”（arXiv v5，未见会议标注）**。逐题 “empirical support dynamics”：RLVR 下失去支持的题多于获得的（shrinkage > expansion）。只看 RLVR，不含蒸馏对照（grep 无同 base 蒸馏实验）。与我们的“逐题 overlap”有方法近邻（题级匹配），但无蒸馏。
**4. Qwen3 技术报告 Table 21**。Qwen3-8B：off-policy 蒸馏 55.0 → +RL 67.6（17,920 GPU h）；→ +on-policy 蒸馏 74.4（1,800 GPU h）；括号内 pass@64 分别 90.0 / 90.0 / 93.3（AIME24）。是同一起点之后 RL vs on-policy 蒸馏，起点是已蒸馏模型，不是 base，且无 token/题/前缀分析。给出“蒸馏 pass@k 上升、RL 不升”的旁证（pass@64: 90.0→90.0 vs →93.3）。注意：官方 Qwen3-8B 还含 thinking-mode fusion 与 general RL，不是纯蒸馏。
**5. Meng et al. 2603.22446（ICLR 2026，Qwen Pilot）**。Qwen2.5-32B 为主，另 Qwen2.5-Math-7B、Qwen3-8B-Base、Mistral-24B；DAPO/GRPO。JS 散度逐位置：DAPO >80% 位置几乎无变化；跨采样：往 base 注入约 4% RL token 即恢复大部分 AIME24 增益（~8%→>25%），反向把 5% base token 换进 RL 会掉回 base。与 SFT（Qwen2.5-32B，附录 A.4）对比：SFT 的高散度位置更多、遍及整段回复。这是对 (a) 最近的已发表工作，且含 RL vs SFT 的稀疏度对比；但 SFT 是自己训的小规模 SFT，不是 Qwen3 官方强到弱蒸馏，不比 pass@1 增益相等的情形，无逐题交集，无前缀长度扫描。
**6. Zhang et al. 2610.24663（arXiv 2026-10，Meituan LongCat）**。Qwen3-4B-Base 与其 GRPO 模型，120 道 AIME22–25；另 3 个模型对 MATH-500、Qwen3-8B 做 coverage 复核。“rl-replace”：仅在两模型 greedy 不同处（约 4% 位置）借 RL token，恢复 90.5% pass@1 增益；强制 base 以 “Alright” 开头恢复 35%；开头之后的替换再加 5.2 点；k=256 时 67.5% 高于 RL 自身 (61.4%)。**对 (a) 最近**，还包含我们已设计的 Alright 提示控制。无蒸馏、无逐题交集、无前缀长度扫描（只做 1 个开头 token）。
**7. Akgül et al. 2605.06241 “sparse policy selection”（arXiv，USC）**。多家族多规模，RL 的有益改动：1–3% 位置，促进的 token 总在 base top-5，base 自己的熵可定位这些位置（无需 RL 模型），随机位置修正失败；KL-LoRA 蒸馏 RL 教师到 rank-32 适配器即可复现；据此提出 ReasonMaxxer。对 (a)“高熵位置的选择”几乎同题；仅 RL，蒸馏只作工具。
**8. Cai et al. 2510.00553（ICLR 2026，即你们的 DAPO 来源）**。Rank-1 子空间复现 RL 增益；明确含 DIST (R1-Distill-Qwen-7B vs Qwen2.5-Math-7B)、SFT (Qwen3-8B-Base+DeepMath-103K)、On-Policy Distillation (Qwen3-8B-Base-Open-Thoughts-OPD) 控制，声称这些“yielded neither property”（rank-1 主导 + 近线性演化）。前缀实验（Fig.14）：把 Rank-1 模型推理链前 n token 喂 base，**前 20 token 即近全参数更新**——只对 RL/Rank-1 做，**未对蒸馏做前缀对照**。即 (b) 的 RL 一侧已有，蒸馏一侧空缺。注意它比较的是参数更新结构，不是行为层面的“同增益不同机制”。
**9. Hu et al. 2505.21067（arXiv）**。920 条样本蒸馏优于 zero-RL；蒸馏模型更常用拟人 token/逻辑连接词，多视角与元认知行为多。度量是 token 频率与行为标注。
**10. TIP 2604.14084 / OPD-for-RL 2609.28145（arXiv）**。OPD 内部的 token 重要性（高学生熵 + 低熵高分歧）；OPD 作为 RL 的前置。与我们关系：提示蒸馏信号来自“学生自信但错”的低熵位置，RL 靠高熵探索——是 (a) 的对立假设，值得检查“低熵位置的选择”在蒸馏里是否也有贡献。

## 结论（直说）
- “同一 base，RL vs 蒸馏，pass@1 增益相等但机制不同”**没有作为一个整体被确立**。找不到一篇在同一 base、匹配 pass@1 增益的前提下，对 RL 与强到弱蒸馏做逐题交集、高熵位置选择、前缀交接长度的论文。
- 已被拥有的子主张：
  - RL pass@k 不超 base，蒸馏超：Yue 2504.13837（+Qwen3 报告 Table 21 旁证）。你们的 pass@8 分叉**不是新结果**，只是在同一 base 与官方 Qwen3 上的复现。
  - RL 改动稀疏、集中于高熵位置，借 ~4% RL token 恢复大部分增益：Meng 2603.22446、Zhang 2610.24663、Akgül 2605.06241（三篇均 2026，且独立）。(a) 对 RL 一侧**已被占**。
  - 开头短前缀/开头 token 恢复增益：2510.00553（20 token）、Zhang（Alright 35%）、Wang 2026（未读）。(b) 的 RL 一侧**已被占**。
  - RL 改动比 SFT 稀疏：Meng 附录 A.4、2510.00553。
  - RL 压缩/SFT 扩张的轨迹层面：Matsutani。
- 仍开放：(1) 蒸馏一侧的 (a)(b)：蒸馏模型在 base 高熵位置的选择能否恢复其增益、需要多长前缀（2510.00553 暗示蒸馏“不是低秩/稀疏”，但没做前缀）；(2) pass@1 增益相等时的逐题交集（split-half 校正 r≈0.6），仅 Invisible Leash 有题级匹配而无蒸馏；(3) 把 pass@8 分叉与“选择位置是否在 base top-k 内”联系起来（蒸馏是否把 base 概率近 0 的 token 提上来）。这是最有增量的位置：核心问题应表述为“蒸馏增益里有多少超出 base top-k 支持”，而非 RL 稀疏性本身。
- 风险：若蒸馏的结果也是“稀疏高熵选择可恢复”，则只是 Meng/Zhang 在蒸馏上的复制；若不是，则是真正的差异，但需在多个检查点与种子上稳固。

## 顶级论文的开篇问法（引文）
- Yue 2504.13837：问题是“whether … RLVR truly expands … reasoning boundary or mainly amplifies” base 已有的；给出一个可度量的边界（pass@k at large k）。
- Zhang 2610.24663：“These observations describe what changes, not which change produces the gain.” 然后把观察变成对 base 的干预，逐项问“恢复多少增益”。
- Wu 2507.14843：“Does the current practice of RLVR expand base models’ reasoning capabilities, or simply reinforce patterns base models already know…?”
共同点：用一句有争议的领域问题开头，随后给出可干预或可度量的对象；不做大而空的二分。
