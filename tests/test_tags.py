import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from repositories.tags import suggested_friends, suggested_friends_old


@pytest.mark.asyncio()
async def test_suggested_friends_basic_1() -> None:
    friends = [(5, "a")] * 5 + [(3, "b")] * 4
    res = await suggested_friends(friends, 1)
    assert res == {5: ["a"] * 5}


@pytest.mark.asyncio()
async def test_suggested_friends_basic_2() -> None:
    friends = [(1, "a"), (1, "b"), (1, "c"), (2, "c"), (2, "b"), (3, "a")]
    res = await suggested_friends(friends, 2)
    assert res == {1: ["a", "b", "c"], 2: ["c", "b"]}


@pytest.mark.asyncio()
@given(st.lists(st.tuples(st.text(), st.text())), st.integers())
async def test_suggested_friends_equal(xs: list[tuple[int, str]], amt: int) -> None:
    assume(amt > 0)
    assert await suggested_friends(xs, amt) == await suggested_friends_old(xs, amt)
