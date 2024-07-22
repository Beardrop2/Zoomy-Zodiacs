import logging

import aiosqlite
from disnake.ext.commands import InteractionBot
from rich.logging import RichHandler

from bot.repositories.tags import SqliteTagRepository, TagRepository
from bot.settings import Settings


class Bot(InteractionBot):
    def __init__(self) -> None:
        super().__init__()

        self.settings = Settings()  # pyright: ignore[reportCallIssue]

        self._configure_logging()
        self.logger = logging.getLogger("zz")

        self.database_connection: aiosqlite.Connection | None = None
        self.tag_repository: TagRepository | None = None

        self.load_extensions("bot/exts")

    def _configure_logging(self) -> None:
        file_handler = logging.FileHandler("zz.log", encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s:%(levelname)s:%(name)s: %(message)s",
            "%Y-%m-%d:%H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
            datefmt="%X",
            handlers=[RichHandler(), file_handler],
        )

    async def connect_to_database(self) -> None:
        # TODO: Use PostgreSQL
        self.database_connection = await aiosqlite.connect(self.settings.database_path)

        self.tag_repository = SqliteTagRepository(self.database_connection)
        await self.tag_repository.initialize()

    async def close_database_connection(self) -> None:
        if self.database_connection is not None:
            await self.database_connection.close()
