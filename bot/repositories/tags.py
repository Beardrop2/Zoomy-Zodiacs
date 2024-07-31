from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Literal, override

import aiosqlite


class UnknownUserError(Exception):
    """Raised when a user id is not found in the database."""


class DatabaseIntegrityError(Exception):
    """Raised when the database returns anomalous output."""


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
    async def add(self, user_id: int, tag: list[TagType], greeter: bool) -> None:
        """Add a tag to a user.

        Args:
            guild_id: the Discord Server ID
            user_id: The user's Discord ID.
            tag: The tag to add.
            greeter: A flag for if the user has opted in to suggestions
        """

    @abstractmethod
    async def get_tags(self, guild_id: int, user_id: int) -> list[str]:
        """Get all the tags of a user.

        Args:
            guild_id: the Discord Server ID
            user_id: The user's Discord ID.

        Returns:
            A list of the user's tags.
        """

    @abstractmethod
    async def remove_tag(self, guild_id: int, user_id: int, tag: TagType) -> None:
        """Remove a tag from a user.

        This does nothing if the user doesn't have the specified tag.

        Args:
            guild_id: the Discord Server ID
            user_id: The user's Discord ID.
            tag: The tag to remove.
        """

    @abstractmethod
    async def update_greeter(
        self,
        guild_id: int,
        user_id: int,
        greeter: bool,
    ) -> None:
        """Update a given users status as a greeter within a guild.

        Args:
            user_id: The user's Discord ID.
            guild_id: The Discord Server ID.
            greeter: A flag for if the user has opted in as a greeter or not.
        """

    @abstractmethod
    async def get_greeter(self, guild_id: int, user_id: int) -> bool:
        """Check a given users status as a greeter within a guild.

        Returns True if the user record has the Greeter role.
        Else returns false.

        Note that the user record should be kept in sync with the Discord user.

        Args:
            user_id: The user's Discord ID.
            guild_id: The Discord Server ID.
            greeter: A flag for if the user opts in to suggestions
        """

    @abstractmethod
    async def get_friend_suggestions(self, guild_id: int, user_id: int) -> list[tuple[int, list[str]]]:
        """Suggest friends for a user based on their tags.

        Args:
            user_id: The user's Discord ID.
            guild_id: The Discord Server ID.

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
            await cursor.execute(
                """
               CREATE TABLE IF NOT EXISTS tags (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    greeter BOOLEAN,
                    PRIMARY KEY (guild_id, user_id, tag)
                )
                """,
            )
        await self.database.commit()

    @override
    async def add(
        self,
        guild_id: int,
        user_id: int,
        tags: list[TagType],
        greeter: bool,
    ) -> None:
        async with self.database.cursor() as cursor:
            sql_script = "INSERT OR IGNORE INTO tags (guild_id, user_id, tag, greeter) VALUES (?, ?, ?, ?)"
            for tag in tags:
                await cursor.execute(
                    sql_script,
                    (guild_id, user_id, tag, greeter),
                )
            await self.database.commit()

    @override
    async def get_tags(self, guild_id: int, user_id: int) -> list[str]:
        async with self.database.cursor() as cursor:
            await cursor.execute(
                "SELECT tag FROM tags WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    @override
    async def remove_tag(self, guild_id: int, user_id: int, tag: TagType) -> None:
        query = "DELETE FROM tags WHERE guild_id = ? AND user_id = ? AND tag = ?"
        async with self.database.cursor() as cursor:
            await cursor.execute(
                query,
                (guild_id, user_id, tag),
            )
            await self.database.commit()

    @override
    async def update_greeter(
        self,
        guild_id: int,
        user_id: int,
        greeter: bool,
    ) -> None:
        async with self.database.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE tags
                SET greeter = ?
                WHERE guild_id = ? AND user_id = ?""",
                (greeter, guild_id, user_id),
            )
        await self.database.commit()

    @override
    async def get_greeter(self, guild_id: int, user_id: int) -> bool:
        async with self.database.cursor() as cursor:
            await cursor.execute(
                "SELECT greeter FROM tags WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            )
            rows = await cursor.fetchall()
            if len(rows) == 0:
                return False
            if len(rows) > 1:  # There should never be duplicate users.
                raise DatabaseIntegrityError
            return bool(rows[0][0])

    @override
    async def get_friend_suggestions(self, guild_id: int, user_id: int) -> list[tuple[int, list[str]]]:
        async with self.database.cursor() as cursor:
            user_tags = await self.get_tags(guild_id, user_id)

            if not user_tags:
                return []

            query = """
                SELECT t.user_id, t.tag
                FROM tags t
                WHERE t.user_id  IN (
                    SELECT t2.user_id
                    FROM tags t1
                    JOIN tags t2 ON t1.tag = t2.tag
                    WHERE t1.user_id = ? AND
                    t2.user_id != t1.user_id AND
                    t1.guild_id = t2.guild_id AND
                    t2.greeter = TRUE
                )
            """
            await cursor.execute(query, (user_id,))

            result_any_tags: list[tuple[int, str]] = await cursor.fetchall()  # pyright: ignore[reportAssignmentType]

            # Limit to top 10 users with best ratio of tags in common
            return await suggest_friends(result_any_tags, 10, user_tags)


async def group_friends(result: list[tuple[int, str]]) -> dict[int, set[str]]:
    # Group the results by Discord ID
    suggestions: defaultdict[int, set[str]] = defaultdict(set)
    for suggested_user_id, tag in result:
        suggestions[suggested_user_id].add(tag)
    return dict(suggestions)


async def suggest_friends(
    result: list[tuple[int, str]],
    limit: int,
    user_tags: list[str],
) -> list[tuple[int, list[str]]]:
    suggestions = await group_friends(result)
    deduplicated_user_tags = set(user_tags)

    def key(tags: set[str]) -> float:
        """Use ratio of tags in common:total tags to prevent gaming the system by having every tag."""
        return len(deduplicated_user_tags & tags) / len(deduplicated_user_tags | tags)

    # Limit to top `limit` users with most common tags
    res = sorted(suggestions.items(), key=lambda x: (key(x[1]), x[0]), reverse=True)[:limit]
    return [(k, sorted(v)) for k, v in res]
