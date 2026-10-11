# E115：Llama上的冻结形成解释与原生计算（2026-10-11）

- **状态：** PLANNED（跑前）
- **类型：** REPRO / C21–C23的家族迁移检验。
- **对应：** C21/C22/C23、I04、P17。
- **问题（一句话）：** 已有形成→新输入判断的因果解释能否在Llama原样成立，还是Qwen/Mistral的特定实现？
- **设置：** Llama-3.1-8B base，NousResearch/Meta-Llama-3.1-8B revision 1f47e50cdbe801ad8a5174156ec3a0655108fb9f；四个safetensors的LFS SHA/大小与Meta官方revision d04e592bb4f6aa9cfee91e2e20afa771667e1d4b完全一致，下载后逐文件本地hash核对。不是蒸馏/量化版。conda verl-clean，FP32/eager，全层、全部43条件沿用E114；脚本仅增加modeling_llama路由、Llama revision记录与默认路径/描述，其余科学引擎与分析完全相同。
- **配置：** discovery n16 seed115001旧词句；数值/阳性通过后confirmation n32 seed115101 validation新词句，两个私人方向平衡；5504/11008评分。不给Llama重选层/头/标签/BOS/格式以追正结果。实际分块token流保留，sender区域按真实word+separator长度；query全Source读取，whole-query gated与single/instruction原对照一并保留。
- **读数：** E114原D=mean_q gold*(z_cross−z_origin)，A/B缓存条件作用signed/absolute、signed交互、namespace K/KV/V系数1原生label/full-A重建r/RMSE/zero、固定label跨类−同类关联超额作用。context-bootstrap10000 seed910；原有所有读数同时保存，不由Llama结果再选择主指标。
- **阳性对照：** single A两私人映射；shared/far两个native端点与cache crossing一致；第一context全部8query full/split误差≤.001；self edge≤.001；sender layer0固定label配对不变；source-cache指纹、全32层真实消费；token边界/Source/A原文/label身份控制和确认文本交集0。
- **噪声地板 + MIE：** FP32同形状GEMM原生实现，自复制与actual consumption先过；CI报告不以微小r高宣称全部机制。single A任一私人方向<90%时保留完整结果，关联路径阴性不能归因为Llama缺失该机制；不改变标签/格式救结果。若目标反事实明显而预测不足，判解释存在家族边界。
- **混杂审计：** 沿用E114的8项审计并明确Llama实际token化；F/R是上下文化位置缓存，非两个独立模块；query状态会演化；混合corner诊断，完整00/11阳性另核；一个受控情绪任务，跨家族不等于跨任务；所有失败/通道/条件保留，实际donor预测非无donor算法。模型identity与本地hash先核，不把redistributor名字误当新模型。
- **决策表（跑之前写）：**

| 结果 | 科学更新 |
|---|---|
| 数值和private能力通过 | 不选择是否“足够阳性”，原样n32新词句确认，负结果同样需要确认 |
| formation与association/native均保持 | 扩已直接测到的家族范围，比较效应/残差；不自动锁定论文主线或宣布所有ICL |
| 目标namespace/label作用明确但形成边预测弱 | 已有解释是有界的，确认后报告Llama的计算差异，不在该模型再搜索最佳层 |
| 形成保持但native被补偿/调节不同 | 区分子图迁移与原生使用，保留signed交互与所有背景，不仅比较准确率 |
| single/private阳性弱 | 此接口不足以解释能力或机制阴性，保存全记录；不以模型弱/论文价值低直接关线 |
| 数值/几何失败 | 无科学结论，修实现而非机制；失败目录与版本保存，不挑contexts |

- **算力预算：** 独立单卡≤.4 GPU·时（下载不占GPU）；计划fvcrc21 GPU0，其他独立阅读/资产核对继续。总12卡可用，但此依赖实验不铺配置。实际待run.json记录。
- **命令：** `CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python -u scripts/e115_llama_native_mechanism.py --model /tmp/ices_models/Llama-3.1-8B --out results/e115/llama_discovery --n 16 --seed 115001 --materials discovery`；确认改out为llama_confirmation、n32/seed115101/materials validation。另同设置preflight-only。
- **定位：** 这不是新idea/novelty声称；沿用CTA功能路径与AddUp背景条件比较，检验当前C21–C23解释的直接模型范围。ACL/EMNLP/NAACL全文阅读继续审视自然问题/实验链，不因增加Llama自动敲定论文。

## 结果（运行后追加，跑前字段保留）
待运行。源码SHA256：ff749f370b443385e76dca8b424a13e43e81db5c445f2dc67c3aa3034d3097fe；原E114 SHA为2ae995abf40944e5018814cd42c0e0a28b71dfaf90206ec44e3df9890e703499。

跑前实现校正：补全run的Llama revision字典，防止在保存元数据时KeyError；无GPU科学记录，干预/分析/条件不变。discovery与validation CPU预检已过：全部配对几何一致、A原文不变。
