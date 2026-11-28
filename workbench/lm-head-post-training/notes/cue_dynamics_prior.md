# 「RL 训练中增益何时不再能被固定开头 cue 替代」：先行工作核查（2026-11-28）

读法：下面凡写"全文"，指 arXiv PDF 经 pdftotext 读过正文+附录相关节；图只能读到说明文字和图内文字，曲线数值读不到处标「未核对」。

## 1. Wang et al., 2610.06851（全文已读，含附录 A–F）
(a) 跨 RL 训练步的测量：**没有逐检查点测 P(cue)，也没有"强制 cue 后的 RL 中间检查点精度"。** 只有三类端点或曲线：
- P(cue) 只测 base 与 RL 终点两个点：Olmo-3-7B ".\n\n Okay" 0.14→0.65，Qwen3-14B "Alright," 0.04→0.58（§2.3，图 3 中图；附录 D.2 图 16 给 4 个模型的前后概率）。Qwen3-4B 的 "To determine" 0.02→0.08，更宽的 "To" 分支 0.20→0.58。
- 学习曲线（图 3 右、附录图 14，300 步 GRPO）：标准 RL 的 MATH-500 pass@1 随步数，对比"cue 强制的 RL"（从 base+cue 的精度起步）。原文："Before any updates, prefilling matches accuracies that standard RL reaches only after training"，约等于 Olmo 100 步、Qwen3-14B 50 步的标准 RL；"Further cue-forced training yields little improvement as standard RL catches up"。Qwen3-4B：cue-forced 100 步达到标准 300 步的精度；Qwen3-14B："RL adds little to the cued base's accuracy"（D.2）。曲线上的逐步数值：未核对（只有图）。
- 只评 MATH-500，每步无 cue 可替代性（"RL 检查点自己 vs 同一检查点的 base+cue"）的指标：没有。
- 此外有 RL 终点的 swap：RL 生成的开头（到第一个空行后两个 token）+ base 续写 = 0.777，RL 单独 0.751，base+强制 cue 0.777；base 的开头 + RL 续写 = 0.437（base 0.417）（附录 D.3，表 13，Olmo-3-7B）。
(b) RL 设置（附录 D.1，表 12）：自训，不是公开检查点。模型 Olmo-3-7B/32B、Qwen3-4B/14B（Base）；GRPO，MATH 7500 题训练，32 题/步×16 rollout=512 rollout/步，300 步，训练温度 1.0，上限 4096 token，二值奖励，无 std 归一，无 KL，clip 0.20/0.28，LoRA rank64/α128，lr 1e-5，5 步 warmup。算力（GPU 小时）：全文未见 RL 的算力数；只提中训重训用 4 GPU（附录 F）。另外 Olmo-3 的 RL-Zero 官方检查点和一个 Qwen3-14B-GRPO-MATH 作参照。**没有 Qwen3-8B-Base。**
(c) RL 超过 base+cue 的情形：有。表 5/表 6（附录 C.1）：Olmo-3-7B（RL-Zero 提示）RL 对 base+cue：AIME24 35.2 对 23.3，AMC23 66.2 对 59.5，OlympiadBench 41.6 对 36.5；MATH-500 反过来 75.0 对 77.9，GSM8K 60.5 对 85.9。Qwen3-4B（boxed 提示）MATH-500：RL 75.4 对 base+cue 71.5。Qwen3-14B（boxed）：MATH-500 86.8 对 86.6，AIME24 26.6 对 30.0（cue 更高）。§2.2 的措辞是 "match or outperform RL in most cases"，§6 自述限制："Complex multi-stage post-training pipelines may introduce capabilities beyond those elicited by the token cues"，且只研究 R1-Zero 式单阶段 RL。附录 E.2：同样采样数下，RL 在 Olmo-3-7B 与 Qwen3-14B 从 k=2 起与 cued base 持平，在 Olmo-3-32B 上超过。
(d) cue-forced RL：有（见 (a)，图 3 右/图 14）。训练时 cue 不进 loss，只作条件。比较的只是 MATH-500 曲线，没有训练后"学到了什么"的分析。另有表 6：给 RL 模型再叠加 cue，Olmo-3-7B(RL-Zero 提示) MATH-500 75.0→75.3（几乎无变化，即终点 cue 已被 RL 吸收）；boxed 提示下 +24.7（RL 模型对不同模板并未吸收）。表 6 另有 Olmo-3-32B GRPO-MATH RL-Zero 提示下全部 ±0.3 以内。

