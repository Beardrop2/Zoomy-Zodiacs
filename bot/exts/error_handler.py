from contextlib import suppress

from disnake import ApplicationCommandInteraction, Color, Embed, InteractionResponded
from disnake.ext.commands import BotMissingPermissions, Cog, CommandError
from disnake.ui.button import Button

from bot.bot import Bot
from bot.errors import DatabaseNotConnectedError


class ErrorEmbed(Embed):
    def __init__(self, error: Exception | str, *, internal: bool = True) -> None:
        super().__init__(
            title="😬 Oops! An error occurred.",
            color=Color.red(),
        )

        self.internal = internal
        self.set_error(error)

    def set_tip(self, tip: str) -> None:
        self.set_footer(text=f"💡 {tip}")

    def set_error(self, error: Exception | str) -> None:
        self.description = f"```\n{error}\n```" if not isinstance(error, str) else error

        if self.internal:
            # fmt: off
            self.description += "\n-# Please report this issue on [our GitHub repository](https://github.com/Beardrop2/Zoomy-Zodiacs)."
            # fmt: on


class ReportButton(Button[None]):
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

        embed = ErrorEmbed(error)

        if isinstance(error, DatabaseNotConnectedError):
            embed.internal = True
            embed.set_error("Database not connected")

        if isinstance(error, BotMissingPermissions):
            embed.internal = False
            embed.set_error("I don't have the correct permissions to do that.")
            embed.set_tip("Ensure my role is high enough in the role hierarchy.")

        await interaction.followup.send(
            embed=embed,
            components=[ReportButton()] if embed.internal else [],
        )


def setup(bot: Bot) -> None:
    bot.add_cog(ErrorHandler(bot))
