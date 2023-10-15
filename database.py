import sqlite3
import typing
import os
import disnake
import idtools
import datetime
import time

jwt = idtools.Token()

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
    def get_tickets(self, user: disnake.Member) -> int:
        res = self.db.execute("SELECT sum(ticket_change) FROM ticket_wins WHERE user = ?", (user.id,)).fetchone()
        return res if res else 0
    def award_tickets(self, count: int, user: disnake.Member, game: str) -> None:
        self.db.execute("INSERT INTO ticket_wins (user, game, ticket_change) VALUES (?, ?, ?)", (user.id, game, count))
        self.db.commit()
    def consume_tokens(self, count: int, user: disnake.Member, game: str, token_type: str) -> None:
        self.db.execute("INSERT INTO consumed_tokens (token_type, user, game, token_change) VALUES (?,?, ?, ?)", (token_type, user.id, game, count))
        self.db.commit()
    def get_used_tokens(self, user: disnake.Member, hours: int = default_bucket_hours) -> int:
        cur = self.db.execute("SELECT sum(token_change) FROM consumed_tokens WHERE user = ? and datetime > datetime('now', ?)", (user.id, f"{-hours} hour"))
        return cur.fetchall()[0]
    def award_prize(self, user: disnake.Member, game: str, prize: int) -> None:
        self.db.execute("INSERT INTO prize_wins (user, game, prize) VALUES (?, ?, ?)", (user.id, game, prize))
        self.db.commit()
    def get_prize_wins(self, user: disnake.Member) -> list:
        return self.db.execute("SELECT * FROM prize_wins WHERE user = ?", (user.id,)).fetchall()
    def award_random_prize(self, user: disnake.Member, game: str) -> None:
        self.db.execute("INSERT INTO prize_wins (user, game, prize) SELECT ?, ?, prizes.id from prizes order by random() limit 1", (user.id, game))
        self.db.commit()
    def create_web_game_session(self, user: disnake.Member, game: str, additional_context: dict = {}) -> str:
        additional_context["ts"] = datetime.datetime.now().timestamp()
        token = jwt.make_token(user, additional_context)
        cur = self.db.execute("INSERT INTO web_game_sessions (user, game, status, session_token) VALUES (?, ?, 0, ?)", (user.id, game, token))
        self.db.commit()
        return token
    def play_web_game_session(self, token) -> bool:
        '''Starts an existing, issued game session.'''
        #Do we have any?
        res = self.db.execute("SELECT * FROM web_game_sessions WHERE session_token = ? and status = 0", (token,)).fetchall()
        if len(res) == 0:
            return False
        #Burn token
        time_played = datetime.datetime.now()
        self.db.execute("UPDATE web_game_sessions SET status = 1, time_played = ?, session_token = ? and status = 0", (time_played, token))
        self.db.commit()
        return True
    def submit_game_results(self, token: str, points: int) -> tuple[bool, str]:
        '''Submit completed session'''
        try:
            decrypted_token = jwt.decrypt_token(token) #Confirm token issued by us
        except:
            return False, "Malformed/Altered/Foreign Token"
        res = self.db.execute("SELECT * FROM web_game_sessions WHERE session_token = ? and status = 1", (token,)).fetchall()
        if len(res) == 0:
            return False, "Invalid Token"
        time_finished = datetime.datetime.now()
        self.db.execute("UPDATE web_game_sessions SET status = 2 and points = ? and time_finished = ? WHERE session_token = ? and status = 1", (points, time_finished, token))
        self.db.commit()
        return True, "Valid."

def make_database(file: str):
    schema = open("schema.sql").read()
    db = sqlite3.connect(file)
    db.executescript(schema)
    db.commit()