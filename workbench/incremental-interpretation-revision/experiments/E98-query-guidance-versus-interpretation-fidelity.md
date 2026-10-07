# E98：提前问得更准，是否反而解释得更错？（2026-10-08）

- **状态：** RUNNING；生成器E431在任何forward前更名E98。
- **对应：** I08 / P21，源于已闭合E65/E67 complete-v2+失败补全地图，不读任何在途teacher部分效果。不改变workbench注册，I07其它固定模型继续。
- **问题：** 提前目标问句能改善真实回答，却把同源自由解释推向明确错误关系吗？只改善requested读数未必改善meaning；问句是hypothesis不是premise，要检验model是否将goal中的关系当成证据，还是一般目标选择/输出组装不同。
- **数据：** 既有E96固定50发表pair／100Source／MVRR-NPZ-NPS，不生成新Source/Goal。其中88 Source的INITIAL问题沿E67原字节；另12 Source不存在exact E67句子，按既有original question_id字典序选首题，不能按共享项目编号套用其它句子的旧Goal。两种goal_origin分别全scope报告；这12条不命名INITIAL诱导。其源支持Yes/No/未知仅用既有更正E91原QA标签exact文本匹配，未匹配标NA不造Gold、不重新审原句。所有100Source进入所有条件，GoalGold分层仅input定义，不能把所有INITIAL命名false assumption（P16）。
- **条件：** NATIVE不提前给Goal；GOAL在Source前显示原INITIAL问句；QUESTION_ONLY与GOAL相同，仅加一句"The reading goal is a question, not evidence; base your interpretation only on the sentence."（R8）。每个条件分别真实Answer-YN与free两句P。Source-first/Task-later，三个条件各自QA/P直到Source末尾tokenprefix完全一致；任务仅Source后变化，统一neutralSystem，QA最后只写Yes/No，P用原Amouyal指令。QA64／P96token cap固定，greedy native nonthinking，3models×100S×3条件×2实际用途=1800新输出，无LP。不是再追goal修复得分／改第三个措辞，而是新accuracy-vs-faithfulness对象及核心R8辨别。
- **角色标注：** 仅新P的Source/P关系用原T4-role-v2匿名Step Plan step-5-preview两遍＋分歧裁决，batch≤5／shared8。teacher不见Goal/答案/条件/model/Gold；完全相同Source/P SHA复用已完成T4-role-v2 packet，不重复源语法／自然度审核。按完整model族流水线，最终全3族主图，未知/未停/cap留界限。
- **读数：** QA真实correct_lower/upper（GoalGoldNA明示），T4_CORRECT_ROLES、GP_MISREADING、OTHER、UNKNOWN/cap；同S的QAcorrect且明确GPmisreading、QAcorrect且rolecorrect，以及GOAL−NATIVE、QUESTION_ONLY−GOAL配对差；三构式/GP-cue/GoalGoldYes-No-NA全scope，Source→原paircluster bootstrap10000 seed98。明确错角色与纯遗漏分开，不从两个群体平均反向就推同Source矛盾，也不把跨task外化等同唯一latentparse。
- **阳性对照：** 各条件自己的cue侧、NATIVE同frame自由基线不借E96不同task例子的旧分数。CPU三族QA/P sourceprefix一致、Goal/source SHA/exactmatchedGold验证；固定首QA必须repeattoken相同＋stopped/parseable，首P repeat＋stopped/非空后科学forward。SOURCE在两用途前，所有原事实始终可见。
- **噪声地板：** BF16/eager/seed98／same原native模板，不扫letter mapping/温度/层/更多Goal措辞；QA严格source entailment与T4忠实主要事件是不同构念，SourceGoalTrue不能凭“不增长”判能力不存在。QUESTION_ONLY只是操作辨别，若恢复不代表唯一内部机制，若失败不继续控制。
- **决策表（跑之前写）：** GOAL提高actualQA且GPmisreading上升、joint同Source成立→“回答奖励遮蔽解释损伤”有当下对象；QUESTION_ONLY恢复role并保QA→更像目标/证据接口可修问题，下一选一般用途而非层网格；只有OTHER/格式变化或QA不升→修改旧悖论，不能把旧forced-choice收益叫actual能力；现代不出现→保留旧三族范围、不以benchmark失败为架构结论；只一族/一构式→限定，不拼成一般规律。
- **算力：** ≤4GPU·h估计，8独立slot Q3/G3/Min2，每slot等E97完成再上既有锁，0新model／0Source标注。新P需要900 assignments的T4、exactpacket去重后双遍，唯Step Plan；0现金API。08:55timer与排队/每题guard优先，09:00硬停。实验目标是探索值得追叙事，今晚不要求完整RL方法/全部paper控制。

最近邻定位：Hu/Levy已有QA/probability构念差；Hanna已有GP多parse和QA不复用；false-presupposition QA研究已有拒绝假问题；query-awarecompression已有query可见性与reuse差。拟增量是非assertive目标问题的输入干预使任务correctness与明确错关系相反，尤其同Source能答对但自由表达更错；还不声称这是新机制已证。新目标不是修旧Goal路线的窗口/格式，而是原完整数据揭示的不同后果。

04:48任何E98 forward/API前数据预检：E67 item_id与E96不同，且12/100 Source无exact sentenceSHA（不是14，逐条计数已核对）；不用近似句子/同cluster替换。固定fallback上述原题排序，Source100不删。dataSHA b9b09ff4383765c281c5d9830ba99cf9c67587a6b4d50c8fde94fde361ab67a5，GoalGoldNo88/Yes12/NA0，goal_origin E67_INITIAL88/fallback12。全100主图加88原INITIAL子图在任何效果前确定。

04:49三族100×3 QA/P sourceprefix全部CPU一致；8slot已按E97 sealed cfg排队。完整首源six-use repeat/stopped/QAparse instrumentation优先；不预读任何E98 P效果。

04:58 POST-HOC instrument gate amendment，尚未读任何E98 scientific outcome/role/QAeffect：Min slot4首源P达到96固定cap而确定性repeat无误，slot5首源通过并已继续；旧gate将固定首P的cap变成全shard过滤，造成非科学幸存选择。保存pre-instrument-amendment-code原脚本；改为P非空+tokenrepeat完全一致，stopped/cap真实记录，所有P cap在主要role/joint读数严格UNKNOWN上下界，不猜结论、不升cap、不改wording、不移除Source。QA首源stopped/parse严格gate保持。仅重启原失败slot4，其它原native输出未更改，两个gate版本cfg/provenance都保留。此前首P-must-stop预注册偏离明确登记，不包装成原始设计。
