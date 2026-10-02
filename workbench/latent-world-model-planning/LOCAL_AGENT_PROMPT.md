# Local Agent Prompt — latent-world-model-planning

把下面整段作为执行机 agent 的启动提示。**不要重新找题；先继承已经做完的 literature/code hardening。**

---

你正在 Nhckdvrl/ssn-group-papaer 的 workbench/latent-world-model-planning/ 工作。

## 最终目标

不是“跑 world model demo”，而是从 compact latent-WM planning 中发展 **ICLR / ICML / NeurIPS / CVPR级**的新认识/方法。我们的资源优势是很多独立GPU，不是多节点大训练；把它用于受控pilot、多seed、多环境、oracle audit和快速idea迭代。

当前科学结果 = 0。不要把SEED写成结论。

## 必读

按顺序完整读：
1. root AGENTS.md
2. root RESOURCES.md
3. workbench/README.md registry
4. 本目录 README.md
5. PAPER_LINEAGE.md
6. LITERATURE_LEDGER.md
7. PROBLEM_METHOD_MAP.md
8. POSITIONING.md
9. EXPERIMENT_PROGRAM.md
10. ASSETS.md
11. HANDOFF.md
12. CLAIMS.md / PAIN_LOG.md
13. ideas/I06_semantic_negatives.md
14. ideas/I03_bottleneck_regime_switch.md
15. I01/I02 parked cards，理解为什么被降级
16. E00–E10 experiment cards

然后：

```bash
python3 tools/process/check.py
```

ERROR先修；WARN理解后处理。不要机械为了清0 warning改科学内容。

## 绝对不要做

- 不从头brainstorm十个idea；
- 不把 prediction≠planning、L2不好、long horizon难、CEM OOD、false negatives exist 当novelty；
- 不删 VOID E03/E04：它们记录了一个被代码审计提前否定的设计；
- 不一次安装所有2026方法；
- 不铺全Cartesian product；
- 不把 cross-trajectory negative称 ground-truth unreachable；
- 不把 oracle variant当deployable method；
- 不筛seed；
- 不擅自改workbench状态；
- 不等待我逐job批准：experiment card决策表允许的下一步自主执行。

## Step 1：资产盘点

先看机器已有repo/env/data/checkpoint，禁止重复下载。

写回 ASSETS：
public entry → downloaded/hash → loadable → smoke passed → numeric reproduction。

不同native repo可以不同venv。不要为了统一framework把依赖搞坏。

## Step 2：E00 resource smoke

单GPU：
- dataset/checkpoint
- env/action/goal/success checker
- planning闭环
- train step
- planner call
- render/env time
- peak VRAM
- data wait

不直接跑100 epochs。

## Step 3：dataset能读就优先 E08（不等训练）

当前第一科学pilot：**Semantic audit of heuristic negatives**。

### 为什么
TD-JEPA：
- paper承认 cross-trajectory hinge会含 reachable false negatives；
- published ablation又显示 removing hinge伤 planning；
- code实际对batch rows做random permutation，loss不查environment connectivity。

RC-aux：
- cross batch goals得到reachability 0-label；
- code也只是batch permutation；
- temporal hard negatives才负责budget identifiability。

所以问的不是“有没有false negatives”，而是：
> **这些negative的收益来自semantic correctness，还是global repulsion/scale/dispersion regularization？**

### E08
instrument pinned sampler，不改它：
- TD-JEPA
- RC-aux

TwoRoom优先，因为可拿 episode/step/position + topology做oracle/certified bounds。

保存 pair provenance：
source episode/step, goal episode/step, negative type, budget/margin, oracle status。

如果 sampler semantic contamination极低 → I06 PARK。  
如果稳定非微小 → E09。

## Step 4：E01 shared instrumentation

LeWM native baseline + TwoRoom + contact-rich task。
candidate logger必须旁路。
restore/replay harness。
H/K/scoring-index全部进manifest。

## Step 5：E02 known decision metric

复制 random/mid/elite alignment、candidate margin、fixed-pool regret。
加 P57 time-index sanity：terminal@H vs prefix@K/running when H>K。

测不到known effect时先修harness。

## Step 6：E09 — mechanism decomposition

E08过gate后先 TD-JEPA：
- FULL
- NO-XNEG
- ORACLE-VALID
- ORACLE-CENSOR
- COUNT-MATCHED VALID
- conditional REPULSION-CONTROL

先1 seed。不要开始就6 variants×5 seeds。

读数：
- semantic calibration
- latent/head scale
- effective rank / dispersion
- gradient norm
- candidate rank/regret
- closed-loop success

关键解释规则：
- oracle filtering变差 ≠ false negative“有益”；先排 count/gradient/dispersion；
- head calibration好但decision null ≠ paper；
- FULL/no-negative方向复制不出来 → 先复现。

E09支持role conflation才E10。

## Step 7：E10 — oracle-free role separation

根据E09机制写 amendment 后再跑。

原则：
- cross-trajectory默认unknown，而不是直接unreachable；
- semantic channel用真正有依据的local/temporal constraints；
- global separation由独立geometry regularizer负责；
- 不用privileged test oracle；
- 真实planning必须不降或改善。

如果oracle upper bound很好但无oracle方法做不出来，诚实停在diagnosis；不要硬造模块。

## Step 8：I03 / E06并行作为第二矿线

E01/E02后可以小规模跑：
- navigation + contact-rich
- goal distance bins
- candidate budgets

oracle layers：
representation/metric、dynamics、action discrimination、proposal/search、time-index/replanning、horizon/target。

显式控制：
H、K、frameskip、action block、terminal/prefix/running cost。

只有跨task observable variable能预测bottleneck/intervention ranking，才E07。

E05不自动跑：I02已PARKED。

## Step 9：多GPU

卡空闲时优先分派：
- independent eval manifests
- E08 audit seeds/batches
- E09 variants
- train seeds（lead通过后）
- goal-distance bins
- candidate audits
- contact-rich confirm

但先local-stage dataset，1→2→4 jobs测I/O退化。不要跨节点DDP。

## Step 10：方法/idea如何继续长

新方法只能来自：
- E## anomaly
- P## real pain
- strong baseline surprising success
- direct-neighbor tension

如果I06成立，优先最小解释：
1. unknown/censor semantic labels
2. certified/local bounds
3. count-matched sampler
4. separate uniformity/dispersion
5. 最后才learned connectivity

每个新intervention建新experiment card，不事后改读数。

## Step 11：写回

每run：
- experiment card result
- raw大文件留节点，git放hash/path/summary
- PAIN_LOG only real P##
- CLAIMS only evidence-backed C##
- logs/YYYY-MM-DD.md
- commit/push

L2前混杂审计；L3前独立校对。

## 什么时候需要人审

- E09说明negative真正作用是什么；
- E10形成跨method/task稳定方法；
- E06/E07形成regime law；
- science C##到L2；
- 需要改变ACTIVE资源；
- 两个lead连续被强近邻或简单baseline吸收。

汇报：
1. E## / commit/hash
2. 核心数字 + CI/train-seed variance
3. C##变化
4. 排除的解释
5. 最新neighbor pressure
6. 下一组最便宜决定性实验
7. 真正需要人决定的事

**不要为了“卡很多”跑不会改变科学判断的实验。**