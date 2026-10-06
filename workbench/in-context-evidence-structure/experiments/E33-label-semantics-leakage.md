# E33：证据泄漏由标签词的语义相似度决定？——14 套标签词的剂量—反应（2026-10-06）

- **状态：** DONE（2026-10-06 整理时更新状态）
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

## 结果（2026-10-06；Qwen3-8B、Qwen2.5-7B、Llama-2-7B、Mistral-7B；Qwen3-14B 运行中）
溢出比（Alex 溢出 / Sam 移动）对两套标签词相似度的 Spearman 相关（数字 n=14 套、SST n=13 套；全部 p<0.005）：
| 模型 | 数字：bge / 锚点（中层） / 锚点（2/3 层） | SST：bge / 锚点（中层） / 锚点（2/3 层） |
|---|---|---|
| Qwen3-8B | +0.94 / +0.82 / +0.78 | +0.90 / +0.96 / +0.95 |
| Qwen2.5-7B | +0.95 / +0.92 / +0.89 | +0.87 / +0.93 / +0.93 |
| Llama-2-7B | +0.85 / +0.81 / +0.78 | +0.75 / +0.75 / +0.80 |
| Mistral-7B | +0.93 / +0.89 / +0.89 | +0.86 / +0.88 / +0.77 |

Qwen2.5-7B 的完整梯度（溢出比）：SST——同词 0.91、unfavorable/favorable 0.69、CASE 0.67、bad/good 0.64、pessimistic/optimistic 0.63、dislike/like 0.54、cold/warm 0.48、poor/great 0.46、low/high 0.36、no/yes 0.26、B/A 0.05、0/1 0.04、nonce 0.00；数字——同词 0.77、CASE 0.29、tiny/huge 0.25、minor/major 0.23、short/tall 0.21、low/high 0.19、few/many 0.15、little/big 0.15、weak/strong 0.14、cold/hot 0.13、less/more 0.12、0/1 0.06、B/A 0.00、nonce 0.00。Sam 移动在各词表间相近（2.5–4.8），溢出比的变化来自 Alex 溢出而不是 Sam 学没学会。
- 结果文件：`results/vocabgrad/summary.csv`、`results/vocabgrad/anchor_*.json`
- **按决策：** 强相关（8/8 格 ρ=0.75–0.96）→ 得到定量规律：**上下文之间的证据泄漏随两套输出标签的语义相似度单调增加**，外部嵌入与模型内部锚点表示都能预测。SST 的情感词比数字的大小词泄漏更多（同等相似度下），说明“同一语义维度”的词更易合并。
- **Qwen3-14B：** 数字 bge +0.90 / 锚点 +0.83 / +0.77；SST +0.92 / +0.86 / +0.87。累计 5 模型 × 2 任务 10/10 格 ρ=0.75–0.96（全部 p≤0.003）。

## 事后补记（2026-10-06，流程字段）
- **阳性对照：** 事后补记：本线统一的阳性对照为标签流条件（E05/E06），同一工具下 13/13 模型测到规范方向效应；此卡跑时未单列。
- **噪声地板：** 事后补记：bf16 batch 噪声 ~0.1 nats/条且无方向，200–300 base 配对平均后 ≈0.007；效应以配对 bootstrap 95% CI 判断。
- **决策表（跑之前写）：** 见上方“决策”条目（跑前写定；此处仅为流程字段名对齐）。
