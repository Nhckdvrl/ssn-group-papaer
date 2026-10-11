# Real-Time Causalization / Distillation for Interactive Video World Models

**更新：2026-10-02。用途：** 新 MAIN 的 problem / method / evaluation map 与 claim-ownership 边界。不是实验结果。

## 0. 核心判断
2025–2026 的 interactive video world model 正形成稳定工程范式：

> **bidirectional / full-attention video generator → action-conditioned teacher → causal AR generator → one/few-step distilled real-time student → long-rollout / memory / deployment adaptations**

领域已有很多论文研究“怎么转换”，但对**转换过程中哪些 world-model capability 被选择性牺牲、损失在哪一步进入、为什么有些 recipe 能保住而另一些不能**，证据仍碎片化。

机会不在于说“causalization hurts”，也不在于再画一张 stage score 表，而在于把 conversion 当成一个可分解的科学对象。

## 1. Problem map
Interactive VWM survey（2606.01164）把三项关键挑战归纳为：
1. action-conditioned controllability；
2. long-horizon interaction / memory；
3. real-time action-following responsiveness。

近期 evaluation 又把 world model 拆成 controller / memory / physics / functional utility：
- **WBench**：video quality、setting adherence、interaction adherence、consistency、physics compliance；
- **PlayWorld**：agent player + long-horizon objectives，评 geometry consistency、interaction fidelity、out-of-sight evolution、insight evolution；
- **R2M-Bench**：用 matched non-revisit control 避免“模型没移动所以回访很像”的 memory shortcut；
- **WorldArena**：区分 perceptual quality 与 data engine / policy evaluator / planner 的 functional utility。

因此研究问题必须落在这些 load-bearing capabilities，而不是任意 synthetic anomaly。

## 2. Method map 与 ownership

### Vid2World — causalization
把 pretrained video diffusion 转成 causal / autoregressive interactive world model。  
**已占：**“如何 causalize video diffusion”的宽故事。

### Self Forcing — self-rollout
训练时让模型吃自己的 generated history，针对 teacher-forcing / inference exposure gap。  
**已占：**泛化的 self-rollout train-test-gap story。

### MotionStream — real-time causal student
bidirectional motion-controlled teacher → Self Forcing + DMD causal student；sub-second latency / real-time streaming。  
**已占：**强实时系统故事。

### Causal Forcing — architectural gap
指出 bidirectional teacher 与 AR student 的 architectural gap 会破坏原 ODE distillation 假设；改为 AR teacher / causal ODE-CD 再 DMD。  
**已占：**bi-teacher→AR-student gap 的理论/方法。

### Astra — memory vs responsiveness
history memory 过强造成 visual inertia；用 noisy history 平衡 coherence 与 action response。  
**已占：**泛化 memory/responsiveness trade-off。

### ForgeWM — progressive stages
Stage 0 bidirectional SFT → Stage 1 teacher-forced causal FM → Stage 2 causal consistency distillation → Stage 3 on-policy DMD，并公开各 stage checkpoint 和 1/2/4-step students。论文已有 stage-wise inference ablation。  
**已占：**progressive recipe；**“stage generic metrics 变化”不能作为我们 novelty。**

### ActionSplice — in-flight action updates
直接研究 chunk-autoregressive sampling 中途 action 改变，在 minWM-Wan / HY-WM1.5 上 retarget sampler state。  
**已占：**chunk/action responsiveness 的宽故事。

## 3. Evaluation map
### Generic visual
FVD / LPIPS / VBench 类 quality、aesthetic、subject consistency、dynamics。必要但不够。

### Action fidelity
action sign、gain、trajectory error、short-event fidelity、phase/boundary sensitivity、action-to-visible-effect latency；旧 seam probe 属于这里。

### Long-horizon state
relative revisit consistency、object/identity/geometry persistence、out-of-sight state evolution、rollout drift。

### Closed-loop functionality
multi-turn interaction adherence；agent-driven long-horizon objective completion。

### Systems
first-frame / in-flight latency、steady-state FPS、denoising steps、KV/memory growth、VRAM。

## 4. 新 MAIN 的 registered object
> **在同一 lineage 的 matched conversion stages 中，哪些 capabilities 被保住、哪些选择性失败，失败最早在哪个 transformation 出现？**

