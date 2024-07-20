import typing

import aiosqlite
import disnake
from disnake.ext.commands import Cog, slash_command

from bot.bot import Bot
from bot.errors import DatabaseNotConnectedError

TagType = typing.Literal[
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


class Tags(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(description="Add a user tag to yourself")
    async def add_tag(self, interaction: disnake.AppCommandInteraction, tag: TagType) -> None:
        db = self.bot.database
        if db is None:
            raise DatabaseNotConnectedError

        # TODO: Move user setup somewhere else
        tag_text = "!" + tag
        async with db:
            await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, tags TEXT)")
            try:
                await db.execute("INSERT INTO users VALUES (?, ?)", (interaction.user.id, tag_text))
            except aiosqlite.IntegrityError:
                await db.execute("UPDATE users SET tags = tags || ? WHERE id = ?", (tag_text, interaction.user.id))
            await db.commit()

        await interaction.response.send_message(f"Added tag `{tag}` to `{interaction.user.id}`")


def setup(bot: Bot) -> None:
    bot.add_cog(Tags(bot))
