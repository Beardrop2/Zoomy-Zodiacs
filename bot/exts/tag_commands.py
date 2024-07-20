import typing

import aiosqlite
import disnake
from disnake.ext.commands import Bot, Cog, slash_command

TAGS = typing.Literal[
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

    @slash_command(name="add_tag", description="Add a user tag to yourself")
    async def ping(self, interaction: disnake.AppCommandInteraction, tags: TAGS) -> None:
        await interaction.response.send_message(f"Added tag `{tags}` to `{interaction.user.id}`")
        tags = "!" + tags
        conn = await aiosqlite.connect("users.db")
        await conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, tags TEXT)")
        try:
            await conn.execute("INSERT INTO users VALUES (?, ?)", (interaction.user.id, tags))
        except aiosqlite.IntegrityError:
            await conn.execute("UPDATE users SET tags = tags || ? WHERE id = ?", (tags, interaction.user.id))
        await conn.commit()
        await conn.close()


def setup(bot: Bot) -> None:
    bot.add_cog(Tags(bot))
