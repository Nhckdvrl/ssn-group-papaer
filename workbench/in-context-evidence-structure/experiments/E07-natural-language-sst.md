# E07：自然语言底座（SST-5 两极句子）（2026-10-05）

- **状态：** DONE（Qwen3-8B pilot）
- **对应：** C03（外部效度）；与 Kossen'24 的调和
- **数据：** SetFit/sst5 train，只取人工细粒度标注两极（0 very negative / 4 very positive），6–25 词（负 747 / 正 916 句）。标签为 nonce 词，规则 = 极性→标签（每 base 随机）；B = 映射反转。200 base × 27 模式（同 E05）。oracle：一个二值属性 = 金标极性。未做 LLM 审计（step-5 配额用尽），以两极人工标注作为质量保障。

## 结果
allA lo_B −10.87，acc 0.99；末位−首位 +2.30 [1.80,2.83]（存在固定位置核）。
- suffix4−disp4：+0.21 [−0.15,0.59]（meta +4.02）
- noise2→suffix3：**+2.13** [1.83,2.44]（meta −1.70）；noise4→suffix3：**+4.27**（meta −1.91）
- block_start4 +6.48 ≈ block_mid4 +6.73 ≈ block_late4_return2 +6.88（过时块不被折扣）
- r(cond means)：set 0.990，meta 0.755
**判读：** 自然语言映射任务同样在潜在规则层面时间盲。Kossen'24 的 recency 可由固定位置核（本处单点翻转的末位优势）解释，不涉及结构推断。
