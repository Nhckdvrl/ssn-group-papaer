# E34：原作者完整预算的正确编码强基线（2026-10-14）

- **状态：** DONE；三个预定seed×两route全部完成原300轮预算，全部阶段与结果保留。
- **类型：** REPRO／训练不足混杂确认，不是新方法。
- **对应：** I02／P06；E25短训、E32正向稳健性、E33完整收益四格。
- **问题（一句话）：** E33中相对利益取向有效而总收益不交叉，能否由30轮训练不足解释？
- **竞争解释：** H1原策略尚未充分学习原生utility；H2身体—利益训练相关性使C单项干预属OOD；H3一致性形成方式改变了效用／语义稳健性。完整预算不是自动收敛保证；H1被削弱后仍不能直接认定H3。
- **设置：** PCSP pin5420f7b，原run_pcsp_v3_large.py默认300 iterations，原train_400_v3与held100，正确last-nonpad编码与E25相同。Full／NoCons，三个预定训练seed42/43/44；各从CPU同初始化重新训练，不把GPU30轮转CPU冒充精确续训。每个seed两route初始policy与首轮rollout须byte一致；仅lambda_consistency不同。η-only已与NoCons政策逐byte相同，不重复计算。
- **训练细节：** 原16人／12×12／69obs／20actions，200cycles，8完整episodes/iter，故每route7,680,000 transitions。PPO4epochs、batch256、lr3e−4、projection lr1e−4、reader lr3e−4、gamma.99、GAE.95、clip.2、value.5、entropy.01、maxgrad.5，Full consistency.5／No0、diversity.01、temperature.07。原sample400不放回取16，无新奖励、数据、动作或loss。世界seed由原iteration×8+ep确定。
- **检查点／选样：** 固定保存30/100/300轮及完整metrics，不按held结果早停、不挑best seed。三个seed全部报告；五个E33人物属于发现样本，跨训练seed复核不能伪称新角色独立确认。若运行异常保留失败日志，不替换seed。
- **读数：** 原生训练utility曲线及held100原始utility、preferred rate、critical needs；E32固定state选择性；E33相同五人物／三世界seed四格完整收益与偏好交叉。30/100/300均按固定读数报告，不事后换primary；重点看训练阶段能否解释收益排序，不能只报差中差。canonical数值控制、原型整体响应、同body原生action→state闭环仍须通过。主要训练seed级报告；3seed不足以声称广泛机制普适性。
- **阳性对照：** 先两route CPU各一iteration成本gate，核初始policy hash／obs/actions/rewards逐byte同一、Full consistency对projection+reader非零梯度；300轮训练的首轮亦核对。仅增加checkpoint序列化，不能改变随机数；与无checkpoint一轮控制比较。同样原编码、原PersonaConfig、原引擎及损失；source/array/script/config/权重hash保存。
- **噪声地板 + MIE：** byte replay为实现地板；三训练seed及三个world seed均保留。不用更长训练自动刷过阈值。相对方向仍有效但总收益无交叉时，不能称改善目标实现；若仅某seed恢复，按不稳定结果汇报。
- **混杂审计：** train/test无ID重叠，但20职业共享，held为新BF组合，不能说unseen occupation。CPU与旧GPU训练数值不同，固定CPU30→100→300比较把设备控制住；旧E25仅作发现背景。所有loss、sampler、训练预算匹配；身体—目标相关性及v3手工风格reward未消除。论文另有MeltingPot／UE5，不将本分支外推全文。
- **决策表（跑之前写）：** 300轮原生utility仍不稳定／角色控制不足→只记强基线未达准入，不立机制；随训练原四格恢复交叉→优先接受短训解释；稳定无交叉但相对取向正→再区分身体相关性／可达策略／样本方差，不能直接新loss；Full跨seed保留语义选择性且有独立utility优势→更新定位再考虑机制。所有情况均不改工作台状态。
- **算力预算：** 当前fvcrc21 24CPU、load约.4、488GiB available；最多6个单线程CPU任务，0GPU/API。先seed42两route单iteration成本核查，预计每轮约29秒；门槛≤40秒/iteration且首轮byte控制通过后运行六个固定300轮任务，单任务估计≤3.5小时；总约18CPU小时。无跨节点同步，使用既有fgvd/deps与cache/runs/e34_*，每任务定期写检查点，不干扰其他用户。若成本gate失败先停在原始测量，不自动扩算力。

## 结果（跑完后填写；不改上面的内容）
尚未启动。

启动gate：Full29.458秒／No21.851秒；初始policy及首轮obs/actions/rewards byte同一；新checkpoint代码与旧CPU Full一轮policy／reader完全一致。三个seed两route共六任务已从头启动，首轮配对控制全部通过；结果文件E34_training_cost_gate.json，尚未读取完整预算结论。

评估执行细节（首个新checkpoint评估前补充）：canonical使用独立world seeds34011/34012/34013，固定seed置换100角色、每组16，末组原样循环补齐但只汇报实际角色。每个actor行动前读fresh observation；先与原_rollout_persona同policy／同seed的homogeneous16人3200frames逐byte对齐。旧E25/E26部分mixed评估采用cycle开头统一observation，不能把其与新数字之差当纯训练轮数效应；本次CPU30/100/300统一同一fresh AEC协议。E32同原固定1200states，E33仍同五base/三world完整四格。pcsp_checkpoint_evaluate.py固定输出三个读数，checkpoint manifest写完才读取，全部seed／阶段保留，不选best。

用户执行准则更新（2026-10-14，原读数不改）：取消以预设MIE／比例／若干base过线作为科学价值裁决或舍弃线索的规则；原卡决策条款仅保留历史。结果按现象、竞争解释及顶会近邻实际证据解释，自由探索。资源预算与实现正确性核对照常记录，不等同科研淘汰bar。

100轮全部三seed测量已完成，Full−No原生episode收益依次+3.0863／−.9452／−1.8403（seed42／43／44）；30轮为−6.2129／+3.8837／+1.1762。训练阶段会改变结论方向，保留全部检查点继续到作者300轮预算，不从中选择最佳种子或科学淘汰。完整读数results/E34_checkpoint_0100.json。

300轮完整结果：六policy各7.68M transitions，全预算合计46.08M。Full−No held原生收益−20.9441/−5.0614/−7.6058，等义相对跨人物log选择性差+.9979/+1.3829/+1.1213。单C原生DD No/Full为1.4022/3.4446、−.5219/−4.8808、1.1480/2.7888；必须读完整四格、正DD并不保证两个目标各自收益更好。E37局部同幅度C功能DD在300轮Full三seed更强，换自身原生状态也保持排序。完整收益与局部响应不同，同时保留而不择一讲故事。见E34_checkpoint_0300.json与E37三个i300结果；C01不升级。
