"""Misc functions that convert a given string to a number via different methods."""

from string import ascii_lowercase

# should these be async ?


def sum_ords(s: str) -> int:
    """Sum characters by unicode values."""
    return sum(map(ord, s))


def alpha_values(s: str) -> int:
    """Sum characters by position in English alphabet."""
    matches = {c: i + 1 for (i, c) in enumerate(ascii_lowercase)}
    return sum(matches.get(c, 0) for c in s.lower())


def agrippan_method(s: str) -> int:
    """Based off of https://en.wikipedia.org/wiki/Numerology#Agrippan_method .

    with adjustments to work for English version of latin alphabet ( j,u,w ).
    """
    seq = "abcdefghi klmnopqrs tuxyzjv*w"
    matches = {c: 10**i * (j + 1) for (i, row) in enumerate(seq.split()) for (j, c) in enumerate(row)}
    del matches["*"]
    # method has 2 different versions of 'j' so disregarding the second one.

    return sum(matches.get(c, 0) for c in s.lower())


def as_bytes(s: str) -> int:
    """Parse as bytestring then int. Will result in large numbers.

    This probably won't be useful but included for completion's sake.
    """
    return int.from_bytes(s.encode())
