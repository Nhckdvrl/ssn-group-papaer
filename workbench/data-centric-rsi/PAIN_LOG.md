# 痛点日志

更新：2026-10-02。

## 本地实际痛点（执行中观察）

**P01 / E00 源码复核 / Open-Ended math 的反馈题面静默丢失。** 固定源码 `f698f39` 的 `baselines/open_ended.py`（另一个 `math/open_ended.py` 相同）将 3 个 `MathTaskInstance` 与 3 个 `CompletedMathTaskInstance` 混合后统一渲染 `task_instance.instruction`；后者只有 `task_instance.instruction` 嵌套字段。sentinel 复核：`hasattr(completed,"instruction")=False`，Jinja 渲染结果为空字符串，而嵌套字段正确输出题面。故该入口名义上接收 3 个错误题，实际只把 3 个随机训练题写进生成 prompt。修复执行时将错误条目显式映射为 `.task_instance`，保留同预算原始/修复两种输入日志；不能仅据此推断论文 Table 2 的成因，且这本身不是论文 idea。

**E00 工程失败记录。** 首个 LoRA 训练尝试在第一个 backward 因 checkpointing 输入不带梯度失败；已加 `enable_input_require_grads()`，相同数据/种子重试。首次 vLLM 评测因 CUDA 已初始化后 fork 失败；已设 `VLLM_WORKER_MULTIPROC_METHOD=spawn`，相同输入重试。两者尚未产生有效科学读数，不筛除失败成本。

**P02 / E00 / 输出协议影响看似巨大的训练收益。** 原版 72 题 smoke 上 base 6/72、静态训练 21/72；base 只有 17/72 回答含 `\\boxed`。看到此结果后用一句格式指令作 POST-HOC 校准，base 12/72、静态 19/72。352 题统一 few-shot＋格式时 base 45、静态三 seed 66/74/75；再统一换 zero-shot＋格式却变成 base 67、静态 73/80/71，训练收益不再稳定大。接近固定源码的 base few-shot/LoRA zero-shot 原口径为 24 对 58/53/52，因评测 prompt 改变不能解读为训练因果增益。P02 是严肃的 baseline measurement 问题；现在不能把任何有利口径独选为论文现象。下一项生成/选择比较以统一 zero-shot＋格式为主读数，并同时留 few-shot＋格式辅读数。

**P03 / E00–E05 / 简单静态配方是否够强仍取决于评测协议。** 均衡抽取 120 条真实 MATH train、3 epoch LoRA、24 步，在统一 few-shot＋格式 352 题上三 seed 比 base 高 5.97–8.52pp；统一 zero-shot＋格式只高 1.70/3.69/1.14pp，逐题区间均跨零。E04 错误检索在 zero-shot held-out280 上对静态多 5/4/12 题，不达到原预设稳定 ≥5pp；E05 分布匹配的 seed17 又仅比检索少 2 题。不能把“静态足够强”或“反馈有特殊效用”当已证事实。应先比较真实生成数据和强简单数据动作，并报告提示协议敏感性，不围绕单次 2–6 题差距造方法。

**P04 / E06 / Open-Ended teacher 的格式通过率掩盖了复制和数学错误。** 用固定 Qwen2.5-32B 与 DataEnvGym 的 MATH 模板，首批 40/arm 中 no-state 的 schema 合格为 40，但 8 条精确复制本次输入示例；with-state 仅 32 合格，38 条可解析中 9 条精确复制输入示例（其中 3 条是开发反馈题）、3 条同臂重复、2 条 JSON 截断。逐条比对已有真值，在复制样本中发现至少 3 条实质错误答案（如两位数平方根小于 8 的概率给成 4/9，真值为 3/5）；另外有缺少完整提问或引用缺失图形的生成题。数据和提示哈希见 [`results/E06_teacher_pilot_quality.json`](results/E06_teacher_pilot_quality.json)。这是**本地 Qwen 适配和这套 prompt/解码**的质量失败，不推断 GPT-4o 论文结果。E06 的预写质量 gate 未过，先不扩训练；E07 只试一次最小的“禁止复制/要求题目自洽＋更长 JSON 输出”修复，若仍失败则不围绕这套 teacher 无休止调 prompt，转向真实标注池上的动作测量或另一成熟生成 substrate。

