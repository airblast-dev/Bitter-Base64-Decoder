

from os import getenv
database_options = {"MongoDB"}


if (db_choice:=getenv("DATABASE")) not in database_options:
    raise ValueError("Invalid database entered.")
elif getenv("CONNECTION_STR") is None and db_choice == "MongoDB":
    raise ValueError("Please provide a connection string.")
if db_choice == "MongoDB":
    from .database.bittermong import BitterDB