# RL(VR) 选出/放大基座已有模式：近邻文献核查（2026-11-28）

阅读深度：Wang 2610.06851、Zhang 2610.24663、Echo Chamber、Venhoff、Spurious Rewards、Qwen3 报告、OLMo 3 报告、Karan&Du、1-shot RLVR、2608.00220、2608.29188、2605.28295 均下载全文用 pdftotext 读过（Wang/Zhang/Qwen3/OLMo3 读了方法、结果、附录表与局限；其余读了摘要、引言和相关章节，未逐段读完附录）。Entropy Minimization (Agarwal 2505.15134)、Gan&Isola 2026 只从引用得知，未读。

## 逐篇

**1. Wang et al. 2610.06851, "Base Models Can Reason By Taking a Cue From Training Data"（MIT/Berkeley/UW/AI2，arXiv 预印本，非 EACL）。最近邻。**
- 设置：Olmo-3-7B/32B、Qwen3-4B/14B(-Base)、SmolLM3；预填 1–2 个 token（Olmo ".\n\n Okay"，Qwen3-14B "Alright,"，Qwen3-4B ".\n To"），不改权重。RL 对照：官方 Olmo RL-Zero；Qwen 的 RL 是作者自己在 MATH 上跑 300 步 GRPO。32 rollout，预算 31,744 token。
- 结论：MATH-500 Olmo-7B 42→78（RL 75），Qwen3-14B 72→87（=RL）；GSM8K/AMC/AIME24 上"匹配或超过 RL"；RL 把 "Alright," 概率从 0.04 抬到 0.58，base 与 RL 的 KL 集中在前两个位置；用 RL 生成的开头让 base 续写恢复 RL 精度；预填后再做 RL，起点已等于 RL 约 50–100 步。cue 在相同 token 预算下仍有效（图 4）；对 Olmo mid-training 数据做 "okay→chicken" 反事实，证明 cue 的效果来自训练数据关联（Olmo mid-training 里 "Okay" 开头占合成推理轨迹 83%）。
- 范围自述（§6）：只研究 R1-Zero 式单阶段 RL；cue 有模型依赖（Llama-3.1-8B 无有效 cue，Qwen2.5-Math 基本无增益）；"多阶段后训练可能带来 cue 之外的能力"。
- 没有的：无蒸馏臂（只在安全小节拿 Olmo Instruct/Think-SFT 作参照）；无 Qwen3-8B-Base；无逐题 RL-vs-cue 相关；无 "RL 训练过的题" 分析；无 prefix-handoff（续写谁的）实验；无"RL 只在前 ~32 token 起作用 vs 蒸馏贯穿"的对比。
- 他们的问题表述："if reasoning may already be present in the base model, how little intervention is needed to elicit it?"；"This leaves open whether RL teaches novel reasoning capabilities or merely exploits capabilities acquired beforehand."

**2. Zhang et al. 2610.24663, "What RL Brings to Reasoning: A Few Decisions the Base Model Would Not Make"（UCSD/Meituan/CUHK-SZ，预印本）。**
- 设置：Qwen3-4B-Base 与其 GRPO(DAPO-Math-17k, verl, step 460) 模型；120 道 AIME22–25 为主，MATH-500 为辅；温度 0.6，**上限 8,192 token**，16 样本（AIME）。
- 强制的内容：只强制单词 "Alright"（也试了 "Alright, I"，无额外增益）。AIME pass@1 10.00→13.23，恢复 RL 增益的 35%（RL 19.32）。rl-replace（仅在两模型 greedy 不一致的约 4% 位置取 RL 的 token）恢复 90.5%；开头之后的替换再加 5.2 点。固定的 "Wait" 规则无效。Power sampling 8192 预算下无增益。
- 与我们的距离：**他们的结论方向相反**——在 Qwen3-4B-Base/AIME/8k 预算下开头只给 35%，"后面的选择贡献更大"。我们是完整短语 "Alright, I have this problem"（RL 模型的实际开头），Qwen3-8B-Base，MATH L1–3/L5/OlympiadBench，且开头之后 base 自取 argmax 无益。两者可并存：难度（AIME vs 中低难度）、预算（8k 截断）、模型尺寸、cue 全长度是可检验的差异点。他们没做 MATH-500 上的 Alright 单独强制。引言里他们明确提到 RL 模型开头是 "Alright, I have this problem..."，base 开头多样（15.6 vs 3.2 个不同开头/16 样本）。
- 问题表述："These observations describe what changes, not which change produces the gain." 他们引用 Wang 2026 为 "a short opening cue … recovers much of the RL gain"。

