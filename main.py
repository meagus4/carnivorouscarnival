import datetime
import importlib
import os

import disnake
from disnake.ext.commands import Bot

bot = Bot(command_prefix='.', intents=disnake.Intents().all())

class GameStateManager:
    public_game_timer: datetime.datetime  # Time until the next public game starts.
    public_game_list:dict  # Names of the Public Games currently available
    private_game_list:dict  # Names of the Private Games currently available.
    def __init__(self):
        self.public_game_timer = datetime.datetime()
        self.public_game_list = {}
        self.private_game_list = {}

        for file in os.listdir('public_games'):
            importlib.import_module(f'public_games/{file}')
            # self.public_game_list[file] =
            import public_games


    def start_new_public_game(self):
        pass

    def start_new_private_game(self):
        pass

    @bot.slash_command(name="load")
    def load_game(self, game_name:str, game_type:str):
        pass

gamestate = GameStateManager

if __name__ == '__main__':
    bot.run(open('token.txt',encoding="utf8").read())
