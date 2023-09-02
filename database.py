import sqlite3
import typing
import os
import disnake

default_bucket_hours = 3
db_filename = "carnival.db"
class Database:
    db: sqlite3.Connection
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance
    def __init__(self) -> None:
        if not os.path.exists(db_filename):
            make_database(db_filename)
        self.db = sqlite3.connect(db_filename)
    def win_tickets(self, count: int, user: disnake.User, game: str) -> None:
        self.db.execute("INSERT INTO tickets (user_id, game, count) VALUES (?, ?, ?)", (user.id, game, count))
        self.db.commit()
    def consume_tokens(self, count: int, user: disnake.User, game: str, token_type: str) -> None:
        self.db.execute("INSERT INTO consumed_tokens (token_type, user, game, token_change) VALUES (?,?, ?, ?)", (token_type, user.id, game, count))
        self.db.commit()
    def award_random_prize(self, user: disnake.User, game: str) -> None:
        self.db.execute("INSERT INTO prize_wins (user, game, prize) SELECT ?, ?, prizes.id from prizes order by random() limit 1", (user.id, game))
        self.db.commit()
    def get_used_tokens(self, user: disnake.User, hours: int = default_bucket_hours) -> int:
        cur = self.db.execute("SELECT sum(token_change) FROM consumed_tokens WHERE user = ? and datetime > datetime('now', ?)", (user.id, f"{-hours} hour"))
        return cur.fetchall()[0]
    def get_tickets(self, user: disnake.User) -> int:
        return self.db.execute("SELECT sum(count) FROM tickets_wins WHERE user_id = ?", (user.id,)).fetchone()[0]


def make_database(file: str):
    schema = open("schema.sql").read()
    db = sqlite3.connect(file)
    db.executescript(schema)
    db.commit()