# 公开 RL 训练轨迹盘点（只查 HF API / README / arXiv 摘要与正文，未下载权重；2026-11-28）

约定：「核对」= 本次通过 API 或 README 直接看到；「未核对」= 没看到或没读全文。"plateau" 一栏除非写明来源，一律未核对（没有读各论文的曲线）。

## A. 可直接用的长轨迹（同一 run、多个 checkpoint）

### A1. max-rl 组织（MaxRL 论文 2602.02710 + Sheng 等 2611.33102 的同一批资产）——最完整
- 1.7B-Base Polaris-53K，三种算法各一条 run：
  - `max-rl/{maxrl,grpo,rloo}_qwen3_1p7B_base_polaris_checkpoints`：global_step 50,100,...,1000（每 50 步，共 20 个；maxrl 额外有 1040）。每个 step 目录含 FSDP fp32 model 分片 + **optim 分片（AdamW，16 rank）** + extra_state(rng/lr scheduler) + data.pt + actor/huggingface（子目录，核对到目录存在）。每个 ckpt 约 20+GB，整库 ~440-460GB。
  - 配套 rollouts：`max-rl/{maxrl,grpo,rloo}_qwen3_1p7B_base_polaris_rollouts`，每步一个 parquet（data/step-0001..1000；API usedStorage=33092039814 字节，约 33GB），已核对文件数 1041。
- 4B-Base Polaris：`ftajwar/qwen3_4B_Base_GRPO_Polaris_1000_steps`、`..._MaxRL_Polaris_1000_steps`（及 1.7B 同名）只放**最终 step-1000 一个 ckpt**（README：“trained for 1000 steps, released the final checkpoint”）；但 rollouts 全步公开：`ftajwar/maxrl_qwen3_4B_base_polaris_rollouts`（apache-2.0；token ids + 采样 logprob + 原始 reward；1000 步，256 prompt × 16 rollout，T=1.0，max len 4096，纯 REINFORCE 损失无 KL 无 clip，MaxRL advantage；~31GB）。4B Polaris 中间 ckpt：未核对（未见）。
- KnK（Knights-and-Knaves，n=3..12）：`max-rl/maxrl_knk_3_12_checkpoints`(1.7B，100..1000 每 100 步，含 optim；102 个文件)、`max-rl/{grpo,rloo}_knk_3_12_checkpoints`、`max-rl/maxrl_qwen3_4B_base_knk_3_12_checkpoints`（4B，每 100 步 HF bf16；240/260/500/640/700/860/980/1000 带完整 verl 状态含 AdamW；步 1-240 与 241-1000 之间换过 rollout correction，README 已写明）。rollouts：`max-rl/*_knk_3_12_rollout1000`。4B 终点 eval：mean@4 0.8265（README）。
- **“RL 历史影响后续学习”的直接对照**：`ftajwar/{maxrl,grpo}[_dppo]_qwen3_{4B,1p7B}_{base,maxrl_polaris1000}_knk_step_{100..400}` ——同样的 KnK RL，起点分别是 Base 与「先做过 1000 步 MaxRL-Polaris」的 ckpt，每 100 步一个 ckpt（只到 300/400 步）。已核对 repo 名，未读卡片细节；论文 Sheng 等 2611.33102 的“跨模型/跨任务”实验与此相关（未全文核对）。
- 另：`max-rl/maxrl_llama3p1_8b_instruct_bigmath_bs64_checkpoints`：Llama-3.1-8B-Instruct，Big-Math-RL-Verified（242k 题去重，见 ~128k，约 0.53 epoch），MaxRL，**每 50 步 bf16 HF（50..2000，共 40 个）**，仅 1950/2000 带完整 AdamW 状态；lr 1e-7，64 prompt×16，响应≤3072，无 KL；license llama3.1；rollouts `max-rl/maxrl_llama3p1_8b_instruct_bigmath_bs64_rollout2000`。8B 刚好在上限。
- 另有 AceCode87k（代码）：`max-rl/{maxrl,grpo}_acecode87k_checkpoints` + rollouts；`max-rl/checkpoint-archives`（0.6B/1.7B IDK 任务，含 grpo 变体）。
- 训练 prompt 模板：未在卡片给出，需看 github.com/tajwarfahim/maxrl（未核对）。W&B 日志：KnK 卡片给了 run id（paprika_online/..., 公开性未核对）。
- Sheng 2611.33102（arXiv 摘要核对）：“RL Can Be Recovered From Its Own Rollouts”，用归档 rollouts 做 maximum likelihood replay 可复现学习曲线。**归档 rollouts 是公开的**（上述 HF 数据集），正文表格明确 Qwen3-1.7B/4B-Base、Polaris-53K、1000 步。
- 是否平台：未核对（需读 Polaris 曲线；论文 Figure 里有 pass@k 随步数曲线）。

