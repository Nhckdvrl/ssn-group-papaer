"""E12 extension conditions on the same 40 bases.

Two new conditions test whether the collapse is about `before` specifically, and
whether *lexical marking* of non-veridicality is what E08 showed matters — now
with matched lexical content inside the controlled set.

  about_to     "<Subj> was about to <VP> when <main>."
               An unmarked non-veridical temporal construction that is NOT a
               `before`-clause. Gold: NOT_DETERMINED.
  before_modal "<Main> before <Subj> could <VP>."
               The modally MARKED form that dominates natural text (E08).
               Gold: NO.

`subject` and `vp_bare` are the bare-infinitive decomposition of each base's
subordinate clause, written out rather than derived, so irregular verbs and
idiomatic objects stay correct.
"""

# base_id -> (subject, bare VP)
DECOMP = {
    "b01": ("Maya", "submit the application"),
    "b02": ("Daniel", "board the train"),
    "b03": ("Lena", "pay the deposit"),
    "b04": ("Omar", "sign the contract"),
    "b05": ("the nurse", "give the patient the injection"),
    "b06": ("Priya", "catch the ferry"),
    "b07": ("the team", "release the update"),
    "b08": ("Marcus", "return the library book"),
    "b09": ("Sofia", "finish the marathon"),
    "b10": ("the journalist", "publish the article"),
    "b11": ("Ken", "renew his passport"),
    "b12": ("the startup", "ship the prototype"),
    "b13": ("Elena", "hand in her thesis"),
    "b14": ("Rosa", "mail the package"),
    "b15": ("the committee", "approve the budget"),
    "b16": ("Ahmed", "sell his car"),
    "b17": ("Nina", "take the exam"),
    "b18": ("the crew", "put out the fire"),
    "b19": ("Diego", "delete the file"),
    "b20": ("the mayor", "sign the order"),
    "b21": ("Yuki", "collect the prize"),
    "b22": ("the students", "stage the play"),
    "b23": ("Carla", "withdraw the cash"),
    "b24": ("the surgeon", "perform the operation"),
    "b25": ("Tomas", "repay the loan"),
    "b26": ("the village", "rebuild the bridge"),
    "b27": ("Hana", "register for the course"),
    "b28": ("the company", "pay the fine"),
    "b29": ("Ivan", "reach the summit"),
    "b30": ("Grace", "adopt the dog"),
    "b31": ("the engineers", "fix the leak"),
    "b32": ("Leo", "apologise to his sister"),
    "b33": ("the auction house", "sell the painting"),
    "b34": ("Anya", "finish the report"),
    "b35": ("the farmer", "harvest the wheat"),
    "b36": ("Peter", "book the flight"),
    "b37": ("the council", "demolish the old mill"),
    "b38": ("Mira", "have her son vaccinated"),
    "b39": ("the archivist", "digitise the manuscript"),
    "b40": ("Ravi", "cancel the subscription"),
}

EXT_GOLD = {"about_to": "NOT_DETERMINED", "before_modal": "NO"}


def cap(s):
    return s[0].upper() + s[1:]


def ext_passages(base):
    subj, vp = DECOMP[base["id"]]
    return {
        "about_to": f"{cap(subj)} was about to {vp} when {base['main']}.",
        "before_modal": f"{cap(base['main'])} before {subj} could {vp}.",
    }
