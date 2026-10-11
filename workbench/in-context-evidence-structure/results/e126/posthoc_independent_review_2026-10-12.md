# E126 POST-HOC selected-code 独立校对（2026-10-12）

**6/6完整复算一致。** 从实际argmax/独立私人gold与冻结word IDs先派生，再读作者posthoc文件；9216查询判定、600数值项最大误差0，24报告行/360数值呈现一致。无新GPU、未改原primary/科学源；这是一项事后解释观察，不是新primary或独立新实验。

诊断source SHA `6b2a858315af07a4140e543502540e99b5eb7270f0a691feda9436fde1a70ea3`；作者JSON `9870c1c1c74a3b2b992cc73cde116b34c6cf0da770ae49edf8e43329124be997`、MD `6bb4d04db0255b3c0ad8557de8c3aa6fb24409292476dceba9c683f1ca91a522`。原六run/contexts/behavior SHA与已封E126独立seal再次一致。

## 定义与单位

仅origin（相反私人代码）两Actor×八query、全部context/pairs。对每个actual argmax，按固定two-word ID查canonical index0/1；独立gold g_request与g_foreign相反，因此selected other-word必且只归入foreign-rule兼容或request-index兼容之一。own-good、own-bad、other-rule、other-request-index、outside五类互斥穷尽，own-good与原argmax_correct逐query一致。cross相同约定不可区分两规则，未硬拿作该诊断。

作者pair_rates/contrast以所有16请求的比例为单位：不是“所选foreign词里多少正确”。下表给出确认conditional的原始分子/分母作为补充，interval另在JSON以context重采样后的ratio-of-counts提供；没有用不等样本的context比例简单平均。

| family / pair | compatible-other / all-other count | conditional% | requests |
|---|---:|---:|---:|
| qwen3 / 00 | 48 / 48 | 100.00 | 512 |
| qwen3 / 11 | 60 / 62 | 96.77 | 512 |
| qwen3 / 01 | 170 / 181 | 93.92 | 512 |
| qwen3 / 10 | 181 / 186 | 97.31 | 512 |
| mistral / 00 | 169 / 174 | 97.13 | 512 |
| mistral / 11 | 205 / 211 | 97.16 | 512 |
| mistral / 01 | 241 / 248 | 97.18 | 512 |
| mistral / 10 | 236 / 244 | 96.72 | 512 |
| llama / 00 | 189 / 194 | 97.42 | 512 |
| llama / 11 | 185 / 189 | 97.88 | 512 |
| llama / 01 | 210 / 218 | 96.33 | 512 |
| llama / 10 | 214 / 221 | 96.83 | 512 |

foreign-rule兼容比例在确认各pair为93.92–100.00%，与“多数”措辞一致。Qwen00观察48/48一致的经验bootstrap区间退化，并不是全集概率为1的证明；其余具体counts/CIs及所有探索结果保留在JSON。

| 确认family | other全比例差pp | other-rule兼容差pp | request-index兼容差pp | own-bad差pp | outside差pp |
|---|---:|---:|---:|---:|---:|
| qwen3 | -25.10 [-28.81, -21.29] | -23.73 [-27.44, -20.02] | -1.37 [-2.25, -0.59] | 2.54 [0.68, 4.88] | 0.10 [0.00, 0.29] |
| mistral | -10.45 [-13.48, -7.62] | -10.06 [-12.79, -7.42] | -0.39 [-1.07, 0.20] | 0.59 [-0.10, 1.46] | 0.00 [0.00, 0.00] |
| llama | -5.47 [-7.32, -3.71] | -4.88 [-6.64, -3.22] | -0.59 [-1.17, -0.10] | 0.68 [0.10, 1.27] | 0.00 [0.00, 0.00] |

## 实际解释更新

coherent−mixed减少other-rule兼容输出Q−23.73[−27.44,−20.02]、M−10.06[−12.79,−7.42]、L−4.88[−6.64,−3.22]pp；所以“请求code只是用另一词集写出”不是多数错误的合适描述。数据支持wrong-space输出通常携带另一套已示范code兼容的类别，不能据此声称直接观察到了internal called rule。

代价同报：own-bad Q+2.54[.68,4.88]、L+.68[.10,1.27]pp，M+.59[−.10,1.46]pp未定；Qoutside+.10[0,.29]pp，CI包含0。因此不是所有错误类下降。origin-only foreign-rule差不是原both-world primary的中介份额，更不能把23.73pp除以23.49pp当解释百分比。

空间校准/竞争仍可能在已经分别形成的映射间选出另一词集，随之输出该空间中另一private code的top词；这与描述兼容，既有binding/词先验/显著性机制也未排除。本观察提高实际部署错误的可解释性，但不独立识别程序调用、abstract rule composition、ID坐标或原生必要性。原有full/candidate/own函数范围与负项保持。

本项POST-HOC标签、primary不改和机制范围在当前正文§6.5/附录I.5写明；对应数字由本独立raw复算支持。当前文稿snapshot另在[paper-critical审阅](manuscript_claim_audit_2026-10-12.md)封。未编辑scientific script/card/claims/论文、未commit/push；只写独立审计与链接。

[JSON](posthoc_independent_review_2026-10-12.json)保留完整six-run pair/contrast、Actor rates、raw counts、conditional ratio及作者comparison。
