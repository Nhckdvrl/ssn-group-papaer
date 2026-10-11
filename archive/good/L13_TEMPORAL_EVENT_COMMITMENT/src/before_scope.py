"""What counts as an in-scope natural `before`-clause for L13.

The scientific question is whether the realization of the subordinate event of a
`before`-clause survives into an emitted event structure. That question only
arises when the subordinate clause denotes a *particular eventuality whose
realization is at issue*. The following are therefore out of scope, and are
excluded before adjudication rather than adjudicated and discarded:

  PP / adverbial `before`      "before the trial", "before 1880", "before then"
  forensic / spatial `before`  "before the Court", "presented before the Conqueror"
  generic / habitual           "Match tickets go on sale two weeks before a game."
  deontic / procedural present "You need a warrant before you can search a phone."
  imperative / second person   "Write the unit tests before you write your code."
  irrealis matrix              "He might have to bring the house up to code before ..."

In scope: a finite subordinate clause with a past-tense or `could/would` verb, in
a past-tense narrative or reportive matrix.
"""
import re

IRREGULAR = (
    "was were had did said went came saw took got made knew thought found gave told "
    "became left felt put brought began kept held wrote stood heard let meant set met "
    "ran paid sat spoke lay led grew lost fell sent built understood drew broke spent "
    "cut rose drove bought wore chose sought caught taught fought threw shot hid shone "
    "arose beat bit blew bore burst dealt dug drank drove ate fed fled flew forgot "
    "froze hung hurt knelt lent lit meant rode rang sank sold shook shrank sang slept "
    "slid spread sprang stole stuck struck swam swore swung tore woke wound withdrew"
).split()

PAST_VERB = re.compile(
    r"\b(?:\w+ed|" + "|".join(IRREGULAR) + r")\b", re.I
)
SUB_CLAUSE = re.compile(
    r"\bbefore\s+((?:the|a|an|his|her|their|its|my|our|I|we|he|she|they|it|[A-Z]\w*)"
    r"(?:\s+\w+){0,4}?\s+(?:could|would|" + r"\w+ed|" + "|".join(IRREGULAR) + r"))\b",
    re.I,
)
OUT_OF_SCOPE = re.compile(
    r"\b(?:you|your|one|we all)\b.*\bbefore\b|"          # second person / advisory
    r"\bbefore\s+(?:you|your)\b|"
    r"\b(?:must|should|need to|needs to|have to|has to|can|may|might|will|shall)\b"
    r"[^.]*\bbefore\b|"                                   # deontic / future matrix
    r"\bbefore\s+the\s+(?:court|judge|justices|committee|board|house|senate)\b|"
    r"^\s*(?:[A-Z][a-z]+\s+)?(?:write|do|make|check|read|see|note|try|use|take)\b",
    re.I,
)
QUESTION = re.compile(r"\?")


def in_scope(sentence):
    """(bool, reason) — whether the sentence carries an in-scope `before`-clause."""
    if QUESTION.search(sentence):
        return False, "question"
    if OUT_OF_SCOPE.search(sentence):
        return False, "generic_deontic_or_forensic"
    m = SUB_CLAUSE.search(sentence)
    if not m:
        return False, "no_finite_past_subordinate_clause"
    matrix = sentence[: m.start()]
    if not PAST_VERB.search(matrix):
        return False, "matrix_not_past"
    return True, m.group(1)
