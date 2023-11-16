"""Module for interacting with an SQLite database"""

from collections.abc import Sequence

class QueryResult:
    """The result of a query"""
    
    def rows(self) -> Sequence[Sequence[int | float | str | bytes | None]]:
        """The row results, each of which contains the values for all the columns in that row"""
        raise NotImplementedError

    def columns(self) -> Sequence[str]:
        """The names of the columns retrieved in the query"""
        raise NotImplementedError

class SqliteConnection:
    """Represents an open connection to an SQLite database"""
    
    def execute(self, query: str, parameters: Sequence[int | float | str | bytes | None]) -> QueryResult:
        """Execute the specified statement"""
        raise NotImplementedError

def sqlite_open(database: str) -> SqliteConnection:
    """Open a connection to a named database instance.

    If `database` is "default", the default instance is opened.

    An `AssertionError` will be raised if the `name` is not recognized.

    """
    raise NotImplementedError

def sqlite_open_default() -> SqliteConnection:
    """Open a connection to the default database"""
    raise NotImplementedError
