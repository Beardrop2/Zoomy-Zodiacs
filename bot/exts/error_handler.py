from contextlib import suppress

from disnake import ApplicationCommandInteraction, Color, Embed, InteractionResponded
from disnake.ext.commands import BotMissingPermissions, Cog, CommandError
from disnake.ui.button import Button

from bot.bot import Bot
from bot.errors import DatabaseNotConnectedError


class ErrorHandler(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_slash_command_error(
        self,
        interaction: ApplicationCommandInteraction,
        error: CommandError,
    ) -> None:
        self.bot.logger.exception(error)

        with suppress(InteractionResponded):
            await interaction.response.defer()

        if isinstance(error, BotMissingPermissions):
            await interaction.followup.send(
                "Sorry, I don't have permission to do that."
                "\n-# 💡 Ensure I have the correct permissions and try again.",
                ephemeral=True,
            )
            return

        embed = Embed(
            title="😬 Oops! An error occurred.",
            description=f"```\n{error}\n```",
            color=Color.red(),
        )
        embed.set_footer(text="Please report this issue on our GitHub repository.")

        if isinstance(error, DatabaseNotConnectedError):
            embed.description = "Database not connected"

        await interaction.followup.send(
            embed=embed,
            components=[
                Button(emoji="🚩", label="Report", url="https://github.com/Beardrop2/Zoomy-Zodiacs/issues/new"),
            ],
        )


def setup(bot: Bot) -> None:
    bot.add_cog(ErrorHandler(bot))
