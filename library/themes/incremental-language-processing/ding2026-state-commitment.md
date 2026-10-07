# State commitment learning: training language models to distinguish computation from memory（作者v1，2026-05；接收未核对）

`[证据级别：主文精读＋全部方法附录]` [arXiv2606.05201v1](https://arxiv.org/abs/2606.05201v1)，作者署Alibaba／Tsinghua，独立实现未核；17p PDF SHA8612fa17a60264a49f9b0c43b0efe93e805516c07637f827a36c97f696eb9eca。main1–8 pp1–9、AppA–K pp12–17全读，p8主结果／消融视觉核；参考文献不等于逐篇读过，运行代码未获得。

1. **论文形态／idea来源（RECONSTRUCTED）：** 从thought过长／错误分支成为未来上下文→区分temporary computation H与persistent answer A→擦H后A是否仍能支持未来任务→counterfactual erasure correctness训练这个接口。新的研究动作是future-use sufficiency的训练对象，不仅压缩率或“写一个摘要”。
2. **与近邻的距离：** TokenSkip／Halo／LightThinker等保留或压缩过去trace，作者CERL＋HSCO训练删H后的未来正确性；MemAgent／MEM1／其它学memory本身已存在，作者的首创表述不可泛化成所有state interface从无训练。I06一般可携带／可用解释和I07未来用途不足都有近邻，增量须落到正确关系更新。
3. **方法：** 同x,H,A生成matched full与删H context，下游重新生成；4H×8A×两侧4continuations＋4skip=260条/x。A reward为删H correctness（失败−ψ）减A peer-relative长度与成功continuation相对min-length惩罚；H reward为其8个A的删H平均正确率，两段gradient不重叠、逐渐扩大erasure。不是字面重建reward，不把I07外域结果叫本方法错误。
4. **对象与构念：** PSS定义为条件于同tuple删H后正确概率不低于full，是task-projected条件；ASG=Accfull−Accpe、DH／DE分别成功损失／净化，ASG=DH−DE为事件代数。随机paired rollouts的DH还取决于两side采样耦合，不能当独立潜在state概率；MSG>0仅否定完全忽略A重算，作者也明确不证明A是抽象state。删文字还是重算所有剩余KV／隐藏状态未在实现层核对。
5. **数据／实验：** DeepMath103k严格去污是作者报告，skill先生成成功progressive-erasure轨迹，SFT再CERL；Qwen3-8B主、14/32B附、32k context。AIME24/25、ZebraLogic／AutoLogi／GPQA／BFCL3；8sample Avg@8，5seed bootstrap CI文字。8B AIME24 82.1±.6 vs正确性RL79.6±.8，BFCL76.7±.8 vs68.5±.6；ASG−1.5／ESR99.9／MSG8.5为聚合点估计，不是每域机制CI。
6. **基线与边界：** 普通baseline没有相同H/A分段，主表不算其ASG／MSG；matched同family删RL／curriculum／anti-postpone较有意义，但没有matched correctness-only RL的全H/A指标，不能从主表精确测它是否internalize不足。反事实gap未直接优化（会激励full变差）；直接奖励删H正确避免这个显式漏洞，但不保证所有PSS条件自动成立。理论是定义／代数，不是学习收敛保证。
7. **复现与成本：** 全文给260分支和α/β/ψ约值／DeepMath源，却没有完整SFT/RL步数、batch／硬件／精确checkpoint与公开运行代码。visible-CoT audit rubric有说明但未给主表完整率；不能照搬所有“低依赖／成本优势”数字作已独立验证结论。没有因身份或这些缺项桌面否定其idea。
8. **对我们：** 将解释的“当前可读”改成“作为未来接口可依赖”，有显著后果，值得借其研究动作；E90现有source-bank不是完整KV／recurrent迁移，不满足本论文text erasure协议，不能仅拿两个null拼机制。I07若只是评分相关图不够，需具体关系更新对未来使用的影响。保留源事实、删错误工作草稿、改变旧解释是三种操作，不能统称忘记。
