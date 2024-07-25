from disnake import AppCmdInter
from disnake.ext.commands import Cog, slash_command
from ollama import AsyncClient

from bot.bot import Bot

SYSTEM_STRING = "It is essential that you provide answers that are short and concise without sacrificing any meaning."


class Help(Cog):
    """Cog for helping members with general questions."""

    @slash_command()
    async def help(self, question: str, inter: AppCmdInter) -> None:
        """Get general AI help."""
        await inter.response.defer()

        messages = [
            {"role": "system", "content": SYSTEM_STRING},
            {"role": "user", "content": question},
        ]
        response = await AsyncClient().chat(model="phi3", messages=messages)
        await inter.send(response)


def setup(bot: Bot) -> None:
    """Load the Help cog."""
    bot.add_cog(Help(bot))
