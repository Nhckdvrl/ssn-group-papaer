"""Per-language configuration for E02 Layer 1.

Tickets are the parent's PUBLISHED sets (KS-Lottery Appendix Table 11), not ours,
so no reproduction of their selection procedure is load-bearing here.
"""

PUBLISHED_TICKETS = {
    "ca": [13, 263, 278, 297, 304, 310, 322, 338, 376, 393, 411,
           29871, 29889, 29892, 29896, 29900, 29901, 29949],
    "es": [13, 262, 263, 278, 297, 304, 310, 313, 322, 363, 393, 411,
           29871, 29889, 29892, 29896, 29897, 29901],
    "ro": [13, 278, 297, 304, 310, 322, 338, 366, 393,
           29871, 29889, 29892, 29896, 29900, 29901],
    "da": [13, 263, 278, 297, 304, 310, 322, 29871, 29889, 29892, 29896, 29900],
    "de": [13, 263, 278, 297, 304, 310, 322, 338, 363,
           29871, 29889, 29892, 29896, 29901, 29915],
    "pt": [13, 263, 278, 297, 304, 310, 322, 338, 363, 411,
           29871, 29889, 29892, 29896, 29900, 29901, 29915],
}

LANG = {
    "ca": {"name": "Catalan", "flores": "cat", "opus": "ca-en"},
    "es": {"name": "Spanish", "flores": "spa", "opus": "en-es"},
    "ro": {"name": "Romanian", "flores": "ron", "opus": "en-ro"},
    "de": {"name": "German", "flores": "deu", "opus": "de-en"},
}


def template(lang):
    """The E01 `explicit` template with only the language name substituted."""
    n = LANG[lang]["name"]
    return (f"Translate the following sentence from English to {n}.\nEnglish:",
            f"\n{n}:")