**3. Venhoff et al., ICML 2026 Spotlight（2510.07364）。** 9 对 base/thinking（0.5B–32B，Qwen2.5/Llama，不含 Qwen3）；用 SAE 分类推理行为，base 上学得的 steering 向量 + 触发分类器的"混合模型"恢复 RL 型 thinking 模型 base→thinking 差距约 76%，恢复 SFT 蒸馏型（R1-Distill）仅约 11%（小的两对约 0）。结论："RL mainly teaches a model how to orchestrate mechanisms the base model already has, while SFT distillation installs new ones." 与我们的距离：它给了"RL 可被 base 内机制恢复、蒸馏不行"的机制侧证据，但手段是 steering 向量而非固定开头；无 Qwen3-Base、无 prompt/cue 对照、无逐题对齐。**与我们"蒸馏超过 cue 只在难题"的方向一致，但不是同一测量。**

**4. Spurious Rewards, Shao et al. 2506.10947（UW/AI2 等，预印本）。** Qwen2.5-Math-7B 上随机奖励 +21.4 MATH-500（真奖励 +29.1），归因于 GRPO 剪裁偏置放大预训练中已有的 "code reasoning"（65%→90%+）；Llama3/OLMo2 无效。设置含"prompt 引出"检验（Qwen2.5-Math 对无关 prompt 也极敏感）。距离：同属"RL 选择已有模式"，但对象是代码推理、Qwen2.5-Math，不是开头 cue；它警告结论必须跨家族验证——我们已有 Qwen3 + Olmo-3（Wang）两族，仍缺非推理 mid-training 基座。

**5. Echo Chamber, Zhao et al., COLM 2025（2504.07912）。** 在开源数据混合上从零预训练 150M/1B 模型，PPO/GRPO/ExpIt 后 RL 收敛到混合中的单一格式分布（如 TinyGSM 风格），伴随精度上升；不同规模收敛到不同格式。距离：机制层最早的"RL 放大一种预训练格式"，规模小、数学玩具，无固定开头对照，无蒸馏。

**6. Karan & Du, ICLR 2026 oral（2510.14901）。** 训练免费的 MCMC 幂分布采样，Qwen2.5-Math-7B 等在 MATH500/HumanEval/GPQA 上接近甚至超过 GRPO，且保留多样性。距离：另一种"无训练达到 RL"；Zhang 2610.24663 在 8k 预算下实测它对 Qwen3-4B-Base 的 AIME 无增益（MATH-500 有 +2.4 到 +3.5）。我们的 cue 成本为零、无需多次采样。

**7. 其余。** One-shot RLVR（Wang 2504.20571，NeurIPS 2025）：Qwen2.5-Math-1.5B 一条样本即可 36→73.6，并报告其中包含"格式纠正"成分——用于说明"格式/开头"解释的先例，不是同一问题。2608.00220（PKU，预印本）：Qwen3-8B-Base 上 RLVR 主要重排已有开头，开头强制对数学可搜索性有因果作用，但关注跨任务（math↔IF）支持缩窄，没有"cue 恢复 RL 全部 pass@1 增益"的比较。2608.29188（Countdown，Qwen2.5-3B）：RLVR 的覆盖缩窄集中在"入口"。2605.28295 REFT：首 token 多样化改进 RLVR 探索。另有 2610.20639（"Same Answer, New Box"）：SimpleRL 7B 对的域外增益有 82% 是答案格式——相关的"格式非能力"先例，我只读了检索摘要。

