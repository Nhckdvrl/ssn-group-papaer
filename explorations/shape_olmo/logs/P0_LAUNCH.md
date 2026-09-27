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
