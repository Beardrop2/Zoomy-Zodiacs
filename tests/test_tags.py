from random import sample
from string import ascii_lowercase

import aiosqlite
import pytest
from hypothesis import given
from hypothesis import strategies as st
from repositories.tags import SqliteTagRepository, group_friends, suggest_friends

characters = st.sampled_from(ascii_lowercase)
test_guild = 1234
other_guild = 2468
is_greeter = True
not_greeter = False
# more likely to be desired duplicates than with st.text()


@pytest.mark.asyncio()
async def test_suggested_friends_basic_1() -> None:
    friends = [(1, "a"), (2, "a"), (2, "b")]
    res = await suggest_friends(friends, 1, {"a"})
    assert res == list({1: ["a"]}.items())


@pytest.mark.asyncio()
async def test_suggested_friends_basic_2() -> None:
    friends = [(1, "a"), (1, "b"), (1, "c"), (2, "c"), (2, "b"), (3, "agf")]
    res = await suggest_friends(friends, 2, {"b", "c"})
    assert res == [(2,  ["b", "c"]) , ( 1, ["a", "b", "c"]) ]


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
        await repos.add(guild_id=test_guild, user_id=id, tags=[tag], greeter=is_greeter)

    res = await repos.get_friend_suggestions(guild_id=test_guild, user_id=1)

    for id, tag in data:
        await repos.remove_tag(test_guild, id, tag)

    await database_connection.close()
    assert res == list({2: ["a"]}.items())


@pytest.mark.asyncio()
@given(
    st.lists(st.tuples(st.text(), st.text())),
    st.integers(min_value=1),
    st.lists(characters),
)
async def test_suggested_friends_deterministic(
    xs: list[tuple[str, str]],
    amt: int,
    user_tags: list[str],
) -> None:
    result1 = await suggest_friends(xs, amt, user_tags)
    result2 = await suggest_friends(xs, amt, user_tags)
    assert result1 == result2, "The suggest_friends function should be consistent."


@pytest.mark.asyncio()
@given(
    st.lists(st.tuples(st.text(), st.text())),
    st.integers(min_value=1),
    st.lists(characters),
)
async def test_suggested_friends_order_irrelevant(
    xs: list[tuple[str, str]],
    amt: int,
    user_tags: list[str],
) -> None:
    """Verify that order of inputted lists doesn't change the output"""

    # from https://docs.python.org/3/library/random.html#random.shuffle :
    # To shuffle an immutable sequence and return a new shuffled list, use sample(x, k=len(x)) instead.

    xs2 = sample(xs, k=len(xs))
    user_tags2 = sample(user_tags, k=len(user_tags))

    a = await suggest_friends(xs, amt, user_tags)
    b = await suggest_friends(xs2, amt, user_tags)
    c = await suggest_friends(xs, amt, user_tags2)
    d = await suggest_friends(xs2, amt, user_tags2)
    assert a == b == c == d

@pytest.mark.asyncio()
async def test_full_tag_suggestions_2() -> None:
    database_connection = await aiosqlite.connect("test.db")

    repos = SqliteTagRepository(database_connection)
    await repos.initialize()

    data = [(1, "a"), (2, "a"), (3, "b"), (4, "a")]

    for id, tag in data:
        await repos.add(test_guild, id, tag, is_greeter)

    res = await repos.get_friend_suggestions(test_guild, 1)

    for id, tag in data:
        await repos.remove_tag(test_guild, id, tag)

    await database_connection.close()

    assert res == [(4, ["a"]), (2, ["a"])]


@pytest.mark.asyncio()
async def test_suggested_friends_suggestion_ratio() -> None:


    # user 1: Alice has tag a, b, and c
    # user 2: Bob has tag b, c, and d
    # user 3: Mal has tags a, b, c, d, e, f, g, h, i, j
    data = [

        (2, "b"),
        (2, "c"),
        (2, "d"),
    ] + [(3, t) for t in "abcdefghij"]


    res = await suggest_friends(data, 1, {"a", "b", "c"})
    assert res == [(2, ["b", "c", "d"])]

@pytest.mark.asyncio()
async def test_suggestions_in_same_guild() -> None:
    # user 1: Alice has tags a, b and is a member of test guild
    # user 2: Bob has tag b and is a member of test guild
    # user 3: Mal has tags a, b, and is a member of other guild

    database_connection = await aiosqlite.connect("test.db")

    repos = SqliteTagRepository(database_connection)
    await repos.initialize()

    data = [
        (test_guild, 1, "a"),
        (test_guild, 1, "b"),
        (test_guild, 2, "b"),
        (other_guild, 3, "a"),
        (other_guild, 3, "b"),
    ]
    for guild, id, tag in data:
        await repos.add(guild, id, tag, is_greeter)

    res = await repos.get_friend_suggestions(test_guild, 1)

    for guild, id, tag in data:
        await repos.remove_tag(guild, id, tag)
    await database_connection.close()
    assert res == [(2, ["b"])]


@pytest.mark.asyncio()
async def test_suggestions_are_greeters() -> None:
    # user 1: Alice has tags a, b and is a greeter
    # user 2: Bob has tag b and is a greeter
    # user 3: Lilly has tags a, b, and is not a greeter
    database_connection = await aiosqlite.connect("test.db")

    repos = SqliteTagRepository(database_connection)
    await repos.initialize()

    data = [
        (1, "a", is_greeter),
        (1, "b", is_greeter),
        (2, "b", is_greeter),
        (3, "a", not_greeter),
        (3, "b", not_greeter),
    ]
    for id, tag, greeter in data:
        await repos.add(test_guild, id, tag, greeter)

    res = await repos.get_friend_suggestions(test_guild, 1)

    for row in data:
        await repos.remove_tag(test_guild, row[0], row[1])
    await database_connection.close()
    assert res == [(2, ["b"])]


@pytest.mark.asyncio()
async def test_greeters_update() -> None:
    # In this test, Lilly becomes a greeter
    # user 1: Alice has tags a, b and is a greeter
    # user 2: Bob has tag b and is a greeter
    # user 3: Lilly has tags a, b, and is not INITALLY a greeter
    database_connection = await aiosqlite.connect("test.db")

    repos = SqliteTagRepository(database_connection)
    await repos.initialize()

    data = [
        (1, "a", is_greeter),
        (1, "b", is_greeter),
        (2, "b", is_greeter),
        (3, "a", not_greeter),
        (3, "b", not_greeter),
    ]
    for id, tag, greeter in data:
        await repos.add(test_guild, id, tag, greeter)

    await repos.update_greeter(test_guild, 3, is_greeter)
    res = await repos.get_friend_suggestions(test_guild, 1)

    for row in data:
        await repos.remove_tag(test_guild, row[0], row[1])

    await database_connection.close()
    assert res[0] == (3, ["a", "b"])
