import ollama
from disnake import AppCmdInter, Guild, TextChannel, VoiceChannel
from disnake.ext.commands import Cog, NoPrivateMessage, guild_only, slash_command

from bot.bot import Bot

SYSTEM_PROMPT_TEMPLATE = """
You are a helpful AI assistant guiding new Discord server members. Here is the
list of channels:

{server_summary}

When mentioning a channel, use the format <#Channel ID> as it renders to a
clickable link to the channel on Discord.

It is essential that you provide answers that are short and concise without
sacrificing any meaning. Do not respond to non-server related questions.
"""


class Help(Cog):
    """Cog for helping members with general questions."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @guild_only()
    @slash_command()
    async def help(self, question: str, inter: AppCmdInter) -> None:
        """Get general AI help."""

        if inter.guild is None:
            raise NoPrivateMessage

        host = self.bot.settings.ollama_host
        model = self.bot.settings.ollama_model

        await inter.response.defer()

        messages: list[ollama.Message] = [
            {"role": "system", "content": build_system_prompt(inter.guild)},
            {"role": "user", "content": question},
        ]

        client = ollama.AsyncClient(host)
        response = await client.chat(model, messages)
        response_text: str = response["message"]["content"]

        await inter.send(response_text)


def build_system_prompt(guild: Guild) -> str:
    server_summary = f"Server Name: {guild.name}"
    # server_summary = f"Invite: {guild.invites[0]}" TODO: find a better way to get invites
    server_summary += "*Channels info*"

    for channel in guild.channels:
        server_summary += f"Name: {channel.name}\n"
        server_summary += f"ID: {channel.id}\n"

        if isinstance(channel, TextChannel):
            server_summary += "Type: Text Channel\n"
            server_summary += f"Topic: {channel.topic}\n\n"

        elif isinstance(channel, VoiceChannel):
            server_summary += "Type: Voice Channel\n\n"

    server_summary += "*Roles info*"
    for role in guild.roles:
        server_summary += f"Name: {role.name}"
        server_summary += "Type: Role"
        # server_summary += f"Permissions: {role.permissions}" TODO: turn the permission into text

    # TODO: add the bots command info?

    return SYSTEM_PROMPT_TEMPLATE.format(server_summary=server_summary)


def setup(bot: Bot) -> None:
    """Load the Help cog."""
    bot.add_cog(Help(bot))
