from typing import cast, get_args, override

from disnake import AllowedMentions, AppCmdInter, Color, Embed, Member, MessageInteraction, SelectOption
from disnake.ext.commands import Cog, slash_command
from disnake.ui import StringSelect, View

from bot.bot import Bot
from bot.errors import DatabaseNotConnectedError
from bot.repositories.tags import TagType


class TagsDropdown(StringSelect[None]):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        options = [
            SelectOption(label=tag, description=f"You're interested in {tag}")  # pyright: ignore[reportAny]
            for tag in get_args(TagType)  # pyright: ignore[reportAny]
        ]

        super().__init__(
            placeholder="Choose your tags",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    @override
    async def callback(self, interaction: MessageInteraction) -> None:
        tag_repo = self.bot.tag_repository
        if tag_repo is None:
            raise DatabaseNotConnectedError

        await tag_repo.add(interaction.author.id, cast(list[TagType], self.values))

        s = "s" if len(self.values) > 1 else ""  # Fix grammar if multiple tags are added
        added_tags = ", ".join(f"`{tag}`" for tag in self.values)

        await interaction.send(f"Added tag{s} {added_tags} to {interaction.user}", ephemeral=True)


class DropdownView(View):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.add_item(TagsDropdown(bot=bot))


class Tags(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command()
    async def tag(self, _: AppCmdInter) -> None:
        """Manage your tags."""

    @tag.sub_command()
    async def add(self, interaction: AppCmdInter) -> None:
        """Add user tag(s) to yourself."""

        view = DropdownView(self.bot)
        await interaction.response.send_message("What are you interested in?", view=view)

    @tag.sub_command()
    async def remove(self, interaction: AppCmdInter, tag: TagType) -> None:
        """Remove a user tag from yourself."""

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

    @tag.sub_command()
    async def suggest_friends(self, interaction: AppCmdInter) -> None:
        """Suggest friends for you based on your tags."""

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
        for suggested_user_id, common_tags in suggestions:
            user = await self.bot.fetch_user(suggested_user_id)
            tag_list = ", ".join(f"`{tag}`" for tag in common_tags)
            response += f"- {user.mention}\n  Common tags: {tag_list}\n\n"

        embed = Embed(title="🫂 Friend suggestions", description=response, color=Color.blue())

        await interaction.followup.send(embed=embed, ephemeral=True)

    @tag.sub_command()
    async def info(self, interaction: AppCmdInter, member: Member) -> None:
        """View tags and info of given member."""

        tag_repo = self.bot.tag_repository
        if not tag_repo:
            raise DatabaseNotConnectedError

        tag_list = await tag_repo.get(member.id)

        name = member.name
        if member.nick:
            name = f"{member.nick} ({name})"

        # [1:] to remove the @everyone in the roles list
        info_dict = {
            "Roles": ", ".join(role.mention for role in member.roles[1:]),
            "Tags": ", ".join(f"`{tag}`" for tag in tag_list),
        }

        # The join date info may not be available on some users
        if member.joined_at is not None:
            info_dict["Joined"] = f"<t:{int(member.joined_at.timestamp())}:R>"

        content = "**Member Info**\n"
        for key, value in info_dict.items():
            if value != "":
                content += f"{key}: {value}\n"
            else:
                # If roles/tags are empty for the user, display "None"
                content += f"{key}: None\n"

        user_info = Embed(title=name, description=content)
        user_info.set_thumbnail(member.display_avatar.url)

        await interaction.send(embed=user_info, allowed_mentions=AllowedMentions.none())


def setup(bot: Bot) -> None:
    bot.add_cog(Tags(bot))
