"""
S03 / E01 — build exact-prefix goal-intervention stimuli.

Design contract (frozen by the S03 identification requirement):

  * Within a matched pair the ASSISTANT PREFIX is token-for-token identical.
  * Only the USER GOAL changes, flipping whether the replayed prefix already
    satisfies the request.
  * The competitor token at the decision point is the SAME token in both
    conditions (it is the first token of the correct missing continuation,
    taken from the incomplete condition).

Three families, deliberately non-isomorphic:

  A  bounded_quantity   explicit cardinality in the request ("first 3" / "first 4")
  B  semantic_predicate NO cardinality anywhere; the goal is a set-membership
                        predicate, and only the predicate changes.  This is the
                        family that decides whether the effect is more than
                        counting.
  C  slot_requirement   a requested field set ({name, occupation} vs
                        {name, occupation, country}); semantic slots, not items.

Each item yields two decision positions, both measured in one forward pass:

  P1 = immediately after the last content token of the prefix
       competitor = the item separator (the only way to continue)
  P2 = immediately after the separator
       competitor = the first token of the correct missing content

P2 is the primary position because it matches the S03 spec
("logit(stop) - logit(correct_next_missing_token)"); P1 is reported as a
secondary, separator-free check.
"""
import json
import os

# --------------------------------------------------------------------------
# Family A — bounded quantity.  Ordered lists where the request names N.
# Each entry: (topic phrase, ordered items).  We always replay the first k
# items and contrast "first k" (complete) against "first k+1" (incomplete).
# --------------------------------------------------------------------------
ORDERED_LISTS = [
    ("the planets of the Solar System in order from the Sun",
     ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn"]),
    ("the days of the week starting from Monday",
     ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]),
    ("the months of the year in order",
     ["January", "February", "March", "April", "May", "June"]),
    ("the letters of the English alphabet in order",
     ["A", "B", "C", "D", "E", "F"]),
    ("the Great Lakes ordered from west to east",
     ["Superior", "Michigan", "Huron", "Erie", "Ontario"]),
    ("the colours of the rainbow in order",
     ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo"]),
    ("the notes of the C major scale in order",
     ["C", "D", "E", "F", "G", "A"]),
    ("the first Presidents of the United States in order",
     ["Washington", "Adams", "Jefferson", "Madison", "Monroe", "Adams"]),
    ("the continents ordered by land area, largest first",
     ["Asia", "Africa", "North America", "South America", "Antarctica", "Europe"]),
    ("the seasons of the year starting from spring",
     ["Spring", "Summer", "Autumn", "Winter"]),
    ("the planets of the Solar System ordered by size, largest first",
     ["Jupiter", "Saturn", "Uranus", "Neptune", "Earth", "Venus"]),
    ("the oceans of the world ordered by area, largest first",
     ["Pacific", "Atlantic", "Indian", "Southern", "Arctic"]),
]

# --------------------------------------------------------------------------
# Family B — semantic predicate.  No number appears in either prompt.
# The replayed prefix is exactly the set satisfying `goal_complete`; the
# incomplete goal names a strictly larger set whose next member is `missing`.
# --------------------------------------------------------------------------
PREDICATE_ITEMS = [
    dict(complete="the planets that orbit closer to the Sun than Earth",
         incomplete="the planets that orbit closer to the Sun than Jupiter",
         prefix=["Mercury", "Venus"], missing="Earth"),
    dict(complete="the Great Lakes that lie entirely within the United States",
         incomplete="the Great Lakes that border the state of Michigan",
         prefix=["Michigan"], missing="Superior"),
    dict(complete="the months that fall in the first quarter of the year",
         incomplete="the months that fall in the first half of the year",
         prefix=["January", "February", "March"], missing="April"),
    dict(complete="the noble gases that are lighter than argon",
         incomplete="the noble gases that are lighter than xenon",
         prefix=["Helium", "Neon"], missing="Argon"),
    dict(complete="the days of the week whose English name begins with the letter T",
         incomplete="the days of the week that fall on a weekday",
         prefix=["Tuesday", "Thursday"], missing="Monday"),
    dict(complete="the US states that border the Pacific Ocean on the mainland",
         incomplete="the US states that border Mexico",
         prefix=["California"], missing="Arizona"),
    dict(complete="the primary colours of light",
         incomplete="the colours that appear in the visible spectrum",
         prefix=["Red", "Green", "Blue"], missing="Orange"),
    dict(complete="the countries of the United Kingdom that lie on the island of Great Britain",
         incomplete="the countries that make up the United Kingdom",
         prefix=["England", "Scotland", "Wales"], missing="Northern Ireland"),
    dict(complete="the planets of the Solar System that have no moons",
         incomplete="the planets of the Solar System that are rocky",
         prefix=["Mercury", "Venus"], missing="Earth"),
    dict(complete="the seasons that fall between the spring equinox and the autumn equinox",
         incomplete="the seasons of the year",
         prefix=["Spring", "Summer"], missing="Autumn"),
    dict(complete="the Scandinavian countries",
         incomplete="the Nordic countries",
         prefix=["Denmark", "Norway", "Sweden"], missing="Finland"),
    dict(complete="the oceans that touch the coast of Africa",
         incomplete="the oceans that touch the coast of Asia",
         prefix=["Atlantic", "Indian"], missing="Pacific"),
    dict(complete="the chess pieces that can only move in straight lines",
         incomplete="the chess pieces that are not pawns",
         prefix=["Rook", "Queen", "King"], missing="Bishop"),
    dict(complete="the states of matter that have a definite volume",
         incomplete="the classical states of matter",
         prefix=["Solid", "Liquid"], missing="Gas"),
    dict(complete="the continents that lie entirely in the Southern Hemisphere",
         incomplete="the continents that lie partly in the Southern Hemisphere",
         prefix=["Australia", "Antarctica"], missing="Africa"),
]

# --------------------------------------------------------------------------
# Family C — slot requirement set.  The request names fields, the prefix
# supplies a prefix of that field list.
# --------------------------------------------------------------------------
SLOT_ITEMS = [
    dict(subject="Marie Curie",
         fields=[("Name", "Marie Curie"), ("Occupation", "Physicist and chemist"),
                 ("Country of birth", "Poland")]),
    dict(subject="Ada Lovelace",
         fields=[("Name", "Ada Lovelace"), ("Occupation", "Mathematician"),
                 ("Country of birth", "England")]),
    dict(subject="Mount Everest",
         fields=[("Name", "Mount Everest"), ("Height", "8,849 metres"),
                 ("Mountain range", "Himalayas")]),
    dict(subject="the Amazon River",
         fields=[("Name", "Amazon River"), ("Length", "About 6,400 kilometres"),
                 ("Continent", "South America")]),
    dict(subject="Tokyo",
         fields=[("Name", "Tokyo"), ("Country", "Japan"),
                 ("Population", "About 14 million")]),
    dict(subject="the novel Moby-Dick",
         fields=[("Title", "Moby-Dick"), ("Author", "Herman Melville"),
                 ("Year of publication", "1851")]),
    dict(subject="the element gold",
         fields=[("Name", "Gold"), ("Symbol", "Au"), ("Atomic number", "79")]),
    dict(subject="the Eiffel Tower",
         fields=[("Name", "Eiffel Tower"), ("City", "Paris"),
                 ("Year completed", "1889")]),
    dict(subject="Beethoven",
         fields=[("Name", "Ludwig van Beethoven"), ("Occupation", "Composer"),
                 ("Country of birth", "Germany")]),
    dict(subject="the Pacific Ocean",
         fields=[("Name", "Pacific Ocean"), ("Area", "About 165 million square kilometres"),
                 ("Deepest point", "Mariana Trench")]),
    dict(subject="the film Casablanca",
         fields=[("Title", "Casablanca"), ("Director", "Michael Curtiz"),
                 ("Year of release", "1942")]),
    dict(subject="the Nile",
         fields=[("Name", "Nile"), ("Continent", "Africa"),
                 ("Length", "About 6,650 kilometres")]),
]


def fmt_list(items):
    return "\n".join(items)


def build_family_a():
    out = []
    for topic, items in ORDERED_LISTS:
        for k in (2, 3):
            if k + 1 >= len(items):
                continue
            prefix_items = items[:k]
            missing = items[k]
            out.append(dict(
                family="A_bounded_quantity",
                item_id=f"A_{topic[:18].replace(' ', '_')}_{k}",
                user_complete=f"List {topic}. Give the first {k}, one per line, with no extra text.",
                user_incomplete=f"List {topic}. Give the first {k + 1}, one per line, with no extra text.",
                prefix_text=fmt_list(prefix_items),
                separator="\n",
                missing_text=missing,
                n_given=k,
            ))
    return out


def build_family_b():
    out = []
    for it in PREDICATE_ITEMS:
        tail = " List them one per line, with no extra text."
        out.append(dict(
            family="B_semantic_predicate",
            item_id=f"B_{it['missing'][:12].replace(' ', '_')}_{len(it['prefix'])}",
            user_complete=f"List {it['complete']}." + tail,
            user_incomplete=f"List {it['incomplete']}." + tail,
            prefix_text=fmt_list(it["prefix"]),
            separator="\n",
            missing_text=it["missing"],
            n_given=len(it["prefix"]),
        ))
    return out


def build_family_c():
    out = []
    for it in SLOT_ITEMS:
        f = it["fields"]
        given = f[:2]
        missing_label = f[2][0]
        names_c = f"{f[0][0].lower()} and {f[1][0].lower()}"
        names_i = f"{f[0][0].lower()}, {f[1][0].lower()}, and {f[2][0].lower()}"
        tail = " Use one 'Field: value' line per field, with no extra text."
        prefix_text = "\n".join(f"{lab}: {val}" for lab, val in given)
        out.append(dict(
            family="C_slot_requirement",
            item_id=f"C_{it['subject'][:16].replace(' ', '_')}",
            user_complete=f"For {it['subject']}, give the {names_c}." + tail,
            user_incomplete=f"For {it['subject']}, give the {names_i}." + tail,
            prefix_text=prefix_text,
            separator="\n",
            missing_text=f"{missing_label}:",
            n_given=2,
        ))
    return out


def main():
    stim = build_family_a() + build_family_b() + build_family_c()
    # item_id is a human-readable label; truncation can make two of them
    # collide, so disambiguate with a running index per family.
    seen = {}
    for s in stim:
        n = seen.get(s["item_id"], 0)
        seen[s["item_id"]] = n + 1
        if n:
            s["item_id"] = f"{s['item_id']}#{n + 1}"
    os.makedirs("stimuli", exist_ok=True)
    path = "stimuli/e01_pairs.jsonl"
    with open(path, "w") as fh:
        for s in stim:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    from collections import Counter
    print(Counter(s["family"] for s in stim))
    print("wrote", path, len(stim), "pairs")


if __name__ == "__main__":
    main()
