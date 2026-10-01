# Real-Time Causalization Capability Preservation

## 状态
**ACTIVE-MAIN（2026-10-02，人确认）**  
**territory：** [`../../search/our-taste/TERRITORY_REALTIME_CAUSALIZATION_2026-10-02.md`](../../search/our-taste/TERRITORY_REALTIME_CAUSALIZATION_2026-10-02.md)  
**目标：** CVPR 2027（2026-11-16）/ ICML 2027 备选  
**一句话：** 不研究某一个 seam bug，而研究强 video/world model 被转换成 causal、few-step、real-time student 时，哪些真正的 world-model capability 被选择性损失或保留，以及损失从哪一步进入。

## Registered object
> **Across matched stages of real-time video-world-model conversion, which capabilities are preserved, which fail selectively, and which transformation is responsible?**

当前 **0 scientific claims / 0 contributions**。旧 seam 现象只是 diagnostic，不自动升级成本线 claim。

## 可接受的 paper shape
1. measurement + scientific finding：aggregate quality 看不出的 capability-selective loss；
2. failure + minimal repair：定位到 conversion factor 后，用最小改动恢复 capability；
3. success-case explanation：某 recipe 明显保住能力，找到 load-bearing design；
4. evaluation protocol：现有 metric 系统性漏掉 conversion-specific failure，并改变方法排序。

**禁止最终 story：**“causalization hurts”“Stage 0/1/2/3 分数不同”“seam 上短按会丢”“又一个 world-model benchmark”。

## Phase-0：先证明 territory 可做
### E00 — stage asset audit
至少找到 2 条独立 lineage：
- stage checkpoint 公开；
- stage definition 清楚；
- interactive/action evaluator 可跑；
- 单卡/单节点可承受；
- 至少能复现一个官方 native metric。

首选：**minWM**（Wan1.3B + HY1.5 8B）和 **ForgeWM**（Stage 0–3 + 1/2/4-step）。

## 第一轮系统测量
### E01 — common capability baseline
同 lineage / same scene/action / 尽可能 same noise：
- visual quality；
- sustained action；
- transient / short-event action fidelity；
- rollout drift；
- revisit / persistent state（接口允许时）；
- latency / FPS。

### E02 — capability × stage
目标不是 leaderboard，而是 structured relation：哪个 capability 在哪个 stage 变化、是否与 generic quality 解耦、是否存在 positive exception。

### E03 — factorized attribution
只有 E02 出现稳定 signal 才启动，尽量区分：
- architecture causality；
- denoising-step compression；
- clean vs self-generated history；
- chunk/cache serving。

不具备理想 factorial 时必须写成 bundled comparison。

## 旧 seam 资产如何用
[`../video-world-model-temporal-interfaces/`](../video-world-model-temporal-interfaces/) 的 phase-balanced replay、short pulse/step、grid shift、teacher/student comparison、MG2/minWM/HY-WorldPlay harness，可作为 **action temporal fidelity** diagnostic。

但不继续旧“扩到 5 个系统 + 调 overlap repair”的路线；只有它能区分 conversion factor 时才复用。

## Hard novelty boundary
必须正面对照 Vid2World、Self Forcing、MotionStream、Causal Forcing、Astra、ForgeWM、ActionSplice、WBench / PlayWorld / R2M。

> **ForgeWM 已经有 Stage 0–3 ablation。我们的结果若能被压缩成“更细的 stage ablation”，立即回到 measurement 重新找对象。**

## 人审触发
- E00 找不到两条可比 lineage；
- E02 出现跨 lineage capability-specific pattern；
- generic quality 与 functional capability 明显解耦；
- 某 recipe 成为清楚 positive exception；
- 需要大规模训练或想提出新 loss/module；
- 第一次出现一句话 paper thesis；
- 新 prior 直接拥有 emerging claim。

## Do not
- 不从零训练 foundation WM；
- 不先发明 architecture 再找问题；
- 不把 distillation / causalization / chunking 混成一个词；
- 不把 synthetic seam failure 外推成 general capability；
- 不为了 deadline 扩大低价值 story。

## 决策记录
- 2026-10-02：旧 seam-specific MAIN 因 scientific scale 与最新 ownership 边界降级。
- **2026-10-02：本 territory 作为新的 ACTIVE-MAIN。** 原因：直连主流 real-time conversion pipeline；公开 stage checkpoints 支持 inference/measurement-first；适合多 GPU 独立横向实验、弱跨节点互联的资源。

## 资产
- 调查：`../../library/themes/video-world-models/REALTIME_CAUSALIZATION_SURVEY.md`
- `CLAIMS.md`、`PAIN_LOG.md`、`experiments/`、`logs/`
- 旧 harness：`../video-world-model-temporal-interfaces/`
