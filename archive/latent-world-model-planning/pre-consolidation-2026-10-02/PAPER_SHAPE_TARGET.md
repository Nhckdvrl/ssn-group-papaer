# Paper Shape Target — RC-aux-like experimental economics, top-conference scientific scale

更新：2026-10-02。

> 目标不是复刻 RC-aux 的题目，而是复刻它的 **科研经济学**：
>
> **问题尺度大于模型尺度；单次实验便宜；方法简单；大量受控实验能快速推进；最终贡献来自新问题/新认识/新方法，而不是训练规模。**

## 1. 我们最想要的 paper shape

参考 RC-aux 这类 compact latent-WM 工作：

- backbone / scoring modules 只有约千万级参数；
- 单 GPU；
- 不训练大型 video generator / foundation model；
- benchmark/simulator 可重置；
- intervention / ablation 成本低；
- 训练和评测可以 independent parallel；
- failure → diagnosis → minimal correction → multi-task validation 的链条清楚。

这类 work 的优势是：

```text
一个假设错了
→ 当天换一个实验
→ 当天拿结果
→ 再设计下一轮
```

而不是：

```text
一个假设错了
→ 重新训一个跨节点大模型
→ 数天/数周后才知道
```

## 2. 资源适配硬约束

### Prefer
- compact latent WM / small encoder / small dynamics；
- 1 GPU / run；
- 单节点；
- offline trajectory / small simulator；
- checkpoint < few GB；
- dataset可节点内缓存；
- 训练 hours 级，而非 days/weeks 级；
- method variant只改小 head/loss/interface；
- eval可完全独立并行；
- candidate/replay/oracle analysis可大量 CPU/GPU并发。

### Avoid as main contribution substrate
- multi-node synchronized training；
- giant video world model pretraining；
- foundation-model scale architecture race；
- 需要数十 TB 数据；
- 高速共享盘 / RDMA / IB 是前提；
- 一个实验失败就浪费几十卡天；
- novelty主要来自 scale。

## 3. 科学尺度不能因为模型小而降低

小模型不等于小问题。

优先 mother questions：
- data / experience 到底识别了什么；
- predictive object 到底应该是什么；
- task/query specialization 与 reuse怎么权衡；
- state / belief什么时候必要；
- world model何时应该被 trust / repair / bypass；
- planner-consumed semantics如何与真实 controllability对齐。

避免：
- 某层 hidden probe异常；
- 某个离散位置奇怪；
- 一个无自然后果的小 artifact；
- 单纯 +1–2% benchmark trick。

## 4. Idea economics score

每个 seed 在真正铺实验前额外打一个 **Experiment-Economics** 账：

| 维度 | 好 | 差 |
|---|---|---|
| single-run latency | hours | days |
| GPU coupling | 1 GPU | multi-node |
| data I/O | local cache small/moderate | huge streaming |
| variant cost | small head/loss/data change | full re-pretrain |
| diagnostic depth | simulator reset / oracle | only end metric |
| parallelism | embarrassingly parallel | synchronized |
| iteration speed | same-day branch | multi-day branch |
| baseline availability | public weights/code | rebuild from scratch |

这个 score **不是论文价值分**，只用于在多个同样重要的 programs 中选择更适合我们资源的第一批 mining seeds。

## 5. 当前 programs 的资源适配

### R1 Data & Identifiability — **excellent**
最符合 RC-aux-like economics：
- same compact model；
- 改 data regime / supervision；
- simulator可控；
- 多 seed / dataset / objective完全独立；
- 失败也快速告诉我们 data role。

I09/E14、I12/E16 都是高优先级。

### R5 Trust / Repair / Bypass — **excellent**
很多实验可基于 released checkpoint：
- 不必重新训练；
- 同一 state/reset 跑不同 recovery action；
- horizon / replan / fallback / feedback 都能独立 eval；
- 非常适合大规模 condition scan。

I11/E18 是高优先级。

### R4 State / Belief — **good**
cheap oracle阶段极便宜；若最终需要复杂 belief architecture，成本会上升。  
先 E11，不预先开发模型。

### R3 Specialization / Reuse — **good**
若能在同一 compact stack 里做 query placement，单 run仍小；但 variant数量容易膨胀。  
先 small 2–3 variant pilot。

### R2 Predictive Abstraction — **medium**
科学问题很大，但不同 method codebase/protocol差异明显；Bagatella TD-JEPA 官方 pixel runs 1M–2M steps，iteration speed明显慢于 RC-aux/LeWM-style objective tweak。

因此：
- 保留；
- 不作为默认第一 GPU sink；
- 优先从 released checkpoints / smaller state-based pilot / minimal matched comparison开始；
- 只有出现强 regime signal才大量铺。

## 6. 多卡的正确使用

我们不是：

```text
24 GPUs → train one 24-GPU model
```

而是：

```text
24 GPUs →
  4 data regimes × 3 seeds
  + 3 method variants × 3 seeds
  + 3 evaluation conditions
```

把 **GPU count 转成 scientific throughput**。

最理想流程：

1. 1 GPU：smoke；
2. 1–2 GPUs：existence pilot；
3. 2–4 GPUs：排除平凡解释；
4. signal成立：
   - 3–5 train seeds；
   - second environment；
   - strongest neighbor；
   - ablations；
   - hold-out regime；
5. 最后一轮几十个 independent jobs同时完成 paper evidence。

## 7. 选择题目的最终标准

理想题同时满足：

[
	ext{community-important mother problem}
]

[
	imes;
	ext{cheap decisive experiments}
]

[
	imes;
	ext{many independent axes}
]

[
	imes;
	ext{clear method lever}
]

[
	imes;
	ext{top-conference narrative}
]

不是追求最便宜，也不是追求最空白。

**最优是：RC-aux 这种“便宜实验承载大问题”的形态。**
