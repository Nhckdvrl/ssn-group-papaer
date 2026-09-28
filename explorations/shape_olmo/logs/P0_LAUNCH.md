# P0 launch log
2026-09-28 01:46 JST — T7 final (Olmo-3-1025-7B main) scoring, fvcrc10 GPU3 (only idle card; fvcrc10 g0-2 and fvcrc12 busy with other jobs, fvcrc13/15 full, fvcrc20 memory held, fvcrc11/21 unreachable).
2026-09-28 01:58 JST — first T7 run KILLED after pg19: mean NLL 4.68 with NLL rising with position (1.99 first 512 → 5.23 last 512).
  Cause: transformers 5.3/5.12 build ONE YaRN rotary for all Olmo 3 layers; 4.57.6 uses default RoPE for
  sliding_attention and YaRN only for full_attention. Under 4.57.6 the same window gives 2.11. Its scores were deleted.
  Relaunched T7 with verl-clean python (transformers 4.57.6), same card.
2026-09-28 02:13 JST — H7 (Olmo-Hybrid-7B main @4f1cc566, no RoPE / DroPE) sanity: pg19 window0 first-512 1.80, full-8k 2.06
  (T7 under tf4.57: 1.90 / 2.11). Launched H7 scoring (openslime + tf5.12), fvcrc10 GPU3, concurrent with T7.
Tagger check (wikipedia window 3, tokens 2000-2060): subword alignment correct; `),` gets close-bracket + punctuation.
  Tagger errors seen: lateral→Noun, lack→Noun (unknown words default to NN; Noun share 36% of prose tokens).
  Brown trigram→bigram→unigram→regexp backoff tagger (our choice; the paper only says "Brown tagset via NLTK").
