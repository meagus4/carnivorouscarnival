import datetime
import importlib
import os
import typing
from carnival_types import *
import disnake
from disnake.ext.commands import Bot
import disnake.ext.tasks as tasks
import random

bot = Bot(command_prefix='.', intents=disnake.Intents().all())
gsm = None


@bot.event
async def on_ready():
    _public = await bot.fetch_channel(1147388785269669908)
    _private = await bot.fetch_channel(1147388437914189844)
    global gsm
    gsm = GameStateManager(_public, _private)
    gsm.start_timed_new_public_game.start()
    print("Ready!")


class GameStateManager:
    # Time until the next public game starts.
    public_game_timer: datetime.datetime
    # Names of the Public Games currently available
    public_game_list: dict[str, typing.Callable]
    # Names of the Private Games currently available.
    private_game_list: dict[str, PrivateGame]
    private_game_channel: disnake.TextChannel
    public_game_channel: disnake.TextChannel

    def __init__(self, _public, _private):
        self.public_game_timer = datetime.datetime.now()
        self.public_game_list = {}
        self.private_game_list = {}
        self.public_game_channel = typing.cast(disnake.TextChannel, _public)
        self.private_game_channel = typing.cast(disnake.TextChannel, _private)

        for file in os.listdir('public_games'):
            if not file.endswith(".py"):
                continue
            name = file.strip(".py")
            module = importlib.import_module(f'public_games.{name}')
            try:
                self.public_game_list[name] = module.play_game
            except Exception as e:
                print(f"Error loading module public_games/{file}: {e}")

        for file in os.listdir('private_games'):
            if not file.endswith(".py"):
                continue
            name = file.strip(".py")
            module = importlib.import_module(f'private_games.{name}')
            try:
                self.private_game_list[name] = module.play_game
            except Exception as e:
                print(f"Error loading module private_games/{file}: {e}")

    async def _start_new_public_game(self, game_name: str | None = None, optional_argument: str | None = None):
        target_channel = self.public_game_channel
        if game_name == None or game_name not in self.public_game_list:
            game_name = random.choice(list(self.public_game_list.keys()))
            game_name = typing.cast(str, game_name)
        game = self.public_game_list[game_name]
        await game(target_channel, optional_argument)

    @bot.slash_command(name="play_public",permissions=disnake.Permissions(manage_messages=True))
    async def start_new_public_game(self, inter: disnake.ApplicationCommandInteraction | None, game_name: str | None, optional_argument: str | None):
        await self._start_new_public_game(game_name, optional_argument)

    @tasks.loop(minutes=30)
    async def start_timed_new_public_game(self):
        await self._start_new_public_game()

    @bot.slash_command(name="play")
    async def start_new_private_game(
            self,
            inter: disnake.ApplicationCommandInteraction,
            game_name: str | None = None,
            optional_argument: str | None = None):
        # Ugliest bodge I've ever written, please fix
        self = typing.cast(GameStateManager, gsm)
        if inter.channel_id != self.private_game_channel.id:
            return await inter.send(f"You can only play games in {self.private_game_channel.mention}.", ephemeral=True)

        if not game_name or game_name not in self.private_game_list:
            buf = "Please select a valid game. Games include:\n"
            buf += "\n".join(self.private_game_list.keys())
            return await inter.send(buf, ephemeral=True)

        pthread = await self.private_game_channel.create_thread(name=game_name, type=disnake.ChannelType.private_thread)
        await pthread.send(f"Starting {game_name}... {inter.author.mention}")
        await inter.send(f"Check {pthread.mention}", ephemeral=True)
        game = self.private_game_list[game_name]
        await game(pthread, typing.cast(disnake.Member, inter.author), optional_argument)

    # @bot.slash_command(name="load")
    # async def load_game(self, game_name: str, game_type: str):
    #    return ""


if __name__ == '__main__':
    bot.run(open('token.txt', encoding="utf8").read())
