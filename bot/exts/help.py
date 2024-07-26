from disnake import AppCmdInter
from disnake.ext.commands import Cog, slash_command
from ollama import AsyncClient

from bot.bot import Bot

SYSTEM_STRING = "It is essential that you provide answers that are short and concise without sacrificing any meaning."


class Help(Cog):
    """Cog for helping members with general questions."""

    def __init__(self, bot: Bot, ollama_host: str, ollama_model: str) -> None:
        self.bot = bot
        self._host = ollama_host
        self._model = ollama_model

    @slash_command()
    async def help(self, question: str, inter: AppCmdInter) -> None:
        """Get general AI help."""
        await inter.response.defer()

        messages = [
            {"role": "system", "content": SYSTEM_STRING},
            {"role": "user", "content": question},
        ]
        response = await AsyncClient(host=self._host).chat(model=self._model, messages=messages)
        await inter.send(response)


def setup(bot: Bot) -> None:
    """Load the Help cog."""
    bot.add_cog(
        cog=Help(
            bot=bot,
            ollama_host=bot.settings.ollama_host,
            ollama_model=bot.settings.ollama_model,
        ),
    )
