# E55：original-noisy-comprehension（2026-10-03）

- **状态：DONE。** 跑前卡、全量源/token preflight后启动。
- **类型：REPRO。** 原人类材料的现代模型迁移；不是精确复现human exposure/history或I01的决定性pilot。
- **对应：C02 / P02。**
- **问题：** 在原400句中，模型默认保留字面还是修复表达，这与结构/合理性怎样相联系；一句literal任务指令能否改变选择而无歧义理解仍保持？
- **设置：** Gibson2013五alternation×20原items×4条件=400原句/原理解问题/原literal答案，E54仅白名单导出，全部保留。8端点：Qwen2.5-14B Base/Instruct、Mistral7B v0.3 Base/Instruct、OLMoE0125 SFT、Qwen3-4B/8B/14B；revision沿原固定manifest。每端点bare/common-Instruct-chat×default/literal一句控制共1600，合计12800完整分布；无随机generation/无训练。共同chat模板用于同family两stage，Q3关闭thinking。
- **读数：** primary完整` Yes.`/` No.`后验及完整candidate mass；content-only为已定secondary，不改变primary。原`CorrectAnswer1`仅用于literal-response映射，不将implausible的literal或repair硬贴对错。plausible/control答案匹配率、各源condition literal rate、default→literal配对差、同family stage差分别按原20-item cluster bootstrap（seed20261003，5000次）。不与QJEP跨dataset效应做因果相减。
- **阳性对照：** 原plausible200句，literal指令下完整字面理解；父任务所需yes/no偏好与candidate质量、无source null的answer prior分别报告。独立完整teacher forcing首末每interface×instruction，LP差<.001、prob差<.001、argmax一致、repeat<1e−6，失败0科学预测；全部prefix/candidate核对、无裁切。
- **噪声地板 + MIE：** 数值校对如上。科学pilot尚未启动；D1中10pp且item CI可排零的instruction变化只用来判断后续需要保留何种任务目标控制，不自动finding。plausible≥.95是入口可用heuristic，不剔除source/模型、不判死。
- **混杂审计：** 四种source条件与不同句法难度未完全解耦→不能把结构差直接当noise机制；没有原随机history/fillers exposure→不能复现原noise/prior context效应；source原句为controlled psycholing材料而非自然会话语料。QJEP metadata/code不适配与人类norm版本差异保留，human描述仅辅助不声称精确parity。chat/bare、instruction、terminal、候选质量分报；不筛正确item、不用judge、不合并language/family成一个能力分。
- **决策表：** A源控制和入口可用→下一卡在原source内固定critical句操纵原evidence，才进入I01；Bliteral一句改变读数且控制可用→解释为目标/默认policy待识别，下一步区分任务goal与交际证据；C控制/质量不共同可用→记录bounds与限制，不再局部救prompt，换能回答主问题的原source。
- **算力预算：** 8独立单卡，预计总2–4 GPU·时，锁后核对显存<10GiB，E51已排队stage优先获得空闲卡，下载与计算并行。**实际：** 8作业合计0.405 GPU·时（含加载与gate，单作业75–268秒）。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
2026-10-03跑前修订（0模型预测）：OLMoE Base/SFT与SFT/DPO的完整backend/词表均不同，先前E27/E49的实际输入核对不能冒充完整backend相同。本新协议不弱化完整gate；保留OLMoE SFT，补缓存Q3-4B，与Q3-8/14形成规模边界；Qwen/Mistral Base/Instruct保留。两次失败及缺preflight的队列拦截均0科学预测，写入`results/E55-preflight-attempts.json`。
- 全12800读数完成，8端点1600/端点，所有原source/token/numeric gates通过。结果`results/E55-noisy-parent-summary.json`，跑前`results/E55-source-preflight.json`，raw外置`runs/E55-noisy-*`。
- common-chat默认plausible200句argmax率：Q25 Base/Instruct .895/.950，Mistral Base/Instruct .760/.865，OLMoE SFT .570，Q3-4/8/14 .905/.950/.850。literal指令下依次 .915/.970/.845/.885/.635/.670/.920/.865；控制没有共同成功，不作总体能力排序。
- 同family默认chat implausible literal-probability差（Instr−Base）：Q25 benef −.1797 CI[−.3199,−.0184]、trans −.1711[−.2752,−.0468]，active/passive +.0899[−.0465,+.2263]。方向不统一且多重cell为描述，不能建立global criterion claim。
- Q25 Instr chat literal指令 loc +.2658[+.0823,+.4560]，trans +.2142[+.0854,+.3574]；完整候选支持质量在默认implausible各cell median仅3.53e−9至3.49e−5。secondary与primary也有差异，不把归一化概率叫实际生成分布或能力改善。
- 决策C/B边界：保留全部读数，不追加局部救分prompt；另用原source证据干预和独立生成读数检查任务目标与证据响应，先做E56完整源审计。
- 主张变化：C02仍L0；无自动升级。
- POST-HOC：无。
