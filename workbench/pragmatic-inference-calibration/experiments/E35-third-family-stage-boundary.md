# E35：第三family原自然材料的stage边界复核

- **状态：** DONE
- **对应：** C02/P02/P08；跨模型边界，不将8端点当8families
- **问题（一句话）：** Qwen/OLMoE的自然解释与取消推断结构能否在独立Mistral真实Base/Instruct谱系重现？
- **设置：** 官方mistralai/Mistral-7B-v0.3 SHA caa1feb0e54d415e2df31207e5f4e273e33509b1与Instruct SHA c170c708c41dac9275d15a8fff4eca08d52bab71，model card明确后者由前者instruction-finetune。non-gated/Apache2.0，Transformers索引所列权重约29GB/pair，不重复下载consolidated。先完整tokenizer/targets CPU preflight；原Hu、Wave、ImplicatureX与E33/E34相同自然材料复用，不新增benchmark/标签。是否兼容single-token协议未知，不能把不兼容当模型错。
- **读数：** 原parent task/scoring不变；能满足原single-token协议的仅照原score。若不能，先记录协议不可用，完整候选序列评分在独立preflight与附加协议卡冻结后才跑，不悄悄改旧E28–34主读数。samefamily完整common tokenizer与actual IDs比较；bare与common-chat均保留，不把base的陌生chat失败当posttraining gains。
- **阳性对照：** 只完整固定权重，原source/hash/gold、token绑定、prefix完整与完整读数数值gate；首末单序列重复、选择support/invalid/ordering诊断同前，不使用不完整文件。
- **噪声地板 + MIE：** FP32/noTF32；CI按原item/concept pair/question而非模型多seed；numerical threshold原.001或single repeat1e-6，不能因新family放宽gate。
- **混杂审计：** 两checkpoint没有独立training replicate；Instruct具体mixture未公开完整，不能归某种RLHF因果；Mistral2024不是最新frontier，只是第三family stage控制。计算budget/source版本/terminal/多token编码原样报告。官方asset下载和CPU检查不称GPU实验。
- **决策表（跑之前写）：** A同自然条件结构跨family成立→候选observation需独立数据/替代解释，不升claim；B方向反转→报告stage/family边界，拒绝统一criterion；C强baseline均改善→保留baseline，不造paper；D协议或numerical gate不兼容→技术隔离，用源能力协议重新判断而非因失败报差。
- **算力预算：** 两pinned权重下载并复用本地3.0TB空盘；最多8独立卡由GPU锁接上、每endpoint/task≤1GPU，默认无training/API/judge/子agent。具体GPU运行只在后续readout兼容检查通过后启动。

## 结果
跑前卡；当前只是official manifest与asset下载准备，不能报告任何第三family实验结果。

## 跑前协议兼容补充（尚无Mistral GPU预测）

两个原数字字符串encode都是公共空格token29473+不同数字token，单token脚本不可用。新readout计算完整数字内容序列：原完整prompt前缀严格匹配，所有候选分解为同一已生成prefix+最后一个不同token，公共prefix概率在归一化中精确约掉。保留full-choice-content LP、公共prefix LP、conditional candidate mass和joint support mass，不把公共空格的prob当选择概率；numeric无EOS，匹配parent atomic意义。裸入口固定原BOS1；chat用完整官方Instruct tokenizer与原system/user角色，共用于Base/Instruct。

冻结四task×两stage=8slot：原Hu bare1365、Hu chat1365、Circa433×original/strict×bare/chat×两order=3464、原ImplicatureX6504（parent/format）。源class/order/gold/condition不改；CIRCA不是原训练复现。FP32/noTF32/single sequence/no padding，首末repeat概率1e-6后全量。不与旧Qwen/OL无BOS原task绝对数字作training因果配对，不更改任何旧主读数。输入/full-choice SHA每项保存，两Mistral固定实际完整tokenizer。第三family如果同样只有prompt效应，不升级scientific claim。


跑前完整预检通过：1365/1365/3464/6504全部full-choice前缀严格保持。Hu原尾空格不额外添加；Circa裸入口不添加空格。官方chat_template在追加assistant后会遗漏system（只在user是loop.last时合并system），因此冻结原generation prompt，再追加官方assistant序列`空格+content+EOS`，评分去掉EOS，原system完整保留。两个失败均在CPU、0预测；不是科学异常。除repeat外，首末每个候选以独立完整teacher forcing核对factored LP/概率<.001、argmax完全一致；不放宽数值gate。预检见results/E35-prefix-preflight.json。


## 完成与证据限度

八作业全部通过独立full teacher-forced LP/概率、repeatgate并完成；1365+1365+3464+6504=12698/model，two stages总25396。逐项原source字段/fullcandidateIDs/prompt SHA与跑前计划全匹配，Base/Instruct实际input一致。原natural Impli Instruct−Base initial endorsement −.29800 CI[−.36977,−.20836]；cancel-minus-irrelevant差+.01163[−.04586,.06584]。Base restricted numeric整体joint支持仅.06535，Instruct.98756；二者readout遵从显著不同，不能裸当latent能力。recognition .08/.14，不能点估计说Instruct更强或统一更爱推断。Hu分phenomenon有改善与恶化（Coherence chat .515→.660，Maxims .537→.347），同任务上也不是全局增益。

Circa PN chat原序强/弱Base .7692/0、Instruct .8846/0；逆序.1538/.0769与.5000/.5000。顺序依赖仍限制科学解释。原完整结果与条件/支持率均见results/E35-third-family-summary.json。C01/C02仍L0；第三家族stage不支持统一criterion故事，但没有自动关线。
