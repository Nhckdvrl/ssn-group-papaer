# E000c — Released coreference and context visibility

Parsed 1,198 source Coreference frames into 1,328 complete mention spans and
142 equivalence classes (largest: 169 mentions). Each edge connects the complete
`Current` and `Coreferent` FE spans. The frame target can be just a head and is
not substituted for `Current`; a multi-node phrase is never split into unrelated
individual mentions. Source edges, NI equivalence candidates and hashes are saved.

Of 256 linked NI records (245 DNI + 11 INI), 178 link spans exactly match a source
coreference mention. The other 78 retain their original source span without
heuristic head/substring expansion; this is conservative incomplete coverage.

102 original link spans are in the target sentence. Counting source-global
equivalents raises the number to 116: 14 cases have a nonlocal original link but
a globally equivalent mention in the target sentence. **Neither count establishes
what is identifiable from the target sentence alone.** The annotation guide §1.2
allows equivalence based on identities revealed later in the story and explicitly
discusses Henderson / Murillo. Global identity must not leak into a local-evidence
gold standard.

These are source-graph properties, not LLM findings or new semantic annotations.
E001a does not score filler recovery, so its frozen inputs/labels are unchanged.
Any later extraction study must distinguish original-link visibility, alternative
mention visibility, and whether the available window establishes their identity.
