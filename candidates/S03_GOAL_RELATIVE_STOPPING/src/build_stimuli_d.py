"""
S03 / E01 family D — lexically and syntactically MATCHED goal intervention.

Why this family exists.  In family C the incomplete prompt is the only one that
contains the missing field's word ("country of birth"), so part of the
continuation-side shift could be plain lexical priming rather than goal
completion.  Family D removes that confound:

  complete:   "Report the name and occupation, but not the country of birth."
  incomplete: "Report the name, occupation, and country of birth, but not the
               year of birth."

Both prompts

  * contain the string of the missing field ("country of birth") verbatim;
  * contain the same negation frame "but not the ...";
  * have closely matched length and syntax;

so lexical priming and the presence of a negation cue are held constant, and
the only thing that changes is whether the replayed prefix already satisfies
the request.

The replayed assistant prefix is the same two lines in both conditions, and the
competitor token is the first token of "Country of birth:" in both.
"""
import json

ITEMS = [
    dict(subject="Marie Curie", f1=("Name", "Marie Curie"),
         f2=("Occupation", "Physicist and chemist"),
         f3="country of birth", f4="year of birth"),
    dict(subject="Ada Lovelace", f1=("Name", "Ada Lovelace"),
         f2=("Occupation", "Mathematician"),
         f3="country of birth", f4="year of birth"),
    dict(subject="Ludwig van Beethoven", f1=("Name", "Ludwig van Beethoven"),
         f2=("Occupation", "Composer"),
         f3="country of birth", f4="year of birth"),
    dict(subject="Mount Everest", f1=("Name", "Mount Everest"),
         f2=("Height", "8,849 metres"),
         f3="mountain range", f4="first ascent year"),
    dict(subject="the Amazon River", f1=("Name", "Amazon River"),
         f2=("Length", "About 6,400 kilometres"),
         f3="continent", f4="mouth"),
    dict(subject="Tokyo", f1=("Name", "Tokyo"), f2=("Country", "Japan"),
         f3="population", f4="land area"),
    dict(subject="the novel Moby-Dick", f1=("Title", "Moby-Dick"),
         f2=("Author", "Herman Melville"),
         f3="year of publication", f4="original publisher"),
    dict(subject="the element gold", f1=("Name", "Gold"), f2=("Symbol", "Au"),
         f3="atomic number", f4="melting point"),
    dict(subject="the Eiffel Tower", f1=("Name", "Eiffel Tower"),
         f2=("City", "Paris"), f3="year completed", f4="architect"),
    dict(subject="the Pacific Ocean", f1=("Name", "Pacific Ocean"),
         f2=("Area", "About 165 million square kilometres"),
         f3="deepest point", f4="average depth"),
    dict(subject="the film Casablanca", f1=("Title", "Casablanca"),
         f2=("Director", "Michael Curtiz"),
         f3="year of release", f4="studio"),
    dict(subject="the Nile", f1=("Name", "Nile"), f2=("Continent", "Africa"),
         f3="length", f4="source"),
]

TAIL = " Use one 'Field: value' line per field, with no extra text."


def main():
    out = []
    for it in ITEMS:
        l1, v1 = it["f1"]; l2, v2 = it["f2"]
        f3, f4 = it["f3"], it["f4"]
        n1, n2 = l1.lower(), l2.lower()
        out.append(dict(
            family="D_lexically_matched",
            item_id=f"D_{it['subject'][:16].replace(' ', '_')}",
            user_complete=(f"For {it['subject']}, report the {n1} and {n2}, "
                           f"but not the {f3}." + TAIL),
            user_incomplete=(f"For {it['subject']}, report the {n1}, {n2}, and {f3}, "
                             f"but not the {f4}." + TAIL),
            prefix_text=f"{l1}: {v1}\n{l2}: {v2}",
            separator="\n",
            missing_text=f3[0].upper() + f3[1:] + ":",
            n_given=2,
        ))
    # both conditions must mention the missing field, and both must carry the
    # same negation frame -- assert it rather than trust the strings
    for o in out:
        key = o["missing_text"].rstrip(":").lower()
        assert key in o["user_complete"].lower(), o["item_id"]
        assert key in o["user_incomplete"].lower(), o["item_id"]
        assert "but not the" in o["user_complete"]
        assert "but not the" in o["user_incomplete"]
    with open("stimuli/e01_pairs_d.jsonl", "w") as fh:
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    print("wrote stimuli/e01_pairs_d.jsonl", len(out))
    print(json.dumps(out[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
