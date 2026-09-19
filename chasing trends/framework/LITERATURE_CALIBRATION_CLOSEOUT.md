# Literature Calibration Closeout

日期：2026-09-19

这份文件记录 broad calibration 的**收口状态**。它不是另一份 search guide。

## 1. 已经建立的证据库

### Academic

`../academic/` 已覆盖多条纵向 lineage，包括：

- RLVR / test-time scaling
- ICL mechanism
- diffusion fast sampling
- VLA/action representation
- pretraining/SFT/distillation
- architecture/inductive bias
- VLM / multimodal
- speech/audio
- negative/limits
- optimization
- world models

### Industry

`../industry/` 记录：

- frontier scale / deployment pressure
- product knobs
- system/model co-design
- failure provenance
- source ledger

### Startup / HF

`../startup_hf/` 记录：

- public checkpoints
- matched stages
- failed/open artifacts
- scientific FMs
- continual/state/harness/auto-research
- long-horizon correction
- proxy / development-tree evidence

## 2. Broad reading 真正改变了什么

### Basic object 经常移动

frontier 常常不是“换一个 module”，而是：

- sequence → branching token
- final failure → onset transition
- data amount → mixture/exposure
- teacher quality → teacher–student relation
- token input → lifecycle/future utility
- turn sequence → concurrent real-time process
- video generator → action-conditioned transition model

但“换 object”也不是 generator。它必须由真实 pressure 推出。

### Proxy 必须对 consumer 负责

training loss、embedding similarity、visual quality、token count、judge score 都可能只是 proxy。

候选必须问：

> downstream consumer 真正需要什么？

### Failure localization 常比全局修复更有信息量

如果 failure 有局部 onset / specific transition，先定位，再决定是否需要 global intervention。

### Resource constraint 可以成为 scientific variable

budget、latency、memory、stream rate、operator compatibility 并非永远只是工程细节；当它改变可行策略时，它会进入 formulation。

### Public artifact 改变 feasibility

matched checkpoint / small proxy / failed release 可能让原本昂贵的问题获得 cheap causal echo。

## 3. Broad phase 新增的硬纪律

最终保留到正式 workflow 的主要规则已经压缩到：

- `../SEARCH_GUIDE_ZH.md`
- `SPECIALIZED_AUDITS.md`

包括：

- artifact maturity / development-tree audit
- proxy fidelity
- evaluator / oracle / specification separation
- trend maturity
- failure-onset / long-horizon classification
- representation × consumer
- modality placement / multi-rate
- world-model consumer contract
- auto-research / research-memory provenance

不再在本文件重复展开。

## 4. 默认视为 crowded 的 surface

截至本轮 broad scan，以下表面方向不能仅凭热度构成 novelty：

- generic GRPO variant
- entropy/selective-token RL
- generic adaptive test-time compute
- visual-token compression
- latent visual reasoning
- unified multimodal model
- student-aware CoT distillation
- full-duplex speech 作为标签
- generic world model
- CoT faithfulness metric
- generic scaling-law fitting
- generic harness self-evolution

不是禁止研究。

含义是：

> 进入这些 cluster 后，必须进一步找到 attribution / compatibility / new premise / unresolved relation。

## 5. 广谱扫描停止规则

从现在起，不再默认 weekly broad crawl。

只有以下情况重新扩搜：

1. concrete CT candidate 需要 nearest-prior audit；
2. dangerous overlap 未确认；
3. target field 仍只有浅 breadth；
4. 新公开 artifact 显著降低 pilot 成本；
5. trend 进入新的 evaluation-correction / negative-result phase；
6. 用户明确要求重新做 frontier calibration。

## 6. 进入正式找题后的姿态

从：

> “还有什么领域没扫？”

切到：

> **一条 lineage 里，现在真正哪个 pressure 值得锁住？**

然后：

> restore → deep prior → one candidate → identification / execution audit → PILOT-AUTHORIZED or KILL。

Broad calibration 的目的已经完成：

> **让后续找题不再被单一热点、单一论文模板或单一来源绑架。**
