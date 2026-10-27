# 论文与作者代码接口核对（2026-10-27）

- **Myth Fig.6：** 同一读出 MoE 上比较不同生成器轨迹最符合图和设定，但论文未明确写出重放实现；不能当成已经直接证明。未见跨独立权重专家匹配的定义（论文 p.8–9；附录 p.15，29）。
- 单条观测为某层两条 rollout 的高频专家集合 Jaccard；原文为 30 题、60 个 reasoning 生成模型、4 seeds；图按 Qwen3、ERNIE、gpt-oss 分面（p.8）。
- 三种比较固定两轴：同题同 seed 改生成模型；同生成模型同 seed 改题；同题同生成模型改 seed。题对与平均权重细节未披露（p.8 §5.1）。
- Eq.13 对每条序列按 token 访问次数统计专家频率；Eq.18 取累计质量 ≥P 的最小高频集合，Eq.19 求交并比；Fig.6 P=.8，Fig.25 附其他 P（p.15、29）。prompt 是否进入该指标未确认。
- **MoE Lens PPL：** 调整所有 MoE 层 top-k 后重新运行完整模型，最终 logits 计算右移 next-token CE，再 exp；不是逐层 LogitLens（`moe_lens_pplx_source.py` 48–53、114–155、163–189）。
- 图 3 的域内曲线是等样本平均 log(PPL) 后对 k 做 min-max，不是原始 PPL 数值（同文件 296–319、346–359；论文 p.4）。长样本按 2048 token 独立块运行，丢失跨块上下文及边界预测。
- 完整模型推理保留 shared experts 和层残差；当前 DeepSeek 官方配置 `norm_topk_prob=false`，故 top-1 至 top-6 均保留全专家 softmax 原权，不对选中专家重归一化。官方模型代码 L245–280、321–369、802 起；配置 L13、22–26、33。
- 本次只核对当前公开模型源码；notebook 没有锁 HF revision，历史运行所用 revision 未确认。
- 局部读出另行从原始前向取各专家输出和门权，截取 top-k 后求和；可加 attention 后残差，但排除 shared，直接 lm_head，不传到后层（`moe_lens_logit_source.py` 303–325、380–439）。截取权重无二次归一化；整数 ID 特殊分支赋权 1.0。
- 论文 p.3 Eq.3–4 写 LayerNorm；局部组合函数直接 lm_head，另一个 helper 仅对 2D 输入做无学习权 RMS 归一化；各代码路径不能一概等同论文公式（同文件 26–36、438–439）。
- 可借鉴：分别报告 shared、残差、门权及后续传播条件；区分序列路由频率与功能损伤。详细出处与未确认项见 `report.json`。
