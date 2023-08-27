import disnake
from disnake.ext import commands
from disnake.ext.commands import Bot
from games import *

bot = Bot(command_prefix='.', intents=disnake.Intents().all())

bot.run(open('token.txt').read())
# Press the green button in the gutter to run the script.


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
