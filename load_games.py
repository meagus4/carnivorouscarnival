import os
import importlib
from carnival_types import PublicGame, PrivateGame

PublicGameList = dict[str, PublicGame]
PrivateGameList = dict[str, PrivateGame]


def load_public_games() -> PublicGameList:
    public_game_list: PublicGameList = {}

    for file in os.listdir('public_games'):
        if not file.endswith(".py"):
            continue
        name = file.removesuffix(".py")
        module = importlib.import_module(f'public_games.{name}')
        try:
            public_game_list[name] = module.play_game
        except Exception as e:
            print(f"Error loading module public_games/{file}: {e}")

    return public_game_list


def load_private_games() -> PrivateGameList:
    private_game_list: PrivateGameList = {}

    for file in os.listdir('private_games'):
        if not file.endswith(".py"):
            continue
        name = file.removesuffix(".py")
        module = importlib.import_module(f'private_games.{name}')
        try:
            private_game_list[name] = module.play_game
        except Exception as e:
            print(f"Error loading module private_games/{file}: {e}")

    return private_game_list