## 2. Cai et al., 2510.00553 ICLR 2026（全文已读，含附录 B–D）
(a) "step-k"：附录 B 写 "We save the checkpoint after each training batch"，即 step-k = 第 k 个训练 batch 之后的检查点；图 6(a) 纵轴 "Checkpoint Step" 标 1,6,11,16,21,27，与 DAPO-step-27 吻合。DAPO 配置：prompt 上限 2048、response 上限 20480；mini-batch 32 样本×16 次梯度累积=有效 batch 512（一次优化器更新）；每 prompt n=8；lr 1e-6 带 warmup；DAPO 每个训练 batch 最多生成 512×3 个候选（动态采样）；"until the reward fails to improve for five consecutive steps" 停训。因此一个 step 约 1 次优化器更新、有效 512 样本；512 指 prompt 还是样本、一个 step 实际多少 prompt：「未核对」（文中 "512 gradient accumulation steps" 与 "effective batch 512" 说法不一致，需看 Alpha-RL 代码）。总训练步数：正文只写 "10%/40% of total training steps"，**未给总步数**；只能由检查点名推断 DAPO 共 27 个（PPO 23、Spiral 22 只见于 HF 仓库名，论文未核对其对应）。Spiral 附录另述 Qwen-4B-Base 自博弈 "roughly 200 checkpoints (saving one checkpoint every two epochs)"，与 HF 的 Spiral-step-0..22 如何对应：「未核对」。
(b) 训练模板（附录 B）：论文写的是纯文本 "User: Solve the following math problem step by step. The last line of your response should be of the form Answer: $Answer ... {question} Remember to put your answer on its own line after "Answer:". Assistant:"，EOS 为 <|endoftext|>。没有出现 <think></think>，没有提 enable_thinking。**注意不一致**：HF 仓库 caiyuchen/DAPO-step-27、PPO-step-23 的 README 写推理用 "{question} Please reason step by step, and put your final answer within boxed{}" + tokenizer.apply_chat_template(add_generation_prompt=True)。我查了 DAPO-step-27 与 Qwen3-8B-Base 的 tokenizer_config.json：模板相同，仅当 enable_thinking=false 才在 assistant 后追加空 <think>\n\n</think>\n\n，默认不加。论文评测用哪种模板：「未核对」。（SFT 对照用另一个 "Please reason step by step..." 模板，同附录 B。）
(c) 精度轨迹：有，但只是相对精度，不是绝对曲线。图 3(b)、附录图 10：Rank-1 重构模型对完整训练模型的相对精度随训练进度；"during the early stages ... slightly lower ... at later checkpoints ... fully match"。表 1：AlphaRL 在 10%/40%/100% 训练步的六个基准（AIME24/25、MATH-500、Minerva、GPQA、GSM8K）；各检查点的绝对精度数字：「未核对」（表 1 我只读了文字）。开头 token：附录 D（图 12–14）。非贪心 token 词云里有 "Alright"、"Let"（开头）和 "But"、"Wait"（转折）；前缀实验（图 14）：把 Rank-1 模型 CoT 的前 n 个 token 喂给 base 续写，"using only the first 20 tokens ... allows the base model to approach the performance of the full parameter update"，结论 "performance gains primarily arise from the early stage of the reasoning chain"。这个实验只做在训练终点，不随检查点变化；具体数值只有图，未核对。图 2 示例里完整模型与 Rank-1 的回答都以 "Alright, I have this geometry problem in front of me" 开头，base 以 "To solve this problem" 开头。**没有任何关于 cue 强制或 P(开头) 随检查点变化的测量。**

## 3. Zhang et al., 2610.24663（全文已读）
- RL 设置（§3.1、附录 A.3，表 9）：Qwen3-4B-Base（不是 8B），GRPO，verl，DAPO-Math-17k（去除与 AIME22/23 重复题），lr 1e-6 常数，128 prompt×8 rollout/步，奖励 ±1，8 卡 FSDP；选用验证集最优检查点 step 460（Qwen3-8B 为 320，Llama-3.2-3B 为 500）。训练动态（附录 A.3）：训练精度 0.071（第 1 步）→0.413（第 50 步）→plateau 0.50–0.54（约 150 步后），中位 rollout 长度 521→3917，无有效答案比例 0.408→0.027。总步数/GPU 小时：只给了评测算力（AIME 一年 16 样本 7.3–7.9 GPU 小时等），训练总预算「未核对」。
- "Alright 恢复 35%"：§3.3 与表 3：120 道 AIME22–25，上限 8192 token，温度 0.6，16 样本；pass@1 10.00→13.23（RL 19.32），pass@16 30.00→35.00；"Alright, I" 为 11.61，无额外增益；"Alright"+base greedy 替换 14.74；rl-replace（只在两模型 greedy 不一致处用 RL 的 token，约 4% 位置）18.44，恢复 90.5%；开头之后的 RL 替换另加 5.2 点。
- 是否随训练步分析可替代性：**没有。** 只有一个终点检查点（及上面的训练精度曲线）。他们自己把 Wang 的结论转述为 "a short opening cue ... recovers much of the RL gain"，与自己 35% 的结果方向不同。

