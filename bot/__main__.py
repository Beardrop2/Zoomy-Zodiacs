import asyncio

from bot.bot import Bot


async def main() -> None:
    bot = Bot()
    await bot.connect_to_database()
    await bot.start(bot.settings.discord_bot_token)
    await bot.close_database_connection()


if __name__ == "__main__":
    asyncio.run(main())
