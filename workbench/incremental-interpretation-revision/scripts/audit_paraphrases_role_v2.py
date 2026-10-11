"""T4 clarification: grammatical voice alone does not establish participant-role error."""
import audit_paraphrases

audit_paraphrases.PROMPT += '''
Important role clarification: grammatical subject and semantic agent are different.
Do not infer GP_MISREADING solely from missing passive auxiliaries or active morphology.
Causative/inchoative alternating verbs can have a theme/patient as the subject of an
active intransitive clause: e.g., "the department merged" can faithfully express that
the department underwent a merger described by "the department was merged".
Use the actual lexical interpretation and expressed arguments. Classify a wrong role
only when the paraphrase explicitly assigns that role, not because it uses active voice.
An ordinary faithful inchoative reformulation may be CORRECT_ROLES. If the paraphrase
is genuinely ambiguous between faithful and wrong-role readings, classify OTHER and
explain the ambiguity; do not confidently assign an unstated agent or rescue missing events.
'''

if __name__ == '__main__':
    audit_paraphrases.main()
