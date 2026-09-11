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
    "b41": ("the technician", "calibrate the spectrometer"),
    "b42": ("Dara", "score the penalty"),
    "b43": ("the witness", "finish her testimony"),
    "b44": ("the paramedics", "reach the casualty"),
    "b45": ("Tobias", "change his currency"),
    "b46": ("the chef", "plate the dessert"),
    "b47": ("the intern", "merge the branch"),
    "b48": ("Lucia", "hand back the marked essays"),
    "b49": ("the trader", "close the position"),
    "b50": ("Nadia", "tell her father the news"),
    "b51": ("the roofers", "seal the skylight"),
    "b52": ("the photographer", "file the picture"),
    "b53": ("the vet", "treat the last calf"),
    "b54": ("the garrison", "surrender the fort"),
    "b55": ("the quartet", "play the encore"),
    "b56": ("Sam", "refund the customer"),
    "b57": ("the driver", "deliver the last parcel"),
    "b58": ("the rangers", "relocate the nest"),
    "b59": ("the team", "lift the mosaic"),
    "b60": ("the translator", "deliver the manuscript"),
    "b61": ("the mechanic", "replace the valve"),
    "b62": ("the student", "titrate the sample"),
    "b63": ("Dr Okafor", "sign the discharge papers"),
    "b64": ("Farid", "collect his residence card"),
    "b65": ("the couple", "exchange their vows"),
    "b66": ("the crew", "haul in the net"),
    "b67": ("the returning officer", "announce the result"),
    "b68": ("the understudy", "learn the part"),
    "b69": ("the dentist", "fit the crown"),
    "b70": ("the helicopter", "lift the climber off the ridge"),
    "b71": ("the conservator", "repair the binding"),
    "b72": ("the founders", "file the patent"),
    "b73": ("the volunteers", "distribute the last blankets"),
    "b74": ("the observatory", "record the transit"),
    "b75": ("Bea", "plant the bulbs"),
    "b76": ("the admin", "rotate the keys"),
    "b77": ("Kofi", "qualify for the final"),
    "b78": ("the port", "clear the container"),
    "b79": ("the crew", "shoot the final scene"),
    "b80": ("the clinic", "finish the second round"),
}

# purpose infinitive: non-veridical, and marked by nothing at all.
# "Maya was there to submit the application" does not entail that she did.
# Shares its matrix clause with `about_to`, so the only difference is whether
# non-realization is marked (aspectually) or carried by the construction alone.
EXT_GOLD = {
    "about_to": "NOT_DETERMINED",
    "before_modal": "NO",
    "purpose": "NOT_DETERMINED",
    "before_post": "NOT_DETERMINED",
}


def cap(s):
    return s[0].upper() + s[1:]


PLURAL = {"b22", "b31", "b44", "b51", "b58", "b65", "b72", "b73"}


def ext_passages(base):
    # E12/E15 run on the original 40 bases only; bases without a hand-written
    # bare-infinitive decomposition contribute no extension conditions.
    if base["id"] not in DECOMP:
        return {}
    subj, vp = DECOMP[base["id"]]
    be = "were" if base["id"] in PLURAL else "was"
    return {
        "about_to": f"{cap(subj)} {be} about to {vp} when {base['main']}.",
        "before_modal": f"{cap(base['main'])} before {subj} could {vp}.",
        "purpose": f"{cap(subj)} {be} there to {vp} when {base['main']}.",
        # the post-posed order, which dominates natural English and forms a
        # one-word minimal pair with `before_modal`
        "before_post": f"{cap(base['main'])} before {base['sub']}.",
    }
