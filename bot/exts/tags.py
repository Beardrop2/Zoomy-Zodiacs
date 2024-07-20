import typing

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
        if self.bot.tag_repository is None:
            raise DatabaseNotConnectedError

        await self.bot.tag_repository.add(interaction.author.id, tag)
        await interaction.response.send_message(f"Added tag `{tag}` to {interaction.user}")


def setup(bot: Bot) -> None:
    bot.add_cog(Tags(bot))
