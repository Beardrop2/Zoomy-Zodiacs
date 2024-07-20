from abc import ABC, abstractmethod
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
