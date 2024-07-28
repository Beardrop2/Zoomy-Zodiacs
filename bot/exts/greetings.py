from disnake import AppCmdInter, ButtonStyle, Guild, Member, MessageInteraction, Role, ui
from disnake.ext.commands import Cog, bot_has_permissions, guild_only, slash_command
from disnake.ui import Button, View

from bot.bot import Bot
from bot.errors import DatabaseNotConnectedError, GreeterRoleNotConfigured, UserNotMemberError

# from bot.repositories.tags import

GREETER_ROLE_NAME = "Greeter"


async def setup_greeter_role(guild: Guild) -> Role:
    if GREETER_ROLE_NAME not in guild.roles:
        guild.create_role(name=GREETER_ROLE_NAME)


async def get_greeter_role(guild: Guild) -> Role:
    for role in guild.roles:
        if role.name.lower() == GREETER_ROLE_NAME.lower():
            return role
    raise GreeterRoleNotConfigured


class GreetingRoleView(View):
    @ui.button(label="Be a greeter", style=ButtonStyle.green)
    async def add_or_remove_role(self, button: Button[None], inter: MessageInteraction) -> None:
        tag_repo = self.bot.tag_repository
        if not tag_repo:
            raise DatabaseNotConnectedError

        guild = inter.guild
        if guild is None:
            # The command requires the Manage Guild and Manage Roles permissions,
            # so this should never happen
            return

        member = inter.author
        if not isinstance(member, Member):
            # The author is a member since the command is guild-only, so this
            # should never happen
            raise UserNotMemberError

        greeter_role = await get_greeter_role(guild)
        has_greeter_role = greeter_role in member.roles

        if has_greeter_role:
            await member.remove_roles(greeter_role)
            button.label = "Be a greeter"
            button.style = ButtonStyle.green

        if not has_greeter_role:
            await member.add_roles(greeter_role)
            button.label = "Stop being a greeter"
            button.style = ButtonStyle.red

        await tag_repo.update_greeter(
            guild.id,
            member.id,
            (not has_greeter_role),  # Update the role to have been flipped.
        )
        await inter.response.edit_message(view=self)


"""    @ui.button(label="End Interaction", style=ButtonStyle.red)
    async def end_interaction(self, button: Button[None], inter: MessageInteraction) -> None:
        button.style = ButtonStyle.gray
        for component in self.children:
            component.disabled = True
        await inter.response.edit_message(view=self)
"""  # not added for now


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
            view=GreetingRoleView(),
            ephemeral=True,
        )


def setup(bot: Bot) -> None:
    """Load the Greetings cog."""
    bot.add_cog(Greetings(bot))
