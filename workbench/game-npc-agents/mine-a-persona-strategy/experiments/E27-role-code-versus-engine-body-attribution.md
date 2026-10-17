# E27：文本角色输入与引擎身体的行为归因（2026-10-14）

- **状态：** DONE
- **类型：** measurement / 竞争解释控制；不是看到reward硬编码就创新。
- **对应：** P06 / I02 / C01；E17–E26。
- **问题（一句话）：** 作者独立行为probe认出的特质，有多少跟随文本code，有多少在code固定时仍由原身体/需求动态维持？
- **设置：** 原PCSP v3-large、public Full/NoCons42/43/44全六政策、原test100/3worldseed27011/12/13/16NPC/200cycles，原cached code按角色ID固定（不再受batch变化）；own、constant（所有NPC用原train ID1的合法code）、within_body（五原test archetype内角色循环换code）、cross_body（同职业槽位跨五archetype循环换code）。不改原body/BigFive/需求衰减/reward/物理/目标。within_body要先确认decay/preferred/BF逐项同一，不能只看文字相似。code变化同时覆盖16伙伴，人口动态限制单列。
- **读数：** 冻结作者extract_features/fit_ridge_probe，复用E17原320角色×2训练/80×2校准轨迹，两个mode与三policy seed混合拟合一次；action-only445维与含state749维分别报告。仅原train/cal选正则温度，不能在干预test上fit。原body BigFive的各axis balanced accuracy、代码donor与body不同时跟随body/code/第三类比例、native return与needs，held persona簇paired CI。constant不是neutral persona，分清counterfactual归因与正常质量。
- **阳性对照：** 六policy strict-load、原own完整episode byte replay；native body/初态/原观测合法；within_body numeric config逐项同一；冻结probe在own条件能读到至少一些轴才解释drop，不能自动给全部轴统一chance .33（test支持类数不同）。外部probe不读φ/η/logits。
- **噪声地板 + MIE：** own重复zero、三seed全部保留。固定code后body特质读出显著保持/某轴变化≥10pp且超过persona簇CI才进一步拆身体 vs主动策略；仅domain-shift导致probe失败不讲角色变无效。措辞、实际policy控制与作者reward效度仍分开。
- **混杂审计：** code/body不一致是明确因果干预，不称新的正常人物、不用其结果给NPC贴人格失败；changing all peers含social反馈。code固定会移出组合训练分布，不能把utility下降叫纯persona效应；独立probe预测不等于内部信念或人类trait有效性。作者已有raw-state+action控制但已读路径未见此code/body对换，仍需全repo/最近邻持续审计。
- **决策表（跑之前写）：** 固定code仍识别body→分解环境通道再谈形成；行为跟随donor→支持语言code有真实控制能力；三轴无阳性→仅记录probe域移，改更直接state-conditioned控制；between/within差异超地板→再定位semantic/机械角色粒度，不把普通因果归因本身称好idea。
- **算力预算：** 单CPU≤30分钟、0GPU/API，复用fgvd+deps/原cache。全部raw不进Git；不重定义人物正确行动。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
六公开policy全部完成，单CPU211.57秒、0GPU/API。action-only mean-axis BA：own .431667–.539444，constant .333704–.343519，within-body .444444–.541111，cross-body约.308–.343。原身体配置/初态不动，固定code显著改变可读行为，**支持真实角色输入有控制作用，不支持一概persona无效**。含state的constant总体约.412–.431，C轴仍.832–.917；它同时包含原环境生理信息，不能归功文本角色控制。

[逐轴/CI/收益](../results/E27_code_body_attribution.json)，raw cache/runs/e27_code_body；probe只用E17原train/cal，未在干预held上fit。macro BA的支持类数随轴不同，不套万能1/3 chance；预测标签不是唯一正确选择/心理人格gold。原作者已有action+state区别，这个归因控制也不自动变成新idea。C01仍L1。
