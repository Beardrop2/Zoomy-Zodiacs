from disnake.ext.commands import CommandError


class DatabaseNotConnectedError(CommandError):
    pass


class UserNotMemberError(CommandError):
    pass
