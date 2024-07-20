import disnake
from disnake.ext.commands import Bot, Cog, slash_command


class Test(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="ping", description="A simple ping command.")
    async def ping(self, interaction: disnake.AppCommandInteraction) -> None:
        await interaction.response.send_message(f"Pong! {self.bot.latency * 1000:.2f}ms")


def setup(bot: Bot) -> None:
    bot.add_cog(Test(bot))
