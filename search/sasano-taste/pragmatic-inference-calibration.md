# Territory：Pragmatic Inference Calibration（2026-10-02）

- **通道：** sasano-taste；用户选定并授权PROPOSED D1/D2。
- **对象：** Across open-weight language models and natural pragmatic phenomena, when do models correctly go beyond literal meaning, when do they over-infer, and to what extent do apparent improvements reflect discrimination versus shifts in inference tendency?
- **原则：** 初始hypothesis/metric/baseline皆为探针，允许失败；目标是值得知道的scientific object。
- **会议：** ACL / EMNLP / NAACL main；没有现成paper claim。

## 热度与谱系

本地65,716篇语料中，`pragmatic|implicature|presupposition`匹配ACL2025 12、EMNLP2025 14、ACL2026 17篇main；词法假阳性存在。ICLR2026切片9/21、基准5358/19813，均不是科学判决。
Hu2023细粒度错误 → Hu/Levy读数 → Multi2024 literal → Wu2024 free-form/PO → Wavelength2025 human distribution → ALTPRAG2026 stages与PaCE2026 suppression；DRInQ/CIS拥有context许可与graded结构的部分claim。[论文卡](../../library/themes/pragmatic-inference/README.md)

## 压力

| 来源 | 最值得辨别的未知 |
|---|---|
| ALTPRAG × PaCE，RECONSTRUCTED | 同设定下discrimination/criterion分别变化？ |
| Hu & Levy | prompted答案、指令恢复与概率之间的差异？ |
| Wavelength | human uncertainty与model uncertainty如何对应？ |
| DRInQ | plausible但过强的解释是否区别于语义错误？ |
| CIS | 表征cosine结构与行为辨别之间还缺什么？ |
| E01/E05实测 | 原生数据能否提供可靠许可标签，而不强行二值化？ |

## 立足点与驻留

Multi原300×4语言；Wavelength100条×40human responses；Hu169×5选项顺序与104×5no-story。8张H20独立单卡、frozen inference、主评测API依赖=0。D1原baseline → D2instrument → slice → intervention → cross-model → explanation；不先做training或堆benchmark。新近邻用于定位，不自动kill。贡献成熟时人审，当前仍PROPOSED。
