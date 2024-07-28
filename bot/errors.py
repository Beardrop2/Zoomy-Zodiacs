from disnake.ext.commands import CommandError


class DatabaseNotConnectedError(CommandError):
    """Raised when the bot is not connected to the database."""


class UserNotMemberError(CommandError):
    """Raised when `Interaction.author` is not a `Member`."""


class GreeterRoleNotConfiguredError(CommandError):
    """Raised when the guild is missing the Greeter role."""
