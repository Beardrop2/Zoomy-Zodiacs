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
    async def get_friend_suggestions(self, user_id: int) -> dict[int, list[str]]:
        """Suggest friends for a user based on their tags.

        Args:
            user_id: The user's Discord ID.

        Returns:
            A dictionary mapping suggested user IDs to the tags they have in
            common with the user.
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
            return await suggest_friends(result, 10)


async def suggest_friends(result: list[tuple[int, str]], amt: int) -> dict[int, list[str]]:
    # Group the results by user_id
    suggestions: defaultdict[int, list[str]] = defaultdict(list)
    for suggested_user_id, tag in result:
        suggestions[suggested_user_id].append(tag)

    # Limit to top 10 users with most common tags
    return dict(sorted(suggestions.items(), key=lambda x: len(x[1]), reverse=True)[:amt])
