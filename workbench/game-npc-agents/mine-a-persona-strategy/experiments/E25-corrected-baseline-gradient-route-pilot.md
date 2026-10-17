# E25：正确编码基线的梯度路由pilot（2026-10-14）

- **状态：** DONE / 单训练seed短pilot
- **类型：** PILOT / 形成机制控制；非新损失先验。
- **对应：** I02 / P06 / P09；E17–E24。
- **问题（一句话）：** 移除已确认的编码混杂后，InfoNCE更新η与更新共享φ，各自是否必要于真实NPC控制与读出？
- **设置：** 原PCSP pin5420f7b v3-large 16NPC、原train400/test100、原env/reward/goal/合法动作不变。E23正确last-nonpad原500编码另存，不覆盖作者.npy。Full：原PPO+div+cons；NoCons：原lambda_consistency0；readout_only：原cons前仅对persona_proj返回值detach，η照常训，PPO/div完全原路径。这是因果干预，不预定新训练法。源_consistency_loss无随机采样且各mode仍计算同GRU，所以不另外改world或强同步轨迹；wrapper显式torch/NumPy/Python/CUDA seed42（源train entry只固定persona sampler，torch init未在该entry设seed）。相同初始化、sampler、CFG、预算，目标对照policy byte同一。先各1完整iteration（8episode×16×200），测成本/grad/null；若预计≤1小时/route再同seed各30iteration短pilot。CPU/单GPU按实测选择，最多3独立GPU。只有效阳性对照后根据信息扩到原300/另seed。
- **读数：** gradient group范数、全policy/φ参数hash、每iteration原mean_ep_reward/损失、held100与3worldseed原native utility；原η每actor own200检索与原cohort-prefix口径分别报告。角色ID检索不是独立trait语义；semantic invariance另外卡，不在看到结果后加入此卡primary。短pilot若尚未学会游戏不作方法定论。
- **阳性对照：** Full cons有φ+η梯度、readout_only只有η；NoCons与readout_only初始policy相同、更新后逐byte同一（若差异先查optim/随机数/zero-vsNone，不硬称正）；原one complete episode+原生world state变化。正确pool跨batch已达到数值地板；原public缓存结果全部保留。
- **噪声地板 + MIE：** 参数同一与native replay零差为null floor；firstseed/30iterations只决定下一研究动作。readout_only明显高于NoCons且不低于Full的半数、真实policy控制已形成才值得确认；Full有独特native utility增益则不能讲全是读出。反结果一样保留，不筛seed。
- **混杂审计：** hook只在consistency_loss中临时detach返回值，不影响PPO/div/actor rollout；body/role文本/physical/preferred reward固定。正确编码改变历史训练分布，因此这是新基线非旧weights一键修复；public E17–E24单列。source不同训练entry的随机性/历史reward阅读债不偷换为完全复现。alias语义质量与preference-codedreward限制仍需独立审计。
- **决策表（跑之前写）：** 梯度/byte控制通过且检索可恢复→以独立utility/语义控制继续而非炫耀proxy；Full有实质更好控制→解释φ路径真实作用；短训练没有positive role signal→仅记录cost，不能否定idea；byte不一→修控制不立claim；ordinary readout工程已充分解释→承认已有范围，新科学增量仍0。
- **算力预算：** 完整iteration cost gate后单route≤1小时/最多3GPU（本项目白天≤8）；现有fgvd+deps，0API。原始checkpoint/rollout/cache不进git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

三路完整iteration资格通过，各25600原生transitions，首rollout三路逐byte同一。Full cons对φ/η梯度非零；readout_only对φ/actor/critic零、η非零。NoCons与readout_only一次更新后整个policy逐byte同一，所有原生world/reward未改。成本分别68.58/71.36/69.95秒（NoCons/readout/Full），据预先预算门槛从相同seed42初始化启动三路30iterations，各约35分钟。不是300iteration原结果复现，0API，三GPU≤白天上限8。[完整gate](../results/E25_cost_gradient_gate.json)。

30iterations结束：每路768000原生transitions；Full/NoCons/readout壁时2025.13/2071.29/2096.52秒（合计约1.72GPUh）。NoCons与readout整个policy hash仍同一；原生held100×3世界seed return84.9048逐byte共享，η own200 top1由1%到5%，Full为8.667%且return83.1236。Full−NoCons差−1.7812、persona簇95%[−4.0146,.5271]，不能讲已证明更坏或更好。source homogeneous16/joint-prefix200口径分别1%/2%/4%，与own200不合并。

[完整evaluation](../results/E25_corrected_gradient_route_evaluation.json)，raw cache/runs/e25_30_*。读出共训练可改变proxy而policy不变的控制通过，但PCSP等已有读出/策略区别，未形成新科学增量。额外CPU完整iteration成本28.97秒（GPU约70秒），仅成本资格、CPU/GPU随机抽样不同，未把它当同seed数值复现；后续小MLP训练优先CPU。C01保持L1。