**RL vs 蒸馏 vs prompt/cue 三臂同基座**：未检索到。Wang 只有 RL 与 cue；Venhoff 有 RL/蒸馏/steering 但无 cue；2505.14216 有 RL vs 蒸馏但无 cue。Qwen3 官方蒸馏（强到弱）对 cue 的比较是空白。

## 预训练内容（可引）
- Qwen3 技术报告（2505.09388）§3.1："Reasoning Stage (S2): To further improve the reasoning ability, we optimize the pre-training corpus of this stage by increasing the proportion of STEM, coding, reasoning, and synthetic data. The models are further pre-trained with about 5T higher-quality tokens…" 报告**没有**说 S2 含长 CoT/思考轨迹；只说用 Qwen2.5-Math/Coder 生成合成数据。因此"Qwen3-Base 是否含长 CoT"属推断，不能写成事实。
- OLMo 3 报告（2512.13961）Dolmino 中期训练表 5：明确含 "Thinking (synth)"：QwQ Reasoning Traces 1.87B token (1.87%)、OpenThoughts2 1.25B、Llama-Nemotron 1.25B、Gemini traces 0.25%、OMR Rewrite FullThoughts 0.85% 等，目的写明 "to lay groundwork for … Olmo 3 Think, … and Olmo 3 RL-Zero"。Wang 2610.06851 进一步确认 Olmo mid-training 里 "Okay" 开头占合成推理轨迹 83%，且 cue 的优势在 mid-training 中增大。

## 直接回答

**(1) 已被声称了吗？** 一半。"在现代推理 mid-training 基座上，固定开头（1–2 token）使 pass@1 达到 RL-Zero 水平"已被 Wang 2610.06851 声称并多模型验证（Qwen3-14B 的 "Alright," 在 MATH-500 等于 RL）。Zhang 2610.24663 对 Qwen3-4B-Base/AIME 发现开头只占 35%。"蒸馏的增益不被开头匹配、只在难题上超出"没有人声称。

**(2) 已被占有 / 仍开放。**
- 已被占有：开头 cue ≈ RL-Zero 增益；RL 把 cue 概率抬高、策略变化集中在前几个位置；cue 不是单纯变长；cue 来自训练数据关联；单阶段 RL 的局限被作者自述。
- 开放（需自行核实未被后续预印本占用）：(a) Qwen3-8B-Base + 公开 DAPO 纯 RL 检查点、MATH L1-3/L5/OlympiadBench 上"逐集匹配或超过全部增益"，含 RL 训练过的题；(b) 逐题增益相关（split-half 校正 r=0.90）；(c) 蒸馏 vs cue vs RL 三臂；(d) prefix-handoff：RL 的续写只在前约 32 token 起作用，蒸馏的续写持续到约一半答案；(e) 开头之后 base 自取 argmax 不再有益（对 Zhang 的 rl-replace 结论的限定）；(f) 对 Zhang "开头只占 35%" 的调和（难度/预算/cue 长度）。

**(3) 审稿人会指出的缺失对照。**
1. 无推理 mid-training 的基座（Wang 已有 Llama-3.1-8B 无效、Qwen2.5-Math 无增益；需 Olmo-3 早期 checkpoint 式的前/后 mid-training 对照，Wang 图 22 已做过 Olmo）。
2. 长预算（Zhang 用 8k，Wang 用 31k；我们的上限与 8192-cap cue 检查需写明）。
3. 多种 cue 措辞与 Wang 的无标签选 cue 流程（我们的 "Alright, I have this problem" 取自 RL 模型的开头，有"偷看 RL 输出"的嫌疑，需要无 RL 信息的选法，或用 Wang 式搜索得到的 cue 复现）。
4. 蒸馏臂的混杂：官方 Qwen3-8B 是多阶段（含长 CoT 冷启动+RL+强到弱），与"纯蒸馏"不同，需标注。
5. 其他 RL 配方/检查点（GRPO/MATH 对 DAPO）与多种子；RL 训练题污染。
6. 在 RL 模型上叠加 cue（Wang 表 7 已有 Olmo-32B 例）。

**开题表述的两个最强引文**：Wang："if reasoning may already be present in the base model, how little intervention is needed to elicit it?"；Zhang："These observations describe what changes, not which change produces the gain."