**P05 / E00、E08 / 贪心离线评估的单次读数不稳定。** 同一 base、同一 dev1740 文件、同 prompt/greedy/max350、同 GPU 型号、vLLM 0.11 两次独立运行分别 330 和 324 题正确，但逐题文本改变 926 题、对错翻转 50 题（2.87%）。与 dev352 子集的共有题也翻转 11 题。评分器和文件完整性已审计一致，首要怀疑是 vLLM V1 离线调度/数值路径；不能借这个小现象写论文。按 [vLLM 官方可复现性指南](https://docs.vllm.ai/en/v0.11.1/usage/reproducibility/)只关闭 V1 multiprocessing，dev352 双跑仍翻转 8 题；加 eager 后两次预测文件哈希完全相同、翻转 0。E08 将统一 eager 重评并复跑完整 base，旧模式 1–2pp 差异均降级为未定。根因未做 kernel 级诊断，当前测量修复已足够继续研究。

**P04 追加 / E07：** 一次性提示修复后 no-state/with-state 的结构合格率为 18/20、20/20，精确复制输入示例两臂均 0；但固定前 10/arm 人工抽查至少 4 道答案可证明错误，另有 1 道题设矛盾。完整题目、SymPy/穷举核对、成本见 [E07](experiments/E07-teacher-novelty-repair-gate.md)。按预写 gate 停止该本地 Qwen prompt 路线，不把“格式通过”当“可训练数据”。[DataEnvGym 原论文 Table 6](https://arxiv.org/html/2410.06215v3) 中 GPT-4o-mini 在 MATH Open-Ended 也未带来收益，弱教师风险已被近邻拥有；本地失败不能冒充新科学现象。优先用真实标注池比较动作效用；P04 暂不能升为通用论文问题。

**P04 追加 / E09：** 更换 Qwen3-32B thinking 后，20 次调用的预注册严格数组格式仅 1/20；事后接受完整单对象也只有 16/20 可解析（3 次 3072-token 截断、1 次非法 JSON 转义），其中 13/16 题的答案和题解完全可训练。两道有确定错误答案，一道答案对但题解把 Hessian 行列式写错。对象格式是独立的协议问题，不能把 1/20 伪装成数学正确率；即使消除格式差异，8/10 每臂和 13/20 完整可训练仍不达跑前门槛。不继续调本地数学出题 prompt，也不训练污染监督的学生。外部强 teacher/可验证动作空间仍可探索，**不因本地替代失败判 DataEnvGym 或生成数据这个领域无效**。完整核查见 [E09](experiments/E09-qwen3-teacher-substrate-gate.md)。

**P03 追加 / E08：** 在统一 `VLLM_ENABLE_V1_MULTIPROCESSING=0`＋eager 协议及完整 heldout1668 上，静态三 seed 比 base 多 **70/61/67** 题，确有稳定学习收益；错误检索各比同 seed 静态多 **13/19/22** 题（0.78–1.32pp），逐题区间均跨零、低于预写 2pp 追进门槛，且每 epoch 监督 token 多 16.3%。匹配级别/题型/字符长度的 seed17 只比静态少 1 题，但监督 token 又比检索多 7.7%，不能从此隔离“看到错误反馈”的因果效应。旧/新 base 在 72 反馈题上各错 60 题，却只共同错 53 题，E04 的冻结动作也不是新协议下精确对应的错误集。完整结果见 [E08](experiments/E08-full-dev-data-action-ranking.md)。这限制的是**当前浅层词面 selector 的追进价值**，不推断动态生成或其他状态无价值。一个更有信息量的下一步须改变动作空间或学习状态，并与这一简单配方比较全链路收益。

**P03 追加 / E10：** 为确认 120 条/24 步学生是否过弱，在运行前冻结了包含旧 120 条的 960 条金标静态集，从同一 Gemma2 父模型独立训练 3 epoch/180 step，再与 base、旧静态120于同一 A100/eager/full-dev 比较。heldout1668 为 **320/391/375**，更长/更多静态数据的单 seed 反低于旧静态 **16 题（−0.96pp，逐题区间 [−2.94,+0.96]pp）**；960 输出最终答案格式更频繁（1504 对 1259/1740）、训练 loss 有限且完成 180 步，没有发现明显格式或训练失败。扩集同时增加数据/监督 token/步数，单 seed 无法说“更多数据有害”。对两状态按同一错误检索规则选 120 条新增题，**110 条相同**；即使当前学生会错不同题，词面动作也难改变。此处最明确的痛点是**当前 substrate 中反馈的行动通道过窄、强静态已难超越**，不是 student state 从不重要。停止 TF-IDF 跨状态训练矩阵；在下一项 GPU 前先找到与强静态训练内容实质不同且答案可验证的行动空间，或换成熟 substrate。完整 [E10](experiments/E10-strong-static-state-gate.md)。

**P06 / E00–E10 结构复盘 / 已有测量与目标量错位。** E00/E08/E10 证明当前改造版 MATH/Gemma 学生环路可训练、可确定性评估；E04/E05 的错误检索只作用于固定真值池，E06/E07/E09 的本地教师均未跨过题解质量 gate，因此至今 **0 个**通过质量 gate 的反馈生成动作进入学生训练，也没有一次实际测到“改进器在新 episode 学会选更有用数据”。静态120 的完整 heldout1668 三 seed 相对 base 稳定 +3.66–4.20pp，检索再高 0.78–1.32pp 且多 16.3% 监督 token；E10 的两个训练后状态词面行动重合 110/120。问题不是负结果太多，而是反复把数据有效性、动作差异或第二学生状态的资格门当作主科学问题的推进。E11 草案又回到两组静态数据，虽可筛素材，却仍不能测试反馈/改进能力，故运行前搁置。这个 P06 是**当前研究执行与 substrate 的结构痛点**，不属于领域普遍规律或新论文主张。DataEnvGym 固定源码的 code Open-Ended 入口生成题后另调用模型解答、直接渲染训练数据，未见新题执行验证；SQLM code 自生成测试并需 SandboxFusion、默认 4 GPU；Curation-Bench 官方为固定池策展，README 所列约 1TB 是整套安装前提，**不是单任务需求**。三者是下一 substrate 选择的具体边界，非“哪个方向已死”的判决；逐项源码和定位见当日日志。后续 GPU 卡必须测一个可辨别、可信的数据动作对**真实训练效用**的增量，并含强静态/冻结策略同预算对照。

**P06 复发机制及 E12 边界（用户再次指出后复核）。** 连续转向并非一串被证伪的论文假说：E00/E08 是学生闭环与评估协议建设，E06/E07/E09 是本地 teacher 质量失败，E10 是当前词面动作区分度失败，E11 是运行前被撤下的静态草案。真正反复出现的执行错误是：每当目标中的一个必要环节不可用，就把“修好这个环节”当作下一项科学进展；局部问题修完后没有重画从本次读数到“反馈改善下一次数据决策、且改进器在新 episode 迁移”的证据链。当前 E12 也有同一风险：四条 seed17 静态 SFT 即使得到可靠排序，也只证明底座存在策略效用差，不能证明反馈的决策价值或 agent 的学习能力。更冒进的一点是，在未训练 base 的八项阳性对照尚未全部完成时，后两条预写静态训练已经启动；前两项评测通路虽有实际分数，这仍承担了若全套评测失败时浪费训练的风险。四条已启动分支保留，但完整 base/四策略的可信评价之前，不追加公开错映射诊断臂、多 seed 或局部策略变体。下一项科学实验的入场条件不是“又有一个分数差”，而是事先说明反馈观测如何选择**与冻结强静态/普通优化器不同**的可执行动作、同总搜索成本下怎样比较终端训练收益、以及哪一个新学生/任务 episode 用来检查改进器本身。若无法给出这条路径，不用 E12 的额外 GPU 填补空白。

**P06 独立复盘后的纠偏边界：** 上段将“下一项科学实验”统一要求为反馈决策与新 episode，表述过度收窄。这条证据链适用于继续发展 I01/I02 的可适配/可学习改进器主张，不能成为整个 workbench 的硬门槛。用户的母目标是从强 baseline 的真实瓶颈、意外成功和文献张力发展重要问题；如果静态配方成功、训练剂量或优化行为出现可重复且有实际后果的结构，允许直接研究数据选择/课程/训练系统，而不为 RSI 名称强造反馈 agent。当前 E12 只有首个 ICONS seed17 全套训练后分数，尚无四策略排序；剂量差和子任务回落只是已量到的事实，不能据此自动立新 idea。下一张科学卡需回答“这个读数改变哪项研究判断、强近邻已有哪部分、最便宜实验区分什么”，具体贡献若不涉及改进器学习，就不强加迁移要求。既不通过资格门刷进展，也不把某一种预设论文形式当答案。

**P07 / E12 跑前源码审计 / 数据策略身份与父模型不能靠 README 名称推定。** 深读 Curation-Bench 论文 B.1/Table 10 与固定源码 `24eea15`，论文链接的 LLaVA 预策展父模型是 `anonneuripsmail/llava-1.5-7b-init`；发布 README、`train_llava15.py` 默认却写已指令微调的 `llava-hf/llava-1.5-7b-hf`，两套 14.1GB 权重 shard SHA 全部不同。没有证据证明论文实际跑错，**但照 README 原样跑无法直接声称复现论文初始化**。原始 LLaVA 665,298 行只有 **389,722 个不同 ID**、87,738 个 ID 重复；ICONS 发布的 133,046 条在原 JSON 中 **全部按完整记录唯一匹配**，但公开 `icons.py` 的“ID/图像路径→最后位置”映射仅 **74,845** 条指到原记录，另 **58,201** 条错指，选中的不同位置只有 100,408。ARDS 发布 199,586 条记录按 `original[global_id]` **199,586/199,586 全记录精确匹配**，而公开 `ards.py` 做 `global_id−1` 则 **0 条**全记录匹配；60,690 条仅同 ID+图，138,896 条连 ID/图不同。第三方 Arrow 全量 665,298 行的 ID 与规范化完整对话均与原 JSON 同位置一致；因此不能再把简单 ID/位置查找视为可信策略身份。ICONS 的纠正/原映射两臂真实 SFT 才能量其训练后果；ARDS 主臂直接使用全记录证实的零基位置，不围绕第二个 bug 再开诊断卡。两者均不能从公开代码推断论文作者当时实际用了错误映射或其分数失效。`lookup.get(id) or lookup.get(image)` 另有 index0 边界问题。E12 在任何 GPU 前冻结论文 init、完整记录映射与八项审计；这属于复现有效性痛点，**不是可写论文的独立 idea**。论文 Table 7 的更强 LESS **33.6±0.3** 对开放式 agent **33.7±0.3**，也纠正了此前只看 ICONS/ARDS 的弱基线叙事。来源和执行边界见 [E12](experiments/E12-curationbench-strong-policy-utility.md) 和 [ICONS](results/E12_icons_mapping_audit.json)、[ARDS](results/E12_ards_mapping_audit.json) CPU 审计。

**P03追加 / E12完成与E13研究动作（2026-10-03）**：四个seed17静态分支的完整八任务均值已齐：random32.2994、五视觉源均衡33.4431、ICONS公开133K池随机10K精确复用32.8145、ARDS32.9515，base28.9560。没有评估fallback，独立raw重算一致；一次同random checkpoint异节点复评变化−0.0519，训练方差仍未知。简单均衡的成功真实存在，但不是各任务全面胜出；ICONS在MMBench相对random+3.608、均衡仅+.086，而均衡主要收益含MMMU+5.333。**没有证据据此关闭I01/I02，亦不能裁判原ICONS按10K预算重求票算法**。本次高信息量问题是：同source×监督剂量的新记录，能否保留策展池的训练价值、从而改变补货决策？[E13](experiments/E13-reuse-replenishment-action-pilot.md)冻结init/used两状态×replay/池内补货/池外廉价律六支；9954记录替换、93.974%监督token覆盖，长文本覆盖不足的边界显式保留。不是再建资格门，也不默认matching控制本身是novelty。若效用无实质差，不继续增加属性/状态矩阵；备选研究动作是选择目标与实际训练更新权重是否对应，需先补近邻并证明有后果的决策压力。

## 已核实的远程工程边界

- A01：P01 作者模型卡明确只发布 learner；generator/optimizer/training code 不在发布中。来源与处理见 [ASSETS](ASSETS.md)。这是资产边界，不证明科学方向不可行。
- A02：DataEnvGym README 提醒旧 `lighteval/MATH` 源不可用。尚未验证本地替代数据是否逐例相同；修复必须保存映射，不悄悄换 benchmark。
- A03：RSIBench-Data 使用云训练/环境服务，不能把它的命令当本地卡现成训练系统。需要明确的 local adapter，成本重测。
- A04（E00 源码审计）：DataEnvGym 论文 App B.7 写 MATH validation 从 test 抽样；固定源码 `f698f39` 的 `MATHTask(split="val_balanced_subset_50")` 实际从 train 抽样。当前不知道论文结果使用了哪版数据路径，不用它的公开 test 数值选择本地配方。官方 math 示例导出的 `performance_history.csv` 把 validation/test 字段写反，底层逐次 report 名称正确。证据：论文 [App B.7](https://arxiv.org/html/2410.06215v3)、官方源码 `src/dataenvgym/gym/tasks/math/MATH/task.py` 与 `examples/math/open_ended.py`；处理见 E00 跑前冻结补充。这是协议/展示问题，目前不是我们的科学主张。
- A05（E00 数据审计）：替代 MATH 源的 train/test 题面规范化 hash 有 1 题重合。已冻结的 120 条静态训练集与开发/测试分别 0 重合；后续生成/选择分支同样检查。见 [`results/E00_manifest.json`](results/E00_manifest.json)。
- A06（E00 源码/论文协议审计）：固定 `examples/math/open_ended.py` 对 base 用 few-shot，LoRA 后经 `ParallelLlmPredictor` 默认退回只含题面的 zero-shot；本地最早评测给两者同 few-shot 加格式指令，适合公平动作比较但不复现源码提示。论文 App B.1.2 写 LoRA r16/alpha32/dropout0.05，示例 YAML 未覆写而 vendor 默认 r8/alpha16/dropout0，且 YAML `val_size=0.1`。示例 teacher 是 GPT-4o-mini，论文主结果 teacher 是 GPT-4o。全部列入 [ASSETS.md](ASSETS.md) 差异账；源码提示校对另见 E00 POST-HOC 小节。

## 文献压力（不是本地结果）

- LP01：teacher 内生奖励与目标学习收益的距离；P01/P02/P06/P16。
- LP02：改进器跨学生/状态复用与再次优化的成本；P01/P02/P11/P15/P21。
- LP03：知道学生错什么，是否足够决定数据动作；P03/P04/P05/P12/P14。
- LP04：使用相同评估集合搜索造成的选择偏差；P03/P09；这是实验卫生，不预设为整篇论文贡献。
- LP05：合成数据的逐条分数无法代替整组训练效用，已有 P32 及它的 GMRel/GREATS 近邻直接拥有此主张；仍需实测在持续变化的学生、开放式数据动作及更长训练时，何种组级信息真正值得支付成本。这是文献压力，**不是 E08 的本地发现**。

## 后续实测记录格式

`P## / 首见 E## / 代码与父模型 hash / 输入与完整配置 / 量级与重复次数 / 更强 baseline 或一句指令能否消除 / 关联 C## / 下一项有区分力的实验`。

优先记录强 baseline 为什么成功，包括不需要复杂动态生成的情形；不只收集支持预设 idea 的失败。

**E13/E14运维收尾（2026-10-04）：** 弱I/O实际同时影响Python依赖导入和权重装载；训练成功不等于已评估。旧E14 judge的PGID限定清理漏掉EngineCore，watch错误信任cleanup_complete，成本低报。新接续使用逐文件SHA一致的节点本地judge权重、跨PGID继承token/start-ticks清理与独立guard，原失败与未知活跃成本保留；这属于工程修复，不另立paper idea。
