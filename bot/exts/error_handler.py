from contextlib import suppress

from disnake import ApplicationCommandInteraction, Color, Embed, InteractionResponded
from disnake.ext.commands import BotMissingPermissions, Cog, CommandError
from disnake.ui.button import Button

from bot.bot import Bot
from bot.errors import DatabaseNotConnectedError


class ErrorEmbed(Embed):
    def __init__(
        self,
        error: Exception | str,
    ) -> None:
        color = Color.red()
        title = "😬 Oops! An error occurred."

        description = f"```\n{error}\n```" if not isinstance(error, str) else error
        footer_text = (
            "Please report this issue on [our GitHub repository](https://github.com/Beardrop2/Zoomy-Zodiacs)."
        )
        description += f"\n\n{footer_text}"

        super().__init__(title=title, description=description, color=color)


class ReportButton(Button):
    def __init__(self) -> None:
        super().__init__(
            label="Report Error",
            url="https://github.com/Beardrop2/Zoomy-Zodiacs/issues/new",
            emoji="🚩",
        )


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
            embed = ErrorEmbed(
                error="I don't have the correct permissions to do that.",
            )

            embed.set_footer(text="💡 Please ensure my role is high enough in the role hierarchy.")

            await interaction.followup.send(
                embed=embed,
                components=[
                    ReportButton(),
                ],
            )
            return

        embed = ErrorEmbed(error=error)

        if isinstance(error, DatabaseNotConnectedError):
            embed.description = "Database not connected"

        await interaction.followup.send(
            embed=embed,
            components=[
                ReportButton(),
            ],
        )


def setup(bot: Bot) -> None:
    bot.add_cog(ErrorHandler(bot))
