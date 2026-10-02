# E21：自然隐含意义撤回的parent与原对照复现（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1–D2；新增直接近邻驻留，非新benchmark贡献
- **对应：** C02/P02/P09；S2许可与更新读数仍需测量
- **问题（一句话）：** 原ImplicatureX的recognition、cancellation与联合更新，在本地同模型是否重现；原irrelevant followup与真正cancellation能否产生不同的连续更新，而不只是保持相同argmax？
- **设置：** arXiv2607.25094v2，repo15d1c58d1d3cb8c198c07ae5c1e63531a672b10d；全部271items（scalar46/discourse31/synthetic144/natural50），原5套发布prompt CSV、原system、True/False两顺序。相同无followup四份逐字断言后复用；共3252unique prompts=271×6states×2orders。原protocol与末尾加一句`Reply with only 1 or 2.`两个固定readout；无thinking、无API、FP32/TF32 off/batch8。Qwen2.5-3B/Qwen3-4B是真实parent模型；原14B、Flan、GPT2为扩展，后三不冒称paper endpoint。OLMoE三stage沿现有队列完成再跑，common SFT template。
- **读数：** 原order-averaged P(True)，recognition>0.5、cancel signed delta<0、联合二者、Plus delta>0、Approx argmax维持；同时报告连续delta、cancel-minus-Approx paired delta与假更新比例Approx delta<0（**额外诊断，不冒称原gold FPR**）。所有item保留，未认出implicature者不能筛掉；条件子集仅辅助并显式分母。支持token绝对质量/全词表argmax/两order差记录，不把条件归一的概率当知识透明窗口。按原4类item分别bootstrap2000 seed0；原sign指标保留，|delta|≤.001单列数值边界，不能事后选threshold。
- **阳性对照：** CSV schema/271 IDs/各state一对option order；同baseline prompt字节一致；原repo已剔除some_all_8双否定错误，遵循canonical271项、不用submission旧272项；published prompt与原生成模板审计；同Qwen cached values/source Table6–8可核对时仅报告误差不强求FP32=原BF16。首末项batch1/8概率差<.001；regex不涉及generation。Flan候选1/2已确认各单token，GPT2left-padding显式position_ids。source/harness/input/model SHA全保存。
- **噪声地板 + MIE：** deterministic probability；item不是independent decoding seed。原binary sign对极小变化敏感，连续paired差和.001边界率必须并列。不设paper方向/MIE，不把未显著当不存在。
- **混杂审计：** 原prior问题重写且context/utterance删除，不能独立归因belief prior；模型MCQ与human Likert z-score尺度不同。Approx原parent是随机移植同类cancellation，尚无该control的人类norm，可能非中性/不自然；诊断异常先审语义/角色/长度，不能声称真实false alarm。合成与自然来源分别报告；官方权重revision未给，精确数值parity有限。添加格式指令只作elicitation边界不证明latent知识。
- **决策表（跑之前写）：** A原走势/条件差复现且cancel显著区别Approx→撤回读数具区分力，进一步自然norm与stage；Bcancel/Approx同向且差小→先审原control中性与prompt，不升级能力；C源模型/Table差→逐项prompt/cache/dtype审计，未通过不解释；Donly format改方向/低支持质量→elicitation边界，回到自然证据条件；E四类方向不一致→记录边界，不维护global criterion。
- **算力预算：** 5完整模型预分派8卡：GPU0/1 Q25、GPU2/3 Q3、GPU4/5 Q14按sorted item IDs交错分为2片，GPU6 Flan/GPU7 GPT2全量；分别释放E20后独立跑，每模型6504readouts；OLMoE GPU5/6/7在E20后；预算≤3 GPU·时。FP3214B每卡≤90GB；无跨GPU训练。

## 结果
跑前冻结。新近邻已有cancellation、prior、negation/strengthening/irrelevant控制ownership；本E不以新指标/旧failure作novelty。

### 2026-10-03结果更新
已完成本卡原运行；后续stage输入差异见E27，旧raw保留。派生数字见results/E21-E23-implicaturex-stage-summary.json与results/E22-E26-stage-controls.json。未升级C01/C02；技术/任务描述不当能力finding。