### A2. allenai Olmo-3 / Tulu / OLMo-2（HF 分支 revision，Apache-2.0）
- `allenai/Olmo-3-7B-RL-Zero-{Math,Code,IF,General,Mix}`：RL-Zero 直接从 Olmo-3-1025-7B **base** 开 RLVR（卡片称 “experimental set for the scientific exploration of RLVR training”）。分支 step_N：Math 100..1900（19 个，每 100）；Code 100..2900（29 个）；IF 100..1700（17）；General 100..800（8）；Mix 100..900 步（每 50 步，约 18）。优化器状态：仓库文件只有 safetensors，**未见 optimizer**。Math 数据集 `allenai/Dolci-RL-Zero-Math-7B`（核对到 Dolci-RL-Zero-* 系列数据集存在）。
- `allenai/Olmo-3.1-7B-RL-Zero-{Math,Code}`：Math step_100..2800（每 100，28 个）；Code 约 050..1900（每 50，33 个）。Olmo-3.1 比 Olmo-3 训得更久（核对分支）。
- Prompt 模板（RL-Zero-Math，chat_template.jinja 核对）：“Solve the following math problem step by step. The last line of your response should be the answer to the problem in form Answer: $Answer ...” 并在末尾附 “Remember to put your answer on its own line after "Answer:"”。base 模型 = `allenai/Olmo-3-1025-7B`。
- 日志：卡片写 “logs (coming soon)”，W&B 链接被注释掉（核对）；奖励/熵曲线是否另处发布：未核对（Olmo 3 技术报告里有图，未读）。
- `allenai/Olmo-3-7B-Think`：RLVR（从 DPO 起）分支 step_0025..1375 每 25 步，共 55 个；`Olmo-3-32B-Think` 到 750 步（每 50），`Olmo-3.1-32B-Think` 到约 2300 步（每 50）。7B-Instruct step_050..400（每 50）。32B 超出 ≤8B。注意 Think 起点已含 SFT+DPO，不是“零起点”。
- `allenai/Llama-3.1-Tulu-3-8B`（branches step_100..1000，每 100；是否为 RLVR 阶段步：未核对）；`OLMo-2-1124-7B-Instruct` step_60..360（每 60，RLVR 阶段推测，未核对）；`OLMo-2-0425-1B-RLVR1` step_200..2600（每 200，14 个，1B；数据 RLVR-GSM-MATH-IF-Mixed-Constraints）。
- Pythia 式提示（备忘）：已有经验 Olmo-3 需 tf4.57（见 memory）。

### A3. polaris-73（个人账号，非官方，无模型卡）
- 约 240 个 repo（`polaris-73/…-step-N` / `…-global_step_N`）：Qwen3-4B 与 DeepSeek-R1-Distill-Qwen-1.5B 各 8 个域的 RLVR（Math/Code/IF/Science/All/All-Without-IF/IF-Cascade-400），每 100 步一个（100..800）；另有 ds1p5b/ds7b/ds8b/qwen7b 的 GRPO/noKL/cliphigh/PPO/REINFORCE/RLOO 变体，每 200 步到 870。**无 README、无 optimizer、无日志；论文来源未核对**（repo 创建 2025-12 至 2026-01）。同一 run 多 ckpt 且有串联(cascade)/continue 版本，对“RL 历史”有用，但可复现信息缺失。
- 论文/数据：未核对。

