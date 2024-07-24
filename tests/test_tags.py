from string import ascii_lowercase

import aiosqlite
import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from repositories.tags import SqliteTagRepository, group_friends, suggest_friends

characters = st.sampled_from(ascii_lowercase)
# more likely to be desired duplicates than with st.text()


@pytest.mark.asyncio()
async def test_suggested_friends_basic_1() -> None:
    friends = [(1, "a"), (2, "a"), (2, "b")]
    res = await suggest_friends(friends, 1, {"a"})
    assert res == {1: ["a"]}


@pytest.mark.asyncio()
async def test_suggested_friends_basic_2() -> None:
    friends = [(1, "a"), (1, "b"), (1, "c"), (2, "c"), (2, "b"), (3, "agf")]
    res = await suggest_friends(friends, 2, {"b", "c"})
    assert res == {1: ["a", "b", "c"], 2: ["b", "c"]}


@pytest.mark.asyncio()
@given(st.lists(st.tuples(st.integers(), characters)))
async def test_group_friends_nonempty(xs: list[tuple[int, str]]) -> None:
    res = await group_friends(xs)
    assert all(len(v) > 0 for v in res.values())
    # verify that x > 0 in a/x in suggested_friends, avoiding ZeroDivisionError


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


@pytest.mark.asyncio()
async def test_full_tag_suggestion_ratio() -> None:
    database_connection = await aiosqlite.connect("test.db")

    repos = SqliteTagRepository(database_connection)
    await repos.initialize()

    # user 1: Alice has tag a, b, and c
    # user 2: Bob has tag b, c, and d
    # user 3: Mal has tags a, b, c, d, e, f, g, h, i, j
    data = [
        (1, "a"),
        (1, "b"),
        (1, "c"),
        (2, "b"),
        (2, "c"),
        (2, "d"),
    ] + [(3, t) for t in "abcdefghij"]

    for id, tag in data:
        await repos.add(id, tag)

    res = await repos.get_friend_suggestions(1)

    for id, tag in data:
        await repos.remove(id, tag)

    await database_connection.close()

    # Expect Alice and Bob to match and not Mal
    # As Alice and Bob have a greater ratio of intersection
    print(res)
    assert res == {
        2: ["b", "c", "d"],
        3: ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    }  # Where 2 is the user id of Bob
