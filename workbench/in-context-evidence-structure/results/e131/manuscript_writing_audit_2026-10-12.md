# E131 文字改写与新增发现结果的独立校对

结论：当前文字改写通过有界语义、定义、引用归属与呈现校对；没有发现需要修改的实质问题。三项认识仍连成形成→关联内容→使用及公共背景的证据链。该结论不改变主张级别、不宣布整项研究或投稿准备完成。

## 阅读与核对范围

独立阅读了新 Abstract/Introduction、§2.2 符号与 provenance 定义、§6.5 和 Related Work 的变化，以及附录 M 新增 70B n16 段。主文三表和 §3–5、§6.1–6.4/6.6 的定量内容、Discussion/Limitations 与本轮基准 commit `83d522c387ed78d108f0df24aa657880070918c2` 相同；附录 A–L 未变。本轮仅核上述变化及已封结果，没有重新审计历史全部 raw、744 表格单元或重读 22 篇近邻全文。

摘要/引言明确把预测对象限制为测试中的 output-naming/output-namespace evidence interfaces，系数固定；没有将实际 donor 重建写成完整原生程序或全中介解释。公共 Source→词集事实与 private 输入–标签监督仍区分。shared 条件改善是 mean rule-use，既有一致标签代价、query-only 优势和完整输出损失仍在正文/附录保留。§6.5 的 Source-request margin 是原两源 margin 的等价投影，非独立机制量；小 criterion 增益不变成完整标准程序。

## 定义与近邻范围

D_A/D_B 为按 Source 拥有的 demonstrations，H_A/H_B 为按位置分组的上下文化 K/V；F_A/F_B 是固定公共背景下的 prefix 计算输出，R 是指定可达图下的 query 计算，q 包含请求 Source 与新输入，A no/yes 的 z 是 yes−no。这里的 relational provenance 是配对干预中的因果关联依赖，不等同唯一来源恢复、潜在 ID 或已逆向完整算法。句中先固定公共背景使简写公式有明确条件。

22 个原始论文链接及 bibliography 保持。Changed Related Work 延续 CTA/Cho/AddUp/Sun 的 contextualization、input–label 与 operation 所有权，以及 binding/竞争检索、PCW/CacheBlend 的上下文依赖范围；项目的具体多 Source 反事实与 joint use 测试没有被表述为首次一般 contextualization 或 KV 不可组合。既有 Limitations 未删。

## 新增 70B 发现批

附录只纳入已封 13/18 批，另五批运行/等待，正文确认仍指完整 32B 链。70B 的 **100% 是 A 的单源 full-output 控制，两个 private 方向各八个 context**；不据此推出 B 所有函数已验证。signed formation 为 .993 [.612, 1.373] nats。label-interface KV 的 raw r=.542/.854 分别是 shared-word/separate-word **B-position 缓存背景，两者均 full-source query reading**，不能读成 A-only/full-source 开关。RMSE .632/.825 与 zero .705/1.472 相符；第一背景 V 误差低于 KV、K 略高于 zero 的 caveat 保留。fixed-word answer excess magnitude .237 [.116, .368] 与 signed −.229 [−.382, −.085] 均保留。这些数值来自已独立 raw-first 封存的第 13 批，不筛方向。

Root 读取本批 stdout 三个 relation 汇总的例外已在 raw 审计记载；本独立会话仍先 raw 封存后作者比较。不能将本轮称为所有参与者全盲。未执行第二次 GPU 实验。

## 编译与快照

当前 PDF 30 页，main 三表三图、附录 26 表 12 图，manifest 与科学 Markdown SHA 对应；编译日志 Warning/undefined/Overfull 均为 0。视检第 1、2、26 页：摘要与引言、条件定义/公式、70B 段的列布局与符号可读，无裁切或重叠。官方 style/bibliography 与已审版本相同。本项不判断会议信息、页数资格或接受概率。

- PAPER_DRAFT.md：`9aa5e6928e33b95bd426fd4e03bd6746d800a255ad8220dc9d3d31219f0ada18`。
- PAPER_APPENDIX.md：`670e870c1e99fff3896ca8587d788236e2161bdf9ad2fcec74670e814438df5a`。
- build_paper.py：`40a08d5e06cd182dfccf438f8ef416bb3be8d744281931c611425c46ae1e1220`。
- PDF：`5412196d4c1656dfff5a28804cd3cc5ed3f672d225257782afa2010d065579c3`。
- manifest：`481ae74b0fb88f4576b1807b45589cfce2c073e45d8eaf3ca32e9c61ceb14519`。
- 当前 13 批 summary：`66aeae626722594c7eb3ee78d7bf14237b8efa385b512bb6f4927e2bf8bde409`。

待修改事项：无。本轮不新增实验资格、head/layer/format 门槛，不以未完成 70B 确认或有限 Cue 接口收缩既有三项认识与完整 32B 阳性。
