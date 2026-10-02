"""Fixed E29 interventions on released EPITOME wording; no model calls."""
import re

ACCESS = re.compile(r'I have (?:looked at|met|listened to) [123] of the 3 [^.]+\.')

def variants(prompt):
    assert re.search(r'Q:Do you think .+ knows exactly ', prompt)
    matches = list(ACCESS.finditer(prompt))
    assert len(matches) == 1, prompt
    access = matches[0]
    quote_end = prompt.index('"\nQ:', access.end())
    cut = prompt[:access.end()] + prompt[quote_end:]
    assert cut != prompt
    assert cut.split('\nQ:', 1)[1] == prompt.split('\nQ:', 1)[1]
    assert ACCESS.search(cut).group() == access.group()
    negative = re.sub(r'(Q:Do you think .+?) knows exactly ',
                      r'\1 does not know exactly ', prompt, count=1)
    assert negative != prompt
    return {'parent': prompt,
            'role': 'Answer about what the speaker knows, not about how much information the listener receives from the utterance.\n\n' + prompt,
            'access-only': cut, 'negative': negative}
