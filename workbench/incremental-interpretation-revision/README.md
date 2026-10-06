# Incremental Interpretation & Revision

## 状态
- **注册：** PROPOSED（人授权的 baseline residency；不改变当前 ACTIVE-MAIN / ACTIVE-EXPLORE 分配）。
- **2026-10-06 人决定：**
  - 研究从暂停中恢复，并重置主线：采用 [ROUTE](ROUTE.md) 中的路线，放弃 I01/C05；
  - 先广后深；允许一开始就做白盒；
  - 标注只用 Step5；
  - 资源：同一节点上的 8 张 H20，不用付费 API。
- **执行模式：** 自主执行。本地 agent 按 [EXECUTION_BRIEF](EXECUTION_BRIEF.md) 全程推进，原人审节点改为自审；只有真正卡住，或遇到开线/关线/改状态/进入候选这类决定时，才回来找人（EXECUTION_BRIEF §6.7）。开跑前必须先完成 §1 的整体认知建设。
- **territory 卡：** [Territory Card](../../search/our-taste/TERRITORY_INCREMENTAL_INTERPRETATION_2026-10-05.md)　**目标会议：** ACL / EMNLP / NAACL（按证据成熟度选周期）。

## 一句话（当前主线）
> 强 LLM 能看到整句话，为什么仍然读错 garden-path 句？在增量编码过时、作答时选择失败、合理性组装、测量问题这四种解释之间做归因，再用机制解释模型的"修订"在哪里成功、在哪里失败（[I02](ideas/I02-garden-path-misreading-attribution.md)）。

**为什么是这条路线**（详见 [ROUTE](ROUTE.md) §0–§1）：三个社区在这个问题上互相矛盾。
- 理解问答研究：GP 对 LLM 特别难（GPT-5 非 GP 93.7%、GP 46.8%），原因留作未来工作；
- surprisal 研究：LLM 在消歧处并不太惊讶，而且同时保留两种解析；
- 架构研究：把因果掩码当作 GP 失败的原因。

已有证据（Li 中双向模型同样认同误解；thinking 的效果因模型而异，GPT-5 是明显例外）已经在质疑因果掩码的充分解释。

**已有的起点证据：** 对 Amouyal 公开的 31 个模型结果的审计（[结果](results/D0-Amouyal-released-item-type-audit.json)，无新推断）显示：
- 及物 Subj/Obj 和多数 NP/S 条目在无歧义对照句上同样被答 Yes，提示需区分句中断言与可能的额外事件；仅凭此不能完成错误归因。作者已说明部分 No 意为 not necessarily，原任务约定保留；
- 原作者 gold 为 No 的部分条目上，公开答题差距达 25–65pp（GPT-5 RR 62.5% 对 98.8%）；旧 D0 把 RR 等整类视为“确实为假”尚不充分，需 E52 双遍逐题区分 CONTRADICTED 与 NEITHER，不能直接当作真实语义错误。

## 主张与 idea
- [CLAIMS](CLAIMS.md)：新路线是 C06–C09（L0，待验证）。C00–C05 是旧路线的历史测量，保留，不再推进。
- [I02](ideas/I02-garden-path-misreading-attribution.md)：当前主 idea（PILOT）。[I01](ideas/I01-event-reference-or-lexical-echo.md)：PARKED。
- [PAIN_LOG](PAIN_LOG.md)：P13 记录问句语义混杂，P14 记录单模型与复用 24 句的教训。

## 近邻与可借的研究方法（完整定位见 ROUTE §1.3）
- Amouyal ACL'25/'26：人机行为比较、GP 特别难；
- Hanna & Mueller NAACL'25：2B 模型上 GP 特征共存，QA 不复用；
- Zeng Findings'26：词汇修订的推迟机制、非因果 oracle；
- Guo et al. 2026（CICM）/ Tang ICML'26 / Prakash ICLR'26：显式更新中的"保留但未选中"、查询时汇总、lookback；
- CASTLE / Prompt Repetition：因果掩码有害的前提、重复输入。

从广面实验和意外结果找叙事，近邻的局部发现与方法可以复用。完整故事形成后，说明证明它为何值得兴奋、带来什么新认识，以及是否被近邻完整覆盖；不寻找完全空白的空间，不因局部相似关线。

## 历史与资产
- [DIAGNOSIS](DIAGNOSIS_AND_REDIRECTION_2026-10-06.md)：51 个实验为什么没有得到好 idea（执行为主因，数据为次因，领域本身没有被证伪）。
- [PROGRESS_SUMMARY](PROGRESS_SUMMARY_2026-10-06.md)：E00–E51 逐项结果、失败与勘误。[FILE_INDEX](FILE_INDEX.md)：文件入口。
- [DATA_PLAN](DATA_PLAN.md)：数据来源、许可与审计；新路线的数据方案见 EXECUTION_BRIEF §4。
- 本地 cache：`/data1/xiangding/work/incremental-interpretation-revision/`（upstream / normalized / models / runs）。原始数据、模型和逐条输出不进 git；复现入口见 [scripts/README.md](scripts/README.md)。
- 当前自主执行：[E52](experiments/E52-genuine-revision-reading-map.md)，1732公开QA/309 GP pairs；全文综合和“我的理解”见当日日志/领域地图。Step5全部走Step Plan，≤5项/批；HF资产只走镜像，本地推理离线。E52完整资产在上述cache的`E52/`，精度/接口失败同样保留。
- 数据资格：原双轮/裁决资产`E52/step-full-v4/`保留；两遍一致仍可能把角色逆转误当字面矛盾，已登记反例世界复核。`qualified-v2`只作待复核历史资格，最终主分析入口将为`qualified-v3`，不改变原S/Q/gold或独立T2/T3。
- [E53](experiments/E53-faithful-two-sentence-paraphrase.md)：三族10260个纠正原生输入的复述已生成，T4双轮盲审进行；[E59](experiments/E59-source-grounding-versus-world-question.md)：明确答案语义与字母/词读出对照已登记，待语义资格复核后运行。C06–C09均L0。

## 决策记录
- **2026-10-05：** 人选择本 territory，授权 training-free baseline residency；取消 agent 自加的停步 gate；构造与语义审计改用 Step。
- **2026-10-06：** 人要求暂停并归档（E51 后）。同日，人接受诊断，决定重置主线、采用新路线、恢复研究、标注只用 Step5、先广后深、允许白盒，并上传 main 交给本地 agent 执行。随后人决定采用**自主执行模式**：本地 agent 全程自主推进，原人审节点改为自审，只有真正卡住或需要人做的状态类决定时才回来找人；这条决定覆盖 AGENTS/EXECUTION 中"决策点请人审"的默认规则。
