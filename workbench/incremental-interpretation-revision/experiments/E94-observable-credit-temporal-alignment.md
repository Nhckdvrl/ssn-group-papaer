# E94：原观察是否按正确时刻给belief修订credit？（2026-10-08）

- **状态：** DONE；生成器E431在任何reward计算前改E94。
- **类型：** PILOT；I07／P20的独立可观察更新接口，不是新workbench或改变主线状态。
- **对应：** I07 / P20。GP解释改变与agent状态更新不同，本pilot只问二者共同依赖的“观察如何给更新后解释credit”接口；不拿agent结果认证GP神经机制。
- **问题（一句话）：** policy依据当前观察产生belief再行动，若评分器把它直接与行动后观察的状态比较，是否漏奖正确的当前belief并偏好提前宣称尚未发生的状态？研究对象是credit的时间坐标；先区分作者实现与一般机制，不把一个bug叫合格idea。
- **设置：** ReBel作者GitHub tree10f0d2eee4edf2486f32ac9e0c14a85386767e2e；现发布coldstart426episode原始obs/action/step全部，16,442,466bytes SHA0a61235269b17140e22a76d260efd0aec109faeffcb90e4a4d8faf25696d89ae（paper390SFT非同一版本，不称复现训练）。用作者GroundTruthTracker累积观察，给每个有下一obs的原连续step构造b_before/b_after（同官方state schema、已观察到的objects／states／visited／unvisited／inventory）。它们是程序可验证的**累积观察状态**，不是完整simulator GT，parser盲点另列。不调用模型／API、不重审成熟原trajectory。
- **读数：** 作者实际calculate_state_reward的四格：before belief对before/after observation-state、after belief对before/after。主为全部可关联连续transition的after-ranker偏好Δ=R(b_after,G_after)−R(b_before,G_after)，及原before事实的reward变动；分state-changing（take/put/heat/cool/clean/open/close）、information-only（go/look/examine）、其它原action；相同观察状态／实际Nothing happens不单独丢掉。state变化input stratum，不按reward筛样本。字段覆盖、原step、末step无next、seq异常、未知command单列。episode→cluster bootstrap10000/seed94，逐行均值另报。
- **阳性对照：** 输入模板明确先更新current state、再action；env_manager实际先env.step/updateGT再对同条belief算reward，已读279–351。每个state schema通过作者parser，oracle对同一自身观察状态重复reward完全一致，手工公式点核至少held-object transition；这只校工具，不证明世界状态完整。
- **噪声地板 + MIE：** deterministic CPU code，无生成／token布局／seed噪声，exact repeat；bootstrap是episode异质，不是数值随机性。输入状态相同→四格相等，否则报异常不悄改。保留失败／缺失step，不把原teacher生成belief当正确Gold。
- **混杂审计：** code当前revision非论文提交revision，coldstart legacyschema非训练最终输出；仅r_state，不猜admissible phase／终结reward，也不复制keyword预测claim。事实揭示和事实因action改变区分；GT parser的过期事实／substring字段相等不等于语义truth。最后terminal put缺next不补构造，报告覆盖。单实现pilot不支持跨方法／三模型一般定律。
- **决策表（跑之前写）：** after-scoring偏好anticipation且集中action-caused变化→I07里独立时间错配值得下一步检查其它实际接口／动态原任务；只有新可观察信息覆盖缺失→是oracle覆盖问题，不称奖励说谎；全同或before更好→该猜想收窄；若主要parser/schema失败→定位实现，不开修bug网格。一般动作需transition-aware verifier已有理论owner，本pilot不独占它。保留原E93／GP块推进，结果改变对象优先级即可，不要求今晚发展完整RL论文。
- **算力预算：** 0GPU／0新API，CPU1process，原代码与schema离线；不增加GPU排队任务。08:55停卡删权重约束不变。

输入raw/schema先检查后才写科学runner。先保存全部episode/step/原动作及raw SHA；若时间关联不可可靠确定则标缺失，不造next observation。

计算前input-only核对：426episode均为作者选成功轨迹、5409step，全部step1..n连续且单个action tag可解析；不称覆盖失败episode。4983非末step可关联next obs，426terminal无next，不补造。作者tracker某些正则会将from/with relation尾部包含于object key：构造观察belief时仅将inventory字段取首个object instance ID，objects/states原字典与raw GT保持原样用于打分，这些映射/异常逐条记录，不能把程序观察状态称完整世界GT。现代RL prompt先更新当前state再行动已读，coldstart为旧schema而不会使用其生成belief作为真值。

## 完整结果与自审

4983transition／426公开成功trace／36预注册分层，0GPU／0model输出／0API；fullmap SHAb0ce10f9f7fb03c3155faacf88f324b4a4accf79a97bcc787c234907c3e5fb62，逐转移map SHA9029418722ce136788b6508668a55fb7d392e2a9c0e8fcc135c0ca8e8cd5254c，原4格与parser数据全留。全部scope读取，525同state四格全tie、426末step无next保留，不丢失败动作174 Nothing happens。

全部episode等权anticipatory观察投影偏好+.12777[.12371,.13189] reward units，偏好率77.20[75.88,78.49]%；truthful-before投影的评分变化−.10159[−.10484,−.09839]。state-changing1932条+.10400[.09643,.11162]、information-only2978条+.14294[.13726,.14874]，后者偏好率92.49[91.29,93.63]%。它是单个当前code reference的时间错配，未证明模型经训练会提前幻觉。

POST-HOC按原command仅诊断：open1175次raw偏好均值+.1886（1163positive/12tie）；take499次+.0116（101positive/398tie）；put57次全部tie，作者GT regex未正确更新含the/in-on的发布反馈；heat42与cool45全部反向（−.0794/−.0747），可追到compound object-state key与substring匹配碰撞，不能只报positive看起来“奖励说谎”。source-known parser复合key诊断早先只计from/with，实际发布文本使用using；原schema未修，scope范围明确。

决定：这一步提高“奖励的观察参照需带时间坐标／可观察范围”优先级，也暴露具体实现parser问题；**不是合格新idea**，不继续修regex／phase／reward权重控制链。若值得推广，应由独立真实接口／学习后果验证，ReBel理论已有action-aware C(b,a,o)不属于我们的首创。E93完整外域和E67完整自由角色仍会改变I07排序；C06–08L0/C09限定L1、registry不变。
