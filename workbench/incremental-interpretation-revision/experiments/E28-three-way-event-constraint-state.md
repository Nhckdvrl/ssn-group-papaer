# E28：supported / contradicted / undetermined的事件状态（2026-10-05）

- **状态：** PLANNED
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
- **算力预算：** 两空闲H20 base2880/repair960，预计总≤.16 GPU·h；**实际：** 待运行。
- **命令：** event_constraint_state.py build/adopt/run --mode base / repair；analyze_event_state.py --base/--repair immutable runs；原prompt/QA/labels/outputs只cache、git为hash/stat/code/card。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待运行。I01 PILOT；C04是transfer测量，不提前定义成错误信念或已修订隐状态。
