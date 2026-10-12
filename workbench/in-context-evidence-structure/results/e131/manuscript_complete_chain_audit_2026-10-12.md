# E131 完整18批主文/附录与最终呈现独立校对

结论：**通过本次新增呈现与有界主张校对，没有发现实质必改项。** 当前四模型链、完整18批和最终PDF绑定一致。本报告是paper-critical增量/呈现审计，不是接受判断或整项研究价值的自动结案。

- 对应同一 ICES / C21–C24 / I04 / P17。没有改变任何科学源、正文、主张等级或研究状态，没有新GPU评分。
- 完整18批、480 run-stage contexts、245,760 scores、63.99923660106129科学GPU·时；六组新32同family/stage配对已独立封。原有pre-author raw与pair snapshots保持。
- 原三认识仍是：输出身份影响历史形成、消息携带学习的关联、形成与读取具有不同功能约束。新增70B与32B证据支持这些已定义接口/操作的重复检验；没有改成唯一latent算法、独立hidden模块或完整criterion程序。

## 打印数字与配对范围

独立从已封full precision逐项核145个打印标量：主文Table3的48项、附录Table30的36项、70B确认功能段48项、正文功能段10项、明确Qwen-only恢复配对3项。所有数值及CI直接舍入一致；没有双重舍入差异，Q8 full-reading restoration lower仍为−1.269。另核A单源能力归属及三个raw reconstruction r。

70B确认shared/full准确率88.48%→98.93%，mean gain10.45[7.91,13.09]pp；A/B分别9.57/11.33pp，same-convention gain0，opposite20.90pp。此均值不等于joint98.05%。targeted−all23.05[21.78,24.22]pp，query-only7.32[3.81,10.84]pp。far/all isolation候选99.12%、实际full54.30%、joint9.96%，other-source词45.31%；far query-only−1.76[−3.22,−.59]pp和far selective CI跨0均保留。70B−8B selective gain差1.56[−1.56,4.88]pp未被写成确定容量优势，query-only差−10.84[−14.94,−6.93]pp保留。

四模型signed formation/removal各确认CI为正；四模型A-only恢复各CI正、full-source恢复各CI负，正文没有混淆signed与abs。70B形成单源控制明确只验证A（99.22%每私有方向）；native A single100%和function A/B/namespace/private96.88–100%具有各自范围。raw r .883/.619/.909是对应label KV/background的部分重建，不是完整准确运输。−1.368恢复配对明确仅Qwen。

contexts逐字配对限定同family/stage；形成和function分别采样SST，native使用controlled restaurant。不同训练recipe的checkpoint比较没有被写成causal scaling law；same operation的重复检验没有要求幅度相同。抽象新增仅32B/70B确认，§2.2–6、RelatedWork、Discussion、Limitations对上一sealed稿字节保留，近邻所有权与原criterion有界结论未扩展。

## 图与实际PDF

12/12确认点，36个mean/CI端点等于sealed raw、最终summary与CSV；旧11点原值不变，没有pending/零占位。get_stat AST原样，尺寸/字体/footer和CRLF→LF仅呈现改动。Function面板是shared/full/two-Actor mean gain，不是joint。此前图资产存在但未嵌入的snapshot不能称作实际成稿图；当前AppendixM的Figure17在PDF P33实际嵌入。

独立视检P1、7、8、9、28、29、30、31、32、33及原PNG。Table3/Table30、Figure17在实际ACL宽度可读，无裁切。正文Discussion结束P8，Limitations独立P9页首，总33页；3主图3主表、14附图27附表。最终compiler pass Warning/undefined/Overfull各0（早期引用/line-number警告已收敛）；81条Underfull排版提示保留在log，所检页面没有裁切。官方style/BST/preamble/24条bib与已审版本一致。

## 最终封签

- main：`11c7cbe89e9b3f6336e2aa8440880413961ea5ffce05876292be79d3122874ba`
- appendix：`09359666a8b39bef8e8640516f9a7904a3a34b7cc3cb15f62e047c328d3e454b`
- PDF：`070026c97c4da05892ced9810e0dcc8559a50aca582f19bff9bc4d82ee1fe5e4`
- summary：`06a2b0bdb61baf6b91889e13ae877d0168a4a7c456c7df878ed3cc2d1688a0b6`
- plot manifest：`fbf5772c45246fad544fe5cc473ded3a758e00583c2942691691c981896a592f`
- 本JSON：`c250874a99b9e665a3b05ac5d71e26278544792f72c997dc7be09575003c4457`

阅读范围是本次git diff、新增§7与完整AppendixM、已封raw/analysis/report/pairs以及上列PDF页。没有重算旧744单元/旧stage的bootstrap，没有独立GPU重跑。18批各自raw-first读序及root第13批stdout阅读例外继续由原始审计披露；不能写成所有参与者全盲。这里只确认当前新增证据与叙述适配、呈现完整，不以近邻兼容或接口有限重新设科研资格，也不自动宣告论文科学意义已终结。