尽量分解：
- architecture：bidirectional/full attention → causal AR；
- sampling budget：multi-step → few-step；
- history distribution：clean/teacher-forced → self-generated/on-policy；
- serving：frame / chunk / cache policy。

不能形成理想 factorial 时必须明确是 bundled comparison，不偷换成因果语言。

## 5. 可能的真正增量
1. **capability-specific decomposition**：generic quality 看似保住时，action transient / revisit state / closed-loop utility 是否断裂；
2. **cross-lineage reproducibility**：同一 loss 是否在至少两条独立 conversion recipe 出现；
3. **factorized attribution**：把 architecture / step budget / history distribution / serving 拆开；
4. **positive exception**：哪个 recipe 保住了能力，哪个 design 是 load-bearing；
5. **minimal repair**：只在稳定 bottleneck 出现后做小型 adapter / conditioning / objective / inference intervention。

如果结果只能写成“Stage 1 比 Stage 0 低，Stage 2 又高一点”，**不够。**

## 6. 首选公开 substrates
### minWM
Wan2.1 1.3B 与 HunyuanVideo 1.5 8B；覆盖 bidirectional SFT、TF causal AR、causal ODE/CD、asymmetric DMD self-rollout。我们已有 minWM harness。

### ForgeWM
Stage 0–3 checkpoints、MG2/Minecraft action interface、1/2/4-step students。最适合先验证 measurement instrument，但必须越过作者已有 stage ablation。

### 旧 temporal-interface 资产
MG2 / minWM / HY-WorldPlay 的 short pulse/step、phase-balanced replay、grid shift、teacher/student stage comparison、overlap intervention。只作为 high-resolution action diagnostic。

## 7. 第一轮执行逻辑
### R0
pin repo/checkpoint/objective/attention/steps/history source；先确认 native metric 与硬件/I/O 可行性。

### E01 common capability baseline
同 lineage / same scene/action / 尽可能 same noise：
- visual quality；
- sustained control；
- transient / short-event control；
- rollout drift；
- revisit/persistence（接口允许时）；
- latency/FPS。

### E02 capability × stage
找 structured relation：哪些 capability 在哪个 stage 变化；是否与 generic quality 解耦；是否有 positive exception。

### E03 factorized control
只有 E02 有稳定 signal 才启动。用邻近 checkpoint / alternative recipe / minimal intervention 去区分 architecture、steps、history、serving。

## 8. 资源适配
这条线适合“卡多但跨节点互联差”：stage × scene × seed × metric 基本可独立并行；优先 1.3B/5B/8B public checkpoints；不需要多节点同步 pretrain。真正需要预防的是视频数据 / checkpoint I/O。

## 9. 终止 / 转向条件
- 找不到 ≥2 条公开且可公平 stage comparison 的 lineage → 不做跨-lineage story；
- 只有 generic FVD/VBench 变化 → 不推进；
- effect 只存在 synthetic probe、真实 interaction / closed-loop 无 consequence → 不推进；
- 所有 capability 都保住 → 优先研究“什么 design 保护了能力”，而不是硬写 failure；
- 需要大规模重训才能让现象存在 → 不适合本资源结构。

## 10. Primary references
- Interactive VWM survey: https://arxiv.org/abs/2606.01164
- Vid2World (ICLR 2026): https://proceedings.iclr.cc/paper_files/paper/2026/hash/1214d67bb7fa38d40e0b3c2be677e39b-Abstract-Conference.html
- Self Forcing (NeurIPS 2025 Spotlight): https://arxiv.org/abs/2506.08009
- MotionStream (ICLR 2026): https://proceedings.iclr.cc/paper_files/paper/2026/hash/0cece806cd3d1dfad4a893f016ad3d7d-Abstract-Conference.html
- Astra (ICLR 2026): https://proceedings.iclr.cc/paper_files/paper/2026/hash/7fc516909e0b90c96bcc75a16ebee6a2-Abstract-Conference.html
- Causal Forcing (ICML 2026): https://proceedings.mlr.press/v306/zhu26bf.html
- ForgeWM: https://arxiv.org/abs/2608.14022
- ActionSplice: https://arxiv.org/abs/2609.08230
- WBench: https://arxiv.org/abs/2605.25874
- PlayWorld: https://arxiv.org/abs/2608.13552
- R2M-Bench: https://arxiv.org/abs/2608.27328
- minWM: https://github.com/shengshu-ai/minWM
