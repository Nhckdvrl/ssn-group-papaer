# E70：同一源修补到底改了哪些断言，是否传递到依赖关系？（2026-10-07）

- **状态：** RUNNING；E64-v2完整效果后POST-HOC测量选择，原子标签读取前固定本卡与读数。
- **对应：** I03/I04、C09/P17。因果入口已有，完整CORRECT_ROLES只能说明所有关系是否共同正确，不能定位部分修复。输入排序首2 MVRR源已见真实V1受事恢复但V2仍错接/遗漏；不是为了证明原猜想追加防御控制。
- **问题：** 原歧义区修补是共同恢复源断言，还是仅改一部分、另一些不传递或反而损坏？聚焦隐式GP解释修订的后果，不做一般输出事实benchmark。
- **数据与方法：** 已有E64三族BASE_BANK/TARGET_BANK完整自由输出，一个核心配对对比；保留全部输入资格108units/54GP源/51clusters（MVRR19/NPZ9/NPS26；NPVP缺失明确）。原S/Q/gold/模型/源库一律不改、不重跑；只把已发表、最终已资格的**原始yes/no问题**作为新自由文本的语义原子。原问题来自E52 qualified-v3，可覆盖旧patch run没有评分但同一原S已有的其他问题；按S SHA匹配、Q去重，source G2 gold按原完成T1 ENTAILED→Yes、C/N→No映射。原FULL/CONTEXT/E63完整role图仍是既有证据，不再为了本新粒度重标所有条件。
- **新标注（不是重审可信源）：** Step只看PARAPHRASE与一个问题，判断positive proposition在该自由文本中ENTAILED/CONTRADICTED/NEITHER；不看原S、模型、bank、原source gold或旧T4标签，避免拿原S救回生成的遗漏。**每个PARAPHRASE/Q为一个独立标注项，每请求最多5个原子项**；不把5组×多问题打包规避用户上限。输出后聚回同一源的全部原Q，qid/文本SHA/schema/覆盖校验。Step Plan step-5-preview、4workers/共享总8活HTTP、medium effort/max32768、两遍独立打乱分批与第三遍分歧裁决，失败单条≤2语义重试。已有T4-v2与全部raw留存，新annotation不是替换旧类别。
- **主读数（新标签前固定）：** 每构式/GP或cue/initial-final-all/原source gold Yes或No：自由文本显式支持的比例、原Yes断言保留率、原No命题新增率（ENTAILED才算多断言），BASE/TARGET及TARGET−BASE。每source全部原问题共同保持源支持模式；源有initial/final正向断言时另报两者同时表达与单侧表达四格，以及其配对转移。没有某类Q的源记该原子缺失，不作无错；source No未在文本断言只说明未过度断言，不等于建立正确关系。
- **统计：** 先Q/同unit，再相同S，再lexical cluster，10000 bootstrap/seed70，source/模型/条件全部报告；unknown/failure独列、不当语义错误。共同正确仅覆盖已给问题，不叫完整latent parse。
- **阳性对照：** 原cue下源断言保持/同表原T4-v2；全部问题指纹匹配已完成metadata，不造新Q。schema强制输出qid与输入对应；相同P/Qpacket跨模型或bank只标一次，不能挑标签版本。
- **噪声地板：** 双遍一致率/分歧/unknown，全source CI；E64源干预已通过source-bank仪器，不加重复GPU baseline。第一固定小包仅检查接口覆盖，完整语义效应必须全包结束才读。
- **混杂审计：** 教师判的是表达文本，不是模型潜在状态；原问题可能含隐含agent/事件细节，某个正断言未表达不等于V1语义角色错（P15仍适用）。不按旧T4正确/错分类挑数据，不把“缺少错误”当“完整理解恢复”，不由名字相同推断依赖已传播。
- **决策表（跑之前写）：** 原子总是共同变化→部分传播失败猜想削弱，回源位置共同控制；同一源/同一bank只恢复initial正断言而final保持失败→用具体关系依赖选择下一机制实验；只删除原No但不建立source Yes→不是共同解释修复；原子与旧联合标签差异仅来自agent省略/含混→调整解释粒度，不包装新机制。全部族/构式的异质和null照报。
- **定位与意义：** Amouyal/Lee及人类good-enough拥有部分修复/混合解释。潜在增量必须是源位置因果改变哪些关系、哪些依赖没有传播的可预测规律，不能只把partial interpretation改名。Hanna一般syntax/QA分离、Geva task-specific KB跨用途不一致仍是近邻，而非自动否决。
- **算力：** 没有新GPU推理；API不限信用预算但保持Step Plan，校验/盲双遍优先质量。原始标签/输出外置E70，小摘要与代码进git。当前C06–08 L0/C09限定L1，没有合格idea。

## 结果

未读取新原子标签或效果。

**标注前范围收紧：** 第一构建草案包括六个旧科学条件，未发出任何HTTP，依用户“只最核心有辨别力”指导收为BASE/TARGET一个配对对比；三族/全部源/两侧不筛。不是用新标签选条件，原草案与manifest外置保留，旧全图不变。每原子P/Q一项，≤5项/请求，不借复合packet打包多于5个标签。

648原输出assignments→1280独立P/Q标注项。data SHAcdb513311ab5792a5a5377f5178c96615d46a042e4e991398bc9ec830e521880、assignment SHAe00b45caf8802f42960d4d8a3d06b31b9a870e139578e8c07eea9f8413b77c36。初版将needs_revision设False，被通用queue过滤成空输入，0 HTTP/0科学标签；空日志/summary保存，改queue标记True不表示重审原S。已核对全部1280进入队列，实际审核1263766/完整地图等待1274278。所有未知仍missing；部分修复/最终损伤/未知排除/四格与空构式的合成fixture已通过。未读部分语义比例。
