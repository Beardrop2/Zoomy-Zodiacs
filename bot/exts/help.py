import ollama
from disnake import AppCmdInter
from disnake.ext.commands import Cog, slash_command

from bot.bot import Bot

SYSTEM_PROMPT = "It is essential that you provide answers that are short and concise without sacrificing any meaning."


class Help(Cog):
    """Cog for helping members with general questions."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command()
    async def help(self, question: str, inter: AppCmdInter) -> None:
        """Get general AI help."""

        host = self.bot.settings.ollama_host
        model = self.bot.settings.ollama_model

        await inter.response.defer()

        messages: list[ollama.Message] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        client = ollama.AsyncClient(host)
        response = await client.chat(model, messages)

        await inter.send(str(response))


def setup(bot: Bot) -> None:
    """Load the Help cog."""
    bot.add_cog(Help(bot))
