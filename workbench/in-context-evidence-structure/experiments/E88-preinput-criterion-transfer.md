# E88：测试输入前的来源条件状态能否转移判断标准？（2026-10-10）

- **状态：** PLANNED；下述协议与脚本在首次GPU评分前冻结。E87原候选继续未运行。
- **类型：** PILOT。
- **对应：** I04 / C16 / C20 / P13 / P20。
- **问题（一句话）：** 保留recipient示例时，名字相同但从示例推断的标准不同的input前状态，能否使新评论转向donor标准？
- **设置：** Qwen3-8B revision `b968826d9c46dd6066d109eabc6255188de91218`，conda `verl-clean`，float32/eager，单卡。24 contexts、固定seed88001；每context Alice/Bob各4条评论覆盖食物×服务四种极性，标准随机交换，标签positive/negative频率平衡。每条相同评论由两人判断，顺序随机。两套未见措辞测试四种极性×两来源，共16 queries/context。donor保持姓名、文本、顺序、标签词表不变，仅交换两人的标准所产生的demo标签。
- **干预对象：** 先计算demos与query的`Source: name\n`字段；该时刻没有测试评论。将donor的整个query来源字段逐层K/V换入recipient的对应位置；recipient全部demo K/V、原位置/RoPE和后续评论/Label文本保留。没有筛层、head、训练、输入后答案状态。相同capsule用于8个新评论。整体KV交换是一个受限的因果接口，不等于单个天然模块或独立抽象规则。
- **读数：** `z=logit(positive)-logit(negative)`；每context/source/template在四极性上计算bias、food/service系数（`mean(z*f)`/`mean(z*s)`）及交互。主读数`T=mean((z_patch-z_base)*(donor_gold-recipient_gold)/2)`，只在两个相反极性评论上计算；正值表示双向靠近donor标准。另报两个方向、同向评论绝对扰动与bias、recipient/donor二选一准确率、原生标准flip效应与移植/native效应比（分母接近0不解释比值）。报原始全词表argmax是否在两标签中，避免把受限候选得分当完整生成能力。context配对bootstrap95%CI，10,000次固定seed880。
- **阳性对照：** native recipient/donor标准flip；同recipient中Bob来源字段换给Alice（反之亦然），检验接口能转移来源条件作用；单句明确使用requested reviewer的native指令；显式说明两人标准的native与同姓名标准flip移植（诊断接口，不替代隐式推断主实验）。
- **噪声地板 + MIE：** self-copy K/V与缓存/整段query分块对照，最大logit差预定≤.01nats，否则该数值运行作废；完整保留失败。主读数CI与原生效应量级共同判断：T≥.10nats且双方向一致、同向评论无相同比例标签偏移，才考虑新材料确认；这是pilot投资启发，不是科学有无的自动判决。不得通过换层或筛种子追阳性。
- **混杂审计：** 标签频率/四极性/source分配/位置顺序平衡；所有contexts保留；demo/query措辞不重叠；donor/recipient token长度和非标签位置一致由preflight断言。自然情绪语义来自预训练，标准分配由context生成，不称学到全新语义。未控制其它模型/真实评论/所有检索算法。all-layer KV可携带多个计算阶段信息；保留示例意味着criterion-conditioned retrieval仍可解释转移。same-source不保证内部地址不变化，排除的仅是固定姓名地址、重新从recipient对应source demos取得标准的受限解释。显式标准条件仅诊断，不用于宣称默认推断机制相同。
- **决策表（跑之前写）：**
  - native隐式有标准作用且同姓名移植出现双向donor标准作用 → 独立新措辞/seed确认；只支持criterion相关信号，随后再让donor criterion与recipient可检索证据竞争，不宣布完整规则胶囊。
  - native隐式清楚、姓名swap阳性、同姓名移植弱/无 → 该input前KV接口没有相同程度的可迁移criterion；地址/后续重新检索仍可行，不扫位置，不宣称模型没有规则表示。
  - 隐式native弱而一句指令或显式标准有效 → 目前首先限制从demo推断/条件选择；如实回到研究问题，不把不适合识别的状态交换称新机制。
  - 两相反方向不一致或同向偏移同样大 → 更接近输出偏好/其它上下文状态，不能支持criterion转移。
  - 数值对照失败 → VOID，同seed修数值，不删除失败。
