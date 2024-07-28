from disnake import AllowedMentions, AppCmdInter, Color, Embed, Member
from disnake.ext.commands import Cog, slash_command

from bot.bot import Bot
from bot.errors import DatabaseNotConnectedError
from bot.exts.greetings import GREETER_ROLE_NAME, get_greeter_role
from bot.repositories.tags import TagType


class Tags(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command()
    async def tag(self, _: AppCmdInter) -> None:
        """Manage your tags."""

    @tag.sub_command()
    async def add(self, interaction: AppCmdInter, tag: TagType) -> None:
        """Add a user tag to yourself."""

        if self.bot.tag_repository is None:
            raise DatabaseNotConnectedError

        guild = interaction.guild
        user = interaction.author
        greeter_role = await get_greeter_role(guild)
        has_greeter_role = greeter_role in user.roles

        await self.bot.tag_repository.add_tag(
            guild_id=interaction.guild.id,
            user_id=interaction.author.id,
            tag=tag,
            greeter=has_greeter_role,
        )
        await interaction.response.send_message(f"Added tag `{tag}` to {user}", ephemeral=True)

    @tag.sub_command()
    async def remove(self, interaction: AppCmdInter, tag: TagType) -> None:
        """Remove a user tag from yourself."""

        tag_repo = self.bot.tag_repository
        if tag_repo is None:
            raise DatabaseNotConnectedError

        user_id = interaction.user.id
        user_tags = await tag_repo.get(user_id)

        if tag not in user_tags:
            message = f"❌ You don't currently have the `{tag}` tag."
            await interaction.response.send_message(message, ephemeral=True)
            return

        await tag_repo.remove(user_id, tag)
        message = f"✅ Removed tag `{tag}` from {interaction.user}"
        await interaction.response.send_message(message, ephemeral=True)

    @tag.sub_command()
    async def suggest_friends(self, interaction: AppCmdInter) -> None:
        """Suggest friends for you based on your tags."""

        await interaction.response.defer()

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        tag_repo = self.bot.tag_repository
        if not tag_repo:
            raise DatabaseNotConnectedError

        suggestions = []
        candidates = await tag_repo.get_friend_suggestions(guild_id, user_id)

        for candidate_user_id, common_tags in candidates:
            member = await self.bot.fetch_user(candidate_user_id)
            member_roles = [role.name for role in member.roles]
            member_mention = member.mention
            tag_list = ", ".join(f"`{tag}`" for tag in common_tags)
            if GREETER_ROLE_NAME in member_roles:
                suggestions.add(tuple(member_mention, tag_list))

        if suggestions == []:
            message = "❌ No friend suggestions found. Try adding more tags!"
            await interaction.followup.send(message, ephemeral=True)
            return

        # Construct the response message
        response = "Here are some friend suggestions based on your tags:\n\n"
        for member_mention, tag_list in suggestions:
            response += f"- {member_mention}\n  Common tags: {tag_list}\n\n"

        embed = Embed(title="🫂 Friend suggestions", description=response, color=Color.blue())

        await interaction.followup.send(embed=embed, ephemeral=True)

    @tag.sub_command()
    async def info(self, interaction: AppCmdInter, member: Member) -> None:
        """View tags and info of given member."""

        tag_repo = self.bot.tag_repository
        if not tag_repo:
            raise DatabaseNotConnectedError

        tag_list = await tag_repo.get_tags(interaction.guild.id, member.id)

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
