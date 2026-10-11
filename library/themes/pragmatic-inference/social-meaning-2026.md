# Social Meaning in LLMs: Structure, Magnitude, and Pragmatic Prompting — arXiv2604.02512v2

[原文v2](https://arxiv.org/abs/2604.02512v2) · [原数据](https://github.com/muehlenbernd/llm-social-calibration) · [原human OSF](https://osf.io/m4rhn)。10页全文/两个附录已读；代码/原cache/human raw未核对，venue未确认。

- **来源 DOCUMENTED：** Solt2025有pretested precision-demand contexts；语言形式如何改变social meaning→structure/magnitude分离；再问alternatives与speaker motives的理论提示是否校准判断。不是仅造新metric。
- **设定：** Human371人、6场景、HP/LP×exact/approximate、六traits7point；GPT4o-mini/ClaudeSonnet4/Gemini2.5Pro每query10次T1；minimal/alternative-aware/knowledge-motives/combined。
- **ownership：** directional正确但强度过夸，alternatives-only提示可放大推断，knowledge-motives可能减弱；ESR与CDS、interaction calibration与不同model的tradeoff均已明确。不能claim第一次语用强度校准或推断过强。
- **数字与边界：** 三model默认CDS .393/.538/1.480，KMA .402/.310/.848；COM .304/.312/1.338。结构DAS/ISS均1但效果不统一。仅一个范式、闭源异构，作者不因果归architecture/training。人均值和individual RMSE不同是聚合事实，不证明群体分歧由模型正确表达。
- **待核对：** AppendixMinimal例正文说competent，示例task却confident，KMA回competent；Table4给participant RMSE不能排除其他semantic/scale artifacts。CDS分母选显著nonzero效应，不是独立校准ground truth。先查公开raw/任务词再用于数据。
- **距离：** 对“说者有多专业”的social judgement与对specific implicit fact的推断不同。此工作直接拥有alternatives×epistemic-motives的prompt叙事；我们的增量不能只做同prompt换openweights，要自然条件证据、同谱系归因与可靠norm。

## E60原资产驻留更新
CMCL2026接收由官方repo说明，尚未核对公开review。code revision c60d6004781cafeb0cdd617105c96581cc93669f，原17280responses/所有432cells×10重复与parser核对；原metric functions与独立十effect arithmetic <1e-12。取得原OSF362/390retained raw，Exp1 global主表35/36按3位小数一致；GeminiCOM rho .916 vs .932，CDS两处小差保留，非全表精确复现。当前144 MIN prompt用competent等六trait，无confident；cache无原prompt，历史query无法确认。知识follow-up不在LLM asset的stimulus文本中；原ELM更揭示motivation可有抵消，不能把KMA提示改善直接当利用实际knowledge证据。
