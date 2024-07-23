from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the bot.

    This is a subclass of `pydantic_settings.BaseSettings` that loads settings
    in the environment variables starting with `ZZ_`. For example, the field
    `discord_bot_token` will be read from `ZZ_DISCORD_BOT_TOKEN`.

    Alongside reading from the environment variables passed in, it also loads
    them from a `.env` file if it exists.

    Attributes:
        discord_bot_token: The Discord bot token. You may retrieve this from the
                           "Bot" tab of your Discord application.
        database_path: The path to the SQLite database.
    """

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ZZ_")

    discord_bot_token: str
    database_path: str = "zz.db"
