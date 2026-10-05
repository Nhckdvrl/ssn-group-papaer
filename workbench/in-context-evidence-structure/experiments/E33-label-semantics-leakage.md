# E33：证据泄漏由标签词的语义相似度决定？——14 套标签词的剂量—反应（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT（I04 机制的定量化）
- **对应：** I04；E31（同词→大写→近义→nonce 溢出单调下降）；近邻 Wang et al. 2023（标签词锚点）
- **问题（一句话）：** 两位标注者各用一套标签词时，Sam 的映射翻转泄漏给 Alex 的比例，能否由两套标签词的语义相似度（外部嵌入、模型内部锚点表示）定量预测？
- **设置：** E31 的交互设计（Alex/Sam 各 8 条随机交错，类别均衡；映射 A vs inter），SEED0=880000，200 base/任务。Alex 始终用自然标签。Sam 的词表 14 套（按与 Alex 的语义距离大致排序，最终排序以测得的相似度为准）：
  - SST（negative, positive）：same、CASE、bad/good、unfavorable/favorable、poor/great、dislike/like、pessimistic/optimistic、no/yes、low/high、cold/warm、0/1、B/A、nonce（审计词库）
  - 数字（small, large）：same、CASE、little/big、tiny/huge、minor/major、few/many、low/high、short/tall、less/more、weak/strong、cold/hot、0/1、B/A、nonce
  - `scripts/build_vocabsep.py`（VOCABSET=graded）→ `data/vocabgrad`。标签词是常用英语词对，按词典义选取；相似度以测量值为准，不依赖人工判断，故不经 step 审计。
- **读数：** 每套词表的溢出比（Alex 移动 / Sam 移动）与绑定。相似度：(a) bge-large-en-v1.5 的词向量余弦（两标签平均）；(b) 模型内部：在中性模板 “Label: w” 中，标签词最后一个 token 的隐状态（中间层与 2/3 层）的余弦，Alex 词与 Sam 对应词平均。
- **预测（I04 + 锚点）：** 溢出比与内部锚点相似度正相关（Spearman ρ>0.6），与外部嵌入相关较弱；nonce 与 B/A、0/1 接近 0。
- **混杂：** Sam 的映射是否被学会（Sam 移动的量级）随词表而变 → 溢出比以 Sam 移动归一化；同时报告 Sam 移动。
- **决策：** 强相关 → 得到“标签词语义 → 证据合并”的定量规律（锚点表示越近，证据越合并）；弱相关 → 合并由别的因素决定（例如标签是否同为情感/大小词），I04 的“输出身份”需重新界定。
- **算力：** 200×2 任务×14×2×4 = 44800 条/模型；Qwen3-8B、Qwen2.5-7B、Llama-2-7B。
