# E02 research log — held-out readout diagnosis

## Observation

On 60 new matched bases, the E01 wording reproduced: positive definition 16/60, positive fact 60/60 correct; exception definition 60/60, exception fact 0/60 correct. With the prespecified scope-clean readouts, positive definition became 60/60 correct, while positive fact fell to 11/60 correct (49/60 incorrectly asserted transfer). Exception definition stayed 60/60, and exception fact rose only to 1/60 correct. All 480 responses parsed. Frame-specific scope-clean fact-positive accuracy was 7/20, 4/20, and 0/20; scope-clean fact-exception accuracy was 1/20, 0/20, and 0/20. The matched definition-minus-fact assertion differences under scope-clean wording were 11/60 for positive and 1/60 for exception.

## Validity

The held-out seed and the two readout variants were committed before inference. Within every base, the core relation, World A extension, World B event, and role sentence were held fixed. Question polarity and A/B keys were balanced within each framing. E01's 144/144 control pass and E02's zero parse failures rule out a basic inability to read the invented relation or the two-world setup. The remaining identification problem is **scope of the bare biconditional itself**: a sentence of the form “An object is a dax iff ...” is grammatically global, while the fact-role preamble asks it to function as a World A summary. E02 cannot show whether the model's cross-world use reflects an untyped association or the natural global reading of the sentence.

## Interpretation candidates

1. **Query-cue dominance:** “Nothing states whether” makes both roles favor uncertainty; removing it makes both roles favor transfer. This is directly supported by the held-out within-item contrast, without proving the mechanism.
2. **Global-biconditional reading:** the unqualified relation acts as a general rule despite the World A report frame, especially in contradiction judgments. This predicts that explicitly delimiting its World A scope in the framing, without changing the relation sentence, would sharply reduce fact transfer.
3. **Role-insensitive association:** the model uses the same relation similarly under both discourse roles; even clearer fact scope would fail to restore the distinction. E02 does not separate this from candidate 2.

## Knowledge consequence

E01's apparent definition-versus-fact positive interaction was not a stable estimate of role-sensitive updating: one uncertainty clause moved both roles in opposite correctness directions. No robust typed-update claim follows. The stable exception failure is a real behavioral observation on held-out items, but it may arise from an ambiguous global-looking proposition; it is not yet an independently validated new scientific law.

## Next decisive experiment

If continuing S12, freeze one final held-out batch crossing the existing natural framing with a single **explicit scope** framing: a shared-language terminology rule versus a World-A-only report that explicitly gives no rule for World B. Keep the same core sentence and World A inventory and use the E02 scope-clean readouts. If only the explicit wording recovers the crossed pattern, S12 as a robust natural-role question should be killed; if even explicit scope fails while controls pass, that supports a narrower role-insensitivity claim. This is a construct-repair gate, not a search for the best prompt.

## Current verdict

**continue original RQ** for one prespecified scope-identification test. The current data do not establish typed updating, untyped updating, or a stronger replacement RQ.

## Focused nearest-prior check

[Fonseca & Cohen 2024](https://arxiv.org/abs/2311.08704) and [Lepori et al. 2026](https://aclanthology.org/2026.acl-long.676/) do not test this role-matched world persistence contrast. [Tessler et al., *Exceptions, Instantiations, and Overgeneralization*](https://direct.mit.edu/coli/article/50/4/1211/123791/Exceptions-Instantiations-and-Overgeneralization) studies how LMs process generics and exceptions, so a generic “LMs overgeneralize a rule” headline would be too close to existing work. The unresolved issue here is the grammatical scope versus discourse-role identification, not exception overgeneralization alone.