- **算力预算：** ≤.3 GPU·时；独立确认只在读完pilot后决定和预注册，最多32新contexts。**实际：** 待填。
- **命令：** `CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e88_criterion_transfer.py --model /tmp/ices_models/Qwen3-8B --out results/e88/qwen3_discovery --n 24 --seed 88001`

## 为什么现在做／与现有解释的关系

E66移除demo读取后single/mixed都失败；本实验保留recipient证据，不重复那个失败接口。E85局部均值预测保留，不扩大成所有Source机制。JIT（Li等v3）与Local Task Vectors（Zheng等ACL2026）已经研究抽象/局部任务状态、可迁移性和位置局部性；输入前交换本身不是新意。这里新增的待测关系是：同姓名在不同demo中获得的标准，怎样与recipient中原有来源证据竞争。第一次转移不能区分可复用criterion与criterion-conditioned retrieval，也不能单凭失败排除分布式/JIT标准表示。

## 结果（首次运行后追加）

待运行。C16/C20不升级；没有开关线或workbench状态变化。

## 2026-10-10：pilot结果后的确认协议（新运行前冻结）

pilot完整24contexts/384queries，源码SHA `522515d8679de5a7947400ba149616993d7d25df7e22aff04eef39e1d8b57b80`；数值误差最大1.14e−5nats，178.33秒=.04953 GPU·时。

主读数同姓名隐式标准T=.00883[−.00798,.02561]nats；姓名交换T=.30106[.14337,.47816]；native标准flipT=.36674[.30070,.43677]。显式标准同接口T=.31405[.25119,.38131]，正/负两个donor方向均为正；显式native flip1.25562[1.12991,1.42052]。

**实际改变判断：** 不进入隐式criterion与recipient证据竞争分支，不扫层/位置。不能说隐式模型已可靠学会：默认discordant accuracy50%[46.9,53.1]；一句指令55.2%[51.6,59.4]；显式63.0%[57.8,68.2]。native logit对标准有响应，与可靠完成标准判断是两回事。接口不是全然无效，但显式/隐式的native作用本来也不等强，绝对迁移差不能自动解释成不同算法。

**POST-HOC发现、随后冻结的确认目标：** 同一来源字段接口，显式给出的criterion比demo推断的criterion有更大迁移作用。确认不是隐式阳性分支，而是有限地检查这项新分离是否随措辞消失。

- 32新contexts，seed188001，stage confirmation；demo和query的各方面/极性短语池与pilot完全不重叠，继续保留全部8个条件、16queries/context。科学引擎不改，不能选好seed。
- 主确认量：`T_explicit_patch − T_implicit_patch`的context配对CI；另报两项T、各方向、姓名swap和native flip以及discordant accuracy。只有差异在新材料仍明确、阳性/数值正常，才保留有界分离。
- 补充量：两项各自相对native flip的**均值比**及配对bootstrap差异，用于诊断原生响应强度的替代解释。native接近0时不据比值判断，不截掉困难context/重采样；该比值不是模块贡献份额。探索集报告为POST-HOC，确认集是冻结读数。
- 如果新材料隐式迁移恢复，或显式/隐式差异消失 → 不保留稳定分离；如果仅native大小不同且相对比值差异不明确 → 更兼容效应强度/识别难度，不称不同信息组织机制；如果同接口分离仍明确 → 保留“标准推断与来源条件状态形成之间的有界区别”，仍不证明纯地址/完整program，不把显式规则任务替代研究中心。
- 额外预算≤.25 GPU·时；本卡总预算≤.55。命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e88_criterion_transfer.py --model /tmp/ices_models/Qwen3-8B --out results/e88/qwen3_confirmation --n 32 --seed 188001 --stage confirmation`。
