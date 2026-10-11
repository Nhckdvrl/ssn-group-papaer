# E95：实际语义比较能否识别被逆向credit漏奖的关系修订？（2026-10-08）

- **状态：** DONE；完整注册三族已封版，旧INTERIM版本保留。
- **对应：** I07 / P20，E91/92块与E94具体实现诊断均已收束，现假说包括误读、语言生产偏好、inverse不适定；不是新领域或新主线。
- **问题：** 同一grader能够实际选择较正确的解释，是否仍在原观察重建排序中漏奖它？这个比较决定“grader不会理解”与“评分通道没给理解credit”的相对优先级，不继续LP suffix／模板／clip控制。
- **设置：** E91全部648冻结P，108原Source／54发表pair／三个old generators，使用8项Step Plan明确POST-HOC更正后的全部原子支持labels。P和Source／问题内容完全不改，源相关已有标签不再重审。三当前grader Q/G/Min，native greedy真实A/B/C回答（C=Tie），两个候选顺序，两个模式：NATIVE语义比较；RECOVERY仅追加一句要求globally correct grammatical parse、避免按局部prefix选，R8对照。Source／原Q集／两个原P，完全无teacher labels／bank名／模型名／奖励入prompt。64token cap事前固定，不使用forced-choice LP作为实际行为。108×3generator×2order×2mode×3grader=3888新实际输出。
- **语义参照：** 原E91 balanced fidelity（positive_retention−unsupported_assertion）排序为主，两维皆存在时使用（GP40／cue43，不造缺失Gold）；原E70全部问题source-pattern accuracy排序为完整108源辅助，无任何label/结果筛选。数值相等为Tie，问题相同而全句未认证同义的范围明确；不能把局部注册QA覆盖叫完整世界解释。标注只由已完成Step5供给，open graders是被测输出，不当新Gold。
- **读数：** actual对teacher-semantic order的准确率与unknown/cap上下界；原E91同grader raw reconstruction对两个P的rank作固定比较，Δactual−raw的paired来源cluster CI；原semanticTie／更好BASE／更好TARGET类别、三构式／GP-cue／generator/grader／顺序与R8变化全量报告。raw score exact ties仅1e−12阈值，直接graders的Tie单列，不能把不分辨的平局当错误反转。semantic changed子群是诊断，所有数据含NA的覆盖留主表。
- **阳性对照：** 首个输入实际重复token一致；两个P完全相同的自然已有pair为Tie锚，source-known self parse不当latent capability证据；正文question-list只有原Q无Gold。新data／旧score配置／Source/P SHA逐项核对。
- **噪声地板：** 固定BF16/eager／同原生模板／greedy；解析只显式Final Answer [a/b/c]或独立字母（c=Tie），未停与无答案按上下界。候选顺序同报；新prompt看到两个P提供了额外对照，实际语义比较不等同原生无候选阅读能力，不虚构同一Bayes joint。
- **混杂边界：** 三grader未做ABBEL训练，旧P来自source-bank干预非当前model原生belief；直接judge与raw比较不同接口。方法只是现成content verifier范式，不声称我们首创direct grading或Min2022 channel scoring。若能识别而不给credit，是后续机制对象；不是整篇论文已完成。
- **决策表（跑之前写）：** actual语义比较／一句恢复可靠而raw分差失配→评分通道问题更有价值，下一要区分production bias与conditional任务不适定并寻找学习后果；actual同样弱→目前更像解释本身困难，不能说能力已在但被reward漏奖；只Tie优势或只某grader/构式→限定对象，不硬扩；actual不优于raw→修正I07，不续judge措辞链。今晚找值得追idea优先，不要求加全部paper控制。
- **算力：** 估计≤5GPU·h，8单卡按3/3/2等待既有E93相应slot释放，0新模型下载／0API；不打断E93、不读partial E93效应，08:55独立释放timer与每任务deadline guard优先，09:00无占卡。为最短实际答案，不开启另一轮长CoT或改64cap。

先构建并CPU三族全输入校对，科学generation排在E93之后。Source／P与全部atoms保持同8项更正版本，原E91/E92 score完全复用。

启动前data SHA1727d0654c1bd863dfe332b574f822c80b9949b4c01b4d4d01819450a40cb804；249／324 fidelity可定义（更好TARGET41／Tie163／更好BASE45），75NA全部保留；pattern全324。三个native输入token范围Q176–309／G178–310／Min684–814。Tie占比高，主全量与预注册changed诊断都必须看，不能仅凭Tie匹配宣称理解能力。

03:24，所有科学forward仍等待E93锁，分析器为已有完全相同P锚增加identical_interpretations分组；不是采新输入／改主读数，不改变主all和changed/Tie预注册scope。

2026-10-08 03:57，任何科学effect读取前prospective分析次序调整：Min族全部shards已完成 全324冻结P对／1296真实回答，可先生成**完整单族探索地图**指导假说；其余固定Q/G任务继续，三族完整主图／所有原指标／CI／cap／data／parser均不改。独立interim文件及scope只供假说生成，不叫三族共同finding、不挑Source或已做对题；这覆盖前述等待全模型才读取的次序约定，原因是尽快利用已释放卡做核心追问，符合用户探索阶段／不防御推进要求。原primary map仍只全三族到齐后生成；未看任何partial Source/teacher labels。

2026-10-08T06:22:28.509912+08:00 完整范围自审：完整三族3888actual/2.394932GPUh，主map forward-semantic-credit-map-v1.json SHA2dbdea41f9ef512f95660b12d589431a3aa0c6b0c54f06b117fa18f32bdbff98。NATIVE每族648输出，Q210/G623/Min0未知；G626 cap包括3已解析，仍上下界按原协议全报。一句RECOVERY Q321/G648/Min5未知。Min95.45%实际Tie，changed不能可靠区分；Q/Gcap使界限宽，不给能力0分，也不支持understanding intact only inverse wrong。全249fidelity eligible/75NA保留，0Source标注，不继续比较措辞网格。
