import json
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
        prize_setup(db_filename)
        self.db = sqlite3.connect(db_filename)


    def get_tickets(self, user: disnake.Member) -> int:
        res, = self.db.execute(
            "SELECT sum(ticket_change) FROM ticket_wins WHERE user = ?", (user.id,)).fetchone()
        return res if res else 0

    def award_tickets(self, count: int, user: disnake.Member, game: str) -> None:
        self.db.execute(
            "INSERT INTO ticket_wins (user, game, ticket_change) VALUES (?, ?, ?)", (user.id, game, count))
        self.db.commit()

    def consume_tokens(self, count: int, user: disnake.Member, game: str, token_type: typing.Literal["public", "private"]) -> None:
        self.db.execute("INSERT INTO consumed_tokens (token_type, user, game, token_change) VALUES (?,?, ?, ?)",
                        (token_type, user.id, game, count))
        self.db.commit()

    def get_tokens(self, user: disnake.Member, token_type: typing.Literal["public", "private"], hours: int = default_bucket_hours) -> int:
        cur = self.db.execute(
            "SELECT sum(token_change) FROM consumed_tokens WHERE user = ? and datetime > datetime('now', ?)", (user.id, f"{-hours} hour"))
        res = cur.fetchall()[0][0] or 0
        return 9 - res

    def award_prize(self, user: disnake.Member, game: str, prize: int) -> None:
        self.db.execute(
            "INSERT INTO prize_wins (user, game, prize) VALUES (?, ?, ?)", (user.id, game, prize))
        self.db.commit()

    def get_prize_wins(self, user: disnake.Member) -> list:
        return self.db.execute("SELECT * FROM prize_wins WHERE user = ?", (user.id,)).fetchall()

    def award_random_prize(self, user: disnake.Member, game: str, rarity: int) -> int:
        self.db.execute(
            "INSERT INTO prize_wins (user, game, prize) SELECT ?, ?, prizes.id from prizes WHERE rarity = ? order by random() limit 1",
            (user.id, game, rarity))
        res = self.db.execute(
            "select prize from prize_wins where rowid = last_insert_rowid()")
        self.db.commit()
        return res.fetchall()[0]

    def get_thread_for_user(self, user: disnake.Member) -> str:
        res = self.db.execute("select thread from threads where user=?",(user.id,)) or None
        thread = res.fetchone()
        if thread:
            thread = thread[0]
        return thread

    def add_thread_for_user(self, user: disnake.Member, thread: disnake.Thread):
        self.db.execute("INSERT INTO threads (user, thread) VALUES (?, ?)", (user.id, thread.id))
        self.db.commit()

    def create_web_game_session(self, user: disnake.Member, game: str, additional_context: dict = {}) -> str:
        additional_context["ts"] = datetime.datetime.now().timestamp()
        token = jwt.make_token(user, additional_context)
        cur = self.db.execute(
            "INSERT INTO web_game_sessions (user, game, status, session_token) VALUES (?, ?, 0, ?)", (user.id, game, token))
        self.db.commit()
        return token

    def play_web_game_session(self, token) -> bool:
        '''Starts an existing, issued game session.'''
        # Do we have any?
        res = self.db.execute(
            "SELECT * FROM web_game_sessions WHERE session_token = ? and status = 0", (token,)).fetchall()
        if len(res) == 0:
            return False
        # Burn token
        time_played = datetime.datetime.now()
        self.db.execute(
            "UPDATE web_game_sessions SET status = 1, time_played = ? WHERE session_token = ? and status = 0", (time_played, token))
        self.db.commit()
        return True

    def submit_game_results(self, token: str, points: int) -> tuple[bool, str]:
        '''Submit completed session'''
        try:
            decrypted_token = jwt.decrypt_token(
                token)  # Confirm token issued by us
        except:
            return False, "Malformed/Altered/Foreign Token"
        res = self.db.execute(
            "SELECT * FROM web_game_sessions WHERE session_token = ? and status = 1", (token,)).fetchall()
        if len(res) == 0:
            return False, "Invalid Token"
        time_finished = datetime.datetime.now()
        self.db.execute(
            "UPDATE web_game_sessions SET status = 2, points = ?, time_finished = ? WHERE session_token = ? and status = 1", (points, time_finished, token))
        self.db.commit()
        return True, "Valid."

    def get_prize(self, id: int):
        return self.db.execute("select * from prizes where id = ?", (id,)).fetchall()[0]

    def get_prize_wins_by_user(self, member: disnake.Member):
        return self.db.execute("select * from prize_wins where user = ?", (member.id,)).fetchall()

    def get_all_prizes(self):
        name_list = self.db.execute("select name from prizes").fetchall()
        final_list = []
        for n in name_list:
            t, = n
            final_list.append(t)
        return final_list

    def add_new_prize(self, name, description, rarity, image, preview):
        self.db.execute("INSERT INTO prizes (name, description, rarity, image) VALUES (?, ?, ?, ?)", (name, description, rarity, image, preview))
        self.db.commit()
        return


    def get_game_data(self, game: str, user: disnake.Member):
        return self.db.execute("select data from game_data where game = ? and user = ?", (game, user.id)).fetchone()

    def set_game_data(self, game: str, user: disnake.Member, data: str) -> None:
        temp_data = self.db.execute(
            "select data from game_data where game = ? and user = ?", (game, user.id)).fetchone()

        if temp_data:
            self.db.execute(
                "UPDATE game_data SET data = ? WHERE game = ? and user = ?", (data, game, user.id))
        else:
            self.db.execute(
                "INSERT INTO game_data (game, user, data) VALUES (?, ?, ?)", (game, user.id, data))
        self.db.commit()

    # Sets up the Prize Database from store.json
    # This fucking code. DID NOT. Work. NO matter what we did.
    # The database was ALWAYS locked.
    # After an hour of troubleshooting, I said "fuck it" and asked ChatGPT to try and fix it instead
    # ChatGPT changed it from 'db = sqlite3.connect(file)' to 'with sqlite3.connect(file) as db:' IN THEORY, this should be identical to what we already did.
    # I have no fucking idea why that worked. But it did. So I am documenting my insanity here.
def prize_setup(file: str):
    try:
        with sqlite3.connect(file) as db:
            with open('store.json', 'r') as file:
                raw_data = json.load(file)
            cur = db.cursor()
            cur.execute("DELETE FROM prizes")
            for prize in raw_data:
                db.execute("INSERT INTO prizes (id, name, description, rarity, image, preview) VALUES (?, ?, ?, ?, ?, ?)",
                           (prize['id'], prize['name'], prize['description'], prize['rarity'], prize['image'], prize['preview']))
    except sqlite3.OperationalError as e:
        print(f"Error in prize_setup: {e}")
def make_database(file: str):
    schema = open("schema.sql").read()
    db = sqlite3.connect(file)
    db.executescript(schema)
    db.commit()

