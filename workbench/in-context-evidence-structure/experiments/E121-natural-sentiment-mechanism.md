# E121：标注明确的真实情绪文本中的同一形成机制

- **状态：** DONE-CONFIRMATION（2026-10-12，四模型16→32新材料全部完成）。
- **类型：** 独立材料/机制泛化，非应用修复benchmark扫分。
- **对应：** C21/C22/C23、I04、P17。
- **问题：** 已验证的形成子图能否预测真实情绪文本的原生namespace作用，并传递固定输出词的关联内容？
- **为什么现在做：** E116 MHS现实文本single私有规则能力低，证明局部margin作用但不能展示功能有阳性基础的自然文本机制。SST5两极有公开情绪gold；私人yes/no每context正反平衡，避免只激活固定预训练positive输出。
- **材料：** 固定已有SetFit/sst5 Arrow缓存e51bdcd8cd3a30da231967c1a249ba59361279a3，原train/validation/test分别hash记录。仅原label0/4（very negative/very positive），保留原文本；CPU按5–64 comment tokens、长度/边界signature构造B两组2pos+2neg，cross/within移动同样8位置且B输出/名字/位置/multiset固定。A8条与B8条不重合，query8条与demo不重合。筛选完全不看模型输出。
- **独立材料划分：** 原train按文本SHA256奇偶分为discovery/confirmation demo池；discovery query来自官方validation，confirmation query来自官方test。跨两个批次demo与query字节无交集，若源数据本有重复先按全字节去重并报告。context之间允许共享text，不把query当独立bootstrap样本。新私人映射/B配对非预训练可记忆的标准gold答案。
- **科学引擎：** 完全沿用E115/E114 43条件：A/B formation×reading crossing、历史B答案K/KV/V到A label、fixed-label cross/within、native/gated、single/instruction；只替换生成材料，保持FP32/eager/系数1/全层、不训权重。真正raw relation与namespace反事实都测，不能用高r代替private任务阳性。
- **配置：** Qwen3-8B、Mistral-7B-v0.3、Llama-3.1-8B、Qwen3-14B各16 seed121001 discovery→32 seed121101 confirmation，所有正负确认。每context43×8=344评分；官方模型revision/环境沿用E115/E119。
- **读数：** 原D signed/abs、A/B缓存条件作用与signed交互、全部raw/rule K/KV/V系数1r/RMSE/zero、固定label关系cross−within signed/abs、每私人方向single/candidate与full-vocabulary argmax、instruction，全部保存。不宣称真实人类标注者规则或下游修复。
- **阳性对照：** single两私人方向在真实gold上的能力、instruction；full/split≤.001/self0、layer0相同词KV0、pristine cache、全部层消费；CPU每world的B配对真值/不变token几何/原始split身份和交集。
- **噪声地板 + MIE：** 原FP32/eager numerical floor；context-bootstrap10000/seed910，reconstruction沿E109；自然文本更难允许效应较小，不看结果后提高n/改metric。single弱时只支持局部causal margin，保留弱能力与所有正负，不换“更好”的样本救故事。
- **混杂审计：** 极性gold是已有语义、私人code为新约定，两者分开；极端类与长度匹配是跑前范围，不推广所有SST5；SST可能预训练见过，不能称无语义污染。按模型tokenizer分别形成配对几何，源池/采样规则相同，不把不同model结果当相同token序列实验。三家族＋更大同族不是四架构，方差单位context。无新训练，不需等训练算力方法对照。
- **论文定位：** 作为形成解释的自然语义测试，与Cho/CTA/AddUp的任务多样性对齐；已有情绪分类分析不重新命名，具体测Source关联的历史形成与原生使用。官方数据入口https://huggingface.co/datasets/SetFit/sst5，原任务来源Socher et al. EMNLP2013。
- **算力预算：** 已缓存权重与Arrow，不重复下载；独立单卡parallel，预计每批.1–.4 GPU时，总≤4 GPU时。GPU空卡由nvidia-smi实测，conda verl-clean优先。
- **决策表（跑之前写）：**

| 结果 | 科学判断与后续 |
|---|---|
| private single有效，冻结形成预测和关系作用在自然文本保持 | 原生形成/关联解释覆盖真实语义且有能力阳性，不以新benchmark数替代机制 |
| namespace保持、固定label关系内容弱 | 命名形成解释较稳，内容有任务边界；保留新任务阴性，不将高r外推所有关联 |
| target非零而冻结路径明显失准 | 同一形成路径在自然文本不足，报告无拟合真实残差，返回主计算问题，不扫head |
| single私有任务仍弱 | 自然材料只支持局部margin，不冒称可靠部署；不继续调格式或筛熟悉文本 |
| token几何/数据可行性失败 | 仅修CPU工具并记录0-score失败；在新评分前注明必要配置变化 |

## 结果（运行后追加）
| 模型，确认n32 | single正约定（n16） | single反约定（n16） | native形成幅度nats | KV label rule r / RMSE / zero | 固定词关联KV abs超额nats |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3-8B | 98.4% [96.1, 100.0] | 88.3% [80.5, 95.3] | 2.151 [1.487, 2.895] | 0.931 / 1.363 / 3.658 | 0.493 [0.280, 0.764] |
| Mistral-7B-v0.3 | 99.2% [97.7, 100.0] | 96.9% [93.0, 100.0] | 1.091 [0.925, 1.258] | 0.948 / 0.336 / 1.048 | 0.128 [0.056, 0.213] |
| Llama-3.1-8B | 97.7% [95.3, 100.0] | 99.2% [97.7, 100.0] | 0.689 [0.488, 0.901] | 0.930 / 0.309 / 0.840 | 0.183 [0.135, 0.239] |
| Qwen3-14B | 99.2% [97.7, 100.0] | 93.8% [87.5, 99.2] | 1.678 [1.340, 2.052] | 0.966 / 0.519 / 1.949 | 0.211 [0.120, 0.311] |

**实际认识：** 所有家族两私人方向都具有明确single能力；同一冻结历史形成预测在独立真实test评论保持，固定word的关联内容也有绝对超额，补上自然材料功能链。不是只有标准positive/negative先验。Llama KV有符号关联超额为−.109[−.194,−.024]，不能把四模型abs阳性描述为同方向修复。Qwen反向能力88.3%低于正向98.4%，分别报告。

**完整性：** 8批192context、66048评分；43条件和各私人方向均保留。新train SHA奇偶demo池、official validation/test query；真实数据字节独立来源审核见[独立校对](../results/e121/independent_review_2026-10-12.md)。原始评分`results/e121/*_{discovery,confirmation}/behavior.jsonl`，analysis/run/完整性与[自然文本图](../results/figs/fig_natural_text_formation.png)可复核。

### 实现冻结（首评分前）

- `scripts/e121_natural_sentiment_mechanism.py` SHA256 `5f96952a6cae82d97406f1726c4e06e1edad28a4d81bd1b91cad26404705b93c`。
- `scripts/e121_sst_materials.py` SHA256 `f02104a87b9e67dec413c9c642c107a0f90a7d1046421306e8c4202c59da94ec`。
- Qwen/Llama discovery CPU几何已通过；Qwen43个可行length-bin、demo positive/negative639/511，validation query165/137；选择仅gold/长度，原Arrow hashes见preflight。远端14B首次命令未切cwd导致脚本路径不存在，0评分，已用显式cwd修正。