2026-09-28 03:34 JST — CPU pilot (login node, 22 threads): MB130, PY160, PY160s1, PY160s2, PY410, PY410s1 on first 60 NeoX-2k windows of pg19/wikipedia/python
2026-09-28 04:14 JST — T7s1 launched on fvcrc12 GPU1
2026-09-28 04:24 JST — queue2.sh (≤8 concurrent guard) started on logs/jobs_remaining.txt (H7s1 + Pile/Pythia jobs; T7s1 already running on fvcrc12 GPU1).
2026-09-28 04:34 JST — H7s1 launched on fvcrc12 GPU1
2026-09-28 04:49 JST — queue2 had exited after H7s1 (ssh consumed the job-file stdin); fixed with ssh -n, restarted on jobs_pending.txt.
2026-09-28 04:50 JST — PPT launched on fvcrc12 GPU1
2026-09-28 04:57 JST — PPH launched on fvcrc12 GPU1
2026-09-28 05:07 JST — PPR launched on fvcrc12 GPU1
2026-09-28 05:15 JST — PY28 launched on fvcrc12 GPU1
2026-09-28 05:22 JST — M2_13 launched on fvcrc12 GPU1
2026-09-28 05:28 JST — PY14 launched on fvcrc12 GPU1
2026-09-28 05:32 JST — PY28_71k launched on fvcrc12 GPU1
2026-09-28 05:37 JST — ladder checkpoints local; queue restarted with ladder first: T7s2 H7s2 T7s3e H7s3e PY28_36k 
2026-09-28 05:40 JST — T7s2 launched on fvcrc12 GPU1
2026-09-28 05:51 JST — H7s2 launched on fvcrc12 GPU1
2026-09-28 05:59 JST — T7s3e launched on fvcrc12 GPU1
2026-09-28 06:10 JST — H7s3e launched on fvcrc12 GPU1
2026-09-28 06:13 JST — PY28_36k launched on fvcrc10 GPU1
2026-09-28 06:22 JST — PY28_36k INVALID: HF step36000 branch's model.safetensors is main's blob (bin differs, max|Δ| 0.08); scores moved to scores/INVALID_*; score_any.py now loads pytorch_model.bin for revisions. step71000 verified bin==safetensors.
2026-09-28 06:46 JST — queue started: T7s3m H7s3m PY28_36k 
2026-09-28 06:46 JST — T7s3m launched on fvcrc10 GPU1
2026-09-28 06:48 JST — H7s3m launched on fvcrc10 GPU3
2026-09-28 06:50 JST — PY28_36k launched on fvcrc12 GPU0
2026-09-28 06:58 JST — queue: re-score T7/H7 (3 domains) to add lpin/lpout
2026-09-28 06:58 JST — T7 launched on fvcrc12 GPU0
2026-09-28 07:00 JST — H7 launched on fvcrc10 GPU3
2026-09-28 09:51 JST — queue: probe_order on 8 ladder checkpoints
2026-09-28 09:52 JST — PO_T7s2 launched on fvcrc10 GPU0
2026-09-28 10:01 JST — probe_order queue stopped after PO_T7s2: recency task shows no recency preference even for RoPE T (chance-level, P(last)≈P(first)); task redesigned (code reassignment). T7s2 result kept.
2026-09-28 10:03 JST — queue: probe_order v2 (reassign / keyed) on 8 ladder checkpoints
2026-09-28 10:11 JST — PO_T7s2 launched on fvcrc10 GPU0
2026-09-28 10:13 JST — PO_H7s2 launched on fvcrc10 GPU1
2026-09-28 10:15 JST — PO_T7s3e launched on fvcrc10 GPU2
2026-09-28 10:17 JST — PO_H7s3e launched on fvcrc10 GPU3
2026-09-28 10:19 JST — PO_T7s3m launched on fvcrc12 GPU0
2026-09-28 10:21 JST — PO_H7s3m launched on fvcrc10 GPU0
2026-09-28 10:23 JST — PO_T7 launched on fvcrc10 GPU0
2026-09-28 10:26 JST — PO_H7 launched on fvcrc12 GPU1
2026-09-28 10:46 JST — queue: probe_channel (full vs reconly) on H7s2/H7s3m/H7
2026-09-28 10:46 JST — PC_H7s2 launched on fvcrc10 GPU0
2026-09-28 10:48 JST — PC_H7s3m launched on fvcrc10 GPU1
2026-09-28 10:51 JST — PC_H7 launched on fvcrc10 GPU2
2026-09-28 10:53 JST — queue: probe_order on S5 SWA-128 RoPE/NoPE/full
2026-09-28 10:54 JST — PO_S5rope launched on fvcrc10 GPU3
2026-09-28 10:56 JST — PO_S5nope launched on fvcrc10 GPU3
2026-09-28 10:58 JST — PO_S5full launched on fvcrc10 GPU3
2026-09-28 11:07 JST — queue: probe_order S5 rerun (use_cache=False fix)
2026-09-28 11:07 JST — PO_S5rope launched on fvcrc10 GPU0
2026-09-28 11:09 JST — PO_S5nope launched on fvcrc10 GPU0
2026-09-28 11:12 JST — PO_S5full launched on fvcrc10 GPU1
2026-09-28 11:15 JST — queue: probe_attn on H7s2/H7s3m/H7/T7s2/T7
2026-09-28 11:16 JST — PA_H7s2 launched on fvcrc10 GPU0
2026-09-28 11:18 JST — PA_H7s3m launched on fvcrc10 GPU1
2026-09-28 11:20 JST — PA_H7 launched on fvcrc10 GPU0
2026-09-28 11:23 JST — PA_T7s2 launched on fvcrc10 GPU1
2026-09-28 11:25 JST — PA_T7 launched on fvcrc10 GPU0
2026-09-28 11:40 JST — queue: probe_order S5 rerun #2 (explicit attention_mask)
2026-09-28 11:42 JST — PO_S5rope launched on fvcrc10 GPU0
2026-09-28 11:45 JST — PO_S5nope launched on fvcrc10 GPU1
2026-09-28 11:47 JST — PO_S5full launched on fvcrc10 GPU2
2026-09-28 12:05 JST — queue: survey (5 downloaded hybrids + Qwen3.5-4B, PROBE_N=60)
2026-09-28 12:06 JST — SV_granite_4_0_h_micro launched on fvcrc10 GPU3
2026-09-28 12:08 JST — SV_Falcon_H1_1_5B_Base launched on fvcrc12 GPU0
2026-09-28 12:10 JST — SV_Nemotron_H_8B_Base_8K launched on fvcrc12 GPU1
2026-09-28 12:13 JST — SV_granite_4_0_h_tiny launched on fvcrc12 GPU1
2026-09-28 12:15 JST — SV_Bamba_9B_v2 launched on fvcrc10 GPU0
2026-09-28 12:17 JST — SV_Qwen3_5_4B launched on fvcrc10 GPU1
2026-09-28 12:19 JST — survey restarted: PROBE_GAPS=4,32 (torch-fallback Mamba OOM at 7k tokens), PROBE_TRC=0 (native nemotron_h); earlier partial files in results/probe_order/survey_aborted/
2026-09-28 12:19 JST — SV_granite_4_0_h_micro launched on fvcrc10 GPU0
2026-09-28 12:21 JST — SV_Falcon_H1_1_5B_Base launched on fvcrc10 GPU1
2026-09-28 12:23 JST — SV_Nemotron_H_8B_Base_8K launched on fvcrc10 GPU2
2026-09-28 12:26 JST — SV_granite_4_0_h_tiny launched on fvcrc10 GPU3
2026-09-28 12:28 JST — SV_Bamba_9B_v2 launched on fvcrc12 GPU0
2026-09-28 12:30 JST — SV_Qwen3_5_4B launched on fvcrc12 GPU1
2026-09-28 13:02 JST — queue: ctx_ablation on Pile triplet + scale controls
2026-09-28 13:02 JST — CX_ launched on fvcrc10 GPU0
2026-09-28 13:03 JST — queue: ctx_ablation on Pile triplet + scale controls (retry, correct tags)
2026-09-28 13:03 JST — CX_PPT launched on fvcrc10 GPU0
2026-09-28 13:05 JST — CX_PPH launched on fvcrc10 GPU1
2026-09-28 13:08 JST — CX_PPR launched on fvcrc10 GPU2
2026-09-28 13:10 JST — CX_PY14 launched on fvcrc10 GPU3
2026-09-28 13:12 JST — CX_PY28 launched on fvcrc10 GPU0
2026-09-28 13:15 JST — CX_M2_13 launched on fvcrc12 GPU0
2026-09-28 13:18 JST — queue: probe_order Llama-2-7B RoPE vs DroPE (transformer DroPE control)
2026-09-28 13:18 JST — PO_L2rope launched on fvcrc10 GPU3
2026-09-28 13:20 JST — PO_L2drope launched on fvcrc10 GPU1
2026-09-28 13:25 JST — queue: L2drope retry (snapshot dir on PYTHONPATH for custom_models)
2026-09-28 13:26 JST — PO_L2drope launched on fvcrc10 GPU0