### A4. Miaow-Lab：`Miaow-Lab/RLVR-Linearity-Checkpoints`（arXiv 2601.04537，Apache-2.0）
- R1-Distill-Qwen-1.5B + GRPO，global_step 100..1300 每 100，共 13 个；lr 1e-6，batch 128，group 16，32×H100 约 150h；训练集 `Miaow-Lab/RLVR-Linearity-Dataset`(deepscaler-preview, aime24)。无 optimizer。论文称进入“线性区”，是否平台：论文讲线性漂移，未核对。

### A5. caiyuchen（arXiv 2510.00553 AlphaRL，已核对摘要/正文片段）
- `caiyuchen/DAPO-step-0..27`（28 个，每步一个）、`PPO-step-0..23`、`Spiral-step-0..22`；DAPO：Qwen3-8B-Base，DAPO-Math-17k，apache-2.0；README 模板：“{question} Please reason step by step, and put your final answer within boxed{}.” 再套 chat template。每个 repo 一个完整 8B 权重（4 shard）。总步数/是否平台：这些只是**前 ~28 步**，远没到平台；论文用 8 个模型 7 种算法，其余 ckpt 另行：`caiyuchen/Qwen3-4B-Non-Thinking-Math-RL` 等（单点）。无 optimizer、无 rollout（未见）。
- 同系关联：`Keven16/Qwen3-4B-Non-Thinking-RL-{Math,Code}-Step{500,1200 / 300,1200}`（LaSeR 相关，各 2 个点）。

### A6. 其它第三方（零散，一次发布几个点）
- `kushasareen/qwen3-4b-dapo-grpo-step{20,100,200,400,600}`（Qwen3-4B，无卡片）；`kushasareen/polaris-rl-only-step1450`、`codeio-rl-only-think-8b-step{950,1250}` 等。
- `billkunghappy/*-Dapo-*-Step{5..100 / 200 / 2000}`（Qwen3-1.7B/8B-Base，DAPO；多变体，无卡片）。
- `daviddavidlu/DAPO-with-prompt-augmentation-step{2480,2720,2820}`（PrAg-PO 2602.03190，Qwen2.5-Math-1.5B，MATH L3-5；github wenquanlu/PrAg-PO）。
- `stellalisy/rethink_rlvr_reproduce-{ground_truth,random,majority_vote,format,incorrect}-qwen2.5_math_7b-lr5e-7-kl0.00-step{50,100,150}`：Spurious-Rewards 的 Qwen2.5-Math-7B 复现，各奖励类型只有 3 个点，150 步（短）。
- `alphaXiv/spurious-rewards-rlvr-training-qwen-2.5-1.5b-math-ckpt-{50,200,400,1000}`：4 个点。`grpo-spurious-rewards/*`（85 个，剑桥学位论文，Qwen2.5-1.5B-Instruct/OLMo-2-1B/Llama，TRL）：每个 run **只有 checkpoint-2400 一个点**，但含 optimizer.pt + trainer_state.json（无中间点，不适合作轨迹）。
- `JackHsieh/Qwen3-{4B,8B}.gpnp-rl...step-N`（写作/知识类 RL，非可验证数学；中间点数未核对）。`z369217411/Qwen3-30B-A3B-DAPO-*-step-NNNN`（30B MoE，超范围）。

