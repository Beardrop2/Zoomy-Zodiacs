import logging

import aiosqlite
from disnake.ext.commands import InteractionBot
from rich.logging import RichHandler

from bot.settings import Settings


class Bot(InteractionBot):
    def __init__(self) -> None:
        super().__init__()

        self.settings = Settings()  # pyright: ignore[reportCallIssue]

        self._configure_logging()
        self.logger = logging.getLogger("zz")

        self.database: aiosqlite.Connection | None = None

        self.load_extensions("bot/exts")

    def _configure_logging(self) -> None:
        file_handler = logging.FileHandler("zz.log", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
            handlers=[RichHandler(), file_handler],
        )

    async def connect_to_database(self) -> None:
        # TODO: Use PostgreSQL
        self.database = aiosqlite.connect(self.settings.database_path)
