"""E97 original Belief-R text with one explicit concise-answer instruction."""
from belief_r_credit import FORMAT

INSTRUCTION = 'Do not provide explanations; write only Final Answer [a], Final Answer [b], or Final Answer [c].'


def prepare(row, tok):
    user = row['question']+'\n\n'+FORMAT+'\n'+INSTRUCTION
    rendered = tok.apply_chat_template([dict(role='user', content=user)], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=False)
    return dict(row=row, prompt=rendered, cap=64)
