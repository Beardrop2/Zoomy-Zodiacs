import contextlib
import logging

import aiosqlite
import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot, errors
from rich.logging import RichHandler

import bot.errors
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
        file_formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s", "%Y-%m-%d:%H:%M:%S")
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

    async def on_slash_command_error(
        self,
        interaction: ApplicationCommandInteraction,
        exception: errors.CommandError,
    ) -> None:
        self.logger.exception(exception)
        with contextlib.suppress(disnake.errors.InteractionResponded):
            await interaction.response.defer()
        if isinstance(exception, bot.errors.DatabaseNotConnectedError):
            await interaction.followup.send("Database is not connected", ephemeral=True)
            return
        if isinstance(exception, errors.BotMissingPermissions):
            await interaction.followup.send(f"Sorry! I don't have permission to do that [{exception}]", ephemeral=True)
            return
        await interaction.followup.send(f"Oops! An error occurred: {exception}", ephemeral=True)
