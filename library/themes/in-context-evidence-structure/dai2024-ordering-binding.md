# Dai / Heinzerling / Inui：Ordering 信息与绑定

- **正式来源：** [EMNLP2024 Main PDF](https://aclanthology.org/2024.emnlp-main.967.pdf)；本轮读§2–4.7、结论/limitations；PDF初次web fetch后续超时，使用同官方PDF的本地提取继续读。未复现作者代码。
- **问题/idea来源：** 已有binding ID解释，如何直接提取参与绑定的表示？PCA/ICA提供低秩ordering方向，随后用编辑与steering检验因果作用。
- **有信息量的动作：** 固定绝对位置而改变唯一实体次序、加filler与interjection，区分ordinal ID与token位置；去掉关系语义但保留次序，发现ordering相关仍存在。
- **证据边界：** 该方向可改变检索，并不因此专门编码关系是否成立；实际分析主要query激活，作者明确未解释context如何形成该信息。最终PDF比网页旧摘要更明确区分OI/BI。
- **ICES距离/设计学习：** E126/E127公共表次序与缓存兼容不获得首次ordering/binding所有权。我们的对象是从多Source demos形成的私人关联及联合新输入功能，现有whole-cache效果尚未识别OI方向。无需为此再加PCA/head矩阵；保留来源条件响应和公共共同偏移的竞争解释，按完整证据定位。

## 同一解释的跨模型验证（2026-10-12再读）

正式PDF§4.3–4.5及附录A.4/A.6/A.9/A.10：主体Llama2-7B在六关系上测试ordering方向干预；Llama3-8B、Qwen1.5-7B、Pythia-6.9B与代码微调Float-7B复验相关子空间/因果检索。没有70B目标。不同模型可以使用不同层与强度：Float用l10、v2.55、alpha5，而主体用l8、v2.5、alpha3；Float效应幅度也更大。共同认识是ordering表征参与绑定，而非相同效应数值。它用绝对位置与唯一实体次序的反事实排除最直接替代，不需要声称每个binding都只能采用此法。ICES应保留原生历史形成操作/关系来源的共同功能预测，同时测实际读取环境；不将某个恢复方向或交互差异自动当作全部理论失效，也不为普遍性补每个组件。
