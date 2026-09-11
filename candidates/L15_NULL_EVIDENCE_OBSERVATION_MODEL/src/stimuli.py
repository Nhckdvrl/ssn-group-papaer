"""L15 stimulus construction.

Deterministic, programmatic templates. No LLM generates any load-bearing item or
gold value (DATA_AND_GOLD.md section 7).

Every item states, explicitly and inside the item text:
  - the prior p = P(H);
  - the detection probability s = P(D|H);
  - the false-positive rate f = P(D|~H), which is 0 in the primary grid.
No item requires a hidden domain prior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# --- primary grid (DATA_AND_GOLD.md section 2) --------------------------------

PRIORS = (0.2, 0.5, 0.8)
SENSITIVITIES = (0.05, 0.25, 0.50, 0.75, 0.95)
FALSE_POSITIVE = 0.0
THRESHOLD = 0.20


def posterior_null(p: float, s: float, f: float = FALSE_POSITIVE) -> float:
    """P(H | no detection) under the stated observation model."""
    num = p * (1.0 - s)
    den = num + (1.0 - p) * (1.0 - f)
    return num / den


def posterior_positive(p: float, s: float, f: float = FALSE_POSITIVE) -> float:
    """P(H | detection). Degenerate at 1.0 when f = 0; used as a sanity control."""
    num = p * s
    den = num + (1.0 - p) * f
    return num / den if den > 0 else float("nan")


def likelihood_null_given_h(s: float) -> float:
    """P(no detection | H) = 1 - s."""
    return 1.0 - s


@dataclass(frozen=True)
class Scenario:
    sid: str
    frame: str                 # access | search | monitoring | diagnostic
    transfer: bool             # True for the medical frame (transfer condition only)
    setting: str               # scene-setting sentence, no probabilities
    hypothesis: str            # "Alice entered the building last night"
    hyp_past: str              # "Alice did enter the building last night"
    hyp_neg: str               # "Alice did not enter the building last night"
    procedure: str             # "the camera system"
    detect_pos: str            # "records her"       -> "If H, <procedure> <detect_pos> 95% of the time"
    detect_miss: str           # 3rd person: "... the other 5% of the time it <detect_miss>"
    miss_bare: str             # bare VP: "would nevertheless <miss_bare>"
    report_null: List[str]     # two surface wordings of the same null outcome
    report_pos: str
    question: str              # "the probability that Alice entered the building last night"
    action: str                # the downstream action gated on the threshold


SCENARIOS: List[Scenario] = [
    # ---------------- access / monitoring of people and vehicles ----------------
    Scenario(
        sid="acc_camera",
        frame="access",
        transfer=False,
        setting="A building entrance has an automatic camera system that looks for specific people.",
        hypothesis="Alice entered the building last night",
        hyp_past="Alice did enter the building last night",
        hyp_neg="Alice did not enter the building last night",
        procedure="the camera system",
        detect_pos="records her",
        detect_miss="does not record her at all",
        miss_bare="produce no record of her",
        report_null=[
            "The camera system reports no record of Alice.",
            "Alice was not detected by the camera system.",
        ],
        report_pos="The camera system reports a record of Alice.",
        question="the probability that Alice entered the building last night",
        action="open an access investigation",
    ),
    Scenario(
        sid="acc_badge",
        frame="access",
        transfer=False,
        setting="A server room is protected by a badge reader that logs entries.",
        hypothesis="contractor B-14 entered the server room on Tuesday",
        hyp_past="contractor B-14 did enter the server room on Tuesday",
        hyp_neg="contractor B-14 did not enter the server room on Tuesday",
        procedure="the badge reader",
        detect_pos="logs the entry",
        detect_miss="logs nothing at all",
        miss_bare="log nothing",
        report_null=[
            "The badge reader shows no entry for contractor B-14 on Tuesday.",
            "No Tuesday entry for contractor B-14 was found in the badge log.",
        ],
        report_pos="The badge reader shows an entry for contractor B-14 on Tuesday.",
        question="the probability that contractor B-14 entered the server room on Tuesday",
        action="revoke the contractor's access pending review",
    ),
    Scenario(
        sid="acc_anpr",
        frame="access",
        transfer=False,
        setting="A toll gate uses automatic plate recognition on every passing vehicle.",
        hypothesis="van XG-7741 passed the toll gate on Friday",
        hyp_past="van XG-7741 did pass the toll gate on Friday",
        hyp_neg="van XG-7741 did not pass the toll gate on Friday",
        procedure="the plate recognition system",
        detect_pos="reads the plate",
        detect_miss="fails to read the plate entirely",
        miss_bare="produce no reading of the plate",
        report_null=[
            "The plate recognition system has no Friday reading for van XG-7741.",
            "Van XG-7741 does not appear in Friday's plate recognition output.",
        ],
        report_pos="The plate recognition system has a Friday reading for van XG-7741.",
        question="the probability that van XG-7741 passed the toll gate on Friday",
        action="bill the operator for the Friday crossing",
    ),
    # ---------------- search over a corpus / database ----------------
    Scenario(
        sid="srch_patent",
        frame="search",
        transfer=False,
        setting="An engineer runs a keyword search over a patent archive.",
        hypothesis="a patent covering this technique exists in the archive",
        hyp_past="such a patent does exist in the archive",
        hyp_neg="no such patent exists in the archive",
        procedure="this keyword search",
        detect_pos="returns it",
        detect_miss="returns nothing for it",
        miss_bare="return nothing",
        report_null=[
            "The search returned no matching patent.",
            "The search came back empty.",
        ],
        report_pos="The search returned a matching patent.",
        question="the probability that a patent covering this technique exists in the archive",
        action="file the application without a further freedom-to-operate check",
    ),
    Scenario(
        sid="srch_ticket",
        frame="search",
        transfer=False,
        setting="A support agent queries the ticket system for a customer's earlier complaint.",
        hypothesis="the customer filed this complaint earlier",
        hyp_past="the customer did file this complaint earlier",
        hyp_neg="the customer never filed this complaint",
        procedure="this query",
        detect_pos="retrieves the ticket",
        detect_miss="retrieves nothing",
        miss_bare="retrieve nothing",
        report_null=[
            "The query returned no earlier ticket for this customer.",
            "No earlier ticket for this customer came back from the query.",
        ],
        report_pos="The query returned an earlier ticket for this customer.",
        question="the probability that the customer filed this complaint earlier",
        action="treat the case as a first-time complaint",
    ),
    Scenario(
        sid="srch_phrase",
        frame="search",
        transfer=False,
        setting="An analyst runs a full-text search for a phrase across a document set.",
        hypothesis="the phrase occurs somewhere in the document set",
        hyp_past="the phrase does occur in the document set",
        hyp_neg="the phrase does not occur anywhere in the document set",
        procedure="this full-text search",
        detect_pos="finds an occurrence",
        detect_miss="finds nothing",
        miss_bare="find nothing",
        report_null=[
            "The full-text search found no occurrence of the phrase.",
            "The full-text search produced zero hits for the phrase.",
        ],
        report_pos="The full-text search found an occurrence of the phrase.",
        question="the probability that the phrase occurs somewhere in the document set",
        action="certify the document set as free of the phrase",
    ),
    # ---------------- system / environmental monitoring ----------------
    Scenario(
        sid="mon_leak",
        frame="monitoring",
        transfer=False,
        setting="A pipeline section is watched by an acoustic leak sensor.",
        hypothesis="this section is leaking",
        hyp_past="this section is indeed leaking",
        hyp_neg="this section is not leaking",
        procedure="the acoustic sensor",
        detect_pos="raises an alarm",
        detect_miss="stays silent",
        miss_bare="stay silent",
        report_null=[
            "The acoustic sensor raised no alarm for this section.",
            "No alarm for this section came from the acoustic sensor.",
        ],
        report_pos="The acoustic sensor raised an alarm for this section.",
        question="the probability that this section is leaking",
        action="send a crew to inspect the section",
    ),
    Scenario(
        sid="mon_intrusion",
        frame="monitoring",
        transfer=False,
        setting="A network is watched by an intrusion detection system.",
        hypothesis="an intrusion occurred last month",
        hyp_past="an intrusion did occur last month",
        hyp_neg="no intrusion occurred last month",
        procedure="the intrusion detection system",
        detect_pos="flags it",
        detect_miss="flags nothing",
        miss_bare="flag nothing",
        report_null=[
            "The intrusion detection system flagged nothing last month.",
            "Last month produced no intrusion alerts.",
        ],
        report_pos="The intrusion detection system flagged an intrusion last month.",
        question="the probability that an intrusion occurred last month",
        action="declare a security incident",
    ),
    Scenario(
        sid="mon_defect",
        frame="monitoring",
        transfer=False,
        setting="A production batch passes through an automated visual inspection station.",
        hypothesis="this batch contains a defective unit",
        hyp_past="this batch does contain a defective unit",
        hyp_neg="this batch contains no defective unit",
        procedure="the inspection station",
        detect_pos="rejects the batch",
        detect_miss="passes the batch without comment",
        miss_bare="report no defect",
        report_null=[
            "The inspection station reported no defect in this batch.",
            "This batch came through inspection with nothing reported.",
        ],
        report_pos="The inspection station reported a defect in this batch.",
        question="the probability that this batch contains a defective unit",
        action="hold the batch for manual re-inspection",
    ),
    # ---------------- diagnostic frame: TRANSFER CONDITION ONLY ----------------
    Scenario(
        sid="diag_infection",
        frame="diagnostic",
        transfer=True,
        setting="A clinic screens a patient with a rapid test.",
        hypothesis="the patient has the infection",
        hyp_past="the patient does have the infection",
        hyp_neg="the patient does not have the infection",
        procedure="the rapid test",
        detect_pos="comes back positive",
        detect_miss="comes back negative anyway",
        miss_bare="come back negative",
        report_null=[
            "The rapid test came back negative.",
            "The rapid test did not come back positive.",
        ],
        report_pos="The rapid test came back positive.",
        question="the probability that the patient has the infection",
        action="start treatment",
    ),
    Scenario(
        sid="diag_fracture",
        frame="diagnostic",
        transfer=True,
        setting="A radiographer images a patient's wrist to look for a hairline fracture.",
        hypothesis="the wrist has a hairline fracture",
        hyp_past="the wrist does have a hairline fracture",
        hyp_neg="the wrist has no hairline fracture",
        procedure="this imaging protocol",
        detect_pos="shows the fracture",
        detect_miss="shows nothing",
        miss_bare="show nothing",
        report_null=[
            "The images show no fracture.",
            "Nothing showed up on the images.",
        ],
        report_pos="The images show a fracture.",
        question="the probability that the wrist has a hairline fracture",
        action="immobilise the wrist in a cast",
    ),
    Scenario(
        sid="diag_screen",
        frame="diagnostic",
        transfer=True,
        setting="A laboratory screens a blood sample for a specific antibody.",
        hypothesis="the antibody is present in the sample",
        hyp_past="the antibody is indeed present in the sample",
        hyp_neg="the antibody is absent from the sample",
        procedure="this assay",
        detect_pos="reports the antibody",
        detect_miss="reports nothing",
        miss_bare="report nothing",
        report_null=[
            "The assay reported no antibody.",
            "The assay result was blank for the antibody.",
        ],
        report_pos="The assay reported the antibody.",
        question="the probability that the antibody is present in the sample",
        action="record the sample as antibody-positive for the registry",
    ),
]


def pct(x: float) -> str:
    """Render a probability as a percentage without spurious precision."""
    v = x * 100.0
    return f"{v:g}%"


def build_items() -> List[dict]:
    """The full primary grid: 12 scenarios x 3 priors x 5 sensitivities = 180 items."""
    items: List[dict] = []
    for sc in SCENARIOS:
        for p in PRIORS:
            for s in SENSITIVITIES:
                items.append(
                    {
                        "item_id": f"{sc.sid}|p{int(round(p * 100)):02d}|s{int(round(s * 100)):02d}",
                        "scenario": sc.sid,
                        "frame": sc.frame,
                        "transfer": sc.transfer,
                        "p": p,
                        "s": s,
                        "f": FALSE_POSITIVE,
                        "threshold": THRESHOLD,
                        "gold_p1": likelihood_null_given_h(s),
                        "gold_p2": posterior_null(p, s),
                        "gold_p2_pos": posterior_positive(p, s),
                        "gold_p0": p,
                        "gold_p3": "yes" if posterior_null(p, s) > THRESHOLD else "no",
                    }
                )
    return items
