# E101：重建credit的消歧前后贡献

- **状态：** DONE；完整注册三族已封版，旧INTERIM版本保留。
- **对应：** I07/P20，E96自然先前解释修订的credit机制；POST-HOC E96 Min完整图启发的区域统计，边界在统计前冻结。
- **问题：** 更忠实的cue-P未获得原难观察的高重建reward，主要因为局部前缀吻合旧错误，还是消歧后评价也不改变？竞争解释是pre-disambiguation credit trap vs later scoring still inherits misreading。
- **数据：** E96固定50社区pair/三当前自writer-grader，原GP目标上两个已冻结P的既有LP序列；原qualified-v3共识T2位置，仅sameSource所有已agree annotation唯一非空index且literal word可核，未知位置保NA/不填猜。预检50/50 GP有唯一共识T2，原资格不变。0新Source/P/teacher调用。
- **读数：** cue-P减GP-P reward sum，whole、before-disambiguating-word、disambiguating-word及after-word、from-disambiguating-word；sum严格可加重建全分数。token首offset与目标既有LP位置逐项验证，不按quantile猜边界。原共同Q fidelity/pattern方向乘region差仅在完整T1族可作语义诊断；全50和MVRR/NPZ/NPS并列，Source→paircluster10000bootstrap seed101，无挑负reward样本。
- **阳性对照：** sameTarget两P scored token IDs/offsets完全相同，prepare/context/prompt SHA与原cfg核，word字节/T2一致、pre+from==whole（1e−8）。原cue参考目标whole对比仍由E96主图承担，不把token局部再定义成语义Gold。
- **噪声地板：** 无新forward，原float32 LP和固定native context；tokenregion不是因果erase，也不证明latent唯一parse。全scope均报，semantic Gold missing/原P截断保未知，不将其中负值筛成错误主题。
- **决策表（跑之前写）：** whole负而from-disamb正且pre负→支持前缀成本压过后续修订信号的具体解释；from-disamb亦負→后期评分仍继承解释更合，不能靠去首词补救；主要ctor/model混合→区分作用范围；没有总体alignment异常→不从区域拼新机制。依原T2分解，不追加不同cut或提示模板。
- **算力：** CPU离线tokenizers，0GPU/0API/0model下载；模型tokenizer/config上午停权重后仍可读。先完整族INTERIM，默认三族主图等原E96全部评分/T1封版。不是为了补控制，而是现有LP直接分辨两个主要机制。

05:55Min完整50对/100panels/SHA1b5f1adc1903bf049f17b57b006888b0412e1fcd59472c685e1f44c9b147075d：所有GP cueP-minus-GPP before−2.516[−3.498,−1.694]nats、from+1.776[.749,2.865]、whole−.740[−2.249,.494]；36fidelity eligible对齐before−2.702[−4.020,−1.624]、from+1.938[.859,2.977]。NPZ/NPS从消歧起CI正，MVRR后段整体不稳定但word正；不是无处有修订信号。16/50 whole负而from正，保留所有tie/null；只诊断加和贡献，非因果internalstate证明。新E102单一suffix oracle检验选择质量，旧readout不改。

2026-10-08T06:22:28.509912+08:00 完整范围自审：完整三族150原pair×同两P缓存LP分解，0GPU/API，主map disambiguation-credit-map-v1.json SHA15346d37be15b3e01a32c4059632bb18cbb27f036abf20e076452d2f7a9011a6。ALL before Q−2.282[−2.982,−1.607]/G−7.949[−11.303,−4.624]/Min−2.516[−3.498,−1.694]nats；from Q+1.638[.851,2.448]/G+2.533[−.030,5.287]/Min+1.776[.749,2.865]。各族11/13/16条whole偏GP而suffix偏cue；G后缀均值方向正但CI0，不能写全三族每项显著。fidelity参照亦prefix皆负，from仅Q/MinCI分开零。不是唯一latent解释或神经因果移除。

2026-10-08T06:52:41.365394+08:00 固定原数据首Source（不是选成功案例）politician/bill/received：Q/G/Min from margin为−2.874/−6.115/−.833nats，皆仍偏旧P；Min只有word margin+.221，后续又抵消。该反例与整体图同时保留，不能声称任一Source完整suffix均含正确修订信号；不能把WORD局部诊断替换主suffix。