## B. 只放最终模型（无中间点；已核对 refs 仅 main）
SimpleRL-Zoo(`hkust-nlp/*-SimpleRL-Zoo`，含 Zero 版)、Open-Reasoner-Zero 0.5/1.5/7B/32B（另有 Critic，对 PPO 有价值但无中间 ckpt）、DeepScaleR-1.5B-Preview、Polaris-1.7B/4B/7B-Preview(+1.7B-stage-1)、Skywork-OR1(-Math)-7B/32B、AceReason-Nemotron-1.1-7B、AceMath-RL-Nemotron-7B、One-Shot-RLVR(ypwang61，~25 个变体但各 1 点)、TTRL(各 1 点)。
- ProRL/Nemotron-Research-Reasoning-Qwen-1.5B：refs 为 main(v2)、tag v1、branch v2、brorl，共 3~4 个时间点（ProRL v1、v2、BroRL），license cc-by-nc-4.0（核对）；README 称 >2k 训练步，无中间 ckpt、无 optimizer。
- Spurious-Rewards 官方（Qwen2.5-Math 系）只发最终点（上面是第三方复现）。

## C. 题中所列论文
- Sheng 2611.33102：见 A1，rollouts 公开 = 是。
- Noukhovitch 2609.13443（NGU, “Never Give Up”）：摘要核对：DeepScaleR + Manufactoria 代码；github.com/mnoukhov/never-give-up，博客 mnoukhov.github.io/posts/ngu；是否有多 ckpt：未核对。
- Cui 2505.22617（entropy mechanism，arXiv 未能返回摘要，id 经 API 命中但解析为空）：是否发布中间 ckpt：未核对（本次 HF 上没搜到作者官方 step 系列）。
- Pythia 式 RL 套件：HF 搜 “rl suite / rl trajectory checkpoints” 无结果；唯一接近的是 allenai Olmo-3 RL-Zero 与 max-rl。

## D. 排序：最适合“RL 历史如何改变后续学习”（同 run、多点、到平台、≤8B）
1. **max-rl 1.7B-Base Polaris（GRPO / MaxRL / RLOO 各一条）**：`max-rl/{grpo,maxrl,rloo}_qwen3_1p7B_base_polaris_checkpoints`，每 50 步到 1000，**带 AdamW 状态 + rng + dataloader，可从任意 ckpt 严格续训**；全步 rollouts；三算法同数据同初值可对比；起点 base（零起点，无 SFT 干扰）。平台：未核对。另配套 `ftajwar/*_knk_step_*`（Base vs Polaris1000 起点）可直接做“前史→后续学习”。缺点：每 ckpt ~22GB（含 fp32+optim）；模板见 github。
2. **allenai/Olmo-3-7B-RL-Zero-Math（及 Code，3.1 版更长到 2800 步）**：base 零起点 RLVR，分支每 100 步，Math 1900/ Code 2900 步，Olmo-3.1-Math 2800 步；Apache-2.0；prompt 模板已知；训练数据 Dolci-RL-Zero 公开、预训练全开放（可追溯 base）。缺 optimizer 状态与日志（“coming soon”）。平台：Olmo 3 报告有曲线，未核对。
3. **max-rl Llama-3.1-8B-Instruct Big-Math MaxRL**：每 50 步到 2000（40 个），1950/2000 有 AdamW；rollouts 全公开；lr 1e-7 很小，0.53 epoch，是否平台未核对；license llama3.1；8B。
4. **max-rl 4B-Base KnK**（每 100 步到 1000 + 多个带优化器的点，步 240 前后有 rollout correction 变更，用时需注意）+ rollouts：任务小、易到平台（终点 mean@4 0.8265）；适合便宜 pilot。
5. **Miaow-Lab Distill-Qwen-1.5B GRPO**（100..1300 每 100，无优化器）与 polaris-73 Qwen3-4B 系列（每 100 步到 800、含 cascade/continue，但无文档）为备选。

## 备注
- 若需要“optimizer 状态 + 可续训”：只有 max-rl 系与 grpo-spurious-rewards(仅单点) 满足；Olmo 系没有。
- 存储量大（1.7B Polaris 每条 ~440GB）；只拉 `global_step_N/actor/huggingface` 目录即可得到 bf16 权重（约 3.4GB/点，1.7B 估计，未核对）。
- 题中 id「2611.33102」「2609.13443」「2510.00553」均在 arXiv 核实存在（2510.00553 为 2025-10；2609.13443 为 2026-09；2611.33102 为 2026-11）。
