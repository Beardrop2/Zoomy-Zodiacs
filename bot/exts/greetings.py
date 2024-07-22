from disnake import AppCmdInter, ButtonStyle, Guild, Member, MessageInteraction, Role
from disnake.ext.commands import Cog, bot_has_permissions, guild_only, slash_command
from disnake.ui import Button, View, button

from bot.bot import Bot

GREETER_ROLE_NAME = "Greeter"


async def get_greeter_role(guild: Guild) -> Role:
    for role in guild.roles:
        if role.name.lower() == GREETER_ROLE_NAME.lower():
            return role

    return await guild.create_role(name=GREETER_ROLE_NAME)


class GreetingRoleView(View):
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
            return

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

        await inter.response.edit_message(view=self)


class Greetings(Cog):
    """Cog for introducing friends to new members."""

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
