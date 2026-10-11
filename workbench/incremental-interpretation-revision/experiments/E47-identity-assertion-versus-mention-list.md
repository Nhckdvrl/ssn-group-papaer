# E47：身份断言、未核实引用与名称清单（2026-10-06）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E46 identity作用大且与event表达交互，必须区分meaning、词串与额外曝光。
- **问题（一句话）：** 身份说明引起的负向预测需要该说明作为事实被断言，还是未核实引用/纯名称清单也足以产生？
- **设置：** E46仅unused nearby、event reification0/1、两order与全部24source。identity四条件：absent；original asserted；original全文逐字置于unverified example quote并明确truth left open（不是false）；name inventory，只说account有fixed names和原actor descriptions，不断言identity分离、排他或role关系。actor/activity/role worlds/targets全部冻结，4×2×1152=9216raw；absent/asserted端点需字节复现E46对应4cells。Luna作者24字段＋whole-rendered10176packet独立审核。current QA768contexts×base/R8=1536；identity句状态只用预先固定source-world/mention-first、每source×4identity×2event=192contexts×base/R8=384，合计native1920，不按得分选context。
- **读数：** Dactivity/Dneutral/J、old/newother sameV/differentV、new−old及different−same。主quoted−asserted、inventory−absent、quoted−inventory在newother/sameV两event/order分开和预先均值；身份效应是否依赖事实status与event重复的交互。12family先两源均值、paired10000 bootstrap seed20261005；all/eligible/grammar common/E31固定cohorts全报。identity-status读数判断asserted/unverified_quote/not_asserted，不问世界中身份是否真的相同。
- **阳性对照：** 四个重复端点likelihood逐task drift；old explicit患者QA、原身份句的语篇status可访问；R8 current保持已有scope句，status一句要求区分unverified quote与passage assertion。readout是strings，不叫belief或概率世界错误。
- **噪声地板 + MIE：** E46重复2304task target drift0；identity主newSame activity−6.556 [−7.935,−5.254]bits，但强度包含额外提及和词串。quoted框架加字、inventory长度不同，不冒称严格词数等价；保留全部hash/length，不能从一cell挑结论。
- **混杂审计：** quote是否明显未被endorsed、其实际role facts仍断言；inventory无distinct/separate/否定/活动角色暗示，候选/actors各一次；usual name非alias和群体成员限制原样。identity assertion原文没有断言每event必须不同患者。native少量错答不能倒用作任意世界错误故事。
- **决策表（跑之前写）：** asserted才强负且status可访问→identity表达的断言地位调节role期待，下一自然身份表达/功能用途；quoted同样强负而inventory弱→identity词串/框架足够、断言含义非必要，追lexical suppression；inventory已复制负向→额外实体/actor曝光或列表结构充分，不能当全局角色constraint；activity和neutral近同改动→一般提及/读数；old控制失效或status无法访问→不作语义因果结论，先追数据/读数。结果只修同I01，不能凭新模板首测认证novelty或换题。
- **算力预算：** frozen本地Qwen3-8B/现有venv，四raw分identity独立GPU0–3，nativecurrent/status GPU6/7，预计≤.2GPU·h；**实际：** 四raw76.98/113.73/135.42/105.67s，native current1536/status384完成，commit6e880f7b。
- **命令：** identity_status_roles.py build/adopt/split；frozen likelihood/native；analyze_identity_status.py。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

2026-10-06推断前计数校对：原卡误把每cell1152除以2，builder在候选生成前断言拦下；正确8cells共9216raw、1920native、10176审核packet。设计/读数不变，未运行错误计数版本。

2026-10-06推断前语料v2：独立审核指出v1引用末尾重复句号、inventory元语言句略生硬，作者逐条修复；引用内部原body/status question不变，inventory统一自然“uses … as names / … as descriptions”并对actor strings加引号。v1全部候选/审核保留、未推断；v2全部render重新外审，运行目录明确E47-material-preparation-v2。不改实验读数或假说。

[完整结果](../results/E47-summary.json)：重复端点4608target drift0。twoorder/event预先平均：quoted−asserted newSame activity +1.076 [.264,1.815]bits，name inventory−absent −3.849 [−5.053,−2.670]，quoted−inventory−.571 [−1.176,.066]；asserted−absent−5.496 [−7.105,−4.026]。原identity assertion并非负向预测必要条件，纯额外名称/actor inventory足以产生大部分作用；status有调节但不能叫全部语义原因。

new−old J的inventory−absent−.623 [−2.287,1.083]、quoted−inventory−.275 [−1.250,.670]；一般提及/old读数改变不可省略。不同−同V J的inventory−absent+1.940 [1.232,2.660]，说明还有predicate-conditioned分量，但它没有声明identity/role约束；这不是内部graph或能力错误证据。所有8cells两order/cohort/family原数字在JSON。

actual回答独立两人各960条三hash/全ID核验，old current1536/1536clear/correct、status383/384clear/correct；唯一status错在absent priority，被答成unverified quote，保留不删。模型能区分名称inventory、未核实引用与原断言，但这种知识本身不是新颖性。**C05收窄为受人物提及/语篇frame调节的预测结构，不能讲“明确身份关系导致全局角色排他”的机制。** 下一检验reference identity/form及自然原文材料，不再堆identity词句/模型扫表来认证novelty。
