# Dai / Heinzerling / Inui：Ordering 信息与绑定

- **正式来源：** [EMNLP2024 Main PDF](https://aclanthology.org/2024.emnlp-main.967.pdf)；本轮读§2–4.7、结论/limitations；PDF初次web fetch后续超时，使用同官方PDF的本地提取继续读。未复现作者代码。
- **问题/idea来源：** 已有binding ID解释，如何直接提取参与绑定的表示？PCA/ICA提供低秩ordering方向，随后用编辑与steering检验因果作用。
- **有信息量的动作：** 固定绝对位置而改变唯一实体次序、加filler与interjection，区分ordinal ID与token位置；去掉关系语义但保留次序，发现ordering相关仍存在。
- **证据边界：** 该方向可改变检索，并不因此专门编码关系是否成立；实际分析主要query激活，作者明确未解释context如何形成该信息。最终PDF比网页旧摘要更明确区分OI/BI。
- **ICES距离/设计学习：** E126/E127公共表次序与缓存兼容不获得首次ordering/binding所有权。我们的对象是从多Source demos形成的私人关联及联合新输入功能，现有whole-cache效果尚未识别OI方向。无需为此再加PCA/head矩阵；保留来源条件响应和公共共同偏移的竞争解释，按完整证据定位。
