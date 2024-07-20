class DatabaseNotConnectedError(Exception):
    def __str__(self) -> str:
        return "DatabaseNotConnectedError: Database is not connected"
