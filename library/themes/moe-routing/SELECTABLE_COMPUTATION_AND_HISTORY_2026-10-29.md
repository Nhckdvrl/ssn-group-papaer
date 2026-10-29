# 选择部署、合作与历史重用：本轮全文定位

本轮新增完整阅读8篇197页，含附录/参考；另读OLMoE正式全文Appendix L两页，不声称读完61页。PDF版本、SHA、逐页覆盖及403边界见[阅读凭证](../../../workbench/mechanism-population-dynamics/moe/notes/PRIMARY_READING_ARGUMENT_2026-10-29.json)。未执行作者代码；DeepSeek v1在E166冻结运行时补读完整33页。

## HOPE：Higher-order pruning of experts（2026-09-29，v3，32页）

1. **形态：** 理论驱动的裁剪方法与真实生成/agentic评测。[全文](https://arxiv.org/pdf/2609.18916v3)。
2. **压力：** 独立expert分数遗漏联合删除的代价。
3. **前提变化：** 用gate加权norm的共现乘积矩阵做二次选择。
4. **DOCUMENTED来源：** REAP、集成选择、co-selection结构。
5. **距离：** 一个模型内保留合作，未交叉训练来源或固定函数后改变伙伴。
6. **实证：** 3架构至122B、2校准集、生成/代码任务及匹配SFT；完整表有反向条件，不能称只有相关性。
7. **界限：** 理论为单层替换误差的上界；实际矩阵用条件平均，跨层近似也有真实失败。不能照搬其selected-softmax假设到本研究原生full分母。
8. **可借动作：** 选择部署可受益于合作，不应讲成二者矛盾。
9. **增量/ownership：** 一般“合作重要、交互改进裁剪”已有强owner；C14识别的是历史改变的性质载体、未改函数作用与运行通路。

## CD-MoE：Condense, Don't Just Prune（17页arXiv v3）

1. **形态：** 部分MoE层转dense的压缩方法。[实际阅读版本](https://arxiv.org/pdf/2412.00069v3)。TMLR正式PDF403，未断言两版一致。
2. **压力：** 全层删除损失大、原生路由仍需大量权重。
3. **前提变化：** 贪心选层/函数，保留shared与少量routed，使用校准平均门值。
4. **DOCUMENTED来源：** Layer/Block Drop、expert pruning与merge。
5. **距离：** 选定部分层凝缩，其余保持原生；不是删除整网R，亦非跨历史函数身份。
6. **实证：** DeepSeek/Qwen真实任务、时延/内存、少量SFT恢复；shared-only与SR有明确对比。
7. **界限：** 更好保留S不等于S独立承载任务；作者解释的知识份额并未由这些对照唯一识别。
8. **可借动作：** 保留共同计算能支持压缩；完整质量、恢复训练和原生必要性分开。
9. **增量/ownership：** shared对部署有价值非新；C14在S函数不变时改变其预测作用，并与性质来源、实际消息重用相连。

## SD-MoE（ICML2026正式全文，18页）

1. **形态：** 谱诊断、架构/梯度分解与100B训练。[正式全文](https://proceedings.mlr.press/v306/huang26i.html)。
2. **压力：** 参数/梯度主子空间高度相似，路由沿共同方向。
3. **前提变化：** 共享低秩矩阵与正交补、分开梯度更新。
4. **DOCUMENTED来源：** 表示塌缩、谱条件和正交优化。
5. **距离：** 矩阵级common分量参与非线性expert；不等于输出可加的S消息。
6. **实证：** 两架构/尺度的真实训练、任务/生成、梯度分解消融与吞吐，非只有几何。
7. **界限：** 子空间相似、打乱敏感性与训练收益不直接识别跨历史原生职责；局部Gram阴性也不反驳其方法。
8. **可借动作：** 区分共享参数方向、实际函数输出与预测使用。
9. **增量/ownership：** 一般共享谱结构/训练分解已有owner；C14聚焦固定成熟架构下的来源及使用关系。

## Autonomy-of-Experts（ICML2025，15页）

1. **形态：** 由内部激活norm自选择的MoE架构与训练。[正式全文](https://proceedings.mlr.press/v267/lv25b.html)。
2. **压力：** 独立router与expert计算之间的协作和效率。
3. **前提变化：** 用内部低秩响应生成选择分数，代替独立router。
4. **DOCUMENTED来源：** expert-choice、自选择和低秩计算。
5. **距离：** autonomy指自选择，不是跨背景独立重用；不能用名称当作与C14矛盾的主张。
6. **实证：** 732M/4B、100B训练和真实任务；原生Mixtral/Phi3.5的norm改路由效果依层变化。
7. **界限：** 两expert高斯toy的分化解释不等于完整成熟模型训练规律。
8. **可借动作：** norm既可能参与选择，也可能是参数包迁移的简单候选通路。
9. **增量/ownership：** norm选择和一般router–expert耦合已有owner；本研究固定实际路由再比较性质和伙伴作用。

## Unveiling Super Experts（ICLR2026，32页）

1. **形态：** super-expert测量、删除干预和裁剪方法。[正式全文](https://proceedings.iclr.cc/paper_files/paper/2026/file/c01b90b643d0e877cff0f34cbe27410f-Paper-Conference.pdf)。
2. **压力：** 极少expert具有极不均衡的实际预测作用。
3. **前提变化：** 识别早层极端输出专家，并追踪massive activation/attention sink。
4. **DOCUMENTED来源：** massive activation、attention sink和super weights。
5. **距离：** expert身份及早层放大与本研究历史来源/同函数伙伴作用不同；DeepSeek的shared super experts也已有报告。
6. **实证：** 多模型数学/代码/推理，随机和同层控制，MA/attention衰减；不是只有相关性。
7. **界限：** 附录K是Qwen base/instruct/不同发布版本，不是OLMoE完整预训练轨迹；身份稳定不自动证明函数或职责不变。
8. **可借动作：** 先区分全局条件信号和任务特异计算，避免把高删除损伤直接叫语义知识。
9. **增量/ownership：** super expert、shared大作用和早层条件信号不是我们的新发现；历史—来源—使用分离仍需干预识别。

## Massive Activations（COLM2024，32页v2）

1. **形态：** LM/ViT激活干预与结构解释。[全文](https://arxiv.org/pdf/2402.17762v2)。
2. **压力：** 少数维度出现远大于普通响应的激活。
3. **前提变化：** 零化、固定均值及显式KV bias/register干预。
4. **DOCUMENTED来源：** outliers、attention sinks和registers。
5. **距离：** 解释全局偏置/条件信号，不检验训练来源带走何种预算性质。
6. **实证：** 均值替换可保留预测，GPT2显式KV bias训练和ViT register有真实任务对照。
7. **界限：** 不仅第一token：模型中还可位于句点/换行或弱语义词；prefix删除不能代表所有conditioning。
8. **可借动作：** 简单幅度/均值竞争解释有建设性，不能先假定复杂语义合作。
9. **增量/ownership：** 全局偏置和均值恢复已有owner；C14不能把任意范数现象重新命名机制。

## A Single Layer to Explain Them All（ICML2026，18页）

1. **形态：** ME Layer分析和WeMask干预。[正式全文](https://proceedings.mlr.press/v306/shi26y.html)。
2. **压力：** 特定早层的RMSNorm/FFN放大和方向刚性。
3. **前提变化：** 对首token attention输入的大RMSNorm维度施加mask。
4. **DOCUMENTED来源：** massive activation和早层注意力动力学。
5. **距离：** 调节全局计算背景，不区分来源性质与未改伙伴的角色；我们也不认领首个幅度机制。
6. **实证：** SFT/RL/teacher-forcing任务及替代mask控制，并非只测激活。
7. **界限：** 层/比例/任务协议有范围，不能概括成任意模型任意mask都改善。
8. **可借动作：** 检验小容量尺度干预是否足以复制复杂表型，先于追加位置扫描。
9. **增量/ownership：** conditioning干预的真实收益已有owner；本研究选择跨两个成熟谱系的同一预锁增益解释。

## 尺度选择与下一实验

DeepSeekMoE v1的补读（[全文](https://arxiv.org/pdf/2401.06066v1)，33页）明确了另一重要owner。其idea是细粒度expert组合+shared隔离，目标为降低知识混杂/冗余；源于稀疏路由及DeepSpeed-MoE共享架构。2B/100B受控训练、16B/2T、SFT和145B初步训练均有真实任务证据。§4.5不是只描述：移除shared并增加一个routed后Pile loss1.808→2.414；逐token排除最高概率expert更敏感；减少active k及另训half-active模型也有实测。它支持共享作用与参数使用效率，未识别跨历史性质载体、同函数作用变化或实际消息背景。其per-token最高概率删除与我们的cal定义任务池是不同干预，不能把两条敏感性趋势直接叫矛盾。可借鉴的是同时报告完整质量、受限执行和真实替代；“shared不可替代”“低激活参数仍有效”不是我们新点。增量保持在学习历史选择的来源—使用关系，而不从删除损失推知识百分比。全文图13/14及附录训练曲线33已视觉核对；原文本图字形含伪formfeed，阅读按PDF实际页逐页提取，没有把95个控制字符分段冒充95页。

三篇共同提示的主线是：**选择部署可以由合作支持，但选择成功没有唯一指定可迁移的性质载体或可重用的实际计算。** 当前证据连接成熟历史→参数来源→实际路由→消息使用；不改写成一般“专家有交互”，也不将三种关系定义成一条互斥坐标轴。

E164在低预算下测性质，在完整计算下测S作用；它支持共存与通路区分，未证明低预算优势由shared补偿造成。论文据此保留有雄心的关系识别，不补造因果连接。

跨成熟谱系E165已完成：OLMoE明确5.033T父状态→100B普通退火，无常驻shared。整机预算损伤变差而专家单独移入P改善，D来源干预抵消改善；这是真实来源—使用分离，P16准确率约22%的边界必须保留。Qwen3单端点不能回答历史；0125仅同第一阶段data mix，不追认为共同父权重。均不是关线判断。

新增四篇全文后，优先E166统一增益竞争解释，而不立即做prefix/body定位。每谱系只在既定cal的native P完整轨迹闭式估计16个R增益，固定实际路由比较性质及伙伴作用；不拟合预测损失、不搜索gain。它可以把复杂迁移故事简化为尺度变化，也可能显示其余函数结构不可省；S-zero扩到P32直接区分“共存”与“参与实现”。新条件尚未运行。

**Compression risk：** 若只讲“裁剪会破坏合作”，会被HOPE压缩；只讲“shared很重要”，会被CD-MoE/Basic-Refinement压缩；只讲几何相似不等于计算相同，会落回stitching一般结论。我们的证据组合定位在训练历史选择的分担实现、参数性质来源、同函数角色改变与实际通路，而非否定邻近工作的正面结果。
