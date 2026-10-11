# Territory: Real-Time Causalization Capability Preservation

- **偏好对应：** video world model / 强开源 baseline / 大量横向实验 / problem-first + method-after-pain
- **目标会议：** CVPR 2027 / ICML 2027；证据不足则顺延 NeurIPS 2027
- **状态：** 2026-10-02 人确认，ACTIVE-MAIN
- **领域调查：** [`../../library/themes/video-world-models/REALTIME_CAUSALIZATION_SURVEY.md`](../../library/themes/video-world-models/REALTIME_CAUSALIZATION_SURVEY.md)

## Registered territory object
> **研究 interactive video world model 从 bidirectional / multi-step teacher 转成 causal AR、few-step/distilled、real-time student 时，world-model capabilities 的选择性损失与保留：什么在何时坏掉，什么 recipe 能保住，为什么。**

不预注册“causalization 一定有害”。

## 最近邻边界
- Vid2World：宽 causalization；
- Self Forcing：self-rollout / exposure gap；
- MotionStream：real-time causal streaming；
- Causal Forcing：bi-teacher → AR-student architectural gap；
- Astra：memory / responsiveness；
- ForgeWM：Stage 0→3 + stage-wise generic ablation；
- ActionSplice：in-flight chunk action update；
- WBench / PlayWorld / R2M：multi-dimensional world-model evaluation。

**禁止增量：**“causalization 会掉点”“四个 stage 分数不同”“chunk action responsiveness 有问题”。  
**需要的增量：** capability-specific + factorized attribution + cross-lineage / positive-exception aware。

## 立足点
1. **minWM**：Wan1.3B / HY1.5 8B；bidirectional SFT → TF causal AR → causal ODE/CD → DMD self-rollout；已有本地 harness。
2. **ForgeWM**：Stage 0/1/2/3 全 checkpoint；1/2/4-step students。
3. **旧 seam 资产**：MG2/minWM/HY-WorldPlay phase-balanced replay、short pulse/step、grid shift、stage comparison；仅作 action diagnostic。

## 压力清单
1. aggregate quality 可能掩盖 capability-specific loss；
2. bi→causal、multi→few-step、clean→self-history、chunk serving 经常被 bundle；
3. 普通长按/平滑轨迹可能漏掉短事件 action fidelity；
4. memory 与 responsiveness 存在已知 tension；
5. positive exception 可能比 failure 更有价值；
6. evaluation 正从“视频像不像”转向“世界是否能被交互/记住/用于任务”。

## 驻留顺序
- **D1/R0：** pin minWM + ForgeWM stages，复现 native metric，测 VRAM/I/O/wall-clock；
- **D2/E01：** common capability evaluator；
- **D4/E02：** within-lineage capability × stage matrix；
- **E03：** 只有稳定 signal 后才做 factorized intervention；
- **D5：** 持续查 ForgeWM/Causal Forcing/Astra/ActionSplice 与最新 arXiv；
- **D6：** idea 只能从真实 measurement / pain / positive exception 长出来。

## 决定性问题
- generic quality 保住时，world capability 是否选择性掉？
- loss 最早在哪个 transformation 出现？
- 是否跨 ≥2 lineage 复现？
- 有没有 recipe 明显保住能力；什么 design 是 load-bearing？

## 风险 / 转向
- 只复刻 ForgeWM stage table → 无贡献；
- 只有 seam synthetic probe、真实 interaction 无后果 → 不推进；
- 找不到 ≥2 可比 lineage → 不做跨-lineage general claim；
- 需要大规模重新训练才能知道有没有现象 → 不适合当前资源；
- 全部 capability 都保住 → 转向“what protects capability”，不硬写 failure。

## 与旧主线
`video-world-model-temporal-interfaces` 已 PAUSED。旧 seam finding 是 diagnostic，不是 paper identity；不为了复用旧实验而保护旧 story。
