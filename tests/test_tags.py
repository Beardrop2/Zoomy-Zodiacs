from string import ascii_lowercase

import aiosqlite
import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from repositories.tags import SqliteTagRepository, group_griends, suggested_friends

characters = st.sampled_from(ascii_lowercase)
# more likely to be desired duplicates than with st.text()


@pytest.mark.asyncio()
async def test_suggested_friends_basic_1() -> None:
    friends = [(1, "a"), (2, "a"), (2, "b")]
    res = await suggested_friends(friends, 1, {"a"})
    assert res == {1: ["a"]}


@pytest.mark.asyncio()
async def test_suggested_friends_basic_2() -> None:
    friends = [(1, "a"), (1, "b"), (1, "c"), (2, "c"), (2, "b"), (3, "agf")]
    res = await suggested_friends(friends, 2, {"b", "c"})
    assert res == {1: ["a", "b", "c"], 2: ["b", "c"]}


@pytest.mark.asyncio()
@given(st.lists(st.tuples(st.integers(), characters)))
async def test_group_griends_nonempty(xs: list[tuple[int, str]]) -> None:
    res = await group_griends(xs)
    assert all(len(v) > 0 for v in res.values())
    # verify that x > 0 in a/x in suggested_friends, avoiding ZeroDivisionError


@pytest.mark.asyncio()
@given(st.lists(st.tuples(st.integers(), characters)), st.integers(), st.lists(characters))
async def test_suggested_friends_runs(xs: list[tuple[int, str]], amt: int, user_tags: list[str]) -> None:
    assume(amt > 0)
    await suggested_friends(xs, amt, user_tags)


@pytest.mark.asyncio()
async def test_full_tag_suggestions_1() -> None:
    database_connection = await aiosqlite.connect("test.db")

    repos = SqliteTagRepository(database_connection)
    await repos.initialize()

    data = [(1, "a"), (2, "a"), (3, "b")]
    for id, tag in data:
        await repos.add(id, tag)

    res = await repos.get_friend_suggestions(1)

    for id, tag in data:
        await repos.remove(id, tag)

    await database_connection.close()
    assert res == {2: ["a"]}


@pytest.mark.asyncio()
async def test_full_tag_suggestions_2() -> None:
    database_connection = await aiosqlite.connect("test.db")

    repos = SqliteTagRepository(database_connection)
    await repos.initialize()

    data = [(1, "a"), (2, "a"), (3, "b"), (4, "a")]

    for id, tag in data:
        await repos.add(id, tag)

    res = await repos.get_friend_suggestions(1)

    for id, tag in data:
        await repos.remove(id, tag)

    await database_connection.close()

    assert res == {2: ["a"], 4: ["a"]}
