from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import override

import aiosqlite


class TagRepository(ABC):
    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def add(self, user_id: int, tag: str) -> None: ...

    @abstractmethod
    async def get(self, user_id: int) -> list[str]: ...

    @abstractmethod
    async def remove(self, user_id: int, tag: str) -> None: ...

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
    async def add(self, user_id: int, tag: str) -> None:
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
    async def remove(self, user_id: int, tag: str) -> None:
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

            # Limit to top 10 users with most common tags
            return suggested_friends(result, 10)


async def suggested_friends(result: list[tuple[int, str]], amt: int) -> dict[int, list[str]]:
    # Group the results by user_id
    suggestions: defaultdict[int, list[str]] = defaultdict(list)
    for suggested_user_id, tag in result:
        suggestions[suggested_user_id].append(tag)

    # Limit to top 10 users with most common tags
    return dict(sorted(suggestions.items(), key=lambda x: len(x[1]), reverse=True)[:amt])


async def suggested_friends_old(result: list[tuple[int, str]], amt: int) -> dict[int, list[str]]:
    # Group the results by user_id
    suggestions: dict[int, list[str]] = {}
    for suggested_user_id, tag in result:
        if suggested_user_id not in suggestions:
            suggestions[suggested_user_id] = []
        suggestions[suggested_user_id].append(tag)

    # Limit to top {amt} users with most common tags
    return dict(sorted(suggestions.items(), key=lambda x: len(x[1]), reverse=True)[:amt])
