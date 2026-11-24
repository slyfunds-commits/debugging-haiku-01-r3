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


def _vowel_groups(w):
    """Count maximal runs of vowel letters in a lower-cased word.

    A run of adjacent vowels is one sounded group ('ea' in 'break' is a
    single group), while separated vowels are separate groups ('io' in
    'radio' is two). 'y' counts as a vowel, so 'sky' and 'happy' each
    carry one group here.
    """
    groups = 0
    prev_vowel = False
    for ch in w:
        is_vowel = ch in VOWELS
        if is_vowel and not prev_vowel:
            groups += 1
        prev_vowel = is_vowel
    return groups


def count_syllables(word):
    """Heuristic syllable count: vowel groups, minus a silent final 'e'.

    A silent 'e' also hides before a final 'd'/'s' ('cleared', 'outlives'),
    except after 't'/'d' where the 'e' is sounded ('wanted', 'mended').
    A final 'le' after a consonant adds a sounded syllable back
    ('bottle', 'candle' are two syllables), while a vowel before the
    'le' means the 'e' is already silent ('file', 'tile' stay one).
    """
    w = word.strip(",.!?;:").lower()
    if not w:
        return 0
    groups = _vowel_groups(w)
    if w.endswith("e") and groups > 1:
        groups -= 1
    elif (w.endswith("ed") or w.endswith("es")) and len(w) > 2 \
            and w[-3] not in "td" and groups > 1:
        groups -= 1
    if w.endswith("le") and len(w) > 2 and w[-3] not in VOWELS:
        groups += 1
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
    # Per-line totals, checked one line at a time so a failure names the
    # exact line instead of just the whole [5, 7, 5] shape.
    for i, (got, want) in enumerate(zip(counts, [5, 7, 5])):
        assert got == want, (
            f"line {i + 1} has {got} syllables, expected {want} "
            f"for a 5-7-5 haiku (line: {lines[i]!r})"
        )
    return counts


def check_length(text):
    """Char bound for the whole entry, with a distinct message each way.

    The gate is 1-200 chars: too short means a line is missing, too long
    means the haiku has drifted past the limit.
    """
    n = len(text)
    assert n >= 1, f"entry is empty (0 chars), expected at least 1"
    assert n <= 200, f"entry is {n} chars, over the 200-char limit"
    return n


def check_entry_from_disk(path="/output/entry.txt"):
    """Re-verify the entry already on disk, without rewriting it.

    Used by --check: reads the file back, checks the same gates the
    writer enforces (3 lines, 5-7-5, 1-200 chars, no trailing newline,
    heuristic agrees with the hand count), and reports the result.
    """
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode("utf-8")
    assert not data.endswith(b"\n"), "trailing newline on disk"
    lines = text.split("\n")
    assert len(lines) == 3, f"expected 3 lines on disk, got {len(lines)}"
    counts = check_counts(lines)
    assert counts == [5, 7, 5], f"expected [5, 7, 5] on disk, got {counts}"
    assert 1 <= len(text) <= 200, f"length {len(text)} out of range on disk"
    assert all(line == line.strip() for line in lines), "stray whitespace on disk"
    print(f"check OK: {path}: {len(text)} chars, syllables {counts}")
    return counts


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ("--check", "--self-test"):
        check_entry_from_disk()
        return
    lines = HAIKU.split("\n")
    assert len(lines) == 3, f"expected 3 lines, got {len(lines)}"
    counts = check_counts(lines)
    assert counts == [5, 7, 5], f"expected [5, 7, 5], got {counts}"
    check_length(HAIKU)
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
