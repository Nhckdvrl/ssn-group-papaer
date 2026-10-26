# E149：原生完整网络的backbone × gate × expert bank来源交叉（2026-10-27）

- **状态：** CPU预检通过，准备完整8格推理；8格模型新读数尚未读取。流程生成器登记，按主题移动。
- **类型 / 对应：** MEASUREMENT / 因果PILOT；C11/C12、P31/P32，复用E148 A/B终点672，不新增训练或seed。
- **问题：** 同父等曝光历史后出现的预测差异，是否伴随必须共同保留的系统级接口；相容单位是gate+bank、整个MoE子系统，还是还跨越dense backbone？
- **为何不是L9局部继续扫：** 单层移植不能区分“单层可换但全MoE不能任意换”与“这些历史下组件整体可组合”。本卡改变完整原生网络的三个系统级参数来源，读全部8格，不依据哪个层效果大选层。
- **立项依据：** E148终点A/B预测KL仍非零，A-repeat全状态/预测字节相同；终点NLL差区间跨0。当前尚无E148完整L9 graft汇总；本卡结构按原生架构预先固定，不根据L9强弱或新8格结果调条件。

## 冻结算子与数据

1. 两个来源均为同一公开OLMoE checkpoint的受控全参数继续学习终点A/B；不是独立初始化、不是两个预训练seed。只用已完成终点672，不挑checkpoint。
2. 三个参数组：**backbone**=embedding、LM head、所有attention及其norm、MLP前norm和所有非MoE参数/registered buffers；**gate**=全部16层router矩阵；**bank**=全部16层64专家完整函数。三组覆盖整个网络，不额外学习对齐/增益/温度。
3. 8个确定性组合(B,G,E)∈{A,B}³。AAA/BBB为两个native角，其余6为新合法网络；每层一个完整Top8 router、64专家、原no-renorm/调用/求和顺序。当前来源沿共同祖先物理槽位，不宣称最佳语义匹配。
4. G/E来自同一来源时，全部MoE子系统保持共源；backbone可来自另一来源。只改gate来源、只改bank来源等格均保留，不把单组效果除以总量当责任比例。
5. 完全复用E148固定64序列/32768位置/20实际文件簇、B8顺序和next-token对齐。旧输入已用于探索；不是新确认集。FP32 master快照的BF16 shader原程序不改；source/hash/software全部核对。

## 读数（模型读数之前固定）

- 每格标签NLL及相对AAA/BBB的成对差；同一AAA参考和同一BBB参考的双向全词表KL，方向逐字段明确。
- 三因素固定来源的成对翻转效应：B/G/E分别在另外两组固定时的NLL差；G×E在固定backbone下、backbone×完整MoE的四格有限差分；三阶有限差分另列。均是该合法拼装操作的损失交互，不是不可加“机制贡献百分比”。
- 对20文件簇成对bootstrap1000次、seed149001，全部格共享draw。一个父状态、一个次序处理；input CI非seed总体，8格不是8个独立训练。
- 必须全报AAA/BBB原始NLL/KL，不能用原生NLL接近声称同函数；不同组来源可能相互抵消，保留交叉项/反例。

## 阳性对照

- tiny两个模型验证8格覆盖及backbone/gate/bank的源参数逐一对应；两native角重装输出逐位匹配，不改变非选来源。
- 真模型AAA/BBB的全部held BF16 logits与E148对应native位模式相同；不能把装配伪影计入相容性。
- 原始两模型在所有拼装结束后完整参数hash/registered buffer检查不变。L9的zero与自组装工具阳性沿E148核对；本卡不重新筛有效层。

## 噪声地板 + MIE

E148同流repeat提供精确全流程地板；本卡native角逐位复现与read-only检查。无任意损失准入阈值，所有尺度与native A/B预测差异并列；未检出交互不宣布严格等价或所有历史可组合。BF16真实前向和FP32概率计算分开记。

## 决策表（跑之前写）

| 观察 | 更新认识 |
|---|---|
| 共源G+E即能保留预测、backbone来源相对影响小 | 本次关系较集中在MoE内部；仍不是天然语义联盟或backbone不重要的一般定理 |
| 共源G+E仍与对方backbone不相容，native角各自正常 | 相容边界跨越MoE与dense读写接口；不能仅把专家组叫完整计算单位，也不证明backbone co-adaptation是形成职责的必要条件 |
| 全部hybrid接近native A/B差异尺度、损失交互弱 | 在本父状态/剂量下历史差异并未创造强系统拼装约束；保留可组合范围，不继续扩大扰动直到出现损伤 |
| 某些hybrid改善标签损失或NLL/KL方向不同 | 报全部方向，区分分布/平均标签收益；不筛坏hybrid制造co-adaptation故事 |
| native角不能重现或权重被修改 | 先修实现；不作为科学阴性 |

## 资源与资产

- 单卡两份FP32 master约55.35GB，shader临时BF16约13.84GB；预计峰值<90GB，已有96GB卡。若真实内存不够，先登记只改变流式加载的统一实现修订，不删格。
- 已有mechpop环境；8×64×512=262144计分token条件（2native控制+6新hybrid），源checkpoint/大raw沿E148耐久归档。预计0.15–0.6 GPU·时，硬包1 GPU·时，独立ledger，峰值探索并发≤8。
- 计划代码`scripts/e149_source_cube.py`、`results/e149/`；raw `~/mechpop_cache/e149_native_source_cube`。当前未运行，不将计划与实测混同。

## 结果

CPU两层已知答案通过：全部8格每个参数来源、两native角BF16逐位一致、源参数未变、三阶有限差分已知答案11。见`results/e149/self_test.json`。最初CPU入口发现复用模块的默认GPU号不一致，统一入口默认值后通过；未触及GPU或held读数，实际GPU运行显式传物理卡号。尚无8格真模型结果，不升级主张。
