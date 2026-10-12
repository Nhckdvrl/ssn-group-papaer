# Cai et al. — Beyond Demonstrations（EMNLP2025 Main）

- 原文：[正式PDF](https://aclanthology.org/2025.emnlp-main.297.pdf)；本次读主文§1–7/limitations及附录A/B/F/H/I相关页，未运行其代码。
- 问题：低样本task vector对示例/位置敏感且效果有限，如何形成更可部署的task representation？这是适应方法工作，不是完整原生算法逆向。
- 链条：每个有标签样本轮流作query，提取MHA output projection并平均；再分段、用REINFORCE监督选择位置，固定配置后换另一批同任务示例来源。最后一步把部署位置与所承载任务内容分开，是可借鉴的功能测试。
- 审计：推理时主模型冻结，但位置与强度使用原训练标签优化，不是无监督原生电路；无额外样本不等于无监督。平均收益不能抹掉具体任务的损失，16-shot Qwen组弱于ICL。构造成功不证明模型默认就使用这套状态。
- ICES距离：多层/细分task信息注入已有所有权。E129整体Cue KV与Source条件运输不声称首次分布式task状态；E56涨分也不能当免费读出。方法的收益不自动替代ICES的关系来源、原生操作与功能对比证据，也不迫使我们为涨分改训新模块。
