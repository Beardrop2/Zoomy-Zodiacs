import to_number
from hypothesis import given
from hypothesis.strategies import text

"""testing that input strings don't make code crash."""


@given(text())
def test_sum_ords_runs(s: str) -> None:
    """Test input won't make code crash."""
    to_number.sum_ords(s)


@given(text())
def test_alpha_values_runs(s: str) -> None:
    """Test input won't make code crash."""
    to_number.alpha_values(s)


@given(text())
def test_agrippan_method_runs(s: str) -> None:
    """Test input won't make code crash."""
    to_number.agrippan_method(s)


@given(text())
def test_as_bytes_runs(s: str) -> None:
    """Test input won't make code crash."""
    to_number.as_bytes(s)
