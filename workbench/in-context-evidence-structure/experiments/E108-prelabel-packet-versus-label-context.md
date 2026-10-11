# E108：规则混合在完整标签前编码中形成，还是在标签合并时形成？（2026-10-11）

- **状态：** DONE-CONFIRMATION
- **类型：** PILOT / 计算阶段的路径交换
- **对应：** I04、P17、C16/C20（不自动升级）。
- **问题（一句话）：** 其它Source的输出namespace改变A自身证据，是通过已经包含Source身份的完整pre-label编码，还是在A label状态形成时直接发生？
- **设置：** Qwen3-8B revision b968826d9c46dd6066d109eabc6255188de91218；FP32/eager；E91/E106 MHS评论池、受控私人规则；16新contexts seed108001，A/B各8demo，每context 8未见query。B aligned/conflict × shared safe/toxic vs far pass/flag全交叉；A文本、标签、来源不变。全部query位置禁读B。完整pre-label packet从每条A的Comment字段起，含评论、Annotator/来源名字、Label冒号，止于答案词之前；排除A答案词与尾部换行。未训练、不扫描层/头/词/强度。
- **读数：** 各context的B-rule signed margin差和绝对幅度，成对报告far packet经A label中介的减弱、mirror阻断、评论内容中介及直接far-label KV作用。主统计单位context；10,000 bootstrap。准确率与自由argmax另报；不把正/负context筛开。16×2×11×8＝2816评分。
- **阳性对照：** 完整far A-cache复制到shared必须精确重建far gate；far-label KV作为同下游接口阳性；packet self-trajectory重算全cache精确相同。评论中介同时复测，保证阶段比较同材料。
- **噪声地板 + MIE：** FP32分段/整段margin max≤.001；self交换0，原cache指纹保持。以packet相对完整label接口的功能差异与mirror共同更新解释，不按任意阈值自动判科学价值。方向清楚时同源脚本32新contexts seed108101确认；其它情况先回读机制预测，不扫packet内部。
- **混杂审计：** stage轨迹在全部36层替换，实际消费逐层计数；仅重新形成的A label K/V送给pristine shared query缓存，其余A输入/字段缓存不复制。因此query不能直接读移植packet。B在prefill中仍可被A标签直接访问，这正是竞争路径。packet包括Source和forerunner，但不证明其表示为抽象规则；多层构造性组合可能离开原生分布，mirror/self/同接口阳性有限约束。MHS是输入材料，私人规则是实验规则，不冒充真人标注。
- **决策表（跑之前写）：**

| 结果 | 对主问题的更新 |
|---|---|
| packet中介强，mirror阻断强，而评论中介弱 | 身份/forerunner参与的联合输入编码承担历史规则依赖；不能叫label-only pooling。冻结确认后解释此联合关系如何进入读取 |
| packet与评论中介都弱，但直接label KV强 | 历史影响主要绕过完整pre-label编码进入label形成；下一实验检验label形成时的跨示例消息，而非继续逐字段寻找输入latent |
| packet作用与mirror不一致 | 接受轨迹接口的有界结果，不报中介份额；对照CTA的边干预重新设计 |
| label接口/历史效应不稳或数值失败 | 保留全部结果，不归因计算阶段；只修执行或重新审视已有预测 |

- **算力预算：** discovery＋可能的独立确认≤1 GPU·时；独立单卡。**实际：** 待记录。

## 文献逼出的设计

Cho2025 §3.1/§4.1的forerunner编码在当前label前已经含上下文，E106的评论内容不是完整的该阶段。CTA2025 §3.2要求用下游功能反事实检验传递的信息。How Few-Shot Examples Add Up2026 §5/E.3区分QK routing与V更新，但干预集中于最终FV读取；它并未给出本实验的source-private历史形成预测。这里新增的是多来源共同输出下、原始A证据固定时的阶段竞争，宽泛input编码/label anchor/上下文化所有权归原文献。

## 结果（运行后追加）

待运行。原始JSONL/context本地，analysis/run/preflight/audit入git。

### Discovery完成与确认冻结

16新context全部2816评分：shared gate B-rule幅度.798[.536,1.071]；far label .238[.135,.360]，减弱.560[.287,.831]。评论中介减弱.0019[−.0313,.0390]；完整packet中介减弱−.177[−.408,.057]，mirror−.0264[−.1119,.0645]。完整packet并未补出预期的恢复路径。它不能被写成“Source位置没作用”，但完整pre-label路径目前不足以解释标签namespace效应。

36层干预各130次、self cache精确、原cache指纹不变，max数值差7.63e−6；.0458 GPU·时。源SHA 8e8c6c3c0397b3f5c5f92d9db4e3da0ca83524738a2a1c5346199d6a5bd90099冻结，32未选择新contexts seed108101同配置确认。无token/head/alpha扩展。

### 独立确认完成

32新contexts/5632评分全保留，shared gate幅度.659[.472,.852]，far label .200[.130,.288]，减弱.459[.287,.639]nats。完整packet中介减弱.0404[−.1262,.1989]，mirror−.0246[−.1126,.0439]；评论中介.0115[−.0088,.0332]。两次独立运行没有出现方向一致的pre-label恢复/阻断，强label接口保持。max数值1.91e−6；.0876 GPU·时，合计.1334。

按决策表：转向label形成时接收的历史消息，而非继续分Source字段；E109已冻结并运行。不能从这个构造性交换宣称所有pre-label信息没有因果作用，也不把packet效果估成精确可加份额。C16/C20 L1不改。
