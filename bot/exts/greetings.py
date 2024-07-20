import contextlib

import disnake
from disnake.ext.commands import Cog, slash_command
from disnake.role import Role

from bot.bot import Bot


async def get_greeter_role(inter: disnake.Interaction) -> Role:
    for role in inter.guild.roles:
        if role.name.lower() == "greeter":
            return role
    return await inter.guild.create_role(name="greeter")


class Greetings(Cog):
    """Cog for introducing friends to new members."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        @self.bot.listen("on_button_click")
        async def button_listener(inter: disnake.MessageInteraction) -> None:
            """Listen to button events."""
            with contextlib.suppress(disnake.errors.InteractionResponded):
                await inter.response.defer()
            greeters_role = await get_greeter_role(inter)
            if inter.author != inter.message.interaction.user:
                await inter.followup.send("This is not your button", ephemeral=True)
                return
            match inter.component.custom_id:  # TODO: match the original interaction author
                case "add_greeter":
                    await inter.author.add_roles(greeters_role)
                    await inter.message.edit(
                        "Click the button to discontinue acting as a greeter",
                        components=[
                            disnake.ui.Button(
                                label="Remove role Greeter",
                                style=disnake.ButtonStyle.danger,
                                custom_id="remove_greeter",
                            ),
                        ],
                    )
                case "remove_greeter":
                    await inter.author.remove_roles(greeters_role)
                    await inter.message.edit(
                        "Click the buttons to become a greeter",
                        components=[
                            disnake.ui.Button(
                                label="Add role Greeter",
                                style=disnake.ButtonStyle.success,
                                custom_id="add_greeter",
                            ),
                        ],
                    )
                case _:
                    await inter.followup.send("Invalid button", ephemeral=True)
            await inter.response.defer()

    @slash_command(description="To become a greeter")
    async def greeters(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Add or remove user's Greeter role."""
        greeter_role = await get_greeter_role(inter)
        if greeter_role in inter.author.roles:
            await inter.response.send_message(
                "Click the buttons to no longer be a greeter",
                components=[
                    disnake.ui.Button(
                        label="Remove role Greeter",
                        style=disnake.ButtonStyle.danger,
                        custom_id="remove_greeter",
                    ),
                ],
            )
        else:
            await inter.response.send_message(
                "Click the buttons to become a greeter",
                components=[
                    disnake.ui.Button(
                        label="Add role Greeter",
                        style=disnake.ButtonStyle.success,
                        custom_id="add_greeter",
                    ),
                ],
            )


def setup(bot: Bot) -> None:
    """Load the Greetings cog."""
    bot.add_cog(Greetings(bot))
