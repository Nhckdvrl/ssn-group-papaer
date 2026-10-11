# E26：事件约束能正确访问时，可迁移的关系预测痕迹意味着什么？（2026-10-05）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I01/C04/P11；E25跨actor新事件的likelihood变化，需要独立的scoped-use与原S1 final解释读数。
- **问题（一句话）：** 在关系预测痕迹已迁移到新人物/新活动的同一source上，模型是否仍能正确使用旧活动的局部约束并理解原句的最终主体？
- **设置：** E24/E25同24source/12verb-family，原S1/角色事实/continued桥逐字复用，仅在后续activity/neutral句之前截断passage。每source×GP/cue×2role×2named/generic，共192passage-context；3scope（原event/同actor新event/另一actor新event）×2兼容/矛盾问法=1152Q，再2source final proposition（原matrix主体/换为原actor）=384Q，共1536Q。附加事实始终用原事件被排除患者：ref-only为原NP、NP-only为原actor self/reciprocal；新actor self形式按同verb原source字段换正确gender/number，不误用旧actor的反身词。两个独立Luna匿名768审3hash/有效性/答案/歧义，gold以外部clear判定，在model前完成。原问题概念改为明确“first sentence states”避免把世界可能性当assertion；scope任务只问additional fact的兼容性，不把新事件患者当既有事实。
- **读数：** 原始native no-thinking chat的Yes/No choice agreement、p_correct、choice_mass、greedy label valid/correct。base普通答题指令；repair仅加一句Keep the actors and activities distinct: apply each participant restriction only to the actor and activity it specifies。均passage→proposal→question，无fewshot/prefill/顺序搜索。每scope、source intended/actor-swapped、GP/cue、base/repair全部报告；主同context 6scope+2source-control八读数joint-all-correct，在每family的两source和2role×2style contexts先平均，再12family paired bootstrap10000/seed20261005/95%CI。all-clear及prior-role/scope-faithful clear共同完整family层，未审gold保留null，模型仍评分所有输入。所需源码指标事前写，不挑label/query赢家。
- **阳性对照：** old excluded追加命题确实contradict同活动only事实，另两scope不被旧限制禁止；两等价问法标签翻转，避免全部No或单一答法凑高分。source intended/asserted与actor-swap/not-asserted不能互换，用于区分只读latest only信息与final原句理解。choice_mass/greedy validity同步，不用归一化prob掩盖其它输出。外部反身词/事件范围audit在推理前完成。
- **噪声地板 + MIE：** FP32数值漂移小，主要source-family CI和外部语义判定；没有自动通过gate，零bootstrap CI也不代表population perfect。读数表示固定任务对外部标注的agreement，不能单独证明潜在结构/一般能力。
- **混杂审计：** 源句GP与cue只是作者comma；question在末尾可能促进重分析，因此此结果是末尾可访问的约束/解释，不证明问题出现前隐状态已正确，也不推翻隐藏旧parse可能性。既有likelihood痕迹不是同一个QA指标；新颖性须来自**其可迁移范围能否区分old-event memory与template prior**，不能卖generic probability-vs-QA gap（Hu/Levy与Hanna等已有owner）。兼容性按普通分离actor/entity discourse读取，coref/range歧义由teacher保留，不由parent强标。R8恢复对照是任务特定提醒，不当新的parse机制。
- **决策表（跑之前写）：** scope及原S1两控制可共同正确、且E25可迁移trace保留 → 支持“单凭关系surprisal信号不能识别old event未修订”，进一步定位portable关联来源/自然使用后果；source final读数错而scope对 → latest only被访问但旧S1理解未证，不能讲成功reanalysis；scope也错且repair有效 → 默认访问/任务策略竞争，不讲一般revision无能；scope错且repair不恢复 → 先查标签/具体item/构式，不扩模型；choice mass低/非label输出多 → 明确instrument不适用，不拿归一化accuracy当能力证据。不会因任一分数跨任意阈值自动标idea好坏。
- **算力预算：** 两空闲H20按base/repair独立，1536Q各一片，总3072native next-token任务≤.12 GPU·h；本地pinned Qwen3-8B frozen FP32/SDPA/seed0/TF32false/batch8。**实际：** base111.687s、repair134.387s，总.06835382 GPU·h。
- **命令：** scoped_access.py build/adopt；infer.py --experiment E26 --data $IIR_CACHE/E26-material-preparation-v1/audited-v1.jsonl --recovery-mode base / repair --dtype float32 --batch-size 8；analyze_scoped_access.py --runs两immutable分片；raw passage/QA/gold/results只cache，git为hash/stat/code/card。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

1536Q全部外部clear、3072任务完整评分；所有greedy输出为Yes/No、choice mass最小.99999994，不是非标签输出/归一化mass伪影。全12family与prior-faithful9两层均保留。

base GP source-final94.79 [85.42,100]%、actor-swap91.67 [79.17,100]；cue两项均100%。但原活动scope平均50%、同actor新活动GP52.08 [50,55.21]、另一actor新活动57.29 [54.17,60.42]。八项joint base为0；repair GP1.04 [0,3.13]、cue0。不能由较高final source读数宣布scoped interpretation已可共同使用。

**POST-HOC polarity拆分：** base原event consistent与contradict两问全部192个No；前者100%对、后者0%。同actor新event consistent只有9/192 Yes（4.69%对）、contradict192 No（100%对）；另一actorconsistent32/192 Yes（16.67%对）、contradict192 No（100%对）。平均50不是专属scope错；关系算子/命题验证/No default仍竞争。scope提醒没有整体修复，不能用当前instrument证明不会scoped revise。

[完整统计](../results/E26-summary.json)、[POST-HOC极性拆分](../results/E26-polarity-decomposition.json)、[每family](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E26-per-family.csv)、base/repair配置与audit均已存。按决策表追why：E27同一原活动加入明确允许患者的additional fact，保持relation questions/提示/model不变，区分No default与proposition verification（两问都Yes）及正确关系比较（consistent Yes/contradict No）；不扫模型/措辞。I01 PILOT，C04仍仅transfer measurement，未得到scoped-state与portable-trace共存的证据。
