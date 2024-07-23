from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Literal, override

import aiosqlite

TagType = Literal[
    "algos-and-data-structs",
    "async-and-concurrency",
    "c-extensions",
    "cybersecurity",
    "databases",
    "data-science-and-ai",
    "discord-bots",
    "editors-ides",
    "esoteric-python",
    "game-development",
    "media-processing",
    "microcontrollers",
    "networks",
    "packaging-and-distribution",
    "software-architecture",
    "web-development",
    "tools-and-devops",
    "type-hinting",
    "unit-testing",
    "unix",
    "user-interfaces",
]


class TagRepository(ABC):
    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def add(self, user_id: int, tag: TagType) -> None: ...

    @abstractmethod
    async def get(self, user_id: int) -> list[str]: ...

    @abstractmethod
    async def remove(self, user_id: int, tag: TagType) -> None: ...

    @abstractmethod
    async def get_friend_suggestions(self, user_id: int) -> dict[int, list[str]]: ...


@dataclass
class SqliteTagRepository(TagRepository):
    database: aiosqlite.Connection

    @override
    async def initialize(self) -> None:
        async with self.database.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    user_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    PRIMARY KEY (user_id, tag)
                )
            """)
            await self.database.commit()

    @override
    async def add(self, user_id: int, tag: TagType) -> None:
        async with self.database.cursor() as cursor:
            await cursor.execute("INSERT OR IGNORE INTO tags (user_id, tag) VALUES (?, ?)", (user_id, tag))
            await self.database.commit()

    @override
    async def get(self, user_id: int) -> list[str]:
        async with self.database.cursor() as cursor:
            await cursor.execute("SELECT tag FROM tags WHERE user_id = ?", (user_id,))
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    @override
    async def remove(self, user_id: int, tag: TagType) -> None:
        async with self.database.cursor() as cursor:
            await cursor.execute("DELETE FROM tags WHERE user_id = ? AND tag = ?", (user_id, tag))
            await self.database.commit()

    @override
    async def get_friend_suggestions(self, user_id: int) -> dict[int, list[str]]:
        async with self.database.cursor() as cursor:
            user_tags = await self.get(user_id)

            if not user_tags:
                return {}

            # Find other users who have at least one tag in common
            query = """
                SELECT t2.user_id, t2.tag
                FROM tags t1
                JOIN tags t2 ON t1.tag = t2.tag
                WHERE t1.user_id = ? AND t2.user_id != t1.user_id
                ORDER BY t2.user_id
            """
            await cursor.execute(query, (user_id,))

            result: list[tuple[int, str]] = await cursor.fetchall()  # type: ignore[reportAssignmentType]
            matching = tuple(sorted({user for (user, _) in result}))
            matching = str(matching).replace(",", "") if len(matching) == 1 else str(matching)

            # Find all tags of said other users who have at least one tag in common

            # TODO: verify whether this is volnerable to SQL injection and fix
            # ids should be ints that aren't created by users directly, no strings, so should be safe
            query_any = f"""
                SELECT t.user_id, t.tag
                FROM tags t
                WHERE t.user_id in {matching}
                ORDER BY t.user_id
            """  # noqa: S608


            await cursor.execute(query_any)

            result_any_tags: list[tuple[int, str]] = await cursor.fetchall()  # type: ignore[reportAssignmentType

            # Limit to top 10 users with best ratio of tags in common
            return await suggested_friends(result_any_tags, 10, user_tags)


async def group_griends(result: list[tuple[int, str]]) -> dict[int, set[str]]:
    # Group the results by user_id
    suggestions: defaultdict[int, set[str]] = defaultdict(set)
    for suggested_user_id, tag in result:
        suggestions[suggested_user_id].add(tag)
    return dict(suggestions)


async def suggested_friends(result: list[tuple[int, str]], amt: int, user_tags: list[str]) -> dict[int, list[str]]:
    suggestions = await group_griends(result)
    user_tags = set(user_tags)

    def key(tags: set[str]) -> float:
        """Use ratio of tags in common:total tags to prevent gaming the system by having every tag."""
        return len(user_tags & tags) / len(user_tags | tags)

    # Limit to top {amt}} users with most common tags
    res = dict(sorted(suggestions.items(), key=lambda x: key(x[1]), reverse=True)[:amt])
    return {k: sorted(v) for k, v in res.items()}
    # should we adjust to return set instead of list?
