# E152：固定子集下的归一化规则反事实（2026-10-27）

- **状态：** PLANNED；新归一化规则的模型读数未读取。
- **对应 / 类型：** C14、P32；区分竞争解释的原生PILOT，不训练新模型。
- **问题：** 预算优势和输入选择价值在保留full-router分母时是否仍然存在？现有裁剪结果有多少依赖于可用池内重新归一化这项计算规则？

## 原因与可识别对象

E150显示成熟B比A有更低的预算损伤，但gate单独不能迁移收益；E151显示一般随机预算鲁棒性和R/shared依赖配置同时变化，且输入选择仍有价值。已有mask操作在softmax前删除logit，既限制支持也放大剩余路由门值；因此不能把它的收益直接解释为功能内容被局部封装。

本卡只改变归一化规则，固定公开A/B终点、输入、5套旧mask、预算与shared分支。它不是为了挽救某个局部系数，也不改E150/E151已有读数。识别的是整个原生网络采用该规则的总预测后果；下游H及实际路由可以随上游幅度变化，**不声称全网络两规则的实际路由轨迹逐位固定**。

## 冻结设置与操作

1. 相同成熟A/B pins和FP32加载→统一BF16程序，E150核心9cd5ba33不改。16层、127 routed选7+末槽1 shared，shared系数1，selected-top7不另重归一化。
2. 同64语言窗口、20文件簇、30,994真实target；主评分只在原suffix target ID索引≥128（22,866位置）。探索性旧输入，非独立确认集。
3. 5个32槽mask直接读取封存E150的native A/B prefix mask和E151的random0/1/2；31 routed+1 shared，全部保留，**不重新选子集**。
4. 对每个mask两种规则：**pool**在可用R logit外置−inf后softmax/top7（旧规则）；**full**在同层输入下先算全部127 R softmax，top7索引使用相同masked-score选择规则，但门值从full softmax gather。shared程序不变。
5. 每模型1个native参考+5mask×2rule=11格，共22条件；按原生专家物理顺序聚合。相同H上两规则选择索引相同；整网允许后续H/路由作为该规则的因果路径改变。

## 主读数（新模型前冻结）

- 对每source/mask/rule的suffix NLL−同native、native→variant KL和reverse KL；并列绝对NLL与相对损伤，不能靠降低完整质量制造鲁棒性。
- 每source/mask的full−pool成对NLL/KL差；各规则下B−A损伤及两者差之差，检验B优势是否依赖pool重归一化。
- 每规则、source的随机3probe平均−prefixA/B选择收益；每draw也全报。原生自身selector比较另列，不挑更好selector。
- 同20个(source,file)簇成对bootstrap1000次、seed152001；三random probe是固定MC条件，非训练seed。CI非训练总体，不声称唯一语义模块。
- 辅助记录每层/序列实际施加R门值之和，确认幅度路径，不把层欧氏量或条件恒等式包装机制。

## 阳性对照

- 常数专家oracle：R logits=log4/log2/0，R函数=2/5/8，shared=10；native=10+8/7，去R0后的pool=10+10/3、full=10+10/7；两规则同选R1、shared不变。
- 两个真实源码的tiny模型，FP32/BF16，all-slot两规则逐位复现native，pool部分mask逐位复现原gate-hook；恢复后参数/buffer不变。
- 真模型training-cal对native/full-slot/pool-mask做逐位校对；held中pool每mask逐token NLL必须匹配封存E150/E151，native同样匹配。完整源参数/buffer只读hash。
- CUDA visibility在import torch前设置并比对物理UUID，不占其他进程的卡。

## 噪声地板 + MIE / 混杂审计

统一实际BF16，身份和旧pool重放给精确地板；F32/BF16尺度单列，不线性扣除。干预含幅度向下游路由传播的总作用，不是固定全轨迹的纯直接幅度效应。源混合、语义内容、依赖配置尚非完全可识别。全部正负结果保留，不按效果改mask/预算/输入或挑layer。

## 决策表（跑之前写）

| 观察 | 更新认识 |
|---|---|
| B预算/prefix优势在full规则仍保留 | 削弱“仅由保留池放大造成”；函数/依赖配置仍有作用，不自动证明语义封装 |
| B优势在full规则减弱、消失或反转 | 重归一化适应是重要竞争解释；旧结果是合法pool行为，不能当规则无关的模块性质 |
| NLL/KL或mask方向不同 | 报全部模式，区分标签收益和预测保持，接受混合解释 |
| pool/身份不能复现 | 修实现、保留失败，不当科学阴性 |

## 资源与结果

预算1 GPU·时，含加载/校准/失败/22条件/I/O；单卡2模型BF16，预计<90GB，探索并发≤8。已有mechpop和全部权重，零新训练/下载。raw `~/mechpop_cache/e152_native_normalizer_counterfactual/`；源码/配置/摘要进Git。先代码/已知答案/计划，再读新模型。

未运行，不升级主张；E150/E151已封存结果不变。
