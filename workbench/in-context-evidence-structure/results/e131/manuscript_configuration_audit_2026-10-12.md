# ICES 最终编译配置、方法描述与八页呈现的独立校对

结论：最终快照通过。正文8页，Discussion在第8页结束；独立、无编号Limitations从第9页页首开始，参考文献随后，官方双栏附录从第11页开始，共32页。此次是配置/组织/方法源核与呈现审计，不是新增实验或科学完整性/录用判断，没有改正文、science、claims等级或研究状态。

## 编译配置与实际呈现

直接只读 MPD CLOSED 最终 paper-acl-v3 的 main.tex/build.sh/README。共同 class article/11pt、review ACL、Times/Inconsolata、T1/UTF-8/microtype 及全部共同 package 指令匹配；ACL和BST逐字相同。ICES仅增加array/calc/tabularx用于Markdown表格。编译实际使用manifest所记TinyTeX pdfLaTeX/BibTeX，至少四轮pdfLaTeX、遇错停止并有限补轮；未执行/修改MPD构建。

当前manifest与主文/附录/builder/table captions/style/bibliography SHA逐项相符。独立解析最后pdfLaTeX轮：Warning、undefined、Overfull均0。当前PDF视检第1、2、6、8、9、11、12、13、14、28、29页：摘要/引言、数学notation、自然功能主表/图、32B三环表、P8/9边界、A方法与模型表、B响应矩阵及M的70B发现段均可读；没有裁切、重叠或丢行。旧309f与7f构建只是中间快照，不作为当前final。

## 组织、数字与文献保留

对照重排前全文，主文三张结果表逐字相同；去除标题编号后，正文所有小数读数的多重集完全相同。13个改写内容块逐项阅读：除作者引用/数学符号格式外，是流程、重复论述和Limitations整理。形成→关联内容→使用/公共背景的三项认识及32B确认仍保留；没有改成普遍最优repair、完整criterion程序、唯一算法或参数量因果scaling law。有限Cue、固定aspect以及private功能局限在结果/附录保持。源接口、实际donor、mask重新归一化/后续活演化、构造private、预训练和多重比较边界仍明确。

旧26张附录表全部保留，仅新增固定模型表；现在主文3表3图、附录27表12图。30个有内容caption与编译顺序逐项对应，并核其单位/mean-vs-joint/namespace及发现确认范围；没有重核历史744个数值单元。A/B交换后是方法A与完整功能matrix B，C–M维持编号。原22个primary URL/citekey保留，另加SST和MHS两篇dataset文献，24个citekey全部有定义和引用。citet只改变作者型显示，未改变归属对象；Pei-lin Li的姓氏归一化不改变身份或ownership。

## 新方法的实际源核

SST原class0/4、训练hash奇偶独立池、validation/test queries、5–64 token范围、无model-output筛选，与e121_sst_materials一致。MHS comment_id分组均值、50词、hate-score/race/gender阈值、seed5600与70/30分割，与e56 pools及e90调用一致。literal serialization、历史sender word+separator、严格past edge阻断/受限恢复、全query gate、pristine cache复制、候选/full/joint定义及910/109910 context bootstrap/flattened reconstruction，与列出的冻结源码和已封audit一致。

此次另外只用固定CPU tokenizer复查了附录新举例：Mistral首个E120 confirmation prefix分段351 tokens、literal整段335，separator为3 tokens；32个B sender位置也与已封几何相符。没有新GPU科学forward或旧CI重算。

发现并已修复一处方法概括：E122 controlled criterion×code policy primary平均四个B worlds；E123/E131自然function primary平均origin/cross，within为独立control。该文档修正不改变任何科学数据。单源100%明确为A。70B模型表使用实际Nous镜像beb678…，官方349…在30-shard权重等价说明中；两份metadata的30个size/SHA逐项相同，runtime pin亦为beb678…；8B使用实际Nous镜像1f47…。本轮没有重新hash全权重或读取远端GPU RAM，权重等价部分引用既有身份审计并核一致性。

## 新第14批与图的绑定

新增native段四个signed统计及CI与已封raw相同：removal1.542[1.096,1.970]，A-only restore1.011[.637,1.401]，full-source restore−.440[−.653,−.208]，cross-vs-within2.560[2.065,3.059]。它是n16发现批，正文确认仍指32B；其余四个70B阶段未作为完整证据使用。

图只重绑定14-stage summary，仍9/12个确认点、27个mean/CI值误差0；原CSV/script和已封读数不变，三个70B确认点为空pending。此次未重算已封science/配对/CI，也没有新的模型、head、layer、格式或研究资格要求。

## 最终文件绑定与实际范围

- PAPER_DRAFT.md：`c12bdd4fc407c3a780319079f9387328e23d412e92ca187954e764ca60322616`。
- PAPER_APPENDIX.md：`a55b289ca3a0ee6aef7405b41f32e5a1ae5fd3a7828e6fd1e3c9334bcf6041bf`。
- build_paper.py：`e063a4ef228b3960a955c2b741883435eb483b58abac8c42a236f784b46997a2`。
- PDF：`0e08e552ee29261268f8cf20ae1055c55c0b6ad317e6eb3aeee0b0c7de201aff`。
- manifest：`9c5549fac4f3b5861c2a1d6d9371efb96e0ccee4f2e1b1c27d21a76baa0a5962`。
- 14-stage summary：`d706568667acbcf715e51a63b623971bc8c4057b185886e2928d68f63a8bd8cd`。
- plot审计：`f439cee7fee7910d25479df451f28eff834d835d0c62278831d32a1fd9d4218a`。

本轮实际范围为重排/压缩后的变化段、新A方法源码概括、模型/数据/observer metadata、caption/references对齐与上述典型页。没有重读24篇近邻全文、重审全部历史raw或执行独立GPU rerun；对应已有科学审计保持独立封存。剩余必须修改项：无。
