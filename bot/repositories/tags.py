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
    """Abstract base class for tag repositories.

    This is used for friend suggestions. See `bot.exts.tags` for the slash
    commands that leverage this.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the tag repository.

        For databases, this means creating any tables or schemas.
        """

    @abstractmethod
    async def add(self, user_id: int, tag: TagType) -> None:
        """Add a tag to a user.

        Args:
            user_id: The user's Discord ID.
            tag: The tag to add.
        """

    @abstractmethod
    async def get(self, user_id: int) -> list[str]:
        """Get all the tags of a user.

        Args:
            user_id: The user's Discord ID.

        Returns:
            A list of the user's tags.
        """

    @abstractmethod
    async def remove(self, user_id: int, tag: TagType) -> None:
        """Remove a tag from a user.

        This does nothing if the user doesn't have the specified tag.

        Args:
            user_id: The user's Discord ID.
            tag: The tag to remove.
        """

    @abstractmethod
    async def get_friend_suggestions(self, user_id: int) -> list[tuple[int, list[str]]]:
        """Suggest friends for a user based on their tags.

        Args:
            user_id: The user's Discord ID.

        Returns:
            A list containing pairs of suggested user IDs with
            the tags they have in common with the user.
        """


@dataclass
class SqliteTagRepository(TagRepository):
    """A tag repository that uses SQLite to store data."""

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
    async def get_friend_suggestions(self, user_id: int) -> list[tuple[int, list[str]]]:
        async with self.database.cursor() as cursor:
            user_tags = await self.get(user_id)

            if not user_tags:
                return []

            query = """
                SELECT t.user_id, t.tag
                FROM tags t
                WHERE t.user_id IN (
                    SELECT t2.user_id
                    FROM tags t1
                    JOIN tags t2 ON t1.tag = t2.tag
                    WHERE t1.user_id = ? AND t2.user_id != t1.user_id
                )
                ORDER BY t.user_id;
                """
            await cursor.execute(query, (user_id,))

            result_any_tags: list[tuple[int, str]] = await cursor.fetchall()  # type: ignore[reportAssignmentType]

            # Limit to top 10 users with best ratio of tags in common
            return await suggest_friends(result_any_tags, 10, user_tags)


async def group_friends(result: list[tuple[int, str]]) -> dict[int, set[str]]:
    # Group the results by user_id
    suggestions: defaultdict[int, set[str]] = defaultdict(set)
    for suggested_user_id, tag in result:
        suggestions[suggested_user_id].add(tag)
    return dict(suggestions)


async def suggest_friends(
    result: list[tuple[int, str]],
    amt: int,
    user_tags: list[str],
) -> list[tuple[int, list[str]]]:
    suggestions = await group_friends(result)
    user_tags = set(user_tags)

    def key(tags: set[str]) -> float:
        """Use ratio of tags in common:total tags to prevent gaming the system by having every tag."""
        return len(user_tags & tags) / len(user_tags | tags)

    # Limit to top {amt} users with most common tags
    res = sorted(suggestions.items(), key=lambda x: (key(x[1]), x[0]), reverse=True)[:amt]
    return [(k, sorted(v)) for k, v in res]
