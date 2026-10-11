# E28：supported / contradicted / undetermined的事件状态（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I01/C04/P11；E27允许命题能正确比较，forbidden/未指定仍须分开contradiction与underdetermination。
- **问题（一句话）：** 模型把当前角色事实正确保留为局部event约束，还是把其正/负关系推广到新活动与新actor？
- **设置：** E26/E27原192context，5state读数：old_supported、old_excluded、sameActorNew、otherActorNew、unrelatedUnknown控制。4核心关系仍同source/S1/role fact/活动桥；两个new branch的hypothesis都统一用同一个原NP（两role事实完全相同target），防止新self/reflexive nominal预设让“未知”含混。unknown控制为同一已审上游第一filler整句David投资cryptocurrency，未自行编新动作，原文本留cache。960premise/hypothesis、24source/12verb-family，2Luna480匿名逐条NLI审计+双hash，gold_relation independent，原source QA gold不改。无NLI labels提前赋给model；teacher interpretation_dependent/invalid保留null，全部model评分。
- **读数：** entailed/contradicted/undetermined class agreement、p_correct、3class概率、choice_mass/greedy validity；old两control/new两branch各自全报告。主同context four-state joint-all-correct，macro=(old E准确+old C准确+new两branch U平均)/3，避免U类多数凑overall高分。两new branch同target下signed-role-carryover=50×[(P(C)|old ref-only−P(C)|old NP-only)+(P(E)|old NP-only−P(E)|old ref-only)]：两者gold都U，量化更新符号是否越过作用范围。unknown filler阳性对照单独报告，5state joint辅助。每family两source/2role×2style先平均，paired bootstrap10000/seed20261005/95%CI；all-clear和prior-faithful common完整source/family，原E25对应共同12/9两层。
- **配置：** 同pinned本地Qwen3-8B frozen FP32/SDPA/TF32false/seed0/batch8/native no-thinking，无fewshot/prefill。base三cyclic A/B/C映射，三class各轮流A/B/C，平均全maps并逐mapping报，不能挑赢家；repair只canonical map0加一句Apply participant descriptions to the actor and activity they specify; a different activity may have an unspecified patient。repair只与base-map0配对，不能与三map mean混比。BASE明确定义三种关系，不是针对具体题给答案。总base2880+repair960=3840任务，两卡独立。
- **阳性对照：** 明确允许E/明确排除C、新活动尚无指定patient U、完全无关原filler U。前两项验证known关系比较，filler验证能输出unknown；只有后两event表现差而filler好，才追scope而不是闭世界/label不能输出U。模型的source final/assertion E26已GP94.79/91.67、cue100%，但此处仍独立量化event facts，不由前者强认state已修订。
- **噪声地板 + MIE：** FP32小漂移、12family CI与independent label uncertainty主导。没有自动through-gate，所有类别/映射/R8同步，bootstrap0宽也非population perfect。
- **混杂审计：** 标准NLI定义/末尾任务能引发重分析，此结果是可访问的local constraint use，不证明question前内部图已正确。不是generic QA-vs-probability novelty；增量仍须来自E25可迁移关系痕迹的对象和范围。new hypoths在两个role fact下同NP/actor/verb，相同语义undetermined；old facts出现位置不同只因role事实本身，这是需要检验的符号传播。unknown control内容不同、缺乏相同predicate，不用于claimed role效果，只作类别可用性。gold_relation与upstream Yes/No schema分开，源答案不改。
- **决策表（跑之前写）：** old E/C及new U能共同正确，而E25跨actor trace仍在 → local约束可访问与portable relation prior共存的行为证据增强，不能再把trace直接叫old event未修订；old controls好、filler U好、new U按旧事实正负变E/C → scope越界竞争增强，进一步测试readout/自然用途及范围恢复；全部U差 → primitive类别/任务问题，不卖scope failure；mapping差大 → 报漂移，不能选最好mapping；repair恢复 → 可恢复的默认use/policy现象，不讲一般无能。先具体item/why再任何扩展。
- **算力预算：** 两空闲H20 base2880/repair960，预计总≤.16 GPU·h；**实际：** 两卡总0.10066848 GPU·h，3840任务。
- **命令：** event_constraint_state.py build/adopt/run --mode base / repair；analyze_event_state.py --base/--repair immutable runs；原prompt/QA/labels/outputs只cache、git为hash/stat/code/card。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

3840/3840独立clear标签与greedy合法，mean choice mass .999662、min .968828。all12主base三mapping平均：

| 读数 | GP准确率 % [95%CI] | cue准确率 % [95%CI] |
|---|---|---|
| old_supported | 99.65 [98.96,100] | 99.31 [97.92,100] |
| old_excluded | 85.42 [78.82,90.97] | 79.86 [72.92,86.81] |
| sameActor新活动 U | 33.68 [23.96,44.79] | 32.99 [23.61,42.71] |
| otherActor新活动 U | 65.28 [59.72,70.49] | 64.58 [59.72,69.10] |
| unrelated U控制 | 100 [100,100] | 100 [100,100] |
| four-state系列joint | 21.88 [15.28,29.51] | 17.71 [12.50,23.26] |

signed-role-carryover GP同actor58.60 [48.95,67.89]pp、换actor12.34 [7.24,18.27]；cue55.92 [46.21,65.04]、13.53 [8.70,18.97]。strict9同actorGP59.10 [48.84,68.90]、cue58.54 [47.57,68.24]，换actor12.88/12.66。不是不能输出U，也不是只由GP造成：明示旧关系的正负方向传播到未指定的新活动，且强烈受actor调节。

映射敏感性不可略：GP sameActor U的map0/1/2分别18.75/64.58/17.71%，otherActor79.17/98.96/17.71%；old C89.58/67.71/98.96%。一句repair canonical sameActor27.08%（base-map0 18.75%），otherActor82.29%（79.17%），不足以修复joint；全部mapping与CI保留，不挑最佳map。

**解释限制：** 这是明确三类任务里的scope-conditioned use，依旧可能含response operator偏向；不能用映射平均掩盖波动，也不能把E25的跨actor likelihood痕迹等同这里以同actor为主的语义过推广。four-state系列joint共享source/role/style但original/new branch的活动桥不同，**不是一次同一passage同时访问四个状态**。不证明内部图、GP-specific错误或question前状态。

**下一决定性动作：** E29源句消融，两种读数并行，检验新活动正负迁移需要最初完整S1，还是仅明确排他事实足以产生；保持全部label映射但不再加问答措辞。E28不足以支持“正确scoped修订与portable预测同时成立”的强主旨，I01 PILOT/C04 L1，未升级。

[统计](../results/E28-summary.json)、[family](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E28-per-family.csv)、[base config](../results/E28-base-config.json)、[repair config](../results/E28-repair-config.json)、[独立材料审计](../results/D0-E28-relation-audit.json)。
