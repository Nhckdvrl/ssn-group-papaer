# Code provenance

Each experiment run records the SHA256 of the engine that produced it (`script_sha256` in its run file).
The engines in `code/` differ from those recorded hashes in two ways, neither of which changes the computation for
the models already run:

1. After the Qwen3, Mistral and Llama runs, the engines of E119/E120/E121/E123 gained a Gemma-2 branch (import of the
   Gemma-2 attention module and revision entries) and call the native attention function with keyword arguments,
   because Gemma-2 orders `dropout` before `scaling`.
2. For this package, machine-specific defaults were replaced (model paths, the SST-5 cache path, which can be set
   with `SST5_ARROW_DIR`), and the call that recorded the git commit was removed.

Engine hashes recorded in the runs:

- e120: 5073708206cc, b4b155bfea8f
- e121: 5f96952a6cae, bae20c8132c7
- e122: 1f9455fb905f
- e123: 95a574892e76, b5aa38385e4c
- e124: ea65caf59d2b
- e125: 75f7566582cb
- e126: ad2c6f7af7ab
- e127: cef7952d4ef5
- e128: f0a0146708e1
- e129: a177434cf425
- e130: 7ef59b3f853e
- e131: 75290f9f3d35, a4285fe0eba3, b145f6278e92
- e132: f2167a1d0c45

Hashes of the files in this package and of their repository versions:

| File | Repository | Package |
|---|---|---|
| `e56_query_adapter.py` | `366feef792ca` | `a04e4122fe89` |
| `e109_reconstruction_audit.py` | `205d6c4a54c6` | `f50279620e5d` |
| `e115_llama_native_mechanism.py` | `ff749f370b44` | `73081e29dbf0` |
| `e118_criterion_code_feature_crossing.py` | `9a3984b35773` | `3be2da2fb73f` |
| `e118_mistral_materials.py` | `eea5590ce316` | `1e21abb4e6c0` |
| `e119_criterion_scale.py` | `bb65c208f6a3` | `caadc0d4afc6` |
| `e119_native_scale.py` | `7079be936f1e` | `44d6d247f962` |
| `e120_operation_necessity.py` | `5073708206cc` | `700b84edb130` |
| `e121_sst_materials.py` | `f02104a87b9e` | `f2fb86f853de` |
| `e121_natural_sentiment_mechanism.py` | `bae20c8132c7` | `34143851b13f` |
| `e122_source_preserving_formation.py` | `1f9455fb905f` | `20566e7eea1f` |
| `e123_natural_source_function_policy.py` | `b5aa38385e4c` | `5296ad70cbfa` |
| `e123_wave_report.py` | `9e5cf06cca0e` | `b41054d62e04` |
| `e125_public_output_schema_coordination.py` | `75f7566582cb` | `0e35868b99cf` |
| `e125_swapped_minus_unrelated.py` | `356fb9063eed` | `356fb9063eed` |
| `e127_shared_output_cache_composition.py` | `cef7952d4ef5` | `e599bdbbde90` |
| `e131_dispatch.py` | `5abd14f91ac0` | `5abd14f91ac0` |
| `e131_mechanism.py` | `75290f9f3d35` | `1b29df2f6aff` |
| `e131_native.py` | `a4285fe0eba3` | `decc76ed10f2` |
| `e131_function.py` | `b145f6278e92` | `eb774e073d6d` |
| `e132_cross_source_edges.py` | `f2167a1d0c45` | `f2167a1d0c45` |
| `e132_merge.py` | `bb5dd8712796` | `bb5dd8712796` |
| `run_gemma.py` | `d7e0fdbb9e1b` | `d7e0fdbb9e1b` |
| `gemma_full_output.py` | `fdf099d2220d` | `fdf099d2220d` |
| `flip_single_source.py` | `a8da09cbcb77` | `a8da09cbcb77` |
| `instruction_control.py` | `e50e634e7a34` | `e50e634e7a34` |
| `paper_figures_v2.py` | `044f6625f9be` | `044f6625f9be` |
