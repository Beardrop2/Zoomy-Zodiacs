import typing

from disnake import AppCmdInter, Color, Embed
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

    @slash_command(description="Manage tags")
    async def tag(self, _: AppCmdInter) -> None: ...

    @tag.sub_command(description="Add a user tag to yourself")
    async def add(self, interaction: AppCmdInter, tag: TagType) -> None:
        if self.bot.tag_repository is None:
            raise DatabaseNotConnectedError

        await self.bot.tag_repository.add(interaction.author.id, tag)
        await interaction.response.send_message(f"Added tag `{tag}` to {interaction.user}", ephemeral=True)

    @tag.sub_command(description="Remove a user tag from yourself")
    async def remove(self, interaction: AppCmdInter, tag: TagType) -> None:
        tag_repo = self.bot.tag_repository
        if tag_repo is None:
            raise DatabaseNotConnectedError

        user_id = interaction.user.id
        user_tags = await tag_repo.get(user_id)

        if tag not in user_tags:
            await interaction.response.send_message(f"❌ You don't already have the `{tag}` tag.", ephemeral=True)
            return

        await tag_repo.remove(user_id, tag)
        await interaction.response.send_message(f"✅ Removed tag `{tag}` from {interaction.user}", ephemeral=True)

    @tag.sub_command(description="Suggest friends for you based on your tags")
    async def suggest_friends(self, interaction: AppCmdInter) -> None:
        await interaction.response.defer()

        user_id = interaction.user.id

        tag_repo = self.bot.tag_repository
        if not tag_repo:
            raise DatabaseNotConnectedError

        suggestions = await tag_repo.get_friend_suggestions(user_id)

        if not suggestions:
            await interaction.followup.send("❌ No friend suggestions found. Try adding more tags!", ephemeral=True)
            return

        # Construct the response message
        response = "Here are some friend suggestions based on your tags:\n\n"
        for suggested_user_id, common_tags in suggestions.items():
            user = await self.bot.fetch_user(suggested_user_id)
            tag_list = ", ".join(f"`{tag}`" for tag in common_tags)
            response += f"- {user.mention}\n  Common tags: {tag_list}\n\n"

        embed = Embed(title="🫂 Friend suggestions", description=response, color=Color.blue())

        await interaction.followup.send(embed=embed, ephemeral=True)


def setup(bot: Bot) -> None:
    bot.add_cog(Tags(bot))
