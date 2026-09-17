"""Literal matching and disk-backed character-bigram candidates.

FTS is only a candidate index. Every returned result is checked against normalized
original text, so disconnected grams cannot masquerade as a phrase match.
"""

import re
import unicodedata


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def grams(text: str) -> str:
    text = normalize(text)
    return " ".join(
        sorted({f"g{ord(a):06x}{ord(b):06x}" for a, b in zip(text, text[1:], strict=False)})
    )


def query_terms(query: str, allow_single: bool = False) -> list[str]:
    if len(query) > 256:
        raise ValueError("query_too_long")
    if query.count('"') % 2:
        raise ValueError("unclosed_quote")
    terms = [normalize(a or b) for a, b in re.findall(r'"([^"]*)"|(\S+)', query)]
    terms = list(dict.fromkeys(term for term in terms if term))
    if len(terms) > 12:
        raise ValueError("too_many_terms")
    if not allow_single and any(len(term) < 2 for term in terms):
        raise ValueError("query_too_short")
    return terms


def match_expression(terms: list[str]) -> str:
    return " AND ".join(sorted({gram for term in terms for gram in grams(term).split()}))


def ranges(text: str, terms: list[str]) -> list[list[int]]:
    """Map normalized matches back to original Unicode codepoint offsets."""
    chars, offsets = [], []
    for index, char in enumerate(text):
        for part in unicodedata.normalize("NFKC", char).casefold():
            if part.isspace():
                if chars and chars[-1] != " ":
                    chars.append(" ")
                    offsets.append(index)
            else:
                chars.append(part)
                offsets.append(index)
    canonical = "".join(chars)
    found = []
    for term in terms:
        start = 0
        while (start := canonical.find(term, start)) >= 0:
            end = start + len(term)
            found.append([offsets[start], offsets[end - 1] + 1])
            start = end
    merged = []
    for start, end in sorted(found):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def snippet(text: str, terms: list[str], limit: int = 180) -> dict:
    matches = ranges(text, terms)
    start = max(0, matches[0][0] - 38) if matches else 0
    end = min(len(text), start + limit)
    excerpt = text[start:end]
    return {
        "text": excerpt,
        "ranges": [
            [max(a, start) - start, min(b, end) - start]
            for a, b in matches
            if a < end and b > start
        ],
        "before": start > 0,
        "after": end < len(text),
    }
