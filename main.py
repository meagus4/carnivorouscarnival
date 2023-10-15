import datetime
import importlib
import os
import sys
import time
import typing
import random
from config import load_config
import fastapi
from fastapi import responses
import asyncio
import database
db = database.Database()
import idtools
tokentools = idtools.Token()
from carnival_types import *
from disnake.ext.commands import Bot, when_mentioned, option_enum
import disnake.ext.tasks as tasks
import random

from load_games import PrivateGameList, PublicGameList, load_private_games, load_public_games

intents: disnake.Intents = disnake.Intents(
    guilds=True,
)

bot = Bot(command_prefix=when_mentioned, intents=intents)
gsm = None
config = load_config()

docs = True
if docs:
    web = fastapi.FastAPI()
else:
    web = fastapi.FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@bot.event
async def on_ready():
    _public = await bot.fetch_channel(config['public_channel'])
    _private = await bot.fetch_channel(config['private_channel'])
    global gsm
    gsm = GameStateManager(_public, _private)
    gsm.start_timed_new_public_game.start()
    print("Ready!")

# Load games
public_game_list: PublicGameList = load_public_games()
private_game_list: PrivateGameList = load_private_games()

PrivateGameName = option_enum(
    dict((name.title(), name) for name in private_game_list.keys()))

PublicGameName = option_enum(
    dict((name.title(), name) for name in public_game_list.keys()))


class GameStateManager:
    # Time until the next public game starts.
    public_game_timer: datetime.datetime
    # Names of the Public Games currently available
    public_game_list: PublicGameList
    # Names of the Private Games currently available.
    private_game_list: PrivateGameList
    private_game_channel: disnake.TextChannel
    public_game_channel: disnake.TextChannel

    def __init__(self, _public, _private):
        self.public_game_timer = datetime.datetime.now()
        self.public_game_list = public_game_list
        self.private_game_list = private_game_list
        self.public_game_channel = typing.cast(disnake.TextChannel, _public)
        self.private_game_channel = typing.cast(disnake.TextChannel, _private)

    async def _start_new_public_game(self, game_name: str | None = None, optional_argument: str | None = None):
        target_channel = self.public_game_channel
        if game_name == None or game_name not in self.public_game_list:
            game_name = random.choice(list(self.public_game_list.keys()))
            game_name = typing.cast(str, game_name)
        game = self.public_game_list[game_name]
        await game(target_channel, optional_argument)

    @bot.slash_command(name="play_public", permissions=disnake.Permissions(manage_messages=True))
    async def start_new_public_game(
            self,
            inter: disnake.ApplicationCommandInteraction | None,
            game_name: PublicGameName | None,  # type: ignore
            optional_argument: str | None = None):
        """
        Start a new game for everyone in the public channel.

        Parameters
        ----------
        game_name: The game to start.
        optional_argument: An optional argument to pass to the game.
        """
        await self._start_new_public_game(game_name, optional_argument)

    @tasks.loop(minutes=config['public_game_interval'])
    async def start_timed_new_public_game(self):
        await self._start_new_public_game()

    @bot.slash_command(name="play")
    async def start_new_private_game(
            self,
            inter: disnake.ApplicationCommandInteraction,
            game_name: PrivateGameName,  # type: ignore - this is actually perfectly fine
            optional_argument: str | None = None):
        """
        Start a new game in a private thread.

        Parameters
        ----------
        game_name: The game you want to play.
        optional_argument: An optional argument to pass to the game.
        """
        # Ugliest bodge I've ever written, please fix
        self = typing.cast(GameStateManager, gsm)

        # I _would_ split out the isinstance checks, but pylance doesn't support narrowing like that :/
        in_thread = isinstance(inter.channel, disnake.Thread)

        parent_channel_id: int = (inter.channel.parent_id
                                  if isinstance(inter.channel, disnake.Thread)
                                  else inter.channel_id)
        game_uid = hash(
            f"{inter.author.id}{game_name}{time.time()}{random.randint(0, 1000000)}")
        game_uid += sys.maxsize + 1
        print("gameuid", game_uid)

        if parent_channel_id != self.private_game_channel.id:
            return await inter.send(f"You can only play games in {self.private_game_channel.mention}.", ephemeral=True)

        if not game_name or game_name not in self.private_game_list:
            buf = "Please select a valid game. Games include:\n"
            buf += "\n".join(self.private_game_list.keys())
            return await inter.send(buf, ephemeral=True)

        pthread = inter.channel if isinstance(inter.channel, disnake.Thread) else await self.private_game_channel.create_thread(name=game_name, type=disnake.ChannelType.private_thread)

        if in_thread:
            await inter.send(f"Starting {game_name}...")
        else:
            await pthread.send(f"Starting {game_name}... {inter.author.mention}")
            await inter.send(f"Check {pthread.mention}", ephemeral=True)

        game = self.private_game_list[game_name]
        await game(pthread, typing.cast(disnake.Member, inter.author), bot, str(game_uid), optional_argument)


@web.get("/api/consume_session")
async def consume_session(session: str):
    """
    Discord's play game tokens are single-use. Use this endpoint to validate and burn a token.
    """
    if not tokentools.decrypt_token(session):
        return responses.JSONResponse({"valid": False, "reason": "Malformed/foreign session token."}, status_code=400)
    valid = db.play_web_game_session(session)
    return responses.JSONResponse({"valid": valid}, status_code=200 if valid else 400)

@web.get("/api/submit_session")
async def submit_session(session: str, game_name: str, score: str):
    """
    Submit a completed game using your session token. Games can be submitted *once*.
    """
    print("session: ", session, "\ngame_name: ", game_name, "\nscore: ", score)
    #TODO FIX
    return {"submitted": True}


if __name__ == '__main__':
    print("CarniverousCarnival: THIS INSTANCE IS NOT RUNNING THE API CORRECTLY!")
    print("PLEASE START THE BOT BY LOADING UVICORN")
    print("python -m uvicorn main:web")
    bot.run(open('token.txt', encoding="utf8").read())
else:
    print("CarniverousCarnival: Running as a dependency, likely from Uvicorn.")
    print("If you're doing web debug I'd encourage you to disable Discord")
    print("-Prevents burning your tokens")


@web.on_event("startup")
def api_startup():
    '''Called by FastAPI to handle startup tasks, including starting Discord.'''
    use_discord = True
    print("Webserver up.")
    if use_discord:
        print("Starting Discord...")
        asyncio.create_task(
            bot.start(open('token.txt', encoding="utf8").read()))
        print(f"Bot up - {bot.user}")
