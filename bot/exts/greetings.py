from logging import Logger

from disnake import AppCmdInter, ButtonStyle, Guild, Member, MessageInteraction, Role
from disnake.ext.commands import Cog, CommandError, NoPrivateMessage, bot_has_permissions, guild_only, slash_command
from disnake.ui import Button, View, button

from bot.bot import Bot
from bot.repositories.tags import TagRepository

GREETER_ROLE_NAME = "Greeter"


async def setup_greeter_role(guild: Guild) -> Role:
    if GREETER_ROLE_NAME not in guild.roles:
        guild.create_role(name=GREETER_ROLE_NAME)


async def get_greeter_role(guild: Guild) -> Role:
    for role in guild.roles:
        if role.name.lower() == GREETER_ROLE_NAME.lower():
            return role
    raise CommandError


class GreetingRoleView(View):
    def __init__(self, tag_repository: TagRepository, logger: Logger) -> None:
        super().__init__()

        self.tag_repository = tag_repository
        self.logger = logger

    @button(label="Be a greeter", style=ButtonStyle.green)
    async def add_or_remove_role(self, button: Button[None], inter: MessageInteraction) -> None:
        guild = inter.guild
        if guild is None:
            # The command requires the Manage Guild and Manage Roles permissions,
            # so this should never happen
            return

        member = inter.author
        if not isinstance(member, Member):
            # The author is a member since the command is guild-only, so this
            # should never happen
            raise NoPrivateMessage

        greeter_role = await get_greeter_role(guild)
        has_greeter_role = greeter_role in member.roles

        if has_greeter_role:
            button.label = "Be a greeter"
            button.style = ButtonStyle.green
            await member.remove_roles(greeter_role)

        if not has_greeter_role:
            button.label = "Stop being a greeter"
            button.style = ButtonStyle.red
            await member.add_roles(greeter_role)

        await self.tag_repository.update_greeter(
            guild.id,
            member.id,
            (not has_greeter_role),  # Update the role to have been flipped.
        )

        await inter.response.edit_message(view=self)


class Greetings(Cog):
    """Cog for introducing friends to new members."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @bot_has_permissions(manage_guild=True, manage_roles=True)
    @guild_only()
    @slash_command()
    async def greeters(self, inter: AppCmdInter) -> None:
        """Add or remove your Greeter role."""
        await inter.response.send_message(
            content="Click the button to manage your greeter role",
            view=GreetingRoleView(self.bot.tag_repository, self.bot.logger),
            ephemeral=True,
        )


def setup(bot: Bot) -> None:
    """Load the Greetings cog."""
    bot.add_cog(Greetings(bot))