## 4. Liu et al., 2503.20783 COLM 2025（全文已读，§2、§3.3）
- §2.1–2.2、表 1：模板决定 base 能否"回答问题"；Qwen2.5 系列无模板反而最好（Qwen2.5-Math-1.5B 平均：R1 模板 7.9、Qwen 模板 24.2、无模板 33.1；Qwen2.5-Math-7B：R1 模板 0.0、Qwen 26.5、无模板 38.2；表 1 行由文本推断，行首的模型名未核对）。
- §3.3、图 6（Qwen2.5-Math-1.5B，Dr. GRPO，三种模板×四个题集 ORZ/MATH/GSM/ASDiv）："Templates determine the performance of the initial policies, but RL can improve all policies to a comparable performance of ∼40% (given a proper question set)"；模板严重不匹配（R1 模板）时增益主要来自 RL，需要题集覆盖；用 Qwen-Math 模板时，在 GSM8K 上训练最终最好。作者结论："Applying templates in fact destroys the capability before RL reconstructs it. This implies that we should be more conservative in claiming the huge gains brought about by pure RL"。
- 没有固定推理开头（reasoning opener）的实验；"模板"指整体提示格式，不是回答前缀。未测量 RL 学到什么是否依模板而变，只给最终精度/曲线。

## 5. 近邻检索（arXiv API + 全文，2025–2026）
没有找到"逐检查点测 base+cue 是否复现 RL 增益"的论文，也没有找到"用强制推理开头跑 RL 并与标准 RL 对比"之外于 Wang 的论文。相关：
1. 2610.06851 Wang：唯一的 cue-forced GRPO 对比（见 §1）。
2. 2608.00220 Wei et al.（PKU，全文读了 §3–§5、D.3）：Qwen3-8B-Base 与 Qwen2.5-Math-7B 上 Math-RLVR（MATH 7.5k）/ IF-RLVR；每组一个固定种子；沿 IF-RLVR 检查点（含 step 0→20 等）统计开头路线（DRI 步骤式推导 / DAI 直接给答案），DAI 占比升高与 AIME best@32 下降同步（图 3）；"RLVR mainly reranks openings already available in the base policy"；§5.3：在检查点上强制 base 侧 token 或 DRI 前缀可使 best@32 提升（图 8a，涨幅 +10.2%…+58.6% 一类，具体对应格未核对）。**是目前最近的"跨检查点 + 强制开头"工作，但度量是跨任务 best@k 可搜索性，不是"cue 能否复现 RL 增益"，且只有一个任务的多个检查点。**
3. 2605.28295 Kim & No（REFT，读了摘要、§6、附录 7–8）：RLVR 中对首 token 做多样化采样（top-N 均匀），八个模型 0.5B–14B，GRPO/DAPO；首 token 分布高度集中且与正确性弱相关；有"首 token 集中度随训练演变"的分析（§6）。是"训练时操纵首 token"，不是固定一个推理 cue，也没有 cue 对 RL 增益的替代测试。
4. 2509.25666 Chen et al. NuRL（只读摘要）：RL 中对 0% 通过率题注入自生成提示以突破上限；与"固定开头 cue"无关，仅作"RL 中加条件前缀"的邻居。
5. 2610.22937 Gupta et al.（只读摘要）：后训练阶段（base→SFT→RL）追踪预训练里已有的 cue-routing 注意力头；这里 cue 指选择题提示/诱导，不是推理开头，只作"跨训练阶段追踪 cue 机制"的邻居。
6. 2506.10947 Spurious Rewards、2510.07364 Venhoff（引自 notes/rl_elicits_mode_survey.md，本次未重读）：RL 选择已有模式的近邻，均无逐检查点 cue 测量。

## 对新问题的影响（仅事实）
- 已被回答：终点处 base+cue 能追上 RL-Zero 的 MATH-500 pass@1（Olmo-3-7B、Qwen3-14B；Qwen3-4B/Zhang 的 AIME 上只有 35%）；终点 RL 把 cue 概率抬高、policy 差异集中在前 1–2 个 token；cue-forced RL 起点高、与标准 RL 汇合（图 3 右/图 14，自训 LoRA、MATH、300 步、Olmo/Qwen3-4B/14B）；Rank-1 更新在检查点上线性演化且前 20 token 前缀即可逼近完整更新（Cai，只在终点做前缀）。
- 仍开放：（i）P(cue) 随 RL 步数的曲线：Wang 只有两个端点；（ii）公开中间检查点（DAPO-step-0..27 等）上"同一检查点 vs base+cue"的差距随步数的变化，即何时 cue 不再可替代：未见任何论文测过；Wang 曲线是"标准 RL 精度"对"cue-forced 起点"，不是逐检查点 cue 强制；（iii）Qwen3-8B-Base 上的 cue 对 RL：Wang 没有 8B，Zhang 有 8B 但只做 MATH-500 与覆盖率；（iv）"之后学到什么"：Wang 只给 swap（开头由谁生成）和 KL 集中位置，Zhang 给终点的 rl-replace 分解，二者都不随检查点；（v）Cai 公开检查点的步长/总长/训练模板（纯文本 User/Assistant，而 HF 说明为 ChatML）：论文与 HF 不一致，需自行核对后再用；（vi）Liu 的模板结论针对 Qwen2.5-Math，且没有固定推理开头；与本问题最近的邻居是 2608.00220（跨检查点+强制开头，但度量是跨任务 best@k）。
