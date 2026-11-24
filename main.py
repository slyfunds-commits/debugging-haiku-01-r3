#!/usr/bin/env python3
"""Seventeen Syllables of Debugging — round 3 (FINAL) entry.

Writes the haiku to /output/entry.txt: exactly 3 lines, 5-7-5 syllables,
1-200 chars total, no trailing newline. Stdlib only.
"""

import os

HAIKU = (
    "The logs say success\n"
    "the users say it's broken\n"
    "success was the lie"
)

# Hand-counted syllables for every word in the haiku. The heuristic below
# must agree with this map; a disagreement fails loudly instead of
# silently shipping a wrong count.
EXPECTED = {
    "the": 1, "logs": 1, "say": 1, "success": 2,
    "users": 2, "it's": 1, "broken": 2,
    "was": 1, "lie": 1,
}

VOWELS = "aeiouy"


def count_syllables(word):
    """Heuristic syllable count: vowel groups, minus a silent final 'e'.

    A silent 'e' also hides before a final 'd'/'s' ('cleared', 'outlives'),
    except after 't'/'d' where the 'e' is sounded ('wanted').
    """
    w = word.strip(",.!?;:").lower()
    if not w:
        return 0
    groups = 0
    prev_vowel = False
    for ch in w:
        is_vowel = ch in VOWELS
        if is_vowel and not prev_vowel:
            groups += 1
        prev_vowel = is_vowel
    if w.endswith("e") and groups > 1:
        groups -= 1
    elif (w.endswith("ed") or w.endswith("es")) and len(w) > 2 \
            and w[-3] not in "td" and groups > 1:
        groups -= 1
    return max(groups, 1)


def check_counts(lines):
    counts = []
    for line in lines:
        total = 0
        for raw in line.split():
            w = raw.strip(",.!?;:").lower()
            assert w in EXPECTED, f"word {w!r} has no hand-counted syllable entry"
            got = count_syllables(raw)
            assert got == EXPECTED[w], (
                f"heuristic says {got} for {w!r}, hand count says {EXPECTED[w]}"
            )
            total += EXPECTED[w]
        counts.append(total)
    return counts


def main():
    lines = HAIKU.split("\n")
    assert len(lines) == 3, f"expected 3 lines, got {len(lines)}"
    counts = check_counts(lines)
    assert counts == [5, 7, 5], f"expected [5, 7, 5], got {counts}"
    assert 1 <= len(HAIKU) <= 200, f"length {len(HAIKU)} out of range"
    assert not HAIKU.endswith("\n"), "trailing newline forbidden"
    assert all(line == line.strip() for line in lines), "no stray whitespace"

    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "w", encoding="utf-8", newline="") as f:
        f.write(HAIKU)

    # Read-back verification: what is on disk is exactly the haiku.
    with open("/output/entry.txt", "rb") as f:
        data = f.read()
    assert data == HAIKU.encode("utf-8"), "read-back mismatch"
    assert not data.endswith(b"\n"), "trailing newline on disk"
    print(f"wrote /output/entry.txt: {len(HAIKU)} chars, syllables {counts}")


if __name__ == "__main__":
    main()
